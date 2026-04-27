import pandas as pd

df = pd.read_csv("cpu_data.csv")

print("Dataset cargado correctamente")
print(df)
print("\nResumen:")
print(df.describe())
