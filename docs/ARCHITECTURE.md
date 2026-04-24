# FinFlow Architecture

## Overview
FinFlow is a fintech platform split into two microservices communicating via Kafka.

## Services

### Account Service (port 8000)
Built with Django REST Framework. Handles:
- User registration and JWT authentication
- Account (wallet) management
- Transaction creation and listing
- KYC document upload/download via MinIO
- Publishing Kafka events on transaction lifecycle
- Internal HMAC-authenticated endpoint for status updates

### Processing Service (port 8001)
Built with FastAPI. Handles:
- Consuming `transaction.created` Kafka events
- Triggering Airflow DAG (stubbed) for payment processing
- Calling Account Service internal endpoint via HMAC-signed request
- Updating transaction status to COMPLETED or FAILED

## Event Flow

Browser
|
v JWT
Account Service :8000
|
|-- POST /api/transactions/
|     |-- saves Transaction (PENDING)
|           |-- publishes Kafka: transaction.created
|
|-- PATCH /api/internal/transactions/<id>/  (HMAC protected)
|-- updates Transaction (COMPLETED/FAILED)
Kafka Broker
|-- transaction.created --> Processing Service :8001
|-- trigger Airflow stub
|-- HMAC signed PATCH --> Account Service


## Auth Model

### External Auth (JWT)
- All public endpoints require Authorization: Bearer token
- Tokens issued via POST /api/token/
- Access token expires in 60 minutes
- Refresh token expires in 24 hours

### Internal Auth (HMAC)
- Processing Service signs every internal request with HMAC-SHA256
- Signature = HMAC(secret, timestamp:nonce:body)
- Account Service verifies signature, timestamp tolerance 5 min, nonce replay

## Storage
- PostgreSQL: all structured data (users, accounts, transactions, document metadata)
- MinIO: raw document bytes (KYC files), DB stores only object key and bucket name

## Infrastructure
All services run via docker-compose:
- postgres:15
- confluentinc/cp-kafka:7.5.0 + zookeeper
- minio/minio:latest
- account-service (Django, port 8000)
- processing-service (FastAPI, port 8001)

## Known Limitations
- Refresh tokens are stateless — cannot be revoked before expiry
- Nonce store is in-memory — resets on service restart
- Airflow integration is stubbed — interface matches real Airflow REST API