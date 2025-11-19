from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BaseAdapter(ABC):
    """
    Clase base para todos los adaptadores de IA en el Orquestador.
    Todos los adaptadores deben implementar el método 'process'.
    """

    @abstractmethod
    async def process(
        self,
        prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Procesa un mensaje y devuelve una respuesta en texto.
        Este método debe ser implementado por cada adaptador específico.
        """
        pass
