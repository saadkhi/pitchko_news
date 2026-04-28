from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from .base_agent import BaseAgent
from database import SessionLocal
from models import NewsArticle

class BreakingNewsAgent(BaseAgent):
    def __init__(self):
        super().__init__("BreakingNewsAgent")
        self.breaking_threshold = {
            "impact_level": ["high", "critical"],
            "credibility_score": 0.75,
            "min_sources": 2
        }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and publish breaking news articles"""
        start_time = datetime.now()
        
        try:
            articles = data.get("articles", [])
            if not articles:
                return {"breaking_news": [], "published_count": 0}
            
            # Filter for breaking news criteria
            breaking_candidates = self.filter_breaking_candidates(articles)
            
            # Validate breaking news
            validated_breaking = []
            for article in breaking_candidates:
                if await self.validate_breaking_news(article):
                    validated_breaking.append(article)
            
            # Publish breaking news
            published_breaking = []
            for article in validated_breaking:
                published_article = await self.publish_breaking_news(article)
                if published_article:
                    published_breaking.append(published_article)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "breaking_news": published_breaking,
                "candidates_found": len(breaking_candidates),
                "validated_count": len(validated_breaking),
                "published_count": len(published_breaking),
                "processing_time": processing_time
            }
            
            self.log_processing(data, result, processing_time)
            return result
            
        except Exception as e:
            self.logger.error(f"Breaking news processing failed: {str(e)}")
            return {"error": str(e), "breaking_news": []}
    
    def filter_breaking_candidates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter articles that meet breaking news criteria"""
        candidates = []
        
        for article in articles:
            impact_level = article.get("impact_level", "").lower()
            credibility_score = article.get("credibility_score", 0)
            source_count = article.get("source_count", 1)
            
            # Check breaking news criteria
            if (impact_level in self.breaking_threshold["impact_level"] and
                credibility_score >= self.breaking_threshold["credibility_score"] and
                source_count >= self.breaking_threshold["min_sources"]):
                
                # Add breaking news metadata
                article["is_breaking_candidate"] = True
                article["breaking_score"] = self.calculate_breaking_score(article)
                candidates.append(article)
        
        # Sort by breaking score
        candidates.sort(key=lambda x: x.get("breaking_score", 0), reverse=True)
        
        return candidates
    
    def calculate_breaking_score(self, article: Dict[str, Any]) -> float:
        """Calculate breaking news score"""
        impact_level = article.get("impact_level", "").lower()
        credibility_score = article.get("credibility_score", 0)
        source_count = article.get("source_count", 1)
        confidence_score = article.get("confidence_score", 0)
        
        # Base score from impact level
        impact_scores = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.3}
        base_score = impact_scores.get(impact_level, 0.3)
        
        # Boost from credibility
        credibility_boost = credibility_score * 0.3
        
        # Boost from multiple sources
        source_boost = min(source_count * 0.1, 0.3)
        
        # Boost from confidence
        confidence_boost = confidence_score * 0.2
        
        # Recency boost (if published recently)
        recency_boost = 0
        published_at = article.get("published_at")
        if published_at:
            time_diff = datetime.utcnow() - published_at
            if time_diff < timedelta(hours=1):
                recency_boost = 0.2
            elif time_diff < timedelta(hours=6):
                recency_boost = 0.1
        
        total_score = base_score + credibility_boost + source_boost + confidence_boost + recency_boost
        return min(total_score, 1.0)
    
    async def validate_breaking_news(self, article: Dict[str, Any]) -> bool:
        """Additional validation for breaking news"""
        try:
            # Check for duplicate breaking news
            if await self.is_duplicate_breaking_news(article):
                self.logger.info(f"Duplicate breaking news detected: {article.get('title', '')}")
                return False
            
            # Validate content quality
            if not await self.validate_content_quality(article):
                self.logger.info(f"Content quality validation failed: {article.get('title', '')}")
                return False
            
            # Check for official confirmation for critical news
            if article.get("impact_level") == "critical":
                if not await self.has_official_confirmation(article):
                    self.logger.info(f"Critical news lacks official confirmation: {article.get('title', '')}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Breaking news validation failed: {str(e)}")
            return False
    
    async def is_duplicate_breaking_news(self, article: Dict[str, Any]) -> bool:
        """Check if similar breaking news already exists"""
        try:
            db = SessionLocal()
            
            # Look for similar breaking news from last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            similar_articles = db.query(NewsArticle).filter(
                NewsArticle.is_breaking == True,
                NewsArticle.created_at >= cutoff_time,
                NewsArticle.title.ilike(f"%{article.get('title', '')[:50]}%")
            ).limit(3).all()
            
            db.close()
            
            return len(similar_articles) > 0
            
        except Exception as e:
            self.logger.error(f"Duplicate check failed: {str(e)}")
            return False
    
    async def validate_content_quality(self, article: Dict[str, Any]) -> bool:
        """Validate content quality for breaking news"""
        title = article.get("title", "")
        content = article.get("content", "")
        
        # Check minimum content length
        if len(title) < 10 or len(content) < 50:
            return False
        
        # Check for clickbait indicators
        clickbait_indicators = ["you won't believe", "shocking", "incredible", "amazing"]
        title_lower = title.lower()
        
        clickbait_count = sum(1 for indicator in clickbait_indicators if indicator in title_lower)
        if clickbait_count > 1:
            return False
        
        # Check for factual content
        factual_indicators = ["announced", "released", "launched", "acquired", "funded", "reported"]
        factual_count = sum(1 for indicator in factual_indicators if indicator in content.lower())
        
        return factual_count >= 1 or len(content) > 200
    
    async def has_official_confirmation(self, article: Dict[str, Any]) -> bool:
        """Check for official confirmation in critical news"""
        content = article.get("content", "").lower()
        title = article.get("title", "").lower()
        combined_text = f"{title} {content}"
        
        official_indicators = [
            "official statement", "press release", "confirmed by", "announced by",
            "spokesperson", "executive", "ceo", "cto", "founding team",
            "regulatory filing", "sec filing", "earnings call"
        ]
        
        return any(indicator in combined_text for indicator in official_indicators)
    
    async def publish_breaking_news(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Publish breaking news article"""
        try:
            db = SessionLocal()
            
            # Create breaking news record
            breaking_article = NewsArticle(
                title=article.get("title"),
                content=article.get("content"),
                summary=article.get("summary"),
                short_description=article.get("short_description"),
                category=article.get("category"),
                impact_level=article.get("impact_level"),
                credibility_score=article.get("credibility_score"),
                confidence_score=article.get("confidence_score"),
                source_count=article.get("source_count"),
                headline=article.get("headline"),
                why_it_matters=article.get("why_it_matters"),
                developer_impact=article.get("developer_impact"),
                market_impact=article.get("market_impact"),
                future_prediction=article.get("future_prediction"),
                who_should_care=article.get("who_should_care"),
                url=article.get("url"),
                published_at=article.get("published_at"),
                is_breaking=True,
                is_published=True
            )
            
            db.add(breaking_article)
            db.commit()
            db.refresh(breaking_article)
            
            # Store raw sources if available
            if "additional_sources" in article:
                from models import RawSource
                
                for source in article["additional_sources"]:
                    raw_source = RawSource(
                        article_id=breaking_article.id,
                        source_url=source.get("source_url"),
                        source_name=source.get("source_name"),
                        title=source.get("title"),
                        content=source.get("content", ""),
                        published_at=article.get("published_at")
                    )
                    db.add(raw_source)
                
                db.commit()
            
            db.close()
            
            # Prepare published article data
            published_article = article.copy()
            published_article["id"] = breaking_article.id
            published_article["is_published"] = True
            published_article["published_at"] = breaking_article.created_at
            
            # Log breaking news publication
            self.logger.info(f"Breaking news published: {article.get('title')} (ID: {breaking_article.id})")
            
            return published_article
            
        except Exception as e:
            self.logger.error(f"Breaking news publication failed: {str(e)}")
            return None
    
    async def get_breaking_news_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of recent breaking news"""
        try:
            db = SessionLocal()
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            breaking_news = db.query(NewsArticle).filter(
                NewsArticle.is_breaking == True,
                NewsArticle.created_at >= cutoff_time
            ).order_by(NewsArticle.created_at.desc()).all()
            
            db.close()
            
            # Generate summary
            summary = {
                "total_breaking_news": len(breaking_news),
                "by_category": {},
                "by_impact_level": {},
                "average_credibility": 0,
                "top_stories": []
            }
            
            if breaking_news:
                # Calculate statistics
                total_credibility = sum(article.credibility_score for article in breaking_news)
                summary["average_credibility"] = total_credibility / len(breaking_news)
                
                # Category distribution
                for article in breaking_news:
                    category = article.category or "Unknown"
                    summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
                    
                    impact_level = article.impact_level or "Unknown"
                    summary["by_impact_level"][impact_level] = summary["by_impact_level"].get(impact_level, 0) + 1
                
                # Top stories (by credibility score)
                top_stories = sorted(breaking_news, key=lambda x: x.credibility_score, reverse=True)[:5]
                summary["top_stories"] = [
                    {
                        "id": article.id,
                        "title": article.title,
                        "category": article.category,
                        "impact_level": article.impact_level,
                        "credibility_score": article.credibility_score,
                        "created_at": article.created_at
                    }
                    for article in top_stories
                ]
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Breaking news summary failed: {str(e)}")
            return {"error": str(e)}
