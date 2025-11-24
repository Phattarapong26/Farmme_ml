# Design Document

## Overview

Dashboard UI Redesign เป็นการปรับปรุงการออกแบบหน้า Dashboard Overview ให้มีความสวยงาม ทันสมัย และสอดคล้องกับธีมของหน้าอื่นๆ โดยเน้นการแสดงข้อมูลแบบ time-series และปรับปรุงประสบการณ์การใช้งานให้ดีขึ้น

## Architecture

### Design System Alignment

```
┌─────────────────────────────────────────────────────────────┐
│                    Consistent Theme Layer                    │
│  - Color Palette (Emerald Green Primary)                    │
│  - Typography (Same as Forecast/Map pages)                  │
│  - Spacing System (Tailwind defaults)                       │
│  - Component Styles (shadcn/ui)                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  Dashboard Overview Page                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Navigation Bar (Consistent with other pages)        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Province Selector + Time Range Selector            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Statistics Cards (Simplified, Clean Design)        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Chart Category Tabs                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Time-Series Charts (2-column responsive grid)      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: React, TypeScript, TanStack Query
- **Charts**: Recharts (replacing CanvasJS for better React integration)
- **UI Components**: shadcn/ui (consistent with other pages)
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion (for smooth transitions)

## Components and Interfaces

### 1. Redesigned DashboardOverview Component

```typescript
interface DashboardOverviewProps {
  // No props needed
}

interface TimeRange {
  label: string;
  value: '7d' | '30d' | '90d';
  days: number;
}

interface ChartCategory {
  id: string;
  label: string;
  icon: React.ReactNode;
  charts: ChartConfig[];
}
```


### 2. TimeRangeSelector Component

```typescript
interface TimeRangeSelectorProps {
  selectedRange: '7d' | '30d' | '90d';
  onRangeChange: (range: '7d' | '30d' | '90d') => void;
}

// Design: Similar to Forecast page toggle buttons
// - Card-based buttons with gradient when active
// - Smooth hover effects
// - Clear visual feedback
```

### 3. ChartCategoryTabs Component

```typescript
interface ChartCategoryTabsProps {
  categories: ChartCategory[];
  activeCategory: string;
  onCategoryChange: (categoryId: string) => void;
}

// Design: Tab-based navigation
// - Horizontal scrollable tabs on mobile
// - Active tab highlighted with emerald color
// - Icons for each category
```

### 4. SimplifiedStatsCard Component

```typescript
interface SimplifiedStatsCardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: number;
  };
  icon: React.ReactNode;
}

// Design: Clean, minimal cards
// - White background with subtle shadow
// - Icon in emerald circle
// - Large value display
// - Small trend indicator
```

### 5. TimeSeriesChart Component

```typescript
interface TimeSeriesChartProps {
  title: string;
  data: TimeSeriesDataPoint[];
  dataKeys: string[];
  colors: string[];
  yAxisLabel?: string;
  xAxisLabel?: string;
}

interface TimeSeriesDataPoint {
  date: string;
  [key: string]: string | number;
}

// Design: Recharts-based line/area charts
// - Smooth curves
// - Interactive tooltips
// - Legend with toggle functionality
// - Responsive sizing
```

## Data Models

### Frontend Data Models

```typescript
// Time Range Configuration
interface TimeRangeConfig {
  '7d': { label: '7 วัน', days: 7 };
  '30d': { label: '30 วัน', days: 30 };
  '90d': { label: '90 วัน', days: 90 };
}

// Chart Categories
interface ChartCategory {
  id: 'overview' | 'price' | 'weather' | 'economic' | 'farming';
  label: string;
  icon: React.ReactNode;
  description: string;
}

