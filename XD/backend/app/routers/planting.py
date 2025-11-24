"""
Planting Window API Router
Model B - Planting Window Prediction
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from model_b_wrapper import get_model_b

router = APIRouter(prefix="/api/planting", tags=["planting"])


class PlantingWindowRequest(BaseModel):
    """Request for planting window prediction"""
    planting_date: str = Field(..., description="Date to plant (YYYY-MM-DD)")
    province: str = Field(..., description="Province name (Thai)")
    soil_type: Optional[str] = Field(None, description="Soil type (e.g., ดินร่วน, ดินเหนียว)")
    soil_ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH (0-14)")
    soil_nutrients: Optional[float] = Field(None, ge=0, le=100, description="Soil nutrients (0-100)")
    days_to_maturity: Optional[int] = Field(None, ge=30, le=365, description="Days to maturity")


class PlantingCalendarRequest(BaseModel):
    """Request for planting calendar"""
    province: str = Field(..., description="Province name (Thai)")
    crop_type: str = Field(default="พริก", description="Crop type")
    months_ahead: int = Field(default=12, ge=1, le=24, description="Months to analyze")
    soil_type: Optional[str] = Field(None, description="Soil type")
    soil_ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH")
    soil_nutrients: Optional[float] = Field(None, ge=0, le=100, description="Soil nutrients")


@router.post("/window")
async def predict_planting_window(request: PlantingWindowRequest):
    """
    Predict if a specific date is good for planting
    
    Returns:
        - is_good_window: Boolean indicating if it's a good time to plant
        - confidence: Confidence score (0-1)
        - recommendation: Human-readable recommendation
        - reason: Explanation of the decision
        - weather: Weather data used for prediction
    """
    try:
        # Get Model B instance
        model_b = get_model_b()
        
        # Note: New wrapper requires crop_type, using default 'พริก'
        result = model_b.predict_planting_window(
            crop_type='พริก',  # Default crop type
            province=request.province,
            planting_date=request.planting_date
        )
        
        return {
            'success': True,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calendar")
async def get_planting_calendar(request: PlantingCalendarRequest):
    """
    Get recommended planting windows for the next N months
    
    Returns:
        - monthly_predictions: Prediction for each month
        - good_windows: List of good planting windows
        - best_windows: Best consecutive planting periods
        - summary: Human-readable summary
    """
    try:
        from datetime import datetime, timedelta
        
        # Get Model B instance
        model_b = get_model_b()
        
        # Generate predictions for each month
        monthly_predictions = []
        good_windows = []
        
        current_date = datetime.now()
        
        for month_offset in range(request.months_ahead):
            # Get first day of each month
            target_date = current_date + timedelta(days=30 * month_offset)
            date_str = target_date.strftime('%Y-%m-%d')
            
            # Predict for this date
            result = model_b.predict_planting_window(
                crop_type=request.crop_type,
                province=request.province,
                planting_date=date_str
            )
            
            monthly_predictions.append({
                'month': target_date.strftime('%Y-%m'),
                'date': date_str,
                'is_good_window': result['is_good_window'],
                'confidence': result['confidence'],
                'recommendation': result['recommendation']
            })
            
            if result['is_good_window']:
                good_windows.append({
                    'month': target_date.strftime('%Y-%m'),
                    'confidence': result['confidence']
                })
        
        # Find best consecutive windows
        best_windows = []
        current_window = []
        
        for pred in monthly_predictions:
            if pred['is_good_window']:
                current_window.append(pred['month'])
            else:
                if len(current_window) >= 2:
                    best_windows.append({
                        'start': current_window[0],
                        'end': current_window[-1],
                        'duration_months': len(current_window)
                    })
                current_window = []
        
        # Add last window if exists
        if len(current_window) >= 2:
            best_windows.append({
                'start': current_window[0],
                'end': current_window[-1],
                'duration_months': len(current_window)
            })
        
        # Generate summary
        good_count = len(good_windows)
        total_count = len(monthly_predictions)
        
        if good_count == 0:
            summary = f"ไม่พบช่วงเวลาที่เหมาะสมสำหรับการปลูก{request.crop_type}ใน{request.province}ในช่วง {request.months_ahead} เดือนข้างหน้า"
        elif good_count == total_count:
            summary = f"ทุกเดือนเหมาะสมสำหรับการปลูก{request.crop_type}ใน{request.province}"
        else:
            summary = f"พบ {good_count} เดือนที่เหมาะสมจาก {total_count} เดือน ({good_count/total_count*100:.0f}%) สำหรับการปลูก{request.crop_type}ใน{request.province}"
        
        return {
            'success': True,
            'monthly_predictions': monthly_predictions,
            'good_windows': good_windows,
            'best_windows': best_windows,
            'summary': summary,
            'crop_type': request.crop_type,
            'province': request.province
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check if Model B is loaded and ready"""
    try:
        model_b = get_model_b()
        return {
            "status": "healthy" if model_b.model is not None else "degraded",
            "model_loaded": model_b.model is not None,
            "model_type": "XGBoost",
            "model_path": str(model_b.model_path) if model_b.model_path else None,
            "version": "1.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "model_loaded": False,
            "error": str(e)
        }
