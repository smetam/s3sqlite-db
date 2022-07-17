import logging
import typing

import databases

logger = logging.getLogger("s3sqlite-db")


class S3DatabaseURL(databases.DatabaseURL):
    @property
    def bucket(self) -> str:
        return self.netloc

    @property
    def key(self) -> str:
        return self.database

    @property
    def dbname(self) -> str:
        return self.database.split("/")[-1]

    def to_local(self, local_path: typing.Optional[str] = None):
        if local_path is None:
            local_path = "/tmp/" + self.dbname
            logger.debug("Local path was not provided, using %s", local_path)

        return self.replace(
            dialect="sqlite",
            # driver='aiosqlite',
            netloc="",
            database=local_path,
        )
