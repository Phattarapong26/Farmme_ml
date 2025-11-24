import os
import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

# ==========================================
# 1. SYSTEM CONFIGURATION
# ==========================================
OUTPUT_DIR = "Dataset_Production_ML"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Generate Data for 3 Years (Covers historical & forecast needs)
START_DATE = pd.to_datetime("2023-01-01")
END_DATE = pd.to_datetime("2025-12-31")
DATE_RANGE = pd.date_range(start=START_DATE, end=END_DATE, freq='D')

print(f"🚀 INITIALIZING PRODUCTION GENERATOR")
print(f"📅 Period: {START_DATE.date()} - {END_DATE.date()} ({len(DATE_RANGE)} days)")

# ==========================================
# 2. MASTER DATA: 77 PROVINCES & REGIONS
# ==========================================
REGIONS = {
    'NORTH': ['เชียงใหม่','เชียงราย','น่าน','พะเยา','แพร่','แม่ฮ่องสอน','ลำปาง','ลำพูน','อุตรดิตถ์','ตาก','สุโขทัย','พิษณุโลก','พิจิตร','กำแพงเพชร','เพชรบูรณ์','นครสวรรค์','อุทัยธานี'],
    'NORTHEAST': ['กาฬสินธุ์','ขอนแก่น','ชัยภูมิ','นครพนม','นครราชสีมา','บึงกาฬ','บุรีรัมย์','มหาสารคาม','มุกดาหาร','ยโสธร','ร้อยเอ็ด','เลย','สกลนคร','สุรินทร์','ศรีสะเกษ','หนองคาย','หนองบัวลำภู','อุดรธานี','อุบลราชธานี','อำนาจเจริญ'],
    'CENTRAL': ['กรุงเทพมหานคร','ชัยนาท','นครนายก','นครปฐม','นนทบุรี','ปทุมธานี','พระนครศรีอยุธยา','ลพบุรี','สมุทรปราการ','สมุทรสงคราม','สมุทรสาคร','สระบุรี','สิงห์บุรี','สุพรรณบุรี','อ่างทอง'],
    'EAST': ['จันทบุรี','ฉะเชิงเทรา','ชลบุรี','ตราด','ปราจีนบุรี','ระยอง','สระแก้ว'],
    'WEST': ['กาญจนบุรี','ประจวบคีรีขันธ์','เพชรบุรี','ราชบุรี'],
    'SOUTH': ['กระบี่','ชุมพร','ตรัง','นครศรีธรรมราช','นราธิวาส','ปัตตานี','พังงา','พัทลุง','ภูเก็ต','ยะลา','ระนอง','สงขลา','สตูล','สุราษฎร์ธานี']
}
PROV_TO_REGION = {p: r for r, provs in REGIONS.items() for p in provs}

