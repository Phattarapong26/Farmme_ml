# 🚨 Quick Fix for 404 Errors

## Problem
Frontend getting 404 errors for ML endpoints:
- `GET /api/v2/forecast/price-history` → 404
- `POST /api/v2/model/predict-price-forecast` → 404

## 🚀 Immediate Solutions (Pick One)

### Option 1: Use Working Test Server (Fastest)
```bash
cd @backend
python simple_server_test.py
```
✅ This will work immediately and provide all needed endpoints

### Option 2: Use Minimal Server
```bash
cd @backend
python minimal_main.py
```
✅ This tests just the routers without full app complexity

### Option 3: Fix Main Server
```bash
cd @backend
python fix_404_step_by_step.py
```
✅ This guides you through systematic debugging

## 🔍 Quick Diagnosis

### Test 1: Check if routers can be imported
```bash
cd @backend
python -c "
from app.routers import forecast, model
from app.main import app
print('✅ All imports OK')
print(f'Routes: {len([r for r in app.routes if hasattr(r, \"path\")])}')
"
```

### Test 2: Check server startup
```bash
cd @backend
python -m uvicorn app.main:app --reload --log-level debug
```
Look for: `✅ Forecast router loaded` and `✅ ML Model router loaded`

### Test 3: Check available endpoints
Visit: http://localhost:8000/docs

## 🛠 Common Fixes

### Fix 1: Restart Server
```bash
# Stop server (Ctrl+C)
# Clear cache
rm -rf __pycache__ app/__pycache__
# Restart
python -m uvicorn app.main:app --reload
```

### Fix 2: Check Dependencies
```bash
cd @backend
pip install -r requirements.txt
```

### Fix 3: Manual Router Registration
Add to `app/main.py` after line 175:
```python
# Manual router registration (temporary fix)
from app.routers.forecast import router as forecast_router
from app.routers.model import router as model_router

app.include_router(forecast_router)
app.include_router(model_router)
```

## 📋 Files Created for Debugging

1. **`simple_server_test.py`** - Working test server
2. **`minimal_main.py`** - Minimal version of main server
3. **`debug_routes.py`** - Route debugging tool
4. **`fix_404_step_by_step.py`** - Step-by-step fix guide
5. **`test_endpoints_direct.py`** - Direct endpoint testing

## 🎯 Expected Endpoints

After fix, these should work:
- ✅ `GET /api/v2/forecast/provinces`
- ✅ `GET /api/v2/forecast/crops`
- ✅ `GET /api/v2/forecast/price-history?province=X&crop_type=Y&days=Z`
- ✅ `POST /api/v2/model/predict-price-forecast`

## 🚀 Test Commands

```bash
# Test provinces
curl "http://localhost:8000/api/v2/forecast/provinces"

# Test crops
curl "http://localhost:8000/api/v2/forecast/crops"

# Test price history
curl "http://localhost:8000/api/v2/forecast/price-history?province=เชียงใหม่&crop_type=พริก&days=90"

# Test ML prediction
curl -X POST "http://localhost:8000/api/v2/model/predict-price-forecast" \
  -H "Content-Type: application/json" \
  -d '{"province":"เชียงใหม่","crop_type":"พริก","days_ahead":30}'
```

## ⚡ Emergency Workaround

If nothing else works, use the simple test server:

1. **Stop main server** (Ctrl+C)
2. **Start test server**: `python simple_server_test.py`
3. **Test frontend** - should work immediately
4. **Fix main server** while test server handles requests

The test server provides all the same endpoints with working data.

## 🔧 Root Cause Analysis

The 404 errors are likely caused by:
1. **Router not registered** in main.py
2. **Import errors** preventing router loading
3. **Path conflicts** with existing routes
4. **Server not restarted** after code changes

## ✅ Success Indicators

You'll know it's fixed when:
- Server logs show: `✅ Forecast router loaded` and `✅ ML Model router loaded`
- http://localhost:8000/docs shows all API v2 endpoints
- Frontend stops getting 404 errors
- All test commands return 200 OK

## 📞 If Still Stuck

1. **Use simple_server_test.py** as working solution
2. **Check server logs** for detailed error messages
3. **Run debug_routes.py** to see what's registered
4. **Compare working test server** with main server

The simple test server proves the endpoint logic works, so any remaining issues are just configuration problems in the main server.