from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.config.settings import settings
from src.memory.database import engine, Base, get_db_session
from src.schemas.incident import LogEntry, MetricEntry, IncidentResponse, RemediationRequest
from src.repositories.incident_repo import IncidentRepository
from src.detection.analyzer import AnomalyDetector
from src.ingestion.loki_collector import LokiCollector
from src.ingestion.prom_collector import PrometheusCollector
from src.decision.reasoner import LLMReasoner
from src.execution.k8s_executor import K8sExecutor
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Mount Static Files for UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=FileResponse)
async def serve_dashboard():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Dependency initializations
anomaly_detector = AnomalyDetector()
loki_collector = LokiCollector(anomaly_detector)
prom_collector = PrometheusCollector(anomaly_detector)
llm_reasoner = LLMReasoner()
executor = K8sExecutor()

@app.on_event("startup")
async def startup_event():
    # In production, use alembic. Doing this for IDE sim.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/ingest/logs", response_model=List[IncidentResponse])
async def ingest_logs(logs: List[LogEntry], session: AsyncSession = Depends(get_db_session)):
    incidents_data = await loki_collector.ingest_logs(logs)
    repo = IncidentRepository(session)
    
    created_incidents = []
    for data in incidents_data:
        incident = await repo.create_incident(data)
        created_incidents.append(incident)
        
    return created_incidents

@app.post("/ingest/metrics", response_model=List[IncidentResponse])
async def ingest_metrics(metrics: List[MetricEntry], session: AsyncSession = Depends(get_db_session)):
    incidents_data = await prom_collector.ingest_metrics(metrics)
    repo = IncidentRepository(session)
    
    created_incidents = []
    for data in incidents_data:
        incident = await repo.create_incident(data)
        created_incidents.append(incident)
        
    return created_incidents

@app.get("/incidents", response_model=List[IncidentResponse])
async def get_incidents(limit: int = 100, session: AsyncSession = Depends(get_db_session)):
    repo = IncidentRepository(session)
    return await repo.get_all_incidents(limit)

@app.get("/anomalies", response_model=List[IncidentResponse])
async def get_anomalies(session: AsyncSession = Depends(get_db_session)):
    # Simulating anomalies as open incidents
    repo = IncidentRepository(session)
    # Ideally filter by status="open"
    all_inc = await repo.get_all_incidents()
    return [i for i in all_inc if i.status == "open"]

@app.post("/analyze/{incident_id}", response_model=IncidentResponse)
async def analyze_incident(incident_id: str, session: AsyncSession = Depends(get_db_session)):
    repo = IncidentRepository(session)
    incident = await repo.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    await llm_reasoner.analyze_incident(incident)
    await repo.update_incident(incident)
    
    return incident

@app.post("/execute", response_model=IncidentResponse)
async def execute_remediation(request: RemediationRequest, session: AsyncSession = Depends(get_db_session)):
    repo = IncidentRepository(session)
    incident = await repo.get_incident(request.incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    result_log = await executor.execute_action(request)
    
    incident.remediation_log = result_log
    if "failed" in result_log.lower() or "rejected" in result_log.lower() or "deferred" in result_log.lower():
        incident.remediation_status = "failed or pending"
    else:
        incident.remediation_status = "success"
        incident.status = "resolved"
        
    await repo.update_incident(incident)
    
    return incident
