"""
Lee métricas agregadas del Auto Scaling Group desde CloudWatch
y las guarda en /home/ubuntu/cpu_data.csv para que ia_model.py las procese.
"""
import boto3
import pandas as pd
from datetime import datetime, timedelta, timezone

ASG_NAME = "foca-asg"
CSV_PATH = "/home/ubuntu/cpu_data.csv"

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(minutes=30)


def get_metric(metric_name):
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName=metric_name,
        Dimensions=[
            {'Name': 'AutoScalingGroupName', 'Value': ASG_NAME}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average']
    )
    return sorted(response['Datapoints'], key=lambda x: x['Timestamp'])


cpu = get_metric('CPUUtilization')
network_in = get_metric('NetworkIn')
network_out = get_metric('NetworkOut')

if not cpu:
    print("No hay datapoints aún para el ASG. Saliendo sin generar CSV.")
    raise SystemExit(0)

# Construir un dict por timestamp para alinear las tres métricas
by_ts = {}
for dp in cpu:
    by_ts.setdefault(dp['Timestamp'], {})['CPU'] = dp['Average']
for dp in network_in:
    by_ts.setdefault(dp['Timestamp'], {})['NetworkIn'] = dp['Average']
for dp in network_out:
    by_ts.setdefault(dp['Timestamp'], {})['NetworkOut'] = dp['Average']

data = []
for ts, vals in sorted(by_ts.items()):
    data.append({
        'Timestamp': ts,
        'CPU': vals.get('CPU', 0),
        'NetworkIn': vals.get('NetworkIn', 0),
        'NetworkOut': vals.get('NetworkOut', 0),
    })

df = pd.DataFrame(data)
df.to_csv(CSV_PATH, index=False)

print(f"Datos guardados en {CSV_PATH}")
print(df)
