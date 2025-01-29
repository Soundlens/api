import { Metadata } from 'next';
import HomeContent from '@/components/HomeContent';

export const metadata: Metadata = {
  title: 'SoundLens - Discover Your Music\'s DNA',
  description: 'Analyze your favorite songs with AI technology. Get detailed insights into mood, technical features, and emotional characteristics of any track.',
  openGraph: {
    title: 'SoundLens - AI Music Analysis',
    description: 'Discover the musical DNA of your favorite tracks with advanced AI analysis',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'SoundLens Music Analysis',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SoundLens - Music Analysis',
    description: 'AI-powered music analysis and mood detection',
    images: ['/twitter-image.jpg'],
  },
  alternates: {
    canonical: '/',
    languages: {
      'en-US': '/en-US',
    },
  },
};

export default function Home() {
  return <HomeContent />;
}
