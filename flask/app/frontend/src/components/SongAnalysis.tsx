'use client';

import { AnalysisResponse } from '@/types/api';
import dynamic from 'next/dynamic';
import Logo from './Logo';
import InfoTooltip from './InfoTooltip';
import Link from 'next/link';

// const RadarChart = dynamic(() => import('./RadarChart'), {
//   ssr: false,
// });

const MoodQuadrant = dynamic(() => import('./MoodQuadrant'), {
  ssr: false,
});

interface SongAnalysisProps {
  analysis: AnalysisResponse;
}

export default function SongAnalysis({ analysis }: SongAnalysisProps) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="relative bg-gradient-to-b from-blue-900/50 to-transparent">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <Logo className="w-10 h-10" />
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-violet-400">
                SoundLens
              </span>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-grow">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          {/* Song Header */}
          <div className="flex items-start gap-6 mb-8">
            {analysis.image_url && (
              <img 
                src={analysis.image_url}
                alt={analysis.title}
                width={128}
                height={128}
                className="rounded-lg object-cover"
              />
            )}
            <div>
              <h1 className="text-3xl font-bold">{analysis.title}</h1>
              {analysis.artist && (
                <p className="text-xl text-gray-400">{analysis.artist}</p>
              )}
              <div className="mt-4 flex gap-2">
                {analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.mood_tags.map((tag: string) => (
                  <span 
                    key={tag}
                    className="px-3 py-1 bg-gray-700/50 rounded-full text-sm capitalize"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Analysis Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Technical Features */}
            <div className="bg-gray-800/50 p-6 rounded-xl">
              <h2 className="text-xl font-semibold mb-6 flex items-center">
                Technical Analysis
                <InfoTooltip 
                  title="Technical Features"
                  description="Detailed musical characteristics extracted from audio analysis"
                />
              </h2>
              {/* Add your technical features display here */}
            </div>

            {/* Mood Analysis */}
            <div className="bg-gray-800/50 p-6 rounded-xl">
              <h2 className="text-xl font-semibold mb-6">Mood Analysis</h2>
              <MoodQuadrant 
                arousal={analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.arousal}
                valence={analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.valence}
                mood={analysis.raw_analysis_data.mood}
                closestMoods={analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.closest_moods}
              />
            </div>
          </div>

          {/* Share Section */}
          <div className="mt-8 bg-gray-800/50 p-6 rounded-xl">
            <h2 className="text-xl font-semibold mb-4">Share Analysis</h2>
            <div className="flex gap-4">
              <button 
                onClick={() => {
                  navigator.clipboard.writeText(window.location.href);
                }}
                className="px-4 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
              >
                Copy Link
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 