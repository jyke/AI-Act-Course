import subprocess
import joblib
import mlflow
import mlflow.sklearn

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import os
import time 


# =========================================================
# Configuration MLflow
# =========================================================

start = time.time()

mlflow.set_tracking_uri("sqlite:///mlflow.db")

print("URI:", time.time() - start)

start = time.time()

mlflow.set_experiment("iris-classification")

print("Experiment:", time.time() - start)
# =========================================================
# Récupération du SHA Git
# =========================================================

#GIT_SHA = subprocess.check_output(   ["git", "rev-parse", "--short", "HEAD"]).decode().strip()
GIT_SHA = "abc1234"  # Placeholder pour le SHA Git

# =========================================================
# Chargement du dataset Iris
# =========================================================

iris = load_iris()

X = iris.data
y = iris.target


# =========================================================
# Split train / test
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# =========================================================
# Entraînement du modèle
# =========================================================

model = RandomForestClassifier(
    n_estimators=10,
    max_depth=3,
    random_state=42
)

model.fit(X_train, y_train)


# =========================================================
# Évaluation
# =========================================================

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print(f"Accuracy: {accuracy:.4f}")


# =========================================================
# Logging MLflow
# =========================================================
print(f"\nLogging to MLflow...")
with mlflow.start_run() as run:

    # -----------------------------
    # Paramètres
    # -----------------------------
    mlflow.log_param("model_type", "RandomForestClassifier")
    mlflow.log_param("n_estimators", 10)
    mlflow.log_param("max_depth", 3)
    mlflow.log_param("random_state", 42)

    # -----------------------------
    # Métriques
    # -----------------------------
    mlflow.log_metric("accuracy", accuracy)

    # -----------------------------
    # Métadonnées Git
    # -----------------------------
    mlflow.set_tag("git_sha", GIT_SHA)

    # -----------------------------
    # Sauvegarde du modèle dans MLflow
    # -----------------------------
    #mlflow.sklearn.log_model(sk_model=model,name="model",serialization_format="skops")

    # -----------------------------
    # Récupération du run_id
    # -----------------------------
    run_id = run.info.run_id

    print(f"MLflow Run ID: {run_id}")


# =========================================================
# Sauvegarde locale du modèle
# =========================================================

metadata_folder = "model_artifacts/"
os.makedirs(metadata_folder, exist_ok=True)

joblib.dump(model, metadata_folder + "model.pkl")


# =========================================================
# Sauvegarde des métadonnées
# =========================================================

metadata = {
    "model_version": "iris-v1",
    "mlflow_run_id": run_id,
    "git_sha": GIT_SHA
}

joblib.dump(metadata, metadata_folder + "model_metadata.pkl")


# =========================================================
# Sauvegarde simple du run_id
# =========================================================

with open(metadata_folder + "run_id.txt", "w") as f:
    f.write(run_id)


# =========================================================
# Affichage final
# =========================================================

print("\n=== Training completed ===")
print(f"Model version : iris-v1")
print(f"MLflow run ID : {run_id}")
print(f"Git SHA       : {GIT_SHA}")

print("\nFiles generated:")
print("- model.pkl")
print("- model_metadata.pkl")
print("- run_id.txt")