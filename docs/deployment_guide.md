# Retail Demand Forecasting & Inventory Optimization

## Deployment Guide

### 1. Prerequisites

Before deploying the application, ensure the following tools are installed:

- Python 3.10 or higher
- Git
- Google Cloud SDK
- Docker and Docker Compose
- Access to the configured BigQuery project

---

## 2. Clone the Repository

bash
git clone <repository-url>
cd Retail-Demand-Forecasting-Inventory-Optimization


---

3. Create Virtual Environment

python -m venv venv

Windows

venv\Scripts\activate

Linux/macOS

source venv/bin/activate


---

4. Install Dependencies

pip install -r requirements.txt


---

5. Configure Environment Variables

Create a .env file in the project root.

GCP_PROJECT_ID=your-gcp-project-id
BIGQUERY_DATASET=retail_demand
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

FORECAST_TABLE=forecast_results
SALES_TABLE=clean_sales
INVENTORY_TABLE=inventory_recommendations

Never commit the .env file or service account credentials to Git.


---

6. Configure Google Cloud Authentication

Authenticate using Google Cloud SDK:

gcloud auth application-default login

Verify the active project:

gcloud config get-value project

Set the project if required:

gcloud config set project YOUR_PROJECT_ID


---

7. Run Data Pipeline

Execute the complete pipeline:

python main.py

The pipeline should perform:

1. Load raw data.


2. Validate the dataset.


3. Clean and transform data.


4. Load data into BigQuery.


5. Execute forecasting pipeline.


6. Store forecast results.


7. Generate inventory recommendations.




---

8. Run Tests

Execute all project tests:

pytest -v

Run dashboard tests:

pytest tests/dashboard -v


---

9. Run Streamlit Dashboard

streamlit run dashboard/app.py

The application will normally be available at:

http://localhost:8501


---

10. Docker Deployment

Build and start the application:

docker-compose up --build

Run in detached mode:

docker-compose up -d --build

Stop containers:

docker-compose down


---

11. Production Checklist

Before production deployment, verify:

All tests pass.

Environment variables are configured.

Secrets are not committed to Git.

BigQuery permissions are restricted.

Service accounts follow least-privilege access.

Forecast tables are available.

Dashboard loads successfully.

Scenario analysis works correctly.

Inventory recommendations are validated.



---

12. Recommended Production Flow

Raw M5 Dataset
        |
        v
Data Extraction
        |
        v
Data Quality Validation
        |
        v
BigQuery Data Warehouse
        |
        v
dbt Transformations
        |
        v
Forecasting Models
        |
        v
Forecast Results
        |
        v
Inventory Optimization
        |
        v
Streamlit Dashboard
