# Design Document

## Overview

Dashboard Overview เป็นหน้าแสดงภาพรวมข้อมูลเชิงลึกของจังหวัด ออกแบบให้มีความสวยงาม ใช้งานง่าย และมีประสิทธิภาพสูง โดยใช้ CanvasJS สำหรับ charts, MagicUI components สำหรับ UI, Ripple effect สำหรับพื้นหลัง และ Redis caching สำหรับเพิ่มความเร็ว

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  DashboardOverview.tsx                               │   │
│  │  - Province Selector                                 │   │
│  │  - Statistics Cards (MagicUI)                        │   │
│  │  - CanvasJS Charts                                   │   │
│  │  - Ripple Background                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓ API Calls                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /api/dashboard/overview                             │   │
│  │  - Redis Cache Check                                 │   │
│  │  - Database Query                                    │   │
│  │  - Data Aggregation                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│         ↓ Cache                    ↓ Query                   │
│  ┌─────────────┐           ┌──────────────┐                 │
│  │    Redis    │           │  PostgreSQL  │                 │
│  └─────────────┘           └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: React, TypeScript, TanStack Query, CanvasJS, MagicUI (shadcn)
- **Backend**: FastAPI, Python
- **Database**: PostgreSQL
- **Caching**: Redis
- **Styling**: Tailwind CSS


## Components and Interfaces

### Frontend Components

#### 1. DashboardOverview.tsx (Main Page)
```typescript
interface DashboardOverviewProps {
  // No props needed - uses context for province selection
}

interface DashboardData {
  province: string;
  statistics: ProvinceStatistics;
  priceHistory: PriceDataPoint[];
  weatherData: WeatherDataPoint[];
  cropDistribution: CropDistribution[];
}

interface ProvinceStatistics {
  avgPrice: number;
  totalCropTypes: number;
  currentTemp: number;
  currentRainfall: number;
  mostProfitableCrop: string;
  mostProfitablePrice: number;
}
```

#### 2. ProvinceSelector Component
```typescript
interface ProvinceSelectorProps {
  selectedProvince: string | null;
  onProvinceChange: (province: string) => void;
  provinces: string[];
}
```

#### 3. StatisticsCard Component (MagicUI)
```typescript
interface StatisticsCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number;
}
```

#### 4. ChartContainer Component
```typescript
interface ChartContainerProps {
  title: string;
  children: React.ReactNode;
  isLoading?: boolean;
}
```

#### 5. RippleBackground Component
```typescript
interface RippleBackgroundProps {
  color?: string;
  opacity?: number;
}
```

### Backend API Endpoints

#### GET /api/dashboard/overview
```python
@router.get("/dashboard/overview")
async def get_dashboard_overview(
    province: str,
    days_back: int = 30,
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """
    Get comprehensive dashboard data for a province
    
    Parameters:
    - province: Province name
    - days_back: Number of days to look back for historical data (default: 30)
    
    Returns: DashboardOverviewResponse with 9 datasets integrated
    """
```