# ==========================================
# 3. MASTER DATA: 50 ECONOMIC CROPS
# ==========================================
# Defines specific biology, price ranges, and regional constraints for 50 crops
CROPS_DB = [
    # --- VEGETABLES (ผัก) ---
    {'name': 'คะน้า', 'cat': 'ผัก', 'regions': 'ALL', 'days': 45, 'price': (20, 50), 'months': [10,11,12,1], 'spoil': 0.05},
    {'name': 'ผักบุ้งจีน', 'cat': 'ผัก', 'regions': 'ALL', 'days': 25, 'price': (15, 35), 'months': 'ALL', 'spoil': 0.06},
    {'name': 'กวางตุ้ง', 'cat': 'ผัก', 'regions': 'ALL', 'days': 35, 'price': (18, 40), 'months': 'ALL', 'spoil': 0.05},
    {'name': 'กะหล่ำปลี', 'cat': 'ผัก', 'regions': ['NORTH','NORTHEAST'], 'days': 60, 'price': (10, 35), 'months': [11,12,1], 'spoil': 0.03},
    {'name': 'ผักกาดขาว', 'cat': 'ผัก', 'regions': ['NORTH','NORTHEAST'], 'days': 55, 'price': (15, 45), 'months': [11,12,1], 'spoil': 0.04},
    {'name': 'ต้นหอม', 'cat': 'ผัก', 'regions': 'ALL', 'days': 45, 'price': (50, 120), 'months': 'ALL', 'spoil': 0.05},
    {'name': 'ผักชี', 'cat': 'ผัก', 'regions': 'ALL', 'days': 45, 'price': (60, 150), 'months': [11,12,1], 'spoil': 0.05},
    {'name': 'พริกขี้หนู', 'cat': 'ผัก', 'regions': 'ALL', 'days': 90, 'price': (40, 150), 'months': 'ALL', 'spoil': 0.02},
    {'name': 'พริกจินดา', 'cat': 'ผัก', 'regions': ['NORTHEAST','CENTRAL'], 'days': 90, 'price': (30, 100), 'months': 'ALL', 'spoil': 0.02},
    {'name': 'มะเขือเทศ', 'cat': 'ผัก', 'regions': ['NORTH','NORTHEAST'], 'days': 75, 'price': (20, 60), 'months': [10,11,12], 'spoil': 0.05},
    {'name': 'มะเขือเปราะ', 'cat': 'ผัก', 'regions': 'ALL', 'days': 65, 'price': (15, 40), 'months': 'ALL', 'spoil': 0.03},
    {'name': 'แตงกวา', 'cat': 'ผัก', 'regions': 'ALL', 'days': 40, 'price': (12, 30), 'months': 'ALL', 'spoil': 0.04},
    {'name': 'ถั่วฝักยาว', 'cat': 'ผัก', 'regions': 'ALL', 'days': 55, 'price': (25, 50), 'months': 'ALL', 'spoil': 0.04},
    {'name': 'ฟักทอง', 'cat': 'ผัก', 'regions': 'ALL', 'days': 90, 'price': (10, 25), 'months': 'ALL', 'spoil': 0.01},
    {'name': 'มะนาว', 'cat': 'ผัก', 'regions': 'ALL', 'days': 150, 'price': (30, 120), 'months': [8,9], 'spoil': 0.02},
    {'name': 'ชะอม', 'cat': 'ผัก', 'regions': 'ALL', 'days': 30, 'price': (20, 50), 'months': [5,6,7,8,9], 'spoil': 0.06},
    {'name': 'โหระพา', 'cat': 'ผัก', 'regions': 'ALL', 'days': 50, 'price': (20, 60), 'months': 'ALL', 'spoil': 0.05},
    {'name': 'กะเพรา', 'cat': 'ผัก', 'regions': 'ALL', 'days': 50, 'price': (15, 50), 'months': 'ALL', 'spoil': 0.05},
    {'name': 'บวบเหลี่ยม', 'cat': 'ผัก', 'regions': 'ALL', 'days': 50, 'price': (15, 35), 'months': 'ALL', 'spoil': 0.03},
    {'name': 'มะระจีน', 'cat': 'ผัก', 'regions': 'ALL', 'days': 60, 'price': (25, 50), 'months': 'ALL', 'spoil': 0.03},

    # --- FRUITS (ผลไม้) ---
    {'name': 'ทุเรียน', 'cat': 'ผลไม้', 'regions': ['EAST','SOUTH'], 'days': 120, 'price': (120, 250), 'months': [4,5,6], 'spoil': 0.05},
    {'name': 'มังคุด', 'cat': 'ผลไม้', 'regions': ['EAST','SOUTH'], 'days': 120, 'price': (30, 150), 'months': [4,5,6], 'spoil': 0.04},
    {'name': 'เงาะ', 'cat': 'ผลไม้', 'regions': ['EAST','SOUTH'], 'days': 120, 'price': (25, 60), 'months': [5,6], 'spoil': 0.04},
    {'name': 'ลำไย', 'cat': 'ผลไม้', 'regions': ['NORTH'], 'days': 180, 'price': (25, 60), 'months': [7,8], 'spoil': 0.03},
    {'name': 'ลิ้นจี่', 'cat': 'ผลไม้', 'regions': ['NORTH'], 'days': 150, 'price': (40, 100), 'months': [5,6], 'spoil': 0.05},
    {'name': 'ส้มเขียวหวาน', 'cat': 'ผลไม้', 'regions': ['NORTH','CENTRAL'], 'days': 240, 'price': (40, 80), 'months': [11,12,1], 'spoil': 0.02},
    {'name': 'มะม่วงน้ำดอกไม้', 'cat': 'ผลไม้', 'regions': 'ALL', 'days': 100, 'price': (50, 120), 'months': [3,4,5], 'spoil': 0.03},
    {'name': 'กล้วยหอม', 'cat': 'ผลไม้', 'regions': 'ALL', 'days': 300, 'price': (20, 45), 'months': 'ALL', 'spoil': 0.03},
    {'name': 'สับปะรด', 'cat': 'ผลไม้', 'regions': ['WEST','EAST','NORTH'], 'days': 365, 'price': (8, 18), 'months': 'ALL', 'spoil': 0.02},
    {'name': 'แตงโม', 'cat': 'ผลไม้', 'regions': 'ALL', 'days': 70, 'price': (10, 25), 'months': 'ALL', 'spoil': 0.03},
    {'name': 'เมล่อน', 'cat': 'ผลไม้', 'regions': ['CENTRAL','NORTH'], 'days': 85, 'price': (60, 150), 'months': 'ALL', 'spoil': 0.04},
    {'name': 'สตรอว์เบอร์รี', 'cat': 'ผลไม้', 'regions': ['NORTH'], 'days': 90, 'price': (200, 450), 'months': [12,1,2], 'spoil': 0.08},
    {'name': 'แก้วมังกร', 'cat': 'ผลไม้', 'regions': 'ALL', 'days': 180, 'price': (30, 60), 'months': [5,6,7], 'spoil': 0.03},
    {'name': 'ฝรั่งกิมจู', 'cat': 'ผลไม้', 'regions': ['CENTRAL','WEST'], 'days': 180, 'price': (25, 50), 'months': 'ALL', 'spoil': 0.02},
    {'name': 'มะพร้าวน้ำหอม', 'cat': 'ผลไม้', 'regions': ['CENTRAL','WEST'], 'days': 365, 'price': (15, 40), 'months': 'ALL', 'spoil': 0.01},

    # --- FIELD CROPS (พืชไร่) ---
    {'name': 'ข้าวหอมมะลิ', 'cat': 'พืชไร่', 'regions': ['NORTHEAST','NORTH'], 'days': 120, 'price': (12, 18), 'months': [6,7], 'spoil': 0.001},
    {'name': 'ข้าวเจ้า', 'cat': 'พืชไร่', 'regions': ['CENTRAL','NORTH'], 'days': 100, 'price': (8, 12), 'months': 'ALL', 'spoil': 0.001},
    {'name': 'มันสำปะหลัง', 'cat': 'พืชไร่', 'regions': ['NORTHEAST','EAST'], 'days': 300, 'price': (2.5, 4.5), 'months': [3,4,5], 'spoil': 0.01},
    {'name': 'อ้อย', 'cat': 'พืชไร่', 'regions': ['NORTHEAST','CENTRAL','WEST'], 'days': 330, 'price': (1.5, 2.5), 'months': [11,12,1,2,3], 'spoil': 0.01},
    {'name': 'ข้าวโพดเลี้ยงสัตว์', 'cat': 'พืชไร่', 'regions': ['NORTHEAST','NORTH','CENTRAL'], 'days': 110, 'price': (9, 13), 'months': [6,7], 'spoil': 0.01},
    {'name': 'ยางพารา', 'cat': 'พืชไร่', 'regions': ['SOUTH','EAST','NORTHEAST'], 'days': 365, 'price': (45, 70), 'months': 'ALL', 'spoil': 0.005},
    {'name': 'ปาล์มน้ำมัน', 'cat': 'พืชไร่', 'regions': ['SOUTH'], 'days': 365, 'price': (5, 10), 'months': 'ALL', 'spoil': 0.02},
    {'name': 'ถั่วเหลือง', 'cat': 'พืชไร่', 'regions': ['NORTH','NORTHEAST'], 'days': 90, 'price': (18, 25), 'months': [12,1], 'spoil': 0.005},
    {'name': 'ถั่วเขียว', 'cat': 'พืชไร่', 'regions': ['NORTH','CENTRAL'], 'days': 70, 'price': (25, 35), 'months': [1,2,3], 'spoil': 0.005},

    # --- HERBS (สมุนไพร) ---
    {'name': 'กระเทียม', 'cat': 'สมุนไพร', 'regions': ['NORTH'], 'days': 100, 'price': (60, 120), 'months': [10,11], 'spoil': 0.01},
    {'name': 'หอมแดง', 'cat': 'สมุนไพร', 'regions': ['NORTHEAST','NORTH'], 'days': 80, 'price': (40, 90), 'months': [10,11,12], 'spoil': 0.02},
    {'name': 'ขิง', 'cat': 'สมุนไพร', 'regions': ['NORTH','NORTHEAST'], 'days': 240, 'price': (25, 60), 'months': [3,4], 'spoil': 0.01},
    {'name': 'ข่า', 'cat': 'สมุนไพร', 'regions': 'ALL', 'days': 200, 'price': (25, 55), 'months': 'ALL', 'spoil': 0.01},
    {'name': 'ตะไคร้', 'cat': 'สมุนไพร', 'regions': 'ALL', 'days': 120, 'price': (12, 30), 'months': 'ALL', 'spoil': 0.01},
    {'name': 'พริกไทย', 'cat': 'สมุนไพร', 'regions': ['EAST','SOUTH'], 'days': 300, 'price': (250, 450), 'months': 'ALL', 'spoil': 0.001},
    {'name': 'ขมิ้นชัน', 'cat': 'สมุนไพร', 'regions': ['SOUTH','NORTHEAST'], 'days': 240, 'price': (40, 90), 'months': [5,6], 'spoil': 0.01}
]

