from datetime import datetime
import json
import logging
from typing import Dict
import uuid 
import requests
from requests.adapters import HTTPAdapter, Retry
import polars as pl
import os.path
import sqlite3
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from sqlalchemy.engine import Engine
from sqlalchemy import event


from database import Base, Location, Meter, PricePoint, Product, Region, Service, Sku, Type

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logging.info("Starting")

cache_file = "cache.parquet"
use_cache = True
export_data = True

if (not use_cache) or not os.path.isfile(cache_file) :

    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=2,
                    status_forcelist=[ 500, 502, 503, 504, 429 ])

    s.mount('https://', HTTPAdapter(max_retries=retries))

    items = []
    response = {
        "NextPageLink": "https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview&meterRegion='primary'"
    }
    while True:
        if "NextPageLink" in response and response["NextPageLink"] is not None:
            page = response["NextPageLink"]
        else:
            break

        logging.info(f"load page {page}")
        data = s.get(page)

        response = data.json()
        if "Items" in response:
            items.extend(response["Items"])
        # break


    for item in items:
        key = "savingsPlan"
        if key in response:
            item[key] = json.dumps(item[key])
        else:
            item[key] = ""            
    # Currently does not work: https://github.com/pola-rs/polars/issues/17745
    # df = pl.json_normalize(items)
    df = pl.DataFrame(items)
    df.write_parquet(cache_file)

else:
    df = pl.read_parquet(cache_file)

# df = df.drop(["savingsPlan"])

df = df.with_columns(import_date = datetime.now())
df = df.with_columns(
    pl.when(pl.col(pl.String).str.len_chars() == 0)
    .then(None)
    .otherwise(pl.col(pl.String))
    .name.keep()
)
# TODO: reduce size by transforming data into multiple tables.

if export_data:
    database_path = "frontend/public/test_new.sqlite"
    logging.info(f"Export to {database_path}")

    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)

    regions: Dict[str, Meter] = {}
    locations: Dict[str, Location] = {}
    types: Dict[str, Location] = {}
    meters: Dict[str, Location] = {}
    products: Dict[str, Location] = {}
    skus: Dict[str, Location] = {}
    services: Dict[str, Location] = {}

    logging.info("mapping regions")
    for region in df["armRegionName"].unique():
        if region is not None:
            regions[region] = Region(
                arm_name=region
            )

    logging.info("mapping locations")
    for location in df["location"].unique():
        if location is not None:
            locations[location] = Location(
                name=location
            )

    logging.info("mapping consumption type")
    for type in df["type"].unique():
        types[type] = Type(
            name=type
        )

    logging.info("mapping products")
    product_variations = df[["productId", "productName"]].unique(["productId", "productName"])
    if len(product_variations) != len(df["productId"].unique()):
        raise Exception("product ids not unique")
    for type in product_variations.rows(named=True):
        products[type["productId"]] = Product(
            id=type["productId"],
            name=type["productName"],
        )


    logging.info("mapping services")
    service_variations = df[["serviceId", "serviceName", "serviceFamily"]].unique(["serviceId", "serviceName", "serviceFamily"])
    if len(service_variations) != len(df["serviceId"].unique()):
        raise Exception("service ids not unique")
    for type in service_variations.rows(named=True):
        services[type["serviceId"]] = Service(
            id=type["serviceId"],
            name=type["serviceName"],
            family=type["serviceFamily"],
        )

    
    with Session(engine) as session:
        session.bulk_save_objects(services.values())
        session.bulk_save_objects(products.values())
        session.bulk_save_objects(locations.values())
        session.bulk_save_objects(regions.values())
        session.bulk_save_objects(types.values())
        session.commit()

        regions = {x.arm_name: x.id for x in session.scalars(select(Region)).all()}
        locations = {x.name: x.id for x in session.scalars(select(Location)).all()}
        types = {x.name: x.id for x in session.scalars(select(Type)).all()}
        meters = {x.name: x.id for x in session.scalars(select(Meter)).all()}
        skus = {x.name: x.id for x in session.scalars(select(Sku)).all()}
        # products = {x.id: x for x in session.scalars(select(Product)).all()}
        # services = {x.id: x for x in session.scalars(select(Service)).all()}

    logging.info("converting dataframe")
    df = (df.with_columns(
        pl.struct(pl.col('*')).map_elements(lambda row: PricePoint(
                    unit_price=row["unitPrice"],
                    retail_price=row["retailPrice"],
                    tier_minimum_units=row["tierMinimumUnits"],
                    effective_start_date=datetime.strptime(row["effectiveStartDate"], "%Y-%m-%dT%H:%M:%S%z"),
                    unit_of_measure=row["unitOfMeasure"],
                    is_primary=row["isPrimaryMeterRegion"],
                    reservations=row["reservationTerm"],
                    import_date=row["import_date"],
                    meter_id=uuid.UUID(row['meterId']),
                    region_id=regions[row["armRegionName"]] if row["armRegionName"] is not None else None,
                    location_id=locations[row["location"]] if row["location"] is not None else None,
                    consumption_type_id=types[row["type"]] if row["type"] is not None else None,
                    service_id=row["serviceId"],
                    product_id=row["productId"]

            ))
            .alias('object'))
    )

    
    with Session(engine) as session:
        session.bulk_save_objects(df["object"])
        session.commit()

    engine.dispose()

    # Optimize Database
    con = sqlite3.connect(database_path)
    cursor = con.cursor()
    # https://github.com/mmomtchev/sqlite-wasm-http?tab=readme-ov-file#page-size
    # https://github.com/phiresky/world-development-indicators-sqlite/blob/gh-pages/postproc.sh#L15
    cursor.execute("PRAGMA JOURNAL_MODE = DELETE;")
    cursor.execute("PRAGMA page_size = 1024;")
    cursor.execute("PRAGMA optimize")
    cursor.execute("VACUUM;")
    cursor.close()
    
print(df)