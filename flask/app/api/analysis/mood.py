import numpy as np
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass

@dataclass
class MoodTag:
    name: str
    valence: float
    arousal: float
    quadrant: int

class MoodAnalyzer:
    """Enhanced component for analyzing mood based on audio features"""
    
    def __init__(self):
        """Initialize with mood mapping data"""
        self.mood_tags = self._initialize_mood_tags()
        self.quadrant_descriptions = {
            1: "High Valence, High Arousal (Happy, Energetic)",
            2: "Low Valence, High Arousal (Aggressive, Intense)",
            3: "Low Valence, Low Arousal (Sad, Calm)",
            4: "High Valence, Low Arousal (Peaceful, Relaxing)"
        }

    def _initialize_mood_tags(self) -> List[MoodTag]:
        """Initialize mood tags with their valence/arousal values"""
        # Normalize values from 1-10 scale to 0-1 scale
        return [
            MoodTag("ballad", 6.33/10, 3.6/10, 4),
            MoodTag("calm", 6.89/10, 1.67/10, 4),
            MoodTag("cool", 6.82/10, 3.43/10, 4),
            MoodTag("dark", 5.08/10, 4.09/10, 3),
            MoodTag("dramatic", 5.17/10, 6.59/10, 2),
            MoodTag("emotional", 5.11/10, 5.32/10, 1),
            MoodTag("energetic", 7.57/10, 6.1/10, 1),
            MoodTag("epic", 7.19/10, 4.8/10, 2),
            MoodTag("fun", 8.37/10, 6.32/10, 1),
            MoodTag("happy", 8.47/10, 6.05/10, 1),
            MoodTag("melancholic", 3.74/10, 4.13/10, 3),
            MoodTag("party", 7.18/10, 6.08/10, 1),
            MoodTag("relaxing", 8.19/10, 4.29/10, 4),
            MoodTag("sad", 2.1/10, 3.49/10, 3),
            MoodTag("soft", 7.13/10, 3.04/10, 4),
            MoodTag("upbeat", 7.14/10, 4.92/10, 4),
        ]

    def analyze(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze mood based on audio features"""
        try:
            # Get features with defaults
            valence = features.get('valence')
            energy = features.get('energy')
            
            # Return default scores if essential features are missing
            if valence is None or energy is None:
                return self._get_default_mood_scores()
            
            # Map energy to arousal (considering additional features)
            arousal = self._calculate_arousal(features)
            if arousal is None:
                return self._get_default_mood_scores()
            
            # Get quadrant and closest moods
            quadrant = self._get_quadrant(valence, arousal)
            closest_moods = self._find_closest_moods(valence, arousal)
            
            # Calculate confidence scores
            mood_confidence = self._calculate_confidence(valence, arousal, closest_moods)
            
            return {
                'valence': valence,
                'arousal': arousal,
                'energy': energy,
                'quadrant': quadrant,
                'quadrant_description': self.quadrant_descriptions.get(quadrant, "Unknown"),
                'closest_moods': closest_moods,
                'primary_mood': closest_moods[0]['mood'] if closest_moods else 'unknown',
                'confidence': mood_confidence,
                'mood_tags': [mood['mood'] for mood in closest_moods[:3]]
            }
            
        except Exception as e:
            print(f"Error analyzing mood: {str(e)}")
            return self._get_default_mood_scores()

    def _calculate_arousal(self, features: Dict[str, Any]) -> float:
        """Calculate arousal score based on multiple features"""
        try:
            energy = features.get('energy')
            tempo = features.get('tempo')
            loudness = features.get('loudness')
            speechiness = features.get('speechiness')
            
            # Return None if any required feature is missing
            if any(x is None for x in [energy, tempo, loudness, speechiness]):
                return None
            
            # Normalize tempo and loudness
            tempo_norm = tempo / 200.0
            loudness_norm = (loudness + 60) / 60.0
            
            # Weighted combination of features
            arousal = (
                energy * 0.4 +
                tempo_norm * 0.25 +
                loudness_norm * 0.25 +
                speechiness * 0.1
            )
            
            return max(0.0, min(1.0, arousal))
        except Exception as e:
            print(f"Error calculating arousal: {str(e)}")
            return None

    def _get_quadrant(self, valence: float, arousal: float) -> int:
        """Determine the mood quadrant"""
        if valence >= 0.5:
            return 1 if arousal >= 0.5 else 4
        else:
            return 2 if arousal >= 0.5 else 3

    def _find_closest_moods(self, valence: float, arousal: float) -> List[Dict[str, Any]]:
        """Find the closest matching mood tags"""
        distances = []
        for mood in self.mood_tags:
            distance = np.sqrt(
                (valence - mood.valence)**2 + 
                (arousal - mood.arousal)**2
            )
            distances.append({
                'mood': mood.name,
                'distance': distance,
                'quadrant': mood.quadrant,
                'valence': mood.valence,
                'arousal': mood.arousal
            })
        
        # Sort by distance and return top matches
        return sorted(distances, key=lambda x: x['distance'])[:5]

    def _calculate_confidence(self, valence: float, arousal: float, closest_moods: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for mood prediction"""
        if not closest_moods:
            return 0.0
            
        # Calculate average distance to top 3 matches
        avg_distance = np.mean([mood['distance'] for mood in closest_moods[:3]])
        
        # Convert distance to confidence score (inverse relationship)
        confidence = max(0.0, min(1.0, 1.0 - avg_distance))
        
        return confidence

    def _get_default_mood_scores(self) -> Dict[str, Any]:
        """Return default mood scores"""
        return {
            'valence': 0.5,
            'arousal': 0.5,
            'energy': 0.5,
            'quadrant': 1,
            'quadrant_description': self.quadrant_descriptions[1],
            'closest_moods': [],
            'primary_mood': 'unknown',
            'confidence': 0.0,
            'mood_tags': []
        } 