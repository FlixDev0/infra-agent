from agent.remediator.base import BaseRemediator
from models.drift import DriftEvent


class FixPortsHandler(BaseRemediator):
    async def remediate(self, drift: DriftEvent) -> None:
        # Requiere recrear el contenedor con el puerto correcto
        print(f"[fix_ports] Recreando '{drift.service_name}' con puertos correctos.")
