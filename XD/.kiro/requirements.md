# Requirements Document

## Introduction

ระบบ ML Farming Pipeline เป็นระบบช่วยตัดสินใจสำหรับเกษตรกรตลอดฤดูกาลเพาะปลูก ประกอบด้วย 4 โมเดล ML ที่ทำงานต่อเนื่องกัน เพื่อแนะนำการเลือกพืช กำหนดช่วงเวลาปลูก คาดการณ์ราคา และตัดสินใจเวลาเก็บเกี่ยว โดยป้องกัน data leakage และใช้ข้อมูลที่สามารถสังเกตได้ในขณะตัดสินใจเท่านั้น

## Glossary

- **Crop_Recommendation_System**: ระบบแนะนำพืชที่ควรปลูก (Model A)
- **Planting_Window_Classifier**: ระบบจำแนกช่วงเวลาที่เหมาะสมในการปลูก (Model B)
- **Price_Forecast_System**: ระบบคาดการณ์ราคาพืชผล (Model C)
- **Harvest_Decision_Engine**: ระบบตัดสินใจเวลาเก็บเกี่ยว (Model D)
- **Data_Leakage**: การใช้ข้อมูลที่เกิดขึ้นหลังเหตุการณ์ในการทำนาย
- **Pre-Decision_Data**: ข้อมูลที่สามารถสังเกตได้ก่อนการตัดสินใจ
- **Post-Outcome_Features**: features ที่วัดได้หลังจากผลลัพธ์เกิดขึ้นแล้ว (เช่น actual_yield, success_rate)
- **Overfitting**: สภาวะที่โมเดล train ได้ดีแต่ generalize ไม่ดีบน unseen data
- **Feature_Correlation**: ความสัมพันธ์ระหว่าง feature และ target variable
- **ROI**: Return on Investment (ผลตอบแทนจากการลงทุน)
- **Thompson_Sampling**: อัลกอริทึม Bandit สำหรับการตัดสินใจแบบ sequential
- **NSGA-II**: Non-dominated Sorting Genetic Algorithm II สำหรับ multi-objective optimization
- **Time-Aware_Split**: การแบ่งข้อมูลที่คำนึงถึงลำดับเวลา
- **Evaluation_Plots**: กราฟและ visualization ที่แสดงผลการประเมินโมเดล (confusion matrix, ROC curve, feature importance, learning curves, residual plots)

## Requirements

### Requirement 1: Crop Recommendation System (Model A)

**User Story:** ในฐานะเกษตรกร ฉันต้องการได้รับคำแนะนำพืชที่ควรปลูกตามข้อมูลฟาร์มและงบประมาณ เพื่อให้ได้ผลตอบแทนสูงสุดและความเสี่ยงต่ำ

#### Acceptance Criteria

1. WHEN เกษตรกรป้อนข้อมูลฟาร์ม (ขนาด ดิน สภาพอากาศ งบประมาณ ประสบการณ์), THE Crop_Recommendation_System SHALL return รายการพืช 3 อันดับแรกพร้อม ROI percentage และ risk score
2. THE Crop_Recommendation_System SHALL use เฉพาะ pre-planting features (farm_size, soil_type, soil_ph, weather, budget, experience, crop_characteristics) และ SHALL NOT use post-harvest features (actual_yield_kg, success_rate, harvest_timing_adjustment, yield_efficiency)
3. THE Crop_Recommendation_System SHALL implement NSGA-II algorithm, XGBoost algorithm, และ Random Forest algorithm สำหรับ multi-objective optimization
4. THE Crop_Recommendation_System SHALL achieve R² score ระหว่าง 0.45 ถึง 0.55 บน test dataset
5. THE Crop_Recommendation_System SHALL calculate total profit projection สำหรับแต่ละพืชที่แนะนำ โดยคำนวณจาก farm_size และ expected ROI

### Requirement 2: Planting Window Classification System (Model B)

**User Story:** ในฐานะเกษตรกร ฉันต้องการทราบว่าวันนี้เป็นช่วงเวลาที่เหมาะสมในการปลูกหรือไม่ เพื่อเพิ่มโอกาสความสำเร็จในการงอก

#### Acceptance Criteria

1. WHEN เกษตรกรป้อนข้อมูลดินและสภาพอากาศปัจจุบัน, THE Planting_Window_Classifier SHALL return classification (Good/Bad) พร้อม confidence percentage และ optimal planting time
2. THE Planting_Window_Classifier SHALL use เฉพาะ pre-planting observable data (soil_moisture, recent_rainfall, temperature, humidity, temporal_features) และ SHALL NOT use future data (harvest_date, actual_yield_kg, success_rate)
3. THE Planting_Window_Classifier SHALL implement time-aware data split โดย train บนข้อมูลอดีตและ test บนข้อมูลอนาคต
4. THE Planting_Window_Classifier SHALL achieve F1 score ระหว่าง 0.70 ถึง 0.75 บน test dataset
5. THE Planting_Window_Classifier SHALL provide expected germination success rate เมื่อ classification เป็น Good