**Response Schema (Enhanced):**
```json
{
  "success": true,
  "province": "กรุงเทพมหานคร",
  "statistics": {
    "avg_price": 45.50,
    "price_by_market_type": {
      "ซุปเปอร์มาร์เก็ต": 30.98,
      "พ่อค้าคนกลาง": 13.19,
      "ตลาดสด": 20.50
    },
    "total_crop_types": 25,
    "most_profitable_crop": "มะเขือเทศ",
    "most_profitable_profit": 265179.24,
    "avg_roi": 500.0,
    "avg_margin": 90.31,
    "current_temp": 24.6,
    "current_rainfall": 0.0,
    "current_humidity": 73.0,
    "drought_index": 97.7,
    "total_farmers": 39165,
    "avg_farm_size": 5.0,
    "avg_yield_efficiency": 1.51,
    "avg_farm_skill": 0.546,
    "tech_adoption_rate": 0.226,
    "fuel_price": 39.48,
    "fertilizer_price": 884.34,
    "vegetable_demand_index": 1.124,
    "inflation_rate": 1.60,
    "total_population": 5400000,
    "farmers_count": 39165,
    "avg_income": 239889,
    "rural_share": 0.179
  },
  "price_history": [
    {
      "date": "2023-11-01",
      "crop_type": "คะน้า",
      "price": 30.98,
      "market_type": "ซุปเปอร์มาร์เก็ต",
      "bid_price": 29.74,
      "ask_price": 32.22,
      "spread_pct": 8.0
    }
  ],
  "weather_data": [
    {
      "date": "2023-11-01",
      "temperature": 24.6,
      "rainfall": 0.0,
      "humidity": 73.0,
      "drought_index": 97.7
    }
  ],
  "crop_distribution": [
    {
      "crop_type": "คะน้า",
      "crop_category": "ผักใบ",
      "count": 150,
      "percentage": 25.5,
      "avg_compatibility": 0.738
    }
  ],
  "profitability": [
    {
      "crop_type": "คะน้า",
      "avg_profit": 265179.24,
      "avg_roi": 500.0,
      "avg_margin": 90.31,
      "total_revenue": 293621.38,
      "total_cost": 28442.14
    }
  ],
  "yield_efficiency": [
    {
      "farm_skill": 0.546,
      "yield_efficiency": 1.51,
      "tech_adoption": 0.226,
      "crop_type": "คะน้า"
    }
  ],
  "economic_indicators": [
    {
      "date": "2023-11-01",
      "fuel_price": 39.48,
      "fertilizer_price": 884.34,
      "vegetable_demand_index": 1.124,
      "inflation_rate": 1.60,
      "gdp_growth": 2.72
    }
  ],
  "farmer_demographics": {
    "total_farmers": 39165,
    "commercial_farmers": 35000,
    "subsistence_farmers": 4165,
    "avg_land_size": 5.0,
    "avg_capital": 138144,
    "avg_experience": 7
  },
  "crop_compatibility": [
    {
      "crop_type": "คะน้า",
      "crop_category": "ผักใบ",
      "compatibility_score": 0.738,
      "region": "central"
    }
  ],
  "soil_distribution": [
    {
      "soil_type": "ดินร่วน",
      "count": 120,
      "percentage": 45.2,
      "suitable_crops": ["คะน้า", "กวางตุ้ง", "ผักบุ้ง"]
    },
    {
      "soil_type": "ดินเหนียว",
      "count": 81,
      "percentage": 30.5,
      "suitable_crops": ["มะเขือเทศ", "พริก"]
    }
  ],
  "success_rate_by_soil": [
    {
      "crop_type": "คะน้า",
      "soil_type": "ดินร่วน",
      "success_rate": 0.839,
      "avg_yield_efficiency": 1.51
    }
  ],
  "insights": [
    {
      "type": "soil",
      "title": "ความเหมาะสมของดิน",
      "message": "ดินร่วนในกรุงเทพมหานครเหมาะสมกับการปลูกคะน้า กวางตุ้ง และผักบุ้ง",
      "details": [
        "ดินร่วนมีการระบายน้ำดี เหมาะกับพืชที่ต้องการน้ำสูง",
        "คะแนนความเหมาะสม: 0.738",
        "อัตราความสำเร็จ: 83.9%"
      ]
    }
  ],
  "cached": false,
  "timestamp": "2024-01-01T12:00:00Z"
}
```


## Data Models

### Frontend Data Models

