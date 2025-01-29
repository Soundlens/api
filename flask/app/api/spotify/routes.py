from flask import Blueprint, request, jsonify
from app.api.spotify.services import SpotifyService
from app.exceptions.exception import BusinessLogicException
from flask_babel import gettext as _

bp = Blueprint('spotify', __name__)

@bp.route('/spotify/search', methods=['GET'])
def search_tracks():
    """Search for tracks on Spotify"""
    try:
        query = request.args.get('q')
        if not query:
            raise BusinessLogicException(_('Search query is required'))
            
        offset = request.args.get('offset', 0, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        spotify_service = SpotifyService()
        results = spotify_service.search_tracks(query, offset, limit)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/spotify/tracks/<track_id>', methods=['GET'])
def get_track(track_id):
    """Get a specific track by ID"""
    try:
        spotify_service = SpotifyService()
        track = spotify_service.get_track(track_id)
        
        if not track:
            raise BusinessLogicException(_('Track not found'))
            
        return jsonify(track)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 