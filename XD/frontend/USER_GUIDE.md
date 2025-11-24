# 📖 Forecast Page User Guide

## Overview
The new `/forecast` page provides comprehensive agricultural data analysis with two main views:
1. **Price Forecast (พยากรณ์ราคา)** - ML-powered price predictions
2. **Historical Data (ข้อมูลในอดีต)** - Past data visualization with multiple chart types

---

## 🎯 View 1: Price Forecast (พยากรณ์ราคา)

### What You'll See:
```
┌─────────────────────────────────────────────────────────┐
│  การพยากรณ์และวิเคราะห์การเกษตร                          │
│  ข้อมูลพยากรณ์ราคาและการวิเคราะห์ข้อมูลในอดีต            │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐  ┌──────────────────┐
│ 📈 พยากรณ์ราคา    │  │ 📊 ข้อมูลในอดีต   │
│   (Active)       │  │   (Inactive)     │
└──────────────────┘  └──────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 📈 การพยากรณ์ราคาพืช - กรุงเทพฯ      [ข้าวโพด ▼]      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ ราคาปัจจุบัน │  │   แนวโน้ม    │  │  คำแนะนำ     │    │
│  │ 119.87 บาท  │  │   ↑ +5%     │  │ ราคาดี ควรปลูก│    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  [Chart showing historical (blue) + forecast (orange)] │
│                                                         │
│  สรุปการพยากรณ์:                                        │
│  • ราคาเฉลี่ยในอดีต: 115.50 บาท/กก.                    │
│  • แนวโน้มราคา: เพิ่มขึ้น                               │
│  • คำแนะนำ: ราคาดี ควรปลูก                             │
│  • ข้อมูลอิงจาก 50 จุดข้อมูลในอดีต                      │
└─────────────────────────────────────────────────────────┘
```

### How to Use:
1. **Select Crop Type**: Click the dropdown (e.g., ข้าวโพด, ข้าว, มันสำปะหลัง)
2. **View Current Price**: See the current market price
3. **Check Trend**: Look at the trend indicator (↑ increasing or ↓ decreasing)
4. **Read Recommendation**: Get actionable advice based on predictions
5. **Analyze Chart**: 
   - Blue dots = Historical data (past 6 months)
   - Orange dots = Forecast data (next 6 months)

---

## 📊 View 2: Historical Data (ข้อมูลในอดีต)

### What You'll See:
```
┌─────────────────────────────────────────────────────────┐
│  การพยากรณ์และวิเคราะห์การเกษตร                          │
│  ข้อมูลพยากรณ์ราคาและการวิเคราะห์ข้อมูลในอดีต            │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐  ┌──────────────────┐
│ 📈 พยากรณ์ราคา    │  │ 📊 ข้อมูลในอดีต   │
│   (Inactive)     │  │   (Active)       │
└──────────────────┘  └──────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 💰 ข้อมูลราคาในอดีต - กรุงเทพฯ        [ข้าวโพด ▼]      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Data Type:                                            │
│  [💰 ราคา] [🌡️ อุณหภูมิ] [💧 ปริมาณฝน]                 │
│                                                         │
│  Time Range:                                           │
│  [1 เดือน] [3 เดือน] [6 เดือน] [1 ปี]                 │
│                                                         │
│  Chart Type:                                           │
│  [เส้น] [แท่ง] [พื้นที่]                               │
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ ค่าเฉลี่ย  │ │  สูงสุด   │ │  ต่ำสุด   │ │ แนวโน้ม  │  │
│  │ 115.50   │ │ 150.25   │ │  85.30   │ │ ↑ +8.5% │  │
│  │ บาท/กก.  │ │ บาท/กก.  │ │ บาท/กก.  │ │         │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                         │
│  [Interactive Chart with Selected Filters]            │
│                                                         │
│  📅 สรุปข้อมูล:                                         │
│  • จำนวนข้อมูล: 50 จุดข้อมูล                           │
│  • ช่วงเวลา: 6 เดือน                                   │
│  • ประเภทข้อมูล: ราคา (บาท/กก.)                        │
│  • ข้อมูลจากฐานข้อมูลการพยากรณ์ที่บันทึกไว้ในระบบ       │
└─────────────────────────────────────────────────────────┘
```

### How to Use:

#### Step 1: Select Data Type
Click one of three buttons:
- **💰 ราคา** - View price trends (บาท/กก.)
- **🌡️ อุณหภูมิ** - View temperature trends (°C)
- **💧 ปริมาณฝน** - View rainfall patterns (มม.)

