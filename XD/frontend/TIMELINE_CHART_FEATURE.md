# 📈 Timeline Chart Feature - Historical + ML Forecast

## ✅ สิ่งที่ทำ

เพิ่มฟีเจอร์ **Timeline Chart** ที่แสดงทั้ง:
1. **ราคาจริงในอดีต** (Historical data จาก database)
2. **ราคาที่ ML ทำนาย** (ML forecast จาก model)
3. **Timeframe Selector** เลือกช่วงเวลา (3M, 6M, 1Y, ALL)

---

## 🎯 Features

### 1. **Timeline Chart (Tab แรก)**
- แสดงกราฟเส้นต่อเนื่อง: Historical → ML Forecast
- **เส้นทึบสีเขียว** = ราคาจริงในอดีต (จาก database)
- **เส้นประสีม่วง** = ราคาที่ ML ทำนาย (จาก ML model)
- Timeframe selector: 3M, 6M, 1Y, ALL

### 2. **Timeframe Selector**
- **3M**: แสดง 3 เดือนย้อนหลัง + อนาคต
- **6M**: แสดง 6 เดือนย้อนหลัง + อนาคต (default)
- **1Y**: แสดง 1 ปีย้อนหลัง + อนาคต
- **ALL**: แสดงทั้งหมด

### 3. **Summary Cards**
- Historical Data: จำนวนเดือนที่มีข้อมูลจริง
- ML Forecast: จำนวนเดือนที่ ML ทำนาย
- Total Timeline: จำนวนเดือนรวมทั้งหมด

---

## 🔧 Backend Changes

### `@backend/main.py`

เพิ่มการดึงข้อมูล historical และสร้าง timeline:

```python
# Get historical price data (past 12 months)
historical_cutoff = datetime.today() - timedelta(days=365)
historical_prices = db.query(
    CropPrice.date,
    CropPrice.price_per_kg
).filter(
    CropPrice.crop_type == crop_type,
    CropPrice.province == province,
    CropPrice.date >= historical_cutoff
).order_by(CropPrice.date.asc()).all()

# Aggregate historical data by month
historical_by_month = {}
for record in historical_prices:
    month_key = record.date.strftime("%Y-%m")
    if month_key not in historical_by_month:
        historical_by_month[month_key] = []
    historical_by_month[month_key].append(record.price_per_kg)

# Create historical price trend
historical_price_data = [
    {
        "date": month_key,
        "month": thai_months[int(month_key.split('-')[1])],
        "year": int(month_key.split('-')[0]),
        "average_price": round(sum(prices) / len(prices), 2),
        "type": "historical"  # ระบุว่าเป็นข้อมูลจริง
    }
    for month_key, prices in sorted(historical_by_month.items())
]

# Create future price predictions from ML scenarios
future_predictions = {}
for r in results:
    month_key = r['harvest_date'].strftime("%Y-%m")
    if month_key not in future_predictions:
        future_predictions[month_key] = []
    future_predictions[month_key].append(r['predicted_price'])

ml_price_forecast = [
    {
        "date": month_key,
        "month": thai_months[int(month_key.split('-')[1])],
        "year": int(month_key.split('-')[0]),
        "average_price": round(sum(prices) / len(prices), 2),
        "type": "ml_forecast"  # ระบุว่าเป็นการทำนาย ML
    }
    for month_key, prices in sorted(future_predictions.items())
]

# Combine historical and forecast data
combined_timeline = historical_price_data + ml_price_forecast

return {
    # ... existing fields
    "historical_prices": historical_price_data,
    "ml_forecast": ml_price_forecast,
    "combined_timeline": combined_timeline
}
```

---

## 🎨 Frontend Changes

### `src/components/PlantingRecommendation.tsx`

#### 1. เพิ่ม State สำหรับ Timeframe
```tsx
const [timeframe, setTimeframe] = useState<'3M' | '6M' | '1Y' | 'ALL'>('6M');
```

#### 2. เพิ่ม Tab "Timeline"
```tsx
<TabsList className="grid w-full grid-cols-5">
  <TabsTrigger value="timeline">Timeline</TabsTrigger>
  <TabsTrigger value="trend">แนวโน้มราคา</TabsTrigger>
  <TabsTrigger value="comparison">เปรียบเทียบเดือน</TabsTrigger>
  <TabsTrigger value="detail">รายละเอียด</TabsTrigger>
  <TabsTrigger value="scenarios">ทุก Scenarios</TabsTrigger>
</TabsList>
```

