from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any
import librosa
# import audioflux as af
import traceback
# import torch
# import torchaudio
# import torchaudio.transforms as T
from typing import Tuple

class AudioBackend(ABC):
    """Abstract base class for audio analysis backends"""
    
    def __init__(self):
        self.progress_callback = None
        self.current_feature = None
        self.total_features = 10  # Total number of features we extract
        
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback
        
    def _update_progress(self, feature_name: str):
        """Update progress through callback"""
        if self.progress_callback:
            # Calculate progress based on feature being processed
            feature_weights = {
                'tempo': 0.1,
                'energy': 0.1,
                'loudness': 0.1,
                'key': 0.1,
                'mode': 0.1,
                'time_signature': 0.1,
                'acousticness': 0.1,
                'instrumentalness': 0.1,
                'speechiness': 0.1,
                'valence': 0.1
            }
            
            # Get progress up to current feature
            features_list = list(feature_weights.keys())
            current_idx = features_list.index(feature_name) if feature_name in features_list else 0
            progress = sum(feature_weights[f] for f in features_list[:current_idx + 1])
            
            self.progress_callback(
                int(progress * 100),
                f"Extracting {feature_name.replace('_', ' ')}"
            )
    
    @abstractmethod
    def extract_tempo(self, y: np.ndarray, sr: int) -> float:
        """Extract tempo feature"""
        pass
    
    @abstractmethod
    def extract_energy(self, y: np.ndarray, sr: int) -> float:
        """Extract energy feature"""
        pass
    
    @abstractmethod
    def extract_loudness(self, y: np.ndarray, sr: int) -> float:
        """Extract loudness feature"""
        pass
    
    @abstractmethod
    def extract_key(self, y: np.ndarray, sr: int) -> int:
        """Extract key feature"""
        pass
    
    @abstractmethod
    def extract_mode(self, y: np.ndarray, sr: int) -> int:
        """Extract mode feature"""
        pass
    
    @abstractmethod
    def extract_time_signature(self, y: np.ndarray, sr: int) -> int:
        """Extract time signature feature"""
        pass
    
    @abstractmethod
    def extract_acousticness(self, y: np.ndarray, sr: int) -> float:
        """Extract acousticness feature"""
        pass
    
    @abstractmethod
    def extract_instrumentalness(self, y: np.ndarray, sr: int) -> float:
        """Extract instrumentalness feature"""
        pass
    
    @abstractmethod
    def extract_speechiness(self, y: np.ndarray, sr: int) -> float:
        """Extract speechiness feature"""
        pass
    
    @abstractmethod
    def extract_danceability(self, y: np.ndarray, sr: int, tempo: float) -> float:
        """Extract danceability feature"""
        pass
    
    @abstractmethod
    def extract_valence(self, y: np.ndarray, sr: int) -> float:
        """Extract valence feature"""
        pass
    
    @abstractmethod
    def extract_liveness(self, y: np.ndarray, sr: int) -> float:
        """Extract liveness feature"""
        pass

