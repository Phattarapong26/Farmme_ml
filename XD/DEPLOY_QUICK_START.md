# Quick Start: Deploy to Render

## 1. Push to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

## 2. Get Supabase URL

Go to Supabase → Settings → Database → Copy **Connection pooling** URL

Example:
```
postgresql://postgres.xxxxx:password@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

## 3. Deploy on Render

1. Go to https://render.com
2. New + → Web Service
3. Connect GitHub repo
4. Configure:
   - **Build**: `cd backend && pip install -r requirements.txt`
   - **Start**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `DATABASE_URL` = (Supabase URL from step 2)
   - `GEMINI_API_KEY` = (Your Gemini key)
6. Click **Create Web Service**

## 4. Wait & Test

Wait 5-10 minutes, then visit:
```
https://your-app.onrender.com/health
https://your-app.onrender.com/docs
```

## 5. Update Frontend

```typescript
// frontend/.env
VITE_API_BASE_URL=https://your-app.onrender.com
```

Done! 🎉
