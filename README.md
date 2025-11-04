# Transaction Aggregation ETL Pipeline

## Overview
This project implements an ETL pipeline using PySpark to process large transactional datasets stored in CSV files.
The pipeline aggregates transactions by customer and stores the final results in a PostgreSQL database for analytical querying.
The design emphasizes automation for repeatable, reliable runs.

---

## Features
- **Extract:** Read raw transaction data from CSV.
- **Transform:**
  - Aggregate by `customer_id`.
  - Determine each customer's `favourite_product` (the product with the highest total units sold).
  - Calculate `longest_streak` (the longest sequence of consecutive purchase days).
- **Load:** Write the transformed data into PostgreSQL.
- **Automation:** Support for scheduled daily runs and idempotent re-runs via orchestration (e.g., Airflow or cron).

---

## Tech Stack
| Component | Technology |
|------------|-------------|
| Programming Language | Python 3.9 |
| Processing Engine | Apache Spark |
| Database | PostgreSQL 13 |
| Containerization | Docker, Docker Compose |
| Dependency Management | Poetry |
| Orchestration (Automation) | Apache Airflow or cron (optional) |

---

## Usage

### Run ETL pipeline
```bash
docker-compose build
docker-compose run etl poetry run python main.py   --source /opt/data/transaction.csv   --database warehouse   --table customers
```

### Verify output
```bash
docker-compose exec db psql --user postgres -d warehouse   -c 'SELECT * FROM customers LIMIT 10;'
```

---

## Integration Test
The integration test verifies the correctness of the ETL pipeline by asserting that for `customer_id = 0023938`:
- `favourite_product` matches the most frequently sold product.
- `longest_streak` equals the correct number of consecutive purchase days.

---

## Cloud Deployment Proposal
A scalable, automated deployment can be built on **AWS**:

| Layer | AWS Service | Purpose |
|--------|--------------|----------|
| Data Ingestion | AWS DMS | Move data from on‑premise RDBMS to AWS |
| Scheduling & Orchestration (Automation) | Amazon MWAA (Managed Airflow) or AWS Step Functions | Automate daily jobs, retries, SLAs |
| Data Processing | AWS Glue or Amazon EMR (Spark) | Perform ETL transformations at scale |
| Data Storage | Amazon Redshift | Store aggregated data for interactive analytics |
| Monitoring & Alerts | Amazon CloudWatch, SNS | Centralized logs, metrics, failure notifications |

This design provides automation, scalability, and fault tolerance with managed services and auto-scaling compute.

---

## Deliverables
- `main.py` – ETL entry point (PySpark pipeline implementation)
- `docker-compose.yml` – Defines Spark, PostgreSQL, and ETL containers
- `Dockerfile` – Python 3.9 image with Spark and dependencies
- `tests/` – Integration tests for ETL validation
- `deployment.pdf` – Cloud architecture proposal and explanation
- `changes.patch` – Git patch file containing implementation changes

---

## Project Structure
```
TAKE-HOME-TEST/
├── data/
│   └── transaction.csv
├── main.py
├── integration_test.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── poetry.lock
├── .env
├── .gitignore
└── README.md
```

---

## Keywords
ETL, PySpark, PostgreSQL, Docker, Docker Compose, Data Engineering, Data Pipeline, Orchestration, Scheduling, **Automation**, Airflow, AWS Glue, EMR, Redshift, CloudWatch, CI/CD, Integration Test.

---

## Summary
A reproducible and containerized ETL pipeline built with PySpark, PostgreSQL, and Docker.
Designed for large-scale transaction aggregation, automated scheduling, testing, and cloud-ready deployment.
