import pytest

from s3sqlite_db import S3Database, S3DatabaseURL, __version__


def test_version():
    assert __version__ == "0.1.2"


@pytest.mark.parametrize(
    "bucket, key",
    [
        ("my-bucket", "db.sqlite"),
        ("s3bucket", "sqlite.db"),
        ("my-awesome-bucket", "path/to/my/db.sqlite"),
        ("my-awesome-bucket", "path/to/my/sqlite.db"),
    ],
)
def test_url(bucket, key):
    database_url = f"s3sqlite://{bucket}/{key}"
    s3_db_url = S3DatabaseURL(database_url)
    assert s3_db_url.bucket == bucket
    assert s3_db_url.key == key


@pytest.mark.parametrize(
    "bucket, key, local_path",
    [
        ("my-bucket", "db.sqlite", None),
        ("s3bucket", "sqlite.db", "/path/to/local.db"),
        ("my-awesome-bucket", "path/to/my/db.sqlite", None),
        ("my-awesome-bucket", "path/to/my/sqlite.db", "/path/to/local.db"),
    ],
)
def test_url_to_local(bucket, key, local_path):
    database_url = f"s3sqlite://{bucket}/{key}"
    s3_db_url = S3DatabaseURL(database_url)
    local_db_url = s3_db_url.to_local(local_path)
    assert local_db_url.scheme == "sqlite"
    assert local_db_url.netloc == ""

    local_path = local_path or f'/tmp/{key.split("/")[-1]}'
    assert local_db_url.database == local_path


@pytest.mark.parametrize(
    "bucket, key, local_path",
    [
        ("my-bucket", "db.sqlite", None),
        ("s3bucket", "sqlite.db", "/path/to/local.db"),
        ("my-awesome-bucket", "path/to/my/db.sqlite", None),
        ("my-awesome-bucket", "path/to/my/sqlite.db", "/path/to/local.db"),
    ],
)
def test_db_local_path(bucket, key, local_path):
    database_url = f"s3sqlite://{bucket}/{key}"
    s3_db = S3Database(database_url, local_path=local_path)

    local_path = local_path or f'/tmp/{key.split("/")[-1]}'
    assert s3_db.local_path == local_path
