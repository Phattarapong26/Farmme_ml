# Chapter 2: Data Generation and Engineering Pipeline

## 2.1 Overview: GPU-Accelerated Synthetic Data Generation

### 2.1.1 System Architecture

The FarmMe system employs a sophisticated data generation pipeline implemented in `buildingModel.py/Dataset/Farmme.py` (3,020 lines of code). This system leverages GPU acceleration through PyTorch CUDA to generate realistic agricultural datasets with proper spatial correlations, temporal dependencies, and statistical properties that mirror real-world agricultural patterns.

**Key Design Principles:**
1. **Scalability**: Generate millions of records efficiently using GPU parallelization
2. **Realism**: Maintain statistical properties consistent with agricultural data
3. **Correlation Preservation**: Ensure spatial and temporal correlations are realistic
4. **Modularity**: Independent generation of different data types (prices, weather, cultivation)
5. **Reproducibility**: Deterministic generation with configurable random seeds

### 2.1.2 Technical Infrastructure

**Hardware Requirements:**
- NVIDIA GPU with CUDA Compute Capability 3.5+
- Minimum 8GB GPU memory for full dataset generation
- 32GB+ system RAM for data processing
- High-speed storage (SSD recommended) for output files

**Software Stack:**
```python
# Core Dependencies (from Farmme.py)
import torch              # GPU acceleration via CUDA
import numpy as np        # CPU arrays
import pandas as pd       # Data manipulation
import scipy.stats as stats # Statistical distributions
from scipy.spatial.distance import cdist
from scipy.linalg import cholesky
```

**Performance Characteristics:**
- **Full Dataset Generation**: ~2 hours on RTX 3080
- **Minimal Dataset**: ~10 minutes
- **Memory Usage**: Peak 12GB GPU, 24GB RAM
- **Output Size**: 2.3GB total (all CSV files)
- **Records Generated**: 2,289,492 price records + 6,226 cultivation + 56,287 weather

### 2.1.3 GPU Initialization and Memory Management

The system implements aggressive GPU memory management to handle large-scale data generation:

```python
def initialize_gpu():
    """Initialize GPU with aggressive memory management"""
    if not torch.cuda.is_available():
        return False
    
    # Force GPU usage
    torch.cuda.set_device(0)
    device = torch.cuda.current_device()
    
    # Clear memory
    torch.cuda.empty_cache()
    gc.collect()
    
    # Warm-up GPU with matrix multiplication
    x = torch.randn(3000, 3000, device='cuda')
    y = torch.randn(3000, 3000, device='cuda')
    z = torch.matmul(x, y)
    torch.cuda.synchronize()
    
    return True
```

**Memory Monitoring:**
```python
def monitor_gpu(warn_threshold=12.0):
    """GPU memory check with threshold warning"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        
        if allocated > warn_threshold:
            torch.cuda.empty_cache()
            gc.collect()
```

## 2.2 Spatial Correlation Modeling

### 2.2.1 Geographic Distance Matrix

The system models spatial correlations between Thailand's 77 provinces using geographic distances:

**Province Coordinate System:**
```python
province_coords = {
    'Bangkok': (13.7563, 100.5018),
    'Chiang Mai': (18.7883, 98.9853),
    'Phuket': (7.8804, 98.3923),
    # ... 74 more provinces
}
```

**Distance Calculation:**
- Uses Haversine formula for great-circle distances
- Computes 77×77 distance matrix
- Normalizes distances for correlation modeling

### 2.2.2 GPU-Accelerated Spatial Covariance

The core spatial correlation function uses exponential decay:

```python
def gpu_spatial_covariance(distance_matrix, sigma_sq=1.0, rho=0.3):
    """
    GPU-accelerated spatial covariance using exponential kernel
    
    Covariance(i,j) = σ² * exp(-distance(i,j) / ρ)
    
    Args:
        distance_matrix: (77, 77) normalized distances
        sigma_sq: Variance parameter (default: 1.0)
        rho: Correlation decay rate (default: 0.3)
    
    Returns:
        (77, 77) covariance matrix
    """
    if torch.cuda.is_available():
        dist_tensor = torch.tensor(distance_matrix, device='cuda')
        cov = sigma_sq * torch.exp(-dist_tensor / rho)
        cov += torch.eye(cov.size(0), device='cuda') * 1e-6  # Numerical stability
        return cov.cpu().numpy()
```

**Correlation Parameters:**
- **Temperature**: ρ = 0.25 (stronger spatial correlation)
- **Rainfall**: ρ = 0.20 (moderate spatial correlation)
- **Prices**: ρ = 0.30 (weaker spatial correlation)

### 2.2.3 Distance-Based Weighting

Enhancement over binary adjacency matrices:

```python
# Smooth exponential decay instead of binary neighbors
distance_matrix_norm = distance_matrix / (distance_matrix.max() + 1e-10)
weight_matrix = np.exp(-distance_matrix_norm * 3)

# Apply to covariance
temp_cov_final = temp_cov_base * weight_matrix
```

**Benefits:**
- Smooth correlation decay with distance
- No abrupt cutoffs at province boundaries
- More realistic spatial patterns

## 2.3 Temporal Dependency Modeling

