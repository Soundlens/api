import os
from pathlib import Path
import numpy as np
import soundfile as sf
from typing import Dict, Any, Optional

# Create necessary directories
DOWNLOADS_DIR = Path("downloads")
ANALYSIS_DIR = Path("analysis")
DOWNLOADS_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)

class AudioAnalysisTest:
    def __init__(self):
        from analysis import (
            AudioAnalyzer,
            MoodAnalyzer,
            FeatureExtractor,
            VoiceAnalyzer,
            get_backend
        )
        
        self.analyzer = AudioAnalyzer(
            downloads_dir=str(DOWNLOADS_DIR),
            analysis_dir=str(ANALYSIS_DIR),
            backend='librosa'
        )
        
        self.mood_analyzer = MoodAnalyzer()
        self.feature_extractor = FeatureExtractor(get_backend('librosa'))
        self.voice_analyzer = VoiceAnalyzer()

    def analyze_local_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a local audio file"""
        try:
            # Load audio file
            print(f"Loading audio file: {file_path}")
            y, sr = sf.read(file_path)
            
            # Ensure mono audio
            if len(y.shape) > 1:
                y = np.mean(y, axis=1)
            
            # Convert to float32
            y = np.asarray(y, dtype=np.float32)
            
            # Extract features
            print("Extracting audio features...")
            features = self.feature_extractor.extract_features(y, sr)
            
            # Analyze voice characteristics
            print("Analyzing voice characteristics...")
            voice_features = self.voice_analyzer.analyze(y, sr)
            features['voice_features'] = voice_features
            
            # Analyze mood
            print("Analyzing mood...")
            mood_scores = self.mood_analyzer.analyze(features)
            
            # Combine results
            analysis = {
                'file_path': file_path,
                'technical_features': features,
                'mood_scores': mood_scores,
                'duration': float(len(y) / sr)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing file: {str(e)}")
            return {'error': str(e)}

    def analyze_youtube(self, track_name: str) -> Dict[str, Any]:
        """Analyze a track from YouTube"""
        try:
            print(f"Analyzing track: {track_name}")
            return self.analyzer.analyze_track(track_name)
        except Exception as e:
            print(f"Error analyzing YouTube track: {str(e)}")
            return {'error': str(e)}

def main():
    # Create analyzer instance
    analyzer = AudioAnalysisTest()
    
    # Example 1: Analyze local file
    # local_file = "path/to/your/audio/file.mp3"  # Replace with your audio file path
    # if os.path.exists(local_file):
    #     print("\nAnalyzing local file...")
    #     results = analyzer.analyze_local_file(local_file)
    #     print("\nLocal file analysis results:")
    #     print(results)
    
    # Example 2: Analyze from YouTube
    youtube_track = "The Weeknd - Blinding Lights"  # Replace with the track you want to analyze
    print("\nAnalyzing YouTube track...")

    results = analyzer.analyze_youtube(youtube_track)
    print("\nYouTube track analysis results:")
    print(results)

if __name__ == "__main__":
    main()