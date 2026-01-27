"""
Streamlit demo: Demand Forecasting + Risk-Aware Pricing

Компактна версія для швидкої демонстрації системи.
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict

# Page config
st.set_page_config(
    page_title="Demand Forecasting + Pricing",
    page_icon="📊",
    layout="wide"
)

# ==================== FUNCTIONS ====================

def generate_forecast(segment: Dict, promo: bool) -> Dict:
    """Генерує sample прогноз для демонстрації."""
    np.random.seed(42)
    
    base_forecast = 1000 * (1.3 if promo else 1.0)
    
    # Segment multipliers
    multipliers = {
        'region': {'NA': 1.2, 'EU': 1.0, 'APAC': 1.1, 'LATAM': 0.7},
        'user_type': {'new': 0.8, 'returning': 1.0, 'vip': 1.5},
        'device': {'desktop': 1.2, 'mobile': 1.0, 'tablet': 0.8}
    }
    
    forecast = base_forecast
    forecast *= multipliers['region'][segment['region']]
    forecast *= multipliers['user_type'][segment['user_type']]
    forecast *= multipliers['device'][segment['device']]
    
    std = forecast * 0.15
    return {
        'p10': max(0, forecast - 1.28 * std),
        'p50': forecast,
        'p90': forecast + 1.28 * std
    }


def demand_at_price(forecast: float, price: float, base_price: float, elasticity: float) -> float:
    """Price elasticity model."""
    return forecast * np.exp(-elasticity * (price / base_price - 1.0))


def revenue_at_price(forecast: float, price: float, base_price: float, elasticity: float) -> float:
    """Revenue = price × demand."""
    return price * demand_at_price(forecast, price, base_price, elasticity)


def optimize_price_naive(forecast_p50: float, base_price: float, elasticity: float, constraints: Dict) -> float:
    """Максимізує E[revenue]."""
    min_price = base_price * constraints['min']
    max_price = base_price * constraints['max']
    prices = np.linspace(min_price, max_price, 50)
    revenues = [revenue_at_price(forecast_p50, p, base_price, elasticity) for p in prices]
    return prices[np.argmax(revenues)]


def optimize_price_risk_aware(forecast_p10: float, forecast_p50: float, base_price: float, 
                              elasticity: float, risk_lambda: float, constraints: Dict) -> float:
    """Максимізує E[revenue] - λ × downside."""
    min_price = base_price * constraints['min']
    max_price = base_price * constraints['max']
    prices = np.linspace(min_price, max_price, 50)
    
    objectives = []
    for p in prices:
        rev_p50 = revenue_at_price(forecast_p50, p, base_price, elasticity)
        rev_p10 = revenue_at_price(forecast_p10, p, base_price, elasticity)
        objectives.append(rev_p50 - risk_lambda * (rev_p50 - rev_p10))
    
    return prices[np.argmax(objectives)]


# ==================== MAIN APP ====================

st.title("📊 Demand Forecasting + Risk-Aware Pricing")

st.markdown("**Інтерактивна демонстрація системи прогнозування та ціноутворення**")

# Sidebar
st.sidebar.header("⚙️ Параметри")

st.sidebar.subheader("Сегмент")
tld = st.sidebar.selectbox("TLD", ['.com', '.net', '.org', '.io', '.ai'])
region = st.sidebar.selectbox("Регіон", ['NA', 'EU', 'APAC', 'LATAM'])
user_type = st.sidebar.selectbox("Користувач", ['new', 'returning', 'vip'])
device = st.sidebar.selectbox("Пристрій", ['desktop', 'mobile', 'tablet'])
promo = st.sidebar.checkbox("Промо-акція", value=False)

st.sidebar.markdown("---")

st.sidebar.subheader("Pricing")
risk_lambda = st.sidebar.slider(
    "Risk Aversion (λ)", 
    min_value=0.0, max_value=2.0, value=0.5, step=0.1,
    help="0 = агресивно, 2 = консервативно"
)

price_cap = st.sidebar.slider(
    "Max Price Change (%)", 
    min_value=5, max_value=30, value=10, step=5
)

# Parameters
tld_params = {
    '.com': {'base_price': 10.0, 'elasticity': 1.2},
    '.net': {'base_price': 12.0, 'elasticity': 1.0},
    '.org': {'base_price': 9.0, 'elasticity': 0.8},
    '.io': {'base_price': 25.0, 'elasticity': 1.5},
    '.ai': {'base_price': 30.0, 'elasticity': 1.8}
}

base_price = tld_params[tld]['base_price']
elasticity = tld_params[tld]['elasticity']
constraints = {'min': 1 - price_cap/100, 'max': 1 + price_cap/100}

# Generate forecast
segment = {'region': region, 'user_type': user_type, 'device': device}
forecast = generate_forecast(segment, promo)

# ==================== SECTION 1: FORECAST ====================

st.header("📈 Прогноз попиту")

col1, col2, col3 = st.columns(3)
col1.metric("P10 (Песимістичний)", f"{forecast['p10']:.0f}")
col2.metric("P50 (Очікуваний)", f"{forecast['p50']:.0f}")
col3.metric("P90 (Оптимістичний)", f"{forecast['p90']:.0f}")

# Bar chart
fig1, ax1 = plt.subplots(figsize=(10, 3))
scenarios = ['P10', 'P50', 'P90']
values = [forecast['p10'], forecast['p50'], forecast['p90']]
colors = ['#ff7f0e', '#2ca02c', '#1f77b4']
bars = ax1.barh(scenarios, values, color=colors, alpha=0.7)
ax1.set_xlabel('Demand')
ax1.set_title('Forecast Intervals')
ax1.grid(True, alpha=0.3, axis='x')
for bar, val in zip(bars, values):
    ax1.text(val, bar.get_y() + bar.get_height()/2, f'{val:.0f}', 
             va='center', ha='left', fontweight='bold')
st.pyplot(fig1)
plt.close()

# ==================== SECTION 2: PRICING ====================

st.header("💰 Рекомендації по ціні")

# Optimize prices
price_fixed = base_price
price_naive = optimize_price_naive(forecast['p50'], base_price, elasticity, constraints)
price_risk = optimize_price_risk_aware(forecast['p10'], forecast['p50'], base_price, elasticity, risk_lambda, constraints)

# Calculate revenues
rev_fixed = revenue_at_price(forecast['p50'], price_fixed, base_price, elasticity)
rev_naive = revenue_at_price(forecast['p50'], price_naive, base_price, elasticity)
rev_risk = revenue_at_price(forecast['p50'], price_risk, base_price, elasticity)

# Downside
down_fixed = revenue_at_price(forecast['p10'], price_fixed, base_price, elasticity)
down_naive = revenue_at_price(forecast['p10'], price_naive, base_price, elasticity)
down_risk = revenue_at_price(forecast['p10'], price_risk, base_price, elasticity)

# KPI Table
kpi_df = pd.DataFrame({
    'Policy': ['Fixed Price', 'Naive Dynamic', 'Risk-Aware'],
    'Price ($)': [price_fixed, price_naive, price_risk],
    'Change (%)': [0, (price_naive/base_price-1)*100, (price_risk/base_price-1)*100],
    'Revenue (P50)': [rev_fixed, rev_naive, rev_risk],
    'Revenue (P10)': [down_fixed, down_naive, down_risk],
    'Downside Risk': [rev_fixed-down_fixed, rev_naive-down_naive, rev_risk-down_risk]
})

st.dataframe(
    kpi_df.style.format({
        'Price ($)': '{:.2f}',
        'Change (%)': '{:+.1f}',
        'Revenue (P50)': '{:.0f}',
        'Revenue (P10)': '{:.0f}',
        'Downside Risk': '{:.0f}'
    }).background_gradient(subset=['Revenue (P50)'], cmap='Greens')
      .background_gradient(subset=['Downside Risk'], cmap='Reds_r'),
    use_container_width=True
)

# Revenue curve
st.subheader("📊 Revenue vs Price")

price_range = np.linspace(base_price * constraints['min'], base_price * constraints['max'], 100)
revenues_p50 = [revenue_at_price(forecast['p50'], p, base_price, elasticity) for p in price_range]

fig2, ax2 = plt.subplots(figsize=(12, 5))
ax2.plot(price_range, revenues_p50, linewidth=2.5, label='Revenue (P50)')
ax2.scatter([price_fixed], [rev_fixed], s=120, marker='s', label='Fixed', zorder=5, edgecolors='black', linewidths=2)
ax2.scatter([price_naive], [rev_naive], s=120, marker='o', label='Naive', zorder=5, edgecolors='black', linewidths=2)
ax2.scatter([price_risk], [rev_risk], s=120, marker='^', label=f'Risk-Aware (λ={risk_lambda})', zorder=5, edgecolors='black', linewidths=2)
ax2.axvline(base_price, color='gray', linestyle=':', alpha=0.5, label='Base Price')
ax2.set_xlabel('Price ($)')
ax2.set_ylabel('Revenue ($)')
ax2.set_title('Revenue Optimization')
ax2.legend()
ax2.grid(True, alpha=0.3)
st.pyplot(fig2)
plt.close()

# ==================== EXPANDER ====================

with st.expander("ℹ️ Як це працює?"):
    st.markdown("""
    ### Quantile Regression
    
    Система генерує 3 прогнози:
    - **P10** — песимістичний сценарій (10-й перцентиль)
    - **P50** — найбільш ймовірний (медіана)
    - **P90** — оптимістичний сценарій (90-й перцентиль)
    
    ### Pricing Policies
    
    **Fixed Price:** завжди базова ціна
    
    **Naive Dynamic:** `max revenue(P50)` — максимізує очікуваний revenue
    
    **Risk-Aware:** `max [revenue(P50) - λ × downside_risk]`
    - λ = 0 → еквівалент Naive
    - λ = 1 → рівна вага revenue та downside
    - λ = 2 → дуже консервативно
    
    ### Price Elasticity
    
    `demand(price) = forecast × exp(-elasticity × (price/base_price - 1))`
    
    Вища elasticity = попит більше реагує на ціну.
    """)

st.markdown("---")
st.markdown("**Tech Stack:** Python, scikit-learn, Streamlit | **Автор:** Oleksandr Skakun ML Engineer + Product Quant")