#### 3. Timeline Chart Component
```tsx
<TabsContent value="timeline">
  {/* Timeframe Selector */}
  <div className="flex gap-1">
    {(['3M', '6M', '1Y', 'ALL'] as const).map((tf) => (
      <button
        onClick={() => setTimeframe(tf)}
        className={timeframe === tf ? 'bg-blue-600 text-white' : 'bg-white'}
      >
        {tf}
      </button>
    ))}
  </div>

  {/* Chart */}
  <LineChart data={filteredTimeline}>
    {/* Historical Line - เส้นทึบสีเขียว */}
    <Line 
      dataKey={(item) => item.type === 'historical' ? item.average_price : null}
      stroke="#22c55e" 
      strokeWidth={3}
      name="ราคาจริง (Historical)"
    />
    
    {/* ML Forecast Line - เส้นประสีม่วง */}
    <Line 
      dataKey={(item) => item.type === 'ml_forecast' ? item.average_price : null}
      stroke="#a855f7" 
      strokeWidth={3}
      strokeDasharray="5 5"
      name="ML Forecast"
    />
  </LineChart>

  {/* Summary Cards */}
  <div className="grid grid-cols-3">
    <Card>Historical Data: {data.historical_prices.length}</Card>
    <Card>ML Forecast: {data.ml_forecast.length}</Card>
    <Card>Total: {data.combined_timeline.length}</Card>
  </div>
</TabsContent>
```

#### 4. Timeframe Filtering
```tsx
const filteredTimeline = (() => {
  const timeline = data.combined_timeline;
  const now = new Date();
  let cutoffDate = new Date();
  
  if (timeframe === '3M') {
    cutoffDate.setMonth(now.getMonth() - 3);
  } else if (timeframe === '6M') {
    cutoffDate.setMonth(now.getMonth() - 6);
  } else if (timeframe === '1Y') {
    cutoffDate.setFullYear(now.getFullYear() - 1);
  } else {
    cutoffDate = new Date(0); // Show all
  }
  
  return timeline.filter(item => new Date(item.date) >= cutoffDate);
})()
```

---

## 📊 ตัวอย่างข้อมูลที่แสดง

### ทดสอบกับ พริก (Chili):

```json
{
  "success": true,
  "crop_type": "พริก",
  "province": "เชียงใหม่",
  
  "historical_prices": [
    {
      "date": "2025-05",
      "month": "พฤษภาคม",
      "year": 2025,
      "average_price": 27.57,
      "type": "historical"
    },
    {
      "date": "2025-06",
      "month": "มิถุนายน",
      "year": 2025,
      "average_price": 35.94,
      "type": "historical"
    }
    // ... 5 เดือน
  ],
  
  "ml_forecast": [
    {
      "date": "2026-01",
      "month": "มกราคม",
      "year": 2026,
      "average_price": 31.33,
      "type": "ml_forecast"
    },
    {
      "date": "2026-02",
      "month": "กุมภาพันธ์",
      "year": 2026,
      "average_price": 31.33,
      "type": "ml_forecast"
    }
    // ... 6 เดือน
  ],
  
  "combined_timeline": [
    // รวม historical + ml_forecast = 11 entries
    // เรียงตาม date จากอดีต → อนาคต
  ]
}
```

---

## 🎯 Visual Design

### Chart Legend:
```
━━━━━ เส้นทึบสีเขียว = ราคาจริง (Historical)
- - - เส้นประสีม่วง = ราคาที่ ML ทำนาย (Forecast)
```

