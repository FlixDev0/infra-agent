import json
import uuid
from datetime import datetime
from pathlib import Path

from models.audit import AuditEntry, RemediationResult
from models.drift import DriftEvent


AUDIT_LOG_PATH = Path("logs/audit.jsonl")


class AuditLogger:
    def __init__(self, log_path: Path = AUDIT_LOG_PATH):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        drift: DriftEvent,
        result: RemediationResult,
        attempts: int,
        duration_ms: int,
        error_message: str | None = None,
    ) -> AuditEntry:
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            drift=drift,
            result=result,
            attempts=attempts,
            duration_ms=duration_ms,
            error_message=error_message,
            executed_at=datetime.utcnow(),
        )
        with open(self.log_path, "a") as f:
            f.write(entry.model_dump_json() + "\n")
        return entry

    def read_all(self) -> list[AuditEntry]:
        if not self.log_path.exists():
            return []
        entries = []
        with open(self.log_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(AuditEntry.model_validate_json(line))
        return entries
