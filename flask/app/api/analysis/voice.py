import os
import numpy as np
import librosa
import speech_recognition as sr
from langdetect import detect
import soundfile as sf
import tempfile
from typing import Dict, Any

class VoiceAnalyzer:
    """Component for analyzing voice characteristics in audio using librosa"""
    
    def __init__(self):
        """Initialize voice analyzer with speech recognizer"""
        self.recognizer = sr.Recognizer()

    def analyze(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze voice characteristics"""
        try:
            voice_features = {}
            
            # Convert to mono if needed
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            
            # Analyze pitch using librosa
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            
            # Get pitch statistics where magnitude is strongest
            pitch_values = []
            for time_idx in range(pitches.shape[1]):
                max_mag_idx = magnitudes[:, time_idx].argmax()
                pitch = pitches[max_mag_idx, time_idx]
                if pitch > 0:  # Filter out zero pitches
                    pitch_values.append(pitch)
                    
            if len(pitch_values) > 0:
                pitch_stats = {
                    'mean': float(np.mean(pitch_values)),
                    'min': float(np.min(pitch_values)),
                    'max': float(np.max(pitch_values))
                }
                
                # Determine if audio has voice and its type based on pitch
                mean_pitch = pitch_stats['mean']
                voice_features['has_voice'] = True
                voice_features['voice_type'] = self._determine_voice_type(mean_pitch)
                voice_features['pitch_stats'] = pitch_stats
                
                # Analyze intensity using RMS energy
                rms = librosa.feature.rms(y=y)[0]
                voice_features['intensity'] = {
                    'mean': float(np.mean(rms)),
                    'min': float(np.min(rms)),
                    'max': float(np.max(rms))
                }
                
                # Analyze harmonicity using spectral flatness
                spec_flat = librosa.feature.spectral_flatness(y=y)[0]
                voice_features['harmonicity'] = {
                    'mean': float(np.mean(spec_flat)),
                    'min': float(np.min(spec_flat)),
                    'max': float(np.max(spec_flat))
                }
                
                # Try speech recognition
                speech_features = self._analyze_speech(y, sr)
                voice_features.update(speech_features)
            else:
                voice_features = self._get_default_features()
                voice_features['has_voice'] = False
                voice_features['voice_type'] = 'instrumental'
            
            return voice_features
            
        except Exception as e:
            print(f"Error analyzing voice: {str(e)}")
            return self._get_default_features()

    def _determine_voice_type(self, mean_pitch: float) -> str:
        """Determine voice type based on mean pitch"""
        if mean_pitch < 165:
            return 'male'
        elif mean_pitch > 255:
            return 'female'
        else:
            return 'ambiguous'

    def _analyze_speech(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze speech characteristics"""
        try:
            # Create a temporary WAV file
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_path = temp_wav.name
            temp_wav.close()
            
            try:
                # Ensure the audio is in the correct format for speech recognition
                # Convert to 16-bit PCM WAV
                y_scaled = np.int16(y * 32767)
                sf.write(temp_path, y_scaled, sr, format='WAV', subtype='PCM_16')
                
                # Perform speech recognition
                with sr.AudioFile(temp_path) as source:
                    audio = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio)
                        return {
                            'detected_language': detect(text),
                            'transcribed_text': text[:100]  # Limit text length
                        }
                    except sr.UnknownValueError:
                        print("Speech recognition could not understand the audio")
                        return {
                            'detected_language': None,
                            'transcribed_text': None
                        }
                    except sr.RequestError as e:
                        print(f"Could not request results from speech recognition service: {e}")
                        return {
                            'detected_language': None,
                            'transcribed_text': None
                        }
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            print(f"Speech recognition error: {str(e)}")
            return {
                'detected_language': None,
                'transcribed_text': None
            }

    def _get_default_features(self) -> Dict[str, Any]:
        """Get default features for non-voice audio"""
        return {
            'has_voice': None,
            'voice_type': None,
            'pitch_stats': {'mean': None, 'min': None, 'max': None},
            'intensity': {'mean': None, 'min': None, 'max': None},
            'harmonicity': {'mean': None, 'min': None, 'max': None},
            'detected_language': None,
            'transcribed_text': None
        } 