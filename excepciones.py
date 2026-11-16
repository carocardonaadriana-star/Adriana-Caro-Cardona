"""
excepciones.py
--------------
Jerarquía de excepciones personalizadas del sistema Software FJ.

Todas heredan de SoftwareFJError, lo que permite capturar cualquier error
propio del dominio con un único `except SoftwareFJError`, sin ocultar
errores inesperados de Python.
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema."""

    def __init__(self, mensaje: str, codigo: str = "FJ-000"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.mensaje}"


class ClienteInvalidoError(SoftwareFJError):
    """Datos de cliente inválidos o cliente inexistente."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-CLI")


class ServicioInvalidoError(SoftwareFJError):
    """Datos inválidos al crear o configurar un servicio."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-SRV")


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio no existe o está ocupado."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-DISP")


class ReservaInvalidaError(SoftwareFJError):
    """Intento de reserva incorrecto (duración, datos, etc.)."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-RES")


class OperacionNoPermitidaError(SoftwareFJError):
    """Operación no válida para el estado actual del objeto."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-OP")


class CalculoInconsistenteError(SoftwareFJError):
    """Resultado de cálculo imposible (negativo, descuento > 100 %, etc.)."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-CALC")


class ParametroFaltanteError(SoftwareFJError):
    """Falta un parámetro obligatorio."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "FJ-PARAM")
