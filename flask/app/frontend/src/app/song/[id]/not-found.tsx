import Link from 'next/link';
import Logo from '@/components/Logo';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-gradient-to-b from-blue-900/50 to-transparent">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <Link href="/" className="flex items-center gap-2">
            <Logo className="w-10 h-10" />
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-violet-400">
              SoundLens
            </span>
          </Link>
        </div>
      </header>

      <main className="flex-grow flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">Song Not Found</h1>
          <p className="text-gray-400 mb-8">
            The song analysis you&apos;re looking for doesn&apos;t exist or has been removed.
          </p>
          <Link 
            href="/"
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </main>
    </div>
  );
} 