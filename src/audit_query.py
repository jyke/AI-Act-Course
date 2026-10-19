import json
import argparse
from pathlib import Path


# =========================================================
# Fichier de logs
# =========================================================

LOG_FILE = "logs/audit.jsonl"


# =========================================================
# Vérification existence fichier
# =========================================================

if not Path(LOG_FILE).exists():

    print(f"Log file not found: {LOG_FILE}")
    exit(1)


# =========================================================
# Arguments CLI
# =========================================================

parser = argparse.ArgumentParser(
    description="Reconstituer l'historique d'une prédiction"
)

parser.add_argument(
    "--request_id",
    required=True,
    help="Request ID à rechercher"
)

args = parser.parse_args()

TARGET_REQUEST_ID = args.request_id


# =========================================================
# Recherche du log
# =========================================================

found_entry = None

with open(LOG_FILE, "r") as f:

    for line in f:

        entry = json.loads(line)

        if entry.get("request_id") == TARGET_REQUEST_ID:

            found_entry = entry
            break


# =========================================================
# Résultat
# =========================================================

if not found_entry:

    print("\nRequest ID not found.")
    exit(1)


# =========================================================
# Affichage Audit Trail
# =========================================================

print("\n=== Audit Trail ===\n")

print(f"Request ID      : {found_entry.get('request_id')}")
print(f"Prediction      : {found_entry.get('prediction')}")
print(f"Confidence      : {found_entry.get('confidence')}")
print(f"Latency (ms)    : {found_entry.get('latency_ms')}")

print("\n--- Model Metadata ---\n")

print(f"Model Version   : {found_entry.get('model_version')}")
print(f"MLflow Run ID   : {found_entry.get('mlflow_run_id')}")
print(f"Git SHA         : {found_entry.get('git_sha')}")

print("\n--- Input Traceability ---\n")

print(f"Input Hash      : {found_entry.get('input_hash')}")

if found_entry.get("user_id_pseudo"):
    print(f"User Pseudonym  : {found_entry.get('user_id_pseudo')}")

print("\n--- Documentation ---\n")

print("Model Card      : ./docs/model_card.md")

print("\n========================\n")