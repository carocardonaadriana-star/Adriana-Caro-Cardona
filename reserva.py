"""
reserva.py
----------
Clase Reserva: integra cliente, servicio, duración y estado.
Implementa confirmación, cancelación y procesamiento con excepciones.

Ciclo de vida:  PENDIENTE -> CONFIRMADA -> PROCESADA
                     \\            \\
                      +-> CANCELADA <+
"""

from enum import Enum

from cliente import Cliente
from entidad import Entidad
from excepciones import (CalculoInconsistenteError, OperacionNoPermitidaError,
                         ReservaInvalidaError, ServicioNoDisponibleError)
from servicios import Servicio


class EstadoReserva(Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"


class Reserva(Entidad):
    """Reserva de un servicio por parte de un cliente."""

    def __init__(self, cliente, servicio, duracion):
        # Se valida ANTES de asignar el ID para no consumir identificadores en reservas fallidas
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un objeto Servicio válido.")
        servicio.validar_parametros(duracion)   # polimorfismo: cada servicio valida a su modo
        super().__init__("RES")

        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = duracion
        self.__estado = EstadoReserva.PENDIENTE
        self.__costo_total = 0.0
        self.__historial = [f"Creada ({EstadoReserva.PENDIENTE.value})"]

    # ---------------- solo lectura ----------------
    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def estado(self):
        return self.__estado

    @property
    def costo_total(self):
        return self.__costo_total

    @property
    def historial(self):
        return list(self.__historial)  # copia: no se puede modificar desde fuera

    # ---------------- operaciones ----------------
    def confirmar(self):
        """Ocupa el servicio y calcula el costo con IVA."""
        if self.__estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva {self.id} en estado '{self.__estado.value}'.")
        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError(
                f"'{self.__servicio.nombre}' no está disponible en este momento.")
        try:
            costo = self.__servicio.calcular_costo(self.__duracion, impuesto=True)
        except CalculoInconsistenteError as error:
            # Encadenamiento: el error de cálculo se convierte en error de reserva
            raise ReservaInvalidaError(f"No se pudo confirmar la reserva {self.id}.") from error
        else:
            self.__servicio.ocupar()
            self.__costo_total = costo
            self.__estado = EstadoReserva.CONFIRMADA
            self.__historial.append(f"Confirmada por ${costo:,.2f}")
        return costo

    def cancelar(self, motivo="Sin motivo"):
        if self.__estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise OperacionNoPermitidaError(
                f"La reserva {self.id} ya está '{self.__estado.value}' y no puede cancelarse.")
        if self.__estado is EstadoReserva.CONFIRMADA:
            self.__servicio.liberar()
        self.__estado = EstadoReserva.CANCELADA
        self.__historial.append(f"Cancelada: {motivo}")

    def procesar(self, descuento=0.0):
        """Aplica descuento opcional, factura y libera el servicio."""
        if self.__estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"Solo se procesan reservas confirmadas (estado actual: '{self.__estado.value}').")
        try:
            total = self.__servicio.calcular_costo(self.__duracion, True, descuento)
        except CalculoInconsistenteError as error:
            raise ReservaInvalidaError(f"No se pudo procesar la reserva {self.id}.") from error
        else:
            self.__costo_total = total
            self.__estado = EstadoReserva.PROCESADA
            self.__servicio.liberar()
            return total
        finally:
            # Se ejecuta siempre: deja rastro del intento, haya error o no.
            self.__historial.append(f"Intento de procesamiento (descuento={descuento})")

    # ---------------- contrato de Entidad ----------------
    def validar(self) -> bool:
        return self.__cliente.validar() and self.__servicio.validar()

    def describir(self) -> str:
        return (f"Reserva {self.id}: {self.__cliente.nombre} -> {self.__servicio.nombre} | "
                f"{self.__duracion} {self.__servicio.UNIDAD} | {self.__estado.value} | "
                f"${self.__costo_total:,.2f}")
