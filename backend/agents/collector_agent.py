from typing import Dict, Any, List
import aiohttp
import feedparser
import asyncio
from datetime import datetime, timedelta
import logging
from .base_agent import BaseAgent
import os
from dotenv import load_dotenv

load_dotenv()

class CollectorAgent(BaseAgent):
    def __init__(self):
        super().__init__("CollectorAgent")
        
        # News sources configuration
        self.news_sources = {
            "techcrunch": {
                "rss": "https://techcrunch.com/feed/",
                "trust_score": 0.8,
                "categories": ["Startups", "Big Tech", "AI"]
            },
            "venturebeat": {
                "rss": "https://venturebeat.com/feed/",
                "trust_score": 0.7,
                "categories": ["AI", "Big Tech", "Cybersecurity"]
            },
            "ars-technica": {
                "rss": "https://feeds.arstechnica.com/arstechnica/index",
                "trust_score": 0.8,
                "categories": ["Cybersecurity", "Big Tech"]
            },
            "the-verge": {
                "rss": "https://www.theverge.com/rss/index.xml",
                "trust_score": 0.7,
                "categories": ["Big Tech", "AI"]
            }
        }
        
        self.api_sources = {
            "newsapi": {
                "url": "https://newsapi.org/v2/everything",
                "key": os.getenv("NEWS_API_KEY"),
                "trust_score": 0.6
            },
            "gnews": {
                "url": "https://gnews.io/api/v4/search",
                "key": os.getenv("GNEWS_API_KEY"),
                "trust_score": 0.6
            }
        }
        
        # Tech keywords for filtering
        self.tech_keywords = [
            "artificial intelligence", "AI", "machine learning", "deep learning",
            "startup", "venture capital", "funding", "IPO", "acquisition",
            "cybersecurity", "data breach", "hack", "privacy",
            "apple", "google", "microsoft", "amazon", "meta", "tesla",
            "cryptocurrency", "blockchain", "NFT", "web3",
            "cloud computing", "SaaS", "API", "open source"
        ]
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect news from various sources"""
        start_time = datetime.now()
        
        try:
            # Collect from RSS feeds
            rss_articles = await self.collect_from_rss()
            
            # Collect from APIs
            api_articles = await self.collect_from_apis()
            
            # Combine and normalize
            all_articles = rss_articles + api_articles
            
            # Filter for tech-related content
            tech_articles = self.filter_tech_content(all_articles)
            
            # Remove duplicates (basic URL-based)
            unique_articles = self.remove_duplicates(tech_articles)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "articles": unique_articles,
                "total_collected": len(all_articles),
                "tech_filtered": len(tech_articles),
                "unique_count": len(unique_articles),
                "sources_used": list(self.news_sources.keys()) + list(self.api_sources.keys())
            }
            
            self.log_processing(data, result, processing_time)
            return result
            
        except Exception as e:
            self.logger.error(f"Collection failed: {str(e)}")
            return {"error": str(e), "articles": []}
    
    async def collect_from_rss(self) -> List[Dict[str, Any]]:
        """Collect articles from RSS feeds"""
        articles = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source_name, source_config in self.news_sources.items():
                task = self.fetch_rss_feed(session, source_name, source_config)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    articles.extend(result)
        
        return articles
    
    async def fetch_rss_feed(self, session: aiohttp.ClientSession, source_name: str, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed"""
        try:
            async with session.get(source_config["rss"], timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    articles = []
                    for entry in feed.entries[:20]:  # Limit to 20 most recent
                        article = {
                            "title": entry.title,
                            "content": entry.description if hasattr(entry, 'description') else entry.summary,
                            "url": entry.link,
                            "source_name": source_name,
                            "source_url": source_config["rss"],
                            "trust_score": source_config["trust_score"],
                            "categories": source_config["categories"],
                            "published_at": self.parse_date(entry.published if hasattr(entry, 'published') else None),
                            "collected_at": datetime.utcnow()
                        }
                        articles.append(article)
                    
                    return articles
        except Exception as e:
            self.logger.error(f"Failed to fetch RSS from {source_name}: {str(e)}")
            return []
    
    async def collect_from_apis(self) -> List[Dict[str, Any]]:
        """Collect articles from news APIs"""
        articles = []
        
        # NewsAPI
        if self.api_sources["newsapi"]["key"]:
            newsapi_articles = await self.fetch_newsapi()
            articles.extend(newsapi_articles)
        
        # GNews
        if self.api_sources["gnews"]["key"]:
            gnews_articles = await self.fetch_gnews()
            articles.extend(gnews_articles)
        
        return articles
    
    async def fetch_newsapi(self) -> List[Dict[str, Any]]:
        """Fetch from NewsAPI"""
        try:
            params = {
                "q": "technology OR AI OR startup OR cybersecurity",
                "domains": "techcrunch.com,venturebeat.com,arstechnica.com,theverge.com,wired.com",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 50,
                "apiKey": self.api_sources["newsapi"]["key"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_sources["newsapi"]["url"], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        
                        for article in data.get("articles", []):
                            normalized = {
                                "title": article["title"],
                                "content": article["description"],
                                "url": article["url"],
                                "source_name": article["source"]["name"],
                                "source_url": article["url"],
                                "trust_score": self.api_sources["newsapi"]["trust_score"],
                                "categories": ["AI", "Startups", "Big Tech", "Cybersecurity"],
                                "published_at": self.parse_date(article["publishedAt"]),
                                "collected_at": datetime.utcnow()
                            }
                            articles.append(normalized)
                        
                        return articles
        except Exception as e:
            self.logger.error(f"NewsAPI fetch failed: {str(e)}")
            return []
    
    async def fetch_gnews(self) -> List[Dict[str, Any]]:
        """Fetch from GNews"""
        try:
            params = {
                "q": "technology AI startup cybersecurity",
                "lang": "en",
                "country": "us",
                "max": 50,
                "apikey": self.api_sources["gnews"]["key"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_sources["gnews"]["url"], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        
                        for article in data.get("articles", []):
                            normalized = {
                                "title": article["title"],
                                "content": article["description"],
                                "url": article["url"],
                                "source_name": article["source"]["name"],
                                "source_url": article["url"],
                                "trust_score": self.api_sources["gnews"]["trust_score"],
                                "categories": ["AI", "Startups", "Big Tech", "Cybersecurity"],
                                "published_at": self.parse_date(article["publishedAt"]),
                                "collected_at": datetime.utcnow()
                            }
                            articles.append(normalized)
                        
                        return articles
        except Exception as e:
            self.logger.error(f"GNews fetch failed: {str(e)}")
            return []
    
    def filter_tech_content(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter articles for tech-related content"""
        tech_articles = []
        
        for article in articles:
            title_lower = article.get("title", "").lower()
            content_lower = article.get("content", "").lower()
            
            # Check if any tech keyword is present
            is_tech = any(keyword in title_lower or keyword in content_lower 
                         for keyword in self.tech_keywords)
            
            if is_tech:
                tech_articles.append(article)
        
        return tech_articles
    
    def remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on URL similarity"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse various date formats"""
        if not date_str:
            return datetime.utcnow()
        
        try:
            # Try common formats
            formats = [
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S",
                "%a, %d %b %Y %H:%M:%S %Z"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # Fallback to current time
            return datetime.utcnow()
        except:
            return datetime.utcnow()
