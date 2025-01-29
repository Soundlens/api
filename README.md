# COPY .env.local to .env

cp flask/.env.local flask/.env


# init the backend application:
docker compose -f docker-compose-local.yml up --build


# access the web at:

http://localhost:8059


# You need the following venv variables:


SPOTIFY_CLIENT_ID=xxxx
SPOTIFY_CLIENT_SECRET=xxxx

LASTFM_API_KEY=xxxx
LASTFM_SHARED_SECRET=xxxx

# create a user for the api:

docker exec -ti soundlens-api bash


# remove the database and create a new one:

docker exec -ti soundlens-db psql
\c soundlens
drop database soundlens;
create database soundlens;

# then restart the container



# to check tables 
\dt 


# remove pyc

find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf


# the rollup issue

use yarn --ignore-platform 