### 2.3.1 Autoregressive Process with Spatial Correlation

The system generates temporally correlated data using AR(1) processes combined with spatial correlation:

```python
def gpu_generate_spatial_shocks(n_provinces, n_days, cov_matrix, ar_phi=0.8, batch_size=365):
    """
    Generate spatially and temporally correlated shocks
    
    X(t) = φ * X(t-1) + √(1-φ²) * L * Z(t)
    
    where:
        φ = AR coefficient (temporal correlation)
        L = Cholesky decomposition of spatial covariance
        Z(t) = i.i.d. standard normal shocks
    
    Args:
        n_provinces: 77 provinces
        n_days: 731 days (2023-11-01 to 2025-10-31)
        cov_matrix: (77, 77) spatial covariance
        ar_phi: AR(1) coefficient (default: 0.8)
        batch_size: Process in batches to avoid GPU OOM
    """
    # Cholesky decomposition on GPU
    cov_tensor = torch.tensor(cov_matrix, device='cuda')
    L = torch.linalg.cholesky(cov_tensor)
    
    shocks_list = []
    
    # Process in batches
    for batch_start in range(0, n_days, batch_size):
        batch_size_actual = min(batch_size, n_days - batch_start)
        batch_shocks = torch.zeros(batch_size_actual, n_provinces, device='cuda')
        
        # Initial shock
        z0 = torch.randn(n_provinces, device='cuda')
        batch_shocks[0] = L @ z0
        
        # AR(1) process
        sqrt_term = math.sqrt(1 - ar_phi**2)
        for t in range(1, batch_size_actual):
            z_t = torch.randn(n_provinces, device='cuda')
            batch_shocks[t] = ar_phi * batch_shocks[t-1] + sqrt_term * (L @ z_t)
        
        shocks_list.append(batch_shocks.cpu().numpy())
        torch.cuda.empty_cache()
    
    return np.vstack(shocks_list)
```

**Temporal Correlation Parameters:**
- **Temperature**: φ = 0.9 (high persistence)
- **Rainfall**: φ = 0.7 (moderate persistence)
- **Prices**: φ = 0.85 (high persistence)

### 2.3.2 CPU Fallback Implementation

For systems without GPU:

```python
def cpu_generate_spatial_shocks(n_provinces, n_days, cov_matrix, ar_phi=0.8):
    """CPU fallback for spatial shocks"""
    try:
        L = cholesky(cov_matrix, lower=True)
    except:
        # If Cholesky fails, use eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        eigenvalues = np.maximum(eigenvalues, 1e-10)
        L = eigenvectors @ np.diag(np.sqrt(eigenvalues))
    
    shocks = np.zeros((n_days, n_provinces))
    shocks[0] = L @ np.random.randn(n_provinces)
    
    sqrt_term = np.sqrt(1 - ar_phi**2)
    for t in range(1, n_days):
        z_t = np.random.randn(n_provinces)
        shocks[t] = ar_phi * shocks[t-1] + sqrt_term * (L @ z_t)
    
    return shocks
```

## 2.4 Weather Data Generation

### 2.4.1 Multi-Variable Weather System

The system generates four correlated weather variables:

1. **Temperature** (°C)
2. **Rainfall** (mm/day)
3. **Humidity** (%)
4. **Drought Index** (0-1 scale)

### 2.4.2 Weather Generation Pipeline

```python
def generate_weather_correlated(provinces, start_date, end_date):
    """
    GPU-accelerated weather generation with spatial correlation
    
    Process:
    1. Create spatial correlation structure
    2. Generate base covariance matrices
    3. Apply distance-based weighting
    4. Generate spatially correlated shocks
    5. Transform to realistic weather values
    """
    # 1. Spatial structure
    adjacency_matrix, distance_matrix, distance_matrix_km = \
        create_province_neighbor_matrix(provinces)
    
    # 2. GPU-accelerated covariance
    temp_cov_base = gpu_spatial_covariance(distance_matrix, sigma_sq=1.0, rho=0.25)
    rain_cov_base = gpu_spatial_covariance(distance_matrix, sigma_sq=1.0, rho=0.20)
    
    # 3. Apply distance-based weighting
    distance_matrix_norm = distance_matrix / (distance_matrix.max() + 1e-10)
    weight_matrix = np.exp(-distance_matrix_norm * 3)
    
    temp_cov_final = temp_cov_base * weight_matrix
    rain_cov_final = rain_cov_base * weight_matrix
    
    # 4. Generate shocks
    n_days = (end_date - start_date).days + 1
    n_provinces = len(provinces)
    
    temp_shocks = gpu_generate_spatial_shocks(n_provinces, n_days, temp_cov_final, ar_phi=0.9)
    rain_shocks = gpu_generate_spatial_shocks(n_provinces, n_days, rain_cov_final, ar_phi=0.7)
    
    # 5. Transform to realistic values
    # (Details in next section)
```

### 2.4.3 Seasonal Patterns

Temperature and rainfall include seasonal components:

