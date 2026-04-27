import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('/home/ec2-user/cpu_data.csv')

X = df[['CPU', 'NetworkIn', 'NetworkOut']]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_scaled)

joblib.dump(model, '/home/ec2-user/isolation_forest_model.pkl')
joblib.dump(scaler, '/home/ec2-user/scaler.pkl')

print("Modelo y scaler guardados correctamente")