```typescript
// Province Statistics (Enhanced)
interface ProvinceStatistics {
  // Price & Market
  avgPrice: number;
  priceByMarketType: { [key: string]: number };
  totalCropTypes: number;
  mostProfitableCrop: string;
  mostProfitableProfit: number;
  avgROI: number;
  avgMargin: number;
  
  // Weather
  currentTemp: number;
  currentRainfall: number;
  currentHumidity: number;
  droughtIndex: number;
  
  // Farming
  totalFarmers: number;
  avgFarmSize: number;
  avgYieldEfficiency: number;
  avgFarmSkill: number;
  techAdoptionRate: number;
  
  // Economic
  fuelPrice: number;
  fertilizerPrice: number;
  vegetableDemandIndex: number;
  inflationRate: number;
  
  // Population
  totalPopulation: number;
  farmersCount: number;
  avgIncome: number;
  ruralShare: number;
}

// Price Data Point (Enhanced)
interface PriceDataPoint {
  date: string;
  cropType: string;
  price: number;
  marketType: string;
  bidPrice: number;
  askPrice: number;
  spreadPct: number;
}

// Weather Data Point (Enhanced)
interface WeatherDataPoint {
  date: string;
  temperature: number;
  rainfall: number;
  humidity: number;
  droughtIndex: number;
}

// Crop Distribution
interface CropDistribution {
  cropType: string;
  cropCategory: string;
  count: number;
  percentage: number;
  avgCompatibility: number;
}

// Profitability Data
interface CropProfitability {
  cropType: string;
  avgProfit: number;
  avgROI: number;
  avgMargin: number;
  totalRevenue: number;
  totalCost: number;
}

// Yield Efficiency Data
interface YieldEfficiencyPoint {
  farmSkill: number;
  yieldEfficiency: number;
  techAdoption: number;
  cropType: string;
}

// Economic Indicators
interface EconomicIndicators {
  date: string;
  fuelPrice: number;
  fertilizerPrice: number;
  vegetableDemandIndex: number;
  inflationRate: number;
  gdpGrowth: number;
}

// Farmer Demographics
interface FarmerDemographics {
  totalFarmers: number;
  commercialFarmers: number;
  subsistenceFarmers: number;
  avgLandSize: number;
  avgCapital: number;
  avgExperience: number;
}

// Crop Compatibility
interface CropCompatibility {
  cropType: string;
  cropCategory: string;
  compatibilityScore: number;
  region: string;
}

// Soil Distribution
interface SoilDistribution {
  soilType: string;
  count: number;
  percentage: number;
  suitableCrops: string[];
}

// Success Rate by Soil
interface SuccessRateBySoil {
  cropType: string;
  soilType: string;
  successRate: number;
  avgYieldEfficiency: number;
}

// Insights
interface Insight {
  type: 'soil' | 'weather' | 'economic' | 'success' | 'profitability';
  title: string;
  message: string;
  details?: string[];
  data?: any;
}

// Dashboard Data (Enhanced)
interface DashboardData {
  province: string;
  statistics: ProvinceStatistics;
  priceHistory: PriceDataPoint[];
  weatherData: WeatherDataPoint[];
  cropDistribution: CropDistribution[];
  profitability: CropProfitability[];
  yieldEfficiency: YieldEfficiencyPoint[];
  economicIndicators: EconomicIndicators[];
  farmerDemographics: FarmerDemographics;
  cropCompatibility: CropCompatibility[];
  soilDistribution: SoilDistribution[];
  successRateBySoil: SuccessRateBySoil[];
  insights: Insight[];
  cached: boolean;
  timestamp: string;
}
```

### Backend Data Models

```python
from pydantic import BaseModel
from typing import List
from datetime import datetime

class ProvinceStatistics(BaseModel):
    avg_price: float
    total_crop_types: int
    current_temp: float
    current_rainfall: float
    most_profitable_crop: str
    most_profitable_price: float

class PriceDataPoint(BaseModel):
    date: str
    crop_type: str
    price: float

class WeatherDataPoint(BaseModel):
    date: str
    temperature: float
    rainfall: float

class CropDistribution(BaseModel):
    crop_type: str
    count: int
    percentage: float

class DashboardOverviewResponse(BaseModel):
    success: bool
    province: str
    statistics: ProvinceStatistics
    price_history: List[PriceDataPoint]
    weather_data: List[WeatherDataPoint]
    crop_distribution: List[CropDistribution]
    cached: bool
    timestamp: datetime
```


## Redis Caching Strategy

### Cache Key Structure
```
dashboard:overview:{province}
```

### Cache TTL
- **Default TTL**: 5 minutes (300 seconds)
- **Rationale**: Balance between data freshness and database load

### Caching Flow

