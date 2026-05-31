from abc import ABC, abstractmethod
from models.desired_state import ServiceSpec
from models.snapshot import ObservedService
from models.drift import DriftEvent


class DriftRule(ABC):
    """Clase base — cada regla sabe detectar un tipo específico de desviación."""

    @abstractmethod
    def evaluate(
        self,
        spec: ServiceSpec,
        observed: ObservedService | None,
    ) -> list[DriftEvent]:
        """Retorna lista de DriftEvents. Lista vacía = sin desviación."""
        ...
