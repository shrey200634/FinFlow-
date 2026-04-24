# FinFlow — Fintech Microservices Platform

A production-style fintech platform. Split into two microservices communicating via Kafka, with JWT external auth, HMAC internal auth, and MinIO document storage.

---

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Running the Services](#running-the-services)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [Key Endpoints](#key-endpoints)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Overview

FinFlow is a fintech platform split into two services:

Account Service (Django REST Framework — port 8000)
- User registration and JWT login
- Account (wallet) CRUD
- Transaction create, list, get
- KYC document upload and download via MinIO
- Publishes Kafka events on transaction lifecycle
- Internal HMAC-protected endpoint for status updates

Processing Service (FastAPI — port 8001)
- Consumes transaction.created Kafka events
- Triggers Airflow DAG stub for payment processing
- Calls Account Service internal endpoint with HMAC-signed request
- Updates transaction status to COMPLETED or FAILED

---

## Architecture

Browser → JWT → Account Service :8000
  - POST /api/transactions/ → saves as PENDING → publishes Kafka: transaction.created
  - PATCH /api/internal/transactions/id/ (HMAC) → updates to COMPLETED or FAILED

Kafka: transaction.created → Processing Service :8001
  - triggers Airflow stub → HMAC signed PATCH → Account Service

Infrastructure:
  PostgreSQL  — all structured data
  MinIO       — KYC document bytes
  Kafka       — event bus
  Zookeeper   — Kafka cluster manager

Full details in docs/ARCHITECTURE.md

---

## Prerequisites

- Docker + Docker Compose
- Python 3.11+
- Git

---

## Setup

1. Clone the repository

git clone https://github.com/shrey200634/FinFlow-.git
cd FinFlow-

2. Create environment files

copy .env.example account-service\.env
copy .env.example processing-service\.env

Edit each .env file if needed. Defaults work for local development.

3. Start all services

docker-compose up --build

This starts: PostgreSQL, Zookeeper, Kafka, MinIO, Account Service, Processing Service

4. Run migrations (first time only)

docker exec finflow-account-service python manage.py migrate

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DJANGO_SECRET_KEY | Django secret key | dev-secret-change-me |
| DEBUG | Debug mode | True |
| ALLOWED_HOSTS | Comma separated hosts | * |
| DB_NAME | PostgreSQL database | finflow |
| DB_USER | PostgreSQL user | postgres |
| DB_PASSWORD | PostgreSQL password | postgres |
| DB_HOST | PostgreSQL host | localhost |
| DB_PORT | PostgreSQL port | 5432 |
| KAFKA_BROKER | Kafka broker URL | localhost:9092 |
| KAFKA_TOPIC_CREATED | Kafka topic for created events | transaction.created |
| KAFKA_TOPIC_UPDATED | Kafka topic for updated events | transaction.updated |
| KAFKA_GROUP_ID | Kafka consumer group | processing-service |
| MINIO_ENDPOINT | MinIO endpoint | localhost:9000 |
| MINIO_ACCESS_KEY | MinIO access key | minioadmin |
| MINIO_SECRET_KEY | MinIO secret key | minioadmin |
| MINIO_BUCKET | MinIO bucket name | finflow-docs |
| HMAC_SECRET | Internal HMAC signing secret | dev-hmac-secret-change-me |
| ACCOUNT_SERVICE_URL | Account Service base URL | http://localhost:8000 |

---

## Running the Services

Locally without Docker:

Account Service:
cd account-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

Processing Service:
cd processing-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

With Docker Compose:
docker-compose up --build

---

## Running Tests

Account Service:
cd account-service
pytest

Processing Service:
cd processing-service
pytest

With coverage:
cd account-service
pytest --cov=apps --cov-report=term-missing

cd processing-service
pytest --cov=app --cov-report=term-missing

Coverage Results:
- Account Service: 92%
- Processing Service: 78%

Run linting:
cd account-service
black apps/
isort apps/
flake8 apps/

pre-commit hooks (runs automatically on every git commit):
pre-commit run --all-files

---

## API Documentation

http://localhost:8000/api/docs/    — Swagger UI Account Service
http://localhost:8000/api/redoc/   — ReDoc Account Service
http://localhost:8001/health       — Health check Processing Service
http://localhost:9001              — MinIO Console

---

## Key Endpoints

Auth:
POST   /api/token/           Login — returns JWT access and refresh token
POST   /api/token/refresh/   Refresh access token

Users:
POST   /api/users/           Register new user
GET    /api/users/id/        Get user details (JWT)
PATCH  /api/users/id/        Update user (JWT)
DELETE /api/users/id/        Soft delete user (JWT)

Accounts:
GET    /api/accounts/        List accounts (JWT)
POST   /api/accounts/        Create account (JWT)
GET    /api/accounts/id/     Get account (JWT)
PATCH  /api/accounts/id/     Update account (JWT)
DELETE /api/accounts/id/     Soft delete account (JWT)

Transactions:
GET    /api/transactions/      List transactions (JWT)
POST   /api/transactions/      Create transaction — publishes Kafka event (JWT)
GET    /api/transactions/id/   Get transaction (JWT)

Documents:
GET    /api/documents/                  List documents (JWT)
POST   /api/documents/upload/           Upload KYC document to MinIO (JWT)
GET    /api/documents/id/download/      Download document from MinIO (JWT)

Internal (Processing Service only):
PATCH  /api/internal/transactions/id/   Update transaction status (HMAC)
Headers required: X-Timestamp, X-Nonce, X-Signature

---

## Project Structure

finflow/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   └── API_CONTRACTS.md
├── account-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── pytest.ini
│   ├── setup.cfg
│   ├── mypy.ini
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/
│       ├── users/
│       ├── accounts/
│       ├── transactions/
│       └── documents/
└── processing-service/
    ├── Dockerfile
    ├── requirements.txt
    ├── pytest.ini
    └── app/
        ├── main.py
        ├── config.py
        ├── consumer.py
        ├── hmac_auth.py
        ├── airflow_stub.py
        └── tests/

---

## Troubleshooting

Postgres connection refused:
docker start finflow-postgres

Kafka not ready:
docker-compose restart kafka

MinIO not accessible:
docker start finflow-minio

Migrations not applied:
docker exec finflow-account-service python manage.py migrate

Tests failing — postgres not running:
docker start finflow-postgres
pytest

pre-commit failing:
pre-commit run --all-files
git add .
git commit -m "your message"

---

## Submission Checklist

- docker-compose up starts all services without manual steps
- Swagger UI works at http://localhost:8000/api/docs/
- pytest passes for both services
- Coverage above 85% for core modules
- pre-commit hooks passing — black, isort, flake8
- No secrets hardcoded — all via .env
- .env files in .gitignore — never committed
- docs/ARCHITECTURE.md complete
- docs/API_CONTRACTS.md complete
- README.md complete

---

