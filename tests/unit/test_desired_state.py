import pytest
from pydantic import ValidationError
from models.desired_state import DesiredState, ServiceSpec, PortMapping, Policies


class TestServiceSpec:
    def test_spec_valida_crea_correctamente(self):
        spec = ServiceSpec(name="web", image="nginx:latest", replicas=1)
        assert spec.name == "web"
        assert spec.restart_policy == "always"

    def test_replicas_minimo_uno(self):
        with pytest.raises(ValidationError):
            ServiceSpec(name="web", image="nginx:latest", replicas=0)

    def test_tipo_invalido_falla(self):
        with pytest.raises(ValidationError):
            ServiceSpec(name="web", image="nginx:latest", type="inexistente")


class TestDesiredState:
    def test_desired_state_valido(self):
        ds = DesiredState(
            version="1.0",
            environment="staging",
            services=[ServiceSpec(name="web", image="nginx:latest")],
        )
        assert ds.environment == "staging"
        assert len(ds.services) == 1

    def test_policies_por_defecto(self):
        ds = DesiredState(
            version="1.0",
            environment="prod",
            services=[],
        )
        assert ds.policies.dry_run is False
        assert ds.policies.max_remediation_attempts == 3

    def test_sin_servicios_es_valido(self):
        ds = DesiredState(version="1.0", environment="test", services=[])
        assert ds.services == []
