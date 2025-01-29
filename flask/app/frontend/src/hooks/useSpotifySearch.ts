import { useState, useCallback } from 'react';

export interface SpotifyTrack {
  id: string;
  name: string;
  artists: Array<{
    id: string;
    name: string;
  }>;
  album: {
    id: string;
    name: string;
    images: Array<{
      url: string;
      height: number;
      width: number;
    }>;
  };
  duration_ms: number;
  spotify_info?: {
    id: string;
    name: string;
    artist: string;
    imageUrl: string;
    duration_ms: number;
  };
}

export function useSpotifySearch() {
  const [suggestions, setSuggestions] = useState<SpotifyTrack[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [currentQuery, setCurrentQuery] = useState('');

  const searchTracks = useCallback(async (query: unknown) => {
    // Convert query to string and handle edge cases
    const queryString = typeof query === 'string' ? query : String(query || '');
    const trimmedQuery = queryString.trim();

    // Return early if query is empty after trimming
    if (!trimmedQuery) {
      setSuggestions([]);
      setHasMore(false);
      return;
    }
    
    try {
      setIsLoading(true);
      setCurrentQuery(trimmedQuery);
      setOffset(0);

      const response = await fetch(
        `/api/spotify/search?q=${encodeURIComponent(trimmedQuery)}&offset=0`
      );

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      console.log('Search Response:', data);

      const tracks = data.items || (data.tracks && data.tracks.items) || [];
      console.log('Processed tracks:', tracks);

      setSuggestions(tracks);
      setHasMore(tracks.length === 20);
    } catch (error) {
      console.error('Search error:', error);
      setSuggestions([]);
      setHasMore(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadMore = useCallback(async () => {
    if (!currentQuery || isLoading) return;

    try {
      setIsLoading(true);
      const nextOffset = offset + 20;

      const response = await fetch(
        `/api/spotify/search?q=${encodeURIComponent(currentQuery)}&offset=${nextOffset}`
      );

      if (!response.ok) {
        throw new Error('Load more failed');
      }

      const data = await response.json();
      console.log('Load More Response:', data);

      const tracks = data.items || (data.tracks && data.tracks.items) || [];
      console.log('Processed more tracks:', tracks);

      setSuggestions(prev => [...prev, ...tracks]);
      setHasMore(tracks.length === 20);
      setOffset(nextOffset);
    } catch (error) {
      console.error('Load more error:', error);
    } finally {
      setIsLoading(false);
    }
  }, [currentQuery, offset, isLoading]);

  return {
    suggestions,
    isLoading,
    hasMore,
    searchTracks,
    loadMore,
  };
} 