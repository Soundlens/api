import { useState } from 'react';
import { AnalysisResponse } from '@/types/api';

interface AnalysisRequest {
  title: string;
  artist: string;
  track_name: string;
  spotify_info: {
    id: string;
    name: string;
    artist: string;
    imageUrl: string;
    duration_ms: number;
  } | null;
}

export const useAudioAnalysis = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);

  const analyzeTrack = async (data: AnalysisRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/analyses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze track');
      }

      const analysisData = await response.json();
      setAnalysis(analysisData);
      return analysisData;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze track');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const checkAnalysisStatus = async (analysisId: number) => {
    try {
      const response = await fetch(`/api/analyses/${analysisId}/status`);
      if (!response.ok) {
        throw new Error('Failed to fetch analysis status');
      }
      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    }
  };

  const cancelAnalysis = async (analysisId: number) => {
    try {
      const response = await fetch(`/api/analyses/${analysisId}/cancel`, {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error('Failed to cancel analysis');
      }
      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    }
  };

  const getAnalysis = async (analysisId: number) => {
    try {
      const response = await fetch(`/api/analyses/${analysisId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch analysis');
      }
      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    }
  };

  return {
    analyzeTrack,
    checkAnalysisStatus,
    cancelAnalysis,
    getAnalysis,
    isLoading,
    error,
    analysis,
  };
}; 