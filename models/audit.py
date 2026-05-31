from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from models.drift import DriftEvent


class RemediationResult(str, Enum):
    SUCCESS = "success"
    FAILED  = "failed"
    SKIPPED = "skipped"


class AuditEntry(BaseModel):
    id: str
    drift: DriftEvent
    result: RemediationResult
    attempts: int
    duration_ms: int
    error_message: str | None = None
    executed_at: datetime
    executed_by: str = "agent"
