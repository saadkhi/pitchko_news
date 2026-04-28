'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '@/components/Layout/Header';
import Footer from '@/components/Layout/Footer';
import ArticleCard from '@/components/News/ArticleCard';
import { newsAPI, NewsArticle, formatRelativeTime, getImpactColor, getCategoryColor } from '@/lib/api';
import { 
  ArrowLeftIcon,
  ShareIcon,
  BookmarkIcon,
  ClockIcon,
  EyeIcon,
  PlayIcon,
  ChartBarIcon,
  UserGroupIcon,
  TrendingUpIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const ArticlePage = () => {
  const params = useParams();
  const router = useRouter();
  const articleId = params.id as string;
  
  const [article, setArticle] = useState<NewsArticle | null>(null);
  const [relatedArticles, setRelatedArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [isBookmarked, setIsBookmarked] = useState(false);

  useEffect(() => {
    if (articleId) {
      fetchArticle();
      fetchRelatedArticles();
    }
  }, [articleId]);

  const fetchArticle = async () => {
    try {
      setLoading(true);
      const data = await newsAPI.getArticle(parseInt(articleId));
      setArticle(data);
    } catch (error) {
      console.error('Failed to fetch article:', error);
      toast.error('Failed to load article');
      router.push('/');
    } finally {
      setLoading(false);
    }
  };

  const fetchRelatedArticles = async () => {
    try {
      const data = await newsAPI.getRelatedArticles(parseInt(articleId));
      setRelatedArticles(data);
    } catch (error) {
      console.error('Failed to fetch related articles:', error);
    }
  };

  const handleShare = async () => {
    if (navigator.share && article) {
      try {
        await navigator.share({
          title: article.title,
          text: article.short_description || article.summary,
          url: window.location.href,
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied to clipboard!');
    }
  };

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
    toast(isBookmarked ? 'Removed from bookmarks' : 'Added to bookmarks');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-6"></div>
            <div className="space-y-4">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!article) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Article not found</h1>
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Go Home
            </button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const impactClasses = getImpactColor(article.impact_level);
  const categoryClasses = getCategoryColor(article.category);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeftIcon className="h-5 w-5" />
          <span>Back to News</span>
        </button>

        {/* Article Header */}
        <article className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 lg:p-8">
            {/* Article Meta */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${categoryClasses}`}>
                  {article.category}
                </span>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${impactClasses}`}>
                  {article.impact_level}
                </span>
                {article.is_breaking && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 border border-red-200">
                    BREAKING
                  </span>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleShare}
                  className="p-2 text-gray-500 hover:text-primary-600 transition-colors"
                  aria-label="Share article"
                >
                  <ShareIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={handleBookmark}
                  className={`p-2 transition-colors ${isBookmarked ? 'text-primary-600' : 'text-gray-500 hover:text-primary-600'}`}
                  aria-label="Bookmark article"
                >
                  <BookmarkIcon className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Title */}
            <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4 leading-tight">
              {article.headline || article.title}
            </h1>

            {/* Article Info */}
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-gray-200">
              <div className="flex items-center space-x-6 text-sm text-gray-500">
                <span className="flex items-center space-x-1">
                  <ClockIcon className="h-4 w-4" />
                  <span>{formatRelativeTime(article.created_at)}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <EyeIcon className="h-4 w-4" />
                  <span>{article.source_count} sources</span>
                </span>
                <span className="flex items-center space-x-1">
                  <span className="font-medium">Credibility:</span>
                  <span className={`font-medium ${
                    article.credibility_score >= 0.8 ? 'text-green-600' :
                    article.credibility_score >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {(article.credibility_score * 100).toFixed(0)}%
                  </span>
                </span>
              </div>
              
              {article.is_video_generated && (
                <a
                  href={`/videos/${article.id}`}
                  className="inline-flex items-center space-x-1 text-primary-600 hover:text-primary-700 font-medium"
                >
                  <PlayIcon className="h-5 w-5" />
                  <span>Watch Video</span>
                </a>
              )}
            </div>

            {/* Short Description */}
            {article.short_description && (
              <div className="mb-8">
                <p className="text-xl text-gray-600 leading-relaxed italic">
                  {article.short_description}
                </p>
              </div>
            )}

            {/* Main Content */}
            <div className="prose prose-lg max-w-none mb-8">
              {article.full_article ? (
                <div dangerouslySetInnerHTML={{ __html: article.full_article.replace(/\n/g, '<br>') }} />
              ) : (
                <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {article.content}
                </div>
              )}
            </div>

            {/* Insights Section */}
            {(article.why_it_matters || article.developer_impact || article.market_impact || article.future_prediction) && (
              <div className="border-t border-gray-200 pt-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                  <ChartBarIcon className="h-6 w-6 text-primary-600" />
                  <span>Key Insights</span>
                </h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {article.why_it_matters && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                      <h3 className="font-semibold text-blue-900 mb-3 flex items-center space-x-2">
                        <UserGroupIcon className="h-5 w-5" />
                        <span>Why It Matters</span>
                      </h3>
                      <p className="text-blue-700 leading-relaxed">{article.why_it_matters}</p>
                    </div>
                  )}
                  
                  {article.developer_impact && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                      <h3 className="font-semibold text-green-900 mb-3 flex items-center space-x-2">
                        <PlayIcon className="h-5 w-5" />
                        <span>Developer Impact</span>
                      </h3>
                      <p className="text-green-700 leading-relaxed">{article.developer_impact}</p>
                    </div>
                  )}
                  
                  {article.market_impact && (
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                      <h3 className="font-semibold text-purple-900 mb-3 flex items-center space-x-2">
                        <TrendingUpIcon className="h-5 w-5" />
                        <span>Market Impact</span>
                      </h3>
                      <p className="text-purple-700 leading-relaxed">{article.market_impact}</p>
                    </div>
                  )}
                  
                  {article.future_prediction && (
                    <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
                      <h3 className="font-semibold text-orange-900 mb-3 flex items-center space-x-2">
                        <ChartBarIcon className="h-5 w-5" />
                        <span>Future Prediction</span>
                      </h3>
                      <p className="text-orange-700 leading-relaxed">{article.future_prediction}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Who Should Care */}
            {article.who_should_care && (
              <div className="border-t border-gray-200 pt-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Who Should Care</h2>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <p className="text-gray-700 leading-relaxed">{article.who_should_care}</p>
                </div>
              </div>
            )}

            {/* Sources */}
            {article.source && (
              <div className="border-t border-gray-200 pt-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Source Information</h3>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{article.source.name}</p>
                      <p className="text-sm text-gray-500">Trust Score: {(article.source.trust_score * 100).toFixed(0)}%</p>
                    </div>
                    {article.url && (
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                      >
                        View Original →
                      </a>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </article>

        {/* Related Articles */}
        {relatedArticles.length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Related Articles</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {relatedArticles.map((relatedArticle) => (
                <ArticleCard 
                  key={relatedArticle.id} 
                  article={relatedArticle} 
                  variant="compact" 
                />
              ))}
            </div>
          </div>
        )}
      </main>
      
      <Footer />
    </div>
  );
};

export default ArticlePage;
