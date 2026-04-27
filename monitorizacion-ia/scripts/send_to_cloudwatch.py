import boto3
import pandas as pd
from datetime import datetime

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

df = pd.read_csv("cpu_data.csv")

events = df[df['severity'] > 0]

for _, row in events.iterrows():
    cloudwatch.put_metric_data(
        Namespace='Custom/AnomalyDetection',
        MetricData=[
            {
                'MetricName': 'Anomaly',
                'Timestamp': datetime.utcnow(),
                'Value': 1,
                'Unit': 'Count'
            },
            {
                'MetricName': 'AnomalySeverity',
                'Timestamp': datetime.utcnow(),
                'Value': int(row['severity']),
                'Unit': 'Count'
            }
        ]
    )

print("Anomalías y severidad enviadas a CloudWatch")