class LibrosaBackend(AudioBackend):
    """Librosa implementation of audio analysis"""
    
    def extract_tempo(self, y: np.ndarray, sr: int) -> float:
        try:
            self._update_progress('tempo')
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            return float(tempo)
        except Exception as e:
            print("Error extracting tempo (Librosa):")
            traceback.print_exc()
            return 120.0

    def extract_energy(self, y: np.ndarray, sr: int) -> float:
        try:
            self._update_progress('energy')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
                
            # Calculate multiple energy features
            rms = librosa.feature.rms(y=y)[0]
            spectral = librosa.feature.spectral_contrast(y=y, sr=sr)[0]
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            
            # Combine different energy indicators
            energy_score = (
                0.4 * np.mean(rms) / np.max(rms) +  # RMS energy
                0.3 * np.mean(spectral) / np.max(spectral) +  # Spectral contrast
                0.3 * np.mean(onset_env) / np.max(onset_env)  # Onset strength
            )
            
            # Apply non-linear scaling to better differentiate high-energy tracks
            energy = np.power(energy_score, 0.5)  # Square root to boost high values
            
            return float(np.clip(energy, 0.0, 1.0))
        except Exception as e:
            print("Error extracting energy (Librosa):")
            traceback.print_exc()
            return 0.5

    def extract_loudness(self, y: np.ndarray, sr: int) -> float:
        try:
            self._update_progress('loudness')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            rms = librosa.feature.rms(y=y)
            if isinstance(rms, tuple):
                rms = rms[0]
            rms = np.array(rms, dtype=np.float32)
            mean_rms = np.array([np.mean(rms)], dtype=np.float32)
            return float(librosa.amplitude_to_db(mean_rms)[0])
        except Exception as e:
            print("Error extracting loudness (Librosa):")
            traceback.print_exc()
            return -20.0

    def extract_key(self, y: np.ndarray, sr: int) -> int:
        try:
            self._update_progress('key')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            chromagram = librosa.feature.chroma_stft(y=y, sr=sr)
            if isinstance(chromagram, tuple):
                chromagram = chromagram[0]
            chromagram = np.array(chromagram, dtype=np.float32)
            return int(np.argmax(np.mean(chromagram, axis=1)))
        except Exception as e:
            print("Error extracting key (Librosa):")
            traceback.print_exc()
            return 0

    def extract_mode(self, y: np.ndarray, sr: int) -> int:
        try:
            self._update_progress('mode')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            y_harmonic = librosa.effects.harmonic(y)
            if y_harmonic is not None:
                mode_feature = librosa.feature.tonnetz(y=y_harmonic, sr=sr)
                if isinstance(mode_feature, tuple):
                    mode_feature = mode_feature[0]
                mode_feature = np.array(mode_feature, dtype=np.float32)
                return int(np.mean(mode_feature[0]) > np.mean(mode_feature[1]))
        except Exception as e:
            print("Error extracting mode (Librosa):")
            traceback.print_exc()
        return 1

    def extract_time_signature(self, y: np.ndarray, sr: int) -> int:
        try:
            self._update_progress('time_signature')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            _, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            if len(beats) > 0:
                return int(round(np.mean(np.diff(beats)) / 2) * 2)
        except Exception as e:
            print("Error extracting time signature (Librosa):")
            traceback.print_exc()
        return 4

    def extract_acousticness(self, y: np.ndarray, sr: int) -> float:
        try:
            self._update_progress('acousticness')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            if isinstance(spectral_bandwidth, tuple):
                spectral_bandwidth = spectral_bandwidth[0]
            spectral_bandwidth = np.array(spectral_bandwidth, dtype=np.float32)
            return float(1.0 - min(1.0, np.mean(spectral_bandwidth) / (sr/4)))
        except Exception as e:
            print("Error extracting acousticness (Librosa):")
            traceback.print_exc()
            return 0.5

    def extract_instrumentalness(self, y: np.ndarray, sr: int) -> float:
        try:
            self._update_progress('instrumentalness')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            zcr = librosa.feature.zero_crossing_rate(y)
            if isinstance(zcr, tuple):
                zcr = zcr[0]
            zcr = np.array(zcr, dtype=np.float32)
            return float(min(1.0, np.mean(zcr) * 10))
        except Exception as e:
            print("Error extracting instrumentalness (Librosa):")
            traceback.print_exc()
            return 0.5

    def extract_speechiness(self, y: np.ndarray, sr: int) -> float:
        try:
            self._update_progress('speechiness')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            # Use multiple features to detect speech
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            
            # Speech typically has higher MFCC variance and ZCR
            mfcc_var = np.std(mfccs, axis=1)
            zcr_mean = np.mean(zcr)
            
            # Combine features with weights
            speech_score = (
                0.6 * np.mean(mfcc_var) / 100 +  # Normalized MFCC variance
                0.4 * zcr_mean * 10  # Normalized ZCR
            )
            
            # Apply sigmoid-like normalization
            return float(np.clip(speech_score, 0.0, 1.0))
        except Exception as e:
            print("Error extracting speechiness (Librosa):")
            traceback.print_exc()
            return 0.1

    def extract_danceability(self, y: np.ndarray, sr: int, tempo: float) -> float:
        try:
            self._update_progress('danceability')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
                
            # Get onset envelope and tempo-related features
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo_normalized = max(0, min(1, (tempo - 50) / (180 - 50)))  # Normalize tempo between 50-180 BPM
            
            # Calculate rhythm regularity
            _, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            if len(beats) > 1:
                beat_intervals = np.diff(beats)
                rhythm_regularity = 1.0 - np.std(beat_intervals) / np.mean(beat_intervals)
            else:
                rhythm_regularity = 0.0
                
            # Calculate pulse clarity using PLP (Perceptual Linear Prediction)
            pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)
            pulse_clarity = np.mean(pulse) / np.max(pulse) if len(pulse) > 0 else 0.0
            
            # Get low-frequency energy ratio (bass presence)
            spec = np.abs(librosa.stft(y))
            freqs = librosa.fft_frequencies(sr=sr)
            bass_mask = freqs <= 250  # Consider frequencies up to 250 Hz as bass
            bass_energy = np.mean(spec[bass_mask]) / np.mean(spec)
            
            # Combine features with weights
            danceability = (
                0.3 * tempo_normalized +          # Tempo contribution
                0.3 * rhythm_regularity +         # Beat consistency
                0.2 * pulse_clarity +             # Beat strength
                0.2 * min(1.0, bass_energy)       # Bass presence
            )
            
            # Apply non-linear scaling to emphasize differences
            danceability = np.power(danceability, 0.7)  # Adjust curve
            
            return float(np.clip(danceability, 0.0, 1.0))
            
        except Exception as e:
            print("Error extracting danceability (Librosa):")
            traceback.print_exc()
            return 0.5

    def extract_valence(self, y: np.ndarray, sr: int) -> float:
        """Extract valence (musical positiveness)"""
        try:
            self._update_progress('valence')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
                
            # Get chromagram
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            
            # Calculate spectral statistics
            spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            
            # Major/minor chord detection
            major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
            minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
            
            # Calculate correlation with major/minor profiles
            chroma_norm = librosa.util.normalize(chroma, axis=0)
            major_corr = np.mean([np.correlate(chr_frame, major_profile) for chr_frame in chroma_norm.T])
            minor_corr = np.mean([np.correlate(chr_frame, minor_profile) for chr_frame in chroma_norm.T])
            
            # Combine features
            valence_score = (
                0.5 * (major_corr - minor_corr) +  # Chord profile contribution
                0.3 * (np.mean(spec_cent) / (sr/2)) +  # Spectral centroid contribution
                0.2 * (1 - np.mean(spec_bw) / (sr/2))  # Spectral bandwidth contribution
            )
            
            # Normalize to 0-1 range
            valence = (valence_score + 1) / 2
            return float(np.clip(valence, 0.0, 1.0))
        except Exception as e:
            print("Error extracting valence (Librosa):")
            traceback.print_exc()
            return 0.5

    def extract_liveness(self, y: np.ndarray, sr: int) -> float:
        """Extract liveness feature"""
        try:
            self._update_progress('liveness')
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
                
            # Get chromagram
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            
            # Calculate spectral statistics
            spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            
            # Major/minor chord detection
            major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
            minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
            
            # Calculate correlation with major/minor profiles
            chroma_norm = librosa.util.normalize(chroma, axis=0)
            major_corr = np.mean([np.correlate(chr_frame, major_profile) for chr_frame in chroma_norm.T])
            minor_corr = np.mean([np.correlate(chr_frame, minor_profile) for chr_frame in chroma_norm.T])
            
            # Combine features
            liveness_score = (
                0.5 * (major_corr - minor_corr) +  # Chord profile contribution
                0.3 * (np.mean(spec_cent) / (sr/2)) +  # Spectral centroid contribution
                0.2 * (1 - np.mean(spec_bw) / (sr/2))  # Spectral bandwidth contribution
            )
            
            # Normalize to 0-1 range
            liveness = (liveness_score + 1) / 2
            return float(np.clip(liveness, 0.0, 1.0))
        except Exception as e:
            print("Error extracting liveness (Librosa):")
            traceback.print_exc()
            return 0.5

