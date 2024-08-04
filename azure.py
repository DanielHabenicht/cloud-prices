import requests
from requests.adapters import HTTPAdapter, Retry
import polars as pl
import os.path
import sqlite3


cache_file = "cache.parquet"
use_cache = True
export_data = True

i = 0
if (not use_cache) or not os.path.isfile(cache_file) :
    i = i + 1
    firstRequest = True
    items = []

    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=2,
                    status_forcelist=[ 500, 502, 503, 504, 429 ])

    s.mount('https://', HTTPAdapter(max_retries=retries))

    while firstRequest or json["NextPageLink"] is not None: 
        print("load page")
        firstRequest = False
        data = s.get("https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview&meterRegion='primary'")

        json = data.json()
        if "Items" in json:
            items.extend(json["Items"])
        else:
            break;

    print(json)

    df = pl.DataFrame(items)
else:
    df = pl.read_parquet(cache_file)


df.write_parquet(cache_file)

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

print(len(df))
print(df)