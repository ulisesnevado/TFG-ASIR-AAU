"""
Lee /home/ubuntu/cpu_data.csv (ya enriquecido por ia_model.py) y envia
las anomalias detectadas al namespace Custom/AnomalyDetection en CloudWatch.

Solo envia los puntos con severity > 0 para no contaminar la metrica.
"""
import boto3
import pandas as pd
from datetime import datetime, timezone

CSV_PATH = "/home/ubuntu/cpu_data.csv"

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

df = pd.read_csv(CSV_PATH)

events = df[df['severity'] > 0]

if events.empty:
    print("Sin anomalias en este ciclo. Nada que enviar.")
    raise SystemExit(0)

now = datetime.now(timezone.utc)

for _, row in events.iterrows():
    cloudwatch.put_metric_data(
        Namespace='Custom/AnomalyDetection',
        MetricData=[
            {
                'MetricName': 'Anomaly',
                'Timestamp': now,
                'Value': 1,
                'Unit': 'Count'
            },
            {
                'MetricName': 'AnomalySeverity',
                'Timestamp': now,
                'Value': int(row['severity']),
                'Unit': 'Count'
            }
        ]
    )

print(f"Enviadas {len(events)} anomalias a CloudWatch")
