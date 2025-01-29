from app.main import db
from app.utils.database import Updateable, UserStampedMixin
from app.api.files.database import CanHaveFileMixin
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
import os

class AudioAnalysis(Updateable, CanHaveFileMixin, db.Model):
    __tablename__ = "audio_analyses"
    if os.environ.get("DEV_TENANT_NAME", None) != None:
        __bind_key__ = "__all__"

    # Basic Info
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    artist = db.Column(db.String(255), nullable=True, index=True)
    track_name = db.Column(db.String(255), nullable=False)  # For YouTube download
    duration = db.Column(db.Float, nullable=True)
    
    # Spotify Information
    spotify_info = db.Column(JSONB, nullable=True)  # Store Spotify track details
    
    # Analysis Status
    status = db.Column(db.String(50), nullable=False, default="pending")
    error_message = db.Column(db.Text, nullable=True)
    
    # Task tracking
    task_id = db.Column(db.String(36), nullable=True)
    progress = db.Column(db.Integer, default=0)
    current_step = db.Column(db.String(100), nullable=True)
    
    # Raw Analysis Data
    raw_analysis_data = db.Column(JSONB, nullable=True)

    # Add image URL field
    image_url = db.Column(db.String(500), nullable=True)  # Store Spotify/album cover URL

    # Spotify metadata
    spotify_id = db.Column(db.String(255), index=True)  # Add this line
    spotify_preview_url = db.Column(db.String(500))     # Optional: Add this if you want to store the preview URL
    spotify_duration_ms = db.Column(db.Integer)         # Optional: Add this if you want to store duration

    def __repr__(self):
        return f"<AudioAnalysis {self.title}>"
    
    @property
    def audio_file(self):
        """Returns the associated audio file"""
        return next((file for file in self.files if file.mime_type.startswith('audio/')), None)
    
    @property
    def waveform_image(self):
        """Returns the associated waveform visualization"""
        return next((file for file in self.files if file.mime_type.startswith('image/')), None) 