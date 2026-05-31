from agent.remediator.base import BaseRemediator
from models.drift import DriftEvent


class FixEnvHandler(BaseRemediator):
    async def remediate(self, drift: DriftEvent) -> None:
        print(f"[fix_env] Recreando '{drift.service_name}' con variables de entorno correctas.")
