import pickle
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(HERE, "..", "ml", "keystroke_model.pkl")

# load the trained model once when this module is imported
with open(MODEL_PATH, "rb") as f:
    saved = pickle.load(f)

model = saved["model"]
scaler = saved["scaler"]
columns = saved["columns"]


def keystroke_score(timing_values):
    """
    Takes a list of keystroke timing values (same order as training columns).
    Returns a similarity score 0-100.
    """
    scaled = scaler.transform([timing_values])
    raw = model.decision_function(scaled)[0]
    score = 60 + (raw * 100)
    score = max(0, min(100, score))
    return round(score, 1)