# class TorchAudioBackend(AudioBackend):
#     """TorchAudio implementation of audio analysis"""
    
#     def __init__(self, device: str = None):
#         """Initialize with optional device (cuda/cpu)"""
#         self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
#         print(f"Using TorchAudio backend on {self.device}")
        
#         # Create window once and reuse
#         self.window = torch.hann_window(2048).to(self.device)
        
#         # Initialize transforms
#         self.mel_spectrogram = T.MelSpectrogram(
#             sample_rate=22050,
#             n_fft=2048,
#             hop_length=512,
#             n_mels=128,
#             window_fn=torch.hann_window
#         ).to(self.device)
        
#         self.mfcc_transform = T.MFCC(
#             sample_rate=22050,
#             n_mfcc=13,
#             melkwargs={'window_fn': torch.hann_window}
#         ).to(self.device)

#     def _to_tensor(self, y: np.ndarray) -> torch.Tensor:
#         """Convert numpy array to torch tensor"""
#         if isinstance(y, torch.Tensor):
#             return y.to(self.device)
#         return torch.from_numpy(y.astype(np.float32)).to(self.device)

#     def _find_peaks(self, x: torch.Tensor) -> torch.Tensor:
#         """Find peaks in a 1D tensor"""
#         try:
#             if x is None or x.numel() == 0:
#                 return torch.tensor([], device=self.device)
                
