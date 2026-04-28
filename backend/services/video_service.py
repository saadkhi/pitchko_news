from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from models import NewsArticle, Video
from schemas import VideoResponse
import os
from dotenv import load_dotenv
import aiohttp
import asyncio

load_dotenv()

class VideoService:
    def __init__(self):
        self.heygen_api_key = os.getenv("HEYGEN_API_KEY")
        self.synthesia_api_key = os.getenv("SYNTHESIA_API_KEY")
        self.heygen_base_url = "https://api.heygen.com/v1"
        self.synthesia_base_url = "https://api.synthesia.io/v2"
    
    async def get_videos(self, db: Session, limit: int = 10) -> List[VideoResponse]:
        """Get generated video news reports"""
        try:
            videos = db.query(Video).filter(
                Video.status == "completed"
            ).order_by(desc(Video.created_at)).limit(limit).all()
            
            # Load article data for each video
            video_responses = []
            for video in videos:
                article = db.query(NewsArticle).filter(NewsArticle.id == video.article_id).first()
                video_data = VideoResponse.from_orm(video)
                if article:
                    video_data.article = {
                        "id": article.id,
                        "title": article.title,
                        "headline": article.headline,
                        "category": article.category,
                        "summary": article.summary
                    }
                video_responses.append(video_data)
            
            return video_responses
            
        except Exception as e:
            raise Exception(f"Failed to get videos: {str(e)}")
    
    async def generate_video_for_article(self, db: Session, article_id: int) -> Dict[str, Any]:
        """Generate video for a specific article"""
        try:
            # Get article
            article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
            if not article:
                raise Exception("Article not found")
            
            # Check if video already exists
            existing_video = db.query(Video).filter(Video.article_id == article_id).first()
            if existing_video:
                if existing_video.status == "completed":
                    return {"status": "exists", "video_url": existing_video.video_url}
                elif existing_video.status == "generating":
                    return {"status": "in_progress", "video_id": existing_video.id}
            
            # Generate script
            script = await self.generate_video_script(article)
            
            # Create video record
            video = Video(
                article_id=article_id,
                script=script,
                status="generating",
                created_at=datetime.utcnow()
            )
            db.add(video)
            db.commit()
            db.refresh(video)
            
            # Start video generation in background
            asyncio.create_task(self.generate_video_with_provider(video.id, script))
            
            return {"status": "started", "video_id": video.id}
            
        except Exception as e:
            raise Exception(f"Failed to generate video: {str(e)}")
    
    async def generate_video_script(self, article) -> str:
        """Generate video script from article"""
        try:
            # Create a concise script for video narration
            script_parts = []
            
            # Headline
            if article.headline:
                script_parts.append(f"Headline: {article.headline}")
            else:
                script_parts.append(f"Headline: {article.title}")
            
            # Main story
            if article.summary:
                # Extract key points from summary
                summary_sentences = article.summary.split('.')[:3]  # First 3 sentences
                script_parts.append("Here's what you need to know:")
                for sentence in summary_sentences:
                    if sentence.strip():
                        script_parts.append(sentence.strip() + '.')
            
            # Why it matters
            if article.why_it_matters:
                script_parts.append("Why this matters:")
                # Take first 2 sentences from why_it_matters
                why_sentences = article.why_it_matters.split('.')[:2]
                for sentence in why_sentences:
                    if sentence.strip():
                        script_parts.append(sentence.strip() + '.')
            
            # Developer impact
            if article.developer_impact:
                script_parts.append("For developers:")
                # Take first sentence from developer_impact
                dev_sentences = article.developer_impact.split('.')[:1]
                for sentence in dev_sentences:
                    if sentence.strip():
                        script_parts.append(sentence.strip() + '.')
            
            # Future prediction
            if article.future_prediction:
                script_parts.append("Looking ahead:")
                # Take first sentence from future_prediction
                future_sentences = article.future_prediction.split('.')[:1]
                for sentence in future_sentences:
                    if sentence.strip():
                        script_parts.append(sentence.strip() + '.')
            
            # Join and clean up
            full_script = ' '.join(script_parts)
            
            # Ensure script is under 500 words for video generation
            words = full_script.split()
            if len(words) > 500:
                full_script = ' '.join(words[:500]) + '...'
            
            return full_script
            
        except Exception as e:
            # Fallback script
            return f"Breaking news in {article.category}: {article.title}. This is an important development that affects the technology industry. Stay tuned for more updates."
    
    async def generate_video_with_provider(self, video_id: int, script: str):
        """Generate video using available provider"""
        try:
            # Try HeyGen first, then Synthesia
            if self.heygen_api_key:
                result = await self.generate_with_heygen(video_id, script)
                if result.get("success"):
                    return
            
            if self.synthesia_api_key:
                result = await self.generate_with_synthesia(video_id, script)
                if result.get("success"):
                    return
            
            # Mark as failed if no provider worked
            await self.update_video_status(video_id, "failed", "No video provider available")
            
        except Exception as e:
            await self.update_video_status(video_id, "failed", str(e))
    
    async def generate_with_heygen(self, video_id: int, script: str) -> Dict[str, Any]:
        """Generate video using HeyGen API"""
        try:
            if not self.heygen_api_key:
                return {"success": False, "error": "HeyGen API key not configured"}
            
            headers = {
                "X-Api-Key": self.heygen_api_key,
                "Content-Type": "application/json"
            }
            
            # Create video generation request
            payload = {
                "video_inputs": [
                    {
                        "character": {
                            "character_id": "your-character-id",  # You'll need to configure this
                            "avatar_style": "normal"
                        },
                        "voice": {
                            "voice_id": "your-voice-id",  # You'll need to configure this
                            "speed": 1.0,
                            "emotion": "neutral"
                        },
                        "background": {
                            "background_id": "your-background-id"  # You'll need to configure this
                        },
                        "script": {
                            "type": "text",
                            "input": script,
                            "provider": "microsoft"  # or other provider
                        }
                    }
                ],
                "test": False,  # Set to True for testing
                "aspect_ratio": "16:9"
            }
            
            async with aiohttp.ClientSession() as session:
                # Submit video generation request
                async with session.post(
                    f"{self.heygen_base_url}/video/generate",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {"success": False, "error": f"HeyGen API error: {error_text}"}
                    
                    result = await response.json()
                    video_id_heygen = result.get("data", {}).get("video_id")
                    
                    if not video_id_heygen:
                        return {"success": False, "error": "No video ID returned from HeyGen"}
                    
                    # Poll for completion
                    video_url = await self.poll_heygen_video(video_id_heygen, headers)
                    
                    if video_url:
                        await self.update_video_status(video_id, "completed", video_url)
                        return {"success": True, "video_url": video_url}
                    else:
                        await self.update_video_status(video_id, "failed", "Video generation timed out")
                        return {"success": False, "error": "Video generation timed out"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def poll_heygen_video(self, video_id_heygen: str, headers: Dict[str, str], max_attempts: int = 30) -> Optional[str]:
        """Poll HeyGen for video completion"""
        for attempt in range(max_attempts):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.heygen_base_url}/video/{video_id_heygen}",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            status = result.get("data", {}).get("status")
                            
                            if status == "completed":
                                return result.get("data", {}).get("video_url")
                            elif status == "failed":
                                return None
                            elif status in ["processing", "pending"]:
                                await asyncio.sleep(10)  # Wait 10 seconds
                                continue
                        else:
                            await asyncio.sleep(10)
                            continue
            except Exception:
                await asyncio.sleep(10)
                continue
        
        return None
    
    async def generate_with_synthesia(self, video_id: int, script: str) -> Dict[str, Any]:
        """Generate video using Synthesia API"""
        try:
            if not self.synthesia_api_key:
                return {"success": False, "error": "Synthesia API key not configured"}
            
            headers = {
                "Authorization": f"Bearer {self.synthesia_api_key}",
                "Content-Type": "application/json"
            }
            
            # Create video generation request
            payload = {
                "video": {
                    "input": [
                        {
                            "scriptText": script,
                            "avatar": {
                                "avatarId": "your-avatar-id"  # You'll need to configure this
                            },
                            "background": {
                                "backgroundColor": "#ffffff"
                            },
                            "voice": {
                                "voiceId": "your-voice-id"  # You'll need to configure this
                            }
                        }
                    ],
                    "title": "Tech News Report",
                    "description": "Automated tech news video report"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                # Submit video generation request
                async with session.post(
                    f"{self.synthesia_base_url}/videos",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status not in [200, 201]:
                        error_text = await response.text()
                        return {"success": False, "error": f"Synthesia API error: {error_text}"}
                    
                    result = await response.json()
                    video_id_synthesia = result.get("id")
                    
                    if not video_id_synthesia:
                        return {"success": False, "error": "No video ID returned from Synthesia"}
                    
                    # Poll for completion
                    video_url = await self.poll_synthesia_video(video_id_synthesia, headers)
                    
                    if video_url:
                        await self.update_video_status(video_id, "completed", video_url)
                        return {"success": True, "video_url": video_url}
                    else:
                        await self.update_video_status(video_id, "failed", "Video generation timed out")
                        return {"success": False, "error": "Video generation timed out"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def poll_synthesia_video(self, video_id_synthesia: str, headers: Dict[str, str], max_attempts: int = 30) -> Optional[str]:
        """Poll Synthesia for video completion"""
        for attempt in range(max_attempts):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.synthesia_base_url}/videos/{video_id_synthesia}",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            status = result.get("status")
                            
                            if status == "complete":
                                return result.get("download_url")
                            elif status == "failed":
                                return None
                            elif status in ["inProgress", "processing"]:
                                await asyncio.sleep(10)  # Wait 10 seconds
                                continue
                        else:
                            await asyncio.sleep(10)
                            continue
            except Exception:
                await asyncio.sleep(10)
                continue
        
        return None
    
    async def update_video_status(self, video_id: int, status: str, video_url: str = None, error_message: str = None):
        """Update video status in database"""
        try:
            from database import SessionLocal
            db = SessionLocal()
            
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                video.status = status
                if video_url:
                    video.video_url = video_url
                    video.generated_at = datetime.utcnow()
                if error_message:
                    # Store error in a separate field if available
                    pass
                db.commit()
            
            db.close()
            
        except Exception as e:
            print(f"Failed to update video status: {str(e)}")
    
    async def get_video_status(self, db: Session, video_id: int) -> Optional[VideoResponse]:
        """Get video status"""
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                return VideoResponse.from_orm(video)
            return None
            
        except Exception as e:
            raise Exception(f"Failed to get video status: {str(e)}")
    
    async def delete_video(self, db: Session, video_id: int) -> bool:
        """Delete video record"""
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                db.delete(video)
                db.commit()
                return True
            return False
            
        except Exception as e:
            raise Exception(f"Failed to delete video: {str(e)}")
    
    async def get_video_statistics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Get video generation statistics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Total videos
            total_videos = db.query(Video).filter(
                Video.created_at >= cutoff_time
            ).count()
            
            # By status
            status_stats = db.query(
                Video.status,
                db.func.count(Video.id).label('count')
            ).filter(
                Video.created_at >= cutoff_time
            ).group_by(Video.status).all()
            
            # Average duration
            avg_duration = db.query(
                db.func.avg(Video.duration)
            ).filter(
                and_(
                    Video.created_at >= cutoff_time,
                    Video.duration.isnot(None)
                )
            ).scalar()
            
            return {
                "total_videos": total_videos,
                "by_status": [
                    {
                        "status": stat.status,
                        "count": stat.count
                    }
                    for stat in status_stats
                ],
                "average_duration": float(avg_duration) if avg_duration else 0
            }
            
        except Exception as e:
            raise Exception(f"Failed to get video statistics: {str(e)}")
