# Dashboard Overview - Enhanced Layout Design

## Dynamic & Engaging Layout

### Key Design Principles
1. **Visual Hierarchy**: Important data gets larger, prominent cards
2. **Mixed Sizes**: Variety in card dimensions to break monotony
3. **Color Coding**: Different colors for different data categories
4. **Interactive Elements**: Hover effects, animations, tooltips
5. **Asymmetric Grid**: Not everything in perfect rows
6. **Whitespace**: Breathing room between sections
7. **Progressive Disclosure**: Show summary first, details on interaction

## Layout Grid System

### CSS Grid Configuration
```css
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1.5rem;
  padding: 2rem;
}

/* Hero Stats - Full Width */
.stats-row {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

/* Featured Chart - Large */
.featured-chart {
  grid-column: span 8;
  min-height: 400px;
}

/* Insights Sidebar */
.insights-sidebar {
  grid-column: span 4;
  position: sticky;
  top: 100px;
}

/* Medium Charts */
.medium-chart {
  grid-column: span 6;
  min-height: 350px;
}

/* Small Charts */
.small-chart {
  grid-column: span 4;
  min-height: 300px;
}
```


## Visual Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│                          Navbar                                   │
└──────────────────────────────────────────────────────────────────┘

🌊 Animated Ripple Background

┌──────────────────────────────────────────────────────────────────┐
│  📍 กรุงเทพมหานคร [เปลี่ยนจังหวัด ▼]                            │
│  ภาพรวมข้อมูลเกษตรกรรมและเศรษฐกิจ                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ 💰 ราคา  │ │ 👨‍🌾 เกษตร│ │ 🌡️ อากาศ│ │ 🌱 ผลกำไร│ │ 📊 ROI   │
│  45.5฿   │ │  39,165  │ │  32.5°C  │ │  265K฿   │ │  500%    │
│  ↗️ +5.2%│ │  คน      │ │  ☀️ แดด │ │  /รอบ    │ │  ผลตอบแทน│
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘

┌─────────────────────────────────────────┐ ┌──────────────────┐
│  📈 แนวโน้มราคาตามประเภทตลาด (30 วัน)  │ │ 💡 ข้อมูลเชิงลึก │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ │                  │
│                                         │ │ 🌱 ทำไมคะน้า    │
│  [Interactive Multi-Line Chart]        │ │ ปลูกได้ดี?       │
│  • ซุปเปอร์มาร์เก็ต (สีเขียว)          │ │                  │
│  • พ่อค้าคนกลาง (สีน้ำเงิน)            │ │ ✓ ดินเหมาะสม    │
│  • ตลาดสด (สีส้ม)                      │ │   (0.74)        │
│                                         │ │ ✓ อากาศดี       │
│  Hover: แสดงราคาแต่ละวัน               │ │   (24-26°C)     │
└─────────────────────────────────────────┘ │ ✓ ตลาดต้องการ  │
                                            │   (1.12)        │
┌──────────────────┐ ┌──────────────────┐  │                  │
│ 🌧️ สภาพอากาศ    │ │ 🥬 สัดส่วนพืช    │  │ 💰 กำไรเฉลี่ย   │
│ & ดัชนีแห้งแล้ง   │ │ ตามหมวดหมู่      │  │ 265,179฿        │
│                  │ │                  │  │                  │
│ [Combo Chart]    │ │ [Doughnut]       │  │ 📋 คำแนะนำ      │
│ • อุณหภูมิ       │ │                  │  │ • ปลูกคะน้า     │
│ • ความชื้น       │ │  ผักใบ 35%       │  │ • ใช้ดินร่วน    │
│ • ฝน            │ │  ผักผล 28%       │  │ • ขายซุปเปอร์ฯ  │
│ • ดัชนีแห้งแล้ง  │ │  สมุนไพร 20%     │  └──────────────────┘
└──────────────────┘ └──────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  🎯 ความสัมพันธ์: ทักษะเกษตรกร vs ประสิทธิภาพผลผลิต        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                              │
│  [Interactive Scatter Plot with Trend Line]                 │
│  • แต่ละจุด = เกษตรกร 1 คน                                  │
│  • สีต่างกัน = ชนิดพืชต่างกัน                               │
│  • Hover: แสดงรายละเอียดเกษตรกร                             │
│                                                              │
│  📊 Insight: ทักษะสูง → ผลผลิตดีขึ้น 45%                    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────┐ ┌──────────────────────────────────┐
│ 💹 ผลกำไรสูงสุด      │ │ 📊 ตัวชี้วัดเศรษฐกิจ (90 วัน)   │
│ (Top 10 พืช)         │ │                                  │
│                      │ │ [Multi-Line Timeline Chart]     │
│ [Horizontal Bar]     │ │ • ราคาน้ำมัน                     │
│                      │ │ • ราคาปุ๋ย                       │
│ คะน้า    ████████    │ │ • ดัชนีความต้องการผัก           │
│ มะเขือฯ  ██████      │ │ • อัตราเงินเฟ้อ                  │
│ พริก     █████       │ │                                  │
│ ...                  │ │ 💡 Trend: ราคาปุ๋ยขึ้น 12%       │
└──────────────────────┘ └──────────────────────────────────┘

┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ 🌍 ประเภทดิน     │ │ ✅ อัตราสำเร็จ   │ │ 🏆 ความเหมาะสม  │
│                  │ │ ตามชนิดดิน       │ │ ของพืช (Top 15)  │
│ [Pie Chart]      │ │                  │ │                  │
│                  │ │ [Grouped Bar]    │ │ [Column Chart]   │
│  ดินร่วน 45%     │ │                  │ │                  │
│  ดินเหนียว 30%   │ │ คะน้า:           │ │ คะน้า    ████    │
│  ดินทราย 25%     │ │ • ดินร่วน 84%    │ │ กวางตุ้ง ███     │
│                  │ │ • ดินเหนียว 72%  │ │ ผักบุ้ง  ███     │
└──────────────────┘ └──────────────────┘ └──────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  💼 ROI & Margin Analysis (Top 10 พืช)                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                              │
│  [Combination Chart: Column + Line]                         │
│  • Column = ROI (%)                                         │
│  • Line = Margin (%)                                        │
│                                                              │
│  คะน้า: ROI 500% | Margin 90%  ⭐ ดีเยี่ยม                 │
└──────────────────────────────────────────────────────────────┘
```


## Card Design Variations

### 1. Stats Card (Animated)
```tsx
<Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
  <CardContent className="p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-emerald-600 font-medium">💰 ราคาเฉลี่ย</p>
        <AnimatedNumber value={45.5} className="text-3xl font-bold text-emerald-700" />
        <p className="text-xs text-emerald-500">บาท/กก.</p>
      </div>
      <TrendIndicator value={5.2} />
    </div>
  </CardContent>
</Card>
```

### 2. Featured Chart Card (Large)
```tsx
<Card className="col-span-8 bg-white shadow-xl rounded-2xl overflow-hidden">
  <CardHeader className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
    <CardTitle className="flex items-center gap-2">
      <TrendingUp className="w-6 h-6" />
      📈 แนวโน้มราคาตามประเภทตลาด
    </CardTitle>
  </CardHeader>
  <CardContent className="p-6">
    <CanvasJSChart options={priceChartOptions} />
  </CardContent>
</Card>
```

### 3. Insights Card (Sticky Sidebar)
```tsx
<Card className="col-span-4 bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-200 sticky top-24">
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      <Lightbulb className="w-6 h-6 text-yellow-500 animate-pulse" />
      💡 ข้อมูลเชิงลึก
    </CardTitle>
  </CardHeader>
  <CardContent className="space-y-4">
    {insights.map(insight => (
      <InsightBadge key={insight.id} insight={insight} />
    ))}
  </CardContent>
</Card>
```

### 4. Interactive Chart Card (Medium)
```tsx
<Card className="col-span-6 hover:shadow-2xl transition-shadow duration-300">
  <CardHeader className="border-b">
    <CardTitle>🌧️ สภาพอากาศ & ดัชนีแห้งแล้ง</CardTitle>
    <CardDescription>30 วันที่ผ่านมา</CardDescription>
  </CardHeader>
  <CardContent className="p-6">
    <CanvasJSChart options={weatherChartOptions} />
  </CardContent>
  <CardFooter className="bg-gray-50 text-sm text-gray-600">
    💡 Tip: คลิกที่ legend เพื่อซ่อน/แสดงข้อมูล
  </CardFooter>
