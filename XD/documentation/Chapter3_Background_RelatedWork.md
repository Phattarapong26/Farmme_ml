# Chapter 3: Background and Related Work

## 3.1 Introduction

This chapter provides a comprehensive review of the theoretical foundations and related work that inform the FarmMe system. We organize the review into five main areas:

1. **Machine Learning in Agriculture** (Section 3.2)
2. **Multi-Objective Optimization** (Section 3.3)
3. **Time Series Forecasting** (Section 3.4)
4. **Multi-Armed Bandits and Reinforcement Learning** (Section 3.5)
5. **Data Leakage in Machine Learning** (Section 3.6)

Each section reviews relevant literature, establishes theoretical foundations, and identifies gaps that the FarmMe system addresses.

## 3.2 Machine Learning in Agriculture

### 3.2.1 Historical Context

The application of machine learning to agriculture has evolved through several distinct phases:

**Phase 1: Expert Systems (1980s-1990s)**
- Rule-based systems for crop selection and pest management
- Limited by manual knowledge engineering
- Examples: COMAX (cotton management), GOSSYM (crop simulation)

**Phase 2: Statistical Models (1990s-2000s)**
- Linear regression for yield prediction
- Logistic regression for disease classification
- Limited feature engineering capabilities

**Phase 3: Machine Learning Era (2000s-2010s)**
- Support Vector Machines (SVM) for crop classification
- Random Forests for yield prediction
- Neural networks for image-based plant disease detection

**Phase 4: Deep Learning and Big Data (2010s-Present)**
- Convolutional Neural Networks (CNN) for crop monitoring
- Recurrent Neural Networks (RNN) for time series forecasting
- Integration of satellite imagery, IoT sensors, and weather data

### 3.2.2 Crop Recommendation Systems

**Traditional Approaches:**

1. **Rule-Based Systems**
   - Use expert knowledge encoded as if-then rules
   - Example: "IF soil_pH > 7 AND rainfall > 1000mm THEN recommend_rice"
   - Limitations: Cannot handle uncertainty, difficult to maintain

2. **Statistical Models**
   - Linear regression: Yield = β₀ + β₁×rainfall + β₂×temperature + ε
   - Limitations: Assumes linear relationships, cannot capture complex interactions

**Modern ML Approaches:**

1. **Classification-Based Systems**
   - Treat crop recommendation as multi-class classification
   - Algorithms: Decision Trees, Random Forest, SVM, Neural Networks
   - Example: Pudumalar et al. (2016) - Naive Bayes for crop prediction (accuracy: 88%)

2. **Regression-Based Systems**
   - Predict yield for each crop, recommend highest-yielding crop
   - Algorithms: Linear Regression, Ridge, Lasso, XGBoost
   - Example: Khosla et al. (2010) - Precision agriculture using regression models

3. **Ensemble Methods**
   - Combine multiple models for robust predictions
   - Example: Ramesh & Vardhan (2015) - Ensemble of DT, RF, SVM (accuracy: 92%)

**Limitations of Existing Systems:**
- Single-objective optimization (usually profit or yield)
- No consideration of risk or sustainability
- Limited handling of farmer constraints (budget, land, experience)
- Lack of interpretability in complex models

### 3.2.3 Planting Window Prediction

**Agronomic Foundations:**
- Optimal planting windows depend on temperature, rainfall, and day length
- Early/late planting can reduce yields by 20-50%
- Regional and crop-specific variations

**ML Approaches:**

1. **Classification Models**
   - Binary classification: optimal vs. suboptimal
   - Multi-class: early/optimal/late windows
   - Features: historical weather, soil moisture, crop phenology

2. **Time Series Analysis**
   - ARIMA models for weather forecasting
   - Seasonal decomposition for planting patterns
   - Example: Lobell et al. (2007) - Climate trends and crop yields

3. **Hybrid Approaches**
   - Combine crop growth models with ML
   - Example: DSSAT (Decision Support System for Agrotechnology Transfer)
   - Limitations: Require extensive calibration, computationally expensive

**Research Gaps:**
- Limited integration of real-time weather forecasts
- Insufficient consideration of market timing
- Lack of province-specific recommendations for Thailand

### 3.2.4 Agricultural Price Forecasting

**Economic Foundations:**
- Agricultural prices exhibit high volatility (σ = 15-30%)
- Seasonal patterns (harvest seasons → price drops)
- Supply-demand dynamics
- External shocks (weather, policy, global markets)

**Traditional Econometric Models:**