```python
async def get_dashboard_data(province: str, db: Session, redis_client):
    # 1. Generate cache key
    cache_key = f"dashboard:overview:{province}"
    
    # 2. Try to get from cache
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    # 3. If not in cache, query database
    data = await query_database(province, db)
    
    # 4. Store in cache with TTL
    await redis_client.setex(
        cache_key,
        300,  # 5 minutes
        json.dumps(data)
    )
    
    return data
```

### Cache Invalidation
- **Time-based**: Automatic expiration after 5 minutes
- **Manual**: When new data is imported to database
- **Fallback**: If Redis is unavailable, query database directly


## Chart Designs (CanvasJS)

### 1. Price Trend & Market Analysis (Multi-Line Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "แนวโน้มราคาพืชตามประเภทตลาด (30 วัน)" },
  axisX: { title: "วันที่", valueFormatString: "DD MMM" },
  axisY: { title: "ราคา (บาท/กก.)", prefix: "฿" },
  toolTip: { shared: true },
  data: [
    { type: "line", name: "ซุปเปอร์มาร์เก็ต", showInLegend: true, dataPoints: [] },
    { type: "line", name: "พ่อค้าคนกลาง", showInLegend: true, dataPoints: [] },
    { type: "line", name: "ตลาดสด", showInLegend: true, dataPoints: [] }
  ]
}
```

### 2. Weather & Drought Index (Combination Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "สภาพอากาศและดัชนีความแห้งแล้ง (30 วัน)" },
  axisX: { title: "วันที่", valueFormatString: "DD MMM" },
  axisY: { title: "อุณหภูมิ (°C) / ความชื้น (%)", suffix: "" },
  axisY2: { title: "ฝน (มม.) / ดัชนีแห้งแล้ง", suffix: "" },
  data: [
    { type: "line", name: "อุณหภูมิ", showInLegend: true, dataPoints: [] },
    { type: "line", name: "ความชื้น", showInLegend: true, dataPoints: [] },
    { type: "column", name: "ปริมาณฝน", axisYType: "secondary", dataPoints: [] },
    { type: "line", name: "ดัชนีแห้งแล้ง", axisYType: "secondary", dataPoints: [] }
  ]
}
```

### 3. Crop Profitability Analysis (Bar Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "ผลกำไรเฉลี่ยต่อพืช (Top 10)" },
  axisX: { title: "ชนิดพืช" },
  axisY: { title: "กำไร (บาท)", prefix: "฿" },
  data: [{
    type: "bar",
    dataPoints: [
      { label: "มะเขือเทศ", y: 265179 },
      // ... more crops
    ]
  }]
}
```

### 4. Crop Distribution by Category (Doughnut Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "สัดส่วนการปลูกตามหมวดหมู่พืช" },
  data: [{
    type: "doughnut",
    startAngle: 60,
    innerRadius: "60%",
    indexLabel: "{label} - {y}%",
    dataPoints: [
      { y: 35.5, label: "ผักใบ" },
      { y: 28.3, label: "ผักผล" },
      { y: 20.2, label: "สมุนไพร" },
      { y: 16.0, label: "ผักอื่นๆ" }
    ]
  }]
}
```

### 5. Yield Efficiency vs Farm Skill (Scatter Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "ความสัมพันธ์ระหว่างทักษะเกษตรกรกับประสิทธิภาพผลผลิต" },
  axisX: { title: "ทักษะเกษตรกร (0-1)" },
  axisY: { title: "ประสิทธิภาพผลผลิต" },
  data: [{
    type: "scatter",
    markerSize: 8,
    dataPoints: [
      { x: 0.546, y: 1.51 },
      // ... more points
    ]
  }]
}
```

### 6. Economic Indicators Timeline (Multi-Line Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "ตัวชี้วัดเศรษฐกิจที่ส่งผลต่อการเกษตร (90 วัน)" },
  axisX: { title: "วันที่", valueFormatString: "DD MMM" },
  axisY: { title: "ค่าดัชนี" },
  data: [
    { type: "line", name: "ราคาน้ำมัน", showInLegend: true, dataPoints: [] },
    { type: "line", name: "ราคาปุ๋ย", showInLegend: true, dataPoints: [] },
    { type: "line", name: "ดัชนีความต้องการผัก", showInLegend: true, dataPoints: [] },
    { type: "line", name: "อัตราเงินเฟ้อ", showInLegend: true, dataPoints: [] }
  ]
}
```

