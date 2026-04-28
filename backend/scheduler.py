import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from agents.orchestrator import AgentOrchestrator
from services.video_service import VideoService
from database import SessionLocal
from models import ProcessingJob

class NewsScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.orchestrator = AgentOrchestrator()
        self.video_service = VideoService()
        self.logger = logging.getLogger("scheduler")
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def start(self):
        """Start the scheduler"""
        try:
            # Schedule news collection and breaking news detection (every 5 minutes)
            self.scheduler.add_job(
                func=self.run_breaking_news_pipeline,
                trigger=IntervalTrigger(minutes=5),
                id='breaking_news_pipeline',
                name='Breaking News Pipeline',
                replace_existing=True
            )
            
            # Schedule video generation (every hour)
            self.scheduler.add_job(
                func=self.run_video_generation_pipeline,
                trigger=IntervalTrigger(hours=1),
                id='video_generation_pipeline',
                name='Video Generation Pipeline',
                replace_existing=True
            )
            
            # Schedule full pipeline (every 30 minutes for comprehensive processing)
            self.scheduler.add_job(
                func=self.run_full_pipeline,
                trigger=IntervalTrigger(minutes=30),
                id='full_pipeline',
                name='Full News Pipeline',
                replace_existing=True
            )
            
            # Schedule cleanup (daily at 2 AM)
            self.scheduler.add_job(
                func=self.cleanup_old_data,
                trigger='cron',
                hour=2,
                minute=0,
                id='cleanup_job',
                name='Daily Cleanup',
                replace_existing=True
            )
            
            # Schedule health check (every hour)
            self.scheduler.add_job(
                func=self.health_check,
                trigger=IntervalTrigger(hours=1),
                id='health_check',
                name='System Health Check',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.logger.info("News scheduler started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {str(e)}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            self.logger.info("News scheduler stopped")
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {str(e)}")
    
    async def run_breaking_news_pipeline(self):
        """Run breaking news pipeline"""
        job_id = await self.create_job("breaking_news_collection")
        
        try:
            self.logger.info("Starting breaking news pipeline")
            
            # Run the breaking news pipeline
            result = await self.orchestrator.run_breaking_news_pipeline()
            
            # Update job status
            await self.update_job(job_id, "completed", result)
            
            self.logger.info(f"Breaking news pipeline completed: {result.get('status', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Breaking news pipeline failed: {str(e)}")
            await self.update_job(job_id, "failed", {"error": str(e)})
    
    async def run_video_generation_pipeline(self):
        """Run video generation pipeline"""
        job_id = await self.create_job("video_generation")
        
        try:
            self.logger.info("Starting video generation pipeline")
            
            # Get recent high-impact articles that don't have videos yet
            from models import NewsArticle
            from sqlalchemy import and_, desc
            
            db = SessionLocal()
            cutoff_time = datetime.utcnow() - timedelta(hours=6)
            
            recent_articles = db.query(NewsArticle).filter(
                and_(
                    NewsArticle.impact_level.in_(["high", "critical"]),
                    NewsArticle.created_at >= cutoff_time,
                    NewsArticle.is_published == True
                )
            ).order_by(desc(NewsArticle.created_at)).limit(3).all()
            
            db.close()
            
            videos_generated = 0
            for article in recent_articles:
                try:
                    # Check if video already exists
                    db = SessionLocal()
                    existing_video = db.query(Video).filter(Video.article_id == article.id).first()
                    db.close()
                    
                    if not existing_video:
                        result = await self.video_service.generate_video_for_article(SessionLocal(), article.id)
                        if result.get("status") in ["started", "exists"]:
                            videos_generated += 1
                            self.logger.info(f"Video generation started for article: {article.title}")
                
                except Exception as e:
                    self.logger.error(f"Failed to generate video for article {article.id}: {str(e)}")
            
            # Update job status
            result = {
                "status": "completed",
                "articles_processed": len(recent_articles),
                "videos_generated": videos_generated
            }
            await self.update_job(job_id, "completed", result)
            
            self.logger.info(f"Video generation pipeline completed: {videos_generated} videos generated")
            
        except Exception as e:
            self.logger.error(f"Video generation pipeline failed: {str(e)}")
            await self.update_job(job_id, "failed", {"error": str(e)})
    
    async def run_full_pipeline(self):
        """Run full news processing pipeline"""
        job_id = await self.create_job("full_pipeline")
        
        try:
            self.logger.info("Starting full news pipeline")
            
            # Run the complete pipeline
            result = await self.orchestrator.run_full_pipeline()
            
            # Update job status
            await self.update_job(job_id, "completed", result)
            
            self.logger.info(f"Full pipeline completed: {result.get('status', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Full pipeline failed: {str(e)}")
            await self.update_job(job_id, "failed", {"error": str(e)})
    
    async def cleanup_old_data(self):
        """Clean up old data"""
        job_id = await self.create_job("cleanup")
        
        try:
            self.logger.info("Starting data cleanup")
            
            # Clean up old processing jobs (older than 7 days)
            db = SessionLocal()
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            
            deleted_jobs = db.query(ProcessingJob).filter(
                ProcessingJob.created_at < cutoff_time
            ).delete()
            
            db.commit()
            db.close()
            
            # Update job status
            result = {
                "status": "completed",
                "deleted_jobs": deleted_jobs
            }
            await self.update_job(job_id, "completed", result)
            
            self.logger.info(f"Data cleanup completed: {deleted_jobs} old jobs deleted")
            
        except Exception as e:
            self.logger.error(f"Data cleanup failed: {str(e)}")
            await self.update_job(job_id, "failed", {"error": str(e)})
    
    async def health_check(self):
        """Perform system health check"""
        job_id = await self.create_job("health_check")
        
        try:
            self.logger.info("Starting system health check")
            
            # Check agent health
            health_result = await self.orchestrator.health_check()
            
            # Check database connectivity
            try:
                db = SessionLocal()
                db.execute("SELECT 1")
                db.close()
                db_status = "healthy"
            except Exception as e:
                db_status = f"unhealthy: {str(e)}"
            
            # Check scheduler status
            scheduler_status = "healthy" if self.scheduler.running else "stopped"
            
            # Update job status
            result = {
                "status": "completed",
                "agents_health": health_result,
                "database_status": db_status,
                "scheduler_status": scheduler_status,
                "overall_health": "healthy" if (
                    health_result.get("overall_health") == "healthy" and
                    db_status == "healthy" and
                    scheduler_status == "healthy"
                ) else "degraded"
            }
            await self.update_job(job_id, "completed", result)
            
            self.logger.info(f"Health check completed: {result['overall_health']}")
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            await self.update_job(job_id, "failed", {"error": str(e)})
    
    async def create_job(self, job_type: str) -> int:
        """Create a processing job record"""
        try:
            db = SessionLocal()
            
            job = ProcessingJob(
                job_type=job_type,
                status="running",
                started_at=datetime.utcnow()
            )
            
            db.add(job)
            db.commit()
            db.refresh(job)
            
            db.close()
            return job.id
            
        except Exception as e:
            self.logger.error(f"Failed to create job record: {str(e)}")
            return 0
    
    async def update_job(self, job_id: int, status: str, result: dict = None):
        """Update processing job status"""
        try:
            if job_id == 0:
                return
            
            db = SessionLocal()
            
            job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
            if job:
                job.status = status
                if status == "completed":
                    job.completed_at = datetime.utcnow()
                if result:
                    job.metadata = result
                
                db.commit()
            
            db.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update job record: {str(e)}")
    
    def get_job_status(self, job_id: int) -> dict:
        """Get job status"""
        try:
            db = SessionLocal()
            
            job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
            
            if job:
                result = {
                    "id": job.id,
                    "job_type": job.job_type,
                    "status": job.status,
                    "started_at": job.started_at,
                    "completed_at": job.completed_at,
                    "metadata": job.metadata
                }
            else:
                result = {"error": "Job not found"}
            
            db.close()
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get job status: {str(e)}")
            return {"error": str(e)}
    
    def get_scheduler_status(self) -> dict:
        """Get scheduler status"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
            
            return {
                "status": "running" if self.scheduler.running else "stopped",
                "jobs": jobs
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get scheduler status: {str(e)}")
            return {"error": str(e)}
