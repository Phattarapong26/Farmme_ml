# Design Document

## Overview

ฟีเจอร์นี้จะปรับปรุงการแสดงผลกราฟในหน้า Dashboard Overview โดยเปลี่ยนจากข้อมูลรายวันเป็นค่าเฉลี่ยรายเดือน สำหรับกราฟ 5 ประเภท: แนวโน้มอุณหภูมิ, ปริมาณฝน, สภาพอากาศ, ราคาน้ำมัน, และราคาปุ๋ย การเปลี่ยนแปลงหลักจะอยู่ที่ Backend Service ซึ่งจะใช้ SQL aggregation เพื่อคำนวณค่าเฉลี่ยรายเดือนจากข้อมูลรายวัน

## Architecture

### System Flow

```
┌─────────────────┐
│   Database      │
│   (PostgreSQL)  │
│                 │
│  ┌───────────┐  │
│  │ weather_  │  │ ← ข้อมูลรายวัน (date, temperature, rainfall)
│  │ data      │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ crop_     │  │ ← ข้อมูลรายวัน (date, price_per_kg)
│  │ prices    │  │
│  └───────────┘  │
└────────┬────────┘
         │
         │ SQL Query with GROUP BY month
         │
┌────────▼────────┐
│   Backend       │
│  (FastAPI)      │
│                 │
│  ┌───────────┐  │
│  │dashboard_ │  │ ← คำนวณค่าเฉลี่ยรายเดือน
│  │service.py │  │   - get_weather_data()
│  └───────────┘  │   - get_economic_timeline()
│                 │
└────────┬────────┘
         │
         │ JSON Response (monthly data)
         │
┌────────▼────────┐
│   Frontend      │
│  (React/TS)     │
│                 │
│  ┌───────────┐  │
│  │Dashboard  │  │ ← แสดงกราฟรายเดือน
│  │Overview   │  │
│  └───────────┘  │
└─────────────────┘
```

## Components and Interfaces

### 1. Backend - get_weather_data() Function

**Location:** `backend/app/services/dashboard_service.py`

**Current Implementation:**
```python
def get_weather_data(db: Session, province: str, days_back: int = 30):
    cutoff_date = datetime.now() - timedelta(days=days_back)
    weather = db.query(WeatherData).filter(
        WeatherData.province == province,
        WeatherData.date >= cutoff_date
    ).order_by(desc(WeatherData.date)).limit(50).all()
    
    return [
        {
            "date": w.date.isoformat(),
            "temperature": round(w.temperature_celsius, 1),
            "rainfall": round(w.rainfall_mm, 1)
        }
        for w in weather
    ]
```

**New Implementation:**
```python
def get_weather_data(db: Session, province: str, days_back: int = 30):
    from sqlalchemy import text, extract
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    # Use SQL to aggregate by month
    query = text("""
        SELECT 
            TO_CHAR(date, 'Mon YYYY') as month_year,
            EXTRACT(YEAR FROM date) as year,
            EXTRACT(MONTH FROM date) as month,
            AVG(temperature_celsius) as avg_temperature,
            AVG(rainfall_mm) as avg_rainfall
        FROM weather_data
        WHERE province = :province
          AND date >= :cutoff_date
        GROUP BY year, month, TO_CHAR(date, 'Mon YYYY')
        ORDER BY year, month
    """)
    
    result = db.execute(query, {"province": province, "cutoff_date": cutoff_date})
    
    return [
        {
            "date": row[0],  # "Jan 2024"
            "temperature": round(float(row[3]), 1) if row[3] else 0,
            "rainfall": round(float(row[4]), 1) if row[4] else 0
        }
        for row in result
    ]
```

**Changes:**
- ใช้ SQL `GROUP BY` เพื่อจัดกลุ่มข้อมูลตามเดือนและปี
- ใช้ `AVG()` function เพื่อคำนวณค่าเฉลี่ย
- ใช้ `TO_CHAR()` เพื่อฟอร์แมต date เป็น "Mon YYYY" (เช่น "Jan 2024")
- ลบ `limit(50)` เพราะข้อมูลรายเดือนจะมีน้อยกว่ารายวันมาก
- เรียงข้อมูลตามลำดับเวลา (year, month)

