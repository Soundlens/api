'use client';

import { useState } from 'react';
import { useAudioAnalysis } from '@/hooks/useAudioAnalysis';
import { AnalysisResponse, SpotifyTrack } from '@/types/api';
import dynamic from 'next/dynamic';
import SearchBar from './SearchBar';
import SongList from './SongList';
// import PricingPlans from './PricingPlans';
import Footer from './Footer';
import Logo from './Logo';
import InfoTooltip from './InfoTooltip';
import Navigation from './Navigation';
import Link from 'next/link';
import Community from './Community';

const RadarChart = dynamic(() => import('./RadarChart'), {
  ssr: false,
});

const MoodQuadrant = dynamic(() => import('./MoodQuadrant'), {
  ssr: false,
});

function CompletedAnalyses({ analyses }: { analyses: AnalysisResponse[] }) {
  const completedAnalyses = analyses.filter(a => a.status === 'completed' && a.raw_analysis_data);

  if (completedAnalyses.length === 0) return null;

  const technicalFeatures = [
    {
      label: "Tempo",
      description: "Speed or pace of the music measured in beats per minute (BPM). Higher values indicate faster songs.",
      getValue: (analysis: AnalysisResponse) => `${Math.round(analysis.raw_analysis_data.tempo)} BPM`
    },
    {
      label: "Key",
      description: "The musical key of the song, representing the tonal center or main pitch class.",
      getValue: (analysis: AnalysisResponse) => ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][analysis.raw_analysis_data.key]
    },
    {
      label: "Mode",
      description: "Indicates whether the song is in a major or minor key. Major typically sounds brighter, while minor often sounds darker or more melancholic.",
      getValue: (analysis: AnalysisResponse) => analysis.raw_analysis_data.mode === 1 ? 'Major' : 'Minor'
    },
    {
      label: "Time Signature",
      description: "The number of beats in each bar of music. Common time (4/4) is the most frequent in popular music.",
      getValue: (analysis: AnalysisResponse) => `${analysis.raw_analysis_data.time_signature}/4`
    }
  ] as const;

  return (
    <div className="mx-auto max-w-7xl px-6 lg:px-8 py-16">
      {/* Comparison Section */}
      <div className="mb-16">
        <h2 className="text-2xl font-bold mb-8 flex items-center">
          Song Comparison
          <InfoTooltip
            title="Song Comparison"
            description="Compare musical characteristics across different songs"
          />
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Radar Chart */}
          <div className="bg-gray-800/50 p-6 rounded-xl">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              Musical Features
              <InfoTooltip
                title="Musical Features"
                description="Overall comparison of musical characteristics"
              />
            </h3>
            <RadarChart
              features={completedAnalyses.map((a: any) => ({
                energy: a.raw_analysis_data?.energy || 0,
                danceability: a.raw_analysis_data?.danceability || 0,
                valence: a.raw_analysis_data?.valence || 0,
                acousticness: a.raw_analysis_data?.acousticness || 0,
                instrumentalness: a.raw_analysis_data?.instrumentalness || 0,
                speechiness: a.raw_analysis_data?.speechiness || 0,
              }))}
              labels={completedAnalyses.map(a => a.title)}
            />
          </div>

          {/* Quick Stats Comparison */}
          <div className="bg-gray-800/50 p-6 rounded-xl">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              Quick Stats
              <InfoTooltip
                title="Quick Stats"
                description="Key technical characteristics comparison"
              />
            </h3>
            <div className="space-y-6">
              {completedAnalyses.map((analysis: any, index: number) => (
                <div
                  key={analysis.id}
                  className="p-4 bg-gray-700/30 rounded-lg border-l-4"
                  style={{
                    borderLeftColor: `hsla(${index * 137.5}, 70%, 50%, 0.8)`,
                  }}
                >
                  <div className="flex items-start gap-4 mb-3">
                    {analysis.image_url && (

                      <img
                        src={analysis.image_url}
                        alt={analysis.title}
                        width={48}
                        height={48}
                        className="rounded-lg object-cover flex-shrink-0"
                      />
                    )}
                    <div className="flex-grow flex justify-between items-start">
                      <h4 className="font-medium">{analysis.title}</h4>
                      <span className="text-sm text-gray-400">
                        {Math.round(analysis.raw_analysis_data.raw_analysis_data.analysis.duration)}s
                      </span>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Tempo</span>
                      <p className="font-medium">{Math.round(analysis.raw_analysis_data.tempo)} BPM</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Key</span>
                      <p className="font-medium">
                        {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][analysis.raw_analysis_data.key]}
                        {analysis.raw_analysis_data.mode === 1 ? ' Major' : ' Minor'}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-400">Voice</span>
                      <p className="font-medium">
                        {analysis.raw_analysis_data.voice_characteristics.has_voice ? 'Voice' : 'Instrumental'}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-400">Primary Mood</span>
                      <p className="font-medium capitalize">{analysis.raw_analysis_data.mood}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Individual Analyses */}
      <div className="space-y-8">
        <h2 className="text-2xl font-bold mb-8">Detailed Analysis</h2>
        {completedAnalyses.map((analysis, index) => (
          <div
            key={index}
            className="bg-gray-800/50 p-6 rounded-xl"
            style={{
              borderLeft: `4px solid hsla(${index * 137.5}, 70%, 50%, 0.8)`,
            }}
          >
            <div className="flex items-start gap-6 mb-6">
              {analysis.image_url && (
                <img
                  src={analysis.image_url}
                  alt={analysis.title}
                  width={96}
                  height={96}
                  className="rounded-lg object-cover shadow-lg"
                />

              )}
              <div>
                <h3 className="text-xl font-bold">{analysis.title}</h3>
                {analysis.artist && (
                  <p className="text-gray-400 mt-1">{analysis.artist}</p>
                )}
                <div className="flex gap-3 mt-2 text-sm">
                  <span className="text-gray-400">
                    {Math.round(analysis.raw_analysis_data.raw_analysis_data.analysis.duration)}s
                  </span>
                  <span className="text-gray-400">•</span>
                  <span className="text-gray-400">
                    {analysis.raw_analysis_data.voice_characteristics.has_voice ? 'Voice' : 'Instrumental'}
                  </span>
                  <span className="text-gray-400">•</span>
                  <span className="text-gray-400 capitalize">
                    {analysis.raw_analysis_data.mood}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Technical Features */}
              <div>
                <h4 className="text-lg font-semibold mb-4 flex items-center">
                  Technical Analysis
                  <InfoTooltip
                    title="Technical Features"
                    description="Detailed musical characteristics extracted from audio analysis"
                  />
                </h4>
                <div className="space-y-3">
                  {technicalFeatures.map(feature => (
                    <div key={feature.label} className="flex justify-between items-center">
                      <div className="flex items-center">
                        <span>{feature.label}</span>
                        <InfoTooltip
                          title={feature.label}
                          description={feature.description}
                        />
                      </div>
                      <span>{feature.getValue(analysis)}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Mood Quadrant */}
              <MoodQuadrant
                arousal={analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.arousal}
                valence={analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.valence}
                mood={analysis.raw_analysis_data.mood}
                closestMoods={analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.closest_moods}
              />
            </div>

            {/* Add mood description */}
            <div className="mt-4 p-4 bg-gray-700/30 rounded-lg">
              <h4 className="text-lg font-semibold mb-2">Mood Description</h4>
              <p className="text-gray-300">
                {analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.quadrant_description}
              </p>
              <div className="mt-2 flex gap-2 flex-wrap">
                {analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.mood_tags.map((tag: string) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-gray-600/50 rounded-full text-sm capitalize"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Voice Analysis */}
            <div className="mt-4 p-4 bg-gray-700/30 rounded-lg">
              <h4 className="text-lg font-semibold mb-2">Voice Analysis</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-gray-400">Voice Detection</p>
                  <p className="text-lg font-medium">
                    {analysis.raw_analysis_data.voice_characteristics.has_voice ? 'Voice Detected' : 'Instrumental'}
                  </p>
                </div>
                {analysis.raw_analysis_data.voice_characteristics.has_voice && (
                  <>
                    <div>
                      <p className="text-gray-400">Voice Type</p>
                      <p className="text-lg font-medium capitalize">
                        {analysis.raw_analysis_data.voice_characteristics.voice_type}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400">Language</p>
                      <p className="text-lg font-medium uppercase">
                        {analysis.raw_analysis_data.voice_characteristics.detected_language || 'Unknown'}
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function HomeContent() {
  const [analyses, setAnalyses] = useState<AnalysisResponse[]>([]);
  const { analyzeTrack, checkAnalysisStatus, getAnalysis, isLoading, error } = useAudioAnalysis();

  const handleSearch = async (query: string, spotifyTrack?: SpotifyTrack) => {
    try {
      // Extract artist name from query if not provided by spotifyTrack
      let artist = spotifyTrack?.artists[0].name;
      if (!artist && query.includes('-')) {
        // Try to extract artist from the query string (e.g., "Song Name - Artist Name")
        artist = query.split('-')[1].trim();
      }
      // Fallback to "Unknown Artist" if we still don't have an artist
      artist = artist || "Unknown Artist";

      // Format the data properly for the backend
      const analysisData = {
        title: query,
        artist: artist,  // Now always providing an artist
        track_name: query,
        spotify_info: spotifyTrack ? {
          id: spotifyTrack.id,
          name: spotifyTrack.name,
          artist: spotifyTrack.artists[0].name,
          imageUrl: spotifyTrack.album.images[0]?.url,
          duration_ms: spotifyTrack.duration_ms
        } : null
      };

      const result = await analyzeTrack(analysisData);

      // Add the analysis to the list immediately
      setAnalyses(prev => [...prev, result]);

      // Start polling for status
      const pollStatus = async () => {
        try {
          const status = await checkAnalysisStatus(result.id);

          if (status.status === 'completed') {
            // Fetch complete analysis data
            const completeAnalysis = await getAnalysis(result.id);
            setAnalyses(prev =>
              prev.map(analysis =>
                analysis.id === result.id
                  ? completeAnalysis
                  : analysis
              )
            );
          } else {
            // Update just the status
            setAnalyses(prev =>
              prev.map(analysis =>
                analysis.id === result.id
                  ? { ...analysis, ...status }
                  : analysis
              )
            );

            if (status.status === 'processing' || status.status === 'pending') {
              // Poll more frequently at the start, then slow down
              const delay = status.progress < 20 ? 500 : // Every 0.5s at start
                status.progress < 50 ? 1000 : // Every 1s in middle
                  2000;                         // Every 2s near end
              setTimeout(pollStatus, delay);
            }
          }
        } catch (error) {
          console.error('Error polling status:', error);
          // Retry on error with exponential backoff
          setTimeout(pollStatus, 3000);
        }
      };

      pollStatus();
    } catch (err) {
      console.error('Failed to analyze track:', err);
    }
  };

  const removeAnalysis = (index: number) => {
    setAnalyses(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />
      <main className="flex-grow">
        {/* Hero Section */}
        <div className="relative overflow-hidden bg-gradient-to-b from-blue-900/50 to-transparent pb-16">
          <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
          <div className="relative pt-16 pb-8 sm:pt-24">
            <div className="mx-auto max-w-7xl px-6 lg:px-8">
              <div className="mx-auto max-w-2xl text-center">
                {/* Alert Banner */}
                <div className="mb-8 rounded-full bg-yellow-500/10 px-4 py-2 text-yellow-500 ring-1 ring-inset ring-yellow-500/20">
                  <p className="text-sm">
                    Spotify API Deprecation Solution Available Now
                  </p>
                </div>

                {/* Logo and Title */}
                <div className="flex flex-col items-center gap-4">
                  <Logo className="w-24 h-24 animate-pulse" />
                  <h1 className="text-4xl font-bold tracking-tight sm:text-6xl bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-violet-400">
                    SoundLens
                  </h1>
                </div>

                {/* Tagline */}
                <p className="mt-6 text-lg leading-8 text-gray-300">
                  Replacement for deprecated Spotify APIs.
                  Drop-in solution for Audio Features, Recommendations, and Analysis endpoints.
                </p>

                {/* Features */}
                <div className="mt-8 flex justify-center gap-8 text-sm text-gray-400">
                  <span>✓ Audio Features API</span>
                  <span>✓ Recommendations</span>
                  <span>✓ Audio Analysis</span>
                </div>

                {/* CTA Buttons */}
                <div className="mt-10 flex items-center justify-center gap-x-6">
                  <Link
                    href="/api/docs"
                    className="rounded-md bg-blue-500 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-400"
                  >
                    View Documentation
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Search Section */}
          <div className="mx-auto px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
              <SearchBar onSearch={handleSearch} isLoading={isLoading} />
            </div>

            {error && (
              <div className="max-w-3xl mx-auto mt-4 p-4 bg-red-500/10 border border-red-500 rounded-xl text-red-500 text-center">
                {error}
              </div>
            )}

            <SongList songs={analyses} onRemove={removeAnalysis} />
          </div>
        </div>

        {/* Analysis Section - Only for completed analyses */}
        <CompletedAnalyses analyses={analyses} />

        {/* Community Section */}
        <Community />

        {/* Pricing Section - Commented out
        <PricingPlans />
        */}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
} 