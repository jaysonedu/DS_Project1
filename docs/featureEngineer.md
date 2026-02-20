# Feature Engineering Rationale and Modeling Benefits

The objective of feature engineering in this project is to transform raw housing and neighborhood data into structured, economically meaningful signals that improve model performance, interpretability, and robustness. Rather than relying solely on original values, we construct features that better capture structural differences, temporal dynamics, and seasonal patterns in housing markets.

---

## Structural Features: Rates and Proportions

Raw counts such as crime incidents or education levels are strongly influenced by population size. Larger ZIP codes naturally generate larger counts, even if the underlying rates are similar. Using raw counts would therefore introduce scale-driven bias into the model.

To address this issue, we construct intensity and proportional measures:

- **Crime per 1,000 residents** to represent crime intensity rather than volume.
- **Education shares** to represent the proportion of residents holding specific degrees.
- **Graduate-level share** to summarize advanced educational attainment.

These transformations ensure comparability across ZIP codes and allow the model to learn relationships driven by structural differences rather than population scale.

---

## Income Transformation

Median income distributions are typically right-skewed. Extremely high-income areas can disproportionately influence model estimation, particularly in linear regression settings.

To mitigate this, we apply a **log transformation to median income**. This reduces skewness, stabilizes variance, and often improves model stability and interpretability. In many economic contexts, log-transformed income variables also align better with elasticity-based interpretations.

---

## Temporal Dynamics: Lag and Trend Features

Housing markets exhibit strong temporal dependence. Current prices are influenced by past prices, and neighborhood conditions evolve gradually over time.

To capture these dynamics, we generate:

- **Lag features** (e.g., 1-, 3-, 6-, and 12-month lags) to represent persistence and momentum.
- **Month-over-month and year-over-year percentage changes** to capture short-term and long-term growth trends.
- **Rolling means** to smooth short-term fluctuations and summarize recent conditions.
- **Rolling standard deviations** to measure volatility and stability.

Lag features allow the model to learn autoregressive behavior, while rolling statistics reduce noise and improve generalization. Volatility features provide information about market stability, which may influence housing demand and pricing dynamics.

All rolling statistics are computed using past information only, reducing the risk of data leakage.

---

## Seasonality Encoding

Housing activity often follows seasonal cycles. However, months are cyclical rather than linear variables: December and January are adjacent in time, despite being numerically far apart.

To preserve cyclical structure, we encode month-of-year using **sine and cosine transformations**. This allows the model to capture seasonal effects without introducing artificial discontinuities in the feature space.

---

## Overall Impact on Model Construction

Collectively, the engineered features expand the feature space from raw observations to structured signals that reflect:

- Structural neighborhood characteristics (rates and shares)
- Temporal persistence and momentum (lags)
- Trend dynamics (percentage changes)
- Stability and risk (volatility measures)
- Seasonal patterns (cyclical encoding)

By incorporating these transformations, the model gains the ability to learn economically meaningful relationships rather than surface-level correlations. This typically improves predictive accuracy, interpretability, and robustness across time and space.
