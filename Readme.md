# 🧠 AI-Powered Test Execution Insights Dashboard

A full-stack backend built using **FastAPI** and **PostgreSQL** to provide dashboards and AI-driven test execution insights using natural language queries.

---

## 🚀 Features

- ✅ **Dashboard Metrics**
  - Number of executions per project
  - Pass/fail rates over time
  - Average execution durations
- ✅ **Time Range Filters**
  - Support `from_date` and `to_date` in queries
- ✅ **Data Seeding**
  - Populate 100 days of historical dummy data
- ✅ **Modular Structure**
  - Separate service, routes, models, and schemas
- ✅ **Production-ready DB**
  - PostgreSQL (Neon or any hosted variant)
- ✅ **OpenAI Integration Ready**
  - Extendable to support natural language querying

---

## 📁 Project Structure

# 📁 Project Structure – AI-Powered Test Execution Dashboard (FastAPI + PostgreSQL)

```plaintext
DashboardBackend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app entrypoint
│   ├── database.py                  # DB engine, session, Base
│   ├── models.py                    # SQLAlchemy models: Project, Execution, TestCase
│   ├── schemas.py                   # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── dashboard_service.py     # Core dashboard logic: aggregations, filtering
│   └── routes/
│       ├── __init__.py
│       └── dashboard.py             # Dashboard API endpoint
├── seed_data.py                     # Script to populate dummy data over 100 days
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (DATABASE_URL)
├── README.md                        # Project overview, setup, and usage instructions

## ⚙️ Setup Instructions

### 1. 📦 Clone the Repository

```bash
git clone https://github.com/yourusername/DashboardBackend.git
cd DashboardBackend

## 2. 🐍 Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. 📥 Install Python Dependencies

pip install -r requirements.txt


4. 🛠️ Configure Environment Variables

Create a .env file in the root directory with your Postgres connection string:

DATABASE_URL=postgresql://<username>:<password>@<host>:5432/<database>


✅ Example (for Neon):

DATABASE_URL=postgresql://postgres:yourpassword@ep-abcxyz.neon.tech:5432/postgres

5. 🧪 Seed the Database with Dummy Data
To populate the database with 100 days of test data:

python3 seed_data.py


This will:

Create projects, executions, and test_cases tables

Insert random test data for multiple projects over 100 days

6. 🚀 Run the FastAPI Application

Start the development server:

uvicorn app.main:app --reload


curl "http://127.0.0.1:8000/dashboard/summary?from_date=2025-01-01&to_date=2025-04-10"
