/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost/api/:path*'
      }
    ]
  },
  images: {
    domains: ['i.scdn.co'],
  },
}

module.exports = nextConfig 