### 7. Farmer Demographics (Column Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "ข้อมูลประชากรเกษตรกร" },
  axisX: { title: "ประเภท" },
  axisY: { title: "จำนวน" },
  data: [{
    type: "column",
    dataPoints: [
      { label: "เกษตรกรทั้งหมด", y: 39165 },
      { label: "วัยทำงาน", y: 3976433 },
      { label: "ประชากรรวม", y: 5400000 }
    ]
  }]
}
```

### 8. Crop Compatibility Heatmap (Column Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "ความเหมาะสมของพืชในจังหวัด (Top 15)" },
  axisX: { title: "ชนิดพืช", labelAngle: -45 },
  axisY: { title: "คะแนนความเหมาะสม", maximum: 1 },
  data: [{
    type: "column",
    color: "#10b981",
    dataPoints: [
      { label: "คะน้า", y: 0.738 },
      // ... more crops
    ]
  }]
}
```

### 9. ROI & Margin Analysis (Combination Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "วิเคราะห์ผลตอบแทนและกำไรขั้นต้น (Top 10 พืช)" },
  axisX: { title: "ชนิดพืช", labelAngle: -45 },
  axisY: { title: "ROI (%)" },
  axisY2: { title: "Margin (%)" },
  data: [
    { type: "column", name: "ROI", showInLegend: true, dataPoints: [] },
    { type: "line", name: "Margin", axisYType: "secondary", showInLegend: true, dataPoints: [] }
  ]
}
```

### 10. Soil Type Distribution (Pie Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "การกระจายประเภทดินในจังหวัด" },
  data: [{
    type: "pie",
    startAngle: 240,
    indexLabel: "{label} - {y}%",
    dataPoints: [
      { y: 45.2, label: "ดินร่วน" },
      { y: 30.5, label: "ดินเหนียว" },
      { y: 24.3, label: "ดินร่วนปนทราย" }
    ]
  }]
}
```

### 11. Success Rate by Crop & Soil (Grouped Bar Chart)
```javascript
{
  animationEnabled: true,
  theme: "light2",
  title: { text: "อัตราความสำเร็จตามชนิดพืชและประเภทดิน" },
  axisX: { title: "ชนิดพืช", labelAngle: -45 },
  axisY: { title: "อัตราความสำเร็จ (%)", maximum: 100 },
  data: [
    { type: "column", name: "ดินร่วน", showInLegend: true, dataPoints: [] },
    { type: "column", name: "ดินเหนียว", showInLegend: true, dataPoints: [] },
    { type: "column", name: "ดินร่วนปนทราย", showInLegend: true, dataPoints: [] }
  ]
}
```


## UI/UX Design

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│                        Navbar                                │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Ripple Background                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Province Selector + Title                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │AvgPrice│ │Farmers │ │Weather │ │TopCrop │ │AvgROI  │   │
│  │ 45.5฿  │ │ 39,165 │ │ 32.5°C │ │มะเขือฯ │ │ 500%   │   │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘   │
│                                                              │
│  ┌─────────────────────────┐ ┌─────────────────────────┐   │
│  │ Price Trend by Market   │ │ Weather & Drought Index │   │
│  │ (Multi-Line Chart)      │ │ (Combination Chart)     │   │
│  └─────────────────────────┘ └─────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────┐ ┌─────────────────────────┐   │
│  │ Crop Profitability      │ │ Crop Distribution       │   │
│  │ (Bar Chart)             │ │ (Doughnut Chart)        │   │
│  └─────────────────────────┘ └─────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────┐ ┌─────────────────────────┐   │
│  │ Yield vs Farm Skill     │ │ Economic Indicators     │   │
│  │ (Scatter Chart)         │ │ (Multi-Line Chart)      │   │
│  └─────────────────────────┘ └─────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────┐ ┌─────────────────────────┐   │
│  │ Farmer Demographics     │ │ Crop Compatibility      │   │
│  │ (Column Chart)          │ │ (Column Chart)          │   │
│  └─────────────────────────┘ └─────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ROI & Margin Analysis (Combination Chart)           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Color Scheme

