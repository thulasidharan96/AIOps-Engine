from openai import AsyncOpenAI
import json
from src.models.incident import Incident
from src.config.settings import settings

class LLMReasoner:
    def __init__(self):
        if settings.ENVIRONMENT == "development":
            self.client = AsyncOpenAI(base_url=f"{settings.OLLAMA_URL}/v1", api_key="ollama")
            self.model = settings.OLLAMA_MODEL
        else:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL

    async def analyze_incident(self, incident: Incident) -> None:
        """
        Analyze the incident to determine root cause and suggest action.
        Mutates the incident object in-place.
        """
        if settings.OPENAI_API_KEY == "sk-mock-key":
            self._mock_analysis(incident)
            return

        prompt = self._build_prompt(incident)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert DevOps AI assistant. Analyze the incident data and output a JSON response with 'root_cause' and 'suggested_action'. 'suggested_action' should be a valid command string or Kubernetes API operation such as 'kubectl restart deployment X', 'scale pods', or 'clear redis cache'."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            incident.root_cause_analysis = result.get("root_cause", "Analysis incomplete")
            incident.suggested_action = result.get("suggested_action", "No action suggested")
            
        except Exception as e:
            incident.root_cause_analysis = f"Failed to analyze: {str(e)}"
            incident.suggested_action = "Manual intervention required"

    def _build_prompt(self, incident: Incident) -> str:
        return f"""
        Incident ID: {incident.id}
        Source: {incident.source}
        Severity: {incident.severity}
        Details: {json.dumps(incident.details)}
        
        Please provide root cause analysis and a remediation action.
        """

    def _mock_analysis(self, incident: Incident) -> None:
        """Mock behavior for local dev without a real LLM"""
        details_str = str(incident.details).lower()
        if "cpu" in details_str:
            incident.root_cause_analysis = "CPU constraint limits hit due to high load."
            incident.suggested_action = "kubectl scale deployment --replicas=3"
        elif "memory" in details_str or "oom" in details_str:
            incident.root_cause_analysis = "Out of memory error detected in container."
            incident.suggested_action = "kubectl restart pod"
        elif "timeout" in details_str:
            incident.root_cause_analysis = "Database or remote service timeout."
            incident.suggested_action = "clear redis cache"
        else:
            incident.root_cause_analysis = "Unknown generic anomaly detected."
            incident.suggested_action = "investigate manually"
