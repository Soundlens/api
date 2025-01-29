from typing import Optional, List
from sqlalchemy import or_, and_
from app.main import db
from app.api.analysis.database.models import AudioAnalysis
from app.api.files.services import FileService
from app.api.exceptions import BusinessLogicException
from flask_babel import gettext as _
from app.api.analysis import AudioAnalyzer
from flask import current_app
from werkzeug.datastructures import FileStorage
from app.utils.app.file import FileType
import boto3
import json
import io
import os

class AudioAnalysisService:
    @staticmethod
    def create_analysis(data: dict) -> AudioAnalysis:
        """Create a new audio analysis"""
        audio_path = None
        try:
            # Extract data
            analysis_data = {
                "title": data["title"],
                "artist": data.get("artist"),
                "track_name": data["track_name"],
                "spotify_info": data.get("spotify_info"),
                "image_url": data.get("spotify_info", {}).get("imageUrl"),
            }

            # Check if analysis already exists
            existing = AudioAnalysis.query.filter(
                or_(
                    and_(
                        AudioAnalysis.title == analysis_data["title"],
                        AudioAnalysis.artist == analysis_data["artist"],
                    ),
                    and_(
                        AudioAnalysis.spotify_id == analysis_data["spotify_info"]["id"],
                        AudioAnalysis.status == "completed",
                    ),
                )
            ).first()

            if existing:
                return existing

            # Create analysis record
            analysis = AudioAnalysis(
                status="pending",
                spotify_id=analysis_data["spotify_info"]["id"],
                **analysis_data,
            )
            db.session.add(analysis)
            db.session.flush()  # Get the ID

            # Initialize S3 client
            from botocore.config import Config
            my_config = Config(
                region_name="eu-west-1",
                signature_version="v4",
                retries={"max_attempts": 10, "mode": "standard"},
            )
            s3 = boto3.client(
                's3',
                config=my_config
            )

            # Store analysis metadata in S3
            s3_analysis_data = {
                "id": analysis.id,
                "title": analysis.title,
                "artist": analysis.artist,
                "track_name": analysis.track_name,
                "spotify_info": analysis.spotify_info,
                "status": "pending",
                "needs_download": True
            }

            # Upload analysis JSON to S3
            s3.put_object(
                Bucket=current_app.config['AWS_S3_BUCKET_NAME'],
                Key=f"analyses/{analysis.id}.json",
                Body=json.dumps(s3_analysis_data, indent=2),
                ContentType='application/json'
            )

            # Create a placeholder file record
            audio_file = FileService.create(
                file_name=analysis_data["track_name"],
                mime_type='audio/mpeg',
                file_type=FileType.AUDIO,
            )
            db.session.commit()

            # Start async analysis
            from app.celery.celery_tasks import analyze_audio
            task = analyze_audio.delay(analysis.id, audio_file.id)
            analysis.task_id = task.id

            db.session.commit()
            return analysis

        except Exception as e:
            db.session.rollback()
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception as cleanup_error:
                    print(f"Error cleaning up file {audio_path}: {cleanup_error}")
            raise e

    @staticmethod
    def get(id: int) -> AudioAnalysis:
        """Get an analysis by ID"""
        analysis = AudioAnalysis.query.get(id)
        if not analysis:
            raise BusinessLogicException(code=404, description=_("Analysis not found."))
        return analysis

    @staticmethod
    def search(search: str = "", **filters) -> List[AudioAnalysis]:
        """Search for analyses with filters"""
        query = AudioAnalysis.query

        if search:
            query = query.filter(
                or_(
                    AudioAnalysis.title.ilike(f"%{search}%"),
                    AudioAnalysis.artist.ilike(f"%{search}%"),
                )
            )

        # Add other filters
        for key, value in filters.items():
            if hasattr(AudioAnalysis, key) and value is not None:
                query = query.filter(getattr(AudioAnalysis, key) == value)

        return query.order_by(AudioAnalysis.inserted_at.desc())

    @staticmethod
    def delete(id: int) -> None:
        """Delete an analysis and its associated files"""
        analysis = AudioAnalysisService.get(id)

        # Get all files associated with this analysis
        files = FileService.search(entity=analysis).all()

        # Delete each file
        for file in files:
            FileService.remove_file(analysis, None, file.id)

        db.session.delete(analysis)

    @staticmethod
    def update_analysis_status(
        id: int,
        status: str,
        error_message: Optional[str] = None,
        progress: Optional[int] = None,
        current_step: Optional[str] = None,
    ) -> AudioAnalysis:
        """Update the analysis status and progress"""
        analysis = AudioAnalysisService.get(id)
        analysis.status = status

        if error_message is not None:
            analysis.error_message = error_message
        if progress is not None:
            analysis.progress = progress
        if current_step is not None:
            analysis.current_step = current_step

        db.session.add(analysis)
        return analysis

    @staticmethod
    def update_analysis_results(id: int, results: dict) -> AudioAnalysis:
        """Update the analysis results"""
        analysis = AudioAnalysisService.get(id)
        from datetime import datetime, timezone

        try:
            # Update basic audio features

            
            # Only update track_name if it's provided and not None
            analysis.timestamp = datetime.now(timezone.utc)

        
            analysis.raw_analysis_data = results


            # Update status
            analysis.status = "completed"

            db.session.add(analysis)
            return analysis

        except Exception as e:
            db.session.rollback()
            raise e
        """Get analyses by status"""

    @staticmethod
    def get_analysis_by_mood(mood: str) -> List[AudioAnalysis]:
        """Get analyses by mood"""
        return AudioAnalysis.query.filter_by(mood=mood).all()

    @staticmethod
    def get_similar_analyses(id: int, limit: int = 5) -> List[AudioAnalysis]:
        """Get similar analyses based on audio features"""
        analysis = AudioAnalysisService.get(id)
        if not analysis:
            return []

        # Get analyses with similar features
        query = AudioAnalysis.query.filter(AudioAnalysis.id != id)

        # Filter by similar energy and valence (within 0.2 range)
        if analysis.energy is not None:
            query = query.filter(
                AudioAnalysis.energy.between(
                    max(0, analysis.energy - 0.2), min(1, analysis.energy + 0.2)
                )
            )
        if analysis.valence is not None:
            query = query.filter(
                AudioAnalysis.valence.between(
                    max(0, analysis.valence - 0.2), min(1, analysis.valence + 0.2)
                )
            )

        return query.limit(limit).all()

    @staticmethod
    def get_public(id: int) -> AudioAnalysis:
        """Get a public analysis by ID"""
        analysis = AudioAnalysis.query.filter_by(id=id, status="completed").first()

        if not analysis:
            raise BusinessLogicException(code=404, description=_("Analysis not found."))
        return analysis
