# API Contracts

## Account Service (port 8000)

### Auth
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/token/ | Get JWT access + refresh token | None |
| POST | /api/token/refresh/ | Refresh access token | None |

Login request:
{ "email": "user@example.com", "password": "secure123" }

Login response:
{ "access": "eyJ...", "refresh": "eyJ..." }

---

### Users
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/users/ | Register new user | None |
| GET | /api/users/<id>/ | Get user | JWT |
| PATCH | /api/users/<id>/ | Update user | JWT |
| DELETE | /api/users/<id>/ | Soft delete user | JWT |

---

### Accounts
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/accounts/ | List user accounts | JWT |
| POST | /api/accounts/ | Create account | JWT |
| GET | /api/accounts/<id>/ | Get account | JWT |
| PATCH | /api/accounts/<id>/ | Update account | JWT |
| DELETE | /api/accounts/<id>/ | Soft delete account | JWT |

Create account request:
{ "name": "My Wallet", "currency": "USD", "status": "ACTIVE" }

---

### Transactions
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/transactions/ | List transactions | JWT |
| POST | /api/transactions/ | Create transaction | JWT |
| GET | /api/transactions/<id>/ | Get transaction | JWT |

Create transaction request:
{ "account": "uuid", "amount": "100.00", "transaction_type": "CREDIT", "description": "Payment" }

Transaction response:
{ "id": "uuid", "account": "uuid", "amount": "100.00", "transaction_type": "CREDIT", "status": "PENDING", "created_at": "2026-04-24T10:00:00Z" }

---

### Documents
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/documents/ | List documents | JWT |
| POST | /api/documents/upload/ | Upload KYC document | JWT |
| GET | /api/documents/<id>/download/ | Download document | JWT |

Upload: multipart/form-data — file (PDF/JPEG/PNG max 5MB), doc_type, account uuid

---

### Internal (HMAC protected)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| PATCH | /api/internal/transactions/<id>/ | Update transaction status | HMAC |

Required headers: X-Timestamp, X-Nonce, X-Signature
Request body: { "status": "COMPLETED" }

---

## Processing Service (port 8001)

### Health
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /health | Health check | None |
| GET | / | Service info | None |

Health response: { "status": "ok", "service": "processing-service" }

---

## Swagger UI
- Account Service: http://localhost:8000/api/docs/
- Account Service ReDoc: http://localhost:8000/api/redoc/