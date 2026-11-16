"""
servicios.py
------------
Clase abstracta Servicio y sus tres especializaciones:
    - ReservaSala
    - AlquilerEquipo
    - AsesoriaEspecializada

Cada subclase sobrescribe (polimorfismo):
    calcular_costo_base(), validar_parametros() y describir().
"""

import math
from abc import abstractmethod
from typing import Union, overload

from entidad import Entidad
from excepciones import (CalculoInconsistenteError, ReservaInvalidaError,
                         ServicioInvalidoError, ServicioNoDisponibleError)


def _es_numero(valor) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


class Servicio(Entidad):
    """Servicio genérico ofrecido por Software FJ (abstracto)."""

    IVA = 0.19
    UNIDAD = "horas"

    def __init__(self, nombre, tarifa_base, disponible=True):
        super().__init__("SRV")
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self._disponible = bool(disponible)

    # ---------------- propiedades validadas ----------------
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ServicioInvalidoError("El nombre del servicio debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor):
        if not _es_numero(valor) or valor <= 0:
            raise ServicioInvalidoError(f"Tarifa inválida '{valor}': debe ser un número mayor que 0.")
        self._tarifa_base = float(valor)

    @property
    def disponible(self) -> bool:
        return self._disponible

    def ocupar(self):
        if not self._disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self.nombre}' ya está ocupado.")
        self._disponible = False

    def liberar(self):
        self._disponible = True

    # ---------------- métodos abstractos (polimorfismo) ----------------
    @abstractmethod
    def calcular_costo_base(self, duracion: float) -> float:
        """Costo sin impuestos ni descuentos."""

    @abstractmethod
    def validar_parametros(self, duracion) -> None:
        """Valida la duración solicitada según el tipo de servicio."""

    # ---------------- método sobrecargado ----------------
    # Python no admite sobrecarga real; se declaran las variantes con
    # @overload (para documentación y editores) y una sola implementación
    # que decide según los argumentos recibidos.
    @overload
    def calcular_costo(self, duracion: float) -> float: ...
    @overload
    def calcular_costo(self, duracion: float, impuesto: Union[bool, float]) -> float: ...
    @overload
    def calcular_costo(self, duracion: float, impuesto: Union[bool, float],
                       descuento: float) -> float: ...

    def calcular_costo(self, duracion, impuesto=False, descuento=0.0):
        """
        Variantes:
            calcular_costo(d)                       -> costo base
            calcular_costo(d, impuesto=True)        -> base + IVA (19 %)
            calcular_costo(d, impuesto=0.08)        -> base + tasa personalizada
            calcular_costo(d, descuento=0.10)       -> base - 10 %
            calcular_costo(d, True, 0.10)           -> base - 10 % + IVA
        """
        self.validar_parametros(duracion)
        costo = self.calcular_costo_base(duracion)

        # Descuento
        if not _es_numero(descuento) or not 0 <= descuento < 1:
            raise CalculoInconsistenteError(
                f"Descuento inválido '{descuento}': debe estar entre 0 y 0.99.")
        costo *= (1 - descuento)

        # Impuesto
        if impuesto is True:
            tasa = self.IVA
        elif impuesto is False or impuesto is None:
            tasa = 0.0
        elif _es_numero(impuesto) and 0 <= impuesto <= 1:
            tasa = float(impuesto)
        else:
            raise CalculoInconsistenteError(f"Impuesto inválido '{impuesto}'.")
        costo *= (1 + tasa)

        if not math.isfinite(costo) or costo <= 0:
            raise CalculoInconsistenteError(f"Costo calculado inconsistente: {costo}.")
        return round(costo, 2)

    # ---------------- validación común ----------------
    def _validar_rango(self, duracion, minimo, maximo):
        if not _es_numero(duracion):
            raise ReservaInvalidaError(f"La duración debe ser numérica (recibido: {duracion!r}).")
        if not minimo <= duracion <= maximo:
            raise ReservaInvalidaError(
                f"Duración {duracion} {self.UNIDAD} fuera de rango para '{self.nombre}' "
                f"(permitido: {minimo}-{maximo} {self.UNIDAD}).")

    def validar(self) -> bool:
        return bool(self.nombre) and self.tarifa_base > 0


class ReservaSala(Servicio):
    """Reserva de salas por horas. Salas grandes tienen recargo del 15 %."""

    UNIDAD = "horas"

    def __init__(self, nombre, tarifa_base, capacidad, disponible=True):
        super().__init__(nombre, tarifa_base, disponible)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or not 1 <= capacidad <= 200:
            raise ServicioInvalidoError(f"Capacidad inválida '{capacidad}': entero entre 1 y 200.")
        self._capacidad = capacidad

    def validar_parametros(self, duracion):
        self._validar_rango(duracion, 1, 12)

    def calcular_costo_base(self, duracion):
        recargo = 1.15 if self._capacidad > 20 else 1.0
        return self.tarifa_base * duracion * recargo

    def describir(self):
        return (f"[{self.id}] Sala '{self.nombre}' - capacidad {self._capacidad} personas - "
                f"${self.tarifa_base:,.0f}/hora")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos por días, con depósito de garantía fijo."""

    UNIDAD = "días"

    def __init__(self, nombre, tarifa_base, tipo_equipo, deposito=0, disponible=True):
        super().__init__(nombre, tarifa_base, disponible)
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise ServicioInvalidoError("Debe indicar el tipo de equipo.")
        if not _es_numero(deposito) or deposito < 0:
            raise ServicioInvalidoError(f"Depósito inválido '{deposito}'.")
        self._tipo_equipo = tipo_equipo.strip()
        self._deposito = float(deposito)

    def validar_parametros(self, duracion):
        self._validar_rango(duracion, 1, 30)

    def calcular_costo_base(self, duracion):
        return self.tarifa_base * duracion + self._deposito

    def describir(self):
        return (f"[{self.id}] Equipo '{self.nombre}' ({self._tipo_equipo}) - "
                f"${self.tarifa_base:,.0f}/día + depósito ${self._deposito:,.0f}")


class AsesoriaEspecializada(Servicio):
    """Asesoría por horas; el nivel del asesor multiplica la tarifa."""

    UNIDAD = "horas"
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_base, especialidad, nivel="junior", disponible=True):
        super().__init__(nombre, tarifa_base, disponible)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ServicioInvalidoError("Debe indicar la especialidad de la asesoría.")
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(
                f"Nivel '{nivel}' no válido. Opciones: {', '.join(self.NIVELES)}.")
        self._especialidad = especialidad.strip()
        self._nivel = nivel

    def validar_parametros(self, duracion):
        self._validar_rango(duracion, 1, 8)

    def calcular_costo_base(self, duracion):
        return self.tarifa_base * duracion * self.NIVELES[self._nivel]

    def describir(self):
        return (f"[{self.id}] Asesoría '{self.nombre}' en {self._especialidad} "
                f"(nivel {self._nivel}) - ${self.tarifa_base:,.0f}/hora")