// Simplified Statistics
interface DashboardStats {
  avgPrice: number;
  priceChange: number;
  totalCrops: number;
  currentTemp: number;
  topCrop: string;
  topCropProfit: number;
}
```

## UI/UX Design

### Color Palette (Aligned with Existing Theme)

```css
/* Primary Colors */
--primary-emerald: #10b981;      /* Main brand color */
--primary-emerald-dark: #059669; /* Hover states */
--primary-emerald-light: #d1fae5; /* Backgrounds */

/* Chart Colors */
--chart-blue: #3b82f6;
--chart-green: #10b981;
--chart-orange: #f59e0b;
--chart-purple: #8b5cf6;
--chart-red: #ef4444;
--chart-cyan: #06b6d4;

/* Neutral Colors */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-500: #6b7280;
--gray-700: #374151;
--gray-900: #111827;

/* Background */
--bg-primary: #ffffff;
--bg-secondary: #f9fafb;
```

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Navbar (Consistent with other pages)                       │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Container (max-w-7xl, centered)                            │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Province Selector + Time Range Selector (Flex Row)     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                  │
│  │Stat1│ │Stat2│ │Stat3│ │Stat4│ │Stat5│  (Grid 5 cols)   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Chart Category Tabs                                    │ │
│  │ [Overview] [Price] [Weather] [Economic] [Farming]     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────┐ ┌──────────────────────┐         │
│  │ Chart 1              │ │ Chart 2              │         │
│  │ (Time Series)        │ │ (Time Series)        │         │
│  └──────────────────────┘ └──────────────────────┘         │
│                                                              │
│  ┌──────────────────────┐ ┌──────────────────────┐         │
│  │ Chart 3              │ │ Chart 4              │         │
│  │ (Time Series)        │ │ (Time Series)        │         │
│  └──────────────────────┘ └──────────────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```


### Responsive Breakpoints

```css
/* Mobile First Approach */
/* Mobile: < 768px - Single column, stacked */
.stats-grid { grid-template-columns: repeat(2, 1fr); }
.charts-grid { grid-template-columns: 1fr; }

/* Tablet: 768px - 1023px - 2 columns for stats, 1 for charts */
@media (min-width: 768px) {
  .stats-grid { grid-template-columns: repeat(3, 1fr); }
  .charts-grid { grid-template-columns: 1fr; }
}

/* Desktop: ≥ 1024px - Full grid layout */
@media (min-width: 1024px) {
  .stats-grid { grid-template-columns: repeat(5, 1fr); }
  .charts-grid { grid-template-columns: repeat(2, 1fr); }
}
```

### Typography

```css
/* Consistent with other pages */
--font-heading: 'Inter', sans-serif;
--font-body: 'Inter', sans-serif;

/* Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
```

## Chart Designs (Recharts)

### 1. Price Trend Over Time (Line Chart)

```typescript
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={priceData}>
    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
    <XAxis 
      dataKey="date" 
      stroke="#6b7280"
      tick={{ fontSize: 12 }}
    />
    <YAxis 
      stroke="#6b7280"
      tick={{ fontSize: 12 }}
      label={{ value: 'ราคา (บาท/กก.)', angle: -90, position: 'insideLeft' }}
    />
    <Tooltip 
      contentStyle={{ 
        backgroundColor: 'white', 
        border: '1px solid #e5e7eb',
        borderRadius: '8px'
      }}
    />
    <Legend />
    <Line 
      type="monotone" 
      dataKey="price" 
      stroke="#10b981" 
      strokeWidth={2}
      dot={{ fill: '#10b981', r: 4 }}
      activeDot={{ r: 6 }}
    />
  </LineChart>
</ResponsiveContainer>
```

**Features:**
- Smooth line curves
- Interactive tooltips showing exact values
- Date on x-axis, price on y-axis
- Emerald green color for consistency
- Responsive sizing

### 2. Weather Trends (Multi-Line Chart)

