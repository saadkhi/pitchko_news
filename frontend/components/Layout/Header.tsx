'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  MagnifyingGlassIcon, 
  NewspaperIcon, 
  PlayIcon, 
  ChartBarIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon
} from '@heroicons/react/24/outline';
import { newsAPI, BreakingNews } from '@/lib/api';
import { formatRelativeTime } from '@/lib/api';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [breakingNews, setBreakingNews] = useState<BreakingNews[]>([]);
  const [showBreakingNews, setShowBreakingNews] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Fetch breaking news on component mount
    const fetchBreakingNews = async () => {
      try {
        const news = await newsAPI.getBreakingNews();
        setBreakingNews(news);
      } catch (error) {
        console.error('Failed to fetch breaking news:', error);
      }
    };

    fetchBreakingNews();
    
    // Refresh breaking news every 5 minutes
    const interval = setInterval(fetchBreakingNews, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setIsMenuOpen(false);
    }
  };

  const navigation = [
    { name: 'Home', href: '/', icon: NewspaperIcon },
    { name: 'Videos', href: '/videos', icon: PlayIcon },
    { name: 'Trends', href: '/trends', icon: ChartBarIcon },
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      {/* Breaking News Ticker */}
      {breakingNews.length > 0 && showBreakingNews && (
        <div className="bg-red-600 text-white py-2 relative overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center">
            <div className="flex items-center space-x-2 flex-shrink-0">
              <BellIcon className="h-4 w-4" />
              <span className="font-semibold text-sm">BREAKING:</span>
            </div>
            <div className="flex-1 overflow-hidden">
              <div className="animate-ticker whitespace-nowrap">
                {breakingNews.map((news, index) => (
                  <span key={news.id} className="mx-8 text-sm">
                    <Link 
                      href={`/article/${news.id}`}
                      className="hover:text-yellow-300 transition-colors"
                    >
                      {news.headline || news.title}
                    </Link>
                    {index < breakingNews.length - 1 && ' • '}
                  </span>
                ))}
              </div>
            </div>
            <button
              onClick={() => setShowBreakingNews(false)}
              className="flex-shrink-0 ml-4 text-white hover:text-red-200"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Main Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <NewspaperIcon className="h-8 w-8 text-primary-600" />
            <span className="text-xl font-bold text-gray-900">Pitchko News</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className="flex items-center space-x-1 text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Search Bar */}
          <div className="hidden md:block flex-1 max-w-md mx-8">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search news..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            </form>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-2">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-md text-gray-700 hover:text-primary-600 hover:bg-gray-100"
            >
              {isMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-4">
            {/* Mobile Search */}
            <form onSubmit={handleSearch} className="px-4 pb-4">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search news..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              </div>
            </form>

            {/* Mobile Nav Links */}
            <nav className="space-y-1 px-4">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setIsMenuOpen(false)}
                    className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 hover:bg-gray-50 px-3 py-2 rounded-md text-base font-medium"
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
