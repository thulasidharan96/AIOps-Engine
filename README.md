# AIOps Engine

A production-grade AI-powered DevOps Autonomous Platform. 

## Overview
This platform:
1. Ingests logs, metrics, and traces
2. Detects anomalies using rules and statistical limits.
3. Uses an LLM to reason about anomalies and suggest remediations.
4. Safely auto-remediates via a Kubernetes Executor.
5. Maintains a historical memory of incidents in PostgreSQL.

## Architecture

![Architecture](https://via.placeholder.com/800x400?text=AIOps+Architecture)

### Data Flow
`Prometheus/Loki` -> `Ingestion Layer` -> `Anomaly Detector` -> `Incident DB (Open)` -> `/analyze (LLM RCA)` -> `/execute (K8s Automation)`

## Getting Started

1. Set up the Configuration
```bash
# Copy the sample environment variables
cp .env.sample .env
```
*(By default, `.env` uses `ENVIRONMENT=development` which delegates LLM requests to local Ollama instead of OpenAI).*

2. Environment (uv)
```powershell
# Provide python 3.12+ 
uv venv

# For Windows / PowerShell:
& ".venv\Scripts\Activate.ps1"
# For Linux / macOS:
# source .venv/bin/activate

make install
```

3. Services
```bash
# Start required backing stores (Postgres & Redis)
make docker-up
```

# Run application
make run
```

## API Usage

### Ingest Logs
```bash
curl -X POST http://localhost:8000/ingest/logs -H "Content-Type: application/json" -d '[
  {
    "timestamp": "2026-04-03T22:00:00Z",
    "level": "CRITICAL",
    "message": "Out of memory gracefully shutting down",
    "service": "billing-service"
  }
]'
```

### Analyze Incident (LLM)
```bash
curl -X POST http://localhost:8000/analyze/<incident-id>
```

### Execute Remediation
```bash
curl -X POST http://localhost:8000/execute -H "Content-Type: application/json" -d '{
  "incident_id": "<incident-id>",
  "action_command": "kubectl restart pod",
  "force": true
}'
```

## Safety Model & Auto-Remediation
- Auto-execution is controlled via `AUTO_EXECUTE_ENABLED` and `APPROVAL_MODE` environment variables.
- When `APPROVAL_MODE=True`, all `/execute` endpoint calls mandate `force: true` to acknowledge manual sign-off.
- The K8s executor records full history to `remediation_log` within the Incident DB for cross-referencing and RBAC auditing.
