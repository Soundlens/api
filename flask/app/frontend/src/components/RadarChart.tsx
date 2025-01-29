import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
// import { TechnicalFeatures } from '@/types/api';

interface RadarChartProps {
  features: {
    energy: number;
    danceability: number;
    valence: number;
    acousticness: number;
    instrumentalness: number;
    speechiness: number;
  }[];
  labels: string[];
}

export default function RadarChart({ features, labels }: RadarChartProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current || features.length === 0) return;

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    const datasets = features.map((feature, index) => ({
      label: labels[index] || `Song ${index + 1}`,
      data: [
        feature.energy,
        feature.danceability,
        feature.valence,
        feature.acousticness,
        feature.instrumentalness,
        feature.speechiness,
      ],
      backgroundColor: `hsla(${index * 137.5}, 70%, 50%, 0.2)`,
      borderColor: `hsla(${index * 137.5}, 70%, 50%, 0.8)`,
      borderWidth: 2,
      pointBackgroundColor: `hsla(${index * 137.5}, 70%, 50%, 0.8)`,
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: `hsla(${index * 137.5}, 70%, 50%, 1)`,
    }));

    chartInstance.current = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: [
          'Energy',
          'Danceability',
          'Valence',
          'Acousticness',
          'Instrumentalness',
          'Speechiness',
        ],
        datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            beginAtZero: true,
            max: 1,
            ticks: {
              stepSize: 0.2,
              color: 'rgba(255, 255, 255, 0.6)',
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)',
            },
            angleLines: {
              color: 'rgba(255, 255, 255, 0.1)',
            },
            pointLabels: {
              color: 'rgba(255, 255, 255, 0.9)',
              font: {
                size: 12,
              },
            },
          },
        },
        plugins: {
          legend: {
            position: 'top' as const,
            labels: {
              color: 'rgba(255, 255, 255, 0.9)',
              font: {
                size: 12,
              },
            },
          },
        },
      },
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [features, labels]);

  if (features.length === 0) {
    return (
      <div className="w-full h-[400px] bg-gray-800/50 p-6 rounded-lg flex items-center justify-center">
        <p className="text-gray-400">No completed analyses yet</p>
      </div>
    );
  }

  return (
    <div className="w-full h-[400px] bg-gray-800/50 p-6 rounded-lg">
      <canvas ref={chartRef} />
    </div>
  );
} 