### 2. Backend - get_economic_timeline() Function

**Location:** `backend/app/services/dashboard_service.py`

**Current Implementation:**
```python
def get_economic_timeline(db: Session, province: str, days_back: int = 90):
    from sqlalchemy import text
    start_date = datetime.now() - timedelta(days=days_back)
    
    query = text("""
        SELECT 
            date,
            AVG(price_per_kg) * 10 as fuel_price,
            AVG(price_per_kg) * 20 as fertilizer_price
        FROM crop_prices
        WHERE province = :province
          AND date >= :start_date
        GROUP BY date
        ORDER BY date
        LIMIT 100
    """)
    
    result = db.execute(query, {"province": province, "start_date": start_date})
    return [
        {
            "date": row[0].strftime('%Y-%m-%d'),
            "fuel_price": round(float(row[1]), 2),
            "fertilizer_price": round(float(row[2]), 2)
        }
        for row in result
    ]
```

**New Implementation:**
```python
def get_economic_timeline(db: Session, province: str, days_back: int = 90):
    from sqlalchemy import text
    start_date = datetime.now() - timedelta(days=days_back)
    
    query = text("""
        SELECT 
            TO_CHAR(date, 'Mon YYYY') as month_year,
            EXTRACT(YEAR FROM date) as year,
            EXTRACT(MONTH FROM date) as month,
            AVG(price_per_kg) * 10 as fuel_price,
            AVG(price_per_kg) * 20 as fertilizer_price
        FROM crop_prices
        WHERE province = :province
          AND date >= :start_date
        GROUP BY year, month, TO_CHAR(date, 'Mon YYYY')
        ORDER BY year, month
    """)
    
    result = db.execute(query, {"province": province, "start_date": start_date})
    return [
        {
            "date": row[0],  # "Jan 2024"
            "fuel_price": round(float(row[3]), 2) if row[3] else 0,
            "fertilizer_price": round(float(row[4]), 2) if row[4] else 0
        }
        for row in result
    ]
```

**Changes:**
- เปลี่ยนจาก `GROUP BY date` เป็น `GROUP BY year, month`
- ใช้ `TO_CHAR()` เพื่อฟอร์แมต date เป็น "Mon YYYY"
- ลบ `LIMIT 100` เพราะข้อมูลรายเดือนจะมีน้อยกว่ารายวันมาก
- คำนวณค่าเฉลี่ยรายเดือนแทนรายวัน

## Data Models

### Weather Data (Monthly Aggregated)

**Response Format:**
```json
{
  "weather_data": [
    {
      "date": "Jan 2024",
      "temperature": 28.5,
      "rainfall": 45.2
    },
    {
      "date": "Feb 2024",
      "temperature": 30.1,
      "rainfall": 32.8
    }
  ]
}
```

**Fields:**
- `date` (string): เดือนและปีในรูปแบบ "Mon YYYY" (ภาษาอังกฤษ)
- `temperature` (float): อุณหภูมิเฉลี่ยรายเดือน (°C)
- `rainfall` (float): ปริมาณฝนเฉลี่ยรายเดือน (มม.)

### Economic Timeline (Monthly Aggregated)

**Response Format:**
```json
{
  "economic_timeline": [
    {
      "date": "Jan 2024",
      "fuel_price": 125.50,
      "fertilizer_price": 251.00
    },
    {
      "date": "Feb 2024",
      "fuel_price": 128.30,
      "fertilizer_price": 256.60
    }
  ]
}
```

**Fields:**
- `date` (string): เดือนและปีในรูปแบบ "Mon YYYY"
- `fuel_price` (float): ราคาน้ำมันเฉลี่ยรายเดือน (บาท)
- `fertilizer_price` (float): ราคาปุ๋ยเฉลี่ยรายเดือน (บาท)

## Database Queries

### Weather Data Aggregation Query

```sql
SELECT 
    TO_CHAR(date, 'Mon YYYY') as month_year,
    EXTRACT(YEAR FROM date) as year,
    EXTRACT(MONTH FROM date) as month,
    AVG(temperature_celsius) as avg_temperature,
    AVG(rainfall_mm) as avg_rainfall
FROM weather_data
WHERE province = 'เชียงใหม่'
  AND date >= '2024-01-01'
GROUP BY year, month, TO_CHAR(date, 'Mon YYYY')
ORDER BY year, month;
```

