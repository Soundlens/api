from flask import Blueprint, request, jsonify
from app.api.lastfm.services import LastFmService
from app.exceptions.exception import BusinessLogicException
from flask_babel import gettext as _
from flask import current_app
from app.api.lastfm.schemas import (
    ArtistSchema, LastFmArtistSchema, ArtistInfoSchema,
    RecommendationsSchema, RecommendationsParamsSchema,
    CategoryPlaylistsSchema, CategorySchema, CategoriesResponseSchema
)
from apifairy import response, other_responses, arguments
from flask import url_for
bp = Blueprint('lastfm', __name__)

@bp.route('/artists/<spotify_id>/related-artists', methods=['GET'])
@response(ArtistSchema(many=True))
@other_responses({404: 'Artist not found'})
def get_related_artists(spotify_id):
    """Get related artists using Spotify ID and Last.fm data"""
    try:
        limit = request.args.get('limit', 20, type=int)
        service = LastFmService()
        artists = service.get_spotify_related_with_lastfm(spotify_id, limit)
        return artists
    except BusinessLogicException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting related artists: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/artists/name/<artist_name>/related-artists', methods=['GET'])
@response(LastFmArtistSchema(many=True))
@other_responses({404: 'Artist not found'})
def get_related_artists_by_name(artist_name):
    """Get related artists using artist name"""
    try:
        limit = request.args.get('limit', 20, type=int)
        service = LastFmService()
        artists = service.get_related_by_name(artist_name, limit)
        return {'artists': artists, 'total': len(artists)}
    except BusinessLogicException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting related artists by name: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/recommendations', methods=['GET'])
@arguments(RecommendationsParamsSchema)
@response(RecommendationsSchema)
@other_responses({400: 'Invalid request parameters'})
def get_recommendations(args):
    """Get track recommendations based on seeds"""
    try:
        seed_artists = args.get('seed_artists', '').split(',') if args.get('seed_artists') else None
        seed_genres = args.get('seed_genres', '').split(',') if args.get('seed_genres') else None
        seed_tracks = args.get('seed_tracks', '').split(',') if args.get('seed_tracks') else None
        limit = args.get('limit', 20)
        
        if not any([seed_artists, seed_genres, seed_tracks]):
            raise BusinessLogicException(_('At least one seed (artists, genres, or tracks) is required'))
            
        service = LastFmService()
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

@bp.route('artists/<spotify_id>/info', methods=['GET'])
@response(ArtistSchema)
@other_responses({404: 'Artist not found'})
def get_artist_by_id(spotify_id):
    """Get artist information by Spotify ID"""
    try:
        from app.api.spotify.services import SpotifyService
        service = LastFmService()
        spotify_service = SpotifyService()
        
        # Get artist from Spotify
        artist = spotify_service.get_artist(spotify_id)
        print(f"Spotify artist response: {artist}", flush=True)  # Debug print
        
        if not artist:
            raise BusinessLogicException(_('Artist not found'))
            
        # Get Last.fm info to enhance the data
        lastfm_info = service.get_artist_info(artist['name'])
        print(f"Last.fm info response: {lastfm_info}", flush=True)  # Debug print
        
        # Return Spotify format but with additional Last.fm data if available
        artist_data = {
            'external_urls': {
                'spotify': f"https://open.spotify.com/artist/{artist['id']}"
            },
            'followers': {
                'href': None,
                'total': artist['followers']['total']
            },
            'genres': artist['genres'],
            'href': url_for('api.lastfm.get_artist_by_id', 
                          spotify_id=artist['id'], 
                          _external=True),
            'id': artist['id'],
            'images': artist['images'],
            'name': artist['name'],
            'popularity': artist['popularity'],
            'type': 'artist',
            'uri': artist['uri']
        }
        
        if lastfm_info:
            artist_data['lastfm'] = {
                'url': lastfm_info['url'],
                'listeners': lastfm_info['listeners'],
                'playcount': lastfm_info['playcount'],
                'bio': lastfm_info['bio'],
                'tags': lastfm_info['tags']
            }
            
        return artist_data
        
    except BusinessLogicException as e:
        print(f"Business logic error: {str(e)}", flush=True)  # Debug print
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        print(f"Unexpected error: {str(e)}", flush=True)  # Debug print
        current_app.logger.error(f"Error getting artist info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/categories/<category_id>/playlists', methods=['GET'])
@response(CategoryPlaylistsSchema)
@other_responses({404: 'Category not found'})
def get_category_playlists(category_id):
    """Get playlists for a specific category using Last.fm tags"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        service = LastFmService()
        playlists = service.get_category_playlists(
            category_id=category_id,
            limit=limit,
            offset=offset
        )
        
        if not playlists or not playlists.get('playlists', {}).get('items'):
            raise BusinessLogicException(_('No playlists found for this category'))
            
        return playlists
        
    except BusinessLogicException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting category playlists: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/categories', methods=['GET'])
@response(CategoriesResponseSchema)
def get_categories():
    """Get available categories using Last.fm top tags"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        service = LastFmService()
        categories = service.get_categories(
            limit=limit,
            offset=offset
        )
        
        return categories
        
    except Exception as e:
        current_app.logger.error(f"Error getting categories: {str(e)}")
        return jsonify({'error': str(e)}), 500 