import { useState, useRef, useEffect } from 'react';
import { useSpotifySearch, SpotifyTrack } from '@/hooks/useSpotifySearch';
import { useDebounce } from '@/hooks/useDebounce';

interface SearchBarProps {
  onSearch: (query: string, spotifyTrack?: SpotifyTrack) => void;
  isLoading: boolean;
  placeholder?: string;
}

export default function SearchBar({ onSearch, isLoading, placeholder = "Search for a song..." }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement>(null);
  
  const { 
    suggestions, 
    isLoading: isSuggestionsLoading, 
    searchTracks,
    loadMore,
    hasMore 
  } = useSpotifySearch();
  
  const debouncedSearchTracks = useDebounce((value: string) => {
    if (value.trim()) {
      searchTracks(value);
    }
  }, 300);

  useEffect(() => {
    if (loadMoreRef.current) {
      observerRef.current = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting && !isSuggestionsLoading && hasMore) {
            loadMore();
          }
        },
        { threshold: 0.5 }
      );

      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [isSuggestionsLoading, hasMore, loadMore]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current && 
        !suggestionsRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setIsOpen(true);
    debouncedSearchTracks(value);
  };

  const handleSuggestionClick = (track: SpotifyTrack) => {
    const searchQuery = `${track.name} - ${track.artists[0].name}`;
    setQuery(searchQuery);
    setIsOpen(false);
    onSearch(searchQuery, {
      ...track,
      spotify_info: {
        id: track.id,
        name: track.name,
        artist: track.artists[0].name,
        imageUrl: track.album.images[0]?.url,
        duration_ms: track.duration_ms
      }
    });
  };

  return (
    <div className="relative w-full max-w-3xl mx-auto" style={{ zIndex: 50 }}>
      {/* Search Container */}
      <div className="relative" style={{ zIndex: 50 }}>
        <form className="relative" onSubmit={(e) => {
          e.preventDefault();
          if (query.trim() && !isLoading) {
            onSearch(query.trim());
            setIsOpen(false);
          }
        }}>
          {/* Search Icon */}
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            <svg 
              className="w-5 h-5 text-gray-400"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" 
              />
            </svg>
          </div>

          {/* Search Input */}
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={handleInputChange}
            onFocus={() => query.trim() && setIsOpen(true)}
            placeholder={placeholder}
            className="w-full pl-12 pr-20 py-4 text-lg rounded-2xl bg-gray-800/95
                     border-2 border-gray-600 focus:border-blue-500 
                     text-white placeholder-gray-400 
                     focus:outline-none focus:ring-2 focus:ring-blue-500/50
                     transition-all duration-300
                     backdrop-blur-sm
                     shadow-xl"
          />

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2
                     px-4 py-2 bg-blue-600 text-white rounded-xl
                     font-medium hover:bg-blue-700 
                     focus:outline-none focus:ring-2 focus:ring-blue-500
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-all duration-300"
          >
            {isLoading ? (
              <div className="flex items-center space-x-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Analyzing</span>
              </div>
            ) : (
              'Analyze'
            )}
          </button>
        </form>

        {/* Suggestions Dropdown */}
        {isOpen && (
          <div 
            ref={suggestionsRef}
            className="absolute w-full mt-2 bg-gray-800/95 backdrop-blur-md 
                     border border-gray-700 rounded-xl shadow-2xl overflow-hidden"
            style={{ 
              zIndex: 51,
              position: 'relative'
            }}
          >
            {isSuggestionsLoading && suggestions.length === 0 ? (
              <div className="p-4 text-center text-gray-400">
                Loading suggestions...
              </div>
            ) : suggestions.length > 0 ? (
              <ul className="max-h-[60vh] overflow-auto">
                {suggestions.map((track) => (
                  <li key={track.id}>
                    <button
                      onClick={() => handleSuggestionClick(track)}
                      className="w-full px-4 py-3 flex items-center gap-4 hover:bg-gray-700/50 transition-colors"
                    >
                      {track.album.images[2] && (
                        <img 
                          src={track.album.images[2].url} 
                          alt={track.album.name}
                          className="w-10 h-10 rounded-lg"
                        />
                      )}
                      <div className="flex-1 text-left">
                        <div className="font-medium text-white">{track.name}</div>
                        <div className="text-sm text-gray-400">
                          {track.artists.map(a => a.name).join(', ')}
                        </div>
                      </div>
                      <div className="text-sm text-gray-400">
                        {Math.round(track.duration_ms / 1000)}s
                      </div>
                    </button>
                  </li>
                ))}
                {/* Load More Trigger */}
                <div 
                  ref={loadMoreRef} 
                  className="p-4 text-center text-gray-400"
                >
                  {isSuggestionsLoading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Loading more...</span>
                    </div>
                  ) : hasMore ? (
                    <span>Scroll for more</span>
                  ) : (
                    <span>No more results</span>
                  )}
                </div>
              </ul>
            ) : query.trim() ? (
              <div className="p-4 text-center text-gray-400">
                No songs found
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* Search Tips */}
      {!isOpen && (
        <div className="mt-2 text-sm text-gray-400 px-4">
          <p>Search for any song to analyze its musical characteristics</p>
        </div>
      )}
    </div>
  );
} 