### Requirement 3: Price Forecast System (Model C)

**User Story:** ในฐานะเกษตรกร ฉันต้องการทราบราคาพืชผลที่คาดว่าจะได้รับในอนาคต เพื่อวางแผนการเก็บเกี่ยวและการขาย

#### Acceptance Criteria

1. WHEN เกษตรกรระบุพืชและจำนวนวันจนถึงการเก็บเกี่ยว, THE Price_Forecast_System SHALL return price forecast พร้อม median, lower bound (Q0.1), upper bound (Q0.9), และ confidence level
2. THE Price_Forecast_System SHALL use market data, seasonal factors, และ current price ในการคาดการณ์
3. THE Price_Forecast_System SHALL achieve R² score มากกว่า 0.99 บน test dataset
4. THE Price_Forecast_System SHALL calculate expected revenue และ expected profit change เทียบกับราคาปัจจุบัน
5. THE Price_Forecast_System SHALL provide RMSE ไม่เกิน 0.30 baht per kilogram

### Requirement 4: Harvest Decision Engine (Model D)

**User Story:** ในฐานะเกษตรกร ฉันต้องการคำแนะนำว่าควรเก็บเกี่ยวเลยหรือรอ เพื่อให้ได้กำไรสูงสุด

#### Acceptance Criteria

1. WHEN เกษตรกรป้อนข้อมูลราคาปัจจุบัน ราคาคาดการณ์ สุขภาพพืช และต้นทุนการเก็บรักษา, THE Harvest_Decision_Engine SHALL return recommended action (Harvest Now, Wait 3 Days, Wait 7 Days) พร้อม profit projection สำหรับแต่ละตัวเลือก
2. THE Harvest_Decision_Engine SHALL implement Thompson Sampling algorithm (L4 Bandit approach) และ SHALL NOT use Deep Q-Network (L5)
3. THE Harvest_Decision_Engine SHALL use เฉพาะ observable pre-decision data (current_price, forecast_price, plant_health, storage_cost) และ SHALL NOT use post-decision data (actual_harvest_date, future_price, days_since_planting calculated from harvest_date)
4. THE Harvest_Decision_Engine SHALL achieve decision accuracy ประมาณ 68% เมื่อเทียบกับ actual best outcome
5. THE Harvest_Decision_Engine SHALL provide profit estimates ที่อยู่ภายใน ±20% ของ actual profit

### Requirement 5: Pipeline Integration System

**User Story:** ในฐานะเกษตรกร ฉันต้องการใช้ระบบที่เชื่อมโยงทั้ง 4 โมเดลเข้าด้วยกัน เพื่อติดตามและรับคำแนะนำตลอดฤดูกาลเพาะปลูก

#### Acceptance Criteria

1. THE Pipeline_Integration_System SHALL connect Model A, Model B, Model C, และ Model D ในลำดับที่ถูกต้อง (A → B → C → D)
2. WHEN เกษตรกรเริ่มฤดูกาลใหม่, THE Pipeline_Integration_System SHALL execute stage_1_crop_selection() เพื่อแนะนำพืช
3. WHEN เกษตรกรพร้อมปลูก, THE Pipeline_Integration_System SHALL execute stage_2_planting_window() เพื่อตรวจสอบช่วงเวลา
4. WHEN พืชเจริญเติบโต, THE Pipeline_Integration_System SHALL execute stage_3_price_forecast() เพื่อคาดการณ์ราคา
5. WHEN พืชพร้อมเก็บเกี่ยว, THE Pipeline_Integration_System SHALL execute stage_4_harvest_decision() เพื่อแนะนำการตัดสินใจ
6. THE Pipeline_Integration_System SHALL track farmer progress และ maintain state ตลอดฤดูกาล
7. THE Pipeline_Integration_System SHALL provide summary report พร้อม total profit projection

### Requirement 6: Data Leakage Prevention

**User Story:** ในฐานะนักพัฒนา ML ฉันต้องการมั่นใจว่าโมเดลไม่มี data leakage เพื่อให้ผลการทำนายมีความน่าเชื่อถือในการใช้งานจริง

#### Acceptance Criteria

1. THE Crop_Recommendation_System SHALL NOT include features ที่วัดได้หลังการเก็บเกี่ยว (actual_yield_kg, success_rate, harvest_timing_adjustment, yield_efficiency) ใน training features
2. THE Planting_Window_Classifier SHALL NOT include features จากอนาคต (harvest_date, actual_yield_kg) ใน training features
3. THE Harvest_Decision_Engine SHALL NOT calculate days_since_planting จาก harvest_date minus planting_date เนื่องจากเป็น tautological feature
4. THE Pipeline_Integration_System SHALL implement time-aware data splitting โดย training data มาจากอดีตและ test data มาจากอนาคต
5. THE Pipeline_Integration_System SHALL enforce embargo period อย่างน้อย 7 วัน ระหว่าง training และ validation datasets

### Requirement 7: Model Training and Validation

**User Story:** ในฐานะนักพัฒนา ML ฉันต้องการ train และ validate โมเดลด้วยข้อมูลที่สะอาด เพื่อให้ได้ performance metrics ที่ซื่อสัตย์