# ==========================================
# 4. LOGIC ENGINE
# ==========================================

def generate_macro_and_weather():
    print("🌍 Generating Macro Economics & Weather...")
    macro_data = []
    weather_data = []
    
    fuel_price = 35.0
    fert_price = 1000.0
    inflation_index = 100.0
    
    for date in DATE_RANGE:
        # Macro Logic: Random Walk with Seasonality
        fuel_price += np.random.normal(0, 0.3)
        fuel_price = max(25, min(50, fuel_price))
        
        fert_season = 1.1 if 5 <= date.month <= 8 else 1.0 # แพงช่วงหน้าฝน
        fert_price = (fert_price * 0.99 + 1000 * 0.01) + np.random.normal(0, 5) # Mean reversion
        
        inflation_index *= (1 + np.random.normal(0.0001, 0.0002)) # Slowly increasing
        
        macro_data.append({
            'date': date,
            'fuel_price': round(fuel_price, 2),
            'fertilizer_price': round(fert_price * fert_season, 2),
            'inflation_index': round(inflation_index, 2)
        })
        
        # Weather Logic: Simplified per region type
        month = date.month
        for prov, region in PROV_TO_REGION.items():
            # Determine Season
            is_rainy = 6 <= month <= 10
            is_winter = 11 <= month <= 2
            is_summer = 3 <= month <= 5
            if region == 'SOUTH': 
                is_rainy = month in [10,11,12,1,5,6]
                is_winter = False
            
            # Temperature
            base_temp = 30
            if is_winter and region in ['NORTH', 'NORTHEAST']: base_temp = 22
            if is_summer: base_temp = 36
            temp = np.random.normal(base_temp, 2)
            
            # Rainfall
            rain = 0.0
            rain_prob = 0.6 if is_rainy else 0.1
            if np.random.rand() < rain_prob:
                rain = np.random.gamma(5, 8)
            
            weather_data.append({
                'date': date,
                'province': prov,
                'avg_temp_c': round(temp, 1),
                'rainfall_mm': round(rain, 1),
                'humidity_pct': round(np.clip(60 + (rain/50)*30 + np.random.normal(0,5), 30, 99), 0)
            })
            
    return pd.DataFrame(macro_data), pd.DataFrame(weather_data)

