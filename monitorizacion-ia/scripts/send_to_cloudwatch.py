#!/usr/bin/env python3
"""
Envía a CloudWatch solo las nuevas anomalías detectadas.

Publica:
- Anomaly
- AnomalySeverity
- AnomalyScore
"""

import os
from pathlib import Path

import boto3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent

CSV_PATH = Path(os.getenv("CSV_PATH", PROJECT_ROOT / "cpu_data.csv"))
STATE_DIR = PROJECT_ROOT / ".state"
STATE_DIR.mkdir(parents=True, exist_ok=True)

STATE_PATH = STATE_DIR / "last_cloudwatch_timestamp.txt"

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ASG_NAME = os.getenv("ASG_NAME", "foca-asg")
NAMESPACE = os.getenv("CW_NAMESPACE", "Custom/AnomalyDetection")

cloudwatch = boto3.client("cloudwatch", region_name=AWS_REGION)


def read_last_sent_timestamp():
    if not STATE_PATH.exists():
        return None

    value = STATE_PATH.read_text(encoding="utf-8").strip()

    if not value:
        return None

    return pd.to_datetime(value, utc=True)


def write_last_sent_timestamp(timestamp):
    STATE_PATH.write_text(timestamp.isoformat(), encoding="utf-8")


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No existe el CSV: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()

    required = ["Timestamp", "severity", "anomaly", "anomaly_score"]

    for col in required:
        if col not in df.columns:
            raise ValueError(
                f"Falta la columna {col}. Ejecuta primero scripts/ia_model.py"
            )

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", utc=True)
    df["severity"] = pd.to_numeric(df["severity"], errors="coerce").fillna(0).astype(int)
    df["anomaly_score"] = pd.to_numeric(df["anomaly_score"], errors="coerce").fillna(0.0)

    df = df.dropna(subset=["Timestamp"])
    df = df.sort_values("Timestamp")

    last_sent = read_last_sent_timestamp()

    events = df[df["severity"] > 0].copy()

    if last_sent is not None:
        events = events[events["Timestamp"] > last_sent]

    if events.empty:
        print("Sin anomalías nuevas para enviar a CloudWatch.")
        return

    metric_data = []

    dimensions = [
        {"Name": "AutoScalingGroupName", "Value": ASG_NAME},
        {"Name": "Source", "Value": "IsolationForest"},
    ]

    for _, row in events.iterrows():
        ts = row["Timestamp"].to_pydatetime()

        metric_data.extend([
            {
                "MetricName": "Anomaly",
                "Dimensions": dimensions,
                "Timestamp": ts,
                "Value": 1.0,
                "Unit": "Count",
                "StorageResolution": 60,
            },
            {
                "MetricName": "AnomalySeverity",
                "Dimensions": dimensions,
                "Timestamp": ts,
                "Value": float(row["severity"]),
                "Unit": "Count",
                "StorageResolution": 60,
            },
            {
                "MetricName": "AnomalyScore",
                "Dimensions": dimensions,
                "Timestamp": ts,
                "Value": float(row["anomaly_score"]),
                "Unit": "None",
                "StorageResolution": 60,
            },
        ])

    for start in range(0, len(metric_data), 1000):
        cloudwatch.put_metric_data(
            Namespace=NAMESPACE,
            MetricData=metric_data[start:start + 1000],
        )

    latest_ts = events["Timestamp"].max()
    write_last_sent_timestamp(latest_ts)

    print(f"Enviadas {len(events)} anomalías nuevas a CloudWatch.")
    print(f"Último timestamp enviado: {latest_ts}")


if __name__ == "__main__":
    main()
