import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import json

app = FastAPI(
    title="Pitchko News API",
    description="Semi-Agentic Tech News Platform - Vercel Compatible",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class NewsItem(BaseModel):
    id: int
    title: str
    summary: str
    category: str
    impact_level: str
    credibility_score: float
    published_at: str
    url: Optional[str] = None

class TrendItem(BaseModel):
    topic: str
    count: int
    sentiment: str

# Mock data for development
MOCK_NEWS = [
    {
        "id": 1,
        "title": "AI Breakthrough: New Model Achieves Human-Level Performance",
        "summary": "Latest AI research shows significant improvements in natural language understanding.",
        "category": "AI/ML",
        "impact_level": "high",
        "credibility_score": 0.95,
        "published_at": "2024-01-15T10:00:00Z",
        "url": "https://example.com/ai-breakthrough"
    },
    {
        "id": 2,
        "title": "Tech Giants Announce Cloud Computing Partnership",
        "summary": "Major technology companies collaborate on next-generation cloud infrastructure.",
        "category": "Cloud",
        "impact_level": "medium",
        "credibility_score": 0.88,
        "published_at": "2024-01-15T09:30:00Z",
        "url": "https://example.com/cloud-partnership"
    }
]

MOCK_TRENDS = [
    {"topic": "Artificial Intelligence", "count": 45, "sentiment": "positive"},
    {"topic": "Cloud Computing", "count": 32, "sentiment": "neutral"},
    {"topic": "Cybersecurity", "count": 28, "sentiment": "positive"},
    {"topic": "Blockchain", "count": 15, "sentiment": "neutral"}
]

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Pitchko News API is running"}

@app.get("/news", response_model=List[NewsItem])
async def get_news(
    category: Optional[str] = None,
    impact_level: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Get news articles with optional filtering"""
    filtered_news = MOCK_NEWS
    
    if category:
        filtered_news = [n for n in filtered_news if n["category"].lower() == category.lower()]
    
    if impact_level:
        filtered_news = [n for n in filtered_news if n["impact_level"].lower() == impact_level.lower()]
    
    return filtered_news[offset:offset + limit]

@app.get("/news/{article_id}", response_model=NewsItem)
async def get_article(article_id: int):
    """Get specific article by ID"""
    article = next((n for n in MOCK_NEWS if n["id"] == article_id), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@app.get("/breaking", response_model=List[NewsItem])
async def get_breaking_news():
    """Get breaking news (high/critical impact with high credibility)"""
    breaking_news = [
        n for n in MOCK_NEWS 
        if n["impact_level"] in ["high", "critical"] and n["credibility_score"] > 0.9
    ]
    return breaking_news

@app.post("/trigger-agents")
async def trigger_agents():
    """Manually trigger the agent pipeline (mock implementation)"""
    return {"message": "Agent pipeline triggered successfully"}

@app.get("/trends", response_model=List[TrendItem])
async def get_trends():
    """Get trending topics and analytics"""
    return MOCK_TRENDS

@app.get("/videos")
async def get_videos(limit: int = 10):
    """Get generated video news reports (mock implementation)"""
    return {
        "videos": [
            {
                "id": 1,
                "title": "AI Weekly Roundup",
                "description": "Latest developments in artificial intelligence",
                "url": "https://example.com/video1",
                "thumbnail": "https://example.com/thumb1.jpg",
                "duration": "5:30",
                "created_at": "2024-01-15T08:00:00Z"
            }
        ]
    }

# Vercel serverless function handler
handler = app
