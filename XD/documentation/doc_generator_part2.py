# Part 2: Chapter 2-5 Generator
# เพิ่มเติมบทที่ 2-5 ลงในเอกสาร

def add_chapter2(doc):
    """บทที่ 2: ทฤษฎีและงานวิจัยที่เกี่ยวข้อง"""
    doc.add_heading('บทที่ 2', level=1)
    doc.add_heading('ทฤษฎีและงานวิจัยที่เกี่ยวข้อง', level=1)
    
    # 2.1 ทฤษฎี ML
    doc.add_heading('2.1 ทฤษฎีและหลักการ Machine Learning', level=2)
    
    ml_theory = """
Machine Learning (ML) เป็นสาขาหนึ่งของปัญญาประดิษฐ์ที่ศึกษาเกี่ยวกับการสร้างระบบที่สามารถเรียนรู้จากข้อมูลและปรับปรุงประสิทธิภาพได้เองโดยอัตโนมัติ โดยไม่ต้องเขียนโปรแกรมโดยตรง

ประเภทของ Machine Learning:

1. Supervised Learning - การเรียนรู้แบบมีผู้สอน
   - มีข้อมูลป้ายกำกับ (labeled data)
   - ใช้สำหรับ Classification และ Regression
   - ตัวอย่าง: การทำนายราคา, การจำแนกประเภท

2. Unsupervised Learning - การเรียนรู้แบบไม่มีผู้สอน
   - ไม่มีข้อมูลป้ายกำกับ
   - ใช้สำหรับ Clustering และ Dimensionality Reduction
   - ตัวอย่าง: การจัดกลุ่มลูกค้า

3. Reinforcement Learning - การเรียนรู้แบบเสริมแรง
   - เรียนรู้จากการลองผิดลองถูก
   - ได้รับ reward หรือ penalty
   - ตัวอย่าง: การตัดสินใจเก็บเกี่ยว

ในโครงการนี้ใช้ทั้ง Supervised Learning (Model A, B, C) และ Reinforcement Learning (Model D)
    """
    
    doc.add_paragraph(ml_theory.strip())
    
    # 2.2 อัลกอริทึม
    doc.add_heading('2.2 อัลกอริทึมที่ใช้ในระบบ', level=2)
    
    # XGBoost
    doc.add_heading('2.2.1 XGBoost (Extreme Gradient Boosting)', level=3)
    xgboost_text = """
XGBoost เป็นอัลกอริทึม Ensemble Learning ที่ใช้เทคนิค Gradient Boosting โดยสร้าง Decision Trees หลายๆ ต้นแบบต่อเนื่อง โดยแต่ละต้นจะเรียนรู้จากความผิดพลาดของต้นก่อนหน้า

ข้อดี:
- ประสิทธิภาพสูง รองรับข้อมูลขนาดใหญ่
- ป้องกัน Overfitting ด้วย Regularization
- รองรับ Missing Values
- สามารถ Parallel Processing ได้

การใช้งานในโครงการ:
- Model A: Crop Recommendation (R² = 0.47)
- Model C: Price Forecasting (MAE = 13.31 บาท)
    """
    doc.add_paragraph(xgboost_text.strip())
    
    # Logistic Regression
    doc.add_heading('2.2.2 Logistic Regression', level=3)
    logistic_text = """
Logistic Regression เป็นอัลกอริทึมสำหรับ Binary Classification ที่ใช้ Sigmoid Function ในการแปลงค่าเป็นความน่าจะเป็น (0-1)

สมการ: P(y=1|x) = 1 / (1 + e^(-z))
โดย z = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ

ข้อดี:
- เข้าใจง่าย ตีความได้
- รวดเร็ว เหมาะกับข้อมูลขนาดใหญ่
- ให้ค่า Probability ที่สามารถใช้ได้

การใช้งานในโครงการ:
- Model B: Planting Window Classification (F1 = 0.70-0.75)
    """
    doc.add_paragraph(logistic_text.strip())
    
    # Thompson Sampling
    doc.add_heading('2.2.3 Thompson Sampling', level=3)
    thompson_text = """
Thompson Sampling เป็นอัลกอริทึมสำหรับปัญหา Multi-Armed Bandit ที่ใช้ Bayesian Inference ในการตัดสินใจภายใต้ความไม่แน่นอน

หลักการ:
1. สร้าง Prior Distribution สำหรับแต่ละ Action
2. Sample ค่าจาก Distribution
3. เลือก Action ที่มีค่า Sample สูงสุด
4. Update Distribution ตาม Reward ที่ได้รับ

ข้อดี:
- Balance ระหว่าง Exploration และ Exploitation
- ปรับตัวได้ตามสถานการณ์
- เหมาะกับปัญหาที่มีความไม่แน่นอนสูง

การใช้งานในโครงการ:
- Model D: Harvest Decision (3 actions: Now, Wait 3d, Wait 7d)
    """
    doc.add_paragraph(thompson_text.strip())
    
    doc.add_page_break()

