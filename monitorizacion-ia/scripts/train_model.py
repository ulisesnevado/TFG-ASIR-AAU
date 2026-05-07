#!/usr/bin/env python3
"""
Entrena Isolation Forest con train/test split.

- Entrena solo con el 80% inicial del histórico.
- Evalúa con el 20% final.
- Si existe columna label, la usa como etiqueta real.
- Si no existe label, genera anomalías sintéticas solo para evaluación.
- Guarda modelo, scaler, thresholds de severidad, classification report y ROC curve.
"""

import json
import os
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent

CSV_PATH = Path(os.getenv("CSV_PATH", PROJECT_ROOT / "cpu_data.csv"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", PROJECT_ROOT))
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "isolation_forest_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"
REPORT_PATH = MODEL_DIR / "classification_report.txt"
METRICS_PATH = MODEL_DIR / "evaluation_metrics.json"
ROC_PATH = MODEL_DIR / "roc_curve.png"

FEATURES = ["CPU", "NetworkIn", "NetworkOut"]

CONTAMINATION = float(os.getenv("CONTAMINATION", "0.05"))
RANDOM_STATE = int(os.getenv("RANDOM_STATE", "42"))


def load_dataset() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No existe el CSV: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()

    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", utc=True)
        df = df.sort_values("Timestamp")

    missing = [col for col in FEATURES if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas obligatorias en el CSV: {missing}")

    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=FEATURES)

    if "Timestamp" in df.columns:
        df = df.dropna(subset=["Timestamp"])
        df = df.drop_duplicates(subset=["Timestamp"])

    if len(df) < 30:
        raise ValueError(
            f"Dataset demasiado pequeño ({len(df)} filas). "
            "Recoge más datos antes de entrenar."
        )

    return df


def normalize_labels(raw_labels: pd.Series) -> np.ndarray:
    """
    Convierte etiquetas habituales a formato:
    0 = normal
    1 = anomalía
    """
    mapped = raw_labels.replace({
        -1: 1,
        1: 0,
        0: 0,
        "normal": 0,
        "NORMAL": 0,
        "ok": 0,
        "OK": 0,
        "anomaly": 1,
        "ANOMALY": 1,
        "anomalia": 1,
        "anomalía": 1,
    })

    return mapped.astype(int).to_numpy()


def create_synthetic_anomalies(X_test: pd.DataFrame) -> pd.DataFrame:
    """
    Genera anomalías de validación controladas.
    No se usan para entrenar, solo para obtener métricas de evaluación.
    """
    n = min(max(10, len(X_test) // 2), len(X_test))
    synth = X_test.sample(n=n, random_state=RANDOM_STATE).copy()

    cpu_anomaly = max(85.0, float(X_test["CPU"].quantile(0.95)) * 3)
    net_in_anomaly = max(
        float(X_test["NetworkIn"].max()) + 1,
        float(X_test["NetworkIn"].quantile(0.95)) * 6,
    )
    net_out_anomaly = max(
        float(X_test["NetworkOut"].max()) + 1,
        float(X_test["NetworkOut"].quantile(0.95)) * 6,
    )

    for pos, idx in enumerate(synth.index):
        if pos % 3 == 0:
            synth.loc[idx, "CPU"] = cpu_anomaly
        elif pos % 3 == 1:
            synth.loc[idx, "NetworkIn"] = net_in_anomaly
        else:
            synth.loc[idx, "NetworkOut"] = net_out_anomaly

    return synth


def save_roc_curve(y_true: np.ndarray, y_score: np.ndarray) -> float | None:
    if len(np.unique(y_true)) < 2:
        print("No se genera ROC: y_true solo tiene una clase.")
        return None

    auc_value = float(roc_auc_score(y_true, y_score))
    fpr, tpr, _ = roc_curve(y_true, y_score)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f"ROC AUC = {auc_value:.3f}")
    plt.plot([0, 1], [0, 1], linestyle="--", label="Azar")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve - Isolation Forest")
    plt.legend()
    plt.tight_layout()
    plt.savefig(ROC_PATH, dpi=150)
    plt.close()

    return auc_value


def main():
    df = load_dataset()

    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        shuffle=False,
    )

    X_train = train_df[FEATURES]
    X_test = test_df[FEATURES]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = IsolationForest(
        n_estimators=300,
        contamination=CONTAMINATION,
        random_state=RANDOM_STATE,
        max_samples="auto",
    )

    model.fit(X_train_scaled)

    train_anomaly_score = -model.decision_function(X_train_scaled)

    severity_thresholds = {
        "severity_1": float(np.percentile(train_anomaly_score, 90)),
        "severity_2": float(np.percentile(train_anomaly_score, 95)),
        "severity_3": float(np.percentile(train_anomaly_score, 99)),
    }

    if "label" in test_df.columns:
        X_eval = X_test.copy()
        y_true = normalize_labels(test_df["label"])
        evaluation_type = "real_labels"
    else:
        synthetic = create_synthetic_anomalies(X_test)

        X_eval = pd.concat([X_test, synthetic], ignore_index=True)
        y_true = np.concatenate([
            np.zeros(len(X_test), dtype=int),
            np.ones(len(synthetic), dtype=int),
        ])
        evaluation_type = "synthetic_validation"

    X_eval_scaled = scaler.transform(X_eval)

    raw_pred = model.predict(X_eval_scaled)
    y_pred = (raw_pred == -1).astype(int)

    y_score = -model.decision_function(X_eval_scaled)

    accuracy = float(accuracy_score(y_true, y_pred))
    report = classification_report(
        y_true,
        y_pred,
        target_names=["normal", "anomalia"],
        zero_division=0,
    )

    matrix = confusion_matrix(y_true, y_pred).tolist()
    auc_value = save_roc_curve(y_true, y_score)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    metadata = {
        "features": FEATURES,
        "contamination": CONTAMINATION,
        "random_state": RANDOM_STATE,
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "evaluation_type": evaluation_type,
        "severity_thresholds": severity_thresholds,
        "model_logic": {
            "normal": 1,
            "anomaly": -1,
            "anomaly_score": "-decision_function; cuanto mayor, más anómalo",
        },
    }

    METADATA_PATH.write_text(
        json.dumps(metadata, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    metrics = {
        "accuracy": accuracy,
        "roc_auc": auc_value,
        "confusion_matrix": matrix,
        "evaluation_type": evaluation_type,
        "report_path": str(REPORT_PATH),
        "roc_curve_path": str(ROC_PATH),
    }

    METRICS_PATH.write_text(
        json.dumps(metrics, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    REPORT_PATH.write_text(
        "Classification Report - Isolation Forest\n"
        f"Evaluation type: {evaluation_type}\n"
        f"Accuracy: {accuracy:.4f}\n"
        f"ROC AUC: {auc_value if auc_value is not None else 'N/A'}\n\n"
        f"{report}\n"
        f"Confusion matrix:\n{matrix}\n",
        encoding="utf-8",
    )

    print("Modelo entrenado correctamente.")
    print(f"Modelo: {MODEL_PATH}")
    print(f"Scaler: {SCALER_PATH}")
    print(f"Metadata: {METADATA_PATH}")
    print(f"Report: {REPORT_PATH}")
    print(f"ROC: {ROC_PATH}")
    print(report)


if __name__ == "__main__":
    main()
