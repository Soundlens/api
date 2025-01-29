from flask import Blueprint, current_app, request, send_file, jsonify
from apifairy import authenticate, body, response, other_responses, arguments
from flask_babel import gettext as _
from celery.result import AsyncResult

from app.main import db, celery
from app.api.analysis.database.models import AudioAnalysis
from app.api.analysis.schemas.analysis import (
    AudioAnalysisSchema, 
    AnalysisStatusSchema,
    AnalysisCancelSchema
)
from app.api.analysis.services.analysis_service import AudioAnalysisService
from app.api.files.schemas import FileSchema
from app.utils.schemas.utils import (
    get_paginated_schema,
    paginate_query,
    get_main_page_schema,
)
from app.exceptions.exception import BusinessLogicException

bp = Blueprint("analysis", __name__)

# Schema instances
analysis_schema = AudioAnalysisSchema()
file_schema = FileSchema()
status_schema = AnalysisStatusSchema()
cancel_schema = AnalysisCancelSchema()

@bp.route("/analyses", methods=["POST"])
@body(AudioAnalysisSchema)
@response(AudioAnalysisSchema, 201, description="Newly created audio analysis")
@other_responses({
    400: "Invalid input data",
    401: "Unauthorized"
})
def create_analysis(args):
    """Create a new audio analysis"""
    try:
        # Create analysis through service
        analysis = AudioAnalysisService.create_analysis(args)
        return analysis
    except Exception as e:
        current_app.logger.error(e)
        raise e

@bp.route("/analyses", methods=["GET"])
@arguments(AudioAnalysisSchema)
@response(
    get_paginated_schema(AudioAnalysisSchema),
    200,
    description="Success: All analyses retrieved successfully"
)
@other_responses({404: "No analyses found"})
def get_analyses(args):
    """Retrieve all audio analyses"""
    page = args.pop("page", None)
    per_page = args.pop("per_page", None)
    search = args.pop("search", "")
    
    analyses = AudioAnalysisService.search(search=search, **args)
    return paginate_query(query=analyses, page=page, per_page=per_page)

@bp.route("/analyses/<int:id>", methods=["GET"])
@response(AudioAnalysisSchema)
@other_responses({404: "Analysis not found"})
def get_analysis(id):
    """Get complete analysis by ID"""
    analysis = AudioAnalysisService.get(id=id)
    if analysis.status != 'completed':
        raise BusinessLogicException(
            code=400,
            description=_('Analysis not yet completed')
        )
    return analysis

@bp.route("/analyses/<int:id>", methods=["DELETE"])
@response(
    '',
    204,
    description="Analysis deleted successfully"
)
@other_responses({
    404: "Analysis not found",
    401: "Unauthorized"
})
def delete_analysis(id):
    """Delete an audio analysis"""
    try:
        AudioAnalysisService.delete(id=id)
        db.session.commit()
        return '', 204
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        raise e

@bp.route("/analyses/<int:id>/audio", methods=["GET"])
@other_responses({
    404: "Audio file not found",
    401: "Unauthorized"
})
def get_audio_file(id):
    """Get the audio file for an analysis"""
    analysis = AudioAnalysisService.get(id=id)
    if not analysis.audio_file:
        raise BusinessLogicException(_('No audio file found for this analysis'))
        
    return send_file(
        analysis.audio_file.path,
        mimetype=analysis.audio_file.mime_type,
        as_attachment=True,
        download_name=analysis.audio_file.file_name
    )

@bp.route("/analyses/<int:id>/waveform", methods=["GET"])
@other_responses({
    404: "Waveform not found",
    401: "Unauthorized"
})
def get_waveform(id):
    """Get the waveform visualization for an analysis"""
    analysis = AudioAnalysisService.get(id=id)
    if not analysis.waveform_image:
        raise BusinessLogicException(_('No waveform image found for this analysis'))
        
    return send_file(
        analysis.waveform_image.path,
        mimetype=analysis.waveform_image.mime_type,
        as_attachment=False
    ) 

@bp.route("/analyses/<int:id>/status", methods=["GET"])
def get_analysis_status(id):
    """Get the status of an analysis"""
    analysis = AudioAnalysisService.get(id=id)
    
    return jsonify({
        'status': analysis.status,
        'progress': analysis.progress or 0,
        'current_step': analysis.current_step,
        'error': analysis.error_message
    })

@bp.route("/analyses/<int:id>/cancel", methods=["POST"])
def cancel_analysis(id):
    """Cancel an ongoing analysis"""
    analysis = AudioAnalysisService.get(id=id)
    
    # Get task ID from analysis
    task_id = analysis.task_id
    if task_id:
        # Revoke the Celery task
        celery.control.revoke(task_id, terminate=True)
        
    # Update analysis status
    analysis.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'status': 'cancelled'}) 

@bp.route("/analyses/<int:id>/public", methods=["GET"])
@response(AudioAnalysisSchema)
@other_responses({404: "Analysis not found"})
def get_public_analysis(id):
    """Get public analysis by ID"""
    return AudioAnalysisService.get_public(id) 