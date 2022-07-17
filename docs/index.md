# Welcome to s3sqlite-databases

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
S3_BUCKET = 'my-bucket'
S3_KEY = 'database.sqlite'
DATABASE_URL = f's3sqlite://{S3_BUCKET}/{S3_KEY}'

async with S3Database(DATABASE_URL) as db:
    query = table.select()
    db.fetch_all(query)

```

or with async framework like FastAPI:

```Python
from fastapi import FastAPI


app = FastAPI()
database = S3Database(DATABASE_URL)


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
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
