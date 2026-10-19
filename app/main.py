# app/main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import structlog
from datetime import datetime

import uuid
import time
import hashlib
import json
import os
import hmac
import joblib 


# =========================================================
# FastAPI app
# =========================================================

app = FastAPI(
    title="Iris Prediction API",
    version="1.0.0"
)


# =========================================================
# Chargement modèle
# =========================================================

metadata_folder = "model_artifacts/"
model = joblib.load(metadata_folder + "model.pkl")


# =========================================================
# Chargement des métadonnées
# =========================================================

metadata = joblib.load(metadata_folder + "model_metadata.pkl")

MODEL_VERSION = metadata["model_version"]
MLFLOW_RUN_ID = metadata["mlflow_run_id"]
GIT_SHA = metadata["git_sha"]

# =========================================================
# Variables environnement
# =========================================================

AUDIT_HMAC_KEY = os.getenv(
    "AUDIT_HMAC_KEY",
    "dev-secret-key"
)


# =========================================================
# Logging setup
# =========================================================

LOG_FILE = "logs/audit.jsonl"

os.makedirs("logs", exist_ok=True)


def write_log(entry: dict):

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


# =========================================================
# Configuration Structlog
# =========================================================

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ]
)

log = structlog.get_logger()


# =========================================================
# Input schema
# =========================================================

class IrisInput(BaseModel):

    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

    user_id: str


# =========================================================
# Helpers
# =========================================================

def pseudonymize_user_id(user_id: str):

    return hmac.new(
        AUDIT_HMAC_KEY.encode(),
        user_id.encode(),
        hashlib.sha256
    ).hexdigest()



def get_model_metadata():

    return {
        "model_version": MODEL_VERSION,
        "git_sha": GIT_SHA,
        "mlflow_run_id": MLFLOW_RUN_ID
    }



# =========================================================
# Middleware Audit Trail
# =========================================================

@app.middleware("http")
async def audit_middleware(request: Request, call_next):

    request_id = str(uuid.uuid4())

    start_time = time.time()

    response = await call_next(request)

    latency_ms = int((time.time() - start_time) * 1000)



    log.info(
        "http_request",
        request_id=request_id,
        endpoint=request.url.path,
        latency_ms=latency_ms
    )

    response.headers["X-Request-ID"] = request_id

    return response

# =========================================================
# Healthcheck
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Iris Prediction API is running"
    }


# =========================================================
# Prediction endpoint
# =========================================================

@app.post("/predict")
def predict(data: IrisInput):

    # -----------------------------------------
    # Request metadata
    # -----------------------------------------

    request_id = str(uuid.uuid4())

    start = time.time()

    # -----------------------------------------
    # Features
    # -----------------------------------------

    X = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]]

    # -----------------------------------------
    # Prediction
    # -----------------------------------------

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    confidence = float(max(probabilities))

    # -----------------------------------------
    # Latency
    # -----------------------------------------

    latency_ms = int(
        (time.time() - start) * 1000
    )

    # -----------------------------------------
    # Pseudonymisation user_id
    # -----------------------------------------

    user_id_pseudo = pseudonymize_user_id(
        data.user_id
    )

    # -----------------------------------------
    # Model metadata
    # -----------------------------------------

    metadata = get_model_metadata()

    # -----------------------------------------
    # Audit log
    # -----------------------------------------

    log_entry = {

        "request_id": request_id,

        "model_version": metadata["model_version"],

        "git_sha": metadata["git_sha"],

        "mlflow_run_id": metadata["mlflow_run_id"],

        "prediction": int(prediction),

        "confidence": confidence,

        "latency_ms": latency_ms,

        "user_id_pseudo": user_id_pseudo
    }

    # -----------------------------------------
    # Write audit log
    # -----------------------------------------

    write_log(log_entry)

    # -----------------------------------------
    # API response
    # -----------------------------------------

    return {

        "request_id": request_id,

        "prediction": int(prediction),

        "confidence": confidence
    }