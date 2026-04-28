from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio

from database import get_db, engine
from models import Base
from schemas import NewsResponse, BreakingNewsResponse, TrendResponse
from agents.orchestrator import AgentOrchestrator
from services.news_service import NewsService
from services.video_service import VideoService
from scheduler import NewsScheduler

# Database tables
Base.metadata.create_all(bind=engine)

# Initialize services
orchestrator = AgentOrchestrator()
news_service = NewsService()
video_service = VideoService()
scheduler = NewsScheduler()

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.start()
    yield
    # Shutdown
    scheduler.stop()

app = FastAPI(
    title="Pitchko News API",
    description="Semi-Agentic Tech News Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/", tags="Health")
async def root():
    return {"status": "healthy", "message": "Pitchko News API is running"}

@app.get("/news", response_model=List[NewsResponse], tags="News")
async def get_news(
    category: Optional[str] = None,
    impact_level: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get news articles with optional filtering"""
    try:
        news = await news_service.get_news(
            db=db,
            category=category,
            impact_level=impact_level,
            limit=limit,
            offset=offset
        )
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/{article_id}", response_model=NewsResponse, tags="News")
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get specific article by ID"""
    try:
        article = await news_service.get_article_by_id(db, article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/breaking", response_model=List[BreakingNewsResponse], tags="Breaking News")
async def get_breaking_news(db: Session = Depends(get_db)):
    """Get breaking news (high/critical impact with high credibility)"""
    try:
        breaking_news = await news_service.get_breaking_news(db)
        return breaking_news
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger-agents", tags="Agents")
async def trigger_agents(background_tasks: BackgroundTasks):
    """Manually trigger the agent pipeline"""
    try:
        background_tasks.add_task(orchestrator.run_full_pipeline)
        return {"message": "Agent pipeline triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trends", response_model=List[TrendResponse], tags="Analytics")
async def get_trends(db: Session = Depends(get_db)):
    """Get trending topics and analytics"""
    try:
        trends = await news_service.get_trends(db)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/videos", tags="Videos")
async def get_videos(limit: int = 10, db: Session = Depends(get_db)):
    """Get generated video news reports"""
    try:
        videos = await video_service.get_videos(db, limit)
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