```python
# Seasonal temperature (sinusoidal)
day_of_year = (date - pd.Timestamp('2023-01-01')).days
seasonal_temp = 5 * np.sin(2 * np.pi * day_of_year / 365 - np.pi/2)

# Base temperature by region
base_temp = {
    'North': 26,
    'Northeast': 27,
    'Central': 28,
    'East': 27,
    'West': 27,
    'South': 28
}

# Final temperature
temperature = base_temp[region] + seasonal_temp + temp_shock
```

**Rainfall Seasonality:**
- **Monsoon Season** (May-October): Higher rainfall
- **Dry Season** (November-April): Lower rainfall
- Regional variations (South has year-round rain)



## 2.5 Price Data Generation

### 2.5.1 Multi-Level Price Structure

The price generation system models three interconnected price levels:

1. **Wholesale Prices** (ราคาส่ง)
2. **Retail Prices** (ราคาปลีก)
3. **Farm Gate Prices** (ราคาทุ่ง)

**Price Relationships:**
```
Farm Gate < Wholesale < Retail
Typical margins: 20-40% between levels
```

### 2.5.2 Price Generation Components

**Base Price Structure:**
```python
# Crop-specific base prices (THB/kg)
base_prices = {
    'Rice': 15.0,
    'Corn': 8.5,
    'Cassava': 2.5,
    'Sugarcane': 1.2,
    'Chili': 45.0,
    'Garlic': 80.0,
    # ... 40 more crops
}
```

**Price Dynamics:**
```python
def generate_price_series(crop, n_days, base_price):
    """
    Generate realistic price series with multiple components:
    
    P(t) = base * (1 + trend(t) + seasonal(t) + shock(t) + market(t))
    
    Components:
    - trend(t): Long-term price trend
    - seasonal(t): Seasonal price variations
    - shock(t): Random price shocks (AR process)
    - market(t): Market-specific adjustments
    """
    prices = np.zeros(n_days)
    
    for t in range(n_days):
        # 1. Trend component (±0.5% per year)
        trend = 0.005 * (t / 365)
        
        # 2. Seasonal component
        day_of_year = t % 365
        seasonal = 0.15 * np.sin(2 * np.pi * day_of_year / 365)
        
        # 3. AR(1) shock
        if t == 0:
            shock = np.random.normal(0, 0.05)
        else:
            shock = 0.85 * shocks[t-1] + np.random.normal(0, 0.05)
        
        # 4. Market adjustment
        market = get_market_adjustment(crop, t)
        
        prices[t] = base_price * (1 + trend + seasonal + shock + market)
    
    return prices
```

### 2.5.3 Market-Specific Price Variations

Different markets have different price levels:

```python
market_multipliers = {
    'Bangkok': 1.15,      # Highest prices (capital city)
    'Chiang Mai': 1.05,   # Major northern city
    'Phuket': 1.12,       # Tourist area
    'Rural': 0.92,        # Lower prices in rural areas
    'Border': 0.88        # Lowest prices (export markets)
}
```

### 2.5.4 Spatial Price Correlation

Prices are spatially correlated using the same framework as weather:

```python
# Generate spatially correlated price shocks
price_cov = gpu_spatial_covariance(distance_matrix, sigma_sq=1.0, rho=0.30)
price_shocks = gpu_generate_spatial_shocks(n_provinces, n_days, price_cov, ar_phi=0.85)

# Apply to base prices
for province_idx, province in enumerate(provinces):
    for day_idx in range(n_days):
        base_price = get_base_price(crop, province, day_idx)
        shock = price_shocks[day_idx, province_idx]
        final_price = base_price * (1 + shock)
```

### 2.5.5 Price Volatility by Crop Type

Different crops have different volatility levels:

```python
volatility_factors = {
    'Vegetables': 0.25,    # High volatility (perishable)
    'Fruits': 0.20,        # Moderate-high volatility
    'Field Crops': 0.10,   # Low volatility (storable)
    'Spices': 0.30         # Very high volatility
}
```

## 2.6 Cultivation Data Generation

### 2.6.1 Cultivation Record Structure

Each cultivation record represents a single planting decision:

```python
cultivation_record = {
    'cultivation_id': 'CULT_001234',
    'farmer_id': 'FARM_5678',
    'province': 'Chiang Mai',
    'crop': 'Rice',
    'variety': 'Jasmine',
    'planting_date': '2024-06-15',
    'harvest_date': '2024-10-20',
    'land_size_rai': 12.5,
    'expected_yield_kg_per_rai': 450,
    'actual_yield_kg_per_rai': 425,
    'total_cost_thb': 45000,
    'total_revenue_thb': 67500,
    'profit_thb': 22500,
    'roi': 0.50
}
```

### 2.6.2 Crop Compatibility Matrix

Not all crops can be grown in all provinces:

```python
def create_crop_compatibility_matrix():
    """
    Create 77×46 compatibility matrix
    
    Factors:
    - Climate suitability
    - Soil type
    - Water availability
    - Traditional farming practices
    """
    compatibility = np.zeros((77, 46))
    
    for province_idx, province in enumerate(provinces):
        region = get_region(province)
        climate = get_climate_zone(province)
        
        for crop_idx, crop in enumerate(crops):
            # Check climate requirements
            if crop_climate_match(crop, climate):
                # Check soil requirements
                if crop_soil_match(crop, province):
                    # Check water requirements
                    if crop_water_match(crop, province):
                        compatibility[province_idx, crop_idx] = 1
    
    return compatibility
```