def generate_farmers(n_farmers=2000):
    print(f"👨‍🌾 Generating {n_farmers} Farmer Profiles...")
    farmers = []
    provinces = list(PROV_TO_REGION.keys())
    
    for i in range(n_farmers):
        prov = random.choice(provinces)
        region = PROV_TO_REGION[prov]
        
        # Profile Generation based on Region Economics
        if region in ['CENTRAL', 'EAST']:
            farmer_type = np.random.choice(['Small', 'Medium', 'Large'], p=[0.3, 0.4, 0.3])
        else:
            farmer_type = np.random.choice(['Small', 'Medium', 'Large'], p=[0.6, 0.3, 0.1])
            
        if farmer_type == 'Small':
            land = random.randint(5, 15)
            budget = random.randint(5000, 30000)
            skill = random.uniform(0.3, 0.6)
            tech = 'Low'
        elif farmer_type == 'Medium':
            land = random.randint(16, 50)
            budget = random.randint(30000, 150000)
            skill = random.uniform(0.5, 0.8)
            tech = 'Medium'
        else:
            land = random.randint(51, 200)
            budget = random.randint(150000, 1000000)
            skill = random.uniform(0.7, 0.95)
            tech = 'High'
            
        farmers.append({
            'farmer_id': f'F{i:05d}',
            'province': prov,
            'region': region,
            'farmer_type': farmer_type,
            'land_size_rai': land,
            'budget': budget,
            'skill_level': round(skill, 2),
            'technology_level': tech,
            'soil_quality': random.choice(['Low', 'Medium', 'High']),
            'water_source': random.choice(['Rainfed', 'Irrigated', 'Groundwater'])
        })
    return pd.DataFrame(farmers)
