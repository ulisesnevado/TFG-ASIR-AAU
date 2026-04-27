import boto3
import pandas as pd
from datetime import datetime, timedelta

ec2_instance_id = "i-0c6cf217dacb6a7eb"

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

end_time = datetime.utcnow()
start_time = end_time - timedelta(minutes=30)

def get_metric(metric_name):
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName=metric_name,
        Dimensions=[
            {'Name': 'InstanceId', 'Value': ec2_instance_id}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average']
    )
    
    return response['Datapoints']

cpu = get_metric('CPUUtilization')
network_in = get_metric('NetworkIn')
network_out = get_metric('NetworkOut')

data = []

for i in range(len(cpu)):
    data.append({
        'Timestamp': cpu[i]['Timestamp'],
        'CPU': cpu[i]['Average'],
        'NetworkIn': network_in[i]['Average'] if i < len(network_in) else 0,
        'NetworkOut': network_out[i]['Average'] if i < len(network_out) else 0
    })

df = pd.DataFrame(data)
df = df.sort_values(by='Timestamp')

df.to_csv("cpu_data.csv", index=False)

print("Datos guardados en cpu_data.csv")
print(df)
