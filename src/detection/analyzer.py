from src.schemas.incident import LogEntry, MetricEntry

class AnomalyDetector:
    def __init__(self):
        # A simple configuration for mock thresholds
        self.thresholds = {
            "cpu_usage_percent": 85.0,
            "memory_usage_bytes": 1024 * 1024 * 1024 * 2 # 2GB
        }

    def detect_log_anomaly(self, log: LogEntry) -> bool:
        """
        Detect anomalies using simple static rules and keyword matching.
        """
        critical_keywords = ["exception", "error", "panic", "timeout", "segfault", "oom"]
        
        if log.level in ["ERROR", "CRITICAL", "FATAL"]:
            return True
            
        if any(keyword in log.message.lower() for keyword in critical_keywords):
            return True
            
        return False

    def detect_metric_anomaly(self, metric: MetricEntry) -> bool:
        """
        Statistically detect metric anomalies. 
        For MVP, implemented as threshold matching.
        """
        if metric.metric_name in self.thresholds:
            if metric.value >= self.thresholds[metric.metric_name]:
                return True
        elif metric.metric_name == "error_rate" and metric.value > 0.05:
            return True
            
        return False