```typescript
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={weatherData}>
    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
    <XAxis dataKey="date" stroke="#6b7280" />
    <YAxis yAxisId="left" stroke="#6b7280" />
    <YAxis yAxisId="right" orientation="right" stroke="#6b7280" />
    <Tooltip />
    <Legend />
    <Line 
      yAxisId="left"
      type="monotone" 
      dataKey="temperature" 
      stroke="#f59e0b" 
      name="อุณหภูมิ (°C)"
    />
    <Line 
      yAxisId="right"
      type="monotone" 
      dataKey="rainfall" 
      stroke="#3b82f6" 
      name="ปริมาณฝน (มม.)"
    />
  </LineChart>
</ResponsiveContainer>
```

**Features:**
- Dual y-axis for different units
- Orange for temperature, blue for rainfall
- Clear legend
- Time-series data over selected range

### 3. Economic Indicators Timeline (Area Chart)

```typescript
<ResponsiveContainer width="100%" height={300}>
  <AreaChart data={economicData}>
    <defs>
      <linearGradient id="colorFuel" x1="0" y1="0" x2="0" y2="1">
        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
      </linearGradient>
    </defs>
    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
    <XAxis dataKey="date" stroke="#6b7280" />
    <YAxis stroke="#6b7280" />
    <Tooltip />
    <Legend />
    <Area 
      type="monotone" 
      dataKey="fuelPrice" 
      stroke="#8b5cf6" 
      fillOpacity={1} 
      fill="url(#colorFuel)"
      name="ราคาน้ำมัน"
    />
  </AreaChart>
</ResponsiveContainer>
```

**Features:**
- Gradient fill for visual appeal
- Shows trends over 90 days
- Multiple economic indicators
- Smooth area curves

### 4. Crop Profitability Comparison (Bar Chart)

```typescript
<ResponsiveContainer width="100%" height={300}>
  <BarChart data={profitabilityData}>
    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
    <XAxis 
      dataKey="cropType" 
      stroke="#6b7280"
      angle={-45}
      textAnchor="end"
      height={100}
    />
    <YAxis stroke="#6b7280" />
    <Tooltip />
    <Bar 
      dataKey="profit" 
      fill="#10b981"
      radius={[8, 8, 0, 0]}
    />
  </BarChart>
</ResponsiveContainer>
```

**Features:**
- Rounded top corners
- Emerald green bars
- Angled labels for readability
- Shows top 10 crops

## Chart Category Organization

### Overview Category
- **Price Trend Over Time**: Line chart showing average price trends
- **Weather Summary**: Multi-line chart with temperature and rainfall
- **Top Crops Performance**: Bar chart of most profitable crops
- **Economic Indicators**: Area chart of key economic factors

### Price Category
- **Price by Market Type**: Multi-line chart comparing different markets
- **Price Distribution**: Area chart showing price ranges
- **Price vs Demand**: Scatter plot showing correlation
- **ROI Analysis**: Bar chart of return on investment

### Weather Category
- **Temperature Trends**: Line chart over time
- **Rainfall Patterns**: Bar chart showing daily rainfall
- **Humidity Levels**: Area chart
- **Drought Index**: Line chart with threshold indicators

### Economic Category
- **Fuel Prices**: Line chart over time
- **Fertilizer Costs**: Line chart
- **Demand Index**: Area chart
- **Inflation Rate**: Line chart

### Farming Category
- **Yield Efficiency**: Scatter plot
- **Farm Size Distribution**: Bar chart
- **Technology Adoption**: Line chart showing trends
- **Farmer Demographics**: Stacked bar chart


## Component Specifications

### TimeRangeSelector Component

**Visual Design:**
```tsx
// Similar to Forecast page toggle buttons
<div className="flex gap-3 justify-center mb-6">
  <Card 
    className={`cursor-pointer transition-all duration-300 hover:scale-105 ${
      selectedRange === '7d'
        ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-lg' 
        : 'bg-white hover:bg-gray-50 shadow-md'
    }`}
    onClick={() => onRangeChange('7d')}
  >
    <CardContent className="p-4 flex items-center gap-2">
      <Calendar className="w-5 h-5" />
      <span className="font-semibold">7 วัน</span>
    </CardContent>
  </Card>
  {/* Similar for 30d and 90d */}
</div>
```

