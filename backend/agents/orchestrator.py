from typing import Dict, Any, List
import asyncio
import logging
from datetime import datetime
from .collector_agent import CollectorAgent
from .deduplication_agent import DeduplicationAgent
from .classification_agent import ClassificationAgent
from .credibility_agent import CredibilityAgent
from .summarizer_agent import SummarizerAgent
from .writer_agent import WriterAgent
from .insight_agent import InsightAgent
from .breaking_news_agent import BreakingNewsAgent
from .publisher_agent import PublisherAgent

class AgentOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger("orchestrator")
        
        # Initialize all agents
        self.collector = CollectorAgent()
        self.deduplicator = DeduplicationAgent()
        self.classifier = ClassificationAgent()
        self.credibility = CredibilityAgent()
        self.summarizer = SummarizerAgent()
        self.writer = WriterAgent()
        self.insight = InsightAgent()
        self.breaking_news = BreakingNewsAgent()
        self.publisher = PublisherAgent()
        
        # Pipeline configuration
        self.pipeline_stages = [
            ("collector", self.collector),
            ("deduplicator", self.deduplicator),
            ("classifier", self.classifier),
            ("credibility", self.credibility),
            ("summarizer", self.summarizer),
            ("writer", self.writer),
            ("insight", self.insight),
            ("breaking_news", self.breaking_news),
            ("publisher", self.publisher)
        ]
    
    async def run_full_pipeline(self, trigger_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the complete agent pipeline"""
        start_time = datetime.now()
        pipeline_data = trigger_data or {}
        
        try:
            self.logger.info("Starting full agent pipeline")
            
            # Run each stage sequentially
            for stage_name, agent in self.pipeline_stages:
                stage_start = datetime.now()
                
                try:
                    self.logger.info(f"Running stage: {stage_name}")
                    
                    # Process data through agent
                    result = await agent.process(pipeline_data)
                    
                    if "error" in result:
                        self.logger.error(f"Stage {stage_name} failed: {result['error']}")
                        # Continue pipeline with existing data
                        continue
                    
                    # Update pipeline data with result
                    pipeline_data.update(result)
                    
                    stage_time = (datetime.now() - stage_start).total_seconds()
                    self.logger.info(f"Stage {stage_name} completed in {stage_time:.2f}s")
                    
                except Exception as e:
                    self.logger.error(f"Stage {stage_name} exception: {str(e)}")
                    continue
            
            # Calculate total processing time
            total_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare final result
            final_result = {
                "status": "completed",
                "total_processing_time": total_time,
                "articles_processed": len(pipeline_data.get("articles", [])),
                "breaking_news_published": len(pipeline_data.get("breaking_news", [])),
                "pipeline_data": pipeline_data
            }
            
            self.logger.info(f"Pipeline completed in {total_time:.2f}s")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "pipeline_data": pipeline_data
            }
    
    async def run_breaking_news_pipeline(self) -> Dict[str, Any]:
        """Run pipeline focused on breaking news detection"""
        start_time = datetime.now()
        pipeline_data = {}
        
        try:
            self.logger.info("Starting breaking news pipeline")
            
            # Run stages up to breaking news
            breaking_stages = [
                ("collector", self.collector),
                ("deduplicator", self.deduplicator),
                ("classifier", self.classifier),
                ("credibility", self.credibility),
                ("breaking_news", self.breaking_news)
            ]
            
            for stage_name, agent in breaking_stages:
                stage_start = datetime.now()
                
                try:
                    self.logger.info(f"Running breaking news stage: {stage_name}")
                    result = await agent.process(pipeline_data)
                    
                    if "error" in result:
                        self.logger.error(f"Breaking news stage {stage_name} failed: {result['error']}")
                        continue
                    
                    pipeline_data.update(result)
                    
                    stage_time = (datetime.now() - stage_start).total_seconds()
                    self.logger.info(f"Breaking news stage {stage_name} completed in {stage_time:.2f}s")
                    
                except Exception as e:
                    self.logger.error(f"Breaking news stage {stage_name} exception: {str(e)}")
                    continue
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "status": "completed",
                "pipeline_type": "breaking_news",
                "processing_time": total_time,
                "breaking_news_found": len(pipeline_data.get("breaking_news", [])),
                "candidates_found": pipeline_data.get("candidates_found", 0),
                "published_count": pipeline_data.get("published_count", 0)
            }
            
            self.logger.info(f"Breaking news pipeline completed in {total_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Breaking news pipeline failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def run_video_generation_pipeline(self) -> Dict[str, Any]:
        """Run pipeline for video generation"""
        start_time = datetime.now()
        pipeline_data = {}
        
        try:
            self.logger.info("Starting video generation pipeline")
            
            # Get recent high-impact articles for video generation
            from database import SessionLocal
            from models import NewsArticle
            from datetime import timedelta
            
            db = SessionLocal()
            cutoff_time = datetime.utcnow() - timedelta(hours=6)
            
            recent_articles = db.query(NewsArticle).filter(
                NewsArticle.impact_level.in_(["high", "critical"]),
                NewsArticle.created_at >= cutoff_time,
                NewsArticle.is_video_generated == False
            ).limit(5).all()
            
            db.close()
            
            if not recent_articles:
                return {
                    "status": "completed",
                    "message": "No articles available for video generation",
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            
            # Convert articles to dict format
            articles_data = []
            for article in recent_articles:
                article_dict = {
                    "id": article.id,
                    "title": article.title,
                    "content": article.content,
                    "summary": article.summary,
                    "headline": article.headline,
                    "category": article.category,
                    "impact_level": article.impact_level
                }
                articles_data.append(article_dict)
            
            pipeline_data["articles"] = articles_data
            
            # Run video generation (would integrate with video service)
            # For now, just mark as processed
            total_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "status": "completed",
                "pipeline_type": "video_generation",
                "processing_time": total_time,
                "articles_processed": len(articles_data),
                "videos_generated": 0  # Would be actual count in real implementation
            }
            
            self.logger.info(f"Video generation pipeline completed in {total_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Video generation pipeline failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def run_custom_pipeline(self, stages: List[str], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a custom pipeline with specific stages"""
        start_time = datetime.now()
        pipeline_data = input_data.copy()
        
        try:
            self.logger.info(f"Starting custom pipeline with stages: {stages}")
            
            # Create stage map
            stage_map = {
                "collector": self.collector,
                "deduplicator": self.deduplicator,
                "classifier": self.classifier,
                "credibility": self.credibility,
                "summarizer": self.summarizer,
                "writer": self.writer,
                "insight": self.insight,
                "breaking_news": self.breaking_news,
                "publisher": self.publisher
            }
            
            # Run specified stages
            for stage_name in stages:
                if stage_name not in stage_map:
                    self.logger.warning(f"Unknown stage: {stage_name}")
                    continue
                
                agent = stage_map[stage_name]
                stage_start = datetime.now()
                
                try:
                    self.logger.info(f"Running custom stage: {stage_name}")
                    result = await agent.process(pipeline_data)
                    
                    if "error" in result:
                        self.logger.error(f"Custom stage {stage_name} failed: {result['error']}")
                        continue
                    
                    pipeline_data.update(result)
                    
                    stage_time = (datetime.now() - stage_start).total_seconds()
                    self.logger.info(f"Custom stage {stage_name} completed in {stage_time:.2f}s")
                    
                except Exception as e:
                    self.logger.error(f"Custom stage {stage_name} exception: {str(e)}")
                    continue
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "status": "completed",
                "pipeline_type": "custom",
                "stages_run": stages,
                "processing_time": total_time,
                "articles_processed": len(pipeline_data.get("articles", []))
            }
            
            self.logger.info(f"Custom pipeline completed in {total_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Custom pipeline failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and statistics"""
        try:
            # This would typically check database for recent processing jobs
            # For now, return basic status
            
            return {
                "status": "ready",
                "available_stages": [stage[0] for stage in self.pipeline_stages],
                "last_run": None,  # Would be actual timestamp
                "total_processed_today": 0,  # Would be actual count
                "errors_today": 0  # Would be actual count
            }
            
        except Exception as e:
            self.logger.error(f"Pipeline status check failed: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        health_status = {}
        
        for stage_name, agent in self.pipeline_stages:
            try:
                # Simple health check - try to access agent properties
                _ = agent.name
                _ = agent.llm
                health_status[stage_name] = "healthy"
            except Exception as e:
                health_status[stage_name] = f"unhealthy: {str(e)}"
        
        overall_health = "healthy" if all(status == "healthy" for status in health_status.values()) else "degraded"
        
        return {
            "overall_health": overall_health,
            "agents": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
