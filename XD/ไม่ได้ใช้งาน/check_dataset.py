import pandas as pd

# Check cultivation data
df_cult = pd.read_csv('buildingModel.py/Dataset/cultivation.csv')
print("=== Cultivation Data ===")
print(f"Records: {len(df_cult)}")
print(f"Columns: {len(df_cult.columns)}")
print(f"Unique provinces: {df_cult['province'].nunique()}")
print(f"Unique crops: {df_cult['crop_type'].nunique()}")
print(f"Date range: {df_cult['planting_date'].min()} to {df_cult['harvest_date'].max()}")

# Check weather data
df_weather = pd.read_csv('buildingModel.py/Dataset/weather.csv')
print("\n=== Weather Data ===")
print(f"Records: {len(df_weather)}")
print(f"Unique provinces: {df_weather['province'].nunique()}")
print(f"Date range: {df_weather['date'].min()} to {df_weather['date'].max()}")

# Check price data
df_price = pd.read_csv('buildingModel.py/Dataset/price.csv')
print("\n=== Price Data ===")
print(f"Records: {len(df_price)}")
print(f"Date range: {df_price['date'].min()} to {df_price['date'].max()}")

# Check economic data
df_econ = pd.read_csv('buildingModel.py/Dataset/economic.csv')
print("\n=== Economic Data ===")
print(f"Records: {len(df_econ)}")
print(f"Columns: {list(df_econ.columns)}")

# Check crop characteristics
df_crops = pd.read_csv('buildingModel.py/Dataset/crop_characteristics.csv')
print("\n=== Crop Characteristics ===")
print(f"Total crops: {len(df_crops)}")
print(f"Crop types: {df_crops['crop_type'].tolist()[:10]}...")
