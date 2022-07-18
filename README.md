# Welcome to s3sqlite-db
![build status](../../workflows/ci/badge.svg)

This is an extension to [encode/databases](https://github.com/encode/databases)
that allows using sqlite database with AWS S3.
Main purpose for this is use with AWS Lambda, to download sqlite db to Lambda on db connect and upload back on disconnect.

## Installation

```console
$ pip install s3sqlite-db
```

## Usage

You can use S3Database as async context manager:

```Python
from s3sqlite_db import S3Database


S3_BUCKET = 'my-bucket'
S3_KEY = 'database.sqlite'
DATABASE_URL = f's3sqlite://{S3_BUCKET}/{S3_KEY}'

async with S3Database(DATABASE_URL) as db:
    query = table.select()
    result = await db.fetch_all(query)

```

or with async framework like FastAPI:

```Python
from fastapi import FastAPI
from s3sqlite_db import S3Database


app = FastAPI()
database = S3Database(DATABASE_URL)


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
```


## Queries

Both sqlalchemy core and raw queries are supported.


### Raw

```Python
async with S3Database(DATABASE_URL) as db:
    query = "INSERT INTO users(name, age) VALUES (:name, :age)"
    values = {"name": "John", "age": 55}
    await database.execute(query=query, values=values)
```

### Sqlalchemy

```Python
import sqlalchemy

metadata = sqlalchemy.MetaData()


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("age", sqlalchemy.Integer),
)


async with S3Database(DATABASE_URL) as db:
    query = sqlalchemy.delete(users).where(users.c.age == 55)
    await database.execute(query=query)
```

## Configuration
By default if remote database was modified, exception is raised, but `ignote_conflicts=True` argument can be specified, to force overwrite.

```Python
async with S3Database(DATABASE_URL, ignote_conflicts=True) as db:
    ...
```

Also you can specify a path to download local copy of db.
This can be useful when working locally (not on AWS Lambda), or when whorking with several sqlite databaases at the same time.

```Python
async with S3Database(DATABASE_URL, local_path='/path/to/db.sqlite') as db:
    ...
```
