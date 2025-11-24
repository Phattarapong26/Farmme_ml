# AgriML Backend API

A FastAPI-based backend for agricultural prediction and chat assistance using machine learning and Google's Gemini AI.

## Features

- **ML Predictions**: Crop price predictions using Random Forest model
- **Chat Assistant**: AI-powered agricultural advice using Gemini
- **Database Integration**: PostgreSQL database for storing predictions and chat sessions
- **RESTful API**: Complete API endpoints for frontend integration

## Database Configuration

The application is configured to use a local PostgreSQL database:

```
DATABASE_URL="postgresql://postgres:592954@localhost:4955/Evena?schema=public"
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   export DATABASE_URL="postgresql://postgres:592954@localhost:4955/Evena?schema=public"
   export GEMINI_API_KEY="your_gemini_api_key"
   ```

3. **Start the Server**:
   ```bash
   ./start.sh
   # or
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /predict` - Make crop predictions
- `POST /chat` - Chat with AI assistant
- `POST /forecast/6months` - 6-month forecast

### Database Endpoints
- `GET /predictions` - Get recent predictions
- `GET /chat-sessions` - Get chat session history
- `GET /chat-sessions/{session_id}` - Get specific chat session

### ML Endpoints
- `POST /predict/probabilities` - Get prediction probabilities
- `GET /explain/features` - Feature importance analysis
- `POST /recommend/crop` - Crop recommendations
- `POST /alert/risk` - Risk assessment

## Database Schema

The application creates the following tables:
- `crop_predictions` - Stores ML prediction results
- `chat_sessions` - Stores chat interactions
- `forecast_data` - Stores forecast data

## Docker Support

Build and run with Docker:

```bash
docker build -t agriml-backend .
docker run -p 8000:8000 agriml-backend
```

## Requirements

- Python 3.11+
- PostgreSQL database
- Google Gemini API key
- ML model file (`model/random_forest_model.pkl`)