**Behavior:**
- Smooth scale animation on hover
- Gradient background when active
- Updates all charts when clicked
- Maintains selection across page navigation

### ChartCategoryTabs Component

**Visual Design:**
```tsx
<Tabs value={activeCategory} onValueChange={onCategoryChange}>
  <TabsList className="grid w-full grid-cols-5 bg-gray-100 p-1 rounded-lg">
    <TabsTrigger 
      value="overview"
      className="data-[state=active]:bg-white data-[state=active]:text-emerald-600"
    >
      <LayoutDashboard className="w-4 h-4 mr-2" />
      ภาพรวม
    </TabsTrigger>
    <TabsTrigger value="price">
      <TrendingUp className="w-4 h-4 mr-2" />
      ราคา
    </TabsTrigger>
    {/* Similar for other categories */}
  </TabsList>
</Tabs>
```

**Behavior:**
- Horizontal scrollable on mobile
- Active tab highlighted with white background
- Icons for visual clarity
- Smooth transition between categories

### SimplifiedStatsCard Component

**Visual Design:**
```tsx
<Card className="bg-white shadow-md hover:shadow-lg transition-shadow">
  <CardContent className="p-6">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm text-gray-500 mb-1">{title}</p>
        <p className="text-3xl font-bold text-gray-900">
          {value}
          <span className="text-lg text-gray-500 ml-1">{unit}</span>
        </p>
        {trend && (
          <div className={`flex items-center gap-1 mt-2 text-sm ${
            trend.direction === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {trend.direction === 'up' ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
            <span>{trend.value}%</span>
          </div>
        )}
      </div>
      <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center">
        {icon}
      </div>
    </div>
  </CardContent>
</Card>
```

**Features:**
- Clean, minimal design
- Large value display for quick scanning
- Icon in emerald circle
- Trend indicator with arrow
- Subtle hover effect

### ChartContainer Component

**Visual Design:**
```tsx
<Card className="bg-white shadow-md">
  <CardHeader>
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        {icon}
        <CardTitle className="text-lg font-semibold">{title}</CardTitle>
      </div>
      {actions}
    </div>
    {description && (
      <CardDescription className="text-sm text-gray-500">
        {description}
      </CardDescription>
    )}
  </CardHeader>
  <CardContent>
    {children}
  </CardContent>
</Card>
```

**Features:**
- Consistent card styling
- Optional icon and actions
- Description for context
- Padding optimized for charts

## Animations and Transitions

### Page Load Animation

```typescript
// Using Framer Motion
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  {/* Content */}
</motion.div>
```

### Chart Category Transition

```typescript
<motion.div
  key={activeCategory}
  initial={{ opacity: 0, x: 20 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: -20 }}
  transition={{ duration: 0.3 }}
>
  {/* Charts */}
</motion.div>
```

### Stats Card Stagger

```typescript
{stats.map((stat, index) => (
  <motion.div
    key={stat.id}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: index * 0.1 }}
  >
    <SimplifiedStatsCard {...stat} />
  </motion.div>
))}
```

## Error Handling

### Loading States

```tsx
// Skeleton for stats cards
<div className="grid grid-cols-5 gap-4">
  {[...Array(5)].map((_, i) => (
    <Card key={i}>
      <CardContent className="p-6">
        <Skeleton className="h-4 w-20 mb-2" />
        <Skeleton className="h-8 w-24 mb-2" />
        <Skeleton className="h-4 w-16" />
      </CardContent>
    </Card>
  ))}
</div>

// Skeleton for charts
<Card>
  <CardHeader>
    <Skeleton className="h-6 w-40" />
  </CardHeader>
  <CardContent>
    <Skeleton className="h-[300px] w-full" />
  </CardContent>