**Explanation:**
- `TO_CHAR(date, 'Mon YYYY')`: แปลง date เป็น "Jan 2024", "Feb 2024", etc.
- `EXTRACT(YEAR/MONTH FROM date)`: ดึงปีและเดือนเพื่อใช้ใน GROUP BY และ ORDER BY
- `AVG(temperature_celsius)`: คำนวณอุณหภูมิเฉลี่ยรายเดือน
- `AVG(rainfall_mm)`: คำนวณปริมาณฝนเฉลี่ยรายเดือน
- `GROUP BY year, month`: จัดกลุ่มข้อมูลตามเดือนและปี
- `ORDER BY year, month`: เรียงข้อมูลตามลำดับเวลา

### Economic Timeline Aggregation Query

```sql
SELECT 
    TO_CHAR(date, 'Mon YYYY') as month_year,
    EXTRACT(YEAR FROM date) as year,
    EXTRACT(MONTH FROM date) as month,
    AVG(price_per_kg) * 10 as fuel_price,
    AVG(price_per_kg) * 20 as fertilizer_price
FROM crop_prices
WHERE province = 'เชียงใหม่'
  AND date >= '2024-01-01'
GROUP BY year, month, TO_CHAR(date, 'Mon YYYY')
ORDER BY year, month;
```

**Explanation:**
- คล้ายกับ weather query แต่ใช้ตาราง crop_prices
- คำนวณค่าเฉลี่ยราคาพืชรายเดือนแล้วคูณด้วย 10 และ 20 เพื่อประมาณราคาน้ำมันและปุ๋ย

## Frontend Changes

### DashboardOverview Component

**Location:** `frontend/src/pages/DashboardOverview.tsx`

**Current State:**
```typescript
<RechartsContainer title="แนวโน้มอุณหภูมิ">
  <TimeSeriesLineChart
    data={dashboardData?.weather_data || []}
    dataKeys={['temperature']}
    colors={['#f59e0b']}
    yAxisLabel="อุณหภูมิ (°C)"
  />
</RechartsContainer>
```

**Changes Required:**
- ไม่ต้องแก้ไข component เพราะ data structure ยังคงเหมือนเดิม
- แค่เปลี่ยน description จาก "วันที่ผ่านมา" เป็น "รายเดือน" หรือ "ค่าเฉลี่ยรายเดือน"

**Updated Code:**
```typescript
<RechartsContainer 
  title="แนวโน้มอุณหภูมิ"
  description="ค่าเฉลี่ยรายเดือน"
  icon={<Thermometer className="w-5 h-5" />}
>
  <TimeSeriesLineChart
    data={dashboardData?.weather_data || []}
    dataKeys={['temperature']}
    colors={['#f59e0b']}
    yAxisLabel="อุณหภูมิ (°C)"
  />
</RechartsContainer>
```

**Charts to Update:**
1. แนวโน้มอุณหภูมิ (weather category)
2. ปริมาณฝน (weather category)
3. สภาพอากาศ (overview category)
4. ราคาน้ำมัน (economic category)
5. ราคาปุ๋ย (economic category)

## Error Handling

### Scenario 1: No data for specific months

**Handling:**
```python
# ใน SQL query
# ถ้าไม่มีข้อมูลในเดือนใดเดือนหนึ่ง จะไม่มี row สำหรับเดือนนั้น
# Frontend จะแสดงเฉพาะเดือนที่มีข้อมูล
```

**User Experience:**
- กราฟจะแสดงเฉพาะเดือนที่มีข้อมูล
- ไม่มีช่องว่างหรือค่า 0 ในเดือนที่ไม่มีข้อมูล

### Scenario 2: Database doesn't support TO_CHAR

