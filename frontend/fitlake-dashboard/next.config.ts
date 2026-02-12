import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    console.log('BACKEND_URL:', process.env.BACKEND_URL);
    return [
      {
        source: '/api/:path*',
        destination: process.env.BACKEND_URL 
          ? `${process.env.BACKEND_URL}/api/:path*`
          : 'http://127.0.0.1:8000/api/:path*', // Fallback for local dev
      },
    ];
  },
};

export default nextConfig;