</Card>
```

### Error States

```tsx
// No data available
<Card className="bg-white shadow-md">
  <CardContent className="p-12 text-center">
    <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
    <p className="text-gray-600 mb-2">ไม่มีข้อมูลสำหรับช่วงเวลานี้</p>
    <p className="text-sm text-gray-500">กรุณาเลือกช่วงเวลาอื่น</p>
  </CardContent>
</Card>

// API error
<Card className="bg-red-50 border-red-200">
  <CardContent className="p-6">
    <div className="flex items-center gap-3">
      <XCircle className="w-6 h-6 text-red-600" />
      <div>
        <p className="font-semibold text-red-900">เกิดข้อผิดพลาด</p>
        <p className="text-sm text-red-700">ไม่สามารถโหลดข้อมูลได้ กรุณาลองใหม่อีกครั้ง</p>
      </div>
    </div>
    <Button 
      variant="outline" 
      className="mt-4 border-red-300 text-red-700 hover:bg-red-100"
      onClick={retry}
    >
      ลองอีกครั้ง
    </Button>
  </CardContent>
</Card>
```

## Accessibility

### Keyboard Navigation

- All interactive elements focusable with Tab
- Chart category tabs navigable with arrow keys
- Time range selector accessible via keyboard
- Focus indicators visible and clear

### Screen Reader Support

```tsx
// ARIA labels for charts
<div role="img" aria-label="กราฟแสดงแนวโน้มราคาพืชใน 30 วันที่ผ่านมา">
  <LineChart {...props} />
</div>

// Descriptive button labels
<Button aria-label="เลือกช่วงเวลา 7 วัน">
  7 วัน
</Button>

// Status announcements
<div role="status" aria-live="polite">
  {loading ? 'กำลังโหลดข้อมูล...' : 'โหลดข้อมูลเสร็จสิ้น'}
</div>
```

### Color Contrast

- All text meets WCAG AA standards (4.5:1 ratio)
- Chart colors distinguishable for color-blind users
- Focus indicators have sufficient contrast
- Error messages use both color and icons

## Performance Optimization

### Code Splitting

```typescript
// Lazy load chart components
const PriceTrendChart = lazy(() => import('./charts/PriceTrendChart'));
const WeatherChart = lazy(() => import('./charts/WeatherChart'));

// Suspense boundary
<Suspense fallback={<ChartSkeleton />}>
  <PriceTrendChart data={data} />
</Suspense>
```

### Memoization

```typescript
// Memoize expensive calculations
const chartData = useMemo(() => {
  return transformDataForChart(rawData);
}, [rawData]);

// Memoize chart components
const MemoizedChart = memo(TimeSeriesChart);
```

### Virtual Scrolling

```typescript
// For long lists of data points
import { useVirtualizer } from '@tanstack/react-virtual';

