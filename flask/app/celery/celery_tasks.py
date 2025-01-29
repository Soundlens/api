import os
import time

from flask import current_app

from app import celery, db
import datetime
from celery import shared_task
from app.main import celery, db
from app.api.analysis import AudioAnalyzer
from app.api.analysis.services.analysis_service import AudioAnalysisService
from flask import current_app
import time

@celery.task(
    name="generic_service_task",
    bind=True,
    args={"function", "args", "kwargs"},
    kwargs={},
)
def generic_service_task(
    self,
    service: str,
    function: str,
    import_path: str,
    kwargs: dict,
):
    current_app.logger.info(
        f"Starting generic service job... for kwargs {kwargs}",
    )
    try:
        # Check if service is a class

        from importlib import import_module

        module = import_module(import_path)

        service_class = getattr(module, service)

        result = getattr(service_class, function)(**kwargs)

        current_app.logger.info(
            f"Generic service job finished... for kwargs {kwargs} with result {result}",
        )

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e


@celery.task(name="sync_data_task", bind=True, args={"target"})
def sync_data_task(self, target: str):
    current_app.logger.info(
        f"Starting sync job... for with target {target}",
    )

    from app.main import sync

    sync(current_app, target)


@celery.task(name="check_task_notifications", bind=True)
def check_task_notifications_task(self):

    current_app.logger.info(
        f"Checking if there are any task notifications to send...",
    )
    try:
        [
            tasks_start,
            tasks_end,
        ] = NotificationService.check_task_notifications()

        for task in tasks_start:
            NotificationService.notify_task_start_date(task)
        for task in tasks_end:
            NotificationService.notify_task_deadline(task)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


# @celery.task(name="check_thresholds", bind=True)
# def check_thresholds(self):

#     current_app.logger.info(
#         f"Checking if there are any thresholds to notify...",
#     )

#     try:
#         ThresholdService.check_all_thresholds()
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         raise e


@celery.task(name="analyze_audio", bind=True)
def analyze_audio(self, analysis_id: int, file_id: int):
    """Celery task to analyze audio file"""
    try:
        # Update status to processing
        analysis = AudioAnalysisService.update_analysis_status(
            analysis_id, 
            'processing',
            progress=0,
            current_step='Waiting for audio file'
        )
        db.session.commit()

        # Initialize analyzer
        analyzer = AudioAnalyzer(
            downloads_dir=current_app.config['UPLOAD_FOLDER'],
            analysis_dir=current_app.config['ANALYSIS_FOLDER'],
            backend=current_app.config.get('ANALYSIS_BACKEND', 'librosa')
        )

        # Wait for audio file to be available in S3
        max_retries = 30  # Try for 5 minutes (10 second intervals)
        for attempt in range(max_retries):
            try:
                
                # Check if file exists in S3
                analyzer.s3.head_object(
                    Bucket=current_app.config['AWS_S3_BUCKET_NAME'],
                    Key=f"audio/{analysis_id}.mp3"
                )
                print(f"Audio file found in S3 for analysis {analysis_id}", flush=True)
                # File exists, proceed with analysis
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    # If we've exhausted all retries, raise the error
                    raise Exception("Timeout waiting for audio file to be available")
                print(f"Audio file not yet available, attempt {attempt + 1}/{max_retries}", flush=True)
                time.sleep(10)  # Wait 10 seconds before next attempt

        # Define progress callback
        def update_progress(progress: int, step: str):
            AudioAnalysisService.update_analysis_status(
                analysis_id,
                'processing',
                progress=progress,
                current_step=step
            )
            print(f"Updated analysis status to {progress}% for analysis {analysis_id}", flush=True)
            db.session.commit()

        # Set progress callback
        analyzer.feature_extractor.set_progress_callback(update_progress)
        
        print(f"Starting audio analysis for analysis {analysis_id}", flush=True)
        # Update status to show we're starting analysis
        
        db.session.commit()
        
        # Perform analysis
        results = analyzer.analyze_track(
            track_id=analysis_id,
            bucket_name=current_app.config['AWS_S3_BUCKET_NAME']
        )

        print(f"Audio analysis completed for analysis {analysis_id}", flush=True)
        
        if 'error' in results:
            raise Exception(results['error'])
        
        # Extract results
        features = results.get('analysis', {}).get('technical_features', {})
        voice_features = results.get('analysis', {}).get('voice_features', {})
        mood_scores = results.get('analysis', {}).get('mood_scores', {})

        # Update analysis with results
        analysis_data = {
            'tempo': features.get('tempo'),
            'key': features.get('key'),
            'mode': features.get('mode'),
            'time_signature': features.get('time_signature'),
            'danceability': features.get('danceability'),
            'energy': features.get('energy'),
            'loudness': features.get('loudness'),
            'speechiness': features.get('speechiness'),
            'acousticness': features.get('acousticness'),
            'instrumentalness': features.get('instrumentalness'),
            'liveness': features.get('spotify_audio_features', {}).get('liveness'),
            'valence': features.get('valence'),
            'mood': mood_scores.get('primary_mood'),
            'mood_confidence': mood_scores.get('confidence'),
            'voice_characteristics': voice_features,
            'segments': results.get('analysis', {}).get('segments', []),
            'raw_analysis_data': results
        }
        print(f"Updating analysis results for analysis {analysis_id}", flush=True)

        AudioAnalysisService.update_analysis_results(analysis_id, analysis_data)
        
        # Update final status
        AudioAnalysisService.update_analysis_status(
            analysis_id,
            'completed',
            progress=100,
            current_step='Analysis completed'
        )
        db.session.commit()

        return {'status': 'completed', 'analysis_id': analysis_id}

    except Exception as e:
        # Update status to failed
        AudioAnalysisService.update_analysis_status(
            analysis_id, 
            'failed', 
            error_message=str(e),
            progress=0,
            current_step='Analysis failed'
        )
        db.session.commit()
        raise e 