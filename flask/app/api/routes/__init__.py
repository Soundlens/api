import logging
from flask import Blueprint

from app.utils.app import import_blueprint
from app.utils.database import check_mixins
from app.utils.schemas.utils import create_schema_blueprint, update_blueprints_with_schemas
from app.api.analysis.routes import bp as analysis_bp
from app.api.spotify.routes import bp as spotify_bp
# from app.api.lastfm.routes import bp as lastfm_bp
from app.api.spotify_replacement.routes import bp as spotify_replacement_bp
# from .routes import bp as api_bp


# List of statically imported mandatory blueprints
mandatory_blueprints = [
    analysis_bp,
    spotify_bp,
    # lastfm_bp,
    spotify_replacement_bp
]


def register_routes(app):
    # Register mandatory blueprints statically imported
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    for bp in mandatory_blueprints:
        api_bp.register_blueprint(bp)

    # Register API blueprint to app
    app.register_blueprint(api_bp)
    
    schema_bp = create_schema_blueprint(app)
    update_blueprints_with_schemas(app, schema_bp)

    app.register_blueprint(schema_bp)

def get_class_service_getter(_cls):
    from app.api.analysis.services import AudioAnalysisService

    mapping = {
        "AudioAnalysis": AudioAnalysisService.get_analysis,
    }
    return mapping[_cls.__name__]

def get_bp_mapping(_cls):

    mapping = {
        "AudioAnalysis": analysis_bp,
    }
    return mapping[_cls.__name__]


