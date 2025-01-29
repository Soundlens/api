import os
import json
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
import soundfile as sf
from .backends import get_backend
from .voice import VoiceAnalyzer
from .features import FeatureExtractor
from .mood import MoodAnalyzer
import boto3
import io
from botocore.config import Config

class AudioAnalyzer:
    """Main class that orchestrates the audio analysis process"""
    
    def __init__(self, 
                 downloads_dir: str = 'downloads',
                 analysis_dir: str = 'analysis',
                 backend: str = 'librosa'):
        """Initialize the audio analyzer with all its components"""
        self.downloads_dir = downloads_dir
        self.analysis_dir = analysis_dir
        
        # Create component instances
        self.backend = get_backend(backend)
        self.voice_analyzer = VoiceAnalyzer()
        self.feature_extractor = FeatureExtractor(self.backend)
        self.mood_analyzer = MoodAnalyzer()
        
        # Initialize S3 client
        my_config = Config(
            region_name="eu-west-1",
            signature_version="v4",
            retries={"max_attempts": 10, "mode": "standard"},
        )
        self.s3 = boto3.client('s3', config=my_config)
        
        # Create directories
        os.makedirs(downloads_dir, exist_ok=True)
        os.makedirs(analysis_dir, exist_ok=True)

    def analyze_track(self, track_id: int, bucket_name: str) -> Dict[str, Any]:
        """Complete analysis pipeline for a track from S3"""
        try:
            # First check if the analysis JSON exists and is processed
            try:
                json_key = f"analyses/{track_id}.json"
                json_obj = self.s3.get_object(
                    Bucket=bucket_name,
                    Key=json_key
                )
                analysis_data = json.loads(json_obj['Body'].read().decode('utf-8'))
                
                if not analysis_data.get('audio_processed'):
                    raise Exception("Audio file not yet processed")
                    
                # Get the audio path from the JSON
                audio_path = analysis_data.get('audio_path')
                if not audio_path:
                    raise Exception("Audio path not found in analysis data")
                    
            except Exception as e:
                print(f"Error checking analysis status: {str(e)}")
                return {'error': 'Analysis not ready for processing'}

            # Get the audio file from S3
            print(f"Getting audio for track ID: {track_id}")
            temp_path = os.path.join(self.downloads_dir, f"temp_{track_id}.mp3")
            
            try:
                # Download file from S3 using the path from JSON
                print(f"Downloading from S3: {audio_path}")
                self.s3.download_file(
                    bucket_name,
                    audio_path,
                    temp_path
                )
                
                if not os.path.exists(temp_path):
                    error_msg = f'Failed to download audio from S3 for track ID: {track_id}'
                    print(error_msg)
                    return {'error': error_msg}
                
                # Load and analyze the audio
                print(f"Loading and analyzing audio from: {temp_path}")
                y, sr = sf.read(temp_path)
                
                # Ensure mono audio
                if len(y.shape) > 1:
                    y = np.mean(y, axis=1)
                
                # Convert to float32
                y = np.asarray(y, dtype=np.float32)
                
                # Extract features
                technical_features = self.feature_extractor.extract_features(y, sr)
             
                # Analyze voice characteristics
                voice_features = self.voice_analyzer.analyze(y, sr)
                
                # Analyze mood
                if technical_features.get('energy') is not None and technical_features.get('valence') is not None:
                    mood_scores = self.mood_analyzer.analyze(technical_features)
                else:
                    mood_scores = self.mood_analyzer._get_default_mood_scores()
                
                # Combine all results
                analysis = {
                    'track_id': track_id,
                    'timestamp': datetime.now().isoformat(),
                    'analysis': {
                        'duration': float(len(y) / sr) if y is not None else None,
                        'technical_features': technical_features,
                        'voice_features': voice_features,
                        'mood_scores': mood_scores
                    }
                }
                
                # Update the analysis JSON with results
                analysis_data.update({
                    'analysis_completed': True,
                    'analysis_completed_at': datetime.now().isoformat(),
                    'analysis_results': analysis
                })
                
                # Save updated analysis back to S3
                self.s3.put_object(
                    Bucket=bucket_name,
                    Key=json_key,
                    Body=json.dumps(analysis_data, indent=2),
                    ContentType='application/json'
                )
                
                return analysis
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            print(f"Error analyzing track {track_id}: {str(e)}")
            return {'error': str(e)}

    def _load_existing_analysis(self, track_id: str) -> Optional[Dict[str, Any]]:
        """Load existing analysis if available"""
        try:
            analysis_path = os.path.join(self.analysis_dir, f"{track_id}_analysis.json")
            
            if os.path.exists(analysis_path):
                print(f"Found existing analysis: {analysis_path}")
                with open(analysis_path, 'r') as f:
                    existing_analysis = json.load(f)
                    if self._is_valid_analysis(existing_analysis):
                        print("Using existing analysis")
                        return existing_analysis
                    print("Existing analysis is incomplete, will reanalyze...")
            
            return None
            
        except Exception as e:
            print(f"Error loading existing analysis: {str(e)}")
            return None

    def _is_valid_analysis(self, analysis: Dict[str, Any]) -> bool:
        """Check if the analysis is valid and complete"""
        try:
            return (
                analysis 
                and 'analysis' in analysis 
                and analysis['analysis'] 
                and 'technical_features' in analysis['analysis']
                and 'mood_scores' in analysis['analysis']
                and any(analysis['analysis']['technical_features'].values())
                and any(analysis['analysis']['mood_scores'].values())
            )
        except Exception:
            return False 