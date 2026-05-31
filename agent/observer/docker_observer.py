"""
Observer para Docker Engine.
Requiere que el daemon de Docker esté corriendo y accesible.
"""
from datetime import datetime
import docker
from docker.errors import DockerException

from agent.observer.base import BaseObserver
from models.snapshot import InfraSnapshot, ObservedService, ObservedPort


class DockerObserver(BaseObserver):
    def __init__(self, environment: str = "local"):
        self.environment = environment
        self._client = docker.from_env()

    async def observe(self) -> InfraSnapshot:
        try:
            containers = self._client.containers.list(all=True)
        except DockerException as e:
            raise RuntimeError(f"No se pudo conectar a Docker: {e}")

        services: list[ObservedService] = []
        unknown: list[str] = []

        for container in containers:
            name = container.name
            status = self._map_status(container.status)
            image = container.image.tags[0] if container.image.tags else "unknown"
            ports = self._extract_ports(container.ports)
            env = self._extract_env(container.attrs.get("Config", {}).get("Env", []))

            stats = self._get_stats(container)

            services.append(ObservedService(
                name=name,
                status=status,
                image=image,
                replicas_running=1 if status == "running" else 0,
                ports=ports,
                env=env,
                cpu_usage=stats["cpu"],
                memory_usage_mb=stats["memory_mb"],
                observed_at=datetime.utcnow(),
            ))

        return InfraSnapshot(
            environment=self.environment,
            observed_at=datetime.utcnow(),
            services=services,
            unknown_containers=unknown,
        )

    def _map_status(self, docker_status: str) -> str:
        mapping = {
            "running": "running",
            "exited": "stopped",
            "paused": "degraded",
            "restarting": "degraded",
            "dead": "stopped",
        }
        return mapping.get(docker_status, "unknown")

    def _extract_ports(self, ports: dict) -> list[ObservedPort]:
        result = []
        for container_port, bindings in (ports or {}).items():
            if bindings:
                for binding in bindings:
                    result.append(ObservedPort(
                        host=int(binding["HostPort"]),
                        container=int(container_port.split("/")[0]),
                    ))
        return result

    def _extract_env(self, env_list: list[str]) -> dict[str, str]:
        result = {}
        for item in env_list:
            if "=" in item:
                key, _, value = item.partition("=")
                result[key] = value
        return result

    def _get_stats(self, container) -> dict:
        try:
            stats = container.stats(stream=False)
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                        stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                           stats["precpu_stats"]["system_cpu_usage"]
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            memory_mb = stats["memory_stats"].get("usage", 0) / (1024 * 1024)
            return {"cpu": round(cpu_percent, 2), "memory_mb": round(memory_mb, 2)}
        except Exception:
            return {"cpu": 0.0, "memory_mb": 0.0}