def simulate_cultivation(farmers_df, macro_df, weather_df):
    print("🌱 Simulating Cultivation (HARD MODE: Strict Rules Applied)...")
    cultivations = []
    daily_supply = {} 
    
    macro_map = macro_df.set_index('date').to_dict('index')
    
    # --- กฎเหล็ก: พืชไฮโซที่ต้องใช้ทุนและฝีมือ ---
    HIGH_VALUE_CROPS = ['ทุเรียน', 'มังคุด', 'สตรอว์เบอร์รี', 'เมล่อน', 'องุ่น', 'พริกไทย']
    MEDIUM_VALUE_CROPS = ['มะม่วงน้ำดอกไม้', 'มะนาว', 'ขิง', 'ยางพารา', 'ปาล์มน้ำมัน']
    
    for _, farmer in farmers_df.iterrows():
        for year in range(START_DATE.year, END_DATE.year + 1):
            
            valid_crops = [c for c in CROPS_DB if (c['regions']=='ALL' or farmer['region'] in c['regions'])]
            if not valid_crops: continue
            
            # เลือกพืช 1-3 ชนิด
            n_crops = random.randint(1, 3)
            chosen_crops = random.sample(valid_crops, k=n_crops)
            
            for crop in chosen_crops:
                area = int(farmer['land_size_rai'] / n_crops)
                
                # Planting Logic (เหมือนเดิม)
                ideal_months = crop['months']
                if ideal_months == 'ALL':
                    plant_month = random.randint(1, 12)
                else:
                    plant_month = random.choice(ideal_months) if random.random() < 0.8 else random.randint(1, 12)
                
                try:
                    plant_date = pd.Timestamp(year=year, month=plant_month, day=random.randint(1, 28))
                except: continue
                
                if plant_date < START_DATE or plant_date > END_DATE: continue
                harvest_date = plant_date + timedelta(days=crop['days'])
                if harvest_date > END_DATE: continue
                
                # --- CORE LOGIC IMPROVEMENT (จุดที่แก้) ---
                
                # 1. ตรวจสอบคุณสมบัติ (Hard Constraints)
                is_high_tier = crop['name'] in HIGH_VALUE_CROPS
                is_med_tier = crop['name'] in MEDIUM_VALUE_CROPS
                
                base_yield_factor = 1.0
                
                # กฎข้อที่ 1: ทุนไม่ถึง ห้ามเล่นของสูง
                if is_high_tier and farmer['budget'] < 50000:
                    base_yield_factor = 0.0 # เจ๊งแน่
                elif is_med_tier and farmer['budget'] < 20000:
                    base_yield_factor = 0.2 # รอดยาก
                    
                # กฎข้อที่ 2: Skill ไม่ถึง อย่าหาทำ
                if is_high_tier and farmer['skill_level'] < 0.7:
                    base_yield_factor *= 0.3 # ผลผลิตออกน้อยมาก
                    
                # กฎข้อที่ 3: เทคโนโลยีช่วยได้
                if is_high_tier and farmer['technology_level'] == 'High':
                    base_yield_factor *= 1.5
                
                # คำนวณ Cost & Yield
                econ = macro_map.get(plant_date, {'fertilizer_price': 1000})
                base_cost_per_rai = 3000
                if is_high_tier: base_cost_per_rai = 8000 # ต้นทุนแพง
                
                total_cost = base_cost_per_rai * area
                
                # Yield Calculation
                yield_per_rai = 1500 
                if crop['cat'] == 'ผลไม้': yield_per_rai = 2500
                if is_high_tier: yield_per_rai = 1200 # ผลไม้แพงมักลูกน้อย
                
                # Apply Factors
                actual_yield = yield_per_rai * area * farmer['skill_level'] * base_yield_factor
                
                # Random Disaster (ภัยธรรมชาติ)
                if random.random() < 0.1: # 10% ซวย
                    actual_yield *= 0.5
                
                cultivations.append({
                    'farmer_id': farmer['farmer_id'],
                    'province': farmer['province'],
                    'crop_type': crop['name'],
                    'planting_date': plant_date,
                    'harvest_date': harvest_date,
                    'area_rai': area,
                    'cost_total': round(total_cost, 2),
                    'yield_kg': round(max(0, actual_yield), 2), # ห้ามติดลบ
                    'is_off_season': ideal_months != 'ALL' and plant_month not in ideal_months,
                    'special_care_needed': False,
                    'fertilizer_price_at_plant': econ['fertilizer_price']
                })
                
                # Update Supply
                if actual_yield > 0: # นับเฉพาะที่รอด
                    for d in range(7):
                        h_day = harvest_date + timedelta(days=d)
                        if h_day <= END_DATE:
                            key = (h_day, farmer['province'], crop['name'])
                            daily_supply[key] = daily_supply.get(key, 0) + (actual_yield / 7.0)

    return pd.DataFrame(cultivations), daily_supply
