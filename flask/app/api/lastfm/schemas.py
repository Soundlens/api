from app import ma
from marshmallow import fields, validate
from flask_babel import lazy_gettext as _

class ImageSchema(ma.Schema):
    """Schema for image objects"""
    url = ma.String(required=True)
    height = ma.Integer(required=True)
    width = ma.Integer(required=True)

class ExternalUrlsSchema(ma.Schema):
    """Schema for external URLs"""
    spotify = ma.String(required=True)

class FollowersSchema(ma.Schema):
    """Schema for followers information"""
    href = ma.String(allow_none=True)
    total = ma.Integer(required=True)

class ArtistSchema(ma.Schema):
    """Schema for Spotify artist format"""
    external_urls = fields.Nested(ExternalUrlsSchema, required=True)
    followers = fields.Nested(FollowersSchema, required=True)
    genres = fields.List(fields.String(), required=True)
    href = ma.String(required=True)
    id = ma.String(required=True)
    images = fields.List(fields.Nested(ImageSchema), required=True)
    name = ma.String(required=True)
    popularity = ma.Integer(required=True)
    type = ma.String(required=True)
    uri = ma.String(required=True)

class LastFmArtistSchema(ma.Schema):
    """Schema for Last.fm artist format"""
    name = ma.String(required=True)
    match = ma.Float(required=True)
    lastfm_url = ma.String(required=True)
    image_url = ma.String(allow_none=True)
    # Optional Spotify data
    id = ma.String(required=False)
    uri = ma.String(required=False)
    spotify_followers = ma.Integer(required=False)
    spotify_popularity = ma.Integer(required=False)
    genres = fields.List(fields.String(), required=False)
    images = fields.List(fields.Nested(ImageSchema), required=False)

class ArtistInfoSchema(ma.Schema):
    """Schema for detailed artist information"""
    name = ma.String(required=True)
    image_url = ma.String(allow_none=True)
    url = ma.String(required=True)
    listeners = ma.Integer(required=True)
    playcount = ma.Integer(required=True)
    bio = ma.String(allow_none=True)
    tags = fields.List(fields.String(), required=True)
    # Optional Spotify data
    spotify_id = ma.String(required=False)
    spotify_uri = ma.String(required=False)
    spotify_followers = ma.Integer(required=False)
    spotify_popularity = ma.Integer(required=False)
    genres = fields.List(fields.String(), required=False)
    spotify_image_url = ma.String(allow_none=True)

class AlbumArtistSchema(ma.Schema):
    """Schema for album artist objects"""
    external_urls = fields.Nested(ExternalUrlsSchema, required=True)
    href = ma.String(required=True)
    id = ma.String(required=True)
    name = ma.String(required=True)
    type = ma.String(required=True)
    uri = ma.String(required=True)

class AlbumSchema(ma.Schema):
    """Schema for album objects"""
    album_type = ma.String(required=True)
    total_tracks = ma.Integer(required=True)
    available_markets = fields.List(fields.String(), required=True)
    external_urls = fields.Nested(ExternalUrlsSchema, required=True)
    href = ma.String(required=True)
    id = ma.String(required=True)
    images = fields.List(fields.Nested(ImageSchema), required=True)
    name = ma.String(required=True)
    release_date = ma.String(required=True)
    release_date_precision = ma.String(required=True)
    type = ma.String(required=True)
    uri = ma.String(required=True)
    artists = fields.List(fields.Nested(AlbumArtistSchema), required=True)

class TrackSchema(ma.Schema):
    """Schema for track objects"""
    album = fields.Nested(AlbumSchema, required=True)
    artists = fields.List(fields.Nested(AlbumArtistSchema), required=True)
    available_markets = fields.List(fields.String(), required=True)
    disc_number = ma.Integer(required=True)
    duration_ms = ma.Integer(required=True)
    explicit = ma.Boolean(required=True)
    external_urls = fields.Nested(ExternalUrlsSchema, required=True)
    href = ma.String(required=True)
    id = ma.String(required=True)
    name = ma.String(required=True)
    popularity = ma.Integer(required=True)
    preview_url = ma.String(allow_none=True)
    track_number = ma.Integer(required=True)
    type = ma.String(required=True)
    uri = ma.String(required=True)
    is_local = ma.Boolean(required=True)

