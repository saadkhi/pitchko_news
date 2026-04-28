from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
from models import NewsArticle, Source, Trend, RawSource
from schemas import NewsResponse, BreakingNewsResponse, TrendResponse

class NewsService:
    def __init__(self):
        pass
    
    async def get_news(
        self,
        db: Session,
        category: Optional[str] = None,
        impact_level: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[NewsResponse]:
        """Get news articles with optional filtering"""
        try:
            query = db.query(NewsArticle).filter(NewsArticle.is_published == True)
            
            # Apply filters
            if category:
                query = query.filter(NewsArticle.category == category)
            
            if impact_level:
                query = query.filter(NewsArticle.impact_level == impact_level)
            
            # Order by creation date (most recent first)
            query = query.order_by(desc(NewsArticle.created_at))
            
            # Apply pagination
            articles = query.offset(offset).limit(limit).all()
            
            # Convert to response format
            return [NewsResponse.from_orm(article) for article in articles]
            
        except Exception as e:
            raise Exception(f"Failed to get news: {str(e)}")
    
    async def get_article_by_id(self, db: Session, article_id: int) -> Optional[NewsResponse]:
        """Get specific article by ID"""
        try:
            article = db.query(NewsArticle).filter(
                and_(NewsArticle.id == article_id, NewsArticle.is_published == True)
            ).first()
            
            if article:
                return NewsResponse.from_orm(article)
            return None
            
        except Exception as e:
            raise Exception(f"Failed to get article: {str(e)}")
    
    async def get_breaking_news(self, db: Session, hours: int = 24) -> List[BreakingNewsResponse]:
        """Get breaking news from recent hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            articles = db.query(NewsArticle).filter(
                and_(
                    NewsArticle.is_breaking == True,
                    NewsArticle.is_published == True,
                    NewsArticle.created_at >= cutoff_time
                )
            ).order_by(desc(NewsArticle.created_at)).limit(10).all()
            
            return [BreakingNewsResponse.from_orm(article) for article in articles]
            
        except Exception as e:
            raise Exception(f"Failed to get breaking news: {str(e)}")
    
    async def get_trends(self, db: Session, days: int = 7) -> List[TrendResponse]:
        """Get trending topics and analytics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Get recent articles
            recent_articles = db.query(NewsArticle).filter(
                and_(
                    NewsArticle.is_published == True,
                    NewsArticle.created_at >= cutoff_time
                )
            ).all()
            
            if not recent_articles:
                return []
            
            # Analyze trends from articles
            trends_data = self.analyze_trends(recent_articles)
            
            # Convert to response format
            return [TrendResponse(**trend) for trend in trends_data]
            
        except Exception as e:
            raise Exception(f"Failed to get trends: {str(e)}")
    
    def analyze_trends(self, articles: List[NewsArticle]) -> List[Dict[str, Any]]:
        """Analyze trending topics from articles"""
        from collections import defaultdict, Counter
        import re
        
        trends = []
        
        # Category trends
        category_counts = Counter(article.category for article in articles)
        for category, count in category_counts.most_common(10):
            if count >= 2:  # Only include categories with at least 2 articles
                # Calculate impact distribution for this category
                category_articles = [a for a in articles if a.category == category]
                impact_dist = Counter(article.impact_level for article in category_articles)
                
                # Calculate average sentiment (simplified)
                avg_sentiment = sum(article.credibility_score for article in category_articles) / len(category_articles)
                
                trends.append({
                    "keyword": category,
                    "category": category,
                    "count": count,
                    "sentiment_score": avg_sentiment,
                    "impact_distribution": dict(impact_dist),
                    "date": datetime.utcnow(),
                    "id": len(trends) + 1
                })
        
        # Extract trending keywords from titles
        all_titles = " ".join(article.title for article in articles)
        words = re.findall(r'\b\w+\b', all_titles.lower())
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'not', 'no', 'yes', 'if', 'then', 'else', 'so', 'because', 'as', 'than', 'like', 'just', 'now', 'new', 'said', 'says'}
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        word_counts = Counter(filtered_words)
        
        # Add top keywords as trends
        for word, count in word_counts.most_common(5):
            if count >= 3:  # Only include words that appear at least 3 times
                trends.append({
                    "keyword": word,
                    "category": "keyword",
                    "count": count,
                    "sentiment_score": 0.7,  # Default sentiment
                    "impact_distribution": {"medium": count},
                    "date": datetime.utcnow(),
                    "id": len(trends) + 1
                })
        
        return trends
    
    async def search_news(
        self,
        db: Session,
        query: str,
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[NewsResponse]:
        """Search news articles"""
        try:
            # Create search query
            search_filter = or_(
                NewsArticle.title.ilike(f"%{query}%"),
                NewsArticle.content.ilike(f"%{query}%"),
                NewsArticle.summary.ilike(f"%{query}%"),
                NewsArticle.headline.ilike(f"%{query}%")
            )
            
            db_query = db.query(NewsArticle).filter(
                and_(
                    NewsArticle.is_published == True,
                    search_filter
                )
            )
            
            if category:
                db_query = db_query.filter(NewsArticle.category == category)
            
            articles = db_query.order_by(desc(NewsArticle.created_at)).offset(offset).limit(limit).all()
            
            return [NewsResponse.from_orm(article) for article in articles]
            
        except Exception as e:
            raise Exception(f"Failed to search news: {str(e)}")
    
    async def get_related_articles(self, db: Session, article_id: int, limit: int = 5) -> List[NewsResponse]:
        """Get articles related to the given article"""
        try:
            # Get the reference article
            article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
            if not article:
                return []
            
            # Find related articles based on category and keywords
            related_query = db.query(NewsArticle).filter(
                and_(
                    NewsArticle.id != article_id,
                    NewsArticle.is_published == True,
                    NewsArticle.category == article.category
                )
            )
            
            # Add keyword matching (simplified)
            keywords = self.extract_keywords(article.title + " " + article.summary)
            for keyword in keywords[:3]:  # Limit to top 3 keywords
                related_query = related_query.filter(
                    or_(
                        NewsArticle.title.ilike(f"%{keyword}%"),
                        NewsArticle.content.ilike(f"%{keyword}%")
                    )
                )
            
            related_articles = related_query.order_by(desc(NewsArticle.created_at)).limit(limit).all()
            
            return [NewsResponse.from_orm(article) for article in related_articles]
            
        except Exception as e:
            raise Exception(f"Failed to get related articles: {str(e)}")
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        import re
        from collections import Counter
        
        words = re.findall(r'\b\w+\b', text.lower())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'not', 'no', 'yes', 'if', 'then', 'else', 'so', 'because', 'as', 'than', 'like', 'just', 'now', 'new', 'said', 'says'}
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 4]
        word_counts = Counter(filtered_words)
        
        return [word for word, count in word_counts.most_common(10)]
    
    async def get_news_by_source(self, db: Session, source_id: int, limit: int = 20) -> List[NewsResponse]:
        """Get news articles by source"""
        try:
            articles = db.query(NewsArticle).filter(
                and_(
                    NewsArticle.source_id == source_id,
                    NewsArticle.is_published == True
                )
            ).order_by(desc(NewsArticle.created_at)).limit(limit).all()
            
            return [NewsResponse.from_orm(article) for article in articles]
            
        except Exception as e:
            raise Exception(f"Failed to get news by source: {str(e)}")
    
    async def get_news_statistics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Get news statistics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Total articles
            total_articles = db.query(NewsArticle).filter(
                and_(
                    NewsArticle.is_published == True,
                    NewsArticle.created_at >= cutoff_time
                )
            ).count()
            
            # By category
            category_stats = db.query(
                NewsArticle.category,
                func.count(NewsArticle.id).label('count'),
                func.avg(NewsArticle.credibility_score).label('avg_credibility')
            ).filter(
                and_(
                    NewsArticle.is_published == True,
                    NewsArticle.created_at >= cutoff_time
                )
            ).group_by(NewsArticle.category).all()
            
            # By impact level
            impact_stats = db.query(
                NewsArticle.impact_level,
                func.count(NewsArticle.id).label('count')
            ).filter(
                and_(
                    NewsArticle.is_published == True,
                    NewsArticle.created_at >= cutoff_time
                )
            ).group_by(NewsArticle.impact_level).all()
            
            # Breaking news count
            breaking_count = db.query(NewsArticle).filter(
                and_(
                    NewsArticle.is_breaking == True,
                    NewsArticle.is_published == True,
                    NewsArticle.created_at >= cutoff_time
                )
            ).count()
            
            return {
                "total_articles": total_articles,
                "breaking_news_count": breaking_count,
                "by_category": [
                    {
                        "category": stat.category,
                        "count": stat.count,
                        "avg_credibility": float(stat.avg_credibility) if stat.avg_credibility else 0
                    }
                    for stat in category_stats
                ],
                "by_impact_level": [
                    {
                        "impact_level": stat.impact_level,
                        "count": stat.count
                    }
                    for stat in impact_stats
                ]
            }
            
        except Exception as e:
            raise Exception(f"Failed to get news statistics: {str(e)}")
