from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch("http://localhost:9200")


def log_prediction(record: dict):
    es.index(
        index="predelinquency_logs",
        document={
            **record,
            "logged_at": str(datetime.utcnow())
        }
    )