### Color Scheme:
- **Historical**: สีเขียว (#22c55e) - แสดงข้อมูลจริงที่เกิดขึ้นแล้ว
- **ML Forecast**: สีม่วง (#a855f7) - แสดงการทำนายของ ML
- **Timeline**: สีน้ำเงิน (#3b82f6) - รวมทั้งหมด

### UI Elements:
1. **Gradient Banner**: สีน้ำเงิน → ม่วง พร้อมคำอธิบาย
2. **Timeframe Buttons**: ปุ่มสลับ 3M, 6M, 1Y, ALL
3. **Legend**: แสดงเส้นทึบ vs เส้นประ
4. **Summary Cards**: 3 การ์ดแสดงสถิติ

---

## 🧪 การทดสอบ

### Test Case 1: พริก (มีข้อมูล historical)
```bash
curl -X POST "http://localhost:8000/recommend-planting-date" \
  -H "Content-Type: application/json" \
  -d '{"crop_type": "พริก", "province": "เชียงใหม่", "growth_days": 75}'
```

**ผลลัพธ์:**
```
✅ Historical Data: 5 เดือน (2025-05 → 2025-09)
✅ ML Forecast: 6 เดือน (2026-01 → 2026-06)
✅ Combined: 11 entries total
```

### Test Case 2: ข่า (ไม่มีข้อมูล historical)
```bash
curl -X POST "http://localhost:8000/recommend-planting-date" \
  -H "Content-Type: application/json" \
  -d '{"crop_type": "ข่า", "province": "เชียงใหม่", "growth_days": 180}'
```

**ผลลัพธ์:**
```
❌ Historical Data: 0 เดือน (ไม่มีข้อมูลในฐานข้อมูล)
✅ ML Forecast: 7 เดือน (2026-04 → 2026-10)
✅ Combined: 7 entries total (แสดงแค่ ML forecast)
```

---

## 📝 User Experience

### Scenario 1: ผู้ใช้เลือกพืชที่มีข้อมูล historical
1. เปิดหน้า Planting Recommendation
2. เลือก "พริก" + "เชียงใหม่"
3. คลิก "วิเคราะห์"
4. ดู Tab "Timeline":
   - เห็นเส้นเขียว (ราคาจริง 5 เดือน)
   - ต่อด้วยเส้นม่วง (ML ทำนาย 6 เดือน)
   - สลับ timeframe 3M/6M/1Y/ALL ได้

### Scenario 2: ผู้ใช้เลือกพืชที่ไม่มีข้อมูล historical
1. เลือก "ข่า" + "เชียงใหม่"
2. ดู Tab "Timeline":
   - ไม่มีเส้นเขียว (ไม่มีข้อมูลจริง)
   - แสดงแค่เส้นม่วง (ML ทำนาย 7 เดือน)
   - Summary card แสดง "Historical: 0 เดือน"

---

## ✅ ข้อดี

1. **ต่อเนื่อง**: เห็นภาพรวมจากอดีต → ปัจจุบัน → อนาคต
2. **เปรียบเทียบได้**: เห็นว่า ML ทำนายแตกต่างจากอดีตอย่างไร
3. **Flexible**: เลือก timeframe ได้ตามต้องการ
4. **โปร่งใส**: ชัดเจนว่าส่วนไหนคือข้อมูลจริง ส่วนไหนคือการทำนาย
5. **ไม่มี Mock Data**: ทุกข้อมูลมาจาก database + ML model จริง

---

## 🎨 UI Components

### 1. Header Banner
```tsx
<div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200">
  <div className="flex items-center justify-between">
    <p>เส้นทึบ = ราคาจริงในอดีต • เส้นประ = ราคาที่ ML ทำนาย</p>
    
    {/* Timeframe Buttons */}
    <div className="flex gap-1">
      {['3M', '6M', '1Y', 'ALL'].map(...)}
    </div>
  </div>
  
  {/* Legend */}
  <div className="flex gap-4">
    <div>━━━━━ สีเขียว = Historical</div>
    <div>- - - สีม่วง = ML Forecast</div>
  </div>
</div>
```

### 2. Summary Cards
```tsx
<div className="grid grid-cols-3 gap-3">
  <Card className="bg-green-50 border-green-200">
    <Calendar icon />
    <p className="text-2xl">{historicalCount}</p>
    <p className="text-xs">เดือนที่มีข้อมูลจริง</p>
  </Card>
  
  <Card className="bg-purple-50 border-purple-200">
    <GiBrain icon />
    <p className="text-2xl">{forecastCount}</p>
    <p className="text-xs">เดือนที่ ML ทำนาย</p>
  </Card>
  
  <Card className="bg-blue-50 border-blue-200">
    <MdTimeline icon />
    <p className="text-2xl">{totalCount}</p>
    <p className="text-xs">เดือนรวมทั้งหมด</p>
  </Card>
</div>
```

---

## 🔍 Data Flow

```
1. User clicks "วิเคราะห์"
   ↓
2. Frontend → POST /recommend-planting-date
   ↓
3. Backend:
   ├─ Query CropPrice (historical data)
   ├─ Run ML Model (26 scenarios)
   ├─ Aggregate by month
   └─ Combine: historical + ml_forecast
   ↓
4. Frontend receives:
   ├─ historical_prices: []
   ├─ ml_forecast: []
   └─ combined_timeline: []
   ↓
5. Render Timeline Chart:
   ├─ Filter by timeframe
   ├─ Draw historical line (green, solid)
   ├─ Draw forecast line (purple, dashed)
   └─ Show summary cards
```

---

## 📊 Response Structure

```typescript
interface TimelineResponse {
  success: boolean;
  crop_type: string;
  province: string;
  growth_days: number;
  
  // ข้อมูลจริงในอดีต
  historical_prices: Array<{
    date: string;        // "2025-05"
    month: string;       // "พฤษภาคม"
    year: number;        // 2025
    average_price: number;
    type: "historical";
  }>;
  
  // ข้อมูลที่ ML ทำนาย
  ml_forecast: Array<{
    date: string;        // "2026-01"
    month: string;       // "มกราคม"
    year: number;        // 2026
    average_price: number;
    type: "ml_forecast";
  }>;
  
  // รวมทั้งหมด (เรียงตาม date)
  combined_timeline: Array<HistoricalData | MLForecast>;
  
  // ... existing fields
}
```

---

## 🎯 ผลลัพธ์

### Before:
- ❌ แสดงแค่กราฟ ML predictions เฉยๆ
- ❌ ไม่เห็นบริบทว่าราคาในอดีตเป็นอย่างไร
- ❌ ไม่สามารถเปรียบเทียบ historical vs forecast

### After:
- ✅ แสดงทั้ง historical + ML forecast ในกราฟเดียว
- ✅ เห็นภาพรวมต่อเนื่องจากอดีต → อนาคต
- ✅ เปรียบเทียบได้ว่า ML ทำนายแตกต่างจากอดีตอย่างไร
- ✅ เลือก timeframe ได้ (3M, 6M, 1Y, ALL)
- ✅ ชัดเจน 100% ว่าข้อมูลมาจากไหน (เส้นทึบ vs เส้นประ)

---

**Status**: ✅ Implemented & Tested
**Charts**: 5 tabs (Timeline, Trend, Comparison, Detail, Scenarios)
**Data Source**: 100% Real (Database + ML Model)
