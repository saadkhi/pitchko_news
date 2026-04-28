'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Header from '@/components/Layout/Header';
import Footer from '@/components/Layout/Footer';
import ArticleCard from '@/components/News/ArticleCard';
import { newsAPI, NewsArticle } from '@/lib/api';
import { 
  MagnifyingGlassIcon,
  FunnelIcon,
  XMarkIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const SearchPage = () => {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  
  const [query, setQuery] = useState(initialQuery);
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [filters, setFilters] = useState({
    category: '',
    impact_level: ''
  });

  const categories = ['All', 'AI', 'Startups', 'Cybersecurity', 'Big Tech'];
  const impactLevels = ['All', 'critical', 'high', 'medium', 'low'];

  useEffect(() => {
    if (initialQuery) {
      performSearch(initialQuery);
    }
  }, [initialQuery]);

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search term');
      return;
    }

    try {
      setLoading(true);
      setSearched(true);
      
      const params: any = {
        q: searchQuery,
        limit: 20
      };
      
      if (filters.category && filters.category !== 'All') {
        params.category = filters.category;
      }
      
      if (filters.impact_level && filters.impact_level !== 'All') {
        params.impact_level = filters.impact_level;
      }

      const data = await newsAPI.searchNews(searchQuery, params);
      setArticles(data);
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      const params = new URLSearchParams();
      params.set('q', query.trim());
      
      if (filters.category && filters.category !== 'All') {
        params.set('category', filters.category);
      }
      
      if (filters.impact_level && filters.impact_level !== 'All') {
        params.set('impact', filters.impact_level);
      }
      
      window.history.pushState(null, '', `/search?${params.toString()}`);
      performSearch(query.trim());
    }
  };

  const clearFilters = () => {
    setFilters({ category: '', impact_level: '' });
    if (query.trim()) {
      performSearch(query.trim());
    }
  };

  const getRecentSearches = () => {
    if (typeof window !== 'undefined') {
      const searches = localStorage.getItem('recentSearches');
      return searches ? JSON.parse(searches) : [];
    }
    return [];
  };

  const saveRecentSearch = (searchTerm: string) => {
    if (typeof window !== 'undefined') {
      const recent = getRecentSearches();
      const filtered = recent.filter((s: string) => s !== searchTerm);
      filtered.unshift(searchTerm);
      const updated = filtered.slice(0, 5); // Keep only 5 recent searches
      localStorage.setItem('recentSearches', JSON.stringify(updated));
    }
  };

  const handleRecentSearch = (searchTerm: string) => {
    setQuery(searchTerm);
    performSearch(searchTerm);
  };

  const recentSearches = getRecentSearches();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Search News</h1>
          
          {/* Search Form */}
          <form onSubmit={handleSearch} className="mb-6">
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <MagnifyingGlassIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search for news, topics, companies..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
                />
              </div>
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>

          {/* Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <FunnelIcon className="h-5 w-5 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Filters</span>
              </div>
              
              {(filters.category || filters.impact_level) && (
                <button
                  onClick={clearFilters}
                  className="flex items-center space-x-1 text-sm text-primary-600 hover:text-primary-700"
                >
                  <XMarkIcon className="h-4 w-4" />
                  <span>Clear Filters</span>
                </button>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <div className="flex flex-wrap gap-2">
                  {categories.map((category) => (
                    <button
                      key={category}
                      onClick={() => {
                        const newFilters = { ...filters, category: category === 'All' ? '' : category };
                        setFilters(newFilters);
                        if (query.trim()) {
                          performSearch(query.trim());
                        }
                      }}
                      className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                        (filters.category || 'All') === category
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Impact Level
                </label>
                <div className="flex flex-wrap gap-2">
                  {impactLevels.map((level) => (
                    <button
                      key={level}
                      onClick={() => {
                        const newFilters = { ...filters, impact_level: level === 'All' ? '' : level };
                        setFilters(newFilters);
                        if (query.trim()) {
                          performSearch(query.trim());
                        }
                      }}
                      className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                        (filters.impact_level || 'All') === level
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Searches */}
        {!searched && recentSearches.length > 0 && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <ClockIcon className="h-5 w-5 text-gray-500" />
              <span>Recent Searches</span>
            </h2>
            <div className="flex flex-wrap gap-2">
              {recentSearches.map((searchTerm: string, index: number) => (
                <button
                  key={index}
                  onClick={() => handleRecentSearch(searchTerm)}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
                >
                  {searchTerm}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Search Results */}
        {searched && (
          <div>
            <div className="mb-6">
              {loading ? (
                <p className="text-gray-600">Searching...</p>
              ) : (
                <p className="text-gray-600">
                  {articles.length > 0 
                    ? `Found ${articles.length} result${articles.length !== 1 ? 's' : ''} for "${query}"`
                    : `No results found for "${query}"`
                  }
                </p>
              )}
            </div>

            {articles.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {articles.map((article) => (
                  <ArticleCard key={article.id} article={article} />
                ))}
              </div>
            )}

            {!loading && articles.length === 0 && (
              <div className="text-center py-12">
                <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
                <p className="text-gray-500 mb-4">
                  Try different keywords or adjust your filters.
                </p>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">Suggestions:</p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Check your spelling</li>
                    <li>• Try more general keywords</li>
                    <li>• Use fewer filters</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
      
      <Footer />
    </div>
  );
};

export default SearchPage;
