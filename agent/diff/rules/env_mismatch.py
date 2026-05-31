from datetime import datetime
from models.desired_state import ServiceSpec
from models.snapshot import ObservedService
from models.drift import DriftEvent, DriftType, DriftSeverity
from .base import DriftRule

SENSITIVE_KEYS = {"PASSWORD", "SECRET", "TOKEN", "KEY", "API_KEY"}


class EnvMismatchRule(DriftRule):
    def evaluate(self, spec: ServiceSpec, observed: ObservedService | None) -> list[DriftEvent]:
        if observed is None:
            return []
        events = []
        for key, expected_val in spec.env.items():
            actual_val = observed.env.get(key)
            if actual_val is None:
                display_expected = "***" if any(s in key.upper() for s in SENSITIVE_KEYS) else expected_val
                events.append(DriftEvent(
                    service_name=spec.name,
                    drift_type=DriftType.ENV_MISMATCH,
                    severity=DriftSeverity.MEDIUM,
                    expected=f"{key}={display_expected}",
                    actual=f"{key}=missing",
                    detected_at=datetime.utcnow(),
                    remediation_action=f"Recrear '{spec.name}' con variable {key} correcta",
                ))
            elif actual_val != expected_val:
                is_sensitive = any(s in key.upper() for s in SENSITIVE_KEYS)
                events.append(DriftEvent(
                    service_name=spec.name,
                    drift_type=DriftType.ENV_MISMATCH,
                    severity=DriftSeverity.MEDIUM,
                    expected=f"{key}=***" if is_sensitive else f"{key}={expected_val}",
                    actual=f"{key}=***" if is_sensitive else f"{key}={actual_val}",
                    detected_at=datetime.utcnow(),
                    remediation_action=f"Recrear '{spec.name}' con variable {key} correcta",
                ))
        return events
