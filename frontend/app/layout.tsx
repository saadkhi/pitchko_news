import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Toaster } from 'react-hot-toast';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'Pitchko News - AI-Powered Tech News Platform',
    template: '%s | Pitchko News'
  },
  description: 'Get the latest tech news powered by AI. Real-time news aggregation, breaking news alerts, video reports, and in-depth analysis on AI, startups, cybersecurity, and big tech.',
  keywords: [
    'tech news',
    'AI news',
    'startup news',
    'cybersecurity news',
    'big tech news',
    'artificial intelligence',
    'technology news',
    'breaking news',
    'news aggregation',
    'AI-powered news'
  ],
  authors: [{ name: 'Pitchko News Team' }],
  creator: 'Pitchko News',
  publisher: 'Pitchko News',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://pitchkonews.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://pitchkonews.com',
    siteName: 'Pitchko News',
    title: 'Pitchko News - AI-Powered Tech News Platform',
    description: 'Get the latest tech news powered by AI. Real-time news aggregation, breaking news alerts, and video reports.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Pitchko News - AI-Powered Tech News Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Pitchko News - AI-Powered Tech News Platform',
    description: 'Get the latest tech news powered by AI. Real-time news aggregation and video reports.',
    images: ['/og-image.png'],
    creator: '@pitchkonews',
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
  verification: {
    google: process.env.GOOGLE_SITE_VERIFICATION,
    yandex: process.env.YANDEX_VERIFICATION,
    bing: process.env.BING_VERIFICATION,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="motion-reduce">
      <body className={`${inter.className} antialiased`}>
        <div className="min-h-screen bg-gray-50">
          {children}
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </body>
    </html>
  );
}
