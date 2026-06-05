from models.drift import DriftType
from agent.remediator.base import BaseRemediator
from agent.remediator.handlers.restart_service import RestartServiceHandler
from agent.remediator.handlers.scale_replicas import ScaleReplicasHandler
from agent.remediator.handlers.fix_ports import FixPortsHandler
from agent.remediator.handlers.fix_env import FixEnvHandler
from agent.remediator.handlers.fix_image import FixImageHandler
from agent.remediator.handlers.stop_unknown import StopUnknownHandler


REGISTRY: dict[DriftType, BaseRemediator] = {
    DriftType.SERVICE_DOWN:      RestartServiceHandler(),
    DriftType.WRONG_REPLICAS:    ScaleReplicasHandler(),
    DriftType.PORT_MISMATCH:     FixPortsHandler(),
    DriftType.ENV_MISMATCH:      FixEnvHandler(),
    DriftType.IMAGE_MISMATCH:    FixImageHandler(),
    DriftType.UNKNOWN_CONTAINER: StopUnknownHandler(),
}

def get_handler(drift_type: DriftType) -> BaseRemediator | None:
    return REGISTRY.get(drift_type)