</Card>
```

## Animation & Interaction Patterns

### 1. Fade-In on Scroll
```tsx
const FadeInCard = ({ children, delay = 0 }) => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTimeout(() => setIsVisible(true), delay);
        }
      },
      { threshold: 0.1 }
    );
    
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [delay]);
  
  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
      }`}
    >
      {children}
    </div>
  );
};
```

### 2. Hover Effects
```css
.chart-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.chart-card:hover .chart-title {
  color: #10b981;
}
```

### 3. Number Counter Animation
```tsx
const AnimatedNumber = ({ value, duration = 2000 }) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let start = 0;
    const end = value;
    const increment = end / (duration / 16);
    
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);
    
    return () => clearInterval(timer);
  }, [value, duration]);
  
  return <span>{count.toLocaleString('th-TH')}</span>;
};
```


## Color Palette & Theming

### Primary Colors
```css
:root {
  /* Agricultural Green */
  --emerald-50: #ecfdf5;
  --emerald-100: #d1fae5;
  --emerald-500: #10b981;
  --emerald-600: #059669;
  --emerald-700: #047857;
  
  /* Data Blue */
  --blue-50: #eff6ff;
  --blue-500: #3b82f6;
  --blue-600: #2563eb;
  
  /* Warning Orange */
  --orange-50: #fff7ed;
  --orange-500: #f59e0b;
  --orange-600: #d97706;
  
  /* Insight Yellow */
  --yellow-50: #fefce8;
  --yellow-500: #eab308;
  
  /* Success/Profit */
  --green-500: #22c55e;
  
  /* Danger/Loss */
  --red-500: #ef4444;
}
```

### Card Color Coding
- **Price Data**: Blue gradient
- **Weather Data**: Sky blue gradient
- **Profitability**: Green gradient
- **Insights**: Yellow/Orange gradient
- **Soil Data**: Brown/Earth tones
- **Economic**: Purple gradient

## Responsive Behavior

### Desktop (≥1280px)
```css
.dashboard-grid {
  grid-template-columns: repeat(12, 1fr);
}

.stats-row {
  grid-template-columns: repeat(5, 1fr);
}

.featured-chart { grid-column: span 8; }
.insights-sidebar { grid-column: span 4; }
.medium-chart { grid-column: span 6; }
.small-chart { grid-column: span 4; }
```

### Tablet (768px - 1279px)
```css
.dashboard-grid {
  grid-template-columns: repeat(8, 1fr);
}

.stats-row {
  grid-template-columns: repeat(3, 1fr);
}

.featured-chart { grid-column: span 8; }
.insights-sidebar { grid-column: span 8; position: relative; }
.medium-chart { grid-column: span 4; }
.small-chart { grid-column: span 4; }
```

### Mobile (<768px)
```css
.dashboard-grid {
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 1rem;
}

.stats-row {
  grid-template-columns: repeat(2, 1fr);
}

.featured-chart,
.insights-sidebar,
.medium-chart,
.small-chart {
  grid-column: span 1;
}
```

## Accessibility Features

1. **Keyboard Navigation**: All interactive elements accessible via Tab
2. **Screen Reader Support**: Proper ARIA labels on charts
3. **Color Contrast**: WCAG AA compliant (4.5:1 minimum)
4. **Focus Indicators**: Clear visual focus states
5. **Alt Text**: Descriptive text for all visual elements
6. **Reduced Motion**: Respect prefers-reduced-motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```


## Enhanced Stats Cards with Icons & NumberTicker

### Icon Library
```tsx
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Thermometer,
  Droplets,
  Sprout,
  BarChart3,
  PieChart,
  Activity,
  Target,
  Award,
  AlertCircle,
  CheckCircle,
  ArrowUpRight,
  ArrowDownRight,
  Leaf,
  Sun,
  Cloud,
  CloudRain,
  Wind,
  Zap,
  TrendingFlat
} from 'lucide-react';
```

### Stats Card with NumberTicker & Icons

```tsx
import { NumberTicker } from "@/registry/magicui/number-ticker";
import { DollarSign, TrendingUp } from 'lucide-react';