#             # Manual peak finding without padding
#             peaks = []
#             for i in range(1, len(x) - 1):
#                 if x[i] > x[i-1] and x[i] > x[i+1]:
#                     peaks.append(i)
            
#             if not peaks:
#                 return torch.tensor([], device=self.device)
                
#             return torch.tensor(peaks, device=self.device)
#         except Exception as e:
#             print(f"Error finding peaks: {str(e)}")
#             return torch.tensor([], device=self.device)

#     def extract_tempo(self, y: np.ndarray, sr: int) -> float:
#         try:
#             y_tensor = self._to_tensor(y)
#             onset_env = self._get_onset_envelope(y_tensor, sr)
            
#             # Manual autocorrelation
#             onset_env = onset_env - onset_env.mean()
#             n = len(onset_env)
#             ac = torch.zeros(n, device=self.device)
#             for i in range(n):
#                 if i == 0:
#                     ac[i] = torch.sum(onset_env * onset_env)
#                 else:
#                     ac[i] = torch.sum(onset_env[:-i] * onset_env[i:])
            
#             # Find peaks in autocorrelation
#             peaks = self._find_peaks(ac)
#             if len(peaks) > 0:
#                 peak_periods = peaks[torch.argsort(ac[peaks])[-5:]]
#                 estimated_tempo = 60.0 * sr / (peak_periods.float().median() * 512)
#                 return float(estimated_tempo)
#             return None
#         except Exception as e:
#             print(f"Error extracting tempo: {str(e)}")
#             return None

#     def extract_energy(self, y: np.ndarray, sr: int) -> float:
#         try:
#             y_tensor = self._to_tensor(y)
#             rms = torch.sqrt(torch.mean(y_tensor ** 2))
#             return float(rms.cpu().numpy() * 10)
#         except Exception as e:
#             print(f"Error extracting energy: {str(e)}")
#             return None

#     def extract_loudness(self, y: np.ndarray, sr: int) -> float:
#         try:
#             y_tensor = self._to_tensor(y)
#             spec = self.mel_spectrogram(y_tensor)
#             loudness = 20 * torch.log10(torch.mean(spec) + 1e-10)
#             return float(loudness.cpu().numpy())
#         except Exception as e:
#             print(f"Error extracting loudness: {str(e)}")
#             return None

#     def extract_key(self, y: np.ndarray, sr: int) -> int:
#         try:
#             y_tensor = self._to_tensor(y)
#             spec = self._stft(y_tensor)
#             magnitudes = torch.abs(spec)
            
#             n_chroma = 12
#             chroma = torch.zeros((n_chroma, magnitudes.shape[1]), device=self.device)
            
#             for i in range(n_chroma):
#                 chroma[i] = torch.sum(magnitudes[i::n_chroma], dim=0)
            
#             chroma = torch.nn.functional.normalize(chroma, p=2, dim=0)
#             key = int(torch.argmax(torch.mean(chroma, dim=1)))
#             return key if key >= 0 else None
#         except Exception as e:
#             print(f"Error extracting key: {str(e)}")
#             return None

#     def extract_mode(self, y: np.ndarray, sr: int) -> int:
#         try:
#             y_tensor = self._to_tensor(y)
#             spec = self._stft(y_tensor)
#             magnitudes = torch.abs(spec)
            
#             n_chroma = 12
#             chroma = torch.zeros((n_chroma, magnitudes.shape[1]), device=self.device)
#             for i in range(n_chroma):
#                 chroma[i] = torch.sum(magnitudes[i::n_chroma], dim=0)
            
#             chroma = torch.nn.functional.normalize(chroma, p=2, dim=0)
#             chroma_sum = torch.mean(chroma, dim=1)
            