- **Primary**: Emerald Green (#10b981) - Agricultural theme
- **Secondary**: Blue (#3b82f6) - Data visualization
- **Accent**: Orange (#f59e0b) - Highlights
- **Background**: White with subtle gradient
- **Ripple**: Light green with low opacity

### MagicUI Components Usage

1. **Animated Number Counter**: For statistics cards
2. **Skeleton Loader**: For loading states
3. **Card Component**: For chart containers
4. **Badge Component**: For status indicators
5. **Ripple Effect**: For background animation

### Responsive Breakpoints

- **Desktop (≥1024px)**: 4-column grid for stats, 2-column for charts
- **Tablet (768px-1023px)**: 2-column grid for stats, 1-column for charts
- **Mobile (<768px)**: 1-column stack layout


## Error Handling

### Frontend Error Handling

```typescript
// API Error Handling
try {
  const data = await fetchDashboardData(province);
  setDashboardData(data);
} catch (error) {
  if (error.response?.status === 404) {
    setError('ไม่พบข้อมูลสำหรับจังหวัดนี้');
  } else if (error.response?.status === 500) {
    setError('เกิดข้อผิดพลาดในการดึงข้อมูล กรุณาลองใหม่อีกครั้ง');
  } else {
    setError('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
  }
}
```

### Backend Error Handling

```python
@router.get("/dashboard/overview")
async def get_dashboard_overview(province: str, db: Session, redis_client):
    try:
        # Try Redis cache first
        cached_data = await get_from_cache(redis_client, province)
        if cached_data:
            return cached_data
        
        # Query database
        data = await query_dashboard_data(db, province)
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for province: {province}"
            )
        
        # Cache the result
        await set_cache(redis_client, province, data)
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard overview error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

### Redis Fallback Strategy

```python
async def get_dashboard_data_with_fallback(province: str, db: Session, redis_client):
    try:
        # Try Redis first
        return await get_from_redis(redis_client, province, db)
    except RedisError as e:
        logger.warning(f"Redis unavailable: {e}. Falling back to database.")
        # Fallback to direct database query
        return await query_database_directly(db, province)
```


## Testing Strategy

### Unit Tests

#### Frontend Unit Tests
- Province selector component rendering
- Statistics card data formatting
- Chart data transformation
- Error state handling
- Loading state display

#### Backend Unit Tests
- Dashboard data aggregation logic
- Redis cache operations
- Database query functions
- Error handling scenarios
- Data serialization/deserialization

### Integration Tests

#### Frontend Integration Tests
- API call with TanStack Query
- Province selection triggers data fetch
- Chart rendering with real data
- Error boundary behavior

#### Backend Integration Tests
- End-to-end API endpoint testing
- Redis cache hit/miss scenarios
- Database connection handling
- Response format validation

### Performance Tests

- **Page Load Time**: < 2 seconds
- **API Response Time**: < 1 second (cached), < 3 seconds (uncached)
- **Chart Rendering**: < 500ms
- **Ripple Animation**: 60fps

### Manual Testing Checklist

- [ ] Province selection updates all charts
- [ ] Statistics display correct values
- [ ] Charts are interactive (hover, zoom)
- [ ] Responsive design works on all screen sizes
- [ ] Loading states appear correctly
- [ ] Error messages are user-friendly
- [ ] Ripple background doesn't interfere with content
- [ ] Navigation highlights active page
- [ ] Redis caching reduces load times
- [ ] Fallback works when Redis is down


## Dependencies and Installation

### Frontend Dependencies

```json
{
  "dependencies": {
    "@canvasjs/react-charts": "^1.0.2",
    "@tanstack/react-query": "^5.0.0",
    "react": "^18.2.0",
    "react-router-dom": "^6.20.0"
  }
}
```

**Installation:**
```bash
npm install @canvasjs/react-charts
npx shadcn@latest add card badge skeleton
```

### Backend Dependencies

```python
# requirements.txt
fastapi>=0.104.0
redis>=5.0.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
```

**Installation:**
```bash
pip install redis
```

### Redis Setup

**Docker (Recommended):**
```bash
docker run -d --name redis-cache -p 6379:6379 redis:latest
```

**Windows:**
```bash
# Download Redis for Windows or use WSL
# https://github.com/microsoftarchive/redis/releases
```

### MagicUI Components

Install required shadcn components:
```bash
npx shadcn@latest add card
npx shadcn@latest add badge
npx shadcn@latest add skeleton
npx shadcn@latest add dropdown-menu
```

Create custom Ripple component based on MagicUI patterns.


## Security Considerations

### API Security
- **Input Validation**: Validate province parameter to prevent SQL injection
- **Rate Limiting**: Implement rate limiting on dashboard endpoint
- **CORS**: Configure appropriate CORS headers
- **Authentication**: Ensure user is authenticated before accessing dashboard

### Redis Security
- **Connection**: Use password-protected Redis connection
- **Data Sanitization**: Sanitize data before caching
- **TTL**: Set appropriate TTL to prevent stale data

### Data Privacy
- **No PII**: Dashboard data should not contain personally identifiable information
- **Aggregated Data**: Display only aggregated statistics, not individual records

## Performance Optimization

### Frontend Optimization
- **Code Splitting**: Lazy load CanvasJS charts
- **Memoization**: Use React.memo for chart components
- **Debouncing**: Debounce province selection changes
- **Virtual Scrolling**: If displaying large datasets

### Backend Optimization
- **Database Indexing**: Index province, crop_type, and date columns
- **Query Optimization**: Use efficient SQL queries with proper joins
- **Connection Pooling**: Use database connection pooling
- **Async Operations**: Use async/await for I/O operations

### Caching Strategy
- **Multi-level Caching**: Browser cache + Redis cache
- **Cache Warming**: Pre-populate cache for popular provinces
- **Partial Updates**: Update only changed data in cache

## Monitoring and Logging

### Metrics to Track
- API response times
- Cache hit/miss ratio
- Database query performance
- Error rates
- User engagement (province selections)

### Logging Strategy
```python
logger.info(f"Dashboard data requested for province: {province}")
logger.info(f"Cache hit: {cached}")
logger.error(f"Database query failed: {error}")
```


## AI-Generated Insights Section

### Insights Analysis Component

The dashboard will include an AI-powered insights section that automatically analyzes the data and provides explanations for why certain crops perform well in the province.

#### Insight Categories

1. **Soil Compatibility Analysis**
```typescript
interface SoilInsight {
  message: string;
  soilType: string;
  suitableCrops: string[];
  reason: string;
}

// Example:
{
  message: "ดินร่วนในกรุงเทพมหานครเหมาะสมกับการปลูกคะน้า กวางตุ้ง และผักบุ้ง",
  soilType: "ดินร่วน",
  suitableCrops: ["คะน้า", "กวางตุ้ง", "ผักบุ้ง"],
  reason: "ดินร่วนมีการระบายน้ำดี เหมาะกับพืชที่ต้องการน้ำสูง"
}
```

2. **Weather Pattern Insights**
```typescript
interface WeatherInsight {
  message: string;
  favorableConditions: string[];
  affectedCrops: string[];
  recommendation: string;
}

// Example:
{
  message: "อุณหภูมิเฉลี่ย 24-26°C และความชื้น 73% เหมาะสมกับผักใบ",
  favorableConditions: ["อุณหภูมิเหมาะสม", "ความชื้นพอดี"],
  affectedCrops: ["คะน้า", "ผักกาดหอม"],
  recommendation: "ช่วงนี้เหมาะสมกับการปลูกผักใบทุกชนิด"
}
```

3. **Economic Factors Insights**
```typescript
interface EconomicInsight {
  message: string;
  keyFactors: { factor: string; impact: string }[];
  marketOpportunity: string;
}

// Example:
{
  message: "ดัชนีความต้องการผักสูง (1.124) ส่งผลให้ราคาคะน้าในตลาดดี",
  keyFactors: [
    { factor: "ความต้องการผัก", impact: "สูง" },
    { factor: "ราคาปุ๋ย", impact: "ปานกลาง" }
  ],
  marketOpportunity: "โอกาสในการขายผักใบในช่วงนี้สูง"
}
```

4. **Success Factor Analysis**
```typescript
interface SuccessFactorInsight {
  message: string;
  topCrop: string;
  successRate: number;
  keyFactors: string[];
  comparison: string;
}

// Example:
{
  message: "คะน้ามีอัตราความสำเร็จ 83.9% เนื่องจากความเหมาะสมของดินและสภาพอากาศ",
  topCrop: "คะน้า",
  successRate: 0.839,
  keyFactors: [
    "ดินร่วนเหมาะสม (compatibility: 0.738)",
    "อุณหภูมิเหมาะสม (24-26°C)",
    "ทักษะเกษตรกรดี (0.546)"
  ],
  comparison: "สูงกว่าค่าเฉลี่ยของจังหวัด 15%"
}
```

5. **Profitability Insights**
```typescript
interface ProfitabilityInsight {
  message: string;
  topProfitableCrop: string;
  avgProfit: number;
  roi: number;
  reasons: string[];
}

// Example:
{
  message: "คะน้าให้ผลกำไรเฉลี่ย 265,179 บาท/รอบ ด้วย ROI 500%",
  topProfitableCrop: "คะน้า",
  avgProfit: 265179.24,
  roi: 500.0,
  reasons: [
    "ต้นทุนการลงทุนต่ำ (8,000 บาท)",
    "ระยะเวลาเก็บเกี่ยวสั้น (45 วัน)",
    "ความต้องการในตลาดสูง",
    "ประสิทธิภาพผลผลิตดี (1.51)"
  ]
}
```

#### Insights Generation Logic

```typescript
function generateInsights(dashboardData: DashboardData): Insight[] {
  const insights: Insight[] = [];
  
  // 1. Analyze soil compatibility
  const soilInsight = analyzeSoilCompatibility(
    dashboardData.farmerDemographics,
    dashboardData.cropCompatibility,
    dashboardData.cropDistribution
  );
  insights.push(soilInsight);
  
  // 2. Analyze weather patterns
  const weatherInsight = analyzeWeatherPatterns(
    dashboardData.weatherData,
    dashboardData.cropDistribution
  );
  insights.push(weatherInsight);
  
  // 3. Analyze economic factors
  const economicInsight = analyzeEconomicFactors(
    dashboardData.economicIndicators,
    dashboardData.priceHistory
  );
  insights.push(economicInsight);
  
  // 4. Analyze success factors
  const successInsight = analyzeSuccessFactors(
    dashboardData.profitability,
    dashboardData.yieldEfficiency,
    dashboardData.cropCompatibility
  );
  insights.push(successInsight);
  
  // 5. Analyze profitability
  const profitInsight = analyzeProfitability(
    dashboardData.profitability,
    dashboardData.cropDistribution
  );
  insights.push(profitInsight);
  
  return insights;
}
```

#### UI Display for Insights

```tsx
<Card className="mt-6 bg-gradient-to-r from-emerald-50 to-blue-50">
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      <Lightbulb className="w-6 h-6 text-yellow-500" />
      🔍 ข้อมูลเชิงลึกและคำแนะนำ
    </CardTitle>
  </CardHeader>
  <CardContent>
    <div className="space-y-4">
      {insights.map((insight, index) => (
        <div key={index} className="p-4 bg-white rounded-lg shadow-sm border-l-4 border-emerald-500">
          <h4 className="font-semibold text-gray-800 mb-2">{insight.title}</h4>
          <p className="text-gray-600 mb-3">{insight.message}</p>
          {insight.details && (
            <ul className="list-disc list-inside text-sm text-gray-500 space-y-1">
              {insight.details.map((detail, i) => (
                <li key={i}>{detail}</li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  </CardContent>
</Card>
```

