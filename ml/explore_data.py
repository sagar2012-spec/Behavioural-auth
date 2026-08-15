import pandas as pd

data = pd.read_csv("DSL-StrongPasswordData.csv")

print("Shape (rows, columns):", data.shape)
print("\nFirst few column names:")
print(list(data.columns)[:10])
print("\nHow many different users:")
print(data["subject"].nunique())
print("\nFirst 3 rows:")
print(data.head(3))