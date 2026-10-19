# Chapter 3 - Audit Trail, Logging & Prediction Traceability

## Overview

This project demonstrates how to transform a machine learning model into a **traceable and auditable AI service**.

Starting from a trained Iris classification model, we build a complete inference system with:

- FastAPI
- MLflow metadata tracking
- Structured audit logs
- User pseudonymization
- Prediction traceability
- GDPR and AI Act considerations

The objective is to understand how to monitor and investigate AI systems once they are deployed in production.

---

## Learning Objectives

By completing this exercise, you will learn how to:

- Serve a machine learning model through an API
- Implement structured logging with Structlog
- Create an audit trail for predictions
- Link predictions to MLflow runs and Git commits
- Pseudonymize user identifiers using HMAC-SHA256
- Reconstruct the history of a prediction
- Apply GDPR and AI Act logging principles

---

## Project Architecture

```text
exercice/
├── app/
│   └── main.py
├── src/
│   ├── train.py
│   └── audit_query.py
├── model_artifacts/
│   ├── model.pkl
│   ├── model_metadata.pkl
│   └── run_id.txt
├── logs/
│   └── audit.jsonl
├── docs/
│   ├── audit_trail.md
│   └── model_card.md
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── .env
```

---

## Tech Stack

- Python
- FastAPI
- Scikit-Learn
- MLflow
- Structlog
- Docker
- UV
- HMAC-SHA256

---

## Features

### Model Training

The training pipeline:

- Loads the Iris dataset
- Trains a RandomForestClassifier
- Logs metrics to MLflow
- Stores model metadata
- Saves model artifacts

### Prediction API

The API exposes:

```http
POST /predict
```

Example payload:

```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2,
  "user_id": "12345"
}
```

Example response:

```json
{
  "request_id": "c9d7b1e8",
  "prediction": 0,
  "confidence": 0.98
}
```

---

### Audit Logging

Every prediction generates an audit record containing:

- Request ID
- Model version
- Git SHA
- MLflow Run ID
- Prediction
- Confidence score
- Latency
- Pseudonymized user ID

Example:

```json
{
  "request_id": "c9d7b1e8",
  "model_version": "iris-v1",
  "git_sha": "abc123",
  "mlflow_run_id": "run_001",
  "prediction": 0,
  "confidence": 0.98,
  "latency_ms": 42,
  "user_id_pseudo": "9b2fa..."
}
```

Logs are stored in:

```text
logs/audit.jsonl
```

---

## Installation

Switch to the second branch 'chapitre-3'

```bash
git checkout chapitre-3
```

Install dependencies:

```bash
uv sync
```

---

## Train the Model

Run:

```bash
uv run src/train.py
```

Expected output:

```text
model_artifacts/
├── model.pkl
├── model_metadata.pkl
└── run_id.txt
```

---

## Configure Environment Variables

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Create a `.env` file:

```env
AUDIT_HMAC_KEY=<your-secret-key>
```

---

## Run the API

Using Docker:

```bash
docker compose up --build api
```

The API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

## Test a Prediction

Using cURL:

```bash
curl -X POST http://localhost:8000/predict \
-H "Content-Type: application/json" \
-d '{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2,
  "user_id": "12345"
}'
```

---

## Query an Audit Trail

Use the generated request ID:

```bash
uv run src/audit_query.py --request_id <REQUEST_ID>
```

Example output:

```text
=== Audit Trail ===

Request ID      : c9d7b1e8
Prediction      : 0
Confidence      : 0.98
Latency (ms)    : 42

--- Model Metadata ---

Model Version   : iris-v1
MLflow Run ID   : run_001
Git SHA         : abc123

--- User ---

User Pseudonym  : 9b2fa...
```

---

## GDPR & AI Act Compliance

## GDPR & AI Act Compliance

Create a `docs/audit_trail.md` document describing the audit logging policy of the application, including the data collected, the purpose of collection (debugging, auditing, compliance, and incident investigation), the GDPR legal basis (Articles 6.1.f and 6.1.c), log retention period, and users' rights regarding their personal data.

This exercise follows several good practices inspired by:

### GDPR

- Data minimization
- User pseudonymization
- Privacy by design
- Limited retention period
- User rights management

### AI Act

- Article 12: Logging requirements
- Article 19: Log retention
- Article 72: Post-market monitoring

### GitHub Repository

## Deliverables

### GitHub Repository

Must contain:

- FastAPI application
- Training pipeline
- Audit trail system
- Model Card
- GDPR logging documentation
- README

### Documentation

- `docs/model_card.md`
- `docs/audit_trail.md`

---

## Key Concepts Covered

- Audit Trail
- Structured Logging
- Model Traceability
- MLflow
- FastAPI
- GDPR
- AI Act
- Privacy by Design
- MLOps Fundamentals

---
