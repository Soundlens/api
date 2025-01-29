from celery import shared_task
from app.main import celery, db
from app.api.analysis import AudioAnalyzer
from app.api.analysis.services.analysis_service import AudioAnalysisService
from app.api.files.services import FileService
from flask import current_app
import time
