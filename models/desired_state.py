from pydantic import BaseModel, Field
from typing import Literal


class PortMapping(BaseModel):
    host: int
    container: int


class ResourceLimits(BaseModel):
    cpu_limit: str = "1.0"
    memory_limit: str = "512m"


class HealthCheck(BaseModel):
    endpoint: str = "/health"
    interval_seconds: int = 30
    timeout_seconds: int = 5
    unhealthy_threshold: int = 3


class ServiceSpec(BaseModel):
    name: str
    type: Literal["container", "process", "cloud_instance"] = "container"
    image: str
    replicas: int = Field(default=1, ge=1)
    ports: list[PortMapping] = []
    env: dict[str, str] = {}
    resources: ResourceLimits = ResourceLimits()
    health_check: HealthCheck | None = None
    restart_policy: Literal["always", "on-failure", "never"] = "always"
    tags: dict[str, str] = {}


class Policies(BaseModel):
    allow_unknown_containers: bool = False
    max_remediation_attempts: int = 3
    remediation_cooldown_seconds: int = 60
    dry_run: bool = False


class DesiredState(BaseModel):
    version: str
    environment: str
    services: list[ServiceSpec]
    policies: Policies = Policies()
