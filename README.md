# Retail-Demand-Forecasting-Inventory-Optimization
An automated analytics platform for retail and supply chain teams that predicts future product demand and generates inventory recommendations.

---

# Project Objective

The system helps retail organizations:

- Predict future product demand.
- Identify high-demand products.
- Reduce stockout risk.
- Reduce overstocking.
- Improve inventory planning.
- Support proactive procurement decisions.

---

# Dataset

The project uses the M5 Forecasting Dataset.

The dataset contains:

- Historical sales.
- Product hierarchy.
- Departments.
- Product categories.
- Store information.
- Calendar events.
- Product prices.

---

# Technology Stack

| Category | Technology |
|---|---|
| Programming | Python, SQL |
| Data Warehouse | Google BigQuery |
| Transformation | dbt |
| Forecasting | Prophet, LightGBM, ARIMA |
| Dashboard | Streamlit |
| Testing | pytest |
| CI/CD | GitHub Actions |

---

# Project Architecture

text
Retail Demand Forecasting
│
├── data/
│
├── src/
│   ├── extraction/
│   ├── validation/
│   ├── transformation/
│   ├── warehouse/
│   ├── features/
│   ├── forecasting/
│   ├── inventory/
│   ├── dashboard/
│   └── config/
│
├── dashboard/
│   ├── app.py
│   └── pages/
│
├── tests/
│
├── docs/
│
├── dbt_project/
│
├── main.py
├── requirements.txt
└── README.md


---

Installation

Clone the repository:

git clone <repository-url>

Move into the project directory:

cd Retail-Demand-Forecasting-Inventory-Optimization

Create a virtual environment:

python -m venv venv

Activate the environment.

Windows

venv\Scripts\activate

Linux/macOS

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt


---

## Configuration

Create a `.env` file in the project root:

GCP_PROJECT_ID=your-google-cloud-project-id
GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id

GOOGLE_APPLICATION_CREDENTIALS=C:/path/to/service-account-key.json

BIGQUERY_LOCATION=US

MARTS_DATASET=retail_demand
BIGQUERY_MART_DATASET=retail_demand

FORECAST_DATASET=retail_demand_forecasting
BIGQUERY_FORECAST_DATASET=retail_demand_forecasting

DAILY_SALES_TABLE=daily_sales
FORECAST_TABLE=forecast_results
METRICS_TABLE=forecast_metrics
MODEL_RUNS_TABLE=model_runs

Never commit the `.env` file or service account credentials to Git.


---

Running the Pipeline

Execute:

python main.py

The pipeline performs:

Extract Data
    ↓
Validate Data
    ↓
Clean Data
    ↓
Load Warehouse
    ↓
Transform Data
    ↓
Generate Forecasts
    ↓
Optimize Inventory


---

Running the Dashboard

Execute:

streamlit run dashboard/app.py


---

Dashboard Features

The dashboard provides:

Store selection.

Product selection.

Historical demand analysis.

Demand forecasts.

Inventory recommendations.

Price change scenarios.

Promotion scenarios.

Stockout risk analysis.

Scenario report downloads.



---

What-if Scenarios

Users can simulate:

Price Changes

Example:

10% Price Reduction
        ↓
Price Elasticity Applied
        ↓
Demand Impact Calculated
        ↓
Revenue Impact Calculated
        ↓
Inventory Impact Calculated

Promotions

Example:

Promotion Demand Lift
        ↓
Scenario Demand Calculation
        ↓
Additional Inventory Requirement
        ↓
Stockout Risk Evaluation


---

Testing

Run all tests:

pytest -v

Run dashboard tests:

pytest tests/dashboard -v


---

Git Workflow

Each team member must commit code daily.

Example:

git add .
git commit -m "feat: complete daily assigned task"
git push origin <branch-name>

Before merging:

git pull origin main
pytest -v


---

Security

Never commit:

.env

Service account credentials.

API keys.

Passwords.

Private configuration files.


Use environment variables for sensitive configuration.


---

Project Timeline

Week 1

Data Architecture and ETL.

Week 2

Data Transformation using dbt.

Week 3

Time-Series Forecasting.

Week 4

Interactive Dashboard and Reporting.


---

Expected Business Impact

The platform aims to:

Reduce revenue loss caused by stockouts.

Reduce warehousing costs caused by overstocking.

Improve demand forecasting accuracy.

Improve supply chain efficiency.

Enable proactive inventory planning.