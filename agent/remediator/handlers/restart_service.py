import docker
from agent.remediator.base import BaseRemediator
from models.drift import DriftEvent


class RestartServiceHandler(BaseRemediator):
    async def remediate(self, drift: DriftEvent) -> None:
        client = docker.from_env()
        try:
            container = client.containers.get(drift.service_name)
            container.restart()
        except docker.errors.NotFound:
            # TODO: levantar desde imagen usando desired state
            print(f"[restart] Contenedor '{drift.service_name}' no encontrado para reiniciar.")