class SeedSchema(ma.Schema):
    """Schema for recommendation seeds"""
    afterFilteringSize = ma.Integer(required=True)
    afterRelinkingSize = ma.Integer(required=True)
    href = ma.String(required=True)
    id = ma.String(required=True)
    initialPoolSize = ma.Integer(required=True)
    type = ma.String(required=True)

class RecommendationsSchema(ma.Schema):
    """Schema for recommendations response"""
    seeds = fields.List(fields.Nested(SeedSchema), required=True)
    tracks = fields.List(fields.Nested(TrackSchema), required=True)

class RecommendationsParamsSchema(ma.Schema):
    """Schema for recommendations request parameters"""
    seed_artists = ma.String(
        required=False,
        validate=validate.Length(max=500),
        metadata={"description": "Comma-separated Spotify artist IDs"}
    )
    seed_genres = ma.String(
        required=False,
        validate=validate.Length(max=500),
        metadata={"description": "Comma-separated genre names"}
    )
    seed_tracks = ma.String(
        required=False,
        validate=validate.Length(max=500),
        metadata={"description": "Comma-separated Spotify track IDs"}
    )
    limit = ma.Integer(
        required=False,
        validate=validate.Range(min=1, max=100),
        metadata={"description": "Number of tracks to return"}
    )

class PlaylistTrackSchema(ma.Schema):
    """Schema for simplified playlist track objects"""
    href = ma.String(required=True)
    total = ma.Integer(required=True)

class PlaylistSchema(ma.Schema):
    """Schema for playlist objects"""
    collaborative = ma.Boolean(required=True)
    description = ma.String(required=True, allow_none=True)
    external_urls = fields.Nested(ExternalUrlsSchema, required=True)
    href = ma.String(required=True)
    id = ma.String(required=True)
    images = fields.List(fields.Nested(ImageSchema), required=True)
    name = ma.String(required=True)
    owner = fields.Nested(FollowersSchema, required=True)
    public = ma.Boolean(required=True, allow_none=True)
    snapshot_id = ma.String(required=True)
    tracks = fields.Nested(PlaylistTrackSchema, required=True)
    type = ma.String(required=True)
    uri = ma.String(required=True)

class CategoryPlaylistsSchema(ma.Schema):
    """Schema for category playlists response"""
    playlists = fields.Nested(PlaylistSchema(many=True), required=True)

class CategorySchema(ma.Schema):
    """Schema for category objects"""
    href = ma.String(required=True)
    icons = fields.List(fields.Nested(ImageSchema), required=True)
    id = ma.String(required=True)
    name = ma.String(required=True)

class CategoriesResponseSchema(ma.Schema):
    """Schema for categories response"""
    categories = fields.Nested(CategorySchema(many=True), required=True)

class AudioFeaturesSchema(ma.Schema):
    """Schema for audio features response"""
    acousticness = ma.Float(required=True)
    analysis_url = ma.String(allow_none=True)
    danceability = ma.Float(required=True)
    duration_ms = ma.Integer(required=True)
    energy = ma.Float(required=True)
    id = ma.String(required=True)
    instrumentalness = ma.Float(required=True)
    key = ma.Integer(required=True)
    liveness = ma.Float(required=True)
    loudness = ma.Float(required=True)
    mode = ma.Integer(required=True)
    speechiness = ma.Float(required=True)
    tempo = ma.Float(required=True)
    time_signature = ma.Integer(required=True)
    track_href = ma.String(allow_none=True)
    type = ma.String(required=True)
    uri = ma.String(required=True)
    valence = ma.Float(required=True) 