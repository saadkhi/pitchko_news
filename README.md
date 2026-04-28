# Pitchko News - Semi-Agentic Tech News Platform

A production-ready autonomous tech news website that collects, analyzes, and publishes news using advanced AI agents.

## 🚀 Features

### Core Architecture
- **Multi-Agent System**: 9 specialized AI agents for news processing
- **Real-time Processing**: 5-minute news collection cycles
- **Guardrails System**: Credibility scoring and validation
- **Video Generation**: Avatar-based news reports
- **Trending Analytics**: Real-time trend detection and visualization

### AI Agents
1. **CollectorAgent**: Fetches news from APIs and RSS feeds
2. **DeduplicationAgent**: Removes duplicates using embeddings
3. **ClassificationAgent**: Categorizes and assesses impact levels
4. **CredibilityAgent**: Validates source credibility (guardrail)
5. **SummarizerAgent**: Generates comprehensive summaries
6. **WriterAgent**: Creates headlines, descriptions, and insights
7. **InsightAgent**: Provides market impact and predictions
8. **BreakingNewsAgent**: Detects and publishes breaking news
9. **PublisherAgent**: Manages content publication and distribution

### Frontend Features
- **Responsive Design**: Mobile-first, modern UI
- **Real-time Updates**: Breaking news ticker
- **Advanced Search**: Full-text search with filters
- **Video Player**: Embedded video reports
- **Trends Dashboard**: Interactive charts and analytics
- **SEO Optimized**: Meta tags, sitemaps, structured data

### Backend Features
- **FastAPI**: High-performance async API
- **PostgreSQL**: Robust database with Supabase
- **Redis Queue**: Background job processing
- **Cron Scheduler**: Automated news processing
- **Video Pipeline**: HeyGen/Synthesia integration

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with Supabase
- **Queue**: Redis + Celery
- **AI**: LangChain + OpenAI GPT-4
- **Video**: HeyGen/Synthesia APIs
- **Scheduler**: APScheduler

### Frontend
- **Framework**: Next.js 14 (React)
- **Styling**: Tailwind CSS + Headless UI
- **Charts**: Recharts
- **State**: SWR + React Hooks
- **Icons**: Heroicons
- **Deployment**: Vercel

### Infrastructure
- **Backend**: Railway/Render/AWS
- **Frontend**: Vercel
- **Database**: Supabase
- **Queue**: Redis Cloud
- **Monitoring**: Custom health checks

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis
- OpenAI API Key
- News API Keys

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/pitchko_news
OPENAI_API_KEY=your-openai-api-key
NEWS_API_KEY=your-news-api-key
GNEWS_API_KEY=your-gnews-api-key
REDIS_URL=redis://localhost:6379/0
```

### Database Setup

```bash
# Install PostgreSQL and create database
createdb pitchko_news

# Run migrations
alembic upgrade head

# Or use Supabase (recommended)
# Create Supabase project and update .env with connection details
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit environment variables
nano .env.local
```

Required environment variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

## 🚀 Running the Application

### Development Mode

```bash
# Terminal 1: Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Production Mode

```bash
# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npm start
```

## 🤖 AI Agent Pipeline

### Automated Execution
- **Every 5 minutes**: News collection + breaking news detection
- **Every 30 minutes**: Full pipeline execution
- **Every hour**: Video generation for high-impact stories
- **Daily at 2 AM**: Data cleanup and maintenance

### Manual Execution
```bash
# Trigger full pipeline
curl -X POST http://localhost:8000/trigger-agents

# Check pipeline status
curl http://localhost:8000/agents/status

# Health check
curl http://localhost:8000/agents/health
```

## 📊 API Endpoints

### News Endpoints
- `GET /news` - Get news articles with filters
- `GET /news/{id}` - Get specific article
- `GET /breaking` - Get breaking news
- `GET /trends` - Get trending topics
- `POST /search` - Search news articles

### Video Endpoints
- `GET /videos` - Get generated videos
- `POST /videos/generate/{article_id}` - Generate video
- `GET /videos/{id}` - Get video status

### Agent Endpoints
- `POST /trigger-agents` - Manual pipeline trigger
- `GET /agents/status` - Pipeline status
- `GET /agents/health` - Health check

