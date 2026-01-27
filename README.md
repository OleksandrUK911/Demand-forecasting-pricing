# 🎯 Прогнозування попиту + Ціноутворення з урахуванням ризиків

**Проєкт:** Namecheap R&D прототип для прогнозування попиту на домени та динамічного ціноутворення

Система машинного навчання для оптимізації ціноутворення на доменні імена з урахуванням невизначеності попиту та ринкових ризиків.

## 📊 Ключові результати

**Model Performance:**
- ✅ **27.8% покращення MAE** порівняно з Baseline (196 vs 271)
- ✅ RMSE: 313 (vs 424 baseline)
- ✅ Prediction intervals (P10/P90) покривають ~80% actual demand

**Business Impact:**
- 💰 **+5.9% revenue** з Risk-Aware Policy vs Fixed Price
- 📉 **-20% волатильність** (CV) vs Naive Dynamic pricing
- 🛡️ Краще downside protection (вищий P10 revenue)

**Dataset:** 65k записів, 365 днів, 5 TLDs, 4 регіони (synthetic data for POC)

## 🚀 Швидкий старт

**Головний файл:**  
→ **[demand_forecasting_pricing.ipynb](demand_forecasting_pricing.ipynb)** — повний ML pipeline (36 cells, детальні пояснення українською)

**Інтерактивне demo:**  
→ **Streamlit App** (4 вкладки: Overview, Pricing Analysis, Revenue Curves, Results)

## 💡 Ключові ідеї

**1. Quantile Regression для Uncertainty Estimation**
- Прогнозуємо не тільки median (P50), але й P10/P90
- Ц🛠️ Встановлення та запуск

### Локально (Jupyter Notebook)
```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/domain-pricing-forecasting.git
cd domain-pricing-forecasting

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run notebook
jupyter notebook demand_forecasting_pricing.ipynb
```

### Streamlit Demo
```bash
# Запустити інтерактивний dashboard
streamlit run app.py

# Відкрити браузер: http://localhost:8501
```

### Google Colab
```python
# 1. Upload demand_forecasting_pricing.ipynb to Colab
# 2. Runtime → Run all (Ctrl+F9)
# 3. Всі залежності встановляться автоматично
```

**Deployment на Streamlit Cloud:** Див. [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📁 Структура проєкту

```
.
├── demand_forecasting_pricing.ipynb  # Головний ML pipeline (36 cells)
├── app.py                            # Streamlit dashboard (246 lines)
├── requirements.txt                  # Python dependencies
├── README.md                         # Цей файл
├── DEPLOYMENT.md                     # Інструкції для deployment
├── .streamlit/config.toml            # Streamlit налаштування
├── .gitignore                        # Git exclusions
└── docs/
    ├── ARCHITECTURE.md               # Production system design
    └── QUICKSTART.md                 # Швидкий старт гайд
```

---

## 🔬 Технічні деталі

**ML Models:**
- Gradient Boosting Regressor (quantile loss)
- 100 trees, depth=5, learning_rate=0.1
- Separate models for P10/P50/P90

**Features:**
- Time features: day_of_week, month, quarter, is_weekend
- Lag features: [1, 7, 14] days
- Rolling stats: mean/std over [7, 28] days windows
- Categorical: TLD, region, user_type, device (one-hot encoded)
- Price features: actual_price, promo flag

**Evaluation Metrics:**
- MAE (Mean Absolute Error): primary metric
- RMSE (Root Mean Squared Error)
- MAPE (Mean Absolute Percentage Error)
- SMAPE (Symmetric MAPE)

**Business KPIs:**
- Total Revenue
- Revenue Volatility (CV = StdDev / Mean)
- Downside Risk (P50 - P10 revenue)
- Uplift vs Fixed Price baseline

---

## ⚠️ Обмеження та Disclaimer

**КРИТИЧНО ВАЖЛИВІ ОБМЕЖЕННЯ:**

1. **Synthetic Data**  
   Всі результати базуються на згенерованих даних. Потрібна валідація на Namecheap production data (мінімум 6 місяців історії).

2. **Price Elasticity Assumed**  
   Параметри elasticity (.com: 1.2, .ai: 1.8) не калібровані на реальних даних. Потрібні A/B тести для точної оцінки.

3. **No External Factors**  
   Модель не враховує: competitor prices, marketing campaigns, economic indicators, seasonal events (Black Friday).

4. **Simplified Architecture**  
   Production система буде складнішою: real-time data ingestion, distributed training, canary deployments.

---

## 📈 Next Steps

**Phase 1: Validation (2-4 тижні)**
- [ ] Інтеграція з Namecheap historical data
- [ ] Feature engineering на real data
- [ ] Model retraining та hyperparameter tuning
- [ ] Backtest на actual transactions

**Phase 2: A/B Testing (4-6 тижнів)**
- [ ] Deploy Risk-Aware Policy на 10% traffic
- [ ] Monitor metrics щоденно (revenue, conversion, churn)
- [ ] Statistical significance testing (p-value < 0.05)
- [ ] Segment analysis (TLD/region breakdown)

**Phase 3: Enhancement (ongoing)**
- [ ] Multi-horizon forecasting (1d/7d/30d)
- [ ] Competitor price tracking integration
- [ ] Reinforcement Learning для adaptive pricing
- [ ] Customer lifetime value (CLV) optimization
- [ ] External signals (Google Trends, crypto prices for .io)

---

## 📚 Документація

- **[DEPLOYMENT.md](DEPLOYMENT.md)** — як задеплоїти на Streamlit Cloud / Heroku / AWS
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — детальна production архітектура
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** — step-by-step гайд для початківців

---

## 🤝 Contributing

Це R&D прототип для Namecheap. Якщо маєте ідеї або знайшли баги:
1. Створіть issue з описом
2. Fork → branch → commit → pull request
3. Додайте tests для нового функціоналу

---

## 📧 Контакт

**Питання / Feedback:**  
Створіть GitHub issue або напишіть мені directly. доменів
- A/B testing framework

## Як запустити

```bash
# Install
pip install -r requirements.txt

# Run notebook
jupyter notebook demand_forecasting_pricing.ipynb

# (Optional) Streamlit demo
streamlit run app.py
```

Детальніші інструкції: [docs/QUICKSTART.md](docs/QUICKSTART.md)

## Обмеження та Next Steps

**Обмеження:**
- Synthetic data (потрібна валідація на реальних даних Namecheap)
- Price elasticity assumed (потрібна калібрація через A/B тести)

**Next Steps:**
- Валідація на production data
- Multi-horizon forecasting (1, 7, 30 днів)
- Competitor price tracking
- A/B testing framework

Детальна архітектура: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

**Tech Stack:** Python, scikit-learn, pandas, matplotlib, Streamlit  
**Автор:** Oleksandr Skakun ML Engineer + Product Quant  
**Дата:** 27 січня 2026
