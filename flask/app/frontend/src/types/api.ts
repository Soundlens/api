export interface VoiceFeatures {
  has_voice: boolean;
  voice_type: string;
  pitch_stats: {
    mean: number;
    min: number;
    max: number;
  };
  intensity: {
    mean: number;
    min: number;
    max: number;
  };
  harmonicity: {
    mean: number;
    min: number;
    max: number;
  };
  detected_language: string;
  transcribed_text: string;
}

export interface TechnicalFeatures {
  duration_ms: number;
  tempo: number;
  key: number;
  mode: number;
  time_signature: number;
  loudness: number;
  acousticness: number;
  danceability: number;
  energy: number;
  instrumentalness: number;
  speechiness: number;
  valence: number;
  voice_features: VoiceFeatures;
}

export interface MoodScores {
  energy: number;
  valence: number;
  arousal: number;
  danceability: number;
  intensity: number;
  mood_tags: string[];
  closest_moods: { 
    mood: string;
    arousal: number;
    valence: number;
    distance: number;
    quadrant: number;
  }[];
  [key: string]: any;
}

export interface Analysis {
  technical_features: TechnicalFeatures;
  mood_scores: MoodScores;
  duration: number;
}

export interface SpotifyTrack {
  id: string;
  name: string;
  artists: { name: string }[];
  album: {
    name: string;
    images: { url: string }[];
  };
  duration_ms: number;
}

export interface AnalysisResponse {
  id: number;
  title: string;
  track_name: string;
  artist?: string;
  image_url?: string;
  duration?: number;
  spotify_info?: SpotifyTrack;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  task_id?: string;
  progress?: number;
  current_step?: string;
  files: any[];
  raw_analysis_data: {
    key: number;
    mode: number;
    mood: string;
    tempo: number;
    energy: number;
    valence: number;
    liveness: number;
    loudness: number;
    segments: any[];
    speechiness: number;
    acousticness: number;
    danceability: number;
    time_signature: number;
    mood_confidence: number;
    instrumentalness: number;
    voice_characteristics: VoiceFeatures;
    raw_analysis_data: {
      analysis: {
        duration: number;
        mood_scores: MoodScores;
        technical_features: {
          key: number;
          mode: number;
          tempo: number;
          energy: number;
          valence: number;
          loudness: number;
          duration_ms: number;
          speechiness: number;
          acousticness: number;
          danceability: number;
          time_signature: number;
          voice_features: VoiceFeatures;
          instrumentalness: number;
          spotify_audio_features: {
            id: string | null;
            key: number;
            uri: string | null;
            mode: number;
            type: string;
            tempo: number;
            energy: number;
            valence: number;
            liveness: number;
            loudness: number;
            track_href: string | null;
            duration_ms: number;
            speechiness: number;
            acousticness: number;
            analysis_url: string | null;
            danceability: number;
            time_signature: number;
            instrumentalness: number;
          };
        };
      };
      timestamp: string;
      audio_file: string;
      track_name: string;
    };
  };
  inserted_at: string;
  updated_at: string;
} 