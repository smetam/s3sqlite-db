import hashlib
import logging
import os
import typing

import boto3
import databases

from .url import S3DatabaseURL

logger = logging.getLogger("s3sqlite-db")


class S3Database(databases.Database):
    def __init__(
        self, url: typing.Union[str, databases.DatabaseURL], *, local_path=None, ignote_conflicts=False, **kwargs
    ):
        """
        URL: {SCHEME}://{BUCKET}/{KEY}
        Example:
        url = "s3sqlite://my-bucket/databases/db_01.sqlite
        """
        s3_url = S3DatabaseURL(url)
        super().__init__(s3_url.to_local(local_path), **kwargs)

        self.s3_url = s3_url
        self.local_path = self.url.database
        self.ignote_conflicts = ignote_conflicts
        self.s3 = boto3.resource("s3")

        self.original_remote_hash = None
        self.original_local_hash = None

    def get_local_hash(self) -> str:
        m = hashlib.md5()
        with open(self.local_path, "rb") as f:
            m.update(f.read())
        return m.hexdigest()

    def get_remote_hash(self) -> str:
        object_summary = self.s3.ObjectSummary(self.s3_url.bucket, self.s3_url.key)
        return object_summary.e_tag[1:-1]

    def hash_match(self) -> bool:
        return self.original_local_hash == self.get_remote_hash()

    def remote_modified(self) -> bool:
        return self.original_remote_hash != self.get_remote_hash()

    def download(self) -> None:
        logger.info("Downloading %s", self.s3_url.key)
        bucket = self.s3.Bucket(self.s3_url.bucket)
        bucket.download_file(self.s3_url.key, self.local_path)
        self.original_remote_hash = self.get_remote_hash()

    def load_remote(self) -> None:
        if os.path.isfile(self.local_path):
            logger.info("Local database file already exists.")
            self.original_local_hash = self.get_local_hash()

        if self.hash_match():
            logger.info("Local database file hash matches remote hash, skipping download.")
            return

        try:
            self.download()
            self.original_local_hash = self.get_local_hash()
        except Exception as e:
            logger.error(e)

    async def connect(self) -> None:
        logger.info("Connecting to db.")
        self.load_remote()
        await super().connect()

    def upload(self) -> None:
        logger.info("Uploading to %s", self.s3_url.key)
        bucket = self.s3.Bucket(self.s3_url.bucket)
        bucket.upload_file(self.local_path, self.s3_url.key)

    def save_remote(self) -> None:
        if self.hash_match():
            logger.info("Local database file hash matches remote hash, skipping upload.")
            return

        if self.remote_modified():
            if self.ignote_conflicts:
                logger.info('Remote database was modified, overwriting according "ignote_conflicts" parameter.')
            else:
                raise Exception("Remote database was modified.")

        try:
            self.upload()
        except Exception as e:
            logger.error(e)

    async def disconnect(self) -> None:
        await super().disconnect()
        self.save_remote()
        logger.info("Disconnected from db.")
