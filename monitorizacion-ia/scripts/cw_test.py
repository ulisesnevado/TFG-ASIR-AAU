#!/usr/bin/env python3
"""
Recolecta métricas agregadas del Auto Scaling Group desde CloudWatch
y las guarda en monitorizacion-ia/datos/cpu_data.csv.
"""

import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

import boto3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent

ASG_NAME = os.getenv("ASG_NAME", "foca-asg")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "90"))
PERIOD_SECONDS = int(os.getenv("CW_PERIOD_SECONDS", "300"))

CSV_PATH = Path(os.getenv("CSV_PATH", PROJECT_ROOT / "cpu_data.csv"))
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

FEATURES = ["CPU", "NetworkIn", "NetworkOut"]

cloudwatch = boto3.client("cloudwatch", region_name=AWS_REGION)

end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=LOOKBACK_HOURS)


def get_metric(metric_name: str):
    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName=metric_name,
        Dimensions=[
            {"Name": "AutoScalingGroupName", "Value": ASG_NAME}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=PERIOD_SECONDS,
        Statistics=["Average"],
    )

    return sorted(response.get("Datapoints", []), key=lambda x: x["Timestamp"])


def main():
    cpu = get_metric("CPUUtilization")
    network_in = get_metric("NetworkIn")
    network_out = get_metric("NetworkOut")

    if not cpu and not network_in and not network_out:
        print(f"No hay datapoints para el ASG {ASG_NAME}. No se genera CSV.")
        return

    by_ts = {}

    for dp in cpu:
        by_ts.setdefault(dp["Timestamp"], {})["CPU"] = dp["Average"]

    for dp in network_in:
        by_ts.setdefault(dp["Timestamp"], {})["NetworkIn"] = dp["Average"]

    for dp in network_out:
        by_ts.setdefault(dp["Timestamp"], {})["NetworkOut"] = dp["Average"]

    rows = []
    for ts, values in sorted(by_ts.items()):
        rows.append({
            "Timestamp": ts,
            "CPU": values.get("CPU", 0.0),
            "NetworkIn": values.get("NetworkIn", 0.0),
            "NetworkOut": values.get("NetworkOut", 0.0),
        })

    new_df = pd.DataFrame(rows)
    new_df["Timestamp"] = pd.to_datetime(new_df["Timestamp"], utc=True)

    if CSV_PATH.exists():
        old_df = pd.read_csv(CSV_PATH)
        df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        df = new_df

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", utc=True)

    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Timestamp"] + FEATURES)
    df = df.drop_duplicates(subset=["Timestamp"])
    df = df.sort_values("Timestamp")
    df = df.tail(2000)

    df.to_csv(CSV_PATH, index=False)

    print(f"Datos guardados en {CSV_PATH}")
    print(df.tail(10))


if __name__ == "__main__":
    main()
