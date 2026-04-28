'use client';

import Link from 'next/link';
import Image from 'next/image';
import { formatRelativeTime, getImpactColor, getCategoryColor, NewsArticle } from '@/lib/api';
import { 
  ClockIcon, 
  EyeIcon, 
  ShareIcon,
  BookmarkIcon,
  PlayIcon
} from '@heroicons/react/24/outline';
import { useState } from 'react';

interface ArticleCardProps {
  article: NewsArticle;
  variant?: 'default' | 'compact' | 'featured';
  showVideo?: boolean;
}

const ArticleCard = ({ 
  article, 
  variant = 'default', 
  showVideo = true 
}: ArticleCardProps) => {
  const [isBookmarked, setIsBookmarked] = useState(false);

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: article.title,
          text: article.short_description || article.summary,
          url: `/article/${article.id}`,
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(`${window.location.origin}/article/${article.id}`);
    }
  };

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
    // Here you would typically save to backend/localStorage
  };

  const impactClasses = getImpactColor(article.impact_level);
  const categoryClasses = getCategoryColor(article.category);

  if (variant === 'compact') {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
        <div className="flex space-x-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${categoryClasses}`}>
                {article.category}
              </span>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${impactClasses}`}>
                {article.impact_level}
              </span>
            </div>
            
            <Link href={`/article/${article.id}`}>
              <h3 className="text-lg font-semibold text-gray-900 hover:text-primary-600 transition-colors line-clamp-2">
                {article.headline || article.title}
              </h3>
            </Link>
            
            <p className="text-gray-600 text-sm mt-1 line-clamp-2">
              {article.short_description || article.summary}
            </p>
            
            <div className="flex items-center justify-between mt-3">
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span className="flex items-center space-x-1">
                  <ClockIcon className="h-4 w-4" />
                  <span>{formatRelativeTime(article.created_at)}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <EyeIcon className="h-4 w-4" />
                  <span>{article.source_count} sources</span>
                </span>
              </div>
              
              {article.is_video_generated && showVideo && (
                <Link 
                  href={`/videos/${article.id}`}
                  className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                >
                  <PlayIcon className="h-4 w-4" />
                  <span className="text-sm">Video</span>
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'featured') {
    return (
      <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
        <div className="relative h-64 bg-gradient-to-br from-primary-500 to-primary-600">
          <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center">
            <div className="text-center text-white p-6">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border border-white bg-white bg-opacity-20`}>
                  {article.category}
                </span>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border border-white bg-white bg-opacity-20`}>
                  {article.impact_level}
                </span>
              </div>
              
              <Link href={`/article/${article.id}`}>
                <h1 className="text-2xl font-bold mb-2 hover:text-yellow-300 transition-colors">
                  {article.headline || article.title}
                </h1>
              </Link>
              
              <p className="text-lg opacity-90 line-clamp-3">
                {article.short_description || article.summary}
              </p>
              
              {article.is_video_generated && showVideo && (
                <div className="mt-4">
                  <Link 
                    href={`/videos/${article.id}`}
                    className="inline-flex items-center space-x-2 bg-white text-primary-600 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <PlayIcon className="h-5 w-5" />
                    <span className="font-medium">Watch Video</span>
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 text-sm text-gray-500">
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
                <span className="text-green-600 font-medium">
                  {(article.credibility_score * 100).toFixed(0)}%
                </span>
              </span>
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
        </div>
      </div>
    );
  }

  // Default variant
  return (
    <article className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all duration-200">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${categoryClasses}`}>
              {article.category}
            </span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${impactClasses}`}>
              {article.impact_level}
            </span>
            {article.is_breaking && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
                BREAKING
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleShare}
              className="p-1.5 text-gray-500 hover:text-primary-600 transition-colors"
              aria-label="Share article"
            >
              <ShareIcon className="h-4 w-4" />
            </button>
            <button
              onClick={handleBookmark}
              className={`p-1.5 transition-colors ${isBookmarked ? 'text-primary-600' : 'text-gray-500 hover:text-primary-600'}`}
              aria-label="Bookmark article"
            >
              <BookmarkIcon className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Title */}
        <Link href={`/article/${article.id}`}>
          <h2 className="text-xl font-semibold text-gray-900 hover:text-primary-600 transition-colors mb-3 line-clamp-2">
            {article.headline || article.title}
          </h2>
        </Link>

        {/* Description */}
        <p className="text-gray-600 mb-4 line-clamp-3">
          {article.short_description || article.summary}
        </p>

        {/* Key Insights */}
        {(article.why_it_matters || article.developer_impact) && (
          <div className="mb-4 space-y-2">
            {article.why_it_matters && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <h4 className="font-medium text-blue-900 text-sm mb-1">Why it matters:</h4>
                <p className="text-blue-700 text-sm line-clamp-2">{article.why_it_matters}</p>
              </div>
            )}
            {article.developer_impact && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <h4 className="font-medium text-green-900 text-sm mb-1">Developer impact:</h4>
                <p className="text-green-700 text-sm line-clamp-2">{article.developer_impact}</p>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center space-x-4 text-sm text-gray-500">
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
          
          {article.is_video_generated && showVideo && (
            <Link 
              href={`/videos/${article.id}`}
              className="inline-flex items-center space-x-1 text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              <PlayIcon className="h-4 w-4" />
              <span>Video</span>
            </Link>
          )}
        </div>
      </div>
    </article>
  );
};

export default ArticleCard;
