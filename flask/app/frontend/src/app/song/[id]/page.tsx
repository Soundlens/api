import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import SongAnalysis from '@/components/SongAnalysis';

// Fetch analysis data from your API
async function getAnalysis(id: string) {
  try {
    const res = await fetch(`/api/analyses/${id}/public`, {
      next: { revalidate: 3600 } // Cache for 1 hour
    });
    
    if (!res.ok) {
      throw new Error('Analysis not found');
    }
    
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const analysis = await getAnalysis(params.id);
  
  if (!analysis) {
    return {
      title: 'Song Not Found | SoundLens',
      description: 'The requested song analysis could not be found.'
    };
  }

  return {
    title: `${analysis.title} Analysis | SoundLens`,
    description: `Discover the musical DNA of ${analysis.title}. Analyze mood, technical features, and emotional characteristics with AI technology.`,
    openGraph: {
      title: `${analysis.title} - Music Analysis`,
      description: `AI analysis of ${analysis.title} shows ${analysis.raw_analysis_data.mood} mood with ${Math.round(analysis.raw_analysis_data.mood_confidence * 100)}% confidence.`,
      images: [
        {
          url: analysis.image_url || '/og-image.jpg',
          width: 1200,
          height: 630,
          alt: `${analysis.title} Analysis`,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: `${analysis.title} - Music Analysis`,
      description: `AI-powered analysis of ${analysis.title}`,
      images: [analysis.image_url || '/twitter-image.jpg'],
    },
  };
}

export default async function SongPage({ params }: any) {
  const analysis = await getAnalysis(params.id);
  
  if (!analysis) {
    notFound();
  }

  return <SongAnalysis analysis={analysis} />;
} 