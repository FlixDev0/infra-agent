from agent.remediator.base import BaseRemediator
from models.drift import DriftEvent


class ScaleReplicasHandler(BaseRemediator):
    async def remediate(self, drift: DriftEvent) -> None:
        # TODO: implementar lógica de scaling (Docker Compose / Swarm / K8s)
        print(f"[scale] Ajustando réplicas de '{drift.service_name}': {drift.actual} → {drift.expected}")