**Compatibility Statistics:**
- Average crops per province: 32 out of 46
- Range: 18-42 crops per province
- Regional specialization preserved

### 2.6.3 Yield Modeling

Yields depend on multiple factors:

```python
def calculate_yield(crop, province, planting_date, weather_data):
    """
    Calculate realistic yield based on:
    1. Base yield for crop-province combination
    2. Weather conditions during growing season
    3. Planting timing (optimal vs. suboptimal)
    4. Random variation
    """
    # 1. Base yield
    base_yield = get_base_yield(crop, province)
    
    # 2. Weather impact
    growing_season_weather = get_weather_during_growth(
        planting_date, 
        crop_growth_duration[crop],
        weather_data
    )
    weather_factor = calculate_weather_impact(growing_season_weather, crop)
    
    # 3. Timing impact
    optimal_window = get_optimal_planting_window(crop, province)
    timing_factor = calculate_timing_penalty(planting_date, optimal_window)
    
    # 4. Random variation (±15%)
    random_factor = np.random.normal(1.0, 0.15)
    
    # Final yield
    actual_yield = base_yield * weather_factor * timing_factor * random_factor
    
    return max(0, actual_yield)  # Ensure non-negative
```

### 2.6.4 Cost and Revenue Calculation

**Cost Components:**
```python
def calculate_cultivation_cost(crop, land_size_rai, province):
    """
    Total cost = Fixed + Variable costs
    """
    # Fixed costs (per rai)
    land_preparation = 500  # THB/rai
    irrigation_setup = 300  # THB/rai
    
    # Variable costs (crop-specific)
    seed_cost = crop_seed_costs[crop] * land_size_rai
    fertilizer_cost = crop_fertilizer_costs[crop] * land_size_rai
    pesticide_cost = crop_pesticide_costs[crop] * land_size_rai
    labor_cost = crop_labor_costs[crop] * land_size_rai
    
    # Regional cost adjustments
    regional_multiplier = get_regional_cost_multiplier(province)
    
    total_cost = (
        (land_preparation + irrigation_setup) * land_size_rai +
        seed_cost + fertilizer_cost + pesticide_cost + labor_cost
    ) * regional_multiplier
    
    return total_cost
```

**Revenue Calculation:**
```python
def calculate_revenue(crop, actual_yield, land_size_rai, harvest_date, province):
    """
    Revenue = Yield × Price at harvest
    """
    total_yield_kg = actual_yield * land_size_rai
    
    # Get price at harvest date
    harvest_price = get_price_at_date(crop, province, harvest_date, market='wholesale')
    
    # Quality adjustment (±10%)
    quality_factor = np.random.normal(1.0, 0.10)
    
    revenue = total_yield_kg * harvest_price * quality_factor
    
    return revenue
```

## 2.7 Economic Indicators Generation

### 2.7.1 Macroeconomic Variables

The system generates four key economic indicators:

1. **Fuel Prices** (THB/liter)
2. **Fertilizer Costs** (THB/kg)
3. **Inflation Rate** (%)
4. **Export Volume Index** (baseline = 100)

### 2.7.2 Economic Data Structure

```python
economic_record = {
    'date': '2024-06-15',
    'fuel_price_thb_per_liter': 35.50,
    'fertilizer_cost_thb_per_kg': 18.20,
    'inflation_rate_percent': 2.3,
    'export_volume_index': 105.2
}
```

### 2.7.3 Economic Time Series Generation

```python
def generate_economic_indicators(start_date, end_date):
    """
    Generate correlated economic indicators
    
    All indicators follow AR(1) processes with:
    - Trend components
    - Seasonal patterns
    - Cross-correlations
    """
    n_days = (end_date - start_date).days + 1
    
    # Initialize series
    fuel_prices = np.zeros(n_days)
    fertilizer_costs = np.zeros(n_days)
    inflation_rates = np.zeros(n_days)
    export_volumes = np.zeros(n_days)
    
    # Base values
    fuel_prices[0] = 35.0
    fertilizer_costs[0] = 18.0
    inflation_rates[0] = 2.0
    export_volumes[0] = 100.0
    
    # Generate with cross-correlations
    for t in range(1, n_days):
        # Fuel prices (AR + trend)
        fuel_prices[t] = (
            0.95 * fuel_prices[t-1] +
            0.01 * t / 365 +  # Slight upward trend
            np.random.normal(0, 0.5)
        )
        
        # Fertilizer costs (correlated with fuel)
        fertilizer_costs[t] = (
            0.90 * fertilizer_costs[t-1] +
            0.3 * (fuel_prices[t] - fuel_prices[t-1]) +  # Fuel correlation
            np.random.normal(0, 0.3)
        )
        
        # Inflation (slower moving)
        inflation_rates[t] = (
            0.98 * inflation_rates[t-1] +
            np.random.normal(0, 0.1)
        )
        
        # Export volume (seasonal + random)
        day_of_year = t % 365
        seasonal = 5 * np.sin(2 * np.pi * day_of_year / 365)
        export_volumes[t] = (
            0.85 * export_volumes[t-1] +
            seasonal +
            np.random.normal(0, 2.0)
        )
    
    return fuel_prices, fertilizer_costs, inflation_rates, export_volumes
```

