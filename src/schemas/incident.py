from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str
    service: str
    metadata: Optional[Dict[str, Any]] = None

class MetricEntry(BaseModel):
    timestamp: datetime
    metric_name: str
    value: float
    service: str
    labels: Optional[Dict[str, str]] = None

class IncidentCreate(BaseModel):
    source: str
    severity: str
    details: Dict[str, Any]

class IncidentResponse(BaseModel):
    id: str
    status: str
    severity: str
    source: str
    root_cause_analysis: Optional[str]
    suggested_action: Optional[str]
    remediation_status: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RemediationRequest(BaseModel):
    incident_id: str
    action_command: str
    force: bool = False
