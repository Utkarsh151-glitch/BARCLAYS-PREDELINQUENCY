import json
from pathlib import Path
from typing import Dict

ROOT_DIR = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT_DIR / "ml" / "metrics.json"


def get_model_metrics() -> Dict:
    # Metrics are computed offline by ml/evaluate_model.py on the hold-out split and stored in
    # ml/metrics.json, so the endpoint stays cheap on the free tier without hard-coding numbers.
    return json.loads(METRICS_PATH.read_text())
