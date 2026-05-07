#!/usr/bin/env python3
"""
Aplica el modelo ya entrenado.

La severidad ya no depende de reglas externas tipo CPU >= 80.
Ahora depende del score del propio Isolation Forest.
"""

import json
import os
from pathlib import Path

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent

CSV_PATH = Path(os.getenv("CSV_PATH", PROJECT_ROOT / "cpu_data.csv"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", PROJECT_ROOT))

MODEL_PATH = MODEL_DIR / "isolation_forest_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"


def load_metadata() -> dict:
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"No existe {METADATA_PATH}. Ejecuta primero scripts/train_model.py"
        )

    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def calculate_severity(prediction: int, anomaly_score: float, thresholds: dict) -> int:
    """
    0 = normal
    1 = anomalía leve
    2 = anomalía media
    3 = anomalía crítica

    Solo se asigna severidad si el modelo ha marcado la fila como anomalía.
    """
    if prediction != -1:
        return 0

    if anomaly_score >= thresholds["severity_3"]:
        return 3

    if anomaly_score >= thresholds["severity_2"]:
        return 2

    return 1


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No existe el CSV: {CSV_PATH}")

    metadata = load_metadata()
    features = metadata["features"]
    thresholds = metadata["severity_thresholds"]

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()

    for col in features:
        if col not in df.columns:
            raise ValueError(f"Falta la columna {col} en {CSV_PATH}")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=features)

    X = df[features]
    X_scaled = scaler.transform(X)

    predictions = model.predict(X_scaled)
    decision_scores = model.decision_function(X_scaled)
    anomaly_scores = -decision_scores

    df["model_score"] = decision_scores
    df["anomaly_score"] = anomaly_scores
    df["anomaly"] = predictions

    df["severity"] = [
        calculate_severity(pred, score, thresholds)
        for pred, score in zip(predictions, anomaly_scores)
    ]

    # Se mantiene por compatibilidad con lo que ya tenías,
    # pero ahora no sobreescribe la decisión del modelo.
    df["final_anomaly"] = df["anomaly"]

    df.to_csv(CSV_PATH, index=False)

    print("Predicción completada.")
    print(df.tail(20)[[
        "Timestamp",
        "CPU",
        "NetworkIn",
        "NetworkOut",
        "anomaly",
        "anomaly_score",
        "severity",
        "final_anomaly",
    ]])


if __name__ == "__main__":
    main()
