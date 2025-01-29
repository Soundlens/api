from typing import List, Dict, Any, Optional
from flask import current_app, url_for
from app.api.spotify.services import SpotifyService
from app.api.lastfm.services import LastFmService
from app.exceptions import BusinessLogicException
from flask_babel import _
from app.api.analysis.analyzer import AudioAnalyzer
from app.api.analysis.services.analysis_service import AudioAnalysisService
from app.api.analysis.database.models import AudioAnalysis
from sqlalchemy import and_
from app.main import db
import os

class SpotifyReplacementService:
    """Service that combines Spotify and Last.fm functionality"""
    
    def __init__(self):
        self.spotify_service = SpotifyService()
        self.lastfm_service = LastFmService()
    
    def get_artist(self, spotify_id: str) -> Dict[str, Any]:
        """Get artist info combining Spotify and Last.fm data"""
        artist = self.spotify_service.get_artist(spotify_id)
        if not artist:
            raise BusinessLogicException(_('Artist not found'))
            
        # Get Last.fm info to enhance the data
        lastfm_info = self.lastfm_service.get_artist_info(artist['name'])
        
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
            'href': url_for('api.spotify_replacement.get_artist', 
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
    
    def get_related_artists(self, spotify_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get related artists using Last.fm data"""
        return self.lastfm_service.get_spotify_related_with_lastfm(spotify_id, limit)
    
    def get_recommendations(self, seed_artists: List[str] = None, 
                          seed_genres: List[str] = None, 
                          seed_tracks: List[str] = None,
                          limit: int = 20) -> Dict[str, Any]:
        """Get recommendations using Last.fm and Spotify"""
        return self.lastfm_service.get_recommendations(
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            seed_tracks=seed_tracks,
            limit=limit
        )
    
    def get_categories(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get categories from Last.fm tags"""
        return self.lastfm_service.get_categories(limit=limit, offset=offset)
    
    def get_category_playlists(self, category_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get category playlists from Last.fm"""
        return self.lastfm_service.get_category_playlists(
            category_id=category_id,
            limit=limit,
            offset=offset
        )
    
    def get_audio_features(self, track_id: str) -> Dict[str, Any]:
        """Get audio features for a track"""
        try:
            # First get the track from Spotify
            print(f"Getting track {track_id} from Spotify", flush=True)
            track = self.spotify_service.get_track(track_id)
            if not track:
                raise BusinessLogicException(_('Track not found'))

            # Check if we already analyzed this track
            existing_analysis = AudioAnalysis.query.filter(
                and_(
                    AudioAnalysis.spotify_id == track_id,
                    AudioAnalysis.status == 'completed'
                )
            ).first()

            print("********************", flush=True)
            print(existing_analysis, flush=True)
            print("********************", flush=True)

            if existing_analysis and existing_analysis.raw_analysis_data:
                # Get technical features directly from raw_analysis_data
                features = existing_analysis.raw_analysis_data.get('raw_analysis_data', {}).get('analysis', {}).get('technical_features', {})
                if features:
                    # Add track-specific fields
                    features['id'] = track_id
                    features['uri'] = f"spotify:track:{track_id}"
                    features['track_href'] = url_for('api.spotify_replacement.get_audio_features', 
                                                   track_id=track_id, 
                                                   _external=True)
                    features['analysis_url'] = url_for('api.spotify_replacement.get_audio_features_status', 
                                                     track_id=track_id, 
                                                     _external=True)
                    
                    # Ensure all required Spotify fields are present
                    spotify_format = {
                        'acousticness': features.get('acousticness', 0.0),
                        'danceability': features.get('danceability', 0.0),
                        'duration_ms': features.get('duration_ms', 0),
                        'energy': features.get('energy', 0.0),
                        'instrumentalness': features.get('instrumentalness', 0.0),
                        'key': features.get('key', 0),
                        'liveness': features.get('liveness', 0.0),
                        'loudness': features.get('loudness', 0.0),
                        'mode': features.get('mode', 0),
                        'speechiness': features.get('speechiness', 0.0),
                        'tempo': features.get('tempo', 0.0),
                        'time_signature': features.get('time_signature', 4),
                        'valence': features.get('valence', 0.0),
                        'id': track_id,
                        'uri': f"spotify:track:{track_id}",
                        'track_href': url_for('api.spotify_replacement.get_audio_features', 
                                            track_id=track_id, 
                                            _external=True),
                        'analysis_url': url_for('api.spotify_replacement.get_audio_features_status', 
                                              track_id=track_id, 
                                              _external=True),
                        'type': 'audio_features'
                    }
                    return spotify_format
            
            # If no existing analysis or no features, create new analysis
            analysis_data = {
                'title': f"{track['artists'][0]['name']} - {track['name']}",
                'artist': track['artists'][0]['name'],
                'track_name': track['name'],
                'spotify_info': {
                    'id': track_id,
                    'name': track['name'],
                    'imageUrl': track['album']['images'][0]['url'] if track['album'].get('images') else None,
                },
            }

            # Create the analysis asynchronously
            analysis = AudioAnalysisService.create_analysis(analysis_data)
            
            # Return immediately with a pending status
            return {
                'id': track_id,
                'type': 'audio_features',
                'analysis_url': url_for('api.spotify_replacement.get_audio_features_status', 
                                      track_id=track_id, 
                                      _external=True),
                'track_href': url_for('api.spotify_replacement.get_audio_features', 
                                    track_id=track_id, 
                                    _external=True),
                'uri': f"spotify:track:{track_id}",
                'status': 'pending'
            }
                
        except Exception as e:
            current_app.logger.error(f"Error getting audio features: {str(e)}")
            raise e
 