// Valid values that match ML model requirements
export const VALID_SOIL_TYPES = ['ดินร่วน', 'ดินร่วนปนทราย', 'ดินเหนียว', 'ดินทราย'];
export const VALID_WATER_LEVELS = ['สูง', 'ปานกลาง', 'ต่ำ'];
export const VALID_BUDGET_LEVELS = ['สูง', 'ปานกลาง', 'ต่ำ'];
export const VALID_RISK_LEVELS = ['สูง', 'ปานกลาง', 'ต่ำ'];

export interface ProfileData {
  province?: string;
  soil_type?: string;
  water_availability?: string;
  budget_level?: string;
  risk_tolerance?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export const validateProvince = (province: string | undefined, validProvinces: string[]): boolean => {
  if (!province) return true; // Optional field
  return validProvinces.includes(province);
};

export const validateSoilType = (soilType: string | undefined): boolean => {
  if (!soilType) return true; // Optional field
  return VALID_SOIL_TYPES.includes(soilType);
};

export const validateWaterAvailability = (water: string | undefined): boolean => {
  if (!water) return true; // Optional field
  return VALID_WATER_LEVELS.includes(water);
};

export const validateBudgetLevel = (budget: string | undefined): boolean => {
  if (!budget) return true; // Optional field
  return VALID_BUDGET_LEVELS.includes(budget);
};

export const validateRiskTolerance = (risk: string | undefined): boolean => {
  if (!risk) return true; // Optional field
  return VALID_RISK_LEVELS.includes(risk);
};

export const validateProfileData = (
  data: ProfileData,
  validProvinces: string[]
): ValidationResult => {
  const errors: string[] = [];

  // Validate province
  if (data.province && !validateProvince(data.province, validProvinces)) {
    errors.push('จังหวัดที่เลือกไม่ถูกต้อง');
  }

  // Validate soil type
  if (data.soil_type && !validateSoilType(data.soil_type)) {
    errors.push(`ประเภทดินไม่ถูกต้อง กรุณาเลือก: ${VALID_SOIL_TYPES.join(', ')}`);
  }

  // Validate water availability
  if (data.water_availability && !validateWaterAvailability(data.water_availability)) {
    errors.push(`ระดับแหล่งน้ำไม่ถูกต้อง กรุณาเลือก: ${VALID_WATER_LEVELS.join(', ')}`);
  }

  // Validate budget level
  if (data.budget_level && !validateBudgetLevel(data.budget_level)) {
    errors.push(`ระดับงบประมาณไม่ถูกต้อง กรุณาเลือก: ${VALID_BUDGET_LEVELS.join(', ')}`);
  }

  // Validate risk tolerance
  if (data.risk_tolerance && !validateRiskTolerance(data.risk_tolerance)) {
    errors.push(`ระดับความเสี่ยงไม่ถูกต้อง กรุณาเลือก: ${VALID_RISK_LEVELS.join(', ')}`);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};
