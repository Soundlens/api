import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import FeedbackButton from '@/components/FeedbackButton'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  title: {
    default: 'SoundLens - Open Source Music Analysis API',
    template: '%s | SoundLens'
  },
  description: 'Community-driven replacement for deprecated Spotify APIs. Open source music analysis platform providing Audio Features, Recommendations, and more.',
  keywords: [
    'spotify api alternative',
    'spotify api replacement',
    'audio analysis api',
    'music recommendations api',
    'audio features api',
    'open source music api',
    'spotify deprecated endpoints',
    'music analysis',
    'audio analysis',
    'music recommendations',
    'music mood detection',
    'audio features extraction',
    'community music api'
  ],
  authors: [{ name: 'SoundLens Community' }],
  creator: 'SoundLens',
  publisher: 'SoundLens Community',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'SoundLens - Open Source Spotify API Alternative',
    description: 'Community-driven replacement for deprecated Spotify APIs. Drop-in replacement for Audio Features, Recommendations, and Analysis endpoints.',
    siteName: 'SoundLens',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'SoundLens - Music Analysis API',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SoundLens - Spotify API Alternative',
    description: 'Replacement for deprecated Spotify APIs',
    images: ['/twitter-image.jpg'],
    creator: '@soundlens',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
    other: {
      rel: 'apple-touch-icon-precomposed',
      url: '/apple-touch-icon-precomposed.png',
    },
  },
  manifest: '/site.webmanifest',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  verification: {
    google: 'your-google-site-verification',
    yandex: 'your-yandex-verification',
    yahoo: 'your-yahoo-verification',
    other: {
      me: ['your-email@domain.com'],
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <main className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white">
          {children}
          <FeedbackButton />
        </main>
      </body>
    </html>
  )
}
