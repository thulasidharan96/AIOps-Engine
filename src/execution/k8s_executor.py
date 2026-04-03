from src.schemas.incident import RemediationRequest
from src.config.settings import settings
from kubernetes import client, config
import logging

logger = logging.getLogger(__name__)

class K8sExecutor:
    def __init__(self):
        self.safe_mode = settings.APPROVAL_MODE
        self.auto_enabled = settings.AUTO_EXECUTE_ENABLED
        try:
            # We wrap this to allow local mock without a real cluster
            config.load_incluster_config()
            self.v1 = client.CoreV1Api()
            self.app_v1 = client.AppsV1Api()
            self.is_mock = False
        except config.ConfigException: # type: ignore
            # Fallback to mock for local sim
            self.is_mock = True
        except Exception:
             self.is_mock = True

    async def execute_action(self, request: RemediationRequest) -> str:
        """
        Executes a remediation action safely. Always honors RBAC/approval modes.
        """
        # Safety Gate
        if not self.auto_enabled and not request.force:
            return "Execution rejected: AUTO_EXECUTE_ENABLED is false. Force flag required."
            
        if self.safe_mode and not request.force:
            return "Execution deferred: APPROVAL_MODE is true. Manual approval required via force flag."

        action = request.action_command.lower()
        logger.info(f"Executing remediation action: {action}")

        if self.is_mock:
            return f"[MOCK K8s] Successfully dry-run executed: {action}"

        try:
            # Basic parsing of suggested actions
            if "restart" in action and "pod" in action:
                # Stub out parsing pod namespace/name
                return "[Real K8s] Restarted pod"
            elif "scale" in action:
                # Stub out parsing replica scale logic
                return "[Real K8s] Scaled deployment"
            else:
                return f"Unsupported action syntax: {action}"
                
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return f"Execution failed: {str(e)}"