#             major_profile = torch.tensor([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1], device=self.device).float()
#             minor_profile = torch.tensor([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0], device=self.device).float()
            
#             major_sim = torch.nn.functional.cosine_similarity(chroma_sum.unsqueeze(0), major_profile.unsqueeze(0))
#             minor_sim = torch.nn.functional.cosine_similarity(chroma_sum.unsqueeze(0), minor_profile.unsqueeze(0))
            
#             # Return None if we're not confident about the mode
#             if major_sim is None or minor_sim is None:
#                 return None
                
#             if abs(major_sim - minor_sim) < 0.1:  # If difference is too small, we're not confident
#                 return None
                
#             # Convert to float before comparison to avoid NoneType error
#             major_sim_val = float(major_sim.cpu().numpy())
#             minor_sim_val = float(minor_sim.cpu().numpy())
            
#             return int(major_sim_val > minor_sim_val)
#         except Exception as e:
#             print(f"Error extracting mode: {str(e)}")
#             return None

#     def _get_onset_envelope(self, y: torch.Tensor, sr: int) -> torch.Tensor:
#         """Calculate onset strength envelope"""
#         try:
#             # Ensure input is 2D for mel spectrogram
#             if y.dim() == 1:
#                 y = y.unsqueeze(0)
            
#             spec = self.mel_spectrogram(y)
#             # Calculate difference along time axis and mean across frequency bins
#             onset_env = torch.mean(torch.diff(spec.squeeze(0), dim=1), dim=0)
            
#             # Handle empty or invalid onset envelope
#             if onset_env.numel() == 0 or torch.all(onset_env == 0):
#                 return None
                
#             return onset_env
#         except Exception as e:
#             print(f"Error calculating onset envelope: {str(e)}")
#             return None

#     def extract_time_signature(self, y: np.ndarray, sr: int) -> int:
#         try:
#             y_tensor = self._to_tensor(y)
#             onset_env = self._get_onset_envelope(y_tensor, sr)
            
#             onset_peaks = self._find_peaks(onset_env)
#             if len(onset_peaks) > 1:
#                 peak_times = onset_peaks.float() * 512 / sr
#                 intervals = peak_times[1:] - peak_times[:-1]
                
#                 median_interval = float(torch.median(intervals).cpu().numpy())
#                 if median_interval == 0:
#                     return None
                    
#                 window_size = 6.0
#                 beats_in_window = window_size / median_interval
                
#                 beats = float(beats_in_window)
#                 if beats >= 22:
#                     return 2
#                 elif beats >= 11:
#                     return 4
#                 elif beats >= 8:
#                     return 3
#                 elif beats >= 5:
#                     return 6
#             return None
#         except Exception as e:
#             print(f"Error extracting time signature: {str(e)}")
#             return None

#     def extract_acousticness(self, y: np.ndarray, sr: int) -> float:
#         try:
#             y_tensor = self._to_tensor(y)
#             spec = torch.abs(self._stft(y_tensor))
            
#             spectral_centroid = torch.mean(
#                 torch.sum(spec * torch.arange(spec.shape[1], device=self.device).unsqueeze(0), dim=1) /
#                 torch.sum(spec, dim=1)
#             )
            
#             acousticness = 1.0 - (spectral_centroid / (sr/4))
#             return float(acousticness.cpu().numpy())
#         except Exception as e:
#             print(f"Error extracting acousticness: {str(e)}")
#             return None

#     def extract_instrumentalness(self, y: np.ndarray, sr: int) -> float:
#         try:
#             y_tensor = self._to_tensor(y)
#             mfccs = self.mfcc_transform(y_tensor)
#             mfcc_var = torch.var(mfccs, dim=1).mean()
#             return float(torch.sigmoid(mfcc_var).cpu().numpy())
#         except Exception as e:
#             print(f"Error extracting instrumentalness: {str(e)}")
#             return None

#     def extract_speechiness(self, y: np.ndarray, sr: int) -> float:
#         try:
#             y_tensor = self._to_tensor(y)
#             mfccs = self.mfcc_transform(y_tensor)
#             speech_mfccs = mfccs[:4].var(dim=1).mean()
#             return float(torch.sigmoid(speech_mfccs).cpu().numpy())
#         except Exception as e:
#             print(f"Error extracting speechiness: {str(e)}")
#             return None