1. **ARIMA (AutoRegressive Integrated Moving Average)**
   - P(t) = c + φ₁P(t-1) + ... + φₚP(t-p) + θ₁ε(t-1) + ... + θₑε(t-q) + ε(t)
   - Strengths: Simple, interpretable, works for stationary series
   - Limitations: Cannot capture non-linear relationships

2. **GARCH (Generalized AutoRegressive Conditional Heteroskedasticity)**
   - Models time-varying volatility
   - σ²(t) = α₀ + α₁ε²(t-1) + β₁σ²(t-1)
   - Used for risk management and option pricing

3. **Vector Autoregression (VAR)**
   - Models multiple time series simultaneously
   - Captures cross-commodity relationships
   - Example: Wheat price affects flour price

**Machine Learning Approaches:**

1. **Support Vector Regression (SVR)**
   - Non-linear regression using kernel trick
   - Example: Tian et al. (2015) - Corn price forecasting (RMSE: 0.12)

2. **Random Forest Regression**
   - Ensemble of decision trees
   - Handles non-linear relationships and interactions
   - Example: Ribeiro & Oliveira (2011) - Soybean price prediction

3. **Neural Networks**
   - Multi-Layer Perceptron (MLP) for price prediction
   - LSTM (Long Short-Term Memory) for sequential data
   - Example: Xiong et al. (2018) - LSTM for agricultural commodities (MAE: 2.3%)

4. **Gradient Boosting (XGBoost, LightGBM)**
   - State-of-the-art for tabular data
   - Handles missing values, feature interactions
   - Example: Chen & Guestrin (2016) - XGBoost framework

**External Factors Integration:**
- Weather data (temperature, rainfall) → supply shocks
- Economic indicators (GDP, inflation) → demand shifts
- Policy variables (subsidies, tariffs) → market interventions
- Example: Ubilava (2012) - El Niño effects on agricultural prices

**Research Gaps:**
- High temporal bias (over-reliance on recent prices)
- Limited robustness to market shocks
- Insufficient integration of weather and economic data
- Lack of bias quantification methodologies

### 3.2.5 Harvest Timing Optimization

**Agronomic Considerations:**
- Crop maturity indicators (color, moisture content, sugar levels)
- Weather windows (avoid rain during harvest)
- Labor availability
- Storage capacity

**Economic Considerations:**
- Current market price vs. expected future price
- Storage costs (0.1-0.3% per day)
- Quality degradation over time
- Opportunity cost of delayed harvest

**Optimization Approaches:**

1. **Dynamic Programming**
   - Optimal stopping problem
   - V(t) = max{harvest_now, E[V(t+1)]}
   - Limitations: Requires accurate price forecasts, computationally expensive

2. **Real Options Theory**
   - Treat harvest decision as financial option
   - Black-Scholes framework adapted for agriculture
   - Example: Isik et al. (2003) - Optimal harvest timing for timber

3. **Stochastic Control**
   - Model price as stochastic process (Geometric Brownian Motion)
   - dP = μP dt + σP dW
   - Solve Hamilton-Jacobi-Bellman equation

**Machine Learning Approaches:**
- Reinforcement Learning (Q-Learning, Policy Gradient)
- Multi-Armed Bandits (Thompson Sampling, UCB)
- Limited prior work in agricultural harvest timing

**Research Gaps:**
- Most work focuses on perennial crops (timber, orchards)
- Limited application to annual crops with short harvest windows
- Insufficient handling of uncertainty in price forecasts
- Lack of practical implementations for smallholder farmers

## 3.3 Multi-Objective Optimization

### 3.3.1 Theoretical Foundations

**Pareto Optimality:**

A solution x* is Pareto optimal if there exists no other solution x such that:
- f_i(x) ≥ f_i(x*) for all objectives i
- f_j(x) > f_j(x*) for at least one objective j

**Pareto Front:**
The set of all Pareto optimal solutions forms the Pareto front, representing the trade-off surface between competing objectives.

**Dominance Relations:**
- Solution A dominates solution B if A is better in at least one objective and no worse in all others
- Non-dominated solutions form the Pareto front

### 3.3.2 Multi-Objective Evolutionary Algorithms (MOEAs)

**Classical Algorithms:**

1. **NSGA (Non-dominated Sorting Genetic Algorithm)**
   - Srinivas & Deb (1994)
   - Ranks solutions by dominance levels
   - Limitations: High computational complexity O(MN³)

2. **NSGA-II (Improved NSGA)**
   - Deb et al. (2002)
   - Fast non-dominated sorting: O(MN²)
   - Crowding distance for diversity preservation
   - Elitism through (μ+λ) selection

