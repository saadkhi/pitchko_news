'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Header from '@/components/Layout/Header';
import Footer from '@/components/Layout/Footer';
import ArticleCard from '@/components/News/ArticleCard';
import { newsAPI, NewsArticle } from '@/lib/api';
import { 
  NewspaperIcon, 
  FunnelIcon,
  ArrowPathIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const HomePage = () => {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [featuredArticle, setFeaturedArticle] = useState<NewsArticle | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedImpact, setSelectedImpact] = useState<string>('');
  const searchParams = useSearchParams();

  const categories = ['All', 'AI', 'Startups', 'Cybersecurity', 'Big Tech'];
  const impactLevels = ['All', 'critical', 'high', 'medium', 'low'];

  useEffect(() => {
    fetchArticles();
    
    // Check for URL parameters
    const category = searchParams.get('category');
    const impact = searchParams.get('impact');
    
    if (category) setSelectedCategory(category);
    if (impact) setSelectedImpact(impact);
  }, [searchParams]);

  const fetchArticles = async () => {
    try {
      setLoading(true);
      const params: any = {
        limit: 20,
        offset: 0
      };
      
      if (selectedCategory && selectedCategory !== 'All') {
        params.category = selectedCategory;
      }
      
      if (selectedImpact && selectedImpact !== 'All') {
        params.impact_level = selectedImpact;
      }

      const data = await newsAPI.getNews(params);
      
      // Set first article as featured if available
      if (data.length > 0) {
        setFeaturedArticle(data[0]);
        setArticles(data.slice(1));
      } else {
        setArticles(data);
      }
    } catch (error) {
      console.error('Failed to fetch articles:', error);
      toast.error('Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await newsAPI.triggerAgents();
      toast.success('News pipeline triggered successfully');
      // Wait a bit then refresh
      setTimeout(() => {
        fetchArticles();
        setRefreshing(false);
      }, 3000);
    } catch (error) {
      console.error('Failed to trigger agents:', error);
      toast.error('Failed to refresh news');
      setRefreshing(false);
    }
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    // Update URL without page reload
    const params = new URLSearchParams(searchParams.toString());
    if (category === 'All') {
      params.delete('category');
    } else {
      params.set('category', category);
    }
    window.history.pushState(null, '', `?${params.toString()}`);
    fetchArticles();
  };

  const handleImpactChange = (impact: string) => {
    setSelectedImpact(impact);
    // Update URL without page reload
    const params = new URLSearchParams(searchParams.toString());
    if (impact === 'All') {
      params.delete('impact');
    } else {
      params.set('impact', impact);
    }
    window.history.pushState(null, '', `?${params.toString()}`);
    fetchArticles();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-2">
                <NewspaperIcon className="h-8 w-8 text-primary-600" />
                <span>Latest Tech News</span>
              </h1>
              <p className="text-gray-600 mt-2">
                AI-powered news aggregation and analysis from trusted sources
              </p>
            </div>
            
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ArrowPathIcon className={`h-5 w-5 ${refreshing ? 'animate-spin' : ''}`} />
              <span>{refreshing ? 'Refreshing...' : 'Refresh News'}</span>
            </button>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center space-x-2 mb-3">
              <FunnelIcon className="h-5 w-5 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Filters:</span>
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
                      onClick={() => handleCategoryChange(category)}
                      className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                        selectedCategory === category
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
                      onClick={() => handleImpactChange(level)}
                      className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                        selectedImpact === level
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

        {/* Featured Article */}
        {featuredArticle && (
          <div className="mb-8">
            <div className="flex items-center space-x-2 mb-4">
              <SparklesIcon className="h-5 w-5 text-yellow-500" />
              <h2 className="text-xl font-semibold text-gray-900">Featured Story</h2>
            </div>
            <ArticleCard article={featuredArticle} variant="featured" />
          </div>
        )}

        {/* Articles Grid */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Latest Articles
            {articles.length > 0 && (
              <span className="text-sm font-normal text-gray-500 ml-2">
                ({articles.length} articles)
              </span>
            )}
          </h2>
          
          {articles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {articles.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <NewspaperIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No articles found</h3>
              <p className="text-gray-500 mb-4">
                Try adjusting your filters or check back later for new content.
              </p>
              <button
                onClick={() => {
                  setSelectedCategory('All');
                  setSelectedImpact('All');
                  fetchArticles();
                }}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          )}
        </div>

        {/* Load More */}
        {articles.length >= 18 && (
          <div className="mt-12 text-center">
            <button
              onClick={() => {
                // TODO: Implement pagination
                toast('Pagination coming soon!');
              }}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              Load More Articles
            </button>
          </div>
        )}
      </main>
      
      <Footer />
    </div>
  );
};

export default HomePage;
