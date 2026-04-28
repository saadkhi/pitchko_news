from typing import Dict, Any, List
import re
from datetime import datetime
import logging
from .base_agent import BaseAgent

class ClassificationAgent(BaseAgent):
    def __init__(self):
        super().__init__("ClassificationAgent")
        
        # Category keywords
        self.category_keywords = {
            "AI": [
                "artificial intelligence", "machine learning", "deep learning", "neural network",
                "chatgpt", "gpt", "openai", "anthropic", "claude", "gemini", "bard",
                "automation", "llm", "large language model", "generative ai", "computer vision",
                "natural language processing", "nlp", "reinforcement learning"
            ],
            "Startups": [
                "startup", "venture capital", "funding round", "series a", "series b", "series c",
                "seed funding", "angel investor", "ipo", "initial public offering", "unicorn",
                "accelerator", "incubator", "pitch", "valuation", "investment", "entrepreneur"
            ],
            "Cybersecurity": [
                "cybersecurity", "data breach", "hack", "malware", "ransomware", "phishing",
                "vulnerability", "security flaw", "encryption", "privacy", "gdpr", "ccpa",
                "firewall", "antivirus", "cyber attack", "zero day", "threat intelligence"
            ],
            "Big Tech": [
                "apple", "google", "alphabet", "microsoft", "amazon", "meta", "facebook",
                "tesla", "netflix", "twitter", "x", "linkedin", "uber", "lyft", "airbnb",
                "spotify", "adobe", "salesforce", "oracle", "ibm", "intel", "nvidia"
            ]
        }
        
        # Impact level keywords
        self.impact_keywords = {
            "critical": [
                "critical", "emergency", "major breach", "shutdown", "outage", "security crisis",
                "billion dollar", "massive layoff", "bankruptcy", "fraud", "scandal", "investigation",
                "regulatory action", "antitrust", "monopoly", "data leak", "cyber attack"
            ],
            "high": [
                "breakthrough", "milestone", "record", "unprecedented", "significant", "major",
                "acquisition", "merger", "partnership", "launch", "release", "funding", "investment",
                "expansion", "growth", "innovation", "disruption"
            ],
            "medium": [
                "update", "improvement", "feature", "enhancement", "partnership", "collaboration",
                "research", "study", "report", "analysis", "trend", "development", "progress"
            ],
            "low": [
                "minor", "small", "update", "patch", "fix", "maintenance", "announcement",
                "statement", "comment", "opinion", "speculation", "rumor"
            ]
        }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify articles by category and impact level"""
        start_time = datetime.now()
        
        try:
            articles = data.get("articles", [])
            if not articles:
                return {"articles": [], "classified_count": 0}
            
            classified_articles = []
            
            for article in articles:
                classified_article = await self.classify_article(article)
                classified_articles.append(classified_article)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "articles": classified_articles,
                "classified_count": len(classified_articles),
                "categories": self.get_category_distribution(classified_articles),
                "impact_levels": self.get_impact_distribution(classified_articles)
            }
            
            self.log_processing(data, result, processing_time)
            return result
            
        except Exception as e:
            self.logger.error(f"Classification failed: {str(e)}")
            return {"error": str(e), "articles": data.get("articles", [])}
    
    async def classify_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a single article"""
        title = article.get("title", "").lower()
        content = article.get("content", "").lower()
        combined_text = f"{title} {content}"
        
        # Classify category
        category = await self.classify_category(combined_text, title, content)
        
        # Classify impact level
        impact_level, confidence = await self.classify_impact(combined_text, title, content)
        
        # Update article with classifications
        classified_article = article.copy()
        classified_article["category"] = category
        classified_article["impact_level"] = impact_level
        classified_article["confidence_score"] = confidence
        
        return classified_article
    
    async def classify_category(self, combined_text: str, title: str, content: str) -> str:
        """Classify article category using keyword matching and LLM"""
        # Keyword-based classification
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences in title (weighted more) and content
                title_count = title.count(keyword)
                content_count = content.count(keyword)
                score += title_count * 3 + content_count
            
            category_scores[category] = score
        
        # Get top category by keyword score
        top_category = max(category_scores, key=category_scores.get)
        
        # Use LLM for verification if keyword score is low
        if category_scores[top_category] < 2:
            llm_category = await self.classify_category_with_llm(title, content)
            if llm_category:
                return llm_category
        
        return top_category
    
    async def classify_category_with_llm(self, title: str, content: str) -> str:
        """Use LLM to classify category when keyword matching is uncertain"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a tech news classification expert. Classify the following article into ONE of these categories:
                    - AI (artificial intelligence, machine learning, etc.)
                    - Startups (funding, ventures, IPOs, etc.)
                    - Cybersecurity (security breaches, privacy, etc.)
                    - Big Tech (major tech companies, products, etc.)
                    
                    Respond with ONLY the category name."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:1000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=50)
            response = response.strip().upper()
            
            # Validate response
            valid_categories = ["AI", "STARTUPS", "CYBERSECURITY", "BIG TECH"]
            for category in valid_categories:
                if category in response:
                    return category
            
            return "Big Tech"  # Default fallback
            
        except Exception as e:
            self.logger.error(f"LLM classification failed: {str(e)}")
            return "Big Tech"
    
    async def classify_impact(self, combined_text: str, title: str, content: str) -> tuple:
        """Classify impact level and confidence"""
        # Keyword-based impact classification
        impact_scores = {}
        
        for impact, keywords in self.impact_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences in title (weighted more) and content
                title_count = title.count(keyword)
                content_count = content.count(keyword)
                score += title_count * 3 + content_count
            
            impact_scores[impact] = score
        
        # Get top impact level
        top_impact = max(impact_scores, key=impact_scores.get)
        
        # Calculate confidence based on score difference
        scores = list(impact_scores.values())
        max_score = max(scores)
        second_max_score = sorted(scores)[-2] if len(scores) > 1 else 0
        
        confidence = min(max_score / (max_score + second_max_score + 1), 1.0)
        
        # Use LLM for high-impact articles to verify
        if top_impact in ["critical", "high"] and confidence < 0.7:
            llm_impact = await self.classify_impact_with_llm(title, content)
            if llm_impact:
                top_impact = llm_impact
                confidence = 0.8  # Higher confidence for LLM classification
        
        return top_impact, confidence
    
    async def classify_impact_with_llm(self, title: str, content: str) -> str:
        """Use LLM to classify impact level for important articles"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a tech news impact analyst. Classify the following article's impact level as:
                    - critical: Emergency situations, major crises, billion-dollar impacts
                    - high: Breakthrough news, major acquisitions, significant launches
                    - medium: Updates, improvements, research findings
                    - low: Minor news, opinions, speculation
                    
                    Consider the potential impact on the tech industry, users, and market.
                    Respond with ONLY the impact level."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:1000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=50)
            response = response.strip().lower()
            
            # Validate response
            valid_impacts = ["critical", "high", "medium", "low"]
            for impact in valid_impacts:
                if impact in response:
                    return impact
            
            return "medium"  # Default fallback
            
        except Exception as e:
            self.logger.error(f"LLM impact classification failed: {str(e)}")
            return "medium"
    
    def get_category_distribution(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of categories"""
        distribution = {}
        for article in articles:
            category = article.get("category", "Unknown")
            distribution[category] = distribution.get(category, 0) + 1
        return distribution
    
    def get_impact_distribution(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of impact levels"""
        distribution = {}
        for article in articles:
            impact = article.get("impact_level", "Unknown")
            distribution[impact] = distribution.get(impact, 0) + 1
        return distribution
