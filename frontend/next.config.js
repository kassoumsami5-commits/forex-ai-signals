/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['images.unsplash.com', 'api.twelvedata.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://forex-ai-signals-api.onrender.com/:path*',
      },
    ];
  },
};

module.exports = nextConfig;