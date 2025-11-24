# Table of Contents

## FarmMe: An Integrated Machine Learning System for Agricultural Decision Support

---

### Front Matter

**Title Page** ............................................................. i  
**Abstract** ............................................................. iii  
**Executive Summary** .................................................... v  
**Table of Contents** ................................................... xi  
**List of Figures** ..................................................... xv  
**List of Tables** ...................................................... xvii  
**List of Algorithms** .................................................. xix  
**Acknowledgments** ..................................................... xxi  

---

## Chapter 1: Introduction ............................................. 1

**1.1** Smart City Agricultural Component: Context and Motivation ........... 2  
&nbsp;&nbsp;&nbsp;&nbsp;1.1.1 The Smart City Vision ................................. 2  
&nbsp;&nbsp;&nbsp;&nbsp;1.1.2 Agricultural Challenges in the Digital Age ............... 3  
&nbsp;&nbsp;&nbsp;&nbsp;1.1.3 The Role of Machine Learning .......................... 4  

**1.2** Problem Statement and Research Questions ........................... 5  
&nbsp;&nbsp;&nbsp;&nbsp;1.2.1 Core Problem Definition ............................... 5  
&nbsp;&nbsp;&nbsp;&nbsp;1.2.2 Specific Research Questions ........................... 6  
&nbsp;&nbsp;&nbsp;&nbsp;1.2.3 System-Level Research Questions ....................... 8  

**1.3** System Scope and Boundaries ....................................... 9  
&nbsp;&nbsp;&nbsp;&nbsp;1.3.1 Geographical Scope ................................... 9  
&nbsp;&nbsp;&nbsp;&nbsp;1.3.2 Temporal Scope ....................................... 10  
&nbsp;&nbsp;&nbsp;&nbsp;1.3.3 Crop Coverage ........................................ 10  
&nbsp;&nbsp;&nbsp;&nbsp;1.3.4 Technical Scope ...................................... 11  
&nbsp;&nbsp;&nbsp;&nbsp;1.3.5 Limitations and Constraints .......................... 12  

**1.4** Proof of Concept Objectives ....................................... 13  
&nbsp;&nbsp;&nbsp;&nbsp;1.4.1 Primary Objectives ................................... 13  
&nbsp;&nbsp;&nbsp;&nbsp;1.4.2 Smart City Integration Objectives .................... 14  
&nbsp;&nbsp;&nbsp;&nbsp;1.4.3 Research Contribution Objectives ..................... 15  

**1.5** Contributions and Innovations ..................................... 16  
&nbsp;&nbsp;&nbsp;&nbsp;1.5.1 Technical Contributions .............................. 16  
&nbsp;&nbsp;&nbsp;&nbsp;1.5.2 System-Level Contributions ........................... 18  
&nbsp;&nbsp;&nbsp;&nbsp;1.5.3 Methodological Contributions ......................... 19  

**1.6** Thesis Organization ............................................... 20  

---

## Chapter 2: Data Generation and Engineering Pipeline ................. 23

**2.1** Overview: GPU-Accelerated Synthetic Data Generation ............... 24  
**2.2** Spatial Correlation Modeling ..................................... 27  
**2.3** Temporal Dependency Modeling ..................................... 30  
**2.4** Weather Data Generation .......................................... 33  
**2.5** Price Data Generation ............................................ 36  
**2.6** Cultivation Data Generation ...................................... 41  
**2.7** Economic Indicators Generation ................................... 45  
**2.8** Data Quality and Validation ...................................... 49  
**2.9** Feature Engineering Pipeline ..................................... 52  
**2.10** Data Leakage Prevention Framework ............................... 59  
**2.11** Dataset Statistics and Characteristics .......................... 62  
**2.12** Computational Performance Analysis .............................. 65  
**2.13** Summary and Key Takeaways ....................................... 68  

---

## Chapter 3: Background and Related Work .............................. 71

**3.1** Introduction ..................................................... 72  
**3.2** Machine Learning in Agriculture .................................. 73  
**3.3** Multi-Objective Optimization .................................... 80  
**3.4** Time Series Forecasting ......................................... 87  
**3.5** Multi-Armed Bandits and Reinforcement Learning .................. 95  
**3.6** Data Leakage in Machine Learning ................................ 105  
**3.7** Related Systems and Platforms ................................... 113  
**3.8** Research Gaps and Opportunities ................................. 117  
**3.9** Summary ......................................................... 120  

---

## Chapter 4: Model A - Crop Recommendation System .................... 123

**4.1** Introduction and Problem Formulation ............................ 124  
**4.2** System Architecture ............................................. 129  
**4.3** Algorithm 1: NSGA-II Multi-Objective Optimization ............... 134  
**4.4** Algorithm 2: XGBoost Regression ................................. 143  
**4.5** Algorithm 3: Random Forest + ElasticNet Ensemble ................ 148  
**4.6** Data Leakage Prevention ......................................... 152  
**4.7** Experimental Results ............................................ 156  
**4.8** Ablation Studies ................................................ 163  
**4.9** Case Study: Multi-Objective Trade-offs .......................... 167  
**4.10** Discussion ..................................................... 170  
**4.11** Summary ........................................................ 173  

---

## Chapter 5: Model B - Planting Window Classification ................ 175

