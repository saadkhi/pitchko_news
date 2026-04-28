from typing import Dict, Any, List
from datetime import datetime
import logging
from .base_agent import BaseAgent

class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("SummarizerAgent")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple sources into structured summary"""
        start_time = datetime.now()
        
        try:
            articles = data.get("articles", [])
            if not articles:
                return {"articles": [], "summarized_count": 0}
            
            summarized_articles = []
            
            for article in articles:
                summarized_article = await self.summarize_article(article)
                summarized_articles.append(summarized_article)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "articles": summarized_articles,
                "summarized_count": len(summarized_articles)
            }
            
            self.log_processing(data, result, processing_time)
            return result
            
        except Exception as e:
            self.logger.error(f"Summarization failed: {str(e)}")
            return {"error": str(e), "articles": data.get("articles", [])}
    
    async def summarize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive summary for a single article"""
        title = article.get("title", "")
        content = article.get("content", "")
        additional_sources = article.get("additional_sources", [])
        
        # Generate different types of summaries
        short_summary = await self.generate_short_summary(title, content)
        detailed_summary = await self.generate_detailed_summary(title, content, additional_sources)
        bullet_points = await self.generate_bullet_points(title, content)
        
        # Create comprehensive summary
        comprehensive_summary = self.create_comprehensive_summary(short_summary, detailed_summary, bullet_points)
        
        summarized_article = article.copy()
        summarized_article["summary"] = comprehensive_summary
        summarized_article["short_description"] = short_summary
        summarized_article["bullet_points"] = bullet_points
        
        return summarized_article
    
    async def generate_short_summary(self, title: str, content: str) -> str:
        """Generate a short, concise summary (1-2 sentences)"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a tech news summarizer. Create a concise, 1-2 sentence summary of the following article.
                    Focus on the most important information and key takeaways.
                    Make it clear, accurate, and engaging."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:2000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=150)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Short summary generation failed: {str(e)}")
            # Fallback: first 200 characters of content
            return content[:200].rstrip() + "..." if len(content) > 200 else content
    
    async def generate_detailed_summary(self, title: str, content: str, additional_sources: List[Dict[str, Any]]) -> str:
        """Generate a detailed summary incorporating multiple sources"""
        try:
            # Prepare additional sources context
            sources_context = ""
            if additional_sources:
                sources_context = "\n\nAdditional sources:\n"
                for i, source in enumerate(additional_sources[:3], 1):
                    sources_context += f"{i}. {source.get('title', '')} ({source.get('source_name', '')})\n"
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a tech news analyst. Create a comprehensive summary of the following article.
                    Include:
                    - Main story and key facts
                    - Context and background
                    - Implications and significance
                    - Information from additional sources if available
                    
                    Make it informative, balanced, and well-structured (3-4 paragraphs)."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content}{sources_context}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=500)
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Detailed summary generation failed: {str(e)}")
            # Fallback: truncated content
            return content[:1000].rstrip() + "..." if len(content) > 1000 else content
    
    async def generate_bullet_points(self, title: str, content: str) -> List[str]:
        """Generate key bullet points from the article"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """Extract the 5-7 most important points from the following tech article as bullet points.
                    Each bullet point should be:
                    - Concise (1 line)
                    - Factual and important
                    - Easy to understand
                    
                    Format as a list with bullet points (•)."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:2000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=300)
            
            # Parse bullet points
            bullet_points = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    bullet_points.append(line.lstrip('•-* ').strip())
                elif line and not line.startswith('•') and not line.startswith('-') and not line.startswith('*'):
                    # Add line as bullet point if it looks like a key point
                    if len(line) < 200 and any(char.isdigit() for char in line):
                        bullet_points.append(line)
            
            return bullet_points[:7]  # Limit to 7 bullet points
            
        except Exception as e:
            self.logger.error(f"Bullet points generation failed: {str(e)}")
            return ["Key information extraction failed"]
    
    def create_comprehensive_summary(self, short_summary: str, detailed_summary: str, bullet_points: List[str]) -> str:
        """Combine different summary types into a comprehensive summary"""
        comprehensive = detailed_summary
        
        # Add bullet points if available
        if bullet_points:
            comprehensive += "\n\nKey Points:\n"
            for point in bullet_points:
                comprehensive += f"• {point}\n"
        
        return comprehensive.strip()
    
    async def merge_multiple_sources(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple related articles into one comprehensive summary"""
        if not articles:
            return {}
        
        if len(articles) == 1:
            return await self.summarize_article(articles[0])
        
        try:
            # Prepare combined content
            main_article = articles[0]
            additional_articles = articles[1:]
            
            combined_content = f"Main Article: {main_article.get('title', '')}\n{main_article.get('content', '')}\n\n"
            
            for i, article in enumerate(additional_articles, 1):
                combined_content += f"Additional Source {i}: {article.get('title', '')}\n{article.get('content', '')}\n\n"
            
            # Generate merged summary
            messages = [
                {
                    "role": "system",
                    "content": """You are merging multiple related news articles about the same story.
                    Create a comprehensive summary that:
                    - Combines information from all sources
                    - Highlights consistent facts across sources
                    - Notes any differences or additional perspectives
                    - Provides the most complete picture of the story
                    
                    Structure as 3-4 paragraphs with key insights."""
                },
                {
                    "role": "user",
                    "content": combined_content[:3000]  # Limit content length
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=600)
            
            # Create merged article
            merged_article = main_article.copy()
            merged_article["summary"] = response.strip()
            merged_article["short_description"] = await self.generate_short_summary(
                main_article.get("title", ""), 
                response
            )
            merged_article["source_count"] = len(articles)
            merged_article["merged_sources"] = [
                {
                    "title": article.get("title", ""),
                    "source_name": article.get("source_name", ""),
                    "url": article.get("url", "")
                }
                for article in articles
            ]
            
            return merged_article
            
        except Exception as e:
            self.logger.error(f"Multiple sources merge failed: {str(e)}")
            return main_article
    
    async def extract_key_entities(self, title: str, content: str) -> Dict[str, List[str]]:
        """Extract key entities (companies, people, technologies) from article"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """Extract key entities from the following tech article and categorize them:
                    - Companies: Tech companies, startups, organizations
                    - People: Executives, founders, researchers
                    - Technologies: AI models, platforms, tools, concepts
                    - Locations: Cities, countries, regions mentioned
                    
                    Format as JSON with these categories as keys and lists as values."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\n\nContent: {content[:2000]}"
                }
            ]
            
            response = await self.call_llm(messages, max_tokens=300)
            
            # Parse response (simple parsing, could be improved with proper JSON parsing)
            entities = {
                "companies": [],
                "people": [],
                "technologies": [],
                "locations": []
            }
            
            # Basic parsing - this could be enhanced with proper JSON parsing
            lines = response.strip().split('\n')
            current_category = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Companies:'):
                    current_category = "companies"
                elif line.startswith('People:'):
                    current_category = "people"
                elif line.startswith('Technologies:'):
                    current_category = "technologies"
                elif line.startswith('Locations:'):
                    current_category = "locations"
                elif line.startswith('-') and current_category:
                    entity = line.lstrip('- ').strip()
                    if entity and current_category in entities:
                        entities[current_category].append(entity)
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {str(e)}")
            return {"companies": [], "people": [], "technologies": [], "locations": []}
