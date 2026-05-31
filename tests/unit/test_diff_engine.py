import pytest
from datetime import datetime
from agent.diff.engine import DiffEngine
from models.drift import DriftType, DriftSeverity
from models.snapshot import InfraSnapshot, ObservedPort


@pytest.fixture
def engine():
    return DiffEngine()


class TestSinDesviaciones:
    def test_infraestructura_saludable_no_genera_eventos(self, engine, desired_state, healthy_snapshot):
        events = engine.compute(desired_state, healthy_snapshot)
        assert events == []


class TestServiceDown:
    def test_servicio_ausente_es_critical(self, engine, desired_state):
        snapshot = InfraSnapshot(
            environment="staging",
            observed_at=datetime.utcnow(),
            services=[],
            unknown_containers=[],
        )
        events = engine.compute(desired_state, snapshot)
        assert len(events) == 1
        assert events[0].drift_type == DriftType.SERVICE_DOWN
        assert events[0].severity == DriftSeverity.CRITICAL

    def test_servicio_detenido_es_critical(self, engine, desired_state, base_observed):
        base_observed.status = "stopped"
        snapshot = InfraSnapshot(
            environment="staging", observed_at=datetime.utcnow(),
            services=[base_observed], unknown_containers=[],
        )
        events = engine.compute(desired_state, snapshot)
        assert any(e.drift_type == DriftType.SERVICE_DOWN for e in events)


class TestWrongReplicas:
    def test_replicas_insuficientes_genera_evento(self, engine, desired_state, base_observed):
        base_observed.replicas_running = 1
        snapshot = InfraSnapshot(
            environment="staging", observed_at=datetime.utcnow(),
            services=[base_observed], unknown_containers=[],
        )
        events = engine.compute(desired_state, snapshot)
        replica_events = [e for e in events if e.drift_type == DriftType.WRONG_REPLICAS]
        assert len(replica_events) == 1
        assert replica_events[0].expected == "2"
        assert replica_events[0].actual == "1"

    def test_replicas_correctas_sin_evento(self, engine, desired_state, healthy_snapshot):
        events = engine.compute(desired_state, healthy_snapshot)
        assert not any(e.drift_type == DriftType.WRONG_REPLICAS for e in events)


class TestPortMismatch:
    def test_puerto_faltante_genera_evento(self, engine, desired_state, base_observed):
        base_observed.ports = []
        snapshot = InfraSnapshot(
            environment="staging", observed_at=datetime.utcnow(),
            services=[base_observed], unknown_containers=[],
        )
        events = engine.compute(desired_state, snapshot)
        assert any(e.drift_type == DriftType.PORT_MISMATCH for e in events)

    def test_puerto_incorrecto_genera_evento(self, engine, desired_state, base_observed):
        base_observed.ports = [ObservedPort(host=8080, container=9999)]
        snapshot = InfraSnapshot(
            environment="staging", observed_at=datetime.utcnow(),
            services=[base_observed], unknown_containers=[],
        )
        events = engine.compute(desired_state, snapshot)
        port_events = [e for e in events if e.drift_type == DriftType.PORT_MISMATCH]
        assert len(port_events) == 1
        assert "9999" in port_events[0].actual


class TestUnknownContainer:
    def test_contenedor_no_declarado_genera_evento(self, engine, desired_state, healthy_snapshot):
        healthy_snapshot.unknown_containers = ["spy-container"]
        events = engine.compute(desired_state, healthy_snapshot)
        unknown_events = [e for e in events if e.drift_type == DriftType.UNKNOWN_CONTAINER]
        assert len(unknown_events) == 1
        assert unknown_events[0].service_name == "spy-container"

    def test_politica_permisiva_ignora_desconocidos(self, engine, desired_state, healthy_snapshot):
        desired_state.policies.allow_unknown_containers = True
        healthy_snapshot.unknown_containers = ["spy-container"]
        events = engine.compute(desired_state, healthy_snapshot)
        assert not any(e.drift_type == DriftType.UNKNOWN_CONTAINER for e in events)


class TestOrdenSeveridad:
    def test_critical_siempre_primero(self, engine, desired_state, base_observed):
        base_observed.status = "stopped"
        snapshot = InfraSnapshot(
            environment="staging", observed_at=datetime.utcnow(),
            services=[base_observed], unknown_containers=["intruder"],
        )
        events = engine.compute(desired_state, snapshot)
        severities = [e.severity for e in events]
        seen_non_critical = False
        for s in severities:
            if s != DriftSeverity.CRITICAL:
                seen_non_critical = True
            if seen_non_critical and s == DriftSeverity.CRITICAL:
                pytest.fail("CRITICAL apareció después de un evento menos severo")
