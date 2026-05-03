from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String)
    trust_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    articles = relationship("NewsArticle", back_populates="source")

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    summary = Column(Text)
    short_description = Column(Text)
    category = Column(String, index=True)  # AI, Startups, Cybersecurity, Big Tech
    impact_level = Column(String, index=True)  # low, medium, high, critical
    credibility_score = Column(Float, index=True)
    confidence_score = Column(Float)
    source_count = Column(Integer, default=1)
    
    # Writer agent outputs
    headline = Column(String)
    why_it_matters = Column(Text)
    developer_impact = Column(Text)
    
    # Insight agent outputs
    market_impact = Column(Text)
    future_prediction = Column(Text)
    who_should_care = Column(Text)
    
    # Metadata
    url = Column(String)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_breaking = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    is_video_generated = Column(Boolean, default=False)
    
    # Foreign keys
    source_id = Column(Integer, ForeignKey("sources.id"))
    
    # Relationships
    source = relationship("Source", back_populates="articles")
    video = relationship("Video", back_populates="article", uselist=False)
    raw_sources = relationship("RawSource", back_populates="article")

class RawSource(Base):
    __tablename__ = "raw_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"))
    source_url = Column(String)
    source_name = Column(String)
    title = Column(String)
    content = Column(Text)
    published_at = Column(DateTime)
    similarity_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("NewsArticle", back_populates="raw_sources")

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"), unique=True)
    video_url = Column(String)
    script = Column(Text)
    duration = Column(Integer)  # seconds
    status = Column(String, default="pending")  # pending, generating, completed, failed
    generated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("NewsArticle", back_populates="video")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String)  # collection, processing, video_generation
    status = Column(String, default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    job_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Trend(Base):
    __tablename__ = "trends"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True)
    category = Column(String)
    count = Column(Integer)
    sentiment_score = Column(Float)
    impact_distribution = Column(JSON)  # distribution of impact levels
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
