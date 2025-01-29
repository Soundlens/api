import requests
from flask import current_app, url_for
from typing import List, Dict, Any, Optional
from flask_babel import _
from app.api.spotify.services import SpotifyService
from app.exceptions import BusinessLogicException

class LastFmService:
    def __init__(self):
        self.api_key = current_app.config['LASTFM_API_KEY']
        self.base_url = "http://ws.audioscrobbler.com/2.0/"
        self.spotify_service = SpotifyService()
        self.api_base_url = current_app.config.get('API_URL', '')  # Get base API URL from config
        
    def get_related_artists(self, artist_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get related artists from Last.fm"""
        try:
            params = {
                'method': 'artist.getsimilar',
                'artist': artist_name,
                'api_key': self.api_key,
                'format': 'json',
                'limit': limit
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Format the response
            similar_artists = data.get('similarartists', {}).get('artist', [])
            formatted_artists = []
            
            for artist in similar_artists:
                # Get the largest image available
                images = artist.get('image', [])
                image_url = next((img['#text'] for img in reversed(images) if img['#text']), None)
                
                formatted_artists.append({
                    'name': artist['name'],
                    'match': float(artist['match']),
                    'image_url': image_url,
                    'url': artist['url']
                })
            
            return formatted_artists
            
        except Exception as e:
            current_app.logger.error(f"Last.fm get related artists error: {str(e)}")
            return []

    def get_artist_info(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed artist information from Last.fm"""
        try:
            params = {
                'method': 'artist.getinfo',
                'artist': artist_name,
                'api_key': self.api_key,
                'format': 'json'
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            artist_data = data.get('artist', {})
            if not artist_data:
                return None
                
            # Get the largest image available
            images = artist_data.get('image', [])
            image_url = next((img['#text'] for img in reversed(images) if img['#text']), None)
            
            return {
                'name': artist_data['name'],
                'image_url': image_url,
                'url': artist_data['url'],
                'listeners': int(artist_data.get('stats', {}).get('listeners', 0)),
                'playcount': int(artist_data.get('stats', {}).get('playcount', 0)),
                'bio': artist_data.get('bio', {}).get('summary'),
                'tags': [tag['name'] for tag in artist_data.get('tags', {}).get('tag', [])]
            }
            
        except Exception as e:
            current_app.logger.error(f"Last.fm get artist info error: {str(e)}")
            return None 

    def get_spotify_related_with_lastfm(self, spotify_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get related artists using Spotify ID and enhancing with Last.fm data"""
        # First get the artist from Spotify
        artist = self.spotify_service.get_artist(spotify_id)
        if not artist:
            raise BusinessLogicException(_('Artist not found'))
        
        # Get related artists from Last.fm
        lastfm_related = self.get_related_artists(artist['name'], limit=limit)
        if not lastfm_related:
            raise BusinessLogicException(_('No related artists found'))
        
        # Format results in Spotify's structure
        artists = []
        
        for lastfm_artist in lastfm_related:
            # Get artist directly from Spotify by searching
            spotify_results = self.spotify_service.search_artist(lastfm_artist['name'])
            spotify_data = spotify_results.get('artists', {}).get('items', [])
            
            if spotify_data:
                spotify_artist = spotify_data[0]  # Get first match
                # Get full artist data from Spotify
                full_artist = self.spotify_service.get_artist(spotify_artist['id'])
                if full_artist:
                    artist_data = {
                        'external_urls': {
                            'spotify': f"https://open.spotify.com/artist/{full_artist['id']}"
                        },
                        'followers': {
                            'href': None,
                            'total': full_artist['followers']['total']
                        },
                        'genres': full_artist['genres'],
                        'href': url_for('api.spotify_replacement.get_artist_by_id', 
                                      spotify_id=full_artist['id'], 
                                      _external=True),  # Generate full URL
                        'id': full_artist['id'],
                        'images': full_artist['images'],
                        'name': full_artist['name'],
                        'popularity': full_artist['popularity'],
                        'type': 'artist',
                        'uri': full_artist['uri']
                    }
                    artists.append(artist_data)
        
        # Sort by Last.fm match score and Spotify popularity
        artists.sort(key=lambda x: (
            x['popularity'] * 0.3 + 
            float(next((a['match'] for a in lastfm_related if a['name'] == x['name']), 0)) * 100 * 0.7
        ), reverse=True)
        
        return artists[:limit]

    def get_related_by_name(self, artist_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get related artists using artist name (Last.fm based with Spotify enhancement)"""
        # Get Last.fm related artists
        lastfm_related = self.get_related_artists(artist_name, limit=limit)
        if not lastfm_related:
            raise BusinessLogicException(_('No related artists found'))
        
        enhanced_artists = []
        
        for lastfm_artist in lastfm_related:
            # Search for artist on Spotify
            spotify_results = self.spotify_service.search_artist(lastfm_artist['name'])
            spotify_data = spotify_results.get('artists', {}).get('items', [])
            
            enhanced_artist = {
                'name': lastfm_artist['name'],
                'match': lastfm_artist['match'],
                'lastfm_url': lastfm_artist['url'],
                'image_url': lastfm_artist['image_url'],
            }
            
            # Add Spotify data if available
            if spotify_data:
                spotify_artist = spotify_data[0]
                enhanced_artist.update({
                    'id': spotify_artist['id'],
                    'uri': spotify_artist['uri'],
                    'spotify_followers': spotify_artist['followers']['total'],
                    'spotify_popularity': spotify_artist['popularity'],
                    'genres': spotify_artist['genres'],
                    'images': spotify_artist['images'],
                })
                
                if spotify_artist['images']:
                    enhanced_artist['image_url'] = spotify_artist['images'][0]['url']
            
            enhanced_artists.append(enhanced_artist)
        
        # Sort by Last.fm match score and Spotify popularity
        enhanced_artists.sort(key=lambda x: (
            float(x['match']) * 0.7 + 
            (x.get('spotify_popularity', 0) / 100 * 0.3)
        ), reverse=True)
        
        return enhanced_artists[:limit]

    def get_recommendations(self, seed_artists: List[str] = None, 
                           seed_genres: List[str] = None, 
                           seed_tracks: List[str] = None,
                           limit: int = 20) -> Dict[str, Any]:
        """Get recommendations using Last.fm and Spotify"""
        try:
            all_tracks = []
            seeds = []
            
            # Get recommendations based on seed artists
            if seed_artists and seed_artists[0]:
                for artist_id in seed_artists:
                    artist = self.spotify_service.get_artist(artist_id)
                    if artist:
                        similar_artists = self.get_related_artists(artist['name'], limit=5)
                        
                        # Add seed info with correct endpoint
                        seeds.append({
                            'afterFilteringSize': len(similar_artists),
                            'afterRelinkingSize': len(similar_artists),
                            'href': url_for('api.spotify_replacement.get_artist_by_id', 
                                          spotify_id=artist_id, 
                                          _external=True),
                            'id': artist_id,
                            'initialPoolSize': len(similar_artists),
                            'type': 'artist'
                        })
                        
                        # Get tracks from similar artists
                        for similar in similar_artists:
                            spotify_results = self.spotify_service.search_artist(similar['name'])
                            if spotify_results.get('artists', {}).get('items'):
                                similar_artist = spotify_results['artists']['items'][0]
                                top_tracks = self.spotify_service.sp.artist_top_tracks(similar_artist['id'])['tracks']
                                all_tracks.extend(top_tracks[:2])
            
            # Add genre seeds
            if seed_genres and seed_genres[0]:
                spotify_genre_tracks = self.spotify_service.get_recommendations(
                    seed_genres=seed_genres,
                    limit=limit
                )
                all_tracks.extend(spotify_genre_tracks.get('tracks', []))
                
                for genre in seed_genres:
                    seeds.append({
                        'afterFilteringSize': 0,
                        'afterRelinkingSize': 0,
                        'href': url_for('api.spotify.get_genre', 
                                      genre=genre, 
                                      _external=True),
                        'id': genre,
                        'initialPoolSize': 0,
                        'type': 'genre'
                    })
            
            # Add track seeds
            if seed_tracks and seed_tracks[0]:
                spotify_track_recommendations = self.spotify_service.get_recommendations(
                    seed_tracks=seed_tracks,
                    limit=limit
                )
                all_tracks.extend(spotify_track_recommendations.get('tracks', []))
                
                for track_id in seed_tracks:
                    seeds.append({
                        'afterFilteringSize': 0,
                        'afterRelinkingSize': 0,
                        'href': url_for('api.spotify.get_track', 
                                      track_id=track_id, 
                                      _external=True),
                        'id': track_id,
                        'initialPoolSize': 0,
                        'type': 'track'
                    })
            
            # Remove duplicates
            seen_tracks = set()
            unique_tracks = []
            for track in all_tracks:
                if track['id'] not in seen_tracks:
                    seen_tracks.add(track['id'])
                    unique_tracks.append(track)
            
            print(f"Seeds: {seeds}", flush=True)
            print(f"Number of tracks found: {len(unique_tracks)}", flush=True)
            
            return {
                'seeds': seeds,
                'tracks': unique_tracks[:limit]
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting recommendations: {str(e)}")
            print(f"Recommendation error: {str(e)}", flush=True)
            raise e

    def get_category_playlists(self, category_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get playlists based on Last.fm tags/categories"""
        try:
            # Use Last.fm tag.gettoptracks to get tracks for this category/tag
            params = {
                'method': 'tag.gettoptracks',
                'tag': category_id,
                'api_key': self.api_key,
                'format': 'json',
                'limit': limit,
                'page': (offset // limit) + 1
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            tracks = data.get('tracks', {}).get('track', [])
            
            # Create a playlist-like structure from the tracks
            playlist = {
                'playlists': {
                    'items': [{
                        'collaborative': False,
                        'description': f"Top tracks for category {category_id}",
                        'external_urls': {
                            'spotify': None
                        },
                        'href': url_for('api.spotify_replacement.get_category_playlists', 
                                      category_id=category_id, 
                                      _external=True),
                        'id': f"lastfm-{category_id}",
                        'images': [{'url': track.get('image', [{}])[-1].get('#text')} 
                                 for track in tracks[:4] if track.get('image')],
                        'name': f"Top {category_id} Tracks",
                        'owner': {
                            'href': None,
                            'total': len(tracks)
                        },
                        'public': True,
                        'snapshot_id': None,
                        'tracks': {
                            'href': url_for('api.spotify_replacement.get_category_tracks', 
                                          category_id=category_id, 
                                          _external=True),
                            'total': len(tracks)
                        },
                        'type': 'playlist',
                        'uri': None
                    }],
                    'total': 1,
                    'limit': limit,
                    'offset': offset
                }
            }
            
            return playlist
            
        except Exception as e:
            current_app.logger.error(f"Last.fm category playlists error: {str(e)}")
            print(f"Error getting category playlists: {str(e)}", flush=True)
            return {'playlists': {'items': []}}

    def get_categories(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get available categories from Last.fm top tags"""
        try:
            params = {
                'method': 'tag.getTopTags',
                'api_key': self.api_key,
                'format': 'json',
                'limit': limit,
                'page': (offset // limit) + 1
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            tags = data.get('toptags', {}).get('tag', [])
            
            return {
                'categories': {
                    'items': [{
                        'href': url_for('api.spotify_replacement.get_category_playlists', 
                                      category_id=tag['name'], 
                                      _external=True),
                        'icons': [{
                            'url': 'https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png'
                        }],
                        'id': tag['name'],
                        'name': tag['name']
                    } for tag in tags],
                    'total': len(tags),
                    'limit': limit,
                    'offset': offset
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Last.fm categories error: {str(e)}")
            return {'categories': {'items': []}}