#### Step 2: Select Time Range
Choose how far back to look:
- **1 เดือน** - Last 30 days
- **3 เดือน** - Last 90 days
- **6 เดือน** - Last 180 days (default)
- **1 ปี** - Last 365 days

#### Step 3: Select Chart Type
Choose visualization style:
- **เส้น** - Line chart (best for trends)
- **แท่ง** - Bar chart (best for comparisons)
- **พื้นที่** - Area chart (best for volume)

#### Step 4: Analyze Statistics
View four key metrics:
- **ค่าเฉลี่ย** - Average value over selected period
- **สูงสุด** - Maximum value recorded
- **ต่ำสุด** - Minimum value recorded
- **แนวโน้ม** - Trend percentage (↑ up or ↓ down)

#### Step 5: Select Crop Type
Use the dropdown to switch between:
- ข้าวโพด (Corn)
- ข้าว (Rice)
- มันสำปะหลัง (Cassava)
- ยางพารา (Rubber)
- อ้อย (Sugarcane)

---

## 🎨 Visual Guide

### Color Coding:
- **Blue** 🔵 - Historical data (actual recorded values)
- **Orange** 🟠 - Forecast data (ML predictions)
- **Green** 🟢 - Positive trend (increasing)
- **Red** 🔴 - Negative trend (decreasing)

### Icons:
- 📈 - Price forecast
- 📊 - Historical data
- 💰 - Price data
- 🌡️ - Temperature data
- 💧 - Rainfall data
- ↑ - Increasing trend
- ↓ - Decreasing trend
- 📅 - Calendar/time info

---

## 💡 Tips for Best Results

### Price Forecast View:
1. **Check Multiple Crops**: Compare different crops to find the best opportunity
2. **Look at Trends**: Upward trend (↑) suggests good time to plant
3. **Read Recommendations**: Follow the AI-powered advice
4. **Monitor Regularly**: Prices change, check back frequently

### Historical Data View:
1. **Start with 6 Months**: Good balance of detail and overview
2. **Compare Data Types**: Look at price, temperature, and rainfall together
3. **Use Line Charts**: Best for spotting trends over time
4. **Check Statistics**: Average tells you the typical value
5. **Watch Trends**: Positive trend means values are increasing

---

## 🔍 Example Use Cases

### Use Case 1: Deciding What to Plant
1. Go to **Price Forecast** view
2. Check each crop type (ข้าวโพด, ข้าว, etc.)
3. Look for:
   - High current price
   - Upward trend (↑)
   - Positive recommendation
4. Choose the crop with best indicators

### Use Case 2: Analyzing Past Performance
1. Go to **Historical Data** view
2. Select **ราคา** (Price)
3. Choose **6 เดือน** (6 months)
4. Select your crop type
5. Analyze:
   - Is average price good?
   - Is trend positive?
   - Are there seasonal patterns?

### Use Case 3: Weather Impact Analysis
1. Go to **Historical Data** view
2. First, check **ราคา** (Price) - note the trend
3. Then, check **ปริมาณฝน** (Rainfall) - see if high rainfall
4. Compare: Does high rainfall correlate with price changes?
5. Use insights for future planning

---

## 🚀 Quick Start Guide

### For First-Time Users:
1. **Open** the `/forecast` page
2. **See** the default Price Forecast view
3. **Select** a crop type from dropdown
4. **Read** the recommendation
5. **Click** "ข้อมูลในอดีต" to see historical data
6. **Experiment** with different filters

### For Regular Users:
1. **Check** Price Forecast daily for current prices
2. **Monitor** trends for your crops
3. **Review** Historical Data weekly for patterns
4. **Compare** different time ranges
5. **Make** informed planting decisions

---

## ❓ FAQ

**Q: What do the blue and orange dots mean?**
A: Blue dots are historical data (actual past prices), orange dots are forecast data (ML predictions for the future).

**Q: How accurate are the predictions?**
A: The ML model has 76.46% accuracy (R² score), which is good for agricultural price prediction.

**Q: How often is data updated?**
A: Data is updated in real-time from the database. New predictions are added continuously.

**Q: Can I see data for my specific province?**
A: Yes! Use the province selector in the navigation bar to filter data by location.

**Q: What if I don't see data for my crop?**
A: The system needs at least 10 data points. If you don't see data, it means not enough predictions have been made yet.

**Q: How do I interpret the trend percentage?**
A: Positive (+) means increasing, negative (-) means decreasing. Larger numbers mean stronger trends.

---

## 📞 Support

If you encounter any issues or have questions:
1. Check the system health at `/health` endpoint
2. Verify database connection is active
3. Ensure ML model is loaded
4. Contact system administrator if problems persist

---

**Happy Farming! 🌾🚜**
