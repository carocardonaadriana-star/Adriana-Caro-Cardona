"""
logger.py
---------
Configuración del archivo de logs (logs/software_fj.log).

Es el ÚNICO uso de archivos del sistema: registrar eventos y errores.
Si el archivo no puede abrirse, el sistema sigue funcionando y los
mensajes se envían a la consola (degradación controlada).
"""

import logging
import os

DIRECTORIO_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
ARCHIVO_LOG = os.path.join(DIRECTORIO_LOGS, "software_fj.log")

_FORMATO = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s", "%Y-%m-%d %H:%M:%S"
)


def obtener_logger() -> logging.Logger:
    """Devuelve el logger del sistema, creándolo una sola vez."""
    logger = logging.getLogger("SoftwareFJ")
    if logger.handlers:  # ya configurado
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    try:
        os.makedirs(DIRECTORIO_LOGS, exist_ok=True)
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
    except OSError as error:
        # No se pudo crear el archivo: se usa la consola y se continúa.
        manejador = logging.StreamHandler()
        manejador.setFormatter(_FORMATO)
        logger.addHandler(manejador)
        logger.warning("No se pudo abrir el archivo de log (%s). Usando consola.", error)
        return logger

    manejador.setFormatter(_FORMATO)
    logger.addHandler(manejador)
    return logger
