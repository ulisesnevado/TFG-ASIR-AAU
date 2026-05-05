import pandas as pd
import joblib

CSV_PATH = '/home/ubuntu/cpu_data.csv'
MODEL_PATH = '/home/ubuntu/isolation_forest_model.pkl'
SCALER_PATH = '/home/ubuntu/scaler.pkl'

df = pd.read_csv(CSV_PATH)

X = df[['CPU', 'NetworkIn', 'NetworkOut']]

scaler = joblib.load(SCALER_PATH)
model = joblib.load(MODEL_PATH)

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

df.to_csv(CSV_PATH, index=False)

print(df)
