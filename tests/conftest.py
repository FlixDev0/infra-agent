import pytest
from datetime import datetime
from models.desired_state import DesiredState, ServiceSpec, PortMapping, Policies
from models.snapshot import InfraSnapshot, ObservedService, ObservedPort


@pytest.fixture
def base_spec() -> ServiceSpec:
    return ServiceSpec(
        name="api-backend",
        type="container",
        image="myapp:latest",
        replicas=2,
        ports=[PortMapping(host=8080, container=80)],
        env={"DEBUG": "false", "PORT": "80"},
    )


@pytest.fixture
def base_observed() -> ObservedService:
    return ObservedService(
        name="api-backend",
        status="running",
        image="myapp:latest",
        replicas_running=2,
        ports=[ObservedPort(host=8080, container=80)],
        env={"DEBUG": "false", "PORT": "80"},
        cpu_usage=10.0,
        memory_usage_mb=128.0,
        observed_at=datetime.utcnow(),
    )


@pytest.fixture
def healthy_snapshot(base_observed) -> InfraSnapshot:
    return InfraSnapshot(
        environment="staging",
        observed_at=datetime.utcnow(),
        services=[base_observed],
        unknown_containers=[],
    )


@pytest.fixture
def desired_state(base_spec) -> DesiredState:
    return DesiredState(
        version="1.0",
        environment="staging",
        services=[base_spec],
        policies=Policies(allow_unknown_containers=False),
    )
