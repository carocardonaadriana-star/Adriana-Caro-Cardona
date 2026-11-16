"""
entidad.py
----------
Clase abstracta Entidad: base de todos los objetos del sistema
(clientes, servicios y reservas).
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Entidad(ABC):
    """Entidad general con identificador único y fecha de creación."""

    _contadores: dict = {}  # un contador independiente por prefijo

    def __init__(self, prefijo: str):
        numero = Entidad._contadores.get(prefijo, 0) + 1
        Entidad._contadores[prefijo] = numero
        self.__id = f"{prefijo}-{numero:03d}"          # atributo privado
        self.__fecha_creacion = datetime.now()

    # --- Encapsulación: solo lectura ---------------------------------
    @property
    def id(self) -> str:
        return self.__id

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    # --- Contrato obligatorio para las subclases ---------------------
    @abstractmethod
    def validar(self) -> bool:
        """Verifica que el objeto esté en un estado consistente."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible del objeto."""

    def __str__(self) -> str:
        return self.describir()