#### Acceptance Criteria

1. THE Crop_Recommendation_System SHALL provide DataLoaderClean class ที่ load ข้อมูลโดยไม่มี post-outcome features
2. THE Planting_Window_Classifier SHALL implement temporal cross-validation โดยใช้ time-based splits
3. WHEN training โมเดลใดๆ, THE Pipeline_Integration_System SHALL log training metrics, validation metrics, และ test metrics แยกกัน
4. THE Pipeline_Integration_System SHALL provide model evaluation methods ที่คำนวณ R², F1, RMSE, MAPE, และ profit accuracy
5. THE Pipeline_Integration_System SHALL save trained models พร้อม metadata (training_date, features_used, performance_metrics)
6. WHEN training โมเดลใดๆ, THE Pipeline_Integration_System SHALL validate ว่าแต่ละ feature มี correlation ที่ make sense กับ target variable และ SHALL document correlation analysis results
7. WHEN training โมเดลใดๆ, THE Pipeline_Integration_System SHALL check สำหรับ data leakage โดยตรวจสอบว่า features ทั้งหมดเป็น pre-decision observable data และ SHALL NOT include post-outcome features
8. WHEN training โมเดลใดๆ, THE Pipeline_Integration_System SHALL detect overfitting โดยเปรียบเทียบ training metrics กับ validation metrics และ SHALL flag เมื่อ gap มากกว่า 15%
9. WHEN training หรือ testing โมเดลใดๆ, THE Pipeline_Integration_System SHALL capture และ save visualization plots (confusion matrix, ROC curve, feature importance, learning curves, residual plots) ไปยัง designated output folder
10. THE Pipeline_Integration_System SHALL label แต่ละ captured plot ด้วย metadata (model_name, evaluation_type, metric_name, timestamp) เพื่อให้สามารถระบุได้ว่าเป็น model evaluation ประเภทใด

### Requirement 8: Real-World Testing and Demonstration

**User Story:** ในฐานะผู้ใช้งาน ฉันต้องการทดสอบระบบด้วย scenario จริง เพื่อเห็นว่าระบบทำงานอย่างไรตลอดฤดูกาล

#### Acceptance Criteria

1. THE Pipeline_Integration_System SHALL provide test scenario ที่จำลองเกษตรกรจริง (เช่น Farmer Somchai) ตลอด 4 stages
2. WHEN running test scenario, THE Pipeline_Integration_System SHALL output ผลลัพธ์ของแต่ละ stage พร้อม profit calculations
3. THE Pipeline_Integration_System SHALL demonstrate complete user journey จาก crop selection ถึง harvest decision
4. THE Pipeline_Integration_System SHALL provide executable test script ที่สามารถ run ได้ด้วย command line
5. THE Pipeline_Integration_System SHALL validate ว่าผลลัพธ์ของแต่ละ stage สมเหตุสมผลและสอดคล้องกับ input data

### Requirement 9: Documentation and Code Quality

**User Story:** ในฐานะนักพัฒนา ฉันต้องการเอกสารที่ครบถ้วนและโค้ดที่มีคุณภาพ เพื่อให้สามารถบำรุงรักษาและพัฒนาต่อได้

#### Acceptance Criteria

1. THE Pipeline_Integration_System SHALL provide README.md ที่อธิบาย architecture, usage, และ getting started guide
2. THE Pipeline_Integration_System SHALL provide QUICK_START.md ที่มี step-by-step tutorial
3. THE Pipeline_Integration_System SHALL provide TECHNICAL_GUIDE.md ที่อธิบาย implementation details
4. THE Pipeline_Integration_System SHALL provide LEAKAGE_PREVENTION.md ที่อธิบายวิธีป้องกัน data leakage
5. THE Pipeline_Integration_System SHALL include logging statements ใน critical functions สำหรับ debugging
6. THE Pipeline_Integration_System SHALL handle errors gracefully และ provide meaningful error messages
7. THE Pipeline_Integration_System SHALL use relative paths และ SHALL NOT use hard-coded absolute paths

### Requirement 10: Performance and Scalability

**User Story:** ในฐานะผู้ดูแลระบบ ฉันต้องการให้ระบบทำงานได้รวดเร็วและรองรับเกษตรกรจำนวนมาก เพื่อให้สามารถใช้งานจริงได้

#### Acceptance Criteria

1. WHEN เกษตรกรขอคำแนะนำ, THE Pipeline_Integration_System SHALL return ผลลัพธ์ภายใน 10 วินาที
2. THE Pipeline_Integration_System SHALL support การประมวลผลสำหรับเกษตรกร 1000+ คนพร้อมกัน
3. THE Crop_Recommendation_System SHALL cache crop characteristics data เพื่อลดเวลาการโหลด
4. THE Price_Forecast_System SHALL update price forecasts ทุกวันโดยอัตโนมัติ
5. THE Pipeline_Integration_System SHALL provide batch processing capability สำหรับการ train โมเดลใหม่
