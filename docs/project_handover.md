# Project Handover Document

# Retail Demand Forecasting & Inventory Optimization

## 1. Project Overview

This project is an automated analytics and forecasting platform designed for retail and supply chain teams.

The system uses historical sales data, calendar events, product prices, and hierarchical product information to predict future demand and generate inventory recommendations.

---

## 2. Technology Stack

### Programming

- Python
- SQL

### Data Warehouse

- Google BigQuery

### Data Transformation

- dbt

### Forecasting

- Facebook Prophet
- LightGBM
- ARIMA

### Dashboard

- Streamlit

### Testing

- pytest

### CI/CD

- GitHub Actions

---

## 3. Main Project Components

```text
Retail Demand Forecasting System
│
├── Data Extraction
├── Data Validation
├── Data Cleaning
├── BigQuery Warehouse
├── dbt Transformations
├── Feature Engineering
├── Forecasting Models
├── Forecast Storage
├── Inventory Optimization
├── Streamlit Dashboard
└── What-if Scenario Analysis

## 4. Data Flow

```text
M5 Dataset
    |
    v
Extraction Scripts
    |
    v
Raw Data Tables
    |
    v
Data Quality Checks
    |
    v
Clean Data Tables
    |
    v
dbt Models
    |
    v
Analytics Data Marts
    |
    v
Forecasting Pipeline
    |
    v
Forecast Results
    |
    v
Inventory Optimization
    |
    v
Streamlit Dashboard
```

---

## 5. Main Execution

The complete pipeline is executed using:

```bash
python main.py
```

The main pipeline coordinates:

1. Data extraction.
2. Data validation.
3. Data cleaning.
4. Warehouse loading.
5. Feature preparation.
6. Forecast generation.
7. Forecast storage.
8. Inventory recommendation generation.

---

## 6. Dashboard Execution

Run the dashboard using:

```bash
streamlit run dashboard/app.py
```

The dashboard provides:

* Store-level analysis.
* Product-level analysis.
* Demand forecasts.
* Historical sales visualization.
* Inventory recommendations.
* Price change scenarios.
* Promotion scenarios.
* Scenario inventory impact.

---

## 7. Testing

Run all tests:

```bash
pytest -v
```

Run dashboard tests:

```bash
pytest tests/dashboard -v
```

All tests should pass before merging code into the `main` branch.

---

## 8. Git Workflow

Each team member should:

1. Pull the latest changes.
2. Create or update their feature branch.
3. Make changes.
4. Run tests.
5. Commit changes.
6. Push the branch.
7. Create a Pull Request.
8. Request code review.
9. Merge only after approval.

Example:

```bash
git checkout main
git pull origin main

git checkout -b feature/member-task

git add .
git commit -m "feat: complete assigned task"

git push origin feature/member-task
```

---

## 9. Important Security Rules

* Never commit `.env`.
* Never commit service account JSON files.
* Do not hardcode passwords.
* Do not expose BigQuery credentials.
* Use environment variables for configuration.
* Apply least-privilege access to service accounts.

---

## 10. Future Improvements

Possible future enhancements include:

* Automated model retraining.
* Real-time inventory updates.
* Advanced demand anomaly detection.
* Supplier lead-time integration.
* Automated reorder notifications.
* Cloud deployment.
* Role-based dashboard access.
* Forecast accuracy monitoring.
