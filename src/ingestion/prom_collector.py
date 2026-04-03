from typing import List
from src.schemas.incident import MetricEntry, IncidentCreate
from src.detection.analyzer import AnomalyDetector

class PrometheusCollector:
    def __init__(self, anomaly_detector: AnomalyDetector):
        self.anomaly_detector = anomaly_detector

    async def ingest_metrics(self, metrics: List[MetricEntry]) -> List[IncidentCreate]:
        new_incidents = []
        for metric in metrics:
            if self.anomaly_detector.detect_metric_anomaly(metric):
                incident = IncidentCreate(
                    source="prometheus",
                    severity="high",
                    details={"metric": metric.metric_name, "value": metric.value, "service": metric.service}
                )
                new_incidents.append(incident)
        return new_incidents
