from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class ObservedPort(BaseModel):
    host: int
    container: int


class ObservedService(BaseModel):
    name: str
    status: Literal["running", "stopped", "degraded", "unknown"]
    image: str
    replicas_running: int
    ports: list[ObservedPort]
    env: dict[str, str]
    cpu_usage: float
    memory_usage_mb: float
    observed_at: datetime


class InfraSnapshot(BaseModel):
    environment: str
    observed_at: datetime
    services: list[ObservedService]
    unknown_containers: list[str]
