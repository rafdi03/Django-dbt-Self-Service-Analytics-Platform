


# 🚀 Django-dbt Self-Service Analytics Platform

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.0+-092E20?style=for-the-badge&logo=django&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-Core-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-316192?style=for-the-badge&logo=postgresql&logoColor=white)

## 📋 Overview

**Django-dbt Platform** is an end-to-end **Data Engineering & Web Application** solution designed to bridge the gap between manual data entry and automated analytics.

This project solves a common business problem: **"Shadow IT" data** (e.g., sales targets, offline budgets) living in Excel/CSV files. This platform allows business users to upload CSVs via a user-friendly Web UI, which automatically triggers **dbt (data build tool)** pipelines to ingest, clean, and transform the data into analytics-ready models in PostgreSQL.

It demonstrates a convergence of **Software Engineering (Django)** and **Analytics Engineering (dbt)** wrapped in a fully containerized **Docker** environment.

---

## 🏗️ System Architecture

The system uses an event-driven approach where a user action (upload) directly orchestrates the data transformation pipeline.

```mermaid
graph LR
    User[Business User] -->|Uploads CSV| WebUI[Django Web App]
    WebUI -->|Pandas Processing| DB_Raw[(PostgreSQL - Raw)]
    WebUI -->|Triggers| DBT[dbt Core]
    DBT -->|Reads Raw Data| DB_Raw| DB_Marts[(PostgreSQL - Marts)]
    DBT -->|Transforms & Materializes| DB_Marts[(PostgreSQL - Marts)]
    DB_Marts -->|Clean Data| BI[BI Dashboard / Analytics]

```

---

## ✨ Key Features

* **Self-Service Data Ingestion:** Custom-built UI for non-technical users to upload structured data (CSV).
* **Automated ELT Pipeline:** Automatically triggers `dbt run` immediately after a successful upload using Python integration.
* **Data Validation:** Uses Pandas to parse and validate CSV structure before database insertion.
* **Containerized Infrastructure:** The entire stack (Web, DB, Transformation logic) runs on Docker Compose for portability and reproducibility.
* **Auditability:** Tracks upload history and transformation status via Django Admin.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| --- | --- | --- |
| **Orchestration & Web** | **Django (Python)** | Handles HTTP requests, file processing, and orchestrates dbt commands. |
| **Transformation** | **dbt-core** | Compiles and runs SQL transformation logic (ELT). |
| **Database** | **PostgreSQL** | Stores both `raw` (staging) and `marts` (production) tables. |
| **Data Processing** | **Pandas** | Used for efficient CSV parsing and pre-validation. |
| **Infrastructure** | **Docker & Compose** | Ensures consistent environment across dev and production. |

---

## 📂 Project Structure

```bash
django_dbt_platform/
├── dbt_project/              # The dbt transformation logic & SQL models
│   ├── models/
│   │   ├── staging/          # Raw data cleaning
│   │   └── marts/            # Business logic tables
│   └── dbt_project.yml
├── platform_app/             # Django Application Logic
│   ├── views.py              # Logic: Upload -> Pandas -> DB -> dbt Trigger
│   ├── models.py             # Database schema definition
│   └── templates/            # HTML Frontend UI
├── docker-compose.yml        # Container orchestration config
├── Dockerfile                # Custom image definition
└── requirements.txt          # Python dependencies

```

---

## 🚀 Getting Started

Follow these steps to run the project locally.

### Prerequisites

* **Docker** & **Docker Compose** installed.
* **Git** installed.

### Installation & Run

1. **Clone the repository**
```bash
git clone [https://github.com/YOUR_USERNAME/django-dbt-platform.git](https://github.com/YOUR_USERNAME/django-dbt-platform.git)
cd django_dbt_platform

```


2. **Build and Run Containers**
```bash
docker-compose up --build

```


3. **Access the Platform**
* **Upload Interface:** [http://localhost:8000/upload/](https://www.google.com/search?q=http://localhost:8000/upload/)
* **Django Admin:** [http://localhost:8000/admin/](https://www.google.com/search?q=http://localhost:8000/admin/)


4. **How to Test**
1. Open the **Upload Interface**.
2. Select a CSV file (ensure it contains `order_delivered_carrier_date` and `customer_id`).
3. Click **Upload & Proses**.
4. Check your terminal/logs to see dbt running automatically!



---

## 💡 Why This Project Matters?
<img width="1908" height="1984" alt="screencapture-localhost-8000-upload-2026-01-08-18_18_14" src="https://github.com/user-attachments/assets/a88dc192-599b-45af-b0d3-d27fb48f1b49" />

In many organizations, Data Engineers spend too much time manually loading Excel files sent by stakeholders. This project proves capability in:

1. **Automation:** Eliminating manual ETL work.
2. **Tool Integration:** Seamlessly connecting Python application logic with SQL-based dbt workflows.
3. **User Empathy:** Building tools that empower business users while maintaining data engineering standards.

---

## 🔮 Future Improvements

* [ ] Implement **Celery & Redis** for asynchronous task processing (handling large files without blocking the UI).
* [ ] Add **dbt tests** to block bad data entry automatically.
* [ ] Create a visualized dashboard using **Metabase** or **Superset** connected to the Postgres container.

---



