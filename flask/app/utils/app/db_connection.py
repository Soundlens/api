import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.engine import URL
from flask import current_app


def get_database_uri(database_name: str) -> URL:
    if os.environ.get("DB_CONNECTION") == "mysql":
        driver_name = "mysql+pymysql"
    elif os.environ.get("DB_CONNECTION") == "postgres":
        driver_name = "postgresql+pg8000"
    else:
        raise Exception(
            f"DB_CONNECTION not recognized: {os.environ.get('DB_CONNECTION')}"
        )

    return URL.create(
        drivername=driver_name,
        username=os.environ.get("DB_USERNAME"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        database=database_name,
    )


def wait_for_db_connection():
    database_name = os.environ.get("DB_NAME")
    db_uri = get_database_uri(database_name)
    try:
        while True:
            try:
                if not database_exists(db_uri):
                    print(
                        f"Main database does not exist. Creating database: {database_name}"
                    )
                    print(db_uri.render_as_string(hide_password=False), flush=True)
                    create_database(db_uri)

                engine = create_engine(db_uri)
                conn = engine.connect()
                conn.execute(text("SELECT 1")).fetchall()
                print(f"Successfully connected to {engine.url}", flush=True)
                return
            except Exception as e:
                print(
                    f"Got exception while connecting to database: {db_uri}", flush=True
                )
                print(f"Exception: {e}", flush=True)
                time.sleep(1)
                raise e
    except:
        while True:
            time.sleep(100)