def add_chapter3(doc):
    """บทที่ 3: การดำเนินงาน"""
    doc.add_heading('บทที่ 3', level=1)
    doc.add_heading('การดำเนินงานและกระบวนการพัฒนา', level=1)
    
    # 3.1 สถาปัตยกรรม
    doc.add_heading('3.1 สถาปัตยกรรมระบบโดยรวม', level=2)
    
    arch_text = """
ระบบ FarmMe ประกอบด้วย 4 โมเดลหลักที่เชื่อมต่อกันเป็น Pipeline:

Model A (Crop Recommendation)
    ↓
Model B (Planting Window)
    ↓
Model C (Price Forecasting)
    ↓
Model D (Harvest Decision)

แต่ละโมเดลทำงานอิสระและส่งผลลัพธ์ไปยังโมเดลถัดไป สร้างเป็นระบบที่สมบูรณ์ตั้งแต่ก่อนปลูกจนถึงหลังเก็บเกี่ยว
    """
    doc.add_paragraph(arch_text.strip())
    
    doc.add_page_break()

def add_chapter4(doc):
    """บทที่ 4: ผลลัพธ์"""
    doc.add_heading('บทที่ 4', level=1)
    doc.add_heading('ผลลัพธ์ที่ได้', level=1)
    
    # 4.1 ผลการประเมิน
    doc.add_heading('4.1 ผลการประเมินประสิทธิภาพของแต่ละโมเดล', level=2)
    
    results_text = """
ผลการประเมินประสิทธิภาพของแต่ละโมเดล:

Model A - Crop Recommendation:
- Algorithm: XGBoost
- R²: 0.47 (honest, no data leakage)
- Training samples: 4,980
- Test samples: 1,246
- Features: 15 features (soil, weather, farm profile)

Model B - Planting Window:
- Algorithm: Logistic Regression
- F1-Score: 0.70-0.75
- Precision: 0.75
- Recall: 0.68
- Features: 9 temporal features

Model C - Price Forecasting:
- Algorithm: XGBoost + Weather + Economic
- Test MAE: 13.31 บาท
- Test RMSE: 18.91 บาท
- Bias Reduction: 28.7% (from 96.79% to 68.09%)
- Features: 21 features (13 original + 8 external)

Model D - Harvest Decision:
- Algorithm: Thompson Sampling
- Decision Accuracy: ~68%
- Profit within: ±20% of actual
- Actions: Harvest Now, Wait 3 Days, Wait 7 Days
    """
    doc.add_paragraph(results_text.strip())
    
    doc.add_page_break()

def add_chapter5(doc):
    """บทที่ 5: สรุป"""
    doc.add_heading('บทที่ 5', level=1)
    doc.add_heading('สรุปและข้อเสนอแนะ', level=1)
    
    # 5.1 สรุป
    doc.add_heading('5.1 สรุปผลการดำเนินงาน', level=2)
    
    summary_text = """
โครงการนี้ได้พัฒนาระบบปัญญาประดิษฐ์สำหรับการเกษตรอัจฉริยะ (FarmMe) ที่ประกอบด้วย 4 โมเดล Machine Learning ที่ทำงานร่วมกันเป็น Pipeline สมบูรณ์

ผลสำเร็จที่สำคัญ:
1. ระบบแนะนำพืชที่เหมาะสมตามสภาพพื้นที่และงบประมาณ
2. ระบบคาดการณ์ช่วงเวลาปลูกที่เหมาะสม
3. ระบบพยากรณ์ราคาที่ลด temporal bias ได้ 28.7%
4. ระบบตัดสินใจเก็บเกี่ยวที่ช่วยเพิ่มกำไร
5. การป้องกัน Data Leakage อย่างเข้มงวด
6. แอปพลิเคชันและแดชบอร์ดที่ใช้งานง่าย

ระบบนี้สามารถช่วยเกษตรกรในการตัดสินใจได้อย่างมีประสิทธิภาพ ลดความเสี่ยง และเพิ่มรายได้
    """
    doc.add_paragraph(summary_text.strip())
    
    # 5.2 ปัญหาและอุปสรรค
    doc.add_heading('5.2 ปัญหาและอุปสรรค', level=2)
    
    problems_text = """
ปัญหาและอุปสรรคที่พบ:

1. Data Leakage - พบปัญหา data leakage ในโมเดลเดิม ต้องแก้ไขและ retrain ใหม่
2. ข้อมูลไม่สมบูรณ์ - บางพื้นที่ขาดข้อมูลสภาพอากาศและราคา
3. ความแม่นยำ vs Robustness - Trade-off ระหว่างความแม่นยำและความทนทานต่อ market shocks
4. การรวบรวมข้อมูล - ต้องใช้เวลาในการรวบรวมและทำความสะอาดข้อมูล
    """
    doc.add_paragraph(problems_text.strip())
    
    # 5.3 ข้อเสนอแนะ
    doc.add_heading('5.3 ข้อเสนอแนะและแนวทางการพัฒนาต่อ', level=2)
    
    recommendations_text = """
ข้อเสนอแนะสำหรับการพัฒนาต่อ:

1. เพิ่ม Real-time Weather API - ใช้ข้อมูลสภาพอากาศจริงแทนข้อมูล synthetic
2. เพิ่ม Economic Indicators - เชื่อมต่อกับข้อมูลเศรษฐกิจจริง
3. พัฒนา Model B ให้มี Weather Awareness - เพิ่ม weather features และ anomaly detection
4. Ensemble Models - รวมหลายโมเดลเพื่อเพิ่มความแม่นยำ
5. Mobile Application - พัฒนา mobile app สำหรับเกษตรกร
6. IoT Integration - เชื่อมต่อกับ sensors ในไร่
7. Continuous Learning - ระบบเรียนรู้และปรับปรุงตัวเองอัตโนมัติ
    """
    doc.add_paragraph(recommendations_text.strip())
    
    doc.add_page_break()
