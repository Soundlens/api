import click
from flask import Blueprint
from app import db
from geoalchemy2 import functions
from app.config.sqlalchemy import config_database_extensions
from app.api.spotify_replacement.api_key_service import ApiKeyService

import requests
import base64
from io import StringIO, BytesIO
from PIL import Image
import os

commands_bp = Blueprint("commands", __name__)

@commands_bp.cli.command("create-api-key")
@click.argument("name")
@click.option("--rate-limit", default=1000, help="Number of requests allowed per day")
def create_api_key(name, rate_limit):
    """Create a new API key"""
    try:
        api_key = ApiKeyService.create_key(name, rate_limit)
        click.echo(f"API Key created successfully!")
        click.echo(f"Name: {api_key.name}")
        click.echo(f"Key: {api_key.key}")
        click.echo(f"Rate Limit: {api_key.rate_limit} requests/day")
    except Exception as e:
        click.echo(f"Error creating API key: {str(e)}", err=True)

@commands_bp.cli.command("list-api-keys")
def list_api_keys():
    """List all API keys"""
    keys = ApiKeyService.list_keys()
    if not keys:
        click.echo("No API keys found.")
        return

    for key in keys:
        click.echo(f"\nName: {key.name}")
        click.echo(f"Key: {key.key}")
        click.echo(f"Active: {key.is_active}")
        click.echo(f"Rate Limit: {key.rate_limit}")
        click.echo(f"Request Count: {key.request_count}")
        click.echo(f"Created At: {key.created_at}")
        click.echo(f"Last Used: {key.last_used_at or 'Never'}")

@commands_bp.cli.command("deactivate-api-key")
@click.argument("key")
def deactivate_api_key(key):
    """Deactivate an API key"""
    if ApiKeyService.deactivate_key(key):
        click.echo("API key deactivated successfully!")
    else:
        click.echo("API key not found.", err=True)

@commands_bp.cli.command("reset-api-key-count")
@click.argument("key")
def reset_api_key_count(key):
    """Reset the request count for an API key"""
    if ApiKeyService.reset_count(key):
        click.echo("Request count reset successfully!")
    else:
        click.echo("API key not found.", err=True)