const virtualizer = useVirtualizer({
  count: dataPoints.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 50,
});
```


## Testing Strategy

### Unit Tests

**Component Tests:**
- TimeRangeSelector renders all options correctly
- ChartCategoryTabs switches categories
- SimplifiedStatsCard displays values and trends
- TimeSeriesChart renders with correct data

**Hook Tests:**
- useDashboardData fetches data correctly
- useTimeRange manages state properly
- useChartCategory handles category switching

### Integration Tests

**User Flow Tests:**
- User selects province → data loads → charts update
- User changes time range → all charts refresh
- User switches chart category → correct charts display
- User hovers over chart → tooltip appears

### Visual Regression Tests

- Screenshot comparison for each chart type
- Responsive layout verification
- Theme consistency check
- Animation smoothness validation

### Performance Tests

- Page load time < 2 seconds
- Chart render time < 500ms
- Smooth 60fps animations
- Memory usage within acceptable limits

## Migration Strategy

### Phase 1: Theme Alignment (Week 1)

1. Update color variables in index.css
2. Replace RippleBackground with clean white background
3. Update MapNavbar styling to match other pages
4. Standardize card components

### Phase 2: Chart Replacement (Week 2)

1. Install Recharts library
2. Create new chart components
3. Migrate data transformation logic
4. Test chart interactivity

### Phase 3: Layout Redesign (Week 3)

1. Implement TimeRangeSelector
2. Create ChartCategoryTabs
3. Redesign statistics cards
4. Update responsive grid layout

### Phase 4: Polish and Testing (Week 4)

1. Add animations with Framer Motion
2. Implement loading and error states
3. Accessibility improvements
4. Performance optimization
5. User acceptance testing

## Dependencies

### New Dependencies

```json
{
  "dependencies": {
    "recharts": "^2.10.0",
    "framer-motion": "^10.16.0",
    "@tanstack/react-virtual": "^3.0.0"
  }
}
```

### Installation Commands

```bash
npm install recharts framer-motion @tanstack/react-virtual
```

### Remove Dependencies

```bash
npm uninstall @canvasjs/react-charts
```

## Design Rationale

### Why Recharts over CanvasJS?

1. **Better React Integration**: Native React components
2. **Smaller Bundle Size**: ~100KB vs ~200KB
3. **More Customizable**: Full control over styling
4. **Better TypeScript Support**: Type-safe props
5. **Active Community**: Regular updates and support

### Why Remove Ripple Background?

1. **Consistency**: Other pages use clean white backgrounds
2. **Performance**: Reduces animation overhead
3. **Readability**: Better contrast for data visualization
4. **Professional Look**: More suitable for data-heavy pages

### Why Tab-Based Chart Selection?

1. **Familiar Pattern**: Users understand tabs intuitively
2. **Space Efficient**: Shows all categories at once
3. **Easy Navigation**: One click to switch categories
4. **Mobile Friendly**: Horizontal scroll on small screens

### Why Time Range Selector?

1. **User Control**: Let users choose relevant time periods
2. **Data Flexibility**: Different insights from different ranges
3. **Consistent Pattern**: Matches Forecast page design
4. **Clear Feedback**: Visual indication of active range

## Future Enhancements

### Phase 2 Features (Post-Launch)

1. **Export Functionality**: Download charts as images or PDF
2. **Comparison Mode**: Compare multiple provinces side-by-side
3. **Custom Date Range**: Allow users to select specific dates
4. **Chart Annotations**: Add notes and markers to charts
5. **Favorites**: Save preferred chart configurations
6. **Dark Mode**: Support for dark theme
7. **Real-time Updates**: WebSocket for live data
8. **Advanced Filters**: Filter by crop type, soil type, etc.

### Analytics Integration

- Track which charts users view most
- Monitor time spent on each category
- Identify popular time ranges
- Measure user engagement with interactive features

## Success Metrics

### User Experience Metrics

- **Page Load Time**: < 2 seconds (target: 1.5s)
- **Time to Interactive**: < 3 seconds (target: 2s)
- **Chart Render Time**: < 500ms (target: 300ms)
- **Animation Frame Rate**: 60fps (no drops)

### User Engagement Metrics

- **Average Session Duration**: Increase by 30%
- **Charts Viewed per Session**: Increase by 50%
- **Return Visit Rate**: Increase by 25%
- **User Satisfaction Score**: > 4.5/5

### Technical Metrics

- **Bundle Size**: < 500KB (gzipped)
- **Memory Usage**: < 100MB
- **API Response Time**: < 1s (cached)
- **Error Rate**: < 0.1%

## Conclusion

This redesign focuses on creating a consistent, modern, and user-friendly dashboard that aligns with the existing application theme while significantly improving data visualization through time-series charts and intuitive navigation. The use of Recharts provides better React integration and customization options, while the tab-based chart selection and time range selector give users more control over their data exploration experience.
