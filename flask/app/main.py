import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS
from apifairy import APIFairy
from dotenv import load_dotenv
import os
from flask_babel import Babel, refresh
import json

from app.utils.app import get_dot_env_path
from app.config import config_profiler, config_logging, configure_celery
from app.config.sqlalchemy import MySQLAlchemy, MySession, MyModel, metadata
from app.utils.app import (
    get_dot_env_path,
    set_logged_user,
    sudo,
    get_locale,
    get_timezone,
)
from werkzeug.exceptions import HTTPException, InternalServerError
from app.config.celery import celery  # used in __init__.py above


"""This is the logic for ingesting Notion data into LangChain."""


db = MySQLAlchemy(
    metadata=metadata,
    add_models_to_shell=True,
    model_class=MyModel,
    session_options={"class_": MySession},
)
load_dotenv()

ma = Marshmallow()
migrate = Migrate(compare_type=True)


cors = CORS(
    resources={
        r"/api/*": {"origins": "*", "expose_headers": "Content-Disposition"},
        r"/*": {"origins": "*"},
    }
)
apifairy = APIFairy(
)
logger = logging.getLogger()


from flask.json import JSONEncoder as BaseEncoder
from flask_babel import lazy_gettext as _, LazyString

class FlaskJSONEncoder(BaseEncoder):
    def default(self, o):
        if isinstance(o, (_, LazyString)):
            return str(o)
        if hasattr(o, '__html__'):
            return str(o.__html__())
        try:
            iterable = iter(o)
            return list(iterable)
        except TypeError:
            pass
        return super().default(o)

def create_app(config_class=None):
    load_dotenv(get_dot_env_path(), override=True)

    if config_class is None:
        from app.config.flask import Config

        # Since the Config class performs some computation,
        # we are importing it only when it is needed.
        config_class = Config

    print("Creating app...", flush=True)

    app = Flask(__name__, static_folder="../adminPanel/dist")
    
    # Set up custom JSON encoders
    app.json_encoder = FlaskJSONEncoder
    
    
    # Initialize extensions
    babel = Babel(
        app,
        locale_selector=get_locale,
        timezone_selector=get_timezone,
        default_timezone="UTC",
        default_locale="en",
    )
    app.config.from_object(config_class)
    db.init_app(app)
    ma.init_app(app)
    migrate = Migrate(app, db)
    cors.init_app(app)
    
    # Initialize APIFairy after configuration
    apifairy.init_app(app)
    
    configure_celery(app)
    config_profiler(app)
    config_logging(app)

    from app.api.routes import register_routes as register_api_routes
    from app.api.commands import register_commands as register_api_commands

    # @app.route("/")
    # def serve():
    #     """serves React App"""
    #     return send_from_directory(app.static_folder, "index.html")

    # @app.route("/<path:path>")
    # def static_proxy(path):
    #     """static folder serve"""
    #     file_name = path.split("/")[-1]
    #     dir_name = os.path.join(app.static_folder, "/".join(path.split("/")[:-1]))
    #     return send_from_directory(dir_name, file_name)

    # @app.errorhandler(404)
    # def handle_404(e):
    #     if request.path.startswith("/api/"):
    #         return jsonify(message="Resource not found"), 404
    #     return send_from_directory(app.static_folder, "index.html")

    # @app.errorhandler(405)
    # def handle_405(e):
    #     if request.path.startswith("/api/"):
    #         return jsonify(message="Mehtod not allowed"), 405
    #     return e

    register_api_routes(app)

    from app.api.errors import errors as errors_bp

    app.register_blueprint(errors_bp)

    register_api_commands(app)

    @app.before_request
    def before():
        # from app.api.history.services import EventService

        app.logger.info(f"Request: {request.method} {request.url}")
        set_logged_user(None)

    @app.after_request
    def after_request(response):
        url = request.url
        refresh()
        try:
            # Log the URL and response data if not in direct passthrough mode
            if not response.direct_passthrough:
                app.logger.info(f"{request.url} : {str(response.data)}")
            else:
                # Log only URL if in direct passthrough mode
                app.logger.info(f"{request.url} : Direct passthrough mode")
        except Exception as e:
            app.logger.error(f"Error logging response data: {str(e)}")
        return response

    return app


def sync(app, target):
    from app.api.permissions.services import PermissionService, RouteService

    with sudo():
        match target:
            case "permissions":
                app.logger.info(f"Syncing routes and permissions")
                PermissionService.sync_actions()
                RouteService.sync_routes()

    db.session.commit()


def bootstrap_app(app):
    pass

    # with app.app_context():

    #     sync(app, "permissions")
