from datetime import datetime
import logging 
import requests
from requests.adapters import HTTPAdapter, Retry
import polars as pl
import os.path
import sqlite3

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logging.info("Starting")

cache_file = "cache.parquet"
use_cache = False
export_data = True

if (not use_cache) or not os.path.isfile(cache_file) :

    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=2,
                    status_forcelist=[ 500, 502, 503, 504, 429 ])

    s.mount('https://', HTTPAdapter(max_retries=retries))

    items = []
    json = {}
    page = "https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview&meterRegion='primary'"
    while True:
        if "NextPageLink" in json and json["NextPageLink"] is not None:
            page = json["NextPageLink"]
        logging.info(f"load page {page}")
        data = s.get(page)

        json = data.json()
        if "Items" in json:
            items.extend(json["Items"])
        else:
            break;

    print(json)

    df = pl.json_normalize(items)
else:
    df = pl.read_parquet(cache_file)


df.write_parquet(cache_file)
df = df.with_columns(import_date = datetime.now())

if export_data:

    database_path = "frontend/public/test.sqlite"
    connection=sqlite3.connect(database_path)

    c=connection.cursor()
    # https://github.com/mmomtchev/sqlite-wasm-http?tab=readme-ov-file#page-size
    c.execute("PRAGMA JOURNAL_MODE = DELETE;")
    c.execute("PRAGMA page_size = 1024;")
    #-- Do it for every FTS table you have
    #-- (geospatial datasets do not use full text search)
    # c.execute("INSERT INTO prices_azure(prices_azure) VALUES ('optimize');")
    #-- Reorganize database and apply changed page size
    #-- Sometimes you will be surprised by the new size of your DB
    c.execute("VACUUM;")
    df.write_database("prices_azure", f"sqlite:///{database_path}", if_table_exists="append")

print(df)