## 🎥 Video Generation

### Configuration
1. **HeyGen Setup**:
   - Get API key from HeyGen dashboard
   - Configure character and voice IDs
   - Update `.env` with `HEYGEN_API_KEY`

2. **Synthesia Setup**:
   - Get API key from Synthesia dashboard
   - Configure avatar and voice IDs
   - Update `.env` with `SYNTHESIA_API_KEY`

### Video Script Generation
The system automatically generates video scripts from:
- Article headlines and summaries
- Key insights and impact analysis
- Future predictions and market implications

## 📈 Analytics & Monitoring

### Built-in Metrics
- Article processing statistics
- Credibility score distribution
- Trend analysis and visualization
- Video generation metrics
- System health monitoring

### Custom Dashboards
Access trends and analytics at `/trends`:
- Real-time trending topics
- Category distribution charts
- Impact level analysis
- Sentiment analysis

## 🔒 Security Features

### Authentication
- JWT-based authentication (optional)
- API rate limiting
- CORS configuration

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection headers
- Content Security Policy

### Privacy
- GDPR compliance
- Data anonymization
- Cookie management
- User consent management

## 🚀 Deployment

### Backend (Railway/Render)

```bash
# Using Docker
docker build -t pitchko-backend .
docker run -p 8000:8000 pitchko-backend

# Railway deployment
railway login
railway init
railway up

# Render deployment
# Connect GitHub repository and configure build settings
```

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Or connect GitHub repository for automatic deployments
```

### Environment Variables

**Production Backend**:
- `DATABASE_URL`: Production PostgreSQL URL
- `OPENAI_API_KEY`: Production OpenAI key
- `REDIS_URL`: Production Redis URL
- `ENVIRONMENT`: `production`

**Production Frontend**:
- `NEXT_PUBLIC_API_URL`: Production API URL
- `NEXT_PUBLIC_SITE_URL`: Production site URL

## 🔧 Configuration

### News Sources
Edit `agents/collector_agent.py` to add/remove RSS feeds and API sources:

```python
self.news_sources = {
    "techcrunch": {
        "rss": "https://techcrunch.com/feed/",
        "trust_score": 0.8,
        "categories": ["Startups", "Big Tech", "AI"]
    },
    # Add more sources...
}
```

### Credibility Thresholds
Configure guardrails in `agents/credibility_agent.py`:

```python
self.breaking_threshold = {
    "impact_level": ["high", "critical"],
    "credibility_score": 0.75,
    "min_sources": 2
}
```

### Video Settings
Configure avatar and voice settings in `services/video_service.py`:

```python
payload = {
    "character": {
        "character_id": "your-character-id",
        "avatar_style": "normal"
    },
    "voice": {
        "voice_id": "your-voice-id",
        "speed": 1.0
    }
}
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Test API endpoints
curl -X GET http://localhost:8000/news

# Test agent pipeline
curl -X POST http://localhost:8000/trigger-agents
```

## 📈 Performance Optimization

### Backend
- Database indexing on frequently queried fields
- Redis caching for API responses
- Async processing for all I/O operations
- Connection pooling for database

### Frontend
- Next.js Image Optimization
- Static asset optimization
- Code splitting and lazy loading
- SWR for efficient data fetching

## 🔄 Scaling

### Horizontal Scaling
- Load balancer configuration
- Multiple backend instances
- Database read replicas
- Redis clustering

### Vertical Scaling
- Increase API rate limits
- Optimize database queries
- Implement caching layers
- Use CDN for static assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/TypeScript
- Write comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Email: support@pitchkonews.com
- Documentation: [docs.pitchkonews.com](https://docs.pitchkonews.com)

## 🗺️ Roadmap

### Upcoming Features
- [ ] Real-time WebSocket updates
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Custom news feeds
- [ ] Social sharing integration
- [ ] Email notifications
- [ ] Multi-language support
- [ ] User authentication and preferences

### Performance Improvements
- [ ] GraphQL API
- [ ] Advanced caching strategies
- [ ] Edge computing integration
- [ ] Database optimization

---

**Built with ❤️ by the Pitchko News Team**