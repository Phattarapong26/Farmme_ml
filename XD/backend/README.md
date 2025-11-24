# FarmMe Backend API

Smart Farming Recommendation System - Backend API built with FastAPI and PostgreSQL.

## Features

- 🌾 Crop price prediction using ML models
- 📊 Weather data integration
- 💬 AI-powered chat recommendations (Gemini)
- 📈 Price forecasting and analytics
- 🔐 User authentication and profiles
- ☁️ Cloud database with Supabase

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy
- **Cache**: Redis
- **ML**: TensorFlow, scikit-learn
- **AI**: Google Gemini API

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (local) or Supabase account
- Redis (optional, for caching)

### Installation

1. **Clone repository**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   copy .env.example .env
   # Edit .env with your credentials
   ```

4. **Run application**:
   ```bash
   python run.py
   ```

5. **Access API**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Database Setup

### Option 1: Supabase (Recommended for Production)

Supabase provides a cloud PostgreSQL database that all team members can access.

**Quick Setup**:
```bash
# Run automated migration
python scripts/migrate_to_supabase.py
```

**Manual Setup**:
1. Get Supabase credentials from team lead
2. Update `.env`:
   ```env
   DATABASE_URL=postgresql://postgres.inhanxxglxnjbugppulg:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```
3. Test connection:
   ```bash
   python scripts/test_supabase_connection.py
   ```

📖 **Full Guide**: See [SUPABASE_MIGRATION_GUIDE.md](SUPABASE_MIGRATION_GUIDE.md)

### Option 2: Local PostgreSQL (Development)

**Setup**:
1. Install PostgreSQL
2. Create database:
   ```bash
   python create_database.py
   ```
3. Import data:
   ```bash
   python import_dataset.py
   ```

**Configuration**:
```env
DATABASE_URL=postgresql://postgres:123@localhost:5432/Evena
```

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database (Choose one)
# Supabase (Production/Team)
DATABASE_URL=postgresql://postgres.inhanxxglxnjbugppulg:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# Local PostgreSQL (Development)
# DATABASE_URL=postgresql://postgres:123@localhost:5432/Evena

# Redis Cache
REDIS_URL=redis://default:[PASSWORD]@redis-15456.c8.us-east-1-4.ec2.redns.redis-cloud.com:15456

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Security
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development

# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   └── models/              # Data models
├── scripts/
│   ├── migrate_to_supabase.py    # Migration orchestrator
│   ├── export_database.py        # Export local DB
│   ├── import_to_supabase.py     # Import to Supabase
│   ├── verify_migration.py       # Verify migration
│   ├── test_supabase_connection.py
│   ├── update_config.py
│   ├── backup_env.py
│   └── get_supabase_credentials.py
├── database.py              # Database configuration
├── config.py                # Application configuration
├── run.py                   # Application entry point
├── create_database.py       # Local DB setup
├── import_dataset.py        # Import CSV data
└── requirements.txt         # Python dependencies
```

## API Endpoints

### Health Check
- `GET /health` - API health status

### Predictions
- `POST /api/predict` - Get crop price prediction
- `GET /api/predictions/{id}` - Get prediction by ID

### Recommendations
- `POST /api/recommend` - Get crop recommendations
- `GET /api/recommendations` - List recommendations

### Chat
- `POST /api/chat` - Chat with AI assistant
- `GET /api/chat/history` - Get chat history

### Forecast
- `GET /api/forecast/{crop_type}` - Get price forecast
- `GET /api/forecast/province/{province}` - Get province forecast

### Data
- `GET /api/crops` - List all crops
- `GET /api/provinces` - List all provinces
- `GET /api/prices` - Get price history

📖 **Full API Documentation**: http://localhost:8000/docs

## Development

### Running Tests

```bash
pytest
```

### Code Style

```bash
# Format code
black .

# Lint code
flake8 .
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Deployment

### Production Checklist

