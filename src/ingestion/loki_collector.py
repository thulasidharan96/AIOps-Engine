from typing import List
from src.schemas.incident import LogEntry, IncidentCreate
from src.detection.analyzer import AnomalyDetector

class LokiCollector:
    def __init__(self, anomaly_detector: AnomalyDetector):
        self.anomaly_detector = anomaly_detector

    async def ingest_logs(self, logs: List[LogEntry]) -> List[IncidentCreate]:
        new_incidents = []
        for log in logs:
            if self.anomaly_detector.detect_log_anomaly(log):
                incident = IncidentCreate(
                    source="loki",
                    severity="high" if log.level == "CRITICAL" else "medium",
                    details={"log_message": log.message, "service": log.service, "metadata": log.metadata}
                )
                new_incidents.append(incident)
        return new_incidents
