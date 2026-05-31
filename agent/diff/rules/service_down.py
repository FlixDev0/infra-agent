from datetime import datetime
from models.desired_state import ServiceSpec
from models.snapshot import ObservedService
from models.drift import DriftEvent, DriftType, DriftSeverity
from .base import DriftRule


class ServiceDownRule(DriftRule):
    def evaluate(self, spec: ServiceSpec, observed: ObservedService | None) -> list[DriftEvent]:
        if observed is None:
            return [DriftEvent(
                service_name=spec.name,
                drift_type=DriftType.SERVICE_DOWN,
                severity=DriftSeverity.CRITICAL,
                expected="running",
                actual="not found",
                detected_at=datetime.utcnow(),
                remediation_action=f"Levantar servicio '{spec.name}' desde imagen {spec.image}",
            )]
        if observed.status in ("stopped", "degraded"):
            return [DriftEvent(
                service_name=spec.name,
                drift_type=DriftType.SERVICE_DOWN,
                severity=DriftSeverity.CRITICAL,
                expected="running",
                actual=observed.status,
                detected_at=datetime.utcnow(),
                remediation_action=f"Reiniciar servicio '{spec.name}'",
            )]
        return []
