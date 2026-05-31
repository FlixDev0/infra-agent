from abc import ABC, abstractmethod
from models.snapshot import InfraSnapshot


class BaseObserver(ABC):
    """Clase base para observadores de infraestructura."""

    @abstractmethod
    async def observe(self) -> InfraSnapshot:
        """Retorna un snapshot del estado actual de la infraestructura."""
        ...
