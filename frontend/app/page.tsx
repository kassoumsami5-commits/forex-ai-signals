import dynamic from 'next/dynamic';

// Dynamic import with SSR disabled to prevent prerendering issues with live data fetching
const HomePageContent = dynamic(() => import('@/components/HomePageContent'), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen bg-dark-900 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-gold-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-dark-400">Loading...</p>
      </div>
    </div>
  ),
});

export default function HomePage() {
  return <HomePageContent />;
}
