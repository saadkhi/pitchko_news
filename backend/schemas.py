from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class SourceBase(BaseModel):
    name: str
    url: str
    trust_score: float = 0.5

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RawSourceBase(BaseModel):
    source_url: str
    source_name: str
    title: str
    content: str
    published_at: Optional[datetime] = None
    similarity_score: Optional[float] = None

class RawSource(RawSourceBase):
    id: int
    article_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class NewsArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    short_description: Optional[str] = None
    category: str
    impact_level: str
    credibility_score: float
    confidence_score: float
    source_count: int = 1
    url: Optional[str] = None
    published_at: Optional[datetime] = None

class NewsArticleCreate(NewsArticleBase):
    source_id: int
    headline: Optional[str] = None
    why_it_matters: Optional[str] = None
    developer_impact: Optional[str] = None
    market_impact: Optional[str] = None
    future_prediction: Optional[str] = None
    who_should_care: Optional[str] = None

class NewsArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    short_description: Optional[str] = None
    category: Optional[str] = None
    impact_level: Optional[str] = None
    credibility_score: Optional[float] = None
    confidence_score: Optional[float] = None
    is_breaking: Optional[bool] = None
    is_published: Optional[bool] = None
    is_video_generated: Optional[bool] = None

class NewsResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: Optional[str]
    short_description: Optional[str]
    category: str
    impact_level: str
    credibility_score: float
    confidence_score: float
    source_count: int
    headline: Optional[str]
    why_it_matters: Optional[str]
    developer_impact: Optional[str]
    market_impact: Optional[str]
    future_prediction: Optional[str]
    who_should_care: Optional[str]
    url: Optional[str]
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_breaking: bool
    is_published: bool
    is_video_generated: bool
    source: Optional[Source] = None
    raw_sources: Optional[List[RawSource]] = None
    
    class Config:
        from_attributes = True

class BreakingNewsResponse(BaseModel):
    id: int
    title: str
    short_description: Optional[str]
    category: str
    impact_level: str
    credibility_score: float
    headline: Optional[str]
    created_at: datetime
    url: Optional[str]
    
    class Config:
        from_attributes = True

class VideoBase(BaseModel):
    script: Optional[str] = None
    duration: Optional[int] = None

class VideoCreate(VideoBase):
    article_id: int

class VideoResponse(BaseModel):
    id: int
    article_id: int
    video_url: Optional[str]
    script: Optional[str]
    duration: Optional[int]
    status: str
    generated_at: Optional[datetime]
    created_at: datetime
    article: Optional[NewsResponse] = None
    
    class Config:
        from_attributes = True

class TrendResponse(BaseModel):
    id: int
    keyword: str
    category: str
    count: int
    sentiment_score: float
    impact_distribution: Dict[str, int]
    date: datetime
    
    class Config:
        from_attributes = True

class AgentInput(BaseModel):
    data: Dict[str, Any]
    agent_type: str

class AgentOutput(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float

class PipelineStatus(BaseModel):
    status: str
    current_agent: Optional[str] = None
    total_articles_processed: int
    articles_published: int
    errors: List[str] = []
