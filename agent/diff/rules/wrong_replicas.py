from datetime import datetime
from models.desired_state import ServiceSpec
from models.snapshot import ObservedService
from models.drift import DriftEvent, DriftType, DriftSeverity
from .base import DriftRule


class WrongReplicasRule(DriftRule):
    def evaluate(self, spec: ServiceSpec, observed: ObservedService | None) -> list[DriftEvent]:
        if observed is None:
            return []
        if observed.replicas_running != spec.replicas:
            deficit = spec.replicas - observed.replicas_running
            severity = (
                DriftSeverity.CRITICAL if observed.replicas_running == 0
                else DriftSeverity.HIGH if deficit > 1
                else DriftSeverity.MEDIUM
            )
            return [DriftEvent(
                service_name=spec.name,
                drift_type=DriftType.WRONG_REPLICAS,
                severity=severity,
                expected=str(spec.replicas),
                actual=str(observed.replicas_running),
                detected_at=datetime.utcnow(),
                remediation_action=f"Escalar '{spec.name}': {observed.replicas_running} → {spec.replicas} réplicas",
            )]
        return []
