from datetime import datetime
from models.desired_state import ServiceSpec
from models.snapshot import ObservedService
from models.drift import DriftEvent, DriftType, DriftSeverity
from .base import DriftRule


class ImageMismatchRule(DriftRule):
    def evaluate(self, spec: ServiceSpec, observed: ObservedService | None) -> list[DriftEvent]:
        if observed is None:
            return []
        if observed.image != spec.image:
            return [DriftEvent(
                service_name=spec.name,
                drift_type=DriftType.IMAGE_MISMATCH,
                severity=DriftSeverity.HIGH,
                expected=spec.image,
                actual=observed.image,
                detected_at=datetime.utcnow(),
                remediation_action=f"Recrear '{spec.name}' con imagen {spec.image}",
            )]
        return []