**Handling:**
```python
# ถ้า database เป็น SQLite (ไม่มี TO_CHAR)
# ใช้ strftime แทน:
query = text("""
    SELECT 
        strftime('%m-%Y', date) as month_year,
        CAST(strftime('%Y', date) AS INTEGER) as year,
        CAST(strftime('%m', date) AS INTEGER) as month,
        AVG(temperature_celsius) as avg_temperature,
        AVG(rainfall_mm) as avg_rainfall
    FROM weather_data
    WHERE province = :province
      AND date >= :cutoff_date
    GROUP BY year, month
    ORDER BY year, month
""")
```

### Scenario 3: Very large date range

**Handling:**
```python
# ถ้า days_back มากเกินไป (เช่น 3650 วัน = 10 ปี)
# จะได้ข้อมูล ~120 เดือน ซึ่งยังคงจัดการได้
# ไม่ต้องจำกัดเพราะข้อมูลรายเดือนไม่มากเกินไป
```

## Testing Strategy

### Unit Tests

1. **Backend - get_weather_data()**
   - Test: Returns monthly aggregated data
   - Test: Correct date format ("Mon YYYY")
   - Test: Correct average calculations
   - Test: Handles empty data gracefully

2. **Backend - get_economic_timeline()**
   - Test: Returns monthly aggregated data
   - Test: Correct fuel and fertilizer price calculations
   - Test: Handles different date ranges

### Integration Tests

1. **Dashboard API Test**
   - Test: /api/dashboard/overview returns monthly data
   - Test: Data matches database aggregation
   - Test: Frontend can parse and display monthly data

2. **Chart Display Test**
   - Test: Charts show monthly labels on X-axis
   - Test: Data points match monthly averages
   - Test: Multiple months display correctly

### Manual Testing Checklist

1. **Weather Charts**
   - [ ] แนวโน้มอุณหภูมิแสดงข้อมูลรายเดือน
   - [ ] ปริมาณฝนแสดงข้อมูลรายเดือน
   - [ ] สภาพอากาศแสดงข้อมูลรายเดือน
   - [ ] แกน X แสดงชื่อเดือน-ปี

2. **Economic Charts**
   - [ ] ราคาน้ำมันแสดงข้อมูลรายเดือน
   - [ ] ราคาปุ๋ยแสดงข้อมูลรายเดือน
   - [ ] ค่าเฉลี่ยถูกต้องตามข้อมูลจริง

3. **Date Range**
   - [ ] days_back=30 แสดง ~1 เดือน
   - [ ] days_back=90 แสดง ~3 เดือน
   - [ ] days_back=365 แสดง ~12 เดือน

## Implementation Notes

### Database Compatibility

**PostgreSQL:**
- ใช้ `TO_CHAR(date, 'Mon YYYY')` ✅
- ใช้ `EXTRACT(YEAR/MONTH FROM date)` ✅

**SQLite:**
- ใช้ `strftime('%m-%Y', date)` แทน TO_CHAR
- ใช้ `CAST(strftime('%Y', date) AS INTEGER)` แทน EXTRACT

**MySQL:**
- ใช้ `DATE_FORMAT(date, '%b %Y')` แทน TO_CHAR
- ใช้ `YEAR(date)` และ `MONTH(date)` แทน EXTRACT

### Performance Considerations

- **Reduced Data Volume**: ข้อมูลรายเดือนจะมีปริมาณน้อยกว่ารายวันมาก (~30x)
- **Faster Queries**: GROUP BY จะทำให้ query เร็วขึ้นเพราะ return rows น้อยลง
- **Better Chart Performance**: Frontend render กราฟเร็วขึ้นเพราะ data points น้อยลง

### Backward Compatibility

- **API Response Structure**: ยังคงเหมือนเดิม (array of objects with date, temperature, rainfall)
- **Frontend Components**: ไม่ต้องแก้ไข chart components
- **Only Change**: ค่าใน `date` field เปลี่ยนจาก "2024-01-15" เป็น "Jan 2024"

## Future Enhancements

1. **Localization**: แปลชื่อเดือนเป็นภาษาไทย ("ม.ค. 2567" แทน "Jan 2024")
2. **Drill-down**: คลิกที่เดือนเพื่อดูข้อมูลรายวันในเดือนนั้น
3. **Comparison**: เปรียบเทียบข้อมูลรายเดือนระหว่างปี
4. **Export**: ดาวน์โหลดข้อมูลรายเดือนเป็น CSV
