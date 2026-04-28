from typing import Dict, Any, List
from datetime import datetime
import logging
from .base_agent import BaseAgent

class InsightAgent(BaseAgent):
    def __init__(self):
        super().__init__("InsightAgent")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market impact, future predictions, and stakeholder analysis"""
        start_time = datetime.now()
        
        try:
            articles = data.get("articles", [])
            if not articles:
                return {"articles": [], "insights_generated": 0}
            
            insight_articles = []
            
            for article in articles:
                insight_article = await self.generate_insights(article)
                insight_articles.append(insight_article)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "articles": insight_articles,
                "insights_generated": len(insight_articles)
            }
            
            self.log_processing(data, result, processing_time)
            return result
            
        except Exception as e:
            self.logger.error(f"Insight generation failed: {str(e)}")
            return {"error": str(e), "articles": data.get("articles", [])}
    
    async def generate_insights(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive insights for an article"""
        title = article.get("title", "")
        content = article.get("content", "")
        category = article.get("category", "")
        impact_level = article.get("impact_level", "")
        
        # Generate different insight types
        market_impact = await self.generate_market_impact(title, content, category, impact_level)
        future_prediction = await self.generate_future_prediction(title, content, category, impact_level)
        who_should_care = await self.generate_who_should_care(title, content, category, impact_level)
        
        # Additional insights
        investment_implications = await self.generate_investment_implications(title, content, category)
        competitive_landscape = await self.generate_competitive_landscape(title, content, category)
        risk_factors = await self.generate_risk_factors(title, content, category, impact_level)
        
        insight_article = article.copy()
        insight_article["market_impact"] = market_impact
        insight_article["future_prediction"] = future_prediction
        insight_article["who_should_care"] = who_should_care
        insight_article["investment_implications"] = investment_implications
        insight_article["competitive_landscape"] = competitive_landscape
        insight_article["risk_factors"] = risk_factors
        
        return insight_article
    
    async def generate_market_impact(self, title: str, content: str, category: str, impact_level: str) -> str:
        """Generate market impact analysis"""
        try:
            category_context = self.get_category_market_context(category)
            
            messages = [
                {
                    "role": "system",
                    "content": f"""Analyze the market impact of this tech news development.
                    
                    Category: {category}
                    Market Context: {category_context}
                    Impact Level: {impact_level}
                    
                    Focus on:
                    - Stock market implications (if applicable)
                    - Market share changes
                    - Industry valuation effects
                    - Consumer behavior impact
                    - Supply chain effects
                    - Economic implications
                    
                    Provide specific, actionable insights for investors, analysts, and business leaders.
                    2-3 paragraphs, data-driven perspective."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:1000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=500)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Market impact analysis failed: {str(e)}")
            return "This development is likely to have significant market implications across related sectors."
    
    async def generate_future_prediction(self, title: str, content: str, category: str, impact_level: str) -> str:
        """Generate short-term future predictions"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Based on this tech news development, provide short-term predictions (next 3-12 months).
                    
                    Category: {category}
                    Impact Level: {impact_level}
                    
                    Predictions should cover:
                    - Likely next developments
                    - Industry trends this will accelerate
                    - Potential responses from competitors
                    - Regulatory or policy implications
                    - Technology adoption timelines
                    - Market evolution expectations
                    
                    Be specific but acknowledge uncertainty. 2-3 paragraphs."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:1000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=400)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Future prediction failed: {str(e)}")
            return "This development is likely to shape industry trends in the coming months."
    
    async def generate_who_should_care(self, title: str, content: str, category: str, impact_level: str) -> str:
        """Generate stakeholder analysis"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Identify who should care about this tech news and why.
                    
                    Category: {category}
                    Impact Level: {impact_level}
                    
                    Stakeholder groups to consider:
                    - Developers and engineers
                    - Product managers and designers
                    - Business executives and strategists
                    - Investors and financial analysts
                    - Policy makers and regulators
                    - End users and consumers
                    - Competitors and partners
                    
                    For each relevant group, explain specifically why this matters to them.
                    Format as clear bullet points with brief explanations."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:1000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=500)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Stakeholder analysis failed: {str(e)}")
            return "This development affects multiple stakeholder groups across the tech ecosystem."
    
    async def generate_investment_implications(self, title: str, content: str, category: str) -> str:
        """Generate investment-focused insights"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Analyze investment implications of this tech news.
                    
                    Category: {category}
                    
                    Focus on:
                    - Public company stock implications
                    - Private company valuation effects
                    - M&A activity likelihood
                    - Sector investment opportunities
                    - Risk factors for investors
                    - Long-term vs short-term considerations
                    
                    Provide balanced analysis suitable for investors. 2 paragraphs."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:800]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=350)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Investment implications analysis failed: {str(e)}")
            return "Investors should monitor this development for potential portfolio implications."
    
    async def generate_competitive_landscape(self, title: str, content: str, category: str) -> str:
        """Analyze competitive implications"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Analyze how this news affects the competitive landscape.
                    
                    Category: {category}
                    
                    Consider:
                    - Which companies benefit or are threatened
                    - Competitive responses we might see
                    - Market positioning changes
                    - Technology race implications
                    - Partnership opportunities
                    - Market consolidation potential
                    
                    Focus on strategic competitive dynamics. 2 paragraphs."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:800]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=350)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Competitive landscape analysis failed: {str(e)}")
            return "This development will likely reshape competitive dynamics in the sector."
    
    async def generate_risk_factors(self, title: str, content: str, category: str, impact_level: str) -> str:
        """Identify risk factors and challenges"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Identify risk factors and challenges related to this development.
                    
                    Category: {category}
                    Impact Level: {impact_level}
                    
                    Risk categories:
                    - Technology risks (implementation, scalability)
                    - Market risks (adoption, competition)
                    - Regulatory risks (compliance, policy)
                    - Operational risks (execution, integration)
                    - Financial risks (cost, ROI)
                    - Reputational risks (public perception)
                    
                    Provide balanced risk assessment. 2-3 paragraphs."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:800]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=400)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Risk factors analysis failed: {str(e)}")
            return "Stakeholders should consider various risk factors when evaluating this development."
    
    def get_category_market_context(self, category: str) -> str:
        """Get market context for category"""
        contexts = {
            "AI": "Rapidly growing AI market with high valuations, intense competition, and significant VC investment",
            "Startups": "Dynamic startup ecosystem with varying funding conditions, M&A activity, and market exits",
            "Cybersecurity": "Critical infrastructure market with increasing demand, regulatory pressure, and evolving threats",
            "Big Tech": "Mature market with antitrust scrutiny, international expansion, and platform competition"
        }
        return contexts.get(category, "Technology sector with evolving market dynamics")
    
    async def generate_trend_analysis(self, title: str, content: str, category: str) -> Dict[str, Any]:
        """Generate trend analysis and connections"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Analyze how this news fits into broader tech trends.
                    
                    Category: {category}
                    
                    Identify:
                    - Major tech trends this connects to
                    - Historical precedents or patterns
                    - Related developments in other sectors
                    - Trend acceleration or reversal indicators
                    - Cross-industry implications
                    
                    Provide structured analysis with trend connections."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:1000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=500)
            
            return {
                "trend_analysis": response.strip(),
                "connected_trends": await self.extract_connected_trends(title, content, category),
                "trend_impact": await self.assess_trend_impact(title, content, category)
            }
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            return {
                "trend_analysis": "This development connects to broader industry trends.",
                "connected_trends": [],
                "trend_impact": "moderate"
            }
    
    async def extract_connected_trends(self, title: str, content: str, category: str) -> List[str]:
        """Extract connected trends"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Extract 5-7 major tech trends that this news connects to.
                    
                    Category: {category}
                    
                    Examples of trends: AI democratization, remote work transformation, 
                    cloud migration, cybersecurity evolution, fintech innovation, 
                    sustainability tech, edge computing, 5G adoption, etc.
                    
                    Return as a simple list of trend names."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:800]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=200)
            
            # Parse list
            trends = []
            for line in response.strip().split('\n'):
                trend = line.strip().lstrip('-•* ').strip()
                if trend and len(trend) < 50:
                    trends.append(trend)
            
            return trends[:7]
            
        except Exception as e:
            self.logger.error(f"Connected trends extraction failed: {str(e)}")
            return []
    
    async def assess_trend_impact(self, title: str, content: str, category: str) -> str:
        """Assess impact on trends"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Assess how this news impacts broader tech trends.
                    
                    Category: {category}
                    
                    Rate the impact as one of: trend_accelerator, trend_initiator, trend_reversal, trend_confirmation, trend_divergence
                    
                    Briefly explain your choice in one sentence."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:600]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=100)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Trend impact assessment failed: {str(e)}")
            return "trend_accelerator"
