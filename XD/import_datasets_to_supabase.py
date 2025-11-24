"""
สคริปต์สำหรับนำเข้าข้อมูลจาก buildingModel.py/Dataset เข้า Supabase ทีละไฟล์
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from datetime import datetime

# Supabase connection
SUPABASE_URL = "postgresql://postgres:Zx0966566414@db.inhanxxglxnjbugppulg.supabase.co:5432/postgres"

# รายการไฟล์ที่จะนำเข้า
DATASETS = {
    'compatibility': 'buildingModel.py/Dataset/compatibility.csv',
    'crop_characteristics': 'buildingModel.py/Dataset/crop_characteristics.csv',
    'cultivation': 'buildingModel.py/Dataset/cultivation.csv',
    'economic': 'buildingModel.py/Dataset/economic.csv',
    'farmer_profiles': 'buildingModel.py/Dataset/farmer_profiles.csv',
    'population': 'buildingModel.py/Dataset/population.csv',
    'price': 'buildingModel.py/Dataset/price.csv',
    'profit': 'buildingModel.py/Dataset/profit.csv',
    'weather': 'buildingModel.py/Dataset/weather.csv',
    'farmme_gpu': 'buildingModel.py/Dataset/FARMME_GPU_DATASET.csv'
}

def connect_to_supabase():
    """เชื่อมต่อกับ Supabase"""
    try:
        conn = psycopg2.connect(SUPABASE_URL)
        print("✅ เชื่อมต่อ Supabase สำเร็จ")
        return conn
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ Supabase: {e}")
        return None

def preview_dataset(file_path, rows=5):
    """แสดงตัวอย่างข้อมูล"""
    try:
        df = pd.read_csv(file_path)
        print(f"\n📊 ตัวอย่างข้อมูลจาก {os.path.basename(file_path)}")
        print(f"   จำนวนแถว: {len(df)}, จำนวนคอลัมน์: {len(df.columns)}")
        print(f"   คอลัมน์: {', '.join(df.columns.tolist())}")
        print(f"\n   ตัวอย่าง {rows} แถวแรก:")
        print(df.head(rows).to_string())
        return df
    except Exception as e:
        print(f"❌ ไม่สามารถอ่านไฟล์: {e}")
        return None

def create_table_from_dataframe(conn, table_name, df):
    """สร้างตารางใน Supabase จาก DataFrame"""
    cursor = conn.cursor()
    
    # แปลง pandas dtype เป็น PostgreSQL type
    type_mapping = {
        'int64': 'INTEGER',
        'float64': 'DOUBLE PRECISION',
        'object': 'TEXT',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP'
    }
    
    columns = []
    for col, dtype in df.dtypes.items():
        pg_type = type_mapping.get(str(dtype), 'TEXT')
        # ทำความสะอาดชื่อคอลัมน์
        clean_col = col.lower().replace(' ', '_').replace('-', '_')
        columns.append(f'"{clean_col}" {pg_type}')
    
    # สร้างตาราง
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        {', '.join(columns)},
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    try:
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"✅ สร้างตาราง {table_name} สำเร็จ")
        return True
    except Exception as e:
        print(f"❌ ไม่สามารถสร้างตาราง: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def insert_data_batch(conn, table_name, df, batch_size=1000):
    """นำเข้าข้อมูลเป็น batch"""
    cursor = conn.cursor()
    
    # ทำความสะอาดชื่อคอลัมน์
    df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
    
    # แปลง NaN เป็น None
    df = df.where(pd.notnull(df), None)
    
    total_rows = len(df)
    inserted = 0
    
    try:
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            
            # สร้าง SQL insert
            columns = ', '.join([f'"{col}"' for col in batch.columns])
            values = [tuple(row) for row in batch.values]
            
            insert_sql = f'INSERT INTO {table_name} ({columns}) VALUES %s'
            execute_values(cursor, insert_sql, values)
            
            inserted += len(batch)
            print(f"   📥 นำเข้าแล้ว {inserted}/{total_rows} แถว ({inserted*100//total_rows}%)")
        
        conn.commit()
        print(f"✅ นำเข้าข้อมูลทั้งหมด {inserted} แถวสำเร็จ")
        return True
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการนำเข้า: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def import_dataset(dataset_name, file_path, conn):
    """นำเข้าข้อมูล 1 ไฟล์"""
    print(f"\n{'='*60}")
    print(f"🚀 เริ่มนำเข้า: {dataset_name}")
    print(f"{'='*60}")
    
    # 1. แสดงตัวอย่างข้อมูล
    df = preview_dataset(file_path)
    if df is None:
        return False
    
    # 2. ถามยืนยัน
    response = input(f"\n❓ ต้องการนำเข้าข้อมูลนี้เข้าตาราง '{dataset_name}' หรือไม่? (y/n): ")
    if response.lower() != 'y':
        print("⏭️  ข้าม")
        return False
    
    # 3. สร้างตาราง
    if not create_table_from_dataframe(conn, dataset_name, df):
        return False
    
    # 4. นำเข้าข้อมูล
    if not insert_data_batch(conn, dataset_name, df):
        return False
    
    print(f"✅ นำเข้า {dataset_name} เสร็จสมบูรณ์")
    return True

def main():
    """ฟังก์ชันหลัก"""
    print("🌾 FARMME - นำเข้าข้อมูลเข้า Supabase")
    print("="*60)
    
    # เชื่อมต่อ Supabase
    conn = connect_to_supabase()
    if not conn:
        return
    
    try:
        # แสดงรายการไฟล์
        print("\n📋 รายการไฟล์ที่พร้อมนำเข้า:")
        for i, (name, path) in enumerate(DATASETS.items(), 1):
            exists = "✅" if os.path.exists(path) else "❌"
            print(f"   {i}. {name:20s} {exists}")
        
        print("\n" + "="*60)
        print("เลือกวิธีการนำเข้า:")
        print("1. นำเข้าทีละไฟล์ (แนะนำ)")
        print("2. นำเข้าทั้งหมดพร้อมกัน")
        print("3. เลือกไฟล์เฉพาะ")
        choice = input("\nเลือก (1-3): ")
        
        if choice == '1':
            # นำเข้าทีละไฟล์
            for name, path in DATASETS.items():
                if os.path.exists(path):
                    import_dataset(name, path, conn)
                    input("\n⏸️  กด Enter เพื่อดำเนินการต่อ...")
                else:
                    print(f"⚠️  ไม่พบไฟล์: {path}")
        
        elif choice == '2':
            # นำเข้าทั้งหมด
            response = input("⚠️  ยืนยันการนำเข้าทั้งหมด? (y/n): ")
            if response.lower() == 'y':
                for name, path in DATASETS.items():
                    if os.path.exists(path):
                        import_dataset(name, path, conn)
        
        elif choice == '3':
            # เลือกไฟล์เฉพาะ
            print("\nเลือกหมายเลขไฟล์ที่ต้องการนำเข้า (คั่นด้วยเครื่องหมายจุลภาค):")
            selected = input("ตัวอย่าง: 1,3,5: ")
            indices = [int(x.strip()) for x in selected.split(',')]
            
            for i, (name, path) in enumerate(DATASETS.items(), 1):
                if i in indices and os.path.exists(path):
                    import_dataset(name, path, conn)
                    input("\n⏸️  กด Enter เพื่อดำเนินการต่อ...")
        
        print("\n" + "="*60)
        print("✅ เสร็จสิ้นการนำเข้าข้อมูล")
        
    finally:
        conn.close()
        print("🔌 ปิดการเชื่อมต่อ Supabase")

if __name__ == "__main__":
    main()