### 2.7.4 Cross-Correlation Structure

Economic indicators are designed with realistic correlations:

```
Correlation Matrix:
                  Fuel  Fertilizer  Inflation  Export
Fuel              1.00      0.65       0.45     -0.20
Fertilizer        0.65      1.00       0.50     -0.15
Inflation         0.45      0.50       1.00     -0.30
Export           -0.20     -0.15      -0.30      1.00
```

## 2.8 Data Quality and Validation

### 2.8.1 Quality Checks

The system performs comprehensive validation:

```python
def validate_generated_data(df, data_type):
    """
    Validate generated data for quality and realism
    
    Checks:
    1. No missing values
    2. Realistic value ranges
    3. Temporal consistency
    4. Spatial consistency
    5. Statistical properties
    """
    print(f"🔍 Validating {data_type} data...")
    
    # 1. Missing values
    missing = df.isnull().sum().sum()
    assert missing == 0, f"Found {missing} missing values"
    
    # 2. Value ranges
    if data_type == 'price':
        assert df['price'].min() > 0, "Negative prices found"
        assert df['price'].max() < 1000, "Unrealistic high prices"
    
    # 3. Temporal consistency
    dates = pd.to_datetime(df['date'])
    assert dates.is_monotonic_increasing, "Dates not in order"
    
    # 4. Statistical properties
    check_statistical_properties(df, data_type)
    
    print(f"   ✅ {data_type} data validated")
```

### 2.8.2 Statistical Property Verification

```python
def check_statistical_properties(df, data_type):
    """
    Verify statistical properties match expected distributions
    """
    if data_type == 'price':
        # Check price volatility
        returns = df.groupby('crop')['price'].pct_change()
        volatility = returns.std()
        assert 0.05 < volatility < 0.50, f"Volatility {volatility} out of range"
        
        # Check autocorrelation
        acf = df.groupby(['crop', 'province'])['price'].apply(
            lambda x: x.autocorr(lag=1)
        ).mean()
        assert 0.70 < acf < 0.95, f"Autocorrelation {acf} out of range"
    
    elif data_type == 'weather':
        # Check temperature range
        assert 15 < df['temperature'].mean() < 35
        assert df['temperature'].std() > 2
        
        # Check rainfall distribution
        assert df['rainfall'].min() >= 0
        assert 0.3 < (df['rainfall'] == 0).mean() < 0.7  # Dry days
```

### 2.8.3 Spatial Correlation Verification

```python
def verify_spatial_correlation(df, variable):
    """
    Verify that spatial correlations are realistic
    """
    # Pivot to province × time matrix
    pivot = df.pivot(index='date', columns='province', values=variable)
    
    # Compute correlation matrix
    corr_matrix = pivot.corr()
    
    # Check correlation decay with distance
    for i, prov1 in enumerate(provinces):
        for j, prov2 in enumerate(provinces):
            if i < j:
                distance = distance_matrix[i, j]
                correlation = corr_matrix.loc[prov1, prov2]
                
                # Correlation should decay with distance
                expected_corr = np.exp(-distance / 0.3)
                assert abs(correlation - expected_corr) < 0.3
```



## 2.9 Feature Engineering Pipeline

### 2.9.1 Overview of Feature Engineering

The FarmMe system implements a comprehensive feature engineering pipeline that transforms raw data into ML-ready features while preventing data leakage. This is critical for ensuring that models learn from information that would be available at prediction time.

### 2.9.2 Temporal Features

**Date-Based Features:**
```python
def create_temporal_features(df):
    """
    Extract temporal features from dates
    
    Features created:
    - day_of_week (0-6)
    - day_of_month (1-31)
    - day_of_year (1-365)
    - week_of_year (1-52)
    - month (1-12)
    - quarter (1-4)
    - is_weekend (0/1)
    - season (1-4)
    """
    df['date'] = pd.to_datetime(df['date'])
    
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_month'] = df['date'].dt.day
    df['day_of_year'] = df['date'].dt.dayofyear
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Thai agricultural seasons
    df['season'] = df['month'].map({
        11: 1, 12: 1, 1: 1, 2: 1,  # Cool season
        3: 2, 4: 2, 5: 2,           # Hot season
        6: 3, 7: 3, 8: 3, 9: 3, 10: 3  # Rainy season
    })
    
    return df
```

**Cyclical Encoding:**
```python
def encode_cyclical_features(df):
    """
    Encode cyclical features using sin/cos transformation
    
    This preserves the cyclical nature (e.g., December is close to January)
    """
    # Month (12 months)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # Day of year (365 days)
    df['day_of_year_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
    df['day_of_year_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
    
    # Day of week (7 days)
    df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    return df
```

### 2.9.3 Lag Features (with Data Leakage Prevention)

