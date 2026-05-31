from abc import ABC, abstractmethod
from models.drift import DriftEvent


class BaseRemediator(ABC):
    """Clase base para handlers de remediación."""

    @abstractmethod
    async def remediate(self, drift: DriftEvent) -> None:
        """Ejecuta la acción correctiva para un DriftEvent."""
        ...
