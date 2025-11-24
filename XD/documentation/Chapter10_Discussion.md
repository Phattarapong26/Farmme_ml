# Chapter 10: Discussion and Analysis

## 10.1 Introduction

This chapter provides critical analysis of the experimental results, discusses lessons learned, examines implications for both practice and research, and addresses the limitations of the FarmMe system. We reflect on the research questions posed in Chapter 1 and evaluate the extent to which they have been answered.

## 10.2 Research Questions Revisited

### 10.2.1 RQ1: Multi-Objective Crop Recommendation

**Research Question:**
*How can multi-objective optimization techniques be applied to crop recommendation systems to balance profitability, risk, and sustainability while preventing data leakage?*

**Answer:**

The FarmMe system successfully demonstrates that NSGA-II can be effectively combined with XGBoost for multi-objective crop recommendation:

**Technical Achievement:**
- NSGA-II generates Pareto-optimal crop portfolios
- XGBoost provides accurate ROI predictions (R² = 0.9944)
- Three objectives balanced: ROI (40%), Risk (30%), Stability (30%)
- Data leakage prevented through temporal validation

**Key Insights:**

1. **Multi-Objective is Essential**
   - Single-objective optimization (maximize ROI only) recommends high-risk crops
   - Farmers need trade-off options based on risk tolerance
   - Pareto front provides choice, not single answer

2. **XGBoost as Fitness Function**
   - Fast evaluation (< 1ms per individual)
   - Accurate predictions enable reliable optimization
   - Regularization prevents overfitting in fitness evaluation

3. **Data Leakage Prevention is Critical**
   - Without temporal validation: R² = 0.999 (too good to be true)
   - With temporal validation: R² = 0.994 (realistic)
   - Honest evaluation builds trust

**Limitations:**
- NSGA-II computational cost (30 seconds per recommendation)
- Limited to three objectives (could expand to sustainability, water use)
- Synthetic data (needs real-world validation)

**Contribution:**
First demonstration of ML-MOEA hybrid for agricultural crop recommendation with rigorous data leakage prevention.

### 10.2.2 RQ2: Temporal Decision Making

**Research Question:**
*How can machine learning models effectively predict optimal planting windows while accounting for seasonal variations and regional differences?*

**Answer:**

Model B demonstrates that simple logistic regression with cyclical temporal encoding outperforms complex tree-based models:

**Surprising Finding