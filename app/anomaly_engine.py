import numpy as np
from pyod.models.iforest import IForest

# Train simple anomaly model (dummy fit for prototype)
anomaly_model = IForest(contamination=0.1)

# Fit on synthetic baseline data
dummy_data = np.random.randn(200, 7)
anomaly_model.fit(dummy_data)


def calculate_anomaly_score(feature_vector: list):
    """
    Calculate anomaly score using PyOD Isolation Forest.
    Higher score = more anomalous
    """
    score = anomaly_model.decision_function([feature_vector])[0]

    # Normalize score to 0–1 range
    score = abs(float(score))
    return score