3. **SPEA2 (Strength Pareto Evolutionary Algorithm 2)**
   - Zitzler et al. (2001)
   - External archive for elite solutions
   - Fitness assignment based on dominance strength

4. **MOEA/D (Multi-Objective Evolutionary Algorithm based on Decomposition)**
   - Zhang & Li (2007)
   - Decomposes multi-objective problem into scalar subproblems
   - Efficient for many-objective optimization (>3 objectives)

### 3.3.3 NSGA-II Algorithm Details

**Algorithm Structure:**
```
1. Initialize population P₀ randomly
2. For generation t = 0 to T:
   a. Create offspring Q_t through crossover and mutation
   b. Combine R_t = P_t ∪ Q_t
   c. Fast non-dominated sorting of R_t
   d. Calculate crowding distance for each front
   e. Select best N solutions for P_{t+1}
3. Return final Pareto front
```

**Fast Non-Dominated Sorting:**
- Complexity: O(MN²) where M = objectives, N = population
- Assigns rank to each solution (rank 1 = non-dominated)
- Creates fronts F₁, F₂, ..., Fₖ

**Crowding Distance:**
- Measures density of solutions in objective space
- Promotes diversity along Pareto front
- Distance(i) = Σⱼ [f_j(i+1) - f_j(i-1)] / [f_j^max - f_j^min]

**Genetic Operators:**
- **Selection**: Binary tournament based on rank and crowding distance
- **Crossover**: Simulated Binary Crossover (SBX) for real-valued variables
- **Mutation**: Polynomial mutation with distribution index

### 3.3.4 Applications in Agriculture

**Crop Planning:**
- Objectives: Maximize profit, minimize risk, maximize sustainability
- Constraints: Land, water, labor, budget
- Example: Sarker & Ray (2009) - Multi-objective crop planning in Bangladesh

**Irrigation Scheduling:**
- Objectives: Maximize yield, minimize water use, minimize energy cost
- Example: Reddy & Kumar (2006) - Multi-objective irrigation optimization

**Fertilizer Management:**
- Objectives: Maximize yield, minimize cost, minimize environmental impact
- Example: Dury et al. (2012) - Nitrogen management optimization

**Limitations of Existing Work:**
- Most studies use simplified objective functions
- Limited integration with ML models for yield/price prediction
- Insufficient handling of uncertainty
- Lack of real-world validation with farmers

### 3.3.5 Hybrid ML-MOEA Approaches

**Surrogate-Assisted Optimization:**
- Use ML models as fitness evaluators
- Reduces computational cost of expensive simulations
- Example: Jin (2011) - Surrogate-assisted evolutionary computation

**ML for Feature Selection in MOO:**
- Use evolutionary algorithms to select optimal feature subsets
- Multiple objectives: accuracy, complexity, interpretability
- Example: Xue et al. (2016) - Multi-objective feature selection

**Adaptive Parameter Control:**
- Use ML to adapt MOEA parameters during evolution
- Example: Eiben et al. (2007) - Parameter control in evolutionary algorithms

**Research Gaps:**
- Limited work on ML-MOEA hybrids for agricultural applications
- Insufficient handling of data leakage in ML-based fitness evaluation
- Lack of interpretable multi-objective crop recommendation systems

## 3.4 Time Series Forecasting

### 3.4.1 Classical Time Series Methods

**Decomposition:**
- Additive: Y(t) = T(t) + S(t) + R(t)
- Multiplicative: Y(t) = T(t) × S(t) × R(t)
- Where: T = trend, S = seasonal, R = residual

**Exponential Smoothing:**
- Simple: ŷ(t+1) = αy(t) + (1-α)ŷ(t)
- Holt-Winters: Adds trend and seasonal components
- Automatic parameter selection via AIC/BIC

**ARIMA Models:**
- AR(p): y(t) = c + Σᵢφᵢy(t-i) + ε(t)
- MA(q): y(t) = μ + ε(t) + Σⱼθⱼε(t-j)
- ARIMA(p,d,q): Combines AR, differencing, MA
- Model selection: ACF/PACF plots, information criteria

**Seasonal ARIMA (SARIMA):**
- ARIMA(p,d,q)(P,D,Q)ₛ
- Handles both non-seasonal and seasonal patterns
- Example: Agricultural prices with annual cycles

### 3.4.2 Machine Learning for Time Series

**Feature Engineering:**
- Lag features: y(t-1), y(t-2), ..., y(t-k)
- Rolling statistics: mean, std, min, max over windows
- Date features: day_of_week, month, season
- Fourier features: sin/cos transformations for seasonality

**Algorithms:**