#     def extract_danceability(self, y: np.ndarray, sr: int, tempo: float) -> float:
#         try:
#             if tempo is None:
#                 return None
                
#             y_tensor = self._to_tensor(y)
#             onset_env = self._get_onset_envelope(y_tensor, sr)
            
#             onset_peaks = self._find_peaks(onset_env)
#             if len(onset_peaks) > 1:
#                 peak_intervals = onset_peaks[1:] - onset_peaks[:-1]
#                 rhythm_regularity = 1.0 - float(torch.std(peak_intervals.float()) / torch.mean(peak_intervals.float()))
                
#                 tempo_factor = float(torch.sigmoid(torch.tensor((tempo - 60) / 120)))
#                 danceability = rhythm_regularity * 0.8 + tempo_factor * 0.2
#                 return max(0.0, min(0.95, danceability))
#             return None
#         except Exception as e:
#             print(f"Error extracting danceability: {str(e)}")
#             return None

#     def _get_beats(self, onset_env: torch.Tensor, sr: int) -> Tuple[float, torch.Tensor]:
#         """Extract tempo and beat frames"""
#         # Estimate tempo first
#         tempo = self._estimate_tempo(onset_env, sr)
        
#         # Calculate expected beat period in frames
#         period = int((60.0 / tempo) * sr / 512)  # 512 is hop_length
        
#         # Find peaks in onset envelope
#         peaks = self._find_peaks(onset_env)
        
#         # Filter peaks to match tempo
#         if len(peaks) > 1:
#             filtered_peaks = []
#             last_peak = peaks[0]
#             filtered_peaks.append(last_peak)
            
#             for peak in peaks[1:]:
#                 # Check if this peak is close to expected beat position
#                 distance = peak - last_peak
#                 if abs(distance - period) < period * 0.2:  # 20% tolerance
#                     filtered_peaks.append(peak)
#                     last_peak = peak
            
#             beat_frames = torch.tensor(filtered_peaks, device=self.device)
#         else:
#             beat_frames = peaks
            
#         return tempo, beat_frames

#     def _estimate_tempo(self, onset_env: torch.Tensor, sr: int) -> float:
#         """Estimate tempo from onset envelope"""
#         try:
#             # Normalize onset envelope
#             onset_env = onset_env - onset_env.mean()
#             onset_env = onset_env / (onset_env.std() + 1e-10)
            
#             # Calculate tempo range in frames
#             min_tempo = 40
#             max_tempo = 240
#             min_period = int(60.0 * sr / (512 * max_tempo))  # 512 is hop_length
#             max_period = int(60.0 * sr / (512 * min_tempo))
            
#             # Calculate windowed autocorrelation
#             ac = torch.zeros(max_period, device=self.device)
#             for i in range(min_period, max_period):
#                 if i >= len(onset_env):
#                     break
#                 ac[i] = torch.sum(onset_env[:-i] * onset_env[i:])
            
#             # Find peaks in valid tempo range
#             peaks = self._find_peaks(ac[min_period:max_period])
#             if len(peaks) > 0:
#                 # Convert peak positions to tempo values
#                 tempos = 60.0 * sr / (512 * (peaks + min_period).float())
#                 # Return median tempo
#                 return float(torch.median(tempos))
            
#             return 120.0
#         except Exception as e:
#             print(f"Error in tempo estimation: {str(e)}")
#             return 120.0

#     def _stft(self, y: torch.Tensor) -> torch.Tensor:
#         """Compute STFT with consistent parameters"""
#         try:
#             if y is None or y.numel() == 0:
#                 return None
                
#             return torch.stft(
#                 y,
#                 n_fft=2048,
#                 hop_length=512,
#                 window=self.window,
#                 return_complex=True
#             )
#         except Exception as e:
#             print(f"Error computing STFT: {str(e)}")
#             return None

def get_backend(backend_name: str = 'librosa') -> AudioBackend:
    """Factory function to get the appropriate backend"""
    backends = {
        'librosa': LibrosaBackend,
        # 'torchaudio': TorchAudioBackend,

        #'audioflux': AudioFluxBackend
    }
    
    if backend_name not in backends:
        raise ValueError(f"Unknown backend: {backend_name}. Available backends: {list(backends.keys())}")
    
    return backends[backend_name]() 
    return backends[backend_name]() 