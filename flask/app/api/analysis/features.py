import numpy as np
from typing import Dict, Any, List
from .backends import AudioBackend
import librosa
import platform
import time

class FeatureExtractor:
    """Component for extracting audio features using configurable backend"""
    
    def __init__(self, backend: AudioBackend):
        """Initialize with audio analysis backend"""
        self.backend = backend
        self.progress_callback = None
        
    def set_progress_callback(self, callback):
        """Set progress callback function"""
        self.progress_callback = callback
        self.backend.set_progress_callback(callback)

    def extract_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract all audio features using the configured backend"""
        try:
            # Ensure input is numpy array with correct dtype
            y = np.asarray(y, dtype=np.float32)
            
            if self.progress_callback:
                self.progress_callback(0, "Starting feature extraction")
            
            # Print debug info
            print(f"\nInput audio shape: {y.shape}")
            print(f"Input audio dtype: {y.dtype}")
            print(f"Sample rate: {sr}")
            
            # Extract each feature using the configured backend
            features = {
                'duration_ms': int(len(y) / sr * 1000),
                'tempo': self.backend.extract_tempo(y, sr),
                'energy': self.backend.extract_energy(y, sr),
                'loudness': self.backend.extract_loudness(y, sr),
                'key': self.backend.extract_key(y, sr),
                'mode': self.backend.extract_mode(y, sr),
                'time_signature': self.backend.extract_time_signature(y, sr),
                'acousticness': self.backend.extract_acousticness(y, sr),
                'instrumentalness': self.backend.extract_instrumentalness(y, sr),
                'speechiness': self.backend.extract_speechiness(y, sr)
            }
            
            # Validate and normalize features
            features['time_signature'] = min(12, max(3, features['time_signature']))
            features['key'] = min(11, max(0, features['key']))
            features['mode'] = min(1, max(0, features['mode']))
            
            # Extract features that depend on other features
            features['danceability'] = self.backend.extract_danceability(y, sr, features['tempo'])
            features['valence'] = self.backend.extract_valence(y, sr)
            
            # Print extracted features for debugging
            print("\nExtracted features:")
            for key, value in features.items():
                print(f"{key}: {value}")
            
            # Normalize values to proper ranges
            for key in ['acousticness', 'danceability', 'energy', 'instrumentalness', 
                       'speechiness', 'valence']:
                if features[key] is not None:
                    features[key] = max(0.0, min(0.95, features[key]))  # Cap at 0.95 instead of 1.0
            
            if features['loudness'] is not None:
                features['loudness'] = max(-60.0, min(0.0, features['loudness']))
            
            # Add liveness since it's part of Spotify's format
            features['liveness'] = self.backend.extract_liveness(y, sr)
            if features['liveness'] is not None:
                features['liveness'] = max(0.0, min(0.95, features['liveness']))
            
            # Add type and empty fields to match Spotify format
            features['type'] = 'audio_features'
            features['analysis_url'] = None
            features['track_href'] = None
            features['uri'] = None
            features['id'] = None
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            return {}

    def calculate_valence(self, energy: float, danceability: float, loudness: float) -> float:
        """Legacy valence calculation - kept for reference but not used"""
        try:
            if energy is None or danceability is None or loudness is None:
                return None
            
            return float(min(1.0,
                energy * 0.4 +
                danceability * 0.3 +
                (1 - abs(loudness) / 60.0) * 0.3))
        except Exception as e:
            print(f"Error calculating valence: {str(e)}")
            return None

    def _create_spotify_format(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Create Spotify-like audio features format"""
        return {
            'acousticness': features.get('acousticness', None),
            'danceability': features.get('danceability', None),
            'duration_ms': features.get('duration_ms', None),
            'energy': features.get('energy', None),
            'instrumentalness': features.get('instrumentalness', None),
            'key': features.get('key', None),
            'liveness': self._calculate_liveness(features),  # New calculation
            'loudness': features.get('loudness', None),
            'mode': features.get('mode', None),
            'speechiness': features.get('speechiness', None),
            'tempo': features.get('tempo', None),
            'time_signature': features.get('time_signature', None),
            'valence': features.get('valence', None),
            'type': 'audio_features',
            'analysis_url': None,  # We don't have this
            'track_href': None,    # We don't have this
            'uri': None,          # We don't have this
            'id': None           # We don't have this
        }

    def _calculate_liveness(self, features: Dict[str, Any]) -> float:
        """Calculate liveness score based on available features"""
        try:
            # Get features with defaults
            energy = features.get('energy')
            instrumentalness = features.get('instrumentalness')
            
            # Return None if any required feature is missing
            if energy is None or instrumentalness is None:
                return None
            
            # Higher energy and lower instrumentalness might indicate live performance
            liveness = (energy * 0.6 + (1 - instrumentalness) * 0.4)
            return max(0.0, min(0.95, liveness))
        except Exception as e:
            print(f"Error calculating liveness: {str(e)}")
            return None

    def get_default_features(self) -> Dict[str, Any]:
        """Get default feature values"""
        default_features = {
            'duration_ms': None,
            'tempo': None,
            'key': None,
            'mode': None,
            'time_signature': None,
            'loudness': None,
            'acousticness': None,
            'danceability': None,
            'energy': None,
            'instrumentalness': None,
            'speechiness': None,
            'valence': None
        }
        
        # Add Spotify-like format to defaults
        default_features['spotify_audio_features'] = self._create_spotify_format(default_features)
        
        return default_features 

    def _create_analysis_format(self, y: np.ndarray, sr: int, features: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed audio analysis format similar to Spotify's"""
        try:
            # Get basic analysis components
            tempo = features.get('tempo', 120.0)
            
            # Calculate confidence scores
            tempo_confidence = self._calculate_confidence(y, sr, 'tempo')
            key_confidence = self._calculate_confidence(y, sr, 'key')
            mode_confidence = self._calculate_confidence(y, sr, 'mode')
            time_signature_confidence = self._calculate_confidence(y, sr, 'time_signature')
            
            # Get timing information
            duration = len(y) / sr
            
            # Get sections, beats, bars, and segments
            sections = self._analyze_sections(y, sr, features)
            beats = self._analyze_beats(y, sr)
            bars = self._analyze_bars(y, sr)
            segments = self._analyze_segments(y, sr)
            
            return {
                'meta': {
                    'analyzer_version': '1.0.0',
                    'platform': platform.system(),
                    'detailed_status': 'OK',
                    'status_code': 0,
                    'timestamp': int(time.time()),
                    'analysis_time': time.time() - self._start_time if hasattr(self, '_start_time') else 0,
                    'input_process': f'librosa {sr}Hz'
                },
                'track': {
                    'num_samples': len(y),
                    'duration': duration,
                    'sample_md5': '',  # Not implemented
                    'offset_seconds': 0,
                    'window_seconds': 0,
                    'analysis_sample_rate': sr,
                    'analysis_channels': 1,
                    'end_of_fade_in': self._find_fade_in(y, sr),
                    'start_of_fade_out': self._find_fade_out(y, sr),
                    'loudness': features.get('loudness', -20),
                    'tempo': tempo,
                    'tempo_confidence': tempo_confidence,
                    'time_signature': features.get('time_signature', 4),
                    'time_signature_confidence': time_signature_confidence,
                    'key': features.get('key', 0),
                    'key_confidence': key_confidence,
                    'mode': features.get('mode', 1),
                    'mode_confidence': mode_confidence,
                    'codestring': '',  # Not implemented
                    'code_version': 1.0,
                    'echoprintstring': '',  # Not implemented
                    'echoprint_version': 1.0,
                    'synchstring': '',  # Not implemented
                    'synch_version': 1.0,
                    'rhythmstring': '',  # Not implemented
                    'rhythm_version': 1.0
                },
                'bars': bars,
                'beats': beats,
                'sections': sections,
                'segments': segments,
                'tatums': self._analyze_tatums(y, sr)
            }
        except Exception as e:
            print(f"Error creating analysis format: {str(e)}")
            return self._get_default_analysis()

    def _calculate_confidence(self, y: np.ndarray, sr: int, feature_type: str) -> float:
        """Calculate confidence score for different feature types"""
        try:
            if feature_type == 'tempo':
                # Use tempo stability as confidence
                onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                return float(np.mean(librosa.feature.rms(y=onset_env)))
            elif feature_type in ['key', 'mode']:
                # Use harmonic features for key/mode confidence
                harmonic = librosa.effects.harmonic(y)
                return float(np.mean(librosa.feature.tonnetz(y=harmonic, sr=sr)[0]))
            elif feature_type == 'time_signature':
                # Use rhythm stability for time signature confidence
                onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                return float(np.mean(librosa.feature.rms(y=onset_env)))
            return 0.5
        except:
            return 0.5

    def _analyze_sections(self, y: np.ndarray, sr: int, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze track sections"""
        try:
            # Use librosa's spectral clustering for segmentation
            S = np.abs(librosa.stft(y))
            chroma = librosa.feature.chroma_stft(S=S, sr=sr)
            
            # Detect section boundaries
            bound_frames = librosa.segment.agglomerative(chroma, 8)  # Detect 8 sections
            bound_times = librosa.frames_to_time(bound_frames, sr=sr)
            
            sections = []
            for i in range(len(bound_times) - 1):
                start = bound_times[i]
                duration = bound_times[i + 1] - start
                
                # Get section-specific features
                section = {
                    'start': float(start),
                    'duration': float(duration),
                    'confidence': 0.8,  # Default confidence
                    'loudness': float(librosa.feature.rms(y=y[int(start*sr):int((start+duration)*sr)])[0].mean()),
                    'tempo': features.get('tempo', 120.0),
                    'tempo_confidence': self._calculate_confidence(y[int(start*sr):int((start+duration)*sr)], sr, 'tempo'),
                    'key': features.get('key', 0),
                    'key_confidence': self._calculate_confidence(y[int(start*sr):int((start+duration)*sr)], sr, 'key'),
                    'mode': features.get('mode', 1),
                    'mode_confidence': self._calculate_confidence(y[int(start*sr):int((start+duration)*sr)], sr, 'mode'),
                    'time_signature': features.get('time_signature', 4),
                    'time_signature_confidence': self._calculate_confidence(y[int(start*sr):int((start+duration)*sr)], sr, 'time_signature')
                }
                sections.append(section)
                
            return sections
        except Exception as e:
            print(f"Error analyzing sections: {str(e)}")
            return []

    def _analyze_beats(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """Analyze beats in the track"""
        try:
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
            
            beats = []
            for i in range(len(beat_times)):
                if i < len(beat_times) - 1:
                    duration = beat_times[i + 1] - beat_times[i]
                else:
                    duration = (len(y) / sr) - beat_times[i]
                    
                beat = {
                    'start': float(beat_times[i]),
                    'duration': float(duration),
                    'confidence': float(librosa.feature.rms(
                        y=y[int(beat_times[i]*sr):int((beat_times[i]+duration)*sr)]
                    )[0].mean())
                }
                beats.append(beat)
            
            return beats
        except Exception as e:
            print(f"Error analyzing beats: {str(e)}")
            return []

    def _analyze_bars(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """Analyze bars in the track"""
        try:
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
            
            # Group beats into bars (assuming 4 beats per bar)
            beats_per_bar = 4
            bars = []
            
            for i in range(0, len(beat_times), beats_per_bar):
                if i + beats_per_bar <= len(beat_times):
                    start = beat_times[i]
                    duration = beat_times[i + beats_per_bar - 1] - start
                    
                    bar = {
                        'start': float(start),
                        'duration': float(duration),
                        'confidence': float(librosa.feature.rms(
                            y=y[int(start*sr):int((start+duration)*sr)]
                        )[0].mean())
                    }
                    bars.append(bar)
            
            return bars
        except Exception as e:
            print(f"Error analyzing bars: {str(e)}")
            return []

    def _analyze_segments(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """Analyze segments in the track"""
        try:
            # Use onset detection for segments
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            segments = []
            for i in range(len(onset_times)):
                if i < len(onset_times) - 1:
                    start = onset_times[i]
                    duration = onset_times[i + 1] - start
                    segment_samples = y[int(start*sr):int((start+duration)*sr)]
                    
                    # Calculate segment features
                    segment = {
                        'start': float(start),
                        'duration': float(duration),
                        'confidence': 0.8,
                        'loudness_start': float(librosa.feature.rms(y=segment_samples[:int(len(segment_samples)*0.1)])[0].mean()),
                        'loudness_max': float(librosa.feature.rms(y=segment_samples)[0].max()),
                        'loudness_max_time': 0.1,  # Simplified
                        'loudness_end': float(librosa.feature.rms(y=segment_samples[-int(len(segment_samples)*0.1):])[0].mean()),
                        'pitches': [float(p) for p in librosa.feature.chroma_cqt(y=segment_samples, sr=sr).mean(axis=1)],
                        'timbre': [float(t) for t in librosa.feature.mfcc(y=segment_samples, sr=sr).mean(axis=1)]
                    }
                    segments.append(segment)
            
            return segments
        except Exception as e:
            print(f"Error analyzing segments: {str(e)}")
            return []

    def _analyze_tatums(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """Analyze tatums (smallest rhythmic units) in the track"""
        try:
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            _, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            tatum_frames = librosa.beat.plp_track(onset_envelope=onset_env, sr=sr)[1]
            tatum_times = librosa.frames_to_time(tatum_frames, sr=sr)
            
            tatums = []
            for i in range(len(tatum_times)):
                if i < len(tatum_times) - 1:
                    duration = tatum_times[i + 1] - tatum_times[i]
                else:
                    duration = (len(y) / sr) - tatum_times[i]
                    
                tatum = {
                    'start': float(tatum_times[i]),
                    'duration': float(duration),
                    'confidence': float(librosa.feature.rms(
                        y=y[int(tatum_times[i]*sr):int((tatum_times[i]+duration)*sr)]
                    )[0].mean())
                }
                tatums.append(tatum)
            
            return tatums
        except Exception as e:
            print(f"Error analyzing tatums: {str(e)}")
            return []

    def _find_fade_in(self, y: np.ndarray, sr: int) -> float:
        """Find the end of fade-in period"""
        try:
            # Calculate RMS energy in small windows
            frame_length = int(sr * 0.05)  # 50ms windows
            hop_length = int(frame_length / 2)
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Find point where energy stabilizes
            threshold = np.mean(rms) * 0.5
            fade_in_frames = np.where(rms > threshold)[0]
            if len(fade_in_frames) > 0:
                return float(librosa.frames_to_time(fade_in_frames[0], sr=sr, hop_length=hop_length))
            return 0.0
        except Exception as e:
            print(f"Error finding fade-in: {str(e)}")
            return 0.0

    def _find_fade_out(self, y: np.ndarray, sr: int) -> float:
        """Find the start of fade-out period"""
        try:
            # Calculate RMS energy in small windows
            frame_length = int(sr * 0.05)  # 50ms windows
            hop_length = int(frame_length / 2)
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Find point where energy starts to decrease
            threshold = np.mean(rms) * 0.5
            fade_out_frames = np.where(rms > threshold)[0]
            if len(fade_out_frames) > 0:
                return float(librosa.frames_to_time(fade_out_frames[-1], sr=sr, hop_length=hop_length))
            return float(len(y) / sr)
        except Exception as e:
            print(f"Error finding fade-out: {str(e)}")
            return float(len(y) / sr)

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis structure"""
        return {
            'meta': {
                'analyzer_version': '1.0.0',
                'platform': platform.system(),
                'detailed_status': 'ERROR',
                'status_code': 1,
                'timestamp': int(time.time()),
                'analysis_time': 0,
                'input_process': 'error'
            },
            'track': {
                'num_samples': 0,
                'duration': 0,
                'sample_md5': '',
                'offset_seconds': 0,
                'window_seconds': 0,
                'analysis_sample_rate': 0,
                'analysis_channels': 1,
                'end_of_fade_in': 0,
                'start_of_fade_out': 0,
                'loudness': -60,
                'tempo': 120,
                'tempo_confidence': 0,
                'time_signature': 4,
                'time_signature_confidence': 0,
                'key': 0,
                'key_confidence': 0,
                'mode': 1,
                'mode_confidence': 0,
                'codestring': '',
                'code_version': 1.0,
                'echoprintstring': '',
                'echoprint_version': 1.0,
                'synchstring': '',
                'synch_version': 1.0,
                'rhythmstring': '',
                'rhythm_version': 1.0
            },
            'bars': [],
            'beats': [],
            'sections': [],
            'segments': [],
            'tatums': []
        }