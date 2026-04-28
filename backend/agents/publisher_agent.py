from typing import Dict, Any, List
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from .base_agent import BaseAgent
from database import SessionLocal
from models import NewsArticle, Source, RawSource

class PublisherAgent(BaseAgent):
    def __init__(self):
        super().__init__("PublisherAgent")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save content to database and trigger frontend updates"""
        start_time = datetime.now()
        
        try:
            articles = data.get("articles", [])
            if not articles:
                return {"published_articles": [], "published_count": 0}
            
            published_articles = []
            
            for article in articles:
                published_article = await self.publish_article(article)
                if published_article:
                    published_articles.append(published_article)
            
            # Trigger frontend updates
            await self.trigger_frontend_updates(published_articles)
            
            # Send to social APIs (if configured)
            await self.send_to_social_apis(published_articles)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "published_articles": published_articles,
                "published_count": len(published_articles),
                "processing_time": processing_time
            }
            
            self.log_processing(data, result, processing_time)
            return result
            
        except Exception as e:
            self.logger.error(f"Publishing failed: {str(e)}")
            return {"error": str(e), "published_articles": []}
    
    async def publish_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Publish a single article to the database"""
        try:
            db = SessionLocal()
            
            # Get or create source
            source = await self.get_or_create_source(db, article)
            
            # Check if article already exists
            existing_article = await self.find_existing_article(db, article)
            if existing_article:
                # Update existing article
                await self.update_existing_article(db, existing_article, article)
                published_article = article.copy()
                published_article["id"] = existing_article.id
                published_article["action"] = "updated"
            else:
                # Create new article
                new_article = await self.create_new_article(db, article, source.id)
                published_article = article.copy()
                published_article["id"] = new_article.id
                published_article["action"] = "created"
            
            # Store raw sources if available
            if "additional_sources" in article:
                await self.store_raw_sources(db, published_article["id"], article["additional_sources"])
            
            db.close()
            
            self.logger.info(f"Article published: {article.get('title')} (ID: {published_article['id']})")
            return published_article
            
        except Exception as e:
            self.logger.error(f"Article publishing failed: {str(e)}")
            return None
    
    async def get_or_create_source(self, db: Session, article: Dict[str, Any]):
        """Get or create source record"""
        source_name = article.get("source_name", "Unknown")
        source_url = article.get("source_url", "")
        trust_score = article.get("trust_score", 0.5)
        
        # Try to find existing source
        source = db.query(Source).filter(Source.name == source_name).first()
        
        if not source:
            # Create new source
            source = Source(
                name=source_name,
                url=source_url,
                trust_score=trust_score
            )
            db.add(source)
            db.commit()
            db.refresh(source)
        
        return source
    
    async def find_existing_article(self, db: Session, article: Dict[str, Any]):
        """Find existing article by URL or title similarity"""
        article_url = article.get("url")
        article_title = article.get("title", "")
        
        if article_url:
            # Try exact URL match first
            existing = db.query(NewsArticle).filter(NewsArticle.url == article_url).first()
            if existing:
                return existing
        
        # Try title similarity
        if article_title:
            existing = db.query(NewsArticle).filter(
                NewsArticle.title.ilike(f"%{article_title[:50]}%")
            ).first()
            if existing:
                return existing
        
        return None
    
    async def update_existing_article(self, db: Session, existing_article: NewsArticle, new_data: Dict[str, Any]):
        """Update existing article with new information"""
        # Update fields if they have new values
        if new_data.get("summary"):
            existing_article.summary = new_data["summary"]
        if new_data.get("short_description"):
            existing_article.short_description = new_data["short_description"]
        if new_data.get("headline"):
            existing_article.headline = new_data["headline"]
        if new_data.get("why_it_matters"):
            existing_article.why_it_matters = new_data["why_it_matters"]
        if new_data.get("developer_impact"):
            existing_article.developer_impact = new_data["developer_impact"]
        if new_data.get("market_impact"):
            existing_article.market_impact = new_data["market_impact"]
        if new_data.get("future_prediction"):
            existing_article.future_prediction = new_data["future_prediction"]
        if new_data.get("who_should_care"):
            existing_article.who_should_care = new_data["who_should_care"]
        
        # Update scores if better
        if new_data.get("credibility_score", 0) > existing_article.credibility_score:
            existing_article.credibility_score = new_data["credibility_score"]
        if new_data.get("confidence_score", 0) > existing_article.confidence_score:
            existing_article.confidence_score = new_data["confidence_score"]
        
        # Update source count
        existing_article.source_count = max(existing_article.source_count, new_data.get("source_count", 1))
        
        # Update timestamp
        existing_article.updated_at = datetime.utcnow()
        
        db.commit()
    
    async def create_new_article(self, db: Session, article: Dict[str, Any], source_id: int) -> NewsArticle:
        """Create new article record"""
        new_article = NewsArticle(
            title=article.get("title"),
            content=article.get("content"),
            summary=article.get("summary"),
            short_description=article.get("short_description"),
            category=article.get("category"),
            impact_level=article.get("impact_level"),
            credibility_score=article.get("credibility_score", 0.5),
            confidence_score=article.get("confidence_score", 0.5),
            source_count=article.get("source_count", 1),
            headline=article.get("headline"),
            why_it_matters=article.get("why_it_matters"),
            developer_impact=article.get("developer_impact"),
            market_impact=article.get("market_impact"),
            future_prediction=article.get("future_prediction"),
            who_should_care=article.get("who_should_care"),
            url=article.get("url"),
            published_at=article.get("published_at"),
            source_id=source_id,
            is_breaking=article.get("is_breaking", False),
            is_published=True
        )
        
        db.add(new_article)
        db.commit()
        db.refresh(new_article)
        
        return new_article
    
    async def store_raw_sources(self, db: Session, article_id: int, additional_sources: List[Dict[str, Any]]):
        """Store additional raw sources"""
        for source_data in additional_sources:
            raw_source = RawSource(
                article_id=article_id,
                source_url=source_data.get("source_url"),
                source_name=source_data.get("source_name"),
                title=source_data.get("title"),
                content=source_data.get("content", ""),
                published_at=source_data.get("published_at")
            )
            db.add(raw_source)
        
        db.commit()
    
    async def trigger_frontend_updates(self, articles: List[Dict[str, Any]]):
        """Trigger frontend updates (WebSocket, cache invalidation, etc.)"""
        try:
            # This would typically involve:
            # 1. WebSocket notifications to connected clients
            # 2. Cache invalidation
            # 3. CDN purging
            # 4. Search index updates
            
            # For now, we'll just log the action
            self.logger.info(f"Triggering frontend updates for {len(articles)} articles")
            
            # In a real implementation, you might:
            # - Send WebSocket messages to connected clients
            # - Invalidate Redis cache keys
            # - Trigger webhook to frontend
            # - Update search index (Elasticsearch, etc.)
            
        except Exception as e:
            self.logger.error(f"Frontend update trigger failed: {str(e)}")
    
    async def send_to_social_apis(self, articles: List[Dict[str, Any]]):
        """Send published articles to social media APIs"""
        try:
            # This would integrate with social media APIs
            # Twitter/X, LinkedIn, Facebook, etc.
            
            for article in articles:
                if article.get("impact_level") in ["high", "critical"]:
                    # Only post high-impact articles to social media
                    await self.post_to_social_media(article)
            
        except Exception as e:
            self.logger.error(f"Social media posting failed: {str(e)}")
    
    async def post_to_social_media(self, article: Dict[str, Any]):
        """Post single article to social media"""
        try:
            # Generate social media content
            title = article.get("title", "")
            short_desc = article.get("short_description", "")
            category = article.get("category", "")
            
            # Create posts for different platforms
            twitter_post = f"{title[:100]}... #{category.replace(' ', '')} #technews"
            linkedin_post = f"{title}\n\n{short_desc}\n\n#tech #{category.replace(' ', '')}"
            
            # Log posts (in real implementation, these would be sent to APIs)
            self.logger.info(f"Twitter post: {twitter_post}")
            self.logger.info(f"LinkedIn post: {linkedin_post}")
            
            # In a real implementation:
            # - Use Twitter API v2 for posting tweets
            # - Use LinkedIn API for sharing posts
            # - Use Facebook Graph API for posting
            # - Handle rate limiting and authentication
            
        except Exception as e:
            self.logger.error(f"Social media post creation failed: {str(e)}")
    
    async def get_publishing_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get publishing statistics"""
        try:
            db = SessionLocal()
            
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get recent articles
            recent_articles = db.query(NewsArticle).filter(
                NewsArticle.created_at >= cutoff_time
            ).all()
            
            db.close()
            
            if not recent_articles:
                return {
                    "total_published": 0,
                    "by_category": {},
                    "by_impact_level": {},
                    "average_credibility": 0,
                    "breaking_news_count": 0
                }
            
            # Calculate statistics
            stats = {
                "total_published": len(recent_articles),
                "by_category": {},
                "by_impact_level": {},
                "average_credibility": sum(a.credibility_score for a in recent_articles) / len(recent_articles),
                "breaking_news_count": sum(1 for a in recent_articles if a.is_breaking)
            }
            
            # Category distribution
            for article in recent_articles:
                category = article.category or "Unknown"
                stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
                
                impact_level = article.impact_level or "Unknown"
                stats["by_impact_level"][impact_level] = stats["by_impact_level"].get(impact_level, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Publishing stats failed: {str(e)}")
            return {"error": str(e)}
    
    async def unpublish_article(self, article_id: int) -> bool:
        """Unpublish an article (soft delete)"""
        try:
            db = SessionLocal()
            
            article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
            if article:
                article.is_published = False
                db.commit()
                
                self.logger.info(f"Article unpublished: {article_id}")
                db.close()
                return True
            
            db.close()
            return False
            
        except Exception as e:
            self.logger.error(f"Article unpublish failed: {str(e)}")
            return False
