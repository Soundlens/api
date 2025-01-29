from app import ma
from app.utils.schemas.utils import CustomSQLAlchemySchema, UTCDateTime
from app.api.files.schemas import FileSchema
from marshmallow import validate, fields
from flask_babel import lazy_gettext as _

class SpotifyInfoSchema(ma.Schema):
    """Schema for Spotify track information"""
    id = ma.String(required=True)
    name = ma.String(required=True)
    artist = ma.String(required=True)
    imageUrl = ma.String(required=False, allow_none=True)
    duration_ms = ma.Integer(required=True)

class AudioAnalysisSchema(CustomSQLAlchemySchema):
    class Meta:
        model = "AudioAnalysis"
        ordered = True
        include_relationships = True
        description ="This schema represents an Audio Analysis"
        react_uischema_extra = {
            "files": {
                "ui:field": "FileUploadField",
                "ui:options": {
                    "accept": "audio/*",
                    "multiple": False
                }
            },
            "status": {
                "ui:readonly": True
            }
        }

    # Basic Info
    id = ma.Integer(dump_only=True)
    title = ma.String(
        required=True,
        validate=validate.Length(min=1, max=255),
        metadata={"title":"Title", "description":"Song title"}
    )
    track_name = ma.String(
        required=True,
        validate=validate.Length(max=255),
        metadata={"title":"Track Name", "description":"Track name for download"}
    )
    artist = ma.String(
        required=True,
        validate=validate.Length(max=255),
        metadata={"title":"Artist", "description":"Song artist"}
    )
    duration = ma.Float(
        dump_only=True,
        metadata={"title":"Duration", "description":"Song duration in seconds"}
    )

    # Spotify Information
    spotify_info = fields.Nested(
        SpotifyInfoSchema,
        required=False,
        allow_none=True,
        metadata={"title":"Spotify Info", "description":"Spotify track information"}
    )

    # Status
    status = ma.String(
        dump_only=True,
        metadata={"title":"Status", "description":"Analysis status"}
    )
    error_message = ma.String(
        dump_only=True,
        metadata={"title":"Error", "description":"Error message if analysis failed"}
    )

    # Task tracking
    task_id = ma.String(dump_only=True)
    progress = ma.Integer(dump_only=True)
    current_step = ma.String(dump_only=True)

    # Files
    files = ma.Nested(
        FileSchema,
        many=True,
        dump_only=True,
        metadata={"title":"Files", "description":"Associated files (audio, waveform)"}
    )

    raw_analysis_data = ma.Raw(dump_only=True)

    # Timestamps
    inserted_at = UTCDateTime(dump_only=True)
    updated_at = UTCDateTime(dump_only=True)

    image_url = ma.String(
        required=False,
        allow_none=True,
        metadata={"title":"Image URL", "description":"Album cover image URL"}
    )

class AnalysisStatusSchema(ma.Schema):
    """Schema for analysis status response"""
    status = ma.String(required=True)
    progress = ma.Integer(required=True)
    current_step = ma.String(required=False)
    error = ma.String(required=False)

class AnalysisCancelSchema(ma.Schema):
    """Schema for analysis cancel response"""
    status = ma.String(required=True) 