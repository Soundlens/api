import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import current_app
from typing import List, Dict, Any, Optional

class SpotifyService:
    def __init__(self):
        client_credentials_manager = SpotifyClientCredentials(
            client_id=current_app.config['SPOTIFY_CLIENT_ID'],
            client_secret=current_app.config['SPOTIFY_CLIENT_SECRET']
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def search_tracks(self, query: str, offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Search for tracks on Spotify"""
        try:
            results = self.sp.search(
                q=query,
                type='track',
                offset=offset,
                limit=limit
            )
            
            # Format the response
            tracks = results['tracks']['items']
            formatted_tracks = []
            
            for track in tracks:
                formatted_tracks.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artists': [{'name': artist['name']} for artist in track['artists']],
                    'album': {
                        'name': track['album']['name'],
                        'images': track['album']['images']
                    },
                    'duration_ms': track['duration_ms']
                })
            
            return {
                'tracks': {
                    'items': formatted_tracks,
                    'total': results['tracks']['total'],
                    'offset': offset,
                    'limit': limit
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Spotify search error: {str(e)}")
            raise e

    def get_track(self, track_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific track by ID"""
        try:
            track = self.sp.track(track_id)
            return {
                'id': track['id'],
                'name': track['name'],
                'artists': [{'name': artist['name']} for artist in track['artists']],
                'album': {
                    'name': track['album']['name'],
                    'images': track['album']['images']
                },
                'duration_ms': track['duration_ms']
            }
        except Exception as e:
            current_app.logger.error(f"Spotify get track error: {str(e)}")
            return None 

    def search_artist(self, artist_name: str) -> Dict[str, Any]:
        """Search for an artist on Spotify"""
        try:
            results = self.sp.search(
                q=artist_name,
                type='artist',
                limit=1
            )
            return results
        except Exception as e:
            current_app.logger.error(f"Spotify search artist error: {str(e)}")
            return {'artists': {'items': []}}

    def get_artist(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific artist by Spotify ID"""
        try:
            print(f"Getting artist with ID: {artist_id}", flush=True)  # Debug print
            artist = self.sp.artist(artist_id)
            print(f"Spotify response: {artist}", flush=True)  # Debug print
            return artist
        except Exception as e:
            current_app.logger.error(f"Spotify get artist error: {str(e)}")
            print(f"Error getting artist from Spotify: {str(e)}", flush=True)  # Debug print
            return None

    def get_artist_related(self, artist_id: str) -> List[Dict[str, Any]]:
        """Get related artists from Spotify"""
        try:
            related = self.sp.artist_related_artists(artist_id)
            return related.get('artists', [])
        except Exception as e:
            current_app.logger.error(f"Spotify get related artists error: {str(e)}")
            return []

    def get_recommendations(self, seed_artists: List[str] = None, 
                           seed_genres: List[str] = None, 
                           seed_tracks: List[str] = None,
                           limit: int = 20) -> Dict[str, Any]:
        """Get recommendations from Spotify"""
        try:
            # Clean up empty seeds
            if seed_artists:
                seed_artists = [a for a in seed_artists if a]
            if seed_genres:
                seed_genres = [g for g in seed_genres if g]
            if seed_tracks:
                seed_tracks = [t for t in seed_tracks if t]
            
            print(f"Getting recommendations with: artists={seed_artists}, genres={seed_genres}, tracks={seed_tracks}", flush=True)
            
            recommendations = self.sp.recommendations(
                seed_artists=seed_artists if seed_artists else None,
                seed_genres=seed_genres if seed_genres else None,
                seed_tracks=seed_tracks if seed_tracks else None,
                limit=limit
            )
            
            print(f"Got {len(recommendations.get('tracks', []))} recommendations from Spotify", flush=True)
            
            return recommendations
            
        except Exception as e:
            current_app.logger.error(f"Spotify recommendations error: {str(e)}")
            print(f"Spotify recommendations error: {str(e)}", flush=True)
            return {'tracks': []}

    def get_category_playlists(self, category_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get a category's playlists"""
        try:
            print(f"Getting playlists for category: {category_id}", flush=True)
            playlists = self.sp.category_playlists(
                category_id=category_id,
                limit=limit,
                offset=offset
            )
            print(f"Got {len(playlists.get('playlists', {}).get('items', []))} playlists", flush=True)
            return playlists
        except Exception as e:
            current_app.logger.error(f"Spotify category playlists error: {str(e)}")
            print(f"Error getting category playlists: {str(e)}", flush=True)
            return {'playlists': {'items': []}}

    def get_categories(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get Spotify categories"""
        try:
            categories = self.sp.categories(
                limit=limit,
                offset=offset
            )
            return categories
        except Exception as e:
            current_app.logger.error(f"Spotify categories error: {str(e)}")
            return {'categories': {'items': []}}