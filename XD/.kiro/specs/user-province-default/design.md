# Design Document

## Overview

ฟีเจอร์นี้จะปรับปรุงประสบการณ์ผู้ใช้ในหน้า Overview โดยแสดงข้อมูลของจังหวัดที่ผู้ใช้อยู่โดยอัตโนมัติ แทนที่จะต้องให้ผู้ใช้เลือกจังหวัดทุกครั้ง การออกแบบนี้จะใช้ข้อมูล province ที่มีอยู่แล้วในระบบ backend และปรับปรุงการจัดการข้อมูลผู้ใช้ใน frontend

## Architecture

### System Components

```
┌─────────────────┐
│   Frontend      │
│  (React/TS)     │
│                 │
│  ┌───────────┐  │
│  │ useAuth   │  │ ← เพิ่ม province ใน User interface
│  │ Hook      │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │Dashboard  │  │ ← ใช้ province จาก useAuth
│  │Overview   │  │
│  └───────────┘  │
└────────┬────────┘
         │
         │ HTTP/JSON
         │
┌────────▼────────┐
│   Backend       │
│  (FastAPI)      │
│                 │
│  ┌───────────┐  │
│  │ Auth      │  │ ← ส่ง province ใน login response (มีอยู่แล้ว)
│  │ Router    │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Database  │  │ ← เก็บ province ในตาราง users (มีอยู่แล้ว)
│  │ (SQLite)  │  │
│  └───────────┘  │
└─────────────────┘
```

### Data Flow

1. **Login/Register Flow**:
   ```
   User → Login/Register → Backend validates → Backend returns user data (including province)
   → Frontend stores in localStorage → useAuth hook reads and provides to components
   ```

2. **Overview Page Load Flow**:
   ```
   User opens /overview → DashboardOverview component mounts → useAuth provides user data
   → Component checks user.province → If exists, set as selectedProvince → Fetch dashboard data
   ```

## Components and Interfaces

### 1. Frontend - User Interface (TypeScript)

**Current State:**
```typescript
interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
}
```

**Updated State:**
```typescript
interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  province?: string;  // เพิ่มฟิลด์นี้
}
```

### 2. Frontend - useAuth Hook

**Location:** `frontend/src/hooks/useAuth.ts`

**Changes Required:**
- อัพเดท User interface ให้รวม province
- ไม่ต้องเปลี่ยนโลจิกอื่นๆ เพราะ localStorage.setItem('user') ใน LocalAuth.tsx จะเก็บ province ที่ backend ส่งมาอัตโนมัติ

### 3. Frontend - LocalAuth Component

**Location:** `frontend/src/pages/LocalAuth.tsx`

**Current Behavior:**
```typescript
// ใน handleLogin และ handleRegister
localStorage.setItem('user', JSON.stringify(data.user));
```

**Analysis:**
- Component นี้ไม่ต้องแก้ไข เพราะมันเก็บ data.user ทั้งหมดที่ backend ส่งมา
- Backend ส่ง province มาแล้วใน login response (ตรวจสอบแล้วใน auth.py)

### 4. Frontend - DashboardOverview Component

**Location:** `frontend/src/pages/DashboardOverview.tsx`

**Current State:**
```typescript
const [selectedProvince, setSelectedProvince] = useState<string | null>(null);
```

**Updated Logic:**
```typescript
const { user } = useAuth();
const [selectedProvince, setSelectedProvince] = useState<string | null>(null);

// เพิ่ม useEffect เพื่อตั้งค่า province เริ่มต้น
useEffect(() => {
  if (user?.province && !selectedProvince) {
    setSelectedProvince(user.province);
  }
}, [user]);
```

**Behavior:**
- เมื่อ component mount และมี user.province → ตั้งค่า selectedProvince อัตโนมัติ
- ถ้าผู้ใช้เปลี่ยนจังหวัดด้วยตัวเอง → selectedProvince จะเปลี่ยนตาม แต่ไม่บันทึกลง localStorage
- เมื่อ refresh หรือกลับมาหน้านี้ใหม่ → จะใช้ user.province อีกครั้ง

### 5. Backend - Auth Router

**Location:** `backend/app/routers/auth.py`

**Current State:**
```python
# ใน login endpoint
return AuthResponse(
    success=True,
    message="เข้าสู่ระบบสำเร็จ",
    user={
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "province": user.province  # มีอยู่แล้ว!
    },
    token=token
)
```

**Analysis:**
- Backend ส่ง province มาแล้ว ✅
- ไม่ต้องแก้ไข backend

## Data Models

### User Model (Database)

**Table:** `users`

**Existing Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    province TEXT,              -- มีอยู่แล้ว
    water_availability TEXT,
    budget_level TEXT,
    experience_crops TEXT,
    risk_tolerance TEXT,
    time_constraint INTEGER,
    preference TEXT,
    soil_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Analysis:**
- Database schema มี province อยู่แล้ว ✅
- ไม่ต้องแก้ไข database

### LocalStorage Data Structure

**Key:** `user`

**Current Value:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "farmer1",
  "full_name": "John Doe"
}
```

**Updated Value:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "farmer1",
  "full_name": "John Doe",
  "province": "เชียงใหม่"
}
```

## Error Handling

### Scenario 1: User has no province in profile