def generate_price_history(cultivation_supply, macro_df):
    print("💵 Generating Price History (Supply-Demand Logic)...")
    price_data = []
    
    # Pre-aggregate National Supply for Base Price
    national_supply = {}
    for (date, prov, crop), vol in cultivation_supply.items():
        key = (date, crop)
        national_supply[key] = national_supply.get(key, 0) + vol
        
    macro_map = macro_df.set_index('date').to_dict('index')
    
    for crop in CROPS_DB:
        base_p = (crop['price'][0] + crop['price'][1]) / 2
        curr_p = base_p
        momentum = 0
        
        for date in DATE_RANGE:
            # 1. Supply Factor
            supply = national_supply.get((date, crop['name']), 0)
            if supply > 10000: # Oversupply
                change = -0.02
            elif supply < 1000: # Shortage
                change = 0.01
            else:
                change = 0
                
            # 2. Macro Factor
            econ = macro_map.get(date)
            if econ['fuel_price'] > 40: change += 0.005 # Cost push
            
            # 3. Seasonality
            # Simple sine wave
            season = np.sin(2 * np.pi * date.dayofyear / 365) * 0.005
            
            # Momentum Update
            momentum = 0.7 * momentum + 0.3 * (change + season + np.random.normal(0, 0.01))
            curr_p *= (1 + momentum)
            
            # Bounds
            curr_p = max(crop['price'][0]*0.5, min(crop['price'][1]*1.5, curr_p))
            
            # Generate Provincial Prices (Only for provinces that grow it)
            # For dataset completeness, we just pick representative provinces
            # In real ML, you'd match provinces.
            relevant_regions = crop['regions']
            if relevant_regions == 'ALL': relevant_regions = list(REGIONS.keys())
            
            # Pick 1 province per region to save space, or all? Let's do All relevant provinces
            # Optimization: Do 5 random provinces to keep CSV size manageable for this script
            target_provs = []
            for r in relevant_regions:
                target_provs.extend(REGIONS[r])
            
            # Sampling 3 provinces per crop per day to keep file size sane for "All Provinces" request
            # (Or logic will generate millions of rows)
            daily_provs = random.sample(target_provs, k=min(len(target_provs), 3))
            
            for prov in daily_provs:
                local_supply = cultivation_supply.get((date, prov, crop['name']), 0)
                local_premium = 0.1 if local_supply < 500 else -0.05
                
                final_p = curr_p * (1 + local_premium)
                
                price_data.append({
                    'date': date,
                    'province': prov,
                    'crop_type': crop['name'],
                    'price_per_kg': round(final_p, 2),
                    'market_supply_kg': round(local_supply, 2)
                })
                
    return pd.DataFrame(price_data)