- [ ] Update `ENVIRONMENT=production` in `.env`
- [ ] Set strong `SECRET_KEY`
- [ ] Use Supabase for database
- [ ] Enable Redis caching
- [ ] Configure CORS origins
- [ ] Set up monitoring
- [ ] Enable rate limiting
- [ ] Use HTTPS

### Docker Deployment

```bash
# Build image
docker build -t farmme-backend .

# Run container
docker run -p 8000:8000 --env-file .env farmme-backend
```

## Troubleshooting

### Database Connection Issues

**Error**: `could not connect to server`

**Solutions**:
1. Check DATABASE_URL in `.env`
2. Verify database is running
3. Test connection: `python scripts/test_supabase_connection.py`
4. Check firewall settings

### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
pip install -r requirements.txt
```

### Redis Connection Failed

**Warning**: `Redis connection failed. Caching disabled.`

**Solution**: This is non-critical. The app will work without caching, but performance may be slower.

### Slow Queries

**Issue**: API responses are slow

**Solutions**:
1. Enable Redis caching
2. Check database indexes
3. Optimize queries
4. Use connection pooling (already configured)

## Migration from Local to Supabase

If you're currently using local PostgreSQL and want to migrate to Supabase:

```bash
# Automated migration (recommended)
python scripts/migrate_to_supabase.py

# Or manual steps
python scripts/backup_env.py
python scripts/export_database.py
python scripts/update_config.py
python scripts/import_to_supabase.py
python scripts/verify_migration.py
```

📖 **Full Migration Guide**: [SUPABASE_MIGRATION_GUIDE.md](SUPABASE_MIGRATION_GUIDE.md)

## Team Collaboration

### Setting Up for Team Members

1. **Get credentials** from team lead:
   - Supabase database password
   - Redis URL
   - Gemini API key

2. **Update .env**:
   ```bash
   copy .env.example .env
   # Edit .env with provided credentials
   ```

3. **Test connection**:
   ```bash
   python scripts/test_supabase_connection.py
   ```

4. **Start development**:
   ```bash
   python run.py
   ```

### Sharing Database

All team members use the same Supabase database:
- No need to import data locally
- Changes are visible to all team members
- Consistent data across all machines

## Performance Optimization

### Connection Pooling

Already configured in `database.py`:
- Pool size: 10 connections
- Max overflow: 20 connections
- Connection timeout: 30 seconds
- Pre-ping enabled

### Caching Strategy

Redis caching for:
- Predictions: 1 hour TTL
- Recommendations: 30 minutes TTL
- Static data: 24 hours TTL

### Query Optimization

- Indexes on frequently queried columns
- Pagination for large result sets
- Batch operations where possible
- Connection pooling

## Monitoring

### Application Logs

Check logs for:
- API requests and responses
- Database queries
- Error messages
- Performance metrics

### Database Monitoring

Supabase Dashboard:
- https://supabase.com/dashboard/project/inhanxxglxnjbugppulg
- Monitor connections, queries, and performance

### Health Check

```bash
curl http://localhost:8000/health
```

## Additional Documentation

- [Supabase Migration Guide](SUPABASE_MIGRATION_GUIDE.md) - Complete migration guide
- [ML Integration](README_ML_INTEGRATION.md) - ML model integration
- [Production Guide](README_PRODUCTION.md) - Production deployment
- [API Documentation](API_DOCUMENTATION.md) - Detailed API docs

## Support

### Common Issues

1. **Connection timeout**: Check internet connection and DATABASE_URL
2. **Import errors**: Run `pip install -r requirements.txt`
3. **Redis warnings**: Non-critical, app works without caching
4. **Slow performance**: Enable Redis, check database indexes

### Getting Help

1. Check documentation in this README
2. Review error messages and logs
3. Check Supabase dashboard for database issues
4. Run verification scripts for diagnostics
5. Contact team lead for credentials/access

## License

[Your License Here]

## Contributors

[Your Team Members Here]