1. **Linear Models**
   - Ridge Regression: L2 regularization
   - Lasso Regression: L1 regularization (feature selection)
   - Elastic Net: Combines L1 and L2

2. **Tree-Based Models**
   - Random Forest: Ensemble of decision trees
   - Gradient Boosting: Sequential error correction
   - XGBoost: Regularized gradient boosting with parallel processing

3. **Neural Networks**
   - MLP: Fully connected layers
   - CNN: Convolutional layers for pattern detection
   - RNN/LSTM: Recurrent connections for sequential data
   - GRU: Simplified LSTM with fewer parameters

**Ensemble Methods:**
- Stacking: Train meta-model on predictions of base models
- Blending: Weighted average of multiple models
- Example: Makridakis et al. (2018) - M4 Competition results

### 3.4.3 Deep Learning for Time Series

**Recurrent Neural Networks (RNN):**
- h(t) = tanh(W_hh h(t-1) + W_xh x(t) + b_h)
- y(t) = W_hy h(t) + b_y
- Problem: Vanishing/exploding gradients

**Long Short-Term Memory (LSTM):**
- Forget gate: f(t) = σ(W_f [h(t-1), x(t)] + b_f)
- Input gate: i(t) = σ(W_i [h(t-1), x(t)] + b_i)
- Output gate: o(t) = σ(W_o [h(t-1), x(t)] + b_o)
- Cell state: C(t) = f(t)⊙C(t-1) + i(t)⊙tanh(W_C [h(t-1), x(t)] + b_C)
- Hidden state: h(t) = o(t)⊙tanh(C(t))

**Gated Recurrent Unit (GRU):**
- Simplified LSTM with 2 gates instead of 3
- Faster training, similar performance
- Update gate: z(t) = σ(W_z [h(t-1), x(t)])
- Reset gate: r(t) = σ(W_r [h(t-1), x(t)])

**Attention Mechanisms:**
- Allows model to focus on relevant time steps
- Transformer architecture (Vaswani et al., 2017)
- Self-attention: Attention(Q,K,V) = softmax(QK^T/√d_k)V

**Temporal Convolutional Networks (TCN):**
- Dilated causal convolutions
- Parallel processing (faster than RNN)
- Example: Bai et al. (2018) - TCN outperforms LSTM on many tasks

### 3.4.4 Multivariate Time Series Forecasting

**Vector Autoregression (VAR):**
- Y(t) = A₁Y(t-1) + ... + AₚY(t-p) + ε(t)
- Where Y(t) is vector of multiple time series
- Captures cross-series dependencies

**Multivariate LSTM:**
- Multiple input features at each time step
- Shared hidden state captures cross-variable relationships
- Example: Qin et al. (2017) - Dual-stage attention LSTM

**Graph Neural Networks for Time Series:**
- Model spatial dependencies as graph
- Temporal dependencies via RNN/CNN
- Example: Yu et al. (2018) - Spatio-temporal graph convolutional networks

### 3.4.5 Evaluation Metrics

**Point Forecast Metrics:**
- MAE (Mean Absolute Error): (1/n)Σ|y_i - ŷ_i|
- RMSE (Root Mean Squared Error): √[(1/n)Σ(y_i - ŷ_i)²]
- MAPE (Mean Absolute Percentage Error): (100/n)Σ|y_i - ŷ_i|/|y_i|
- R² (Coefficient of Determination): 1 - SS_res/SS_tot

**Probabilistic Forecast Metrics:**
- Quantile Loss: ρ_τ(y - ŷ) = (τ-1)(y-ŷ) if y<ŷ, else τ(y-ŷ)
- Continuous Ranked Probability Score (CRPS)
- Prediction Interval Coverage Probability (PICP)

**Directional Accuracy:**
- Percentage of correct direction predictions
- Important for trading strategies



## 3.5 Multi-Armed Bandits and Reinforcement Learning

### 3.5.1 The Multi-Armed Bandit Problem

**Problem Formulation:**
- K arms (actions), each with unknown reward distribution
- At each time step t, select arm a(t) and receive reward r(t)
- Goal: Maximize cumulative reward Σᵗ r(t)
- Trade-off: Exploration (learn about arms) vs. Exploitation (choose best known arm)

**Regret:**
- Regret(T) = T·μ* - Σᵗ r(t)
- Where μ* = expected reward of optimal arm
- Measures opportunity cost of not always choosing best arm

**Types of Bandits:**
1. **Stochastic Bandits**: Rewards drawn from fixed distributions
2. **Adversarial Bandits**: Rewards chosen by adversary
3. **Contextual Bandits**: Rewards depend on context/state
4. **Restless Bandits**: Reward distributions change over time

