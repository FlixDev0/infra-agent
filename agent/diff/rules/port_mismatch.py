from datetime import datetime
from models.desired_state import ServiceSpec
from models.snapshot import ObservedService
from models.drift import DriftEvent, DriftType, DriftSeverity
from .base import DriftRule


class PortMismatchRule(DriftRule):
    def evaluate(self, spec: ServiceSpec, observed: ObservedService | None) -> list[DriftEvent]:
        if observed is None:
            return []
        expected = {p.host: p.container for p in spec.ports}
        actual   = {p.host: p.container for p in observed.ports}
        events = []
        for host_port, container_port in expected.items():
            if host_port not in actual:
                events.append(DriftEvent(
                    service_name=spec.name,
                    drift_type=DriftType.PORT_MISMATCH,
                    severity=DriftSeverity.HIGH,
                    expected=f"{host_port}:{container_port}",
                    actual="not mapped",
                    detected_at=datetime.utcnow(),
                    remediation_action=f"Recrear '{spec.name}' con puerto {host_port}:{container_port}",
                ))
            elif actual[host_port] != container_port:
                events.append(DriftEvent(
                    service_name=spec.name,
                    drift_type=DriftType.PORT_MISMATCH,
                    severity=DriftSeverity.HIGH,
                    expected=f"{host_port}:{container_port}",
                    actual=f"{host_port}:{actual[host_port]}",
                    detected_at=datetime.utcnow(),
                    remediation_action=f"Recrear '{spec.name}' con puerto correcto",
                ))
        return events
