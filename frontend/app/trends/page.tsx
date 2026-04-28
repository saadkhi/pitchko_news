'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Layout/Header';
import Footer from '@/components/Layout/Footer';
import { newsAPI, Trend } from '@/lib/api';
import { 
  ChartBarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  ArrowPathIcon,
  SparklesIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import toast from 'react-hot-toast';

const TrendsPage = () => {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  const timeRanges = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
  ];

  useEffect(() => {
    fetchTrends();
  }, [selectedTimeRange]);

  const fetchTrends = async () => {
    try {
      setLoading(true);
      const data = await newsAPI.getTrends();
      setTrends(data);
    } catch (error) {
      console.error('Failed to fetch trends:', error);
      toast.error('Failed to load trends');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetchTrends();
      toast.success('Trends refreshed successfully');
    } catch (error) {
      toast.error('Failed to refresh trends');
    } finally {
      setRefreshing(false);
    }
  };

  const getSentimentColor = (score: number) => {
    if (score >= 0.7) return '#10b981'; // green
    if (score >= 0.4) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  const getSentimentLabel = (score: number) => {
    if (score >= 0.7) return 'Positive';
    if (score >= 0.4) return 'Neutral';
    return 'Negative';
  };

  const getTrendIcon = (trend: Trend) => {
    const totalImpact = Object.values(trend.impact_distribution).reduce((a, b) => a + b, 0);
    const criticalHigh = (trend.impact_distribution.critical || 0) + (trend.impact_distribution.high || 0);
    
    if (criticalHigh / totalImpact > 0.6) {
      return <TrendingUpIcon className="h-5 w-5 text-red-500" />;
    } else if (criticalHigh / totalImpact > 0.3) {
      return <TrendingUpIcon className="h-5 w-5 text-yellow-500" />;
    }
    return <TrendingDownIcon className="h-5 w-5 text-green-500" />;
  };

  // Prepare data for charts
  const categoryData = trends.reduce((acc: any[], trend) => {
    const existing = acc.find(item => item.category === trend.category);
    if (existing) {
      existing.count += trend.count;
      existing.sentiment = (existing.sentiment + trend.sentiment_score) / 2;
    } else {
      acc.push({
        category: trend.category,
        count: trend.count,
        sentiment: trend.sentiment_score
      });
    }
    return acc;
  }, []);

  const impactData = trends.reduce((acc: any[], trend) => {
    Object.entries(trend.impact_distribution).forEach(([impact, count]) => {
      const existing = acc.find(item => item.impact === impact);
      if (existing) {
        existing.count += count;
      } else {
        acc.push({ impact, count });
      }
    });
    return acc;
  }, []);

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

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
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-2">
                <ChartBarIcon className="h-8 w-8 text-primary-600" />
                <span>Trends & Analytics</span>
              </h1>
              <p className="text-gray-600 mt-2">
                Real-time insights into tech news trends and patterns
              </p>
            </div>
            
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ArrowPathIcon className={`h-5 w-5 ${refreshing ? 'animate-spin' : ''}`} />
              <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
            </button>
          </div>

          {/* Time Range Selector */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700">Time Range:</span>
              <div className="flex space-x-2">
                {timeRanges.map((range) => (
                  <button
                    key={range.value}
                    onClick={() => setSelectedTimeRange(range.value)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                      selectedTimeRange === range.value
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {range.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Trends</p>
                <p className="text-2xl font-bold text-gray-900">{trends.length}</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-primary-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Sentiment</p>
                <p className="text-2xl font-bold text-gray-900">
                  {trends.length > 0 
                    ? (trends.reduce((sum, t) => sum + t.sentiment_score, 0) / trends.length).toFixed(2)
                    : '0.00'
                  }
                </p>
              </div>
              <SparklesIcon className="h-8 w-8 text-yellow-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">High Impact</p>
                <p className="text-2xl font-bold text-gray-900">
                  {impactData.find(d => d.impact === 'high')?.count || 0}
                </p>
              </div>
              <TrendingUpIcon className="h-8 w-8 text-red-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Mentions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {trends.reduce((sum, t) => sum + t.count, 0)}
                </p>
              </div>
              <EyeIcon className="h-8 w-8 text-green-500" />
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Category Distribution */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Trends by Category</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Impact Distribution */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Impact Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={impactData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ impact, count }) => `${impact}: ${count}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {impactData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Trends Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Trending Topics</h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Topic
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Mentions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sentiment
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Impact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Trend
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {trends.map((trend) => (
                  <tr key={trend.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {trend.keyword}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {trend.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{trend.count}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: getSentimentColor(trend.sentiment_score) }}
                        />
                        <span className="text-sm text-gray-900">
                          {getSentimentLabel(trend.sentiment_score)}
                        </span>
                        <span className="text-sm text-gray-500">
                          ({trend.sentiment_score.toFixed(2)})
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {Object.entries(trend.impact_distribution).map(([impact, count]) => (
                          <span key={impact} className="inline-flex items-center mr-2">
                            <span className="text-xs capitalize">{impact}:</span>
                            <span className="text-xs font-medium ml-1">{count}</span>
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getTrendIcon(trend)}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Insights */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-2">Top Category</h4>
              <p className="text-blue-700">
                {categoryData.length > 0 
                  ? `${categoryData.reduce((max, item) => item.count > max.count ? item : max).category} leads with ${categoryData.reduce((max, item) => item.count > max.count ? item : max).count} mentions`
                  : 'No data available'
                }
              </p>
            </div>
            
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-medium text-green-900 mb-2">Overall Sentiment</h4>
              <p className="text-green-700">
                {trends.length > 0 
                  ? `${getSentimentLabel(trends.reduce((sum, t) => sum + t.sentiment_score, 0) / trends.length)} sentiment across all trends`
                  : 'No data available'
                }
              </p>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default TrendsPage;
