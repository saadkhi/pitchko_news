from typing import Dict, Any, List
from datetime import datetime
import logging
from .base_agent import BaseAgent

class WriterAgent(BaseAgent):
    def __init__(self):
        super().__init__("WriterAgent")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate headline, short description, full article, and impact analysis"""
        start_time = datetime.now()
        
        try:
            articles = data.get("articles", [])
            if not articles:
                return {"articles": [], "written_count": 0}
            
            written_articles = []
            
            for article in articles:
                written_article = await self.write_article(article)
                written_articles.append(written_article)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "articles": written_articles,
                "written_count": len(written_articles)
            }
            
            self.log_processing(data, result, processing_time)
            return result
            
        except Exception as e:
            self.logger.error(f"Writing failed: {str(e)}")
            return {"error": str(e), "articles": data.get("articles", [])}
    
    async def write_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete written content for an article"""
        title = article.get("title", "")
        content = article.get("content", "")
        category = article.get("category", "")
        impact_level = article.get("impact_level", "")
        
        # Generate different content types
        headline = await self.generate_headline(title, content, impact_level)
        short_description = await self.generate_short_description(title, content, impact_level)
        full_article = await self.generate_full_article(title, content, category, impact_level)
        why_it_matters = await self.generate_why_it_matters(title, content, category, impact_level)
        developer_impact = await self.generate_developer_impact(title, content, category, impact_level)
        
        written_article = article.copy()
        written_article["headline"] = headline
        written_article["short_description"] = short_description
        written_article["full_article"] = full_article
        written_article["why_it_matters"] = why_it_matters
        written_article["developer_impact"] = developer_impact
        
        return written_article
    
    async def generate_headline(self, title: str, content: str, impact_level: str) -> str:
        """Generate an engaging, accurate headline"""
        try:
            impact_context = self.get_impact_context(impact_level)
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a tech news headline writer. Create an engaging, accurate headline for the following article.
                    
                    Impact Level: {impact_level}
                    Context: {impact_context}
                    
                    Guidelines:
                    - Keep it under 100 characters
                    - Make it punchy and attention-grabbing
                    - Ensure accuracy and avoid clickbait
                    - Include key companies or technologies if relevant
                    - Match the tone to the impact level"""
                },
                {
                    "role": "user",
                    "content": f"Original Title: {title}\n\nContent: {content[:500]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=100)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Headline generation failed: {str(e)}")
            return title  # Fallback to original title
    
    async def generate_short_description(self, title: str, content: str, impact_level: str) -> str:
        """Generate a short description for breaking news alerts"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Create a short, breaking news description (under 200 characters) for this article.
                    Impact Level: {impact_level}
                    
                    This should be suitable for:
                    - Breaking news tickers
                    - Social media posts
                    - Push notifications
                    
                    Make it urgent, informative, and concise."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:300]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=150)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Short description generation failed: {str(e)}")
            return content[:150].rstrip() + "..." if len(content) > 150 else content
    
    async def generate_full_article(self, title: str, content: str, category: str, impact_level: str) -> str:
        """Generate a well-structured full article"""
        try:
            category_context = self.get_category_context(category)
            impact_context = self.get_impact_context(impact_level)
            
            messages = [
                {
                    "role": "system",
                    "content": f"""Write a comprehensive, well-structured tech news article based on the provided information.
                    
                    Category: {category}
                    Context: {category_context}
                    Impact Level: {impact_level}
                    Impact Context: {impact_context}
                    
                    Structure:
                    1. Engaging lead paragraph (what happened)
                    2. Key details and context
                    3. Quotes or official statements (if any)
                    4. Background and previous developments
                    5. Immediate implications
                    6. Looking forward section
                    
                    Style:
                    - Professional but accessible
                    - 400-600 words
                    - Clear, factual, and informative
                    - Include relevant technical details
                    - Maintain journalistic integrity"""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nOriginal Content: {content}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=800)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Full article generation failed: {str(e)}")
            return content  # Fallback to original content
    
    async def generate_why_it_matters(self, title: str, content: str, category: str, impact_level: str) -> str:
        """Generate 'Why it matters' section"""
        try:
            category_context = self.get_category_context(category)
            
            messages = [
                {
                    "role": "system",
                    "content": f"""Explain why this news matters in the broader context.
                    
                    Category: {category}
                    Context: {category_context}
                    Impact Level: {impact_level}
                    
                    Focus on:
                    - Industry-wide implications
                    - Consumer impact
                    - Market effects
                    - Long-term significance
                    - How it fits into larger trends
                    
                    Write 2-3 paragraphs that help readers understand the bigger picture."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:1000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=400)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"'Why it matters' generation failed: {str(e)}")
            return "This development has significant implications for the tech industry and related stakeholders."
    
    async def generate_developer_impact(self, title: str, content: str, category: str, impact_level: str) -> str:
        """Generate developer-specific impact analysis"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Analyze the impact of this news specifically for developers and technical professionals.
                    
                    Category: {category}
                    Impact Level: {impact_level}
                    
                    Address:
                    - How it affects developers' daily work
                    - New tools, APIs, or technologies to consider
                    - Skills that might become more/less valuable
                    - Changes in development practices
                    - Opportunities or challenges for developers
                    - Migration or adaptation requirements
                    
                    Be specific and practical. 2-3 paragraphs."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:1000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=400)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Developer impact generation failed: {str(e)}")
            return "This development may require developers to adapt their skills and workflows accordingly."
    
    def get_impact_context(self, impact_level: str) -> str:
        """Get context description for impact level"""
        contexts = {
            "critical": "Emergency situation with immediate, widespread consequences affecting the entire industry",
            "high": "Major development with significant implications for companies, users, and markets",
            "medium": "Important update or development with moderate impact",
            "low": "Minor news with limited immediate impact"
        }
        return contexts.get(impact_level, "Standard tech news development")
    
    def get_category_context(self, category: str) -> str:
        """Get context description for category"""
        contexts = {
            "AI": "Artificial intelligence, machine learning, and automation technologies",
            "Startups": "Early-stage companies, funding, venture capital, and entrepreneurship",
            "Cybersecurity": "Security threats, privacy, data protection, and digital defense",
            "Big Tech": "Major technology companies and their products, services, and business decisions"
        }
        return contexts.get(category, "Technology industry development")
    
    async def generate_seo_metadata(self, title: str, content: str, category: str) -> Dict[str, str]:
        """Generate SEO-optimized metadata"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """Generate SEO-optimized metadata for this tech article.
                    Return in this format:
                    Title: [SEO title under 60 characters]
                    Description: [Meta description under 160 characters]
                    Keywords: [5-7 relevant keywords separated by commas]"""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:500]}\n\nCategory: {category}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=200)
            
            # Parse response
            metadata = {
                "seo_title": title[:60],
                "meta_description": "",
                "keywords": ""
            }
            
            lines = response.strip().split('\n')
            for line in lines:
                if line.startswith('Title:'):
                    metadata["seo_title"] = line.replace('Title:', '').strip()
                elif line.startswith('Description:'):
                    metadata["meta_description"] = line.replace('Description:', '').strip()
                elif line.startswith('Keywords:'):
                    metadata["keywords"] = line.replace('Keywords:', '').strip()
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"SEO metadata generation failed: {str(e)}")
            return {
                "seo_title": title[:60],
                "meta_description": content[:150],
                "keywords": category
            }
    
    async def generate_social_media_posts(self, title: str, content: str, impact_level: str) -> Dict[str, str]:
        """Generate social media posts for different platforms"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""Generate social media posts for this tech news article.
                    Impact Level: {impact_level}
                    
                    Create posts for:
                    1. Twitter/X (280 chars max, hashtags included)
                    2. LinkedIn (professional tone, 300 chars max)
                    3. Facebook (engaging, 200 chars max)
                    
                    Format each platform clearly."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:300]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=400)
            
            # Parse response
            posts = {
                "twitter": "",
                "linkedin": "",
                "facebook": ""
            }
            
            current_platform = None
            for line in response.strip().split('\n'):
                line = line.strip()
                if line.startswith('Twitter') or line.startswith('X:'):
                    current_platform = "twitter"
                elif line.startswith('LinkedIn'):
                    current_platform = "linkedin"
                elif line.startswith('Facebook'):
                    current_platform = "facebook"
                elif line and current_platform:
                    posts[current_platform] += line + " "
            
            # Clean up posts
            for platform in posts:
                posts[platform] = posts[platform].strip()
            
            return posts
            
        except Exception as e:
            self.logger.error(f"Social media posts generation failed: {str(e)}")
            return {
                "twitter": f"{title[:200]} #technews",
                "linkedin": f"{title}: {content[:200]}",
                "facebook": f"{title}: {content[:150]}"
            }
