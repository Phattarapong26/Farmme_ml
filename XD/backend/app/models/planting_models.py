# -*- coding: utf-8 -*-
"""
Pydantic models for planting-related requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PlantingDateRequest(BaseModel):
    """Request model for planting date recommendations"""
    crop_type: str = Field(..., description="Type of crop to plant")
    province: str = Field(..., description="Province where to plant")
    growth_days: int = Field(..., description="Number of days for crop to grow")
    planting_area_rai: Optional[float] = Field(10.0, description="Planting area in rai")
    start_date: Optional[str] = Field(None, description="Start date for recommendations (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date for recommendations (YYYY-MM-DD)")
    top_n: Optional[int] = Field(10, description="Number of top recommendations to return")
    min_price_threshold: Optional[float] = Field(10.0, description="Minimum price threshold")

class PlantingRecommendation(BaseModel):
    """Individual planting recommendation"""
    planting_date: str
    harvest_date: str
    predicted_price: float
    price: float  # Alternative field name
    confidence: float
    risk_score: float
    planting_score: float
    recommendation: str
    season: str
    weather_suitability: float
    market_timing: float
    total_score: float
    rainfall: float

class RecommendationLevel(BaseModel):
    """Recommendation level analysis"""
    level: str
    text: str
    expected_harvest_date: str
    expected_harvest_month: str
    optimal_planting_month: str
    best_harvest_month: str
    warning_planting_month: str
    worst_harvest_month: str

class PriceAnalysis(BaseModel):
    """Price analysis data"""
    predicted_price: float
    best_price: float
    worst_price: float
    average_price: float
    price_diff_from_best_percent: float

class MonthlyTrend(BaseModel):
    """Monthly price trend data point"""
    month: str
    average_price: float

class TimelineData(BaseModel):
    """Timeline data point"""
    date: str
    average_price: float
    type: str  # "historical" or "ml_forecast"

class HistoricalData(BaseModel):
    """Historical price data point"""
    month: str
    price: float

class ForecastData(BaseModel):
    """Forecast data point"""
    month: str
    price: float

class PlantingDateResponse(BaseModel):
    """Response model for planting date recommendations"""
    success: bool
    recommendations: List[PlantingRecommendation]
    crop_type: str
    province: str
    growth_days: int
    statistics: Dict[str, Any]
    model_info: Dict[str, Any]
    generated_at: str
    recommendation: RecommendationLevel
    price_analysis: PriceAnalysis
    monthly_price_trend: List[MonthlyTrend]
    combined_timeline: List[TimelineData]
    historical_prices: List[HistoricalData]
    ml_forecast: List[ForecastData]
    total_scenarios_analyzed: int