### 3.5.2 Classical Bandit Algorithms

**ε-Greedy:**
```
With probability ε: explore (random arm)
With probability 1-ε: exploit (best arm so far)
```
- Simple, easy to implement
- Regret: O(T^(2/3)) with optimal ε decay
- Problem: Wastes exploration on clearly suboptimal arms

**Upper Confidence Bound (UCB):**
```
Select arm: argmax_a [μ̂_a + √(2ln(t)/n_a)]
```
- μ̂_a = empirical mean reward of arm a
- n_a = number of times arm a selected
- Confidence bound decreases with more samples
- Regret: O(√(T ln K)) (optimal for stochastic bandits)

**UCB1 Algorithm (Auer et al., 2002):**
- Provably optimal regret bound
- No tuning parameters required
- Assumes bounded rewards [0,1]

**UCB Variants:**
- **UCB-V**: Uses variance estimates
- **KL-UCB**: Uses KL divergence for tighter bounds
- **Bayes-UCB**: Bayesian version with posterior sampling

### 3.5.3 Thompson Sampling (Bayesian Approach)

**Algorithm:**
```
1. Maintain posterior distribution P(θ_a | data) for each arm a
2. At time t:
   a. Sample θ̃_a ~ P(θ_a | data) for each arm
   b. Select arm a* = argmax_a θ̃_a
   c. Observe reward r
   d. Update posterior P(θ_a* | data, r)
```

**For Bernoulli Rewards:**
- Prior: Beta(α, β) distribution
- Posterior update: Beta(α + successes, β + failures)
- Conjugate prior → closed-form updates

**For Gaussian Rewards:**
- Prior: Normal-Gamma distribution
- Posterior: Normal-Gamma with updated parameters
- Conjugate prior → closed-form updates

**Advantages:**
- Naturally balances exploration-exploitation
- Incorporates prior knowledge
- Empirically strong performance
- Regret: O(√(T ln K)) (matches UCB)

**Theoretical Results:**
- Agrawal & Goyal (2012): Regret bounds for Thompson Sampling
- Kaufmann et al. (2012): Bayesian optimality properties
- Russo & Van Roy (2014): Information-theoretic analysis

### 3.5.4 Contextual Bandits

**Problem Extension:**
- At time t, observe context x(t) ∈ ℝ^d
- Select arm a(t), receive reward r(t)
- Reward depends on both context and arm: r ~ P(r | x, a)

**LinUCB Algorithm (Li et al., 2010):**
- Assumes linear reward model: E[r | x, a] = x^T θ_a
- Maintains confidence ellipsoid for each θ_a
- Used in news article recommendation (Yahoo!)

**Neural Contextual Bandits:**
- Use neural networks to model reward function
- Example: Riquelme et al. (2018) - Deep Bayesian Bandits

**Applications:**
- Online advertising (display which ad?)
- Recommendation systems (which item to recommend?)
- Clinical trials (which treatment to assign?)

### 3.5.5 Reinforcement Learning Foundations

