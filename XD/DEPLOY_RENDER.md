# Deploy Backend to Render (Free Tier) with Supabase

## Prerequisites

- ✅ Supabase database (already have)
- ✅ GitHub account
- ✅ Render account (https://render.com)
- ✅ Gemini API key

## Step 1: Prepare Your Repository

### 1.1 Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Get Supabase Connection String

### 2.1 Go to Supabase Dashboard
1. Open your Supabase project
2. Go to **Settings** → **Database**
3. Find **Connection string** section
4. Copy the **Connection pooling** URL (recommended for serverless)

Example:
```
postgresql://postgres.[project-ref]:[password]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

### 2.2 Important Notes
- Use **Connection pooling** (port 6543) not direct connection (port 5432)
- Replace `[password]` with your actual database password
- Keep this URL safe!

## Step 3: Deploy to Render

### 3.1 Create New Web Service

1. Go to https://render.com/dashboard
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Select your repository

### 3.2 Configure Service

**Basic Settings:**
- **Name**: `farmtime-backend`
- **Region**: Singapore (closest to Supabase)
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Environment**: `Python 3`
- **Build Command**: 
  ```bash
  cd backend && pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### 3.3 Set Environment Variables

Click **Advanced** → **Add Environment Variable**

Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `postgresql://postgres.[project-ref]:[password]@...` | From Supabase (Step 2) |
| `GEMINI_API_KEY` | `your_gemini_api_key` | Your Gemini API key |
| `REDIS_URL` | `redis://localhost:6379` | Optional (for caching) |
| `ENVIRONMENT` | `production` | Environment flag |
| `PYTHON_VERSION` | `3.11.0` | Python version |

### 3.4 Deploy

1. Click **Create Web Service**
2. Wait for deployment (5-10 minutes)
3. Render will:
   - Clone your repo
   - Install dependencies
   - Start your FastAPI app

## Step 4: Verify Deployment

### 4.1 Check Health Endpoint

Once deployed, visit:
```
https://farmtime-backend.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2024-..."
}
```

### 4.2 Check API Docs

Visit:
```
https://farmtime-backend.onrender.com/docs
```

Should show FastAPI Swagger UI

### 4.3 Test API Endpoint

```bash
curl https://farmtime-backend.onrender.com/api/v2/forecast/provinces
```

## Step 5: Update Frontend

### 5.1 Update API Base URL

In `frontend/src/` files, update:

```typescript
// Before (local)
const API_BASE_URL = 'http://localhost:8000';

// After (production)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://farmtime-backend.onrender.com';
```

### 5.2 Create `.env` file

```bash
# frontend/.env
VITE_API_BASE_URL=https://farmtime-backend.onrender.com
```

### 5.3 Update CORS in Backend

In `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-frontend-domain.vercel.app",  # Add your frontend URL
        "https://farmtime-backend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 6: Important Notes

### 6.1 Free Tier Limitations

⚠️ **Render Free Tier**:
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds (cold start)
- 750 hours/month free
- Shared CPU/RAM

### 6.2 Cold Start Solution

Add a health check or use a service like:
- UptimeRobot (free)
- Cron-job.org (free)

To ping your API every 10 minutes:
```
https://farmtime-backend.onrender.com/health
```

### 6.3 Model Files

⚠️ **Large Model Files**:
- Render has limited disk space on free tier
- If your model files are large (>500MB), consider:
  1. Store models in cloud storage (S3, Google Cloud Storage)
  2. Download on startup
  3. Use smaller models

### 6.4 Database Connection

✅ **Supabase Connection Pooling**:
- Always use connection pooling (port 6543)
- Handles serverless connections better
- Prevents "too many connections" errors

## Step 7: Monitoring

### 7.1 View Logs

In Render Dashboard:
1. Go to your service
2. Click **Logs** tab
3. See real-time logs

### 7.2 Check Metrics

- **Events**: Deployment history
- **Metrics**: CPU, Memory usage
- **Shell**: Access to container shell

## Troubleshooting

### Issue 1: "Application failed to respond"

**Solution**: Check logs for errors
```bash
# Common issues:
- Missing environment variables
- Database connection failed
- Port binding error
```

### Issue 2: "Too many database connections"

**Solution**: Use Supabase connection pooling
```
# Use this (pooler):
postgresql://...@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

# Not this (direct):
postgresql://...@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
```

### Issue 3: "Module not found"

**Solution**: Check `requirements.txt`
```bash
# Make sure all dependencies are listed
pip freeze > backend/requirements.txt
```

### Issue 4: Cold start too slow

**Solution**: 
1. Use UptimeRobot to keep alive
2. Optimize startup (lazy load models)
3. Consider paid tier ($7/month)

## Step 8: Optional Upgrades

### 8.1 Custom Domain

1. Go to **Settings** → **Custom Domain**
2. Add your domain
3. Update DNS records

### 8.2 Redis (Caching)

Use Upstash Redis (free tier):
1. Sign up at https://upstash.com
2. Create Redis database
3. Copy connection URL
4. Update `REDIS_URL` in Render

### 8.3 Background Workers

For long-running tasks:
1. Create separate worker service
2. Use Celery + Redis
3. Deploy as background worker on Render

## Summary

✅ **What you have now**:
- Backend deployed on Render (free)
- Connected to Supabase database
- API accessible at `https://farmtime-backend.onrender.com`
- Auto-deploys on git push

✅ **Next steps**:
1. Deploy frontend to Vercel/Netlify
2. Update frontend API URL
3. Test end-to-end
4. Set up monitoring

🎉 **Your backend is now live!**
