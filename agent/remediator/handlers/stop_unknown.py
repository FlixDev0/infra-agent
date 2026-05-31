import docker
from agent.remediator.base import BaseRemediator
from models.drift import DriftEvent


class StopUnknownHandler(BaseRemediator):
    async def remediate(self, drift: DriftEvent) -> None:
        client = docker.from_env()
        try:
            container = client.containers.get(drift.service_name)
            container.stop()
            print(f"[stop_unknown] Detenido contenedor no declarado: '{drift.service_name}'")
        except docker.errors.NotFound:
            print(f"[stop_unknown] Contenedor '{drift.service_name}' ya no existe.")
