# FinFlow Architecture

## Overview
FinFlow is a fintech platform split into two microservices communicating via Kafka.

## Services

### Account Service (port 8000)
Built with Django REST Framework. Handles:
- User registration and JWT authentication
- Account (wallet) management
- Transaction creation and listing
- KYC document upload and download via MinIO
- Publishing Kafka events on transaction lifecycle
- Internal HMAC-authenticated endpoint for status updates

### Processing Service (port 8001)
Built with FastAPI. Handles:
- Consuming transaction.created Kafka events
- Triggering Airflow DAG (stubbed) for payment processing
- Calling Account Service internal endpoint via HMAC-signed request
- Updating transaction status to COMPLETED or FAILED

## Event Flow

Browser
  |
  v  JWT token required
Account Service :8000
  |
  |-- POST /api/transactions/
  |     |-- saves Transaction as PENDING in PostgreSQL
  |           |-- publishes event to Kafka topic: transaction.created
  |
  |-- PATCH /api/internal/transactions/id/
        |-- HMAC signature verified
              |-- updates Transaction to COMPLETED or FAILED

Kafka Broker :9092
  |-- topic: transaction.created
        |-- consumed by Processing Service :8001
              |-- triggers Airflow stub (mocked)
                    |-- HMAC signed PATCH back to Account Service
                          |-- transaction status updated

## Auth Model

### External Auth (JWT)
- All public endpoints require Authorization: Bearer token header
- Tokens issued via POST /api/token/
- Access token expires in 60 minutes
- Refresh token expires in 24 hours
- Verified by JWTAuthentication on every protected request

### Internal Auth (HMAC)
- Processing Service signs every internal request with HMAC-SHA256
- Signature = HMAC(secret, timestamp:nonce:body)
- Account Service verifies three things:
  1. Signature matches
  2. Timestamp is within 5 minutes of now
  3. Nonce has not been used before (replay protection)

## Storage

### PostgreSQL
Stores all structured data:
- users table
- accounts table
- transactions table
- documents table (metadata only — filename, bucket, object key)

### MinIO
Stores raw file bytes:
- KYC documents uploaded by users
- DB only stores the object key and bucket name
- Ownership enforced — users can only access their own documents

## Infrastructure (docker-compose)

Service         | Image                        | Port
----------------|------------------------------|------
PostgreSQL      | postgres:15                  | 5432
Zookeeper       | confluentinc/cp-zookeeper    | 2181
Kafka           | confluentinc/cp-kafka:7.5.0  | 9092
MinIO           | minio/minio:latest           | 9000
Account Service | ./account-service            | 8000
Processing Svc  | ./processing-service         | 8001

## Known Limitations
- Refresh tokens are stateless and cannot be revoked before expiry
- Nonce store is in-memory and resets on service restart
- Airflow integration is stubbed with clean interface matching real Airflow REST API
- Kafka publish failures are logged but do not crash the request