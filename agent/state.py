"""
Estado global compartido entre el AgentLoop y la API.
"""

from datetime import datetime
from models.drift import DriftEvent
from models.audit import AuditEntry


class AgentState:
    def __init__(self):
        self.running: bool = False
        self.dry_run: bool = True
        self.interval_seconds: int = 30
        self.last_tick: datetime | None = None
        self.current_drifts: list[DriftEvent] = []
        self.total_remediations: int = 0

    def update_tick(self, drifts: list[DriftEvent]):
        self.last_tick = datetime.utcnow()
        self.current_drifts = drifts

    def to_dict(self) -> dict:
        return {
            "running": self.running,
            "dry_run": self.dry_run,
            "interval_seconds": self.interval_seconds,
            "last_tick": self.last_tick.isoformat() if self.last_tick else None,
            "active_drifts": len(self.current_drifts),
            "total_remediations": self.total_remediations,
        }


# Singleton global
agent_state = AgentState()