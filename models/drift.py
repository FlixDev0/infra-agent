from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class DriftType(str, Enum):
    SERVICE_DOWN       = "service_down"
    WRONG_REPLICAS     = "wrong_replicas"
    PORT_MISMATCH      = "port_mismatch"
    ENV_MISMATCH       = "env_mismatch"
    UNKNOWN_CONTAINER  = "unknown_container"
    RESOURCE_EXCEEDED  = "resource_exceeded"
    IMAGE_MISMATCH     = "image_mismatch"


class DriftSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"


class DriftEvent(BaseModel):
    service_name: str
    drift_type: DriftType
    severity: DriftSeverity
    expected: str
    actual: str
    detected_at: datetime
    remediation_action: str