def generate_harvest_decision_data(cultivations_df, price_df):
    print("⚖️ Generating Harvest Decision Scenarios...")
    # Creates a dataset for "Sell vs Wait" classification
    # Join Harvest Date with Price
    
    # Optimize: Filter only rows where we have price info
    # Just creating simulation rows
    
    simulation = []
    price_lookup = price_df.set_index(['date', 'province', 'crop_type'])['price_per_kg'].to_dict()
    
    # Sample 30% of cultivations for decision simulation
    samples = cultivations_df.sample(frac=0.3)
    
    for _, row in samples.iterrows():
        h_date = row['harvest_date']
        crop = row['crop_type']
        prov = row['province']
        
        # Find price today
        p_today = price_lookup.get((h_date, prov, crop))
        if not p_today: continue # No price data generated for this specific combo/day
        
        # Find price next week
        p_next = price_lookup.get((h_date + timedelta(days=7), prov, crop))
        if not p_next: p_next = p_today
        
        # Spoilage Logic
        crop_info = next(c for c in CROPS_DB if c['name'] == crop)
        spoil_rate = crop_info['spoil']
        
        # Calculate Logic
        revenue_now = row['yield_kg'] * p_today
        revenue_wait = (row['yield_kg'] * (1 - spoil_rate*7)) * p_next
        
        label = 'WAIT' if revenue_wait > revenue_now * 1.05 else 'SELL'
        
        simulation.append({
            'cultivation_id': f"{row['farmer_id']}_{row['planting_date'].date()}",
            'crop': crop,
            'harvest_date': h_date,
            'price_today': p_today,
            'price_forecast_7d': p_next,
            'spoilage_risk': spoil_rate,
            'decision': label
        })
        
    return pd.DataFrame(simulation)

# ==========================================
# MAIN RUNNER
# ==========================================
if __name__ == "__main__":
    print(f"🚀 STARTING FULL DATASET GENERATION (50 Crops, 77 Provinces)")
    
    # 1. Macro & Weather
    macro_df, weather_df = generate_macro_and_weather()
    macro_df.to_csv(f"{OUTPUT_DIR}/macro_economics.csv", index=False)
    # Weather file can be huge, saving a sample or splitting is better, but here we save all
    print(f"   - Weather rows: {len(weather_df)}")
    weather_df.to_csv(f"{OUTPUT_DIR}/weather.csv", index=False)
    
    # 2. Farmers
    farmers_df = generate_farmers(n_farmers=50000)
    farmers_df.to_csv(f"{OUTPUT_DIR}/farmers.csv", index=False)
    
    # 3. Cultivation
    cult_df, daily_supply = simulate_cultivation(farmers_df, macro_df, weather_df)
    print(f"   - Cultivation rows: {len(cult_df)}")
    cult_df.to_csv(f"{OUTPUT_DIR}/cultivation_data.csv", index=False)
    
    # 4. Price
    price_df = generate_price_history(daily_supply, macro_df)
    print(f"   - Price rows: {len(price_df)}")
    price_df.to_csv(f"{OUTPUT_DIR}/price_data.csv", index=False)
    
    # 5. Harvest Decision
    decision_df = generate_harvest_decision_data(cult_df, price_df)
    decision_df.to_csv(f"{OUTPUT_DIR}/harvest_decision.csv", index=False)
    
    print("\n✅ DONE! Dataset is ready for all 5 ML Models.")