from flask import Blueprint, request, jsonify, current_app, url_for
from app.exceptions.exception import BusinessLogicException
from flask_babel import gettext as _
from flask import current_app
from app.api.lastfm.schemas import (
    ArtistSchema, RecommendationsSchema, RecommendationsParamsSchema,
    CategoryPlaylistsSchema, CategoriesResponseSchema, AudioFeaturesSchema
)
from apifairy import response, other_responses, arguments
from .services import SpotifyReplacementService
from app.api.analysis.database.models import AudioAnalysis
# from .middleware import require_api_key


bp = Blueprint('spotify_replacement', __name__, url_prefix='/spotify-replacement')

@bp.route('/artists/<spotify_id>/info', methods=['GET'])
@response(ArtistSchema)
# @require_api_key
@other_responses({404: 'Artist not found'})
def get_artist_by_id(spotify_id):
    """Get artist information"""
    try:
        service = SpotifyReplacementService()
        return service.get_artist(spotify_id)
    except BusinessLogicException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting artist: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/artists/<spotify_id>/related-artists', methods=['GET'])
@response(ArtistSchema(many=True))
# @require_api_key
@other_responses({404: 'Artist not found'})
def get_related_artists(spotify_id):
    """Get related artists"""
    try:
        limit = request.args.get('limit', 20, type=int)
        service = SpotifyReplacementService()
        return service.get_related_artists(spotify_id, limit)
    except BusinessLogicException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting related artists: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/recommendations', methods=['GET'])
@arguments(RecommendationsParamsSchema)
@response(RecommendationsSchema)
# @require_api_key
@other_responses({400: 'Invalid request parameters'})
def get_recommendations(args):
    """Get track recommendations"""
    try:
        seed_artists = args.get('seed_artists', '').split(',') if args.get('seed_artists') else None
        seed_genres = args.get('seed_genres', '').split(',') if args.get('seed_genres') else None
        seed_tracks = args.get('seed_tracks', '').split(',') if args.get('seed_tracks') else None
        limit = args.get('limit', 20)
        
        if not any([seed_artists, seed_genres, seed_tracks]):
            raise BusinessLogicException(_('At least one seed is required'))
            
        service = SpotifyReplacementService()
        return service.get_recommendations(
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            seed_tracks=seed_tracks,
            limit=limit
        )
    except BusinessLogicException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/browse/categories', methods=['GET'])
@response(CategoriesResponseSchema)
# @require_api_key
def get_categories():
    """Get available categories"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        service = SpotifyReplacementService()
        return service.get_categories(limit=limit, offset=offset)
    except Exception as e:
        current_app.logger.error(f"Error getting categories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/browse/categories/<category_id>/playlists', methods=['GET'])
@response(CategoryPlaylistsSchema)
# @require_api_key
@other_responses({404: 'Category not found'})
def get_category_playlists(category_id):
    """Get category playlists"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        service = SpotifyReplacementService()
        playlists = service.get_category_playlists(
            category_id=category_id,
            limit=limit,
            offset=offset
        )
        
        if not playlists or not playlists.get('playlists', {}).get('items'):
            raise BusinessLogicException(_('No playlists found'))
            
        return playlists
    except BusinessLogicException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting category playlists: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/audio-features/<track_id>', methods=['GET'])
@response(AudioFeaturesSchema)
# @require_api_key
@other_responses({404: 'Track not found'})
def get_audio_features(track_id):
    """Get audio features for a track"""
    try:
        service = SpotifyReplacementService()
        return service.get_audio_features(track_id)
    except BusinessLogicException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting audio features: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/audio-features/<track_id>/status', methods=['GET'])
@other_responses({404: 'Track not found'})
# @require_api_key
def get_audio_features_status(track_id):
    """Get the status of audio feature analysis"""
    try:
        analysis = AudioAnalysis.query.filter_by(spotify_id=track_id).first()
        if not analysis:
            return jsonify({
                'id': track_id,
                'status': 'not_found',
                'error': 'Analysis not found'
            })

        response = {
            'id': track_id,
            'status': analysis.status,
            'progress': analysis.progress,
            'current_step': analysis.current_step
        }

        # If analysis is complete, include the features
        if analysis.status == 'completed' and analysis.raw_analysis_data:
            spotify_features = analysis.raw_analysis_data.get('analysis', {}).get('spotify_audio_features', {})
            if spotify_features:
                # Update the URLs to point to our endpoints
                spotify_features['analysis_url'] = url_for('api.spotify_replacement.get_audio_features_status', 
                                                         track_id=track_id, 
                                                         _external=True)
                spotify_features['track_href'] = url_for('api.spotify_replacement.get_audio_features', 
                                                       track_id=track_id, 
                                                       _external=True)
                response['features'] = spotify_features
        elif analysis.status == 'failed':
            response['error'] = analysis.error_message
            
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Error getting analysis status: {str(e)}")
        return jsonify({'error': str(e)}), 500 