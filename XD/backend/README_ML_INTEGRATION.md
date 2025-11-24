# ML Integration - Troubleshooting 404 Errors

## 🚨 Problem
Frontend is getting 404 errors for the new ML endpoints:
- `GET /api/v2/forecast/price-history` → 404 Not Found
- `POST /api/v2/model/predict-price-forecast` → 404 Not Found

## 🔍 Diagnosis Steps

### Step 1: Test Simple Server
Run the simple test server to verify endpoints work:

```bash
cd @backend
python simple_server_test.py
```

This will start a minimal FastAPI server with just our endpoints. If this works, the issue is with the main server configuration.

### Step 2: Test Router Imports
Check if routers can be imported without errors:

```bash
cd @backend
python test_server_start.py
```

This will test all imports and show which routes are registered.

### Step 3: Check Main Server
If the simple server works but main server doesn't, there might be:
1. Import errors in the main app
2. Router registration issues
3. Path conflicts

## 🛠 Quick Fixes

### Fix 1: Restart Server with Verbose Logging
```bash
cd @backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

Look for these messages in the logs:
- `✅ Forecast router loaded`
- `✅ ML Model router loaded`

### Fix 2: Check Available Routes
Visit http://localhost:8000/docs to see all registered endpoints.

### Fix 3: Manual Router Registration
If routers aren't loading, add them manually to `app/main.py`:

```python
# Add after other router imports
from app.routers.forecast import router as forecast_router
from app.routers.model import router as model_router

# Add after app creation
app.include_router(forecast_router)
app.include_router(model_router)
```

### Fix 4: Alternative Server Start
Try starting with the production script:

```bash
cd @backend
./start.sh
```

## 🧪 Testing Endpoints

### Test Price History
```bash
curl "http://localhost:8000/api/v2/forecast/price-history?province=เชียงใหม่&crop_type=พริก&days=90"
```

### Test ML Prediction
```bash
curl -X POST "http://localhost:8000/api/v2/model/predict-price-forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "province": "เชียงใหม่",
    "crop_type": "พริก",
    "crop_category": "ผักผล",
    "days_ahead": 30
  }'
```

### Test Provinces
```bash
curl "http://localhost:8000/api/v2/forecast/provinces"
```

### Test Crops
```bash
curl "http://localhost:8000/api/v2/forecast/crops"
```

## 🔧 Common Issues & Solutions

### Issue 1: Import Errors
**Symptoms**: Server fails to start, import errors in logs
**Solution**: Check Python path and dependencies

```bash
cd @backend
pip install -r requirements.txt
python -c "from app.routers import model, forecast; print('✅ Imports OK')"
```

### Issue 2: Router Not Registered
**Symptoms**: Server starts but endpoints return 404
**Solution**: Check router registration in main.py

```python
# Verify this exists in app/main.py
routers = [
    # ... other routers ...
    (forecast.router, "Forecast"),
    (model.router, "ML Model")
]
```

### Issue 3: Path Conflicts
**Symptoms**: Some endpoints work, others don't
**Solution**: Check for duplicate paths or prefix conflicts

### Issue 4: Database Connection Issues
**Symptoms**: Endpoints return 500 errors
**Solution**: Check database connection

```bash
cd @backend
python -c "from database import engine; engine.connect(); print('✅ DB OK')"
```

## 🚀 Alternative: Use Simple Server Temporarily

If the main server has issues, you can use the simple test server temporarily:

1. **Stop the main server**
2. **Start simple server**: `python simple_server_test.py`
3. **Test frontend** - it should work with the simple server
4. **Fix main server** while simple server handles requests

## 📋 Verification Checklist

- [ ] Simple test server works (`python simple_server_test.py`)
- [ ] Router imports work (`python test_server_start.py`)
- [ ] Main server starts without errors
- [ ] All endpoints return 200 (not 404)
- [ ] Frontend can fetch data successfully
- [ ] ML predictions work (even with fallback)

## 🔄 Step-by-Step Recovery

1. **Test simple server first**:
   ```bash
   python simple_server_test.py
   ```

2. **If simple server works, test main server**:
   ```bash
   python -m uvicorn app.main:app --reload --port 8001
   ```

3. **Compare available routes**:
   - Simple server: http://localhost:8000/docs
   - Main server: http://localhost:8001/docs

4. **Fix differences** in main server configuration

5. **Switch back to main server** once fixed

## 📞 Support

If issues persist:

1. **Check server logs** for detailed error messages
2. **Run all test scripts** to identify the exact problem
3. **Compare working simple server** with main server
4. **Verify all file paths** and imports are correct

The simple test server proves that the endpoint logic works, so any 404 errors are configuration issues in the main server.