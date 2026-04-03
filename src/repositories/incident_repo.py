from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from src.models.incident import Incident
from src.schemas.incident import IncidentCreate

class IncidentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_incident(self, incident_in: IncidentCreate) -> Incident:
        db_incident = Incident(
            source=incident_in.source,
            severity=incident_in.severity,
            details=incident_in.details,
            status="open"
        )
        self.session.add(db_incident)
        await self.session.commit()
        await self.session.refresh(db_incident)
        return db_incident

    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        result = await self.session.execute(select(Incident).where(Incident.id == incident_id))
        return result.scalars().first()

    async def get_all_incidents(self, limit: int = 100) -> List[Incident]:
        result = await self.session.execute(select(Incident).order_by(Incident.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def update_incident(self, incident: Incident) -> Incident:
        self.session.add(incident)
        await self.session.commit()
        await self.session.refresh(incident)
        return incident