const StatsCard = ({ title, value, unit, trend, icon: Icon, color }) => {
  return (
    <Card className={`bg-gradient-to-br ${color} border-none hover:shadow-xl transition-all duration-300 hover:-translate-y-2`}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-xl bg-white/50 backdrop-blur-sm`}>
            <Icon className="w-6 h-6" />
          </div>
          {trend && (
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
              trend > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
              {trend > 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
              {Math.abs(trend)}%
            </div>
          )}
        </div>
        <p className="text-sm font-medium text-gray-600 mb-2">{title}</p>
        <div className="flex items-baseline gap-2">
          <NumberTicker 
            value={value} 
            className="text-3xl font-bold text-gray-900"
          />
          <span className="text-sm text-gray-500">{unit}</span>
        </div>
      </CardContent>
    </Card>
  );
};
```

### Stats Cards Implementation

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
  {/* Average Price Card */}
  <StatsCard
    title="ราคาเฉลี่ย"
    value={45.5}
    unit="บาท/กก."
    trend={5.2}
    icon={DollarSign}
    color="from-emerald-50 to-emerald-100"
  />
  
  {/* Farmers Count Card */}
  <StatsCard
    title="จำนวนเกษตรกร"
    value={39165}
    unit="คน"
    trend={2.1}
    icon={Users}
    color="from-blue-50 to-blue-100"
  />
  
  {/* Weather Card */}
  <StatsCard
    title="อุณหภูมิปัจจุบัน"
    value={32.5}
    unit="°C"
    trend={-1.5}
    icon={Thermometer}
    color="from-orange-50 to-orange-100"
  />
  
  {/* Profit Card */}
  <StatsCard
    title="ผลกำไรเฉลี่ย"
    value={265179}
    unit="บาท/รอบ"
    trend={12.3}
    icon={TrendingUp}
    color="from-green-50 to-green-100"
  />
  
  {/* ROI Card */}
  <StatsCard
    title="ROI เฉลี่ย"
    value={500}
    unit="%"
    trend={8.7}
    icon={Target}
    color="from-purple-50 to-purple-100"
  />
</div>
```

### Additional Icon Usage in Charts

```tsx
// Chart Headers with Icons
<CardHeader className="flex flex-row items-center gap-2">
  <BarChart3 className="w-5 h-5 text-blue-500" />
  <CardTitle>แนวโน้มราคาตามประเภทตลาด</CardTitle>
</CardHeader>

// Insights Section with Icons
<div className="flex items-start gap-3">
  <div className="p-2 bg-green-100 rounded-lg">
    <CheckCircle className="w-5 h-5 text-green-600" />
  </div>
  <div>
    <h4 className="font-semibold">ดินเหมาะสม</h4>
    <p className="text-sm text-gray-600">คะแนนความเหมาะสม 0.74</p>
  </div>
</div>

// Weather Icons
<div className="flex items-center gap-2">
  <Sun className="w-4 h-4 text-yellow-500" />
  <span>แดดจัด</span>
</div>

<div className="flex items-center gap-2">
  <CloudRain className="w-4 h-4 text-blue-500" />
  <span>ฝนตก 5.2 มม.</span>
</div>
```

### Icon Color Mapping

```tsx
const iconColorMap = {
  price: 'text-emerald-600',
  farmers: 'text-blue-600',
  weather: 'text-orange-600',
  profit: 'text-green-600',
  roi: 'text-purple-600',
  soil: 'text-amber-600',
  water: 'text-cyan-600',
  success: 'text-green-500',
  warning: 'text-yellow-500',
  danger: 'text-red-500'
};
```

### NumberTicker Configuration

```tsx
// Basic Usage
<NumberTicker value={45.5} />

// With Decimal Places
<NumberTicker 
  value={45.5} 
  decimalPlaces={2}
/>

// With Formatting
<NumberTicker 
  value={265179} 
  className="text-3xl font-bold"
  format={(num) => num.toLocaleString('th-TH')}
/>

// With Duration
<NumberTicker 
  value={500} 
  duration={2000}
  className="text-4xl font-bold text-purple-700"
/>

// With Prefix/Suffix
<div className="flex items-baseline gap-1">
  <span className="text-lg">฿</span>
  <NumberTicker value={45.5} className="text-3xl font-bold" />
  <span className="text-sm text-gray-500">/กก.</span>
</div>
```

