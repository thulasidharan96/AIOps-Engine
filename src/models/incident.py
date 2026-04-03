import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Text, JSON
from src.memory.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    status = Column(String, default="open", index=True) # open, resolving, resolved, failed
    severity = Column(String) # low, medium, high, critical
    source = Column(String) # loki, prometheus
    details = Column(JSON) # raw evidence
    
    # AI Analysis & Remediation
    root_cause_analysis = Column(Text, nullable=True)
    suggested_action = Column(String, nullable=True)
    remediation_status = Column(String, nullable=True)
    remediation_log = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