**Markov Decision Process (MDP):**
- States: S
- Actions: A
- Transition: P(s' | s, a)
- Reward: R(s, a)
- Policy: π(a | s)
- Goal: Maximize expected cumulative reward

**Value Functions:**
- State value: V^π(s) = E_π[Σᵗ γᵗ r(t) | s₀=s]
- Action value: Q^π(s,a) = E_π[Σᵗ γᵗ r(t) | s₀=s, a₀=a]
- Optimal value: V*(s) = max_π V^π(s)

**Bellman Equations:**
- V^π(s) = Σ_a π(a|s) Σ_s' P(s'|s,a)[R(s,a) + γV^π(s')]
- Q^π(s,a) = Σ_s' P(s'|s,a)[R(s,a) + γΣ_a' π(a'|s')Q^π(s',a')]

**Dynamic Programming:**
- Policy Iteration: Evaluate policy → Improve policy → Repeat
- Value Iteration: V(s) ← max_a Σ_s' P(s'|s,a)[R(s,a) + γV(s')]

### 3.5.6 Model-Free RL Algorithms

**Q-Learning (Watkins, 1989):**
```
Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]
```
- Off-policy: Learns optimal Q regardless of behavior policy
- Convergence: Guaranteed under certain conditions
- Problem: Requires discrete state/action spaces

**SARSA (State-Action-Reward-State-Action):**
```
Q(s,a) ← Q(s,a) + α[r + γQ(s',a') - Q(s,a)]
```
- On-policy: Learns Q for current policy
- More conservative than Q-Learning

**Deep Q-Networks (DQN):**
- Use neural network to approximate Q(s,a)
- Experience replay: Store transitions, sample mini-batches
- Target network: Stabilize training
- Example: Mnih et al. (2015) - Atari games

**Policy Gradient Methods:**
- Directly optimize policy π_θ(a|s)
- REINFORCE: ∇_θ J(θ) = E[∇_θ log π_θ(a|s) Q^π(s,a)]
- Actor-Critic: Combine policy gradient with value function
- PPO (Proximal Policy Optimization): State-of-the-art for continuous control

### 3.5.7 Applications in Agriculture

**Irrigation Control:**
- State: Soil moisture, weather forecast
- Action: Irrigation amount
- Reward: Yield - water cost
- Example: Gu et al. (2020) - Deep RL for irrigation scheduling

**Fertilizer Management:**
- State: Crop growth stage, soil nutrients
- Action: Fertilizer type and amount
- Reward: Yield - fertilizer cost - environmental penalty
- Example: Chlingaryan et al. (2018) - RL for precision agriculture

**Pest Management:**
- State: Pest population, crop stage
- Action: Pesticide application decision
- Reward: Yield - pesticide cost - health penalty

**Harvest Timing:**
- State: Crop maturity, market price, weather
- Action: Harvest now or wait
- Reward: Revenue - costs
- Limited prior work (gap addressed by FarmMe)

**Challenges:**
- Long time horizons (months between actions)
- Sparse rewards (only at harvest)
- High-dimensional state spaces
- Limited training data (one season per year)
- Safety constraints (cannot experiment freely)

## 3.6 Data Leakage in Machine Learning

### 3.6.1 Definition and Types

**Data Leakage:**
Information from outside the training dataset is used to create the model, leading to overly optimistic performance estimates that do not generalize to new data.

**Types of Leakage:**

1. **Temporal Leakage**
   - Using future information to predict the past
   - Example: Using next month's price to predict this month's demand
   - Common in time series problems

2. **Target Leakage**
   - Features derived from or highly correlated with target
   - Example: Using "approved" flag to predict loan default
   - Often subtle and hard to detect

3. **Train-Test Contamination**
   - Information from test set influences training
   - Example: Fitting scaler on entire dataset before split
   - Violates independence assumption

4. **Duplicate Data**
   - Same samples in train and test sets
   - Example: Multiple records for same entity
   - Inflates performance metrics

### 3.6.2 Temporal Leakage in Detail

**Common Causes:**

1. **Improper Feature Engineering**
```python
# ❌ WRONG: Using future values
df['next_price'] = df['price'].shift(-1)

# ✅ CORRECT: Using past values only
df['prev_price'] = df['price'].shift(1)
```

2. **Rolling Windows Without Shifting**
```python
# ❌ WRONG: Includes current value
df['rolling_mean'] = df['price'].rolling(7).mean()

# ✅ CORRECT: Excludes current value
df['rolling_mean'] = df['price'].rolling(7).mean().shift(1)
```

3. **Improper Train-Test Split**
```python
# ❌ WRONG: Random split for time series
train, test = train_test_split(df, test_size=0.2)

# ✅ CORRECT: Temporal split
split_date = '2024-01-01'
train = df[df['date'] < split_date]
test = df[df['date'] >= split_date]
```

### 3.6.3 Detection Methods

**Statistical Tests:**

1. **Performance Too Good to Be True**
   - R² > 0.99 for noisy data → likely leakage
   - Perfect accuracy on complex problem → investigate

2. **Feature Importance Analysis**
   - Features with suspiciously high importance
   - Features that shouldn't be predictive

3. **Temporal Consistency Check**
   - Train on period A, test on period B
   - If performance drops dramatically → possible leakage

4. **Correlation Analysis**
   - Check correlations between features and target
   - |correlation| > 0.95 → investigate

**Automated Detection:**
```python
def detect_leakage(X_train, y_train, X_test, y_test):
    """
    Automated leakage detection
    """
    # 1. Check for perfect predictions
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    if train_score > 0.99:
        print("⚠️ WARNING: Perfect training score - possible leakage")
    
    # 2. Check train-test score gap
    if train_score - test_score > 0.3:
        print("⚠️ WARNING: Large train-test gap - possible overfitting or leakage")
    
    # 3. Check feature correlations
    for col in X_train.columns:
        corr = np.corrcoef(X_train[col], y_train)[0,1]
        if abs(corr) > 0.95:
            print(f"⚠️ WARNING: {col} has correlation {corr:.3f} with target")
```

### 3.6.4 Prevention Strategies

**Best Practices:**

1. **Temporal Ordering**
   - Always split data chronologically for time series
   - Never use future information in features
   - Use walk-forward validation

2. **Feature Engineering Discipline**
   - Document when each feature becomes available
   - Use only information available at prediction time
   - Shift all rolling statistics by at least 1 period

3. **Cross-Validation Strategy**
   - Use TimeSeriesSplit for temporal data
   - Ensure test fold is always after train fold
   - Never shuffle time series data

4. **Pipeline Isolation**
   - Fit all transformations on training data only
   - Apply fitted transformations to test data
   - Use sklearn Pipeline to enforce this

**Example: Safe Pipeline**
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),  # Fitted on train only
    ('model', RandomForestRegressor())
])