**5.1** Introduction and Problem Formulation ............................ 176  
**5.2** The Challenge of Seasonal Prediction ............................ 179  
**5.3** Cyclical Temporal Encoding: Key Innovation ...................... 182  
**5.4** Algorithm 1: Logistic Regression with Cyclical Features ......... 186  
**5.5** Algorithm 2: XGBoost Classifier ................................. 191  
**5.6** Algorithm 3: Temporal Gradient Boosting ......................... 195  
**5.7** Data Leakage Prevention ......................................... 199  
**5.8** Experimental Results ............................................ 202  
**5.9** Simple vs Complex Models: Analysis .............................. 209  
**5.10** Discussion ..................................................... 213  
**5.11** Summary ........................................................ 216  

---

## Chapter 6: Model C - Price Forecasting with Bias Reduction ......... 219

**6.1** Introduction and Problem Formulation ............................ 220  
**6.2** Temporal Bias: Discovery and Definition ......................... 223  
**6.3** Measuring Temporal Bias ......................................... 228  
**6.4** Baseline Model: XGBoost with Historical Prices .................. 232  
**6.5** Improved Model: Multi-Source Integration ........................ 237  
**6.6** Weather Data Integration ........................................ 242  
**6.7** Economic Indicators Integration ................................. 246  
**6.8** Data Leakage Prevention ......................................... 250  
**6.9** Experimental Results ............................................ 254  
**6.10** Temporal Bias Reduction Analysis ............................... 261  
**6.11** Market Shock Resilience ........................................ 266  
**6.12** Discussion ..................................................... 270  
**6.13** Summary ........................................................ 274  

---

## Chapter 7: Model D - Harvest Decision Optimization ................. 277

**7.1** Introduction and Problem Formulation ............................ 278  
**7.2** Sequential Decision-Making Framework ............................. 281  
**7.3** Thompson Sampling: Bayesian Approach ............................ 285  
**7.4** Implementation Details .......................................... 290  
**7.5** Price Prediction Integration .................................... 295  
**7.6** Risk Management ................................................. 299  
**7.7** Data Leakage Prevention ......................................... 303  
**7.8** Experimental Results ............................................ 306  
**7.9** Comparison with Alternative Approaches .......................... 312  
**7.10** Case Study: Harvest Timing Scenarios ........................... 317  
**7.11** Discussion ..................................................... 321  
**7.12** Summary ........................................................ 324  

---

## Chapter 8: System Integration and Architecture ..................... 327

**8.1** Introduction ..................................................... 328  
**8.2** System Architecture Overview ..................................... 330  
**8.3** Backend Architecture ............................................. 335  
**8.4** Database Design .................................................. 341  
**8.5** API Design and Implementation .................................... 347  
**8.6** Model Integration Pipeline ....................................... 353  
**8.7** Caching and Performance Optimization ............................. 359  
**8.8** Error Handling and Resilience .................................... 364  
**8.9** Monitoring and Observability ..................................... 369  
**8.10** Security and Authentication ..................................... 374  
**8.11** Deployment Architecture ......................................... 378  
**8.12** Performance Benchmarks .......................................... 383  
**8.13** Summary ......................................................... 388  

---

## Chapter 9: Experimental Results and Evaluation ..................... 391

**9.1** Introduction ..................................................... 392  
**9.2** Evaluation Methodology ........................................... 394  
**9.3** Dataset Characteristics .......................................... 399  
**9.4** Model A: Crop Recommendation Results ............................. 404  
**9.5** Model B: Planting Window Results ................................. 410  
**9.6** Model C: Price Forecasting Results ............................... 416  
**9.7** Model D: Harvest Decision Results ................................ 423  
**9.8** End-to-End System Evaluation ..................................... 429  
**9.9** Case Study 1: Rice Farmer ........................................ 435  
**9.10** Case Study 2: Vegetable Farmer .................................. 440  
**9.11** Case Study 3: Commercial Farm ................................... 445  
**9.12** Statistical Significance Testing ................................ 450  
**9.13** Summary ......................................................... 455  

---

## Chapter 10: Discussion .............................................. 459

**10.1** Key Findings .................................................... 460  
**10.2** Temporal Bias: Implications ..................................... 465  
**10.3** Data Leakage: Lessons Learned ................................... 470  
**10.4** Simple vs Complex Models ........................................ 475  
**10.5** Multi-Objective Optimization Benefits ........................... 480  
**10.6** System Integration Challenges ................................... 485  
**10.7** Limitations ..................................................... 490  
**10.8** Threats to Validity ............................................. 495  
**10.9** Generalizability ................................................ 500  
**10.10** Ethical Considerations ......................................... 505  
**10.11** Future Research Directions ..................................... 510  

---

## Chapter 11: Conclusion .............................................. 515

**11.1** Summary of Contributions ........................................ 516  
**11.2** Research Questions Answered ..................................... 520  
**11.3** Technical Achievements .......................................... 524  
**11.4** Methodological Advances ......................................... 528  
**11.5** Practical Impact ................................................ 532  
**11.6** Future Work ..................................................... 536  
**11.7** Final Remarks ................................................... 540  

---

### Appendices

**Appendix A**: Complete Algorithm Pseudocode ............................ 543  
**Appendix B**: Hyperparameter Tuning Details ............................ 551  
**Appendix C**: Additional Experimental Results .......................... 559  
**Appendix D**: API Documentation ........................................ 567  
**Appendix E**: Database Schema .......................................... 575  
**Appendix F**: Statistical Test Details ................................. 583  

---

### Bibliography

**References** ........................................................... 591  

---

### Index

**Index** ................................................................ 615  

---

**Total Pages**: Approximately 620 pages  
**Word Count**: Approximately 82,000 words  
**Figures**: 87 figures  
**Tables**: 64 tables  
**Algorithms**: 12 algorithms  
