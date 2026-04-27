import pandas as pd
import joblib

df = pd.read_csv('/home/ec2-user/cpu_data.csv')

X = df[['CPU', 'NetworkIn', 'NetworkOut']]

scaler = joblib.load('/home/ec2-user/scaler.pkl')
model = joblib.load('/home/ec2-user/isolation_forest_model.pkl')

X_scaled = scaler.transform(X)

df['anomaly'] = model.predict(X_scaled)

def calcular_severidad(row):
    cpu = row['CPU']

    if cpu >= 80:
        return 3
    elif cpu >= 50:
        return 2
    elif row['anomaly'] == -1:
        return 1
    else:
        return 0

df['severity'] = df.apply(calcular_severidad, axis=1)

def calcular_anomalia_final(row):
    if row['anomaly'] == -1 or row['severity'] > 0:
        return -1
    else:
        return 1

df['final_anomaly'] = df.apply(calcular_anomalia_final, axis=1)

df.to_csv('/home/ec2-user/cpu_data.csv', index=False)

print(df)