# Fit on training data
pipeline.fit(X_train, y_train)

# Transform and predict on test data
# Scaler uses training statistics, not test statistics
y_pred = pipeline.predict(X_test)
```

### 3.6.5 Leakage in Agricultural ML

**Common Scenarios:**

1. **Yield Prediction**
   - ❌ Using actual harvest date to predict yield
   - ❌ Using post-harvest weather data
   - ✅ Using only pre-planting and in-season data

2. **Price Forecasting**
   - ❌ Using same-day prices from other markets
   - ❌ Using future economic indicators
   - ✅ Using lagged prices and forecasted indicators

3. **Crop Recommendation**
   - ❌ Using actual yields from current season
   - ❌ Using future weather data
   - ✅ Using historical yields and weather forecasts

**Case Study: Kaggle Competition Failures**
- Many winning solutions later found to have leakage
- Example: Santander Customer Satisfaction (2016)
  - Winning solution used leaked target information
  - Model failed in production
- Lesson: Rigorous validation is essential

### 3.6.6 Honest Evaluation Framework

**Principles:**

1. **Realistic Feature Availability**
   - Document when each feature becomes available
   - Only use features available at prediction time
   - Simulate production environment

2. **Proper Temporal Validation**
   - Use expanding window or sliding window
   - Respect temporal ordering strictly
   - Test on truly unseen future data

3. **Conservative Performance Reporting**
   - Report test set performance, not training
   - Use multiple evaluation metrics
   - Include confidence intervals

4. **Reproducibility**
   - Fix random seeds
   - Document all preprocessing steps
   - Share code and data (when possible)

**Validation Strategy for Time Series:**
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)

for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    # Fit transformations on train only
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)  # Use train statistics
    
    # Train model
    model.fit(X_train_scaled, y_train)
    
    # Evaluate on test
    score = model.score(X_test_scaled, y_test)
```

## 3.7 Related Systems and Platforms

### 3.7.1 Commercial Agricultural Decision Support Systems

**Climate FieldView (Bayer/Monsanto):**
- Satellite imagery and field mapping
- Yield analysis and benchmarking
- Planting and harvest recommendations
- Limitations: Focused on large-scale farms, US-centric

**John Deere Operations Center:**
- Equipment telemetry and field operations
- Prescription maps for variable rate application
- Integration with John Deere machinery
- Limitations: Requires John Deere equipment, expensive

**Farmers Edge:**
- Weather monitoring and forecasting
- Crop modeling and yield prediction
- Variable rate prescriptions
- Limitations: Subscription-based, limited crop coverage

**Cropio:**
- Satellite-based field monitoring
- Weather data integration
- Scouting and task management
- Limitations: Focused on monitoring, limited decision support

### 3.7.2 Research Prototypes

**DSSAT (Decision Support System for Agrotechnology Transfer):**
- Crop simulation models (CERES, CROPGRO)
- Climate change impact assessment
- Extensive calibration required
- Limitations: Complex, requires expert knowledge

**APSIM (Agricultural Production Systems sIMulator):**
- Modular crop and soil models
- Long-term sustainability analysis
- Widely used in research
- Limitations: Not user-friendly for farmers

**CropSyst:**
- Cropping systems simulation
- Water and nitrogen management
- Climate scenario analysis
- Limitations: Windows-only, limited crop models

### 3.7.3 ML-Based Agricultural Platforms

**Microsoft FarmBeats:**
- IoT sensor integration
- AI-powered insights
- Drone and satellite imagery
- Limitations: Requires infrastructure investment

**IBM Watson Decision Platform for Agriculture:**
- Weather forecasting
- Crop modeling
- Prescriptive analytics
- Limitations: Enterprise-focused, expensive

**Plantix (PEAT):**
- Image-based disease detection
- Crop health monitoring
- Community knowledge sharing
- Limitations: Focused on diagnostics, not planning

### 3.7.4 Comparison with FarmMe

**FarmMe Unique Contributions:**