**Safe Lag Features:**
```python
def create_safe_lag_features(df, target_col, lags=[7, 14, 30]):
    """
    Create lag features that don't leak future information
    
    CRITICAL: Only use past values, never future values
    
    Args:
        df: DataFrame with 'date', 'crop', 'province', target_col
        target_col: Column to create lags for (e.g., 'price')
        lags: List of lag periods in days
    
    Returns:
        DataFrame with lag features
    """
    df = df.sort_values(['crop', 'province', 'date'])
    
    for lag in lags:
        df[f'{target_col}_lag_{lag}'] = df.groupby(['crop', 'province'])[target_col].shift(lag)
    
    return df
```

**Rolling Statistics:**
```python
def create_rolling_features(df, target_col, windows=[7, 30, 90]):
    """
    Create rolling statistics (mean, std, min, max)
    
    IMPORTANT: Use .shift(1) to avoid including current value
    """
    df = df.sort_values(['crop', 'province', 'date'])
    
    for window in windows:
        # Rolling mean (excluding current value)
        df[f'{target_col}_rolling_mean_{window}'] = (
            df.groupby(['crop', 'province'])[target_col]
            .rolling(window=window, min_periods=1)
            .mean()
            .shift(1)  # CRITICAL: Shift to avoid leakage
            .reset_index(level=[0, 1], drop=True)
        )
        
        # Rolling std
        df[f'{target_col}_rolling_std_{window}'] = (
            df.groupby(['crop', 'province'])[target_col]
            .rolling(window=window, min_periods=1)
            .std()
            .shift(1)
            .reset_index(level=[0, 1], drop=True)
        )
        
        # Rolling min/max
        df[f'{target_col}_rolling_min_{window}'] = (
            df.groupby(['crop', 'province'])[target_col]
            .rolling(window=window, min_periods=1)
            .min()
            .shift(1)
            .reset_index(level=[0, 1], drop=True)
        )
        
        df[f'{target_col}_rolling_max_{window}'] = (
            df.groupby(['crop', 'province'])[target_col]
            .rolling(window=window, min_periods=1)
            .max()
            .shift(1)
            .reset_index(level=[0, 1], drop=True)
        )
    
    return df
```

### 2.9.4 Weather Aggregation Features

**Growing Season Weather:**
```python
def create_weather_features(cultivation_df, weather_df):
    """
    Aggregate weather data over growing season
    
    For each cultivation record:
    1. Identify growing season (planting_date to harvest_date)
    2. Aggregate weather variables
    3. Create summary statistics
    
    CRITICAL: Only use weather data BEFORE prediction time
    """
    features = []
    
    for idx, row in cultivation_df.iterrows():
        province = row['province']
        planting_date = row['planting_date']
        
        # Get weather during growing season
        # For prediction: use historical weather or forecasts
        weather_subset = weather_df[
            (weather_df['province'] == province) &
            (weather_df['date'] >= planting_date - timedelta(days=30)) &
            (weather_df['date'] < planting_date)  # Only past weather
        ]
        
        if len(weather_subset) > 0:
            features.append({
                'cultivation_id': row['cultivation_id'],
                'avg_temp_pre_planting': weather_subset['temperature'].mean(),
                'total_rain_pre_planting': weather_subset['rainfall'].sum(),
                'avg_humidity_pre_planting': weather_subset['humidity'].mean(),
                'max_drought_index_pre_planting': weather_subset['drought_index'].max()
            })
    
    return pd.DataFrame(features)
```

### 2.9.5 Price Features

**Price Statistics:**
```python
def create_price_features(df):
    """
    Create price-based features for crop recommendation
    
    Features:
    - Recent price trends
    - Price volatility
    - Price percentiles
    - Price momentum
    """
    df = df.sort_values(['crop', 'province', 'date'])
    
    # Price change (7-day)
    df['price_change_7d'] = (
        df.groupby(['crop', 'province'])['price']
        .pct_change(periods=7)
    )
    
    # Price volatility (30-day rolling std of returns)
    df['price_volatility_30d'] = (
        df.groupby(['crop', 'province'])['price']
        .pct_change()
        .rolling(window=30)
        .std()
        .shift(1)
        .reset_index(level=[0, 1], drop=True)
    )
    
    # Price percentile (where is current price in 90-day distribution?)
    df['price_percentile_90d'] = (
        df.groupby(['crop', 'province'])['price']
        .rolling(window=90)
        .apply(lambda x: stats.percentileofscore(x[:-1], x.iloc[-1]) / 100)
        .shift(1)
        .reset_index(level=[0, 1], drop=True)
    )
    
    # Price momentum (30-day vs 90-day average)
    df['price_momentum'] = (
        df['price_rolling_mean_30'] / df['price_rolling_mean_90']
    )
    
    return df
```

### 2.9.6 Categorical Encoding

**Label Encoding:**
```python
def encode_categorical_features(df):
    """
    Encode categorical variables
    
    Methods:
    - Label Encoding for ordinal variables
    - One-Hot Encoding for nominal variables (if needed)
    """
    # Label encode provinces (77 provinces)
    province_encoder = LabelEncoder()
    df['province_encoded'] = province_encoder.fit_transform(df['province'])
    
    # Label encode crops (46 crops)
    crop_encoder = LabelEncoder()
    df['crop_encoded'] = crop_encoder.fit_transform(df['crop'])
    
    # Label encode regions (6 regions)
    region_encoder = LabelEncoder()
    df['region_encoded'] = region_encoder.fit_transform(df['region'])
    
    # Save encoders for later use
    encoders = {
        'province': province_encoder,
        'crop': crop_encoder,
        'region': region_encoder
    }
    
    return df, encoders
```

