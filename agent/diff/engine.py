from models.desired_state import DesiredState
from models.snapshot import InfraSnapshot
from models.drift import DriftEvent, DriftType, DriftSeverity
from datetime import datetime

from agent.diff.rules.service_down import ServiceDownRule
from agent.diff.rules.wrong_replicas import WrongReplicasRule
from agent.diff.rules.port_mismatch import PortMismatchRule
from agent.diff.rules.env_mismatch import EnvMismatchRule
from agent.diff.rules.image_mismatch import ImageMismatchRule

SEVERITY_ORDER = {
    DriftSeverity.CRITICAL: 0,
    DriftSeverity.HIGH: 1,
    DriftSeverity.MEDIUM: 2,
    DriftSeverity.LOW: 3,
}


class DiffEngine:
    def __init__(self):
        self.rules = [
            ServiceDownRule(),
            WrongReplicasRule(),
            PortMismatchRule(),
            EnvMismatchRule(),
            ImageMismatchRule(),
        ]

    def compute(self, desired: DesiredState, snapshot: InfraSnapshot) -> list[DriftEvent]:
        events: list[DriftEvent] = []
        observed_index = {s.name: s for s in snapshot.services}

        for spec in desired.services:
            observed = observed_index.get(spec.name)
            for rule in self.rules:
                events.extend(rule.evaluate(spec, observed))

        if not desired.policies.allow_unknown_containers:
            declared_names = {s.name for s in desired.services}
            for unknown in snapshot.unknown_containers:
                if unknown not in declared_names:
                    events.append(DriftEvent(
                        service_name=unknown,
                        drift_type=DriftType.UNKNOWN_CONTAINER,
                        severity=DriftSeverity.MEDIUM,
                        expected="not running",
                        actual="running",
                        detected_at=datetime.utcnow(),
                        remediation_action=f"Detener contenedor no declarado '{unknown}'",
                    ))

        events.sort(key=lambda e: SEVERITY_ORDER[e.severity])
        return events
