import pandas as pd
from keystroke_signal import keystroke_score, columns

data = pd.read_csv("../ml/DSL-StrongPasswordData.csv")

genuine_sample = data[data["subject"] == "s002"][columns].iloc[250].tolist()
impostor_sample = data[data["subject"] == "s020"][columns].iloc[0].tolist()

print("Genuine sample score:", keystroke_score(genuine_sample))
print("Impostor sample score:", keystroke_score(impostor_sample))