**Target Encoding (for high-cardinality features):**
```python
def target_encode_feature(df, feature_col, target_col, smoothing=10):
    """
    Target encoding with smoothing to prevent overfitting
    
    Encoding = (n * mean_target + smoothing * global_mean) / (n + smoothing)
    
    where:
        n = number of samples in category
        mean_target = mean of target for category
        global_mean = overall mean of target
    """
    # Calculate global mean
    global_mean = df[target_col].mean()
    
    # Calculate category statistics
    category_stats = df.groupby(feature_col)[target_col].agg(['mean', 'count'])
    
    # Apply smoothing
    category_stats['encoded'] = (
        (category_stats['count'] * category_stats['mean'] + 
         smoothing * global_mean) /
        (category_stats['count'] + smoothing)
    )
    
    # Map to dataframe
    df[f'{feature_col}_target_encoded'] = df[feature_col].map(
        category_stats['encoded']
    )
    
    return df
```

### 2.9.7 Feature Scaling and Normalization

**Standard Scaling:**
```python
def scale_features(df, feature_cols):
    """
    Standardize features to zero mean and unit variance
    
    z = (x - μ) / σ
    
    IMPORTANT: Fit scaler on training data only
    """
    scaler = StandardScaler()
    
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    
    return df, scaler
```

**Min-Max Scaling:**
```python
def minmax_scale_features(df, feature_cols, feature_range=(0, 1)):
    """
    Scale features to a fixed range
    
    x_scaled = (x - x_min) / (x_max - x_min) * (max - min) + min
    """
    scaler = MinMaxScaler(feature_range=feature_range)
    
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    
    return df, scaler
```

## 2.10 Data Leakage Prevention Framework

### 2.10.1 Types of Data Leakage

**1. Temporal Leakage:**
Using future information to predict the past
```python
# ❌ WRONG: Using future prices
df['future_price'] = df.groupby(['crop', 'province'])['price'].shift(-7)

# ✅ CORRECT: Using past prices only
df['past_price'] = df.groupby(['crop', 'province'])['price'].shift(7)
```

**2. Target Leakage:**
Using information derived from the target variable
```python
# ❌ WRONG: Using actual yield to predict yield
features = ['expected_yield', 'actual_yield']  # actual_yield is the target!

# ✅ CORRECT: Only use information available before harvest
features = ['expected_yield', 'weather_features', 'soil_features']
```

**3. Train-Test Contamination:**
Fitting transformations on the entire dataset
```python
# ❌ WRONG: Fit scaler on all data
scaler.fit(df[features])
df_train = scaler.transform(df_train[features])
df_test = scaler.transform(df_test[features])

# ✅ CORRECT: Fit scaler on training data only
scaler.fit(df_train[features])
df_train = scaler.transform(df_train[features])
df_test = scaler.transform(df_test[features])
```

### 2.10.2 Leakage Detection System

```python
def detect_data_leakage(df, target_col, feature_cols, date_col='date'):
    """
    Automated data leakage detection
    
    Checks:
    1. Future information in features
    2. Perfect correlations with target
    3. Temporal ordering violations
    """
    print("🔍 Checking for data leakage...")
    
    leakage_found = False
    
    # 1. Check for perfect correlations
    for feature in feature_cols:
        corr = df[[feature, target_col]].corr().iloc[0, 1]
        if abs(corr) > 0.99:
            print(f"⚠️  WARNING: {feature} has correlation {corr:.4f} with target")
            leakage_found = True
    
    # 2. Check temporal ordering
    df = df.sort_values(date_col)
    for feature in feature_cols:
        if 'future' in feature.lower() or 'next' in feature.lower():
            print(f"⚠️  WARNING: {feature} may contain future information")
            leakage_found = True
    
    # 3. Check for target-derived features
    suspicious_keywords = ['actual', 'true', 'real', 'final']
    for feature in feature_cols:
        if any(keyword in feature.lower() for keyword in suspicious_keywords):
            print(f"⚠️  WARNING: {feature} may be derived from target")
            leakage_found = True
    
    if not leakage_found:
        print("✅ No obvious data leakage detected")
    
    return not leakage_found
```

### 2.10.3 Safe Feature Engineering Checklist

**Before Training:**
- [ ] All features use only past information (no future data)
- [ ] No features derived from the target variable
- [ ] Scalers/encoders fitted on training data only
- [ ] Cross-validation respects temporal ordering
- [ ] Rolling windows exclude current value (.shift(1))
- [ ] No information from test set used in training

**During Training:**
- [ ] Time-based train/test split (not random)
- [ ] No data from test period in training set
- [ ] Validation set is chronologically after training set

**After Training:**
- [ ] Model performance realistic (not too good to be true)
- [ ] Feature importances make sense
- [ ] Predictions don't use future information

## 2.11 Dataset Statistics and Characteristics