1. **End-to-End Decision Support**
   - Covers entire crop lifecycle (planning → planting → harvest)
   - Integrated multi-model pipeline
   - Most systems focus on single aspect

2. **Multi-Objective Optimization**
   - Balances profit, risk, and sustainability
   - Pareto-optimal recommendations
   - Most systems optimize single objective

3. **Data Leakage Prevention**
   - Rigorous temporal validation
   - Documented feature availability
   - Most research papers have leakage issues

4. **Accessibility**
   - Designed for smallholder farmers
   - Low infrastructure requirements
   - Most commercial systems target large farms

5. **Thailand-Specific**
   - 77 provinces, 46 crops
   - Thai agricultural calendar
   - Most systems are US/Europe-centric

**Limitations Compared to Commercial Systems:**
- Synthetic data (not real-world validated)
- Limited sensor integration
- No satellite imagery
- Proof-of-concept stage

## 3.8 Research Gaps and Opportunities

### 3.8.1 Identified Gaps

**1. Multi-Objective Crop Recommendation**
- Existing systems optimize single objective
- Limited handling of farmer constraints
- No Pareto-optimal solution generation
- **FarmMe addresses**: NSGA-II with XGBoost fitness evaluation

**2. Temporal Bias in Price Forecasting**
- High dependence on recent prices (>95%)
- Vulnerable to market shocks
- Limited external factor integration
- **FarmMe addresses**: Weather + economic data integration, bias quantification

**3. Harvest Timing Under Uncertainty**
- Limited ML applications
- Most work on perennial crops
- No practical implementations for annual crops
- **FarmMe addresses**: Thompson Sampling for sequential decisions

**4. Data Leakage in Agricultural ML**
- Widespread but rarely acknowledged
- No standard detection/prevention frameworks
- Inflated performance claims
- **FarmMe addresses**: Comprehensive leakage prevention framework

**5. End-to-End Integration**
- Most systems focus on single decision
- Limited model integration
- No holistic decision support
- **FarmMe addresses**: Four-model integrated pipeline

### 3.8.2 Future Research Directions

**1. Real-World Validation**
- Field trials with actual farmers
- A/B testing of recommendations
- Long-term impact assessment

**2. Causal Inference**
- Move beyond correlation to causation
- Counterfactual reasoning
- Treatment effect estimation

**3. Explainable AI**
- Interpretable model architectures
- Feature importance visualization
- Counterfactual explanations

**4. Transfer Learning**
- Adapt models across regions
- Few-shot learning for new crops
- Domain adaptation techniques

**5. Multi-Agent Systems**
- Coordinate decisions across farmers
- Market equilibrium considerations
- Cooperative optimization

**6. Climate Change Adaptation**
- Long-term climate scenarios
- Adaptive decision-making
- Resilience optimization

## 3.9 Summary

This chapter has reviewed the theoretical foundations and related work across five key areas:

1. **Machine Learning in Agriculture**: Established the evolution from expert systems to deep learning, identified limitations in existing crop recommendation, planting window, price forecasting, and harvest timing systems.

2. **Multi-Objective Optimization**: Reviewed MOEA algorithms, particularly NSGA-II, and their applications in agriculture. Identified gap in ML-MOEA hybrids for crop recommendation.

3. **Time Series Forecasting**: Covered classical methods (ARIMA, exponential smoothing) and modern ML approaches (XGBoost, LSTM). Highlighted temporal bias issues in agricultural price forecasting.

4. **Multi-Armed Bandits**: Reviewed bandit algorithms (UCB, Thompson Sampling) and their theoretical properties. Identified limited application to agricultural harvest timing.

5. **Data Leakage**: Defined types of leakage, detection methods, and prevention strategies. Emphasized importance of honest evaluation in agricultural ML.

**Key Takeaways:**
- Agricultural ML has made significant progress but faces persistent challenges
- Data leakage is widespread and undermines research credibility
- Multi-objective optimization is underutilized in agricultural decision support
- Sequential decision-making (bandits, RL) has limited agricultural applications
- Integration of multiple models into end-to-end systems is rare

**FarmMe's Contributions:**
The FarmMe system addresses these gaps through:
- Multi-objective crop recommendation with NSGA-II
- Temporal bias reduction in price forecasting
- Thompson Sampling for harvest timing
- Comprehensive data leakage prevention
- End-to-end integrated pipeline

The following chapters detail the implementation and evaluation of these contributions.

---

*This chapter has established the theoretical foundations and identified research gaps that motivate the FarmMe system. The next chapters will detail the implementation of each model component, demonstrating how these gaps are addressed.*

