import { AnalysisResponse } from '@/types/api';
import ProgressBar from './ProgressBar';

interface SongListProps {
  songs: AnalysisResponse[];
  onRemove: (index: number) => void;
}

export default function SongList({ songs, onRemove }: SongListProps) {
  if (songs.length === 0) return null;

  const getVoiceType = (song: AnalysisResponse) => {
    try {
      return song.raw_analysis_data?.voice_characteristics?.has_voice ? 'Voice' : 'Instrumental';
    } catch {
      return 'Unknown';
    }
  };

  const getDuration = (song: AnalysisResponse) => {
    try {
      return Math.round(song.raw_analysis_data?.raw_analysis_data?.analysis?.duration || 0);
    } catch {
      return 0;
    }
  };

  const getTempo = (song: AnalysisResponse) => {
    try {
      return Math.round(song.raw_analysis_data?.tempo || 0);
    } catch {
      return 0;
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto mt-8">
      <div className="bg-gray-800/30 rounded-xl p-4">
        <h3 className="text-lg font-semibold text-gray-300 mb-4">
          Analyzed Songs ({songs.length})
        </h3>
        
        <div className="space-y-4">
          {songs.map((song, index) => (
            <div
              key={index}
              className="flex flex-col gap-4 p-4 rounded-lg bg-gray-700/30
                       hover:bg-gray-700/50 transition-colors duration-200"
              style={{
                borderLeft: `4px solid hsla(${index * 137.5}, 70%, 50%, 0.8)`,
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {song.image_url && (
                    <img
                      src={song.image_url}
                      alt={song.title}
                      width={48}
                      height={48}
                      className="rounded-lg object-cover"
                    />
                  )}
                  <div>
                    <div className="font-medium text-white">{song.title}</div>
                    <div className="text-sm text-gray-400 space-x-2">
                      <span>{song.artist}</span>
                      {song.status === 'completed' && song.raw_analysis_data && (
                        <>
                          <span>•</span>
                          <span>{getDuration(song)}s</span>
                          <span>•</span>
                          <span>{getVoiceType(song)}</span>
                          <span>•</span>
                          <span>{getTempo(song)} BPM</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => onRemove(index)}
                  className="p-2 text-gray-400 hover:text-red-500 rounded-lg
                           hover:bg-gray-600/30 transition-all duration-200"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>

              {/* Progress Bar */}
              {song.status !== 'completed' && (
                <ProgressBar 
                  progress={song.progress || 0}
                  status={song.status}
                  currentStep={song.current_step}
                  error={song.error_message}
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 