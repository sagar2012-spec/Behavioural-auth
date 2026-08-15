import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

data = pd.read_csv("DSL-StrongPasswordData.csv")
feature_columns = data.columns[3:]

# test the approach across the first 10 users
users = sorted(data["subject"].unique())[:10]

genuine_scores = []
impostor_scores = []

for genuine_user in users:
    genuine = data[data["subject"] == genuine_user][feature_columns]
    impostors = data[data["subject"] != genuine_user][feature_columns]

    # shuffle and split genuine data
    genuine_shuffled = genuine.sample(frac=1, random_state=42)
    split = len(genuine_shuffled) // 2
    train = genuine_shuffled.iloc[:split]
    genuine_test = genuine_shuffled.iloc[split:]

    # scale based on the genuine training data
    scaler = StandardScaler()
    train_scaled = scaler.fit_transform(train)
    genuine_test_scaled = scaler.transform(genuine_test)
    impostor_scaled = scaler.transform(impostors)

    # train on genuine user only, using our chosen operating point
    model = OneClassSVM(gamma="scale", nu=0.05)
    model.fit(train_scaled)

    genuine_results = model.predict(genuine_test_scaled)
    impostor_results = model.predict(impostor_scaled)

    genuine_pct = (genuine_results == 1).sum() / len(genuine_results) * 100
    impostor_pct = (impostor_results == -1).sum() / len(impostor_results) * 100

    genuine_scores.append(genuine_pct)
    impostor_scores.append(impostor_pct)

    print(f"{genuine_user}: genuine accepted {genuine_pct:.1f}%, impostors rejected {impostor_pct:.1f}%")

# averages across all users
avg_genuine = sum(genuine_scores) / len(genuine_scores)
avg_impostor = sum(impostor_scores) / len(impostor_scores)
print("-" * 50)
print(f"AVERAGE across {len(users)} users: genuine accepted {avg_genuine:.1f}%, impostors rejected {avg_impostor:.1f}%")