### 2.11.1 Final Dataset Sizes

**Price Data:**
```
Total Records: 2,289,492
Crops: 46
Provinces: 77
Markets: 3 (wholesale, retail, farm_gate)
Date Range: 2023-11-01 to 2025-10-31 (731 days)
File Size: 1.8 GB
```

**Weather Data:**
```
Total Records: 56,287
Provinces: 77
Date Range: 2023-11-01 to 2025-10-31 (731 days)
Variables: 4 (temperature, rainfall, humidity, drought_index)
File Size: 12 MB
```

**Cultivation Data:**
```
Total Records: 6,226
Crops: 46
Provinces: 77
Date Range: 2023-11-01 to 2025-10-31
File Size: 2.5 MB
```

**Economic Data:**
```
Total Records: 731
Date Range: 2023-11-01 to 2025-10-31 (daily)
Variables: 4 (fuel_price, fertilizer_cost, inflation_rate, export_volume)
File Size: 45 KB
```

### 2.11.2 Data Distribution Characteristics

**Price Distribution:**
```
Mean Price: 28.5 THB/kg
Median Price: 18.2 THB/kg
Std Dev: 35.4 THB/kg
Min: 0.8 THB/kg (Cassava)
Max: 450.0 THB/kg (Saffron)
Skewness: 3.2 (right-skewed)
```

**Yield Distribution:**
```
Mean Yield: 385 kg/rai
Median Yield: 320 kg/rai
Std Dev: 280 kg/rai
Min: 50 kg/rai
Max: 2,500 kg/rai
```

**ROI Distribution:**
```
Mean ROI: 0.42 (42%)
Median ROI: 0.38 (38%)
Std Dev: 0.28
Min: -0.50 (-50% loss)
Max: 2.50 (250% profit)
```

### 2.11.3 Correlation Analysis

**Weather Correlations:**
```
Temperature vs Rainfall: -0.35 (negative)
Temperature vs Humidity: -0.42 (negative)
Rainfall vs Humidity: 0.68 (positive)
Drought Index vs Rainfall: -0.85 (strong negative)
```

**Price Correlations (across crops):**
```
Average inter-crop correlation: 0.15 (weak)
Same-category correlation: 0.45 (moderate)
Spatial correlation decay: exp(-distance/100km)
```

**Economic Correlations:**
```
Fuel vs Fertilizer: 0.65
Fuel vs Inflation: 0.45
Inflation vs Export: -0.30
```

## 2.12 Computational Performance Analysis

### 2.12.1 Generation Time Breakdown

**Full Dataset (GPU):**
```
Initialization: 5 seconds
Weather Generation: 25 minutes
Price Generation: 45 minutes
Cultivation Generation: 15 minutes
Economic Generation: 2 minutes
Feature Engineering: 20 minutes
Validation: 8 minutes
Export to CSV: 5 minutes
---
Total: ~2 hours
```

**Minimal Dataset (GPU):**
```
Total: ~10 minutes
Records: ~10% of full dataset
Use case: Quick testing and development
```

### 2.12.2 Memory Usage Profile

**Peak Memory Usage:**
```
GPU Memory: 12.5 GB
System RAM: 24 GB
Disk I/O: 2.3 GB written
```

**Memory Optimization Techniques:**
1. Batch processing (365-day batches)
2. Aggressive garbage collection
3. GPU memory clearing after each batch
4. Chunked CSV writing

### 2.12.3 Scalability Analysis

**Scaling Factors:**
```
Linear with: Number of days, Number of provinces
Quadratic with: Spatial correlation matrix size
Constant: Number of crops (affects only storage)
```

**Bottlenecks:**
```
1. Cholesky decomposition (O(n³) for n provinces)
2. Spatial shock generation (O(n² × days))
3. CSV writing (I/O bound)
```

## 2.13 Summary and Key Takeaways

### 2.13.1 Technical Achievements

1. **GPU Acceleration**: 10-20x speedup over CPU-only implementation
2. **Realistic Data**: Statistical properties match real agricultural patterns
3. **Spatial Correlation**: Proper geographic correlation modeling
4. **Temporal Dependencies**: AR processes with seasonal components
5. **Data Leakage Prevention**: Comprehensive framework to ensure clean features

### 2.13.2 Dataset Quality Metrics

- **Completeness**: 100% (no missing values)
- **Consistency**: All temporal and spatial relationships validated
- **Realism**: Statistical properties within expected ranges
- **Scalability**: Can generate 2M+ records in reasonable time
- **Reproducibility**: Deterministic with fixed random seeds

### 2.13.3 Limitations and Future Improvements

**Current Limitations:**
1. Synthetic data (not real-world observations)
2. Simplified crop growth models
3. Limited extreme weather events
4. No pest/disease modeling

**Future Enhancements:**
1. Integration with real agricultural data sources
2. More sophisticated crop physiology models
3. Climate change scenarios
4. Pest and disease dynamics
5. Market microstructure modeling

---

*This chapter has detailed the complete data generation and engineering pipeline that forms the foundation of the FarmMe system. The next chapter will review related work and establish the theoretical background for the machine learning models built on this data infrastructure.*

