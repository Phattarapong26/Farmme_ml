# Historical Chart Smooth Improvement

## ✅ ปรับกราฟข้อมูลในอดีตให้ Smooth

---

## 🎨 การเปลี่ยนแปลง:

### 1. **Line Chart** (เส้นกราฟ)

#### ❌ เดิม:
```tsx
<Line 
  type="monotone"           // โค้งนิดหน่อย
  strokeWidth={2}           // เส้นบาง
  dot={(props) => {...}}    // มี dot ทุกจุด (ดูรก)
/>
```

#### ✅ ใหม่:
```tsx
<Line 
  type="natural"            // Smooth curve (โค้งสวย)
  strokeWidth={3}           // เส้นหนาขึ้น
  dot={false}               // ไม่มี dot (สะอาด)
  activeDot={{ r: 6, strokeWidth: 2, stroke: '#fff' }}  // แสดง dot เมื่อ hover
  connectNulls={true}       // เชื่อมข้อมูลที่ขาด
/>
```

---

### 2. **Area Chart** (กราฟพื้นที่)

#### ❌ เดิม:
```tsx
<Area 
  type="monotone"           // โค้งนิดหน่อย
  fillOpacity={0.3}         // พื้นที่เข้มเกินไป
/>
```

#### ✅ ใหม่:
```tsx
<Area 
  type="natural"            // Smooth curve
  strokeWidth={3}           // เส้นหนาขึ้น
  fillOpacity={0.2}         // พื้นที่โปร่งขึ้น (สวยกว่า)
  dot={false}               // ไม่มี dot
  activeDot={{ r: 6, strokeWidth: 2, stroke: '#fff' }}
  connectNulls={true}
/>
```

---

## 🎯 ผลลัพธ์:

### ก่อนปรับ:
- เส้นโค้งน้อย (monotone)
- มี dot ทุกจุด (ดูรก)
- เส้นบาง (strokeWidth: 2)
- ข้อมูลที่ขาดจะขาด

### หลังปรับ:
- ✅ เส้นโค้งสวย (natural curve)
- ✅ ไม่มี dot (สะอาด)
- ✅ เส้นหนาขึ้น (strokeWidth: 3)
- ✅ แสดง dot เมื่อ hover เท่านั้น
- ✅ เชื่อมข้อมูลที่ขาด (connectNulls)

---

## 📊 เปรียบเทียบ:

### Curve Type:
- **monotone**: โค้งแบบ cubic spline (โค้งนิดหน่อย)
- **natural**: โค้งแบบ natural cubic spline (โค้งสวยกว่า, smooth)

### Dot Display:
- **เดิม**: แสดง dot ทุกจุด → ดูรก
- **ใหม่**: ซ่อน dot, แสดงเมื่อ hover → สะอาด

### Line Width:
- **เดิม**: 2px → บาง
- **ใหม่**: 3px → หนาขึ้น, เห็นชัดขึ้น

---

## 🎨 Visual Improvements:

1. **Smoother Curves** ✅
   - เส้นโค้งสวยกว่า
   - ดูเป็นธรรมชาติมากขึ้น

2. **Cleaner Look** ✅
   - ไม่มี dot รบกวน
   - มองเห็นแนวโน้มชัดเจนขึ้น

3. **Better Interaction** ✅
   - Hover แสดง dot พร้อม tooltip
   - ดูข้อมูลแต่ละจุดได้ง่าย

4. **Thicker Lines** ✅
   - เห็นเส้นชัดเจนขึ้น
   - อ่านกราฟง่ายขึ้น

---

## 📝 ไฟล์ที่แก้ไข:

- `frontend/src/components/HistoricalDataChart.tsx`
  - Line Chart: เปลี่ยนเป็น natural curve, ซ่อน dot
  - Area Chart: เปลี่ยนเป็น natural curve, ซ่อน dot

---

## ✅ สรุป:

**กราฟข้อมูลในอดีตที่ `/forecast` ตอนนี้:**
- ✅ Smooth curve (เหมือนกราฟพยากรณ์ราคา)
- ✅ ไม่มี dot รบกวน
- ✅ เส้นหนาขึ้น
- ✅ ดูสวยและอ่านง่ายขึ้น

🎉 **กราฟสวยขึ้นแล้ว!**
