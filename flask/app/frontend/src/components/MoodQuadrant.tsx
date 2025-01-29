import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import annotationPlugin from 'chartjs-plugin-annotation';
import InfoTooltip from './InfoTooltip';

Chart.register(annotationPlugin);

interface MoodQuadrantProps {
  arousal: number;
  valence: number;
  mood: string;
  closestMoods: Array<{
    mood: string;
    arousal: number;
    valence: number;
    distance: number;
    quadrant: number;
  }>;
}

export default function MoodQuadrant({ arousal, valence, mood, closestMoods }: MoodQuadrantProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    // Create the scatter plot
    chartInstance.current = new Chart(ctx, {
      type: 'scatter',
      data: {
        datasets: [
          // Main mood point
          {
            label: 'Current Song',
            data: [{x: valence, y: arousal, mood: mood}],
            backgroundColor: 'rgba(255, 99, 132, 1)',
            pointRadius: 10,
            pointHoverRadius: 12,
          },
          // Closest moods
          {
            label: 'Similar Moods',
            data: closestMoods.map(m => ({
              x: m.valence,
              y: m.arousal,
              mood: m.mood
            })),
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            pointRadius: 8,
            pointHoverRadius: 10,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'linear',
            position: 'bottom',
            min: 0,
            max: 1,
            title: {
              display: true,
              text: 'Valence',
              color: 'rgba(255, 255, 255, 0.9)',
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)',
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.6)',
            }
          },
          y: {
            min: 0,
            max: 1,
            title: {
              display: true,
              text: 'Arousal',
              color: 'rgba(255, 255, 255, 0.9)',
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)',
            },
            ticks: {
              color: 'rgba(255, 255, 255, 0.6)',
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            labels: {
              color: 'rgba(255, 255, 255, 0.9)',
            }
          },
          tooltip: {
            callbacks: {
              label: (context: any) => {
                const point = context.raw;
                return point.mood ? 
                  `${point.mood} (${point.x.toFixed(2)}, ${point.y.toFixed(2)})` :
                  `Current: ${mood} (${point.x.toFixed(2)}, ${point.y.toFixed(2)})`;
              }
            }
          },
          annotation: {
            annotations: {
              quadrantLines: {
                type: 'line',
                xMin: 0.5,
                xMax: 0.5,
                yMin: 0,
                yMax: 1,
                borderColor: 'rgba(255, 255, 255, 0.2)',
                borderWidth: 1,
                drawTime: 'beforeDatasetsDraw'
              },
              horizontalLine: {
                type: 'line',
                yMin: 0.5,
                yMax: 0.5,
                xMin: 0,
                xMax: 1,
                borderColor: 'rgba(255, 255, 255, 0.2)',
                borderWidth: 1,
                drawTime: 'beforeDatasetsDraw'
              }
            }
          }
        }
      }
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [arousal, valence, mood, closestMoods]);

  return (
    <div className="bg-gray-800/50 p-6 rounded-xl">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold">Mood Analysis</h3>
        <InfoTooltip 
          title="Mood Quadrant"
          description="Visual representation of the song's emotional characteristics. Valence (horizontal) represents positiveness, while Arousal (vertical) represents energy level. The quadrants roughly correspond to different emotional states: Happy/Energetic (top-right), Angry/Tense (top-left), Sad/Depressed (bottom-left), and Calm/Relaxed (bottom-right)."
        />
      </div>
      <p className="text-sm text-gray-400 mb-4">
        Current mood: <span className="text-white font-medium capitalize">{mood}</span>
        <InfoTooltip 
          title="Primary Mood"
          description="The dominant emotional characteristic detected in the song based on its musical features."
        />
      </p>
      <div className="h-[400px]">
        <canvas ref={chartRef} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="text-center p-3 bg-gray-700/30 rounded-lg">
          <div className="text-gray-400 flex items-center justify-center">
            Valence
            <InfoTooltip 
              title="Valence"
              description="Measures the musical positiveness. Higher values sound happier or more cheerful."
            />
          </div>
          <div className="text-xl font-medium">{(valence * 100).toFixed(0)}%</div>
        </div>
        <div className="text-center p-3 bg-gray-700/30 rounded-lg">
          <div className="text-gray-400 flex items-center justify-center">
            Arousal
            <InfoTooltip 
              title="Arousal"
              description="Measures the energy level and intensity. Higher values indicate more energetic or intense emotions."
            />
          </div>
          <div className="text-xl font-medium">{(arousal * 100).toFixed(0)}%</div>
        </div>
      </div>
    </div>
  );
} 