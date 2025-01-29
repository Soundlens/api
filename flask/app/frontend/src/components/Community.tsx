import { Discord, Telegram } from './Icons';

export default function Community() {
  return (
    <section className="relative py-24 overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-900/20 to-purple-900/20" />
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center opacity-20" />
      
      <div className="relative max-w-7xl mx-auto px-6 lg:px-8">
        <div 
          className="text-center mb-16 animate-fade-in-up"
        >
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-violet-400">
            Join Our Community
          </h2>
          <p className="mt-4 text-lg text-gray-300">
            Connect with developers, share ideas, and help shape the future of music analysis
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-2xl mx-auto">
          {/* Discord Card */}
          <div className="relative group transition-transform duration-300 hover:-translate-y-2">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg blur opacity-50 group-hover:opacity-75 transition duration-200" />
            <a
              href="https://discord.gg/Q4Dw489P"
              target="_blank"
              rel="noopener noreferrer"
              className="relative flex flex-col items-center p-8 bg-gray-800/90 rounded-lg hover:bg-gray-800/70 transition duration-200"
            >
              <Discord className="w-16 h-16 text-[#5865F2] mb-4" />
              <h3 className="text-xl font-semibold mb-2">Discord</h3>
              <p className="text-gray-400 text-center">
                Join our Discord server for real-time discussions and support
              </p>
              <span className="mt-4 inline-flex items-center text-sm font-semibold text-blue-400 group-hover:translate-x-1 transition-transform">
                Join Server
                <svg className="ml-2 w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </span>
            </a>
          </div>

          {/* Telegram Card */}
          <div className="relative group transition-transform duration-300 hover:-translate-y-2">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-lg blur opacity-50 group-hover:opacity-75 transition duration-200" />
            <a
              href="https://t.me/soundlens"
              target="_blank"
              rel="noopener noreferrer"
              className="relative flex flex-col items-center p-8 bg-gray-800/90 rounded-lg hover:bg-gray-800/70 transition duration-200"
            >
              <Telegram className="w-16 h-16 text-[#0088cc] mb-4" />
              <h3 className="text-xl font-semibold mb-2">Telegram</h3>
              <p className="text-gray-400 text-center">
                Follow our Telegram channel for updates and announcements
              </p>
              <span className="mt-4 inline-flex items-center text-sm font-semibold text-blue-400 group-hover:translate-x-1 transition-transform">
                Join Channel
                <svg className="ml-2 w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </span>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
} 