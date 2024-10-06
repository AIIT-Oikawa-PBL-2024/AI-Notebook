/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Cloud Run へのデプロイのため
  output: "standalone",
};

export default nextConfig;
