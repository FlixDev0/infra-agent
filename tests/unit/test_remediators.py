# Tests de remediadores — se implementan en semana 4
# Por ahora validan que el registro esté completo

from agent.remediator.registry import get_handler
from models.drift import DriftType


def test_todos_los_drift_types_tienen_handler():
    tipos_con_handler = [
        DriftType.SERVICE_DOWN,
        DriftType.WRONG_REPLICAS,
        DriftType.PORT_MISMATCH,
        DriftType.ENV_MISMATCH,
        DriftType.UNKNOWN_CONTAINER,
    ]
    for tipo in tipos_con_handler:
        assert get_handler(tipo) is not None, f"Sin handler para {tipo}"
