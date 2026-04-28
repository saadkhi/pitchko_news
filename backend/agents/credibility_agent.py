from typing import Dict, Any, List, Optional
import re
from datetime import datetime, timedelta
import logging
from .base_agent import BaseAgent

class CredibilityAgent(BaseAgent):
    def __init__(self):
        super().__init__("CredibilityAgent")
        
        # Trusted sources with their weights
        self.trusted_sources = {
            "techcrunch": 0.9,
            "venturebeat": 0.8,
            "ars-technica": 0.9,
            "the-verge": 0.8,
            "wired": 0.85,
            "reuters": 0.95,
            "bloomberg": 0.9,
            "financial-times": 0.9,
            "wall-street-journal": 0.9,
            "the-information": 0.85,
            "axios": 0.8,
            "protocol": 0.8,
            "mit-technology-review": 0.9,
            "stanford-ai": 0.95,
            "arxiv": 0.9
        }
        
        # Credibility indicators
        self.positive_indicators = [
            "official statement", "press release", "confirmed by", "announced by",
            "according to", "reported by", "spokesperson", "executive", "ceo", "cto",
            "founding team", "board member", "regulatory filing", "sec filing",
            "earnings call", "quarterly report", "annual report", "white paper",
            "research paper", "peer-reviewed", "study", "analysis", "data shows"
        ]
        
        self.negative_indicators = [
            "rumor", "speculation", "unconfirmed", "allegedly", "reportedly",
            "sources say", "anonymous source", "leaked", "rumored", "gossip",
            "clickbait", "conspiracy", "fake news", "misinformation"
        ]
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate credibility of high/critical impact articles"""
        start_time = datetime.now()
        
        try:
            articles = data.get("articles", [])
            if not articles:
                return {"articles": [], "evaluated_count": 0}
            
            evaluated_articles = []
            
            for article in articles:
                # Only evaluate high/critical impact articles
                impact_level = article.get("impact_level", "").lower()
                if impact_level in ["high", "critical"]:
                    evaluated_article = await self.evaluate_credibility(article)
                    evaluated_articles.append(evaluated_article)
                else:
                    # Auto-publish low/medium impact with default credibility
                    article["credibility_score"] = 0.7
                    article["should_publish"] = True
                    evaluated_articles.append(article)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "articles": evaluated_articles,
                "evaluated_count": len(evaluated_articles),
                "high_credibility_count": len([a for a in evaluated_articles if a.get("credibility_score", 0) > 0.75]),
                "publish_count": len([a for a in evaluated_articles if a.get("should_publish", False)])
            }
            
            self.log_processing(data, result, processing_time)
            return result
            
        except Exception as e:
            self.logger.error(f"Credibility evaluation failed: {str(e)}")
            return {"error": str(e), "articles": data.get("articles", [])}
    
    async def evaluate_credibility(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate credibility of a single article"""
        title = article.get("title", "")
        content = article.get("content", "")
        source_name = article.get("source_name", "").lower()
        source_count = article.get("source_count", 1)
        
        # Calculate credibility components
        source_score = self.calculate_source_credibility(source_name, source_count)
        content_score = await self.calculate_content_credibility(title, content)
        consistency_score = await self.calculate_consistency_score(article)
        official_score = await self.check_official_confirmation(title, content)
        
        # Calculate final credibility score
        final_score = (
            source_score * 0.3 +
            content_score * 0.25 +
            consistency_score * 0.25 +
            official_score * 0.2
        )
        
        # Apply guardrails logic
        should_publish, reason = self.apply_guardrails(final_score, article)
        
        evaluated_article = article.copy()
        evaluated_article["credibility_score"] = round(final_score, 2)
        evaluated_article["source_credibility"] = round(source_score, 2)
        evaluated_article["content_credibility"] = round(content_score, 2)
        evaluated_article["consistency_score"] = round(consistency_score, 2)
        evaluated_article["official_confirmation"] = round(official_score, 2)
        evaluated_article["should_publish"] = should_publish
        evaluated_article["publication_reason"] = reason
        
        return evaluated_article
    
    def calculate_source_credibility(self, source_name: str, source_count: int) -> float:
        """Calculate credibility based on source trustworthiness and count"""
        # Base score from trusted sources list
        base_score = 0.5  # Default for unknown sources
        
        for trusted_source, weight in self.trusted_sources.items():
            if trusted_source in source_name:
                base_score = weight
                break
        
        # Boost score for multiple sources
        if source_count >= 2:
            base_score = min(base_score + 0.1, 1.0)
        if source_count >= 3:
            base_score = min(base_score + 0.1, 1.0)
        
        return base_score
    
    async def calculate_content_credibility(self, title: str, content: str) -> float:
        """Calculate credibility based on content indicators"""
        title_lower = title.lower()
        content_lower = content.lower()
        combined_text = f"{title_lower} {content_lower}"
        
        positive_count = sum(1 for indicator in self.positive_indicators if indicator in combined_text)
        negative_count = sum(1 for indicator in self.negative_indicators if indicator in combined_text)
        
        # Base score
        score = 0.5
        
        # Add points for positive indicators
        score += positive_count * 0.05
        
        # Subtract points for negative indicators
        score -= negative_count * 0.1
        
        # Check for specific credibility factors
        if any(word in combined_text for word in ["official", "statement", "announcement"]):
            score += 0.1
        
        if any(word in combined_text for word in ["data", "research", "study", "analysis"]):
            score += 0.05
        
        # Check length (longer articles tend to be more credible)
        if len(content) > 500:
            score += 0.05
        if len(content) > 1000:
            score += 0.05
        
        return max(0.0, min(score, 1.0))
    
    async def calculate_consistency_score(self, article: Dict[str, Any]) -> float:
        """Calculate consistency score based on multiple sources"""
        additional_sources = article.get("additional_sources", [])
        source_count = article.get("source_count", 1)
        
        if source_count == 1:
            return 0.3  # Low consistency for single source
        
        # Base score for multiple sources
        base_score = 0.7
        
        # Boost for more sources
        if source_count >= 3:
            base_score = 0.8
        if source_count >= 5:
            base_score = 0.9
        
        # Check if additional sources have consistent information
        if additional_sources:
            consistent_sources = 0
            for source in additional_sources:
                # Simple consistency check based on title similarity
                source_title = source.get("title", "").lower()
                main_title = article.get("title", "").lower()
                
                # Check for key terms overlap
                main_words = set(re.findall(r'\b\w+\b', main_title))
                source_words = set(re.findall(r'\b\w+\b', source_title))
                
                if main_words and source_words:
                    overlap = len(main_words.intersection(source_words))
                    similarity = overlap / len(main_words.union(source_words))
                    if similarity > 0.3:  # 30% word overlap
                        consistent_sources += 1
            
            if additional_sources:
                consistency_ratio = consistent_sources / len(additional_sources)
                base_score = base_score * (0.5 + 0.5 * consistency_ratio)
        
        return min(base_score, 1.0)
    
    async def check_official_confirmation(self, title: str, content: str) -> float:
        """Check for official confirmation signals"""
        title_lower = title.lower()
        content_lower = content.lower()
        combined_text = f"{title_lower} {content_lower}"
        
        official_signals = [
            "official statement", "press release", "confirmed by", "announced by",
            "spokesperson said", "executive said", "ceo said", "cto said",
            "founding team", "board member", "regulatory filing", "sec filing",
            "form 8-k", "10-q", "10-k", "earnings call", "quarterly results"
        ]
        
        signal_count = sum(1 for signal in official_signals if signal in combined_text)
        
        # Base score
        score = 0.3
        
        # Add points for each official signal
        score += signal_count * 0.15
        
        # Check for specific high-value signals
        if any(signal in combined_text for signal in ["sec filing", "regulatory filing", "earnings call"]):
            score += 0.2
        
        if any(signal in combined_text for signal in ["ceo", "cto", "executive", "spokesperson"]):
            score += 0.1
        
        return min(score, 1.0)
    
    def apply_guardrails(self, credibility_score: float, article: Dict[str, Any]) -> tuple:
        """Apply guardrails logic to determine publication"""
        impact_level = article.get("impact_level", "").lower()
        source_count = article.get("source_count", 1)
        
        # Guardrails logic
        if impact_level in ["low", "medium"]:
            # Auto-publish low/medium impact
            return True, "Auto-published: low/medium impact"
        
        elif impact_level in ["high", "critical"]:
            # Check credibility for high/critical impact
            if credibility_score >= 0.75:
                # Check minimum source requirements
                if source_count >= 2:
                    return True, f"Published: high credibility ({credibility_score:.2f}) with {source_count} sources"
                else:
                    return False, f"Rejected: high impact but only 1 source (credibility: {credibility_score:.2f})"
            elif credibility_score >= 0.6:
                return False, f"Low confidence: credibility {credibility_score:.2f} below threshold"
            else:
                return False, f"Rejected: low credibility {credibility_score:.2f}"
        
        else:
            return False, f"Unknown impact level: {impact_level}"
    
    async def get_credibility_report(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed credibility report for an article"""
        evaluation = await self.evaluate_credibility(article)
        
        return {
            "article_title": article.get("title", ""),
            "credibility_score": evaluation.get("credibility_score", 0),
            "should_publish": evaluation.get("should_publish", False),
            "publication_reason": evaluation.get("publication_reason", ""),
            "source_credibility": evaluation.get("source_credibility", 0),
            "content_credibility": evaluation.get("content_credibility", 0),
            "consistency_score": evaluation.get("consistency_score", 0),
            "official_confirmation": evaluation.get("official_confirmation", 0),
            "source_count": article.get("source_count", 1),
            "impact_level": article.get("impact_level", "")
        }
