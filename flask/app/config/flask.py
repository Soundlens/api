import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from app.utils.app import get_database_uri
import googlemaps

from app.config.utils import as_bool
# import app.api.files.integrations.aws as aws
from botocore.config import Config
import boto3, botocore


def get_s3_client():
    # AWS authentication is made using env variables:
    # AWS_ACCESS_KEY_ID: The access key for the AWS account.
    # AWS_SECRET_ACCESS_KEY: The secret key for the AWS account.
    my_config = Config(
        region_name="eu-west-1",
        signature_version="v4",
        retries={"max_attempts": 10, "mode": "standard"},
    )
    return boto3.client("s3", config=my_config)

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # -------------------
    # SQLAlchemy
    # -------------------
    APP_CONTEXT = os.environ.get("APP_CONTEXT")
    SQLALCHEMY_DATABASE_URI = get_database_uri(os.environ.get("DB_NAME"))

    # edit for sqlite
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, os.environ.get(
    #     "DB_NAME") + '.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_HOST = os.environ.get("APP_HOST")
    APP_PROTOCOL = os.environ.get("APP_PROTOCOL")

    # -------------------
    # APIFairy
    # -------------------
    APIFAIRY_TITLE = "soundlens API"
    APIFAIRY_VERSION = "1.0"
    APIFAIRY_UI = os.environ.get("DOCS_UI", "elements")
    APIFAIRY_UI_PATH = os.environ.get('API_DOCS_URL', '/api/docs')


    # -------------------
    # Our Tokens
    # -------------------
    ACCESS_TOKEN_MINUTES = 60 * 24 * 7
    REFRESH_TOKEN_DAYS = 365

    EMAIL_VERIFICATION_TOKEN_DAYS = 7
    RESET_PASSWORD_TOKEN_HOURS = 1

    REFRESH_TOKEN_IN_COOKIE = as_bool(
        os.environ.get("REFRESH_TOKEN_IN_COOKIE") or "yes"
    )
    REFRESH_TOKEN_IN_BODY = as_bool(os.environ.get("REFRESH_TOKEN_IN_BODY") or "yes")

    # -------------------
    # IDK
    # -------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "top-secret!")
    JSON_SORT_KEYS = False
    # USE_CORS = True
    CORS_SUPPORTS_CREDENTIALS = True
    APP_ENV = os.environ.get("APP_ENV")

    # -------------------
    # DOCUMENTATION
    # -------------------
    DOCUMENTATION_ID = os.environ.get("DOCUMENTATION_ID")

    # -------------------
    # AWS
    # -------------------
    AWS_S3_CLIENT = get_s3_client()
    AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")


    # OPENAI_CLIENT = OpenAI(
    #     # This is the default and can be omitted
    #     api_key=OPENAI_KEY,
    # )
    # -------------------
    # Sendinblue
    # -------------------
    EMAIL_KEY = os.environ.get("EMAIL_KEY")
    DEV_EMAIL = os.environ.get("DEV_EMAIL")


    # print("AA " * 100 ,flush=True)
    # print(TWILIO_WORKSPACE_INFO, flush=True)
    ANALYSIS_BACKEND = os.environ.get("ANALYSIS_BACKEND")
    ANALYSIS_FOLDER = os.environ.get("ANALYSIS_FOLDER")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")


    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
    REDIS_DB = os.environ.get("REDIS_DB", 0)

    BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CELERY_BROKER_URL = BROKER_URL
    CELERY_RESULT_BACKEND = BROKER_URL
    LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
    LASTFM_SHARED_SECRET = os.environ.get("LASTFM_SHARED_SECRET")

    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
    CELERY_BEAT_SCHEDULE = {

    }

    API_URL = os.environ.get('API_URL', 'http://localhost:5000')