**Handling:**
```typescript
// ใน DashboardOverview.tsx
useEffect(() => {
  if (user?.province && !selectedProvince) {
    setSelectedProvince(user.province);
  }
  // ถ้าไม่มี province → selectedProvince จะเป็น null
  // → แสดงข้อความ "เลือกจังหวัดเพื่อดูข้อมูล" เหมือนเดิม
}, [user]);
```

**User Experience:**
- ถ้าผู้ใช้ไม่มี province → แสดงหน้าเลือกจังหวัดเหมือนเดิม
- ไม่มี error แสดง เพียงแต่ไม่ auto-select

### Scenario 2: Province in profile doesn't exist in database

**Handling:**
```typescript
// ใน DashboardOverview.tsx
useEffect(() => {
  if (user?.province && provinces.includes(user.province) && !selectedProvince) {
    setSelectedProvince(user.province);
  }
}, [user, provinces]);
```

**User Experience:**
- ตรวจสอบว่า province ที่เก็บไว้มีอยู่ในรายการจังหวัดจริง
- ถ้าไม่มี → ไม่ auto-select และให้ผู้ใช้เลือกเอง

### Scenario 3: User not logged in

**Handling:**
```typescript
// ใน DashboardOverview.tsx
const { user } = useAuth();

// ถ้า user เป็น null → useEffect จะไม่ทำงาน
// → selectedProvince จะเป็น null → แสดงหน้าเลือกจังหวัด
```

**User Experience:**
- ผู้ใช้ที่ไม่ได้ login จะเห็นหน้าเลือกจังหวัดเหมือนเดิม
- ไม่มีผลกระทบต่อ guest users

## Testing Strategy

### Unit Tests

1. **useAuth Hook Tests**
   - Test: User interface includes province field
   - Test: Hook correctly parses user data with province from localStorage
   - Test: Hook handles missing province gracefully

2. **DashboardOverview Component Tests**
   - Test: Component sets selectedProvince when user has province
   - Test: Component doesn't set selectedProvince when user has no province
   - Test: Component validates province exists in provinces list
   - Test: User can manually change province after auto-selection

### Integration Tests

1. **Login Flow Test**
   - Test: Login returns user data with province
   - Test: Province is stored in localStorage
   - Test: useAuth hook provides province to components

2. **Overview Page Test**
   - Test: Opening /overview with logged-in user auto-selects province
   - Test: Dashboard data loads automatically for user's province
   - Test: Manual province selection still works
   - Test: Refresh page maintains user's province (not manual selection)

### Manual Testing Checklist

1. **New User Registration**
   - [ ] Register with province → Login → Open /overview → Province auto-selected
   - [ ] Register without province → Login → Open /overview → No auto-selection

2. **Existing User Login**
   - [ ] Login with province → Open /overview → Province auto-selected
   - [ ] Login without province → Open /overview → No auto-selection

3. **Province Selection**
   - [ ] Auto-selected province → Change to different province → Works
   - [ ] Refresh page → Returns to user's province (not manual selection)
   - [ ] Navigate away and back → Returns to user's province

4. **Edge Cases**
   - [ ] User with invalid province → No auto-selection, no error
   - [ ] Guest user (not logged in) → Normal behavior, no auto-selection
   - [ ] User updates province in profile → Next login reflects new province

## Implementation Notes

### Minimal Changes Required

1. **Frontend Changes (2 files)**:
   - `frontend/src/hooks/useAuth.ts` - เพิ่ม province ใน User interface
   - `frontend/src/pages/DashboardOverview.tsx` - เพิ่ม useEffect สำหรับ auto-select

2. **Backend Changes**:
   - ไม่ต้องแก้ไข (province ถูกส่งมาแล้ว)

3. **Database Changes**:
   - ไม่ต้องแก้ไข (province field มีอยู่แล้ว)

### Performance Considerations

- **No Additional API Calls**: ใช้ข้อมูลที่มีอยู่แล้วใน localStorage
- **No Database Changes**: ไม่มีผลกระทบต่อ database performance
- **Minimal Re-renders**: useEffect จะทำงานเพียงครั้งเดียวเมื่อ component mount

### Backward Compatibility

- **Existing Users**: ผู้ใช้เก่าที่ไม่มี province จะไม่ได้รับผลกระทบ
- **Guest Users**: ผู้ใช้ที่ไม่ได้ login จะใช้งานได้เหมือนเดิม
- **API Compatibility**: ไม่มีการเปลี่ยนแปลง API endpoints

## Security Considerations

- **Data Validation**: Province จะถูก validate กับรายการจังหวัดที่มีจริง
- **No Sensitive Data**: Province ไม่ใช่ข้อมูลที่ sensitive
- **LocalStorage Security**: ข้อมูลใน localStorage เป็น read-only และไม่มี sensitive data
- **No Authorization Changes**: ไม่มีการเปลี่ยนแปลง authorization logic

## Future Enhancements

1. **Remember Manual Selection**: เก็บจังหวัดที่ผู้ใช้เลือกด้วยตัวเองไว้ใน session
2. **Province Update UI**: เพิ่มปุ่ม "ตั้งเป็นจังหวัดหลัก" ในหน้า Overview
3. **Multiple Provinces**: รองรับผู้ใช้ที่มีฟาร์มหลายจังหวัด
4. **Province Analytics**: แสดงสถิติการใช้งานตามจังหวัด
