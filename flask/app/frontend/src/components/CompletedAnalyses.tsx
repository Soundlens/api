import { AnalysisResponse } from '@/types/api';
import dynamic from 'next/dynamic';
import InfoTooltip from './InfoTooltip';

const RadarChart = dynamic(() => import('./RadarChart'), {
  ssr: false,
});

const MoodQuadrant = dynamic(() => import('./MoodQuadrant'), {
  ssr: false,
});

function CompletedAnalyses({ analyses }: { analyses: AnalysisResponse[] }) {
  const completedAnalyses = analyses.filter(a => a.status === 'completed' && a.raw_analysis_data);

  if (completedAnalyses.length === 0) return null;

  return (
    <div className="relative py-24 overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-gray-900/50 via-blue-900/20 to-purple-900/20" />
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center opacity-10" />

      <div className="relative mx-auto max-w-7xl px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-violet-400">
            Detailed Analysis
          </h2>
          <p className="mt-4 text-lg text-gray-400">
            Comprehensive breakdown of your music&apos;s characteristics
          </p>
        </div>

        {/* Comparison Section */}
        <div className="mb-16">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Radar Chart */}
            <div className="bg-gray-800/50 backdrop-blur-sm p-8 rounded-2xl border border-gray-700/50 shadow-xl">
              <h3 className="text-xl font-semibold mb-6 flex items-center">
                Musical Features
                <InfoTooltip 
                  title="Musical Features"
                  description="Overall comparison of musical characteristics"
                />
              </h3>
              <RadarChart 
                features={completedAnalyses.map(a => ({
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

            {/* Quick Stats */}
            <div className="bg-gray-800/50 backdrop-blur-sm p-8 rounded-2xl border border-gray-700/50 shadow-xl">
              <h3 className="text-xl font-semibold mb-6 flex items-center">
                Quick Stats
                <InfoTooltip 
                  title="Quick Stats"
                  description="Key technical characteristics comparison"
                />
              </h3>
              <div className="space-y-6">
                {completedAnalyses.map((analysis, index) => (
                  <div 
                    key={analysis.id} 
                    className="p-6 bg-gray-700/30 rounded-xl border border-gray-600/50 hover:border-gray-500/50 transition-colors"
                    style={{
                      background: `linear-gradient(to right, hsla(${index * 137.5}, 70%, 50%, 0.1), hsla(${index * 137.5}, 70%, 50%, 0.05))`,
                    }}
                  >
                    <div className="flex items-start gap-4 mb-4">
                      {analysis.image_url && (
                        <img 
                          src={analysis.image_url}
                          alt={analysis.title}
                          className="w-16 h-16 rounded-lg object-cover ring-2 ring-gray-700/50"
                        />
                      )}
                      <div className="flex-grow">
                        <h4 className="font-medium text-lg">{analysis.title}</h4>
                        <p className="text-gray-400">{analysis.artist}</p>
                      </div>
                      <span className="text-sm text-gray-400 tabular-nums">
                        {Math.round(analysis.raw_analysis_data.raw_analysis_data.analysis.duration)}s
                      </span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                      <div className="p-3 bg-gray-800/50 rounded-lg backdrop-blur-sm">
                        <span className="text-gray-400 block mb-1">Tempo</span>
                        <span className="font-medium text-lg">
                          {Math.round(analysis.raw_analysis_data.tempo)} BPM
                        </span>
                      </div>
                      <div className="p-3 bg-gray-800/50 rounded-lg backdrop-blur-sm">
                        <span className="text-gray-400 block mb-1">Key</span>
                        <span className="font-medium text-lg">
                          {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][analysis.raw_analysis_data.key]}
                          {analysis.raw_analysis_data.mode === 1 ? ' Major' : ' Minor'}
                        </span>
                      </div>
                      <div className="p-3 bg-gray-800/50 rounded-lg backdrop-blur-sm">
                        <span className="text-gray-400 block mb-1">Type</span>
                        <span className="font-medium text-lg capitalize">
                          {analysis.raw_analysis_data.voice_characteristics.has_voice ? 'Voice' : 'Instrumental'}
                        </span>
                      </div>
                      <div className="p-3 bg-gray-800/50 rounded-lg backdrop-blur-sm">
                        <span className="text-gray-400 block mb-1">Mood</span>
                        <span className="font-medium text-lg capitalize">
                          {analysis.raw_analysis_data.mood}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Individual Analyses */}
        <div className="space-y-12">
          {completedAnalyses.map((analysis, index) => (
            <div 
              key={index}
              className="bg-gray-800/50 backdrop-blur-sm p-8 rounded-2xl border border-gray-700/50 shadow-xl"
              style={{
                borderImage: `linear-gradient(to right, hsla(${index * 137.5}, 70%, 50%, 0.5), hsla(${(index * 137.5 + 60) % 360}, 70%, 50%, 0.5)) 1`,
              }}
            >
              <div className="flex items-start gap-6 mb-8">
                {analysis.image_url && (
                  <img 
                    src={analysis.image_url}
                    alt={analysis.title}
                    className="w-24 h-24 rounded-xl object-cover ring-2 ring-gray-700/50 shadow-lg"
                  />
                )}
                <div>
                  <h3 className="text-2xl font-bold mb-2">{analysis.title}</h3>
                  {analysis.artist && (
                    <p className="text-gray-400 text-lg">{analysis.artist}</p>
                  )}
                  <div className="flex gap-3 mt-3 text-sm">
                    <span className="px-3 py-1 bg-gray-700/50 rounded-full">
                      {Math.round(analysis.raw_analysis_data.raw_analysis_data.analysis.duration)}s
                    </span>
                    <span className="px-3 py-1 bg-gray-700/50 rounded-full">
                      {analysis.raw_analysis_data.voice_characteristics.has_voice ? 'Voice' : 'Instrumental'}
                    </span>
                    <span className="px-3 py-1 bg-gray-700/50 rounded-full capitalize">
                      {analysis.raw_analysis_data.mood}
                    </span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Technical Features */}
                <div>
                  <h4 className="text-lg font-semibold mb-6 flex items-center">
                    Technical Analysis
                    <InfoTooltip 
                      title="Technical Features"
                      description="Detailed musical characteristics extracted from audio analysis"
                    />
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { label: "Energy", value: `${Math.round(analysis.raw_analysis_data.energy * 100)}%` },
                      { label: "Danceability", value: `${Math.round(analysis.raw_analysis_data.danceability * 100)}%` },
                      { label: "Valence", value: `${Math.round(analysis.raw_analysis_data.valence * 100)}%` },
                      { label: "Acousticness", value: `${Math.round(analysis.raw_analysis_data.acousticness * 100)}%` },
                      { label: "Instrumentalness", value: `${Math.round(analysis.raw_analysis_data.instrumentalness * 100)}%` },
                      { label: "Speechiness", value: `${Math.round(analysis.raw_analysis_data.speechiness * 100)}%` },
                    ].map(feature => (
                      <div key={feature.label} className="p-4 bg-gray-700/30 rounded-lg">
                        <div className="text-gray-400 mb-1">{feature.label}</div>
                        <div className="text-xl font-medium">{feature.value}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Mood Analysis */}
                <MoodQuadrant 
                  arousal={analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.arousal}
                  valence={analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.valence}
                  mood={analysis.raw_analysis_data.mood}
                  closestMoods={analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.closest_moods}
                />
              </div>

              {/* Mood Description */}
              <div className="mt-8 p-6 bg-gray-700/30 rounded-xl border border-gray-600/50">
                <h4 className="text-lg font-semibold mb-3">Mood Analysis</h4>
                <p className="text-gray-300 mb-4">
                  {analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.quadrant_description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {analysis.raw_analysis_data.raw_analysis_data.analysis.mood_scores.mood_tags.map((tag: string) => (
                    <span 
                      key={tag}
                      className="px-3 py-1 bg-gray-600/50 rounded-full text-sm capitalize"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Voice Analysis */}
              <div className="mt-8 p-6 bg-gray-700/30 rounded-xl border border-gray-600/50">
                <h4 className="text-lg font-semibold mb-4">Voice Analysis</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="p-4 bg-gray-800/50 rounded-lg">
                    <span className="text-gray-400 block mb-1">Voice Detection</span>
                    <span className="text-xl font-medium">
                      {analysis.raw_analysis_data.voice_characteristics.has_voice ? 'Voice Detected' : 'Instrumental'}
                    </span>
                  </div>
                  {analysis.raw_analysis_data.voice_characteristics.has_voice && (
                    <>
                      <div className="p-4 bg-gray-800/50 rounded-lg">
                        <span className="text-gray-400 block mb-1">Voice Type</span>
                        <span className="text-xl font-medium capitalize">
                          {analysis.raw_analysis_data.voice_characteristics.voice_type}
                        </span>
                      </div>
                      <div className="p-4 bg-gray-800/50 rounded-lg">
                        <span className="text-gray-400 block mb-1">Language</span>
                        <span className="text-xl font-medium uppercase">
                          {analysis.raw_analysis_data.voice_characteristics.detected_language || 'Unknown'}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default CompletedAnalyses; 