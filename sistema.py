"""
sistema.py
----------
SistemaSoftwareFJ: coordina clientes, servicios y reservas usando
listas internas (sin base de datos).

Ningún método deja escapar excepciones: todas se capturan, se registran
en el log y el sistema continúa funcionando.
"""

from cliente import Cliente
from excepciones import (ClienteInvalidoError, OperacionNoPermitidaError,
                         ParametroFaltanteError, ReservaInvalidaError,
                         ServicioInvalidoError, ServicioNoDisponibleError,
                         SoftwareFJError)
from logger import obtener_logger
from reserva import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


def _detalle(error: Exception) -> str:
    """Texto del error incluyendo la causa encadenada, si existe."""
    texto = str(error)
    if error.__cause__ is not None:
        texto += f" | Causa original: {type(error.__cause__).__name__}: {error.__cause__}"
    return texto


class SistemaSoftwareFJ:
    """Fachada principal del sistema."""

    TIPOS_SERVICIO = {
        "sala": ReservaSala,
        "equipo": AlquilerEquipo,
        "asesoria": AsesoriaEspecializada,
    }

    def __init__(self):
        self._clientes: list = []
        self._servicios: list = []
        self._reservas: list = []
        self._log = obtener_logger()
        self._log.info("=" * 20 + " Sistema Software FJ iniciado " + "=" * 20)

    # ================== consultas de solo lectura ==================
    # Se devuelven tuplas (inmutables) para que el menú pueda mostrar los
    # datos sin modificar las listas internas (se conserva la encapsulación).
    @property
    def clientes(self) -> tuple:
        """Clientes registrados (solo lectura)."""
        return tuple(self._clientes)

    @property
    def servicios(self) -> tuple:
        """Servicios creados (solo lectura)."""
        return tuple(self._servicios)

    @property
    def reservas(self) -> tuple:
        """Reservas creadas (solo lectura)."""
        return tuple(self._reservas)

    # ================== utilidades internas ==================
    def _ok(self, mensaje):
        print(f"   ✔ {mensaje}")
        self._log.info(mensaje)

    def _fallo(self, error, nivel="error"):
        texto = _detalle(error)
        print(f"   ✘ {type(error).__name__}: {texto}")
        getattr(self._log, nivel)(f"{type(error).__name__}: {texto}")

    def _inesperado(self, operacion, error):
        print(f"   ✘ Error inesperado en {operacion}: {error!r} (el sistema continúa)")
        self._log.critical("Error inesperado en %s", operacion, exc_info=True)

    def _buscar_cliente(self, documento):
        for cliente in self._clientes:
            if cliente.documento == str(documento):
                return cliente
        raise ClienteInvalidoError(f"No existe un cliente con documento '{documento}'.")

    def _buscar_servicio(self, id_servicio):
        for servicio in self._servicios:
            if servicio.id == id_servicio:
                return servicio
        raise ServicioNoDisponibleError(f"No existe el servicio '{id_servicio}'.")

    def _buscar_reserva(self, id_reserva):
        for reserva in self._reservas:
            if reserva.id == id_reserva:
                return reserva
        raise ReservaInvalidaError(f"No existe la reserva '{id_reserva}'.")

    # ================== clientes ==================
    def registrar_cliente(self, nombre, documento, email, telefono):
        """try / except / else / finally"""
        cliente = None
        try:
            if any(c.documento == str(documento) for c in self._clientes):
                raise OperacionNoPermitidaError(f"Ya existe un cliente con documento '{documento}'.")
            cliente = Cliente(nombre, documento, email, telefono)
        except SoftwareFJError as error:
            self._fallo(error)
        except Exception as error:
            self._inesperado("registrar_cliente", error)
        else:
            self._clientes.append(cliente)
            self._ok(f"Cliente registrado: {cliente.describir()}")
        finally:
            self._log.debug(f"Fin registro de cliente. Total clientes: {len(self._clientes)}")
        return cliente

    # ================== servicios ==================
    def crear_servicio(self, tipo, **datos):
        """Fábrica de servicios con encadenamiento de excepciones."""
        try:
            clase = self.TIPOS_SERVICIO.get(str(tipo).lower())
            if clase is None:
                raise ServicioInvalidoError(
                    f"Tipo de servicio '{tipo}' no existe. Opciones: {', '.join(self.TIPOS_SERVICIO)}.")
            try:
                servicio = clase(**datos)
            except TypeError as error:
                # Parámetros faltantes/sobrantes: se traduce a un error del dominio
                raise ParametroFaltanteError(
                    f"Parámetros incorrectos para crear '{tipo}'.") from error
        except SoftwareFJError as error:
            self._fallo(error)
            return None
        except Exception as error:
            self._inesperado("crear_servicio", error)
            return None
        else:
            self._servicios.append(servicio)
            self._ok(f"Servicio creado: {servicio.describir()}")
            return servicio

    # ================== reservas ==================
    def crear_reserva(self, documento_cliente, id_servicio, duracion):
        """try / except / else"""
        try:
            cliente = self._buscar_cliente(documento_cliente)
            servicio = self._buscar_servicio(id_servicio)
            reserva = Reserva(cliente, servicio, duracion)
        except SoftwareFJError as error:
            self._fallo(error)
            return None
        except Exception as error:
            self._inesperado("crear_reserva", error)
            return None
        else:
            self._reservas.append(reserva)
            self._ok(f"Reserva creada: {reserva.describir()}")
            return reserva

    def confirmar_reserva(self, id_reserva):
        """try / except / finally"""
        try:
            reserva = self._buscar_reserva(id_reserva)
            costo = reserva.confirmar()
            self._ok(f"Reserva {id_reserva} confirmada. Total con IVA: ${costo:,.2f}")
            return True
        except (ServicioNoDisponibleError, OperacionNoPermitidaError) as error:
            self._fallo(error, "warning")
        except SoftwareFJError as error:
            self._fallo(error)
        except Exception as error:
            self._inesperado("confirmar_reserva", error)
        finally:
            self._log.debug(f"Intento de confirmación de {id_reserva} finalizado.")
        return False

    def cancelar_reserva(self, id_reserva, motivo="Solicitud del cliente"):
        try:
            reserva = self._buscar_reserva(id_reserva)
            reserva.cancelar(motivo)
        except SoftwareFJError as error:
            self._fallo(error, "warning")
            return False
        except Exception as error:
            self._inesperado("cancelar_reserva", error)
            return False
        else:
            self._ok(f"Reserva {id_reserva} cancelada. Motivo: {motivo}")
            return True

    def procesar_reserva(self, id_reserva, descuento=0.0):
        try:
            reserva = self._buscar_reserva(id_reserva)
            total = reserva.procesar(descuento)
        except SoftwareFJError as error:
            self._fallo(error)
            return None
        except Exception as error:
            self._inesperado("procesar_reserva", error)
            return None
        else:
            self._ok(f"Reserva {id_reserva} procesada (descuento {descuento:.0%}). "
                     f"Total facturado: ${total:,.2f}")
            return total

    # ================== reportes ==================
    def resumen(self):
        print("\n" + "=" * 70)
        print(" RESUMEN DEL SISTEMA")
        print("=" * 70)
        print(f"\nClientes ({len(self._clientes)}):")
        for c in self._clientes:
            print("  -", c)
        print(f"\nServicios ({len(self._servicios)}):")
        for s in self._servicios:
            estado = "disponible" if s.disponible else "ocupado"
            print(f"  - {s}  [{estado}]")
        print(f"\nReservas ({len(self._reservas)}):")
        for r in self._reservas:
            print("  -", r)
        ingresos = sum(r.costo_total for r in self._reservas if r.estado.value == "Procesada")
        print(f"\nIngresos facturados: ${ingresos:,.2f}")
        self._log.info(f"Resumen: {len(self._clientes)} clientes, {len(self._servicios)} servicios, "
                       f"{len(self._reservas)} reservas, ingresos ${ingresos:,.2f}")
