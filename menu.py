"""
menu.py
-------
Menú interactivo de consola para gestionar el sistema Software FJ.

Complementa la simulación automática de main.py: aquí el usuario elige
cada operación y escribe los datos. Todos los errores (datos inválidos,
opciones inexistentes, Ctrl+C, fin de entrada) se capturan, se registran
en el log y el menú vuelve a mostrarse sin cerrar el programa.

Ejecución:  python menu.py
"""

from logger import ARCHIVO_LOG, obtener_logger  # Ruta del log y acceso al logger
from sistema import SistemaSoftwareFJ           # Fachada que coordina todo el sistema

# Texto del menú principal; se define una sola vez como constante
OPCIONES = """
======================================================================
 SOFTWARE FJ - Menú principal
======================================================================
  1. Registrar cliente
  2. Crear servicio
  3. Crear reserva
  4. Confirmar reserva
  5. Procesar reserva (facturar)
  6. Cancelar reserva
  7. Ver clientes, servicios y reservas
  8. Cargar datos de demostración
  9. Ver últimas líneas del log
  0. Salir
----------------------------------------------------------------------"""


class EntradaCancelada(Exception):
    """Se lanza cuando el usuario cancela la captura de un dato (Ctrl+C / fin de entrada)."""


def pedir(texto):
    """Pide un dato por teclado y lo devuelve sin espacios sobrantes."""
    try:                                          # Se intenta leer la entrada del usuario
        return input(f"   {texto}: ").strip()     # Se quita el espacio al inicio y al final
    except (KeyboardInterrupt, EOFError) as error:  # Ctrl+C o fin de entrada
        print()                                   # Salto de línea para no mezclar la salida
        raise EntradaCancelada("Captura cancelada por el usuario.") from error  # Encadenamiento


def a_numero(texto):
    """Convierte texto a número; si no se puede, devuelve el texto original.

    Así el propio sistema valida el dato y lanza su excepción personalizada,
    en lugar de que el menú oculte el error.
    """
    try:                                          # Se intenta convertir a número
        valor = float(texto.replace(",", "."))    # Acepta coma o punto decimal
    except ValueError:                            # No era un número
        return texto                              # Se devuelve tal cual para que el sistema lo rechace
    else:                                         # La conversión funcionó
        return int(valor) if valor.is_integer() else valor  # Entero si no tiene decimales


def listar(titulo, elementos):
    """Imprime una lista numerada de objetos o un aviso si está vacía."""
    print(f"\n   {titulo} ({len(elementos)}):")   # Encabezado con la cantidad
    if not elementos:                             # Lista vacía
        print("     (ninguno)")                   # Se avisa en lugar de no mostrar nada
    for elemento in elementos:                    # Se recorre cada objeto
        print(f"     - {elemento}")               # Cada objeto sabe describirse (__str__)


# ============================ opciones del menú ============================

def registrar_cliente(sistema):
    """Opción 1: pide los datos y registra un cliente."""
    nombre = pedir("Nombre completo")             # Dato obligatorio
    documento = pedir("Documento (6 a 10 dígitos)")  # Se valida en la clase Cliente
    email = pedir("Correo electrónico")           # Se valida con expresión regular
    telefono = pedir("Teléfono")                  # Se valida en la clase Cliente
    sistema.registrar_cliente(nombre, documento, email, telefono)  # El sistema captura los errores


def crear_servicio(sistema):
    """Opción 2: pide el tipo de servicio y sus parámetros particulares."""
    tipo = pedir("Tipo (sala / equipo / asesoria)").lower()  # Se normaliza a minúsculas
    datos = {                                     # Parámetros comunes a todos los servicios
        "nombre": pedir("Nombre del servicio"),
        "tarifa_base": a_numero(pedir("Tarifa base")),
    }
    if tipo == "sala":                            # Parámetros propios de una sala
        datos["capacidad"] = a_numero(pedir("Capacidad (personas)"))
    elif tipo == "equipo":                        # Parámetros propios de un equipo
        datos["tipo_equipo"] = pedir("Tipo de equipo")
        datos["deposito"] = a_numero(pedir("Depósito (0 si no aplica)") or "0")
    elif tipo == "asesoria":                      # Parámetros propios de una asesoría
        datos["especialidad"] = pedir("Especialidad")
        datos["nivel"] = pedir("Nivel (junior / senior / experto)").lower() or "junior"
    # Si el tipo no existe, el sistema lanza ServicioInvalidoError y lo registra
    sistema.crear_servicio(tipo, **datos)


def crear_reserva(sistema):
    """Opción 3: asocia un cliente con un servicio por una duración."""
    listar("Clientes", sistema.clientes)          # Se muestran para que el usuario elija
    listar("Servicios", sistema.servicios)
    documento = pedir("Documento del cliente")    # Se busca en la lista interna
    id_servicio = pedir("ID del servicio (ej. SRV-001)").upper()  # Los ID están en mayúsculas
    duracion = a_numero(pedir("Duración (horas o días según el servicio)"))
    reserva = sistema.crear_reserva(documento, id_servicio, duracion)  # Devuelve None si falla
    if reserva and pedir("¿Confirmarla ahora? (s/n)").lower() == "s":  # Confirmación opcional
        sistema.confirmar_reserva(reserva.id)


def pedir_reserva(sistema):
    """Muestra las reservas y devuelve el ID que escriba el usuario."""
    listar("Reservas", sistema.reservas)          # Se muestran con su estado actual
    return pedir("ID de la reserva (ej. RES-001)").upper()


def confirmar_reserva(sistema):
    """Opción 4: confirma una reserva pendiente (ocupa el servicio)."""
    sistema.confirmar_reserva(pedir_reserva(sistema))


def procesar_reserva(sistema):
    """Opción 5: factura una reserva confirmada, con descuento opcional."""
    id_reserva = pedir_reserva(sistema)
    texto = pedir("Descuento en % (Enter = 0)") or "0"   # Valor por defecto: sin descuento
    descuento = a_numero(texto)                   # Puede quedar como texto si es inválido
    if isinstance(descuento, (int, float)):       # Solo los números se pasan a fracción
        descuento = descuento / 100               # 10 % -> 0.10
    sistema.procesar_reserva(id_reserva, descuento=descuento)


def cancelar_reserva(sistema):
    """Opción 6: cancela una reserva indicando el motivo."""
    id_reserva = pedir_reserva(sistema)
    motivo = pedir("Motivo (Enter = Solicitud del cliente)") or "Solicitud del cliente"
    sistema.cancelar_reserva(id_reserva, motivo)


def ver_resumen(sistema):
    """Opción 7: muestra todo lo registrado y los ingresos facturados."""
    sistema.resumen()


def cargar_demo(sistema):
    """Opción 8: crea datos de ejemplo para probar el menú rápidamente."""
    sistema.registrar_cliente("Ana María Gómez", "1012345678", "ana.gomez@correo.com", "3001234567")
    sistema.registrar_cliente("Carlos Pérez", "79856432", "carlos.perez@empresa.co", "3105551234")
    sistema.crear_servicio("sala", nombre="Sala Ejecutiva", tarifa_base=80000, capacidad=30)
    sistema.crear_servicio("equipo", nombre="Proyector 4K", tarifa_base=50000,
                           tipo_equipo="Audiovisual", deposito=100000)
    sistema.crear_servicio("asesoria", nombre="Consultoría Cloud", tarifa_base=120000,
                           especialidad="Arquitectura AWS", nivel="senior")


def ver_log(sistema, lineas=15):
    """Opción 9: muestra las últimas líneas del archivo de logs."""
    try:                                          # La lectura del archivo puede fallar
        with open(ARCHIVO_LOG, encoding="utf-8") as archivo:  # Se cierra solo al terminar
            ultimas = archivo.readlines()[-lineas:]  # Solo las últimas N líneas
    except OSError as error:                      # Archivo inexistente o sin permisos
        print(f"   ✘ No se pudo leer el log: {error}")
    else:                                         # Lectura exitosa
        print(f"\n   Últimas {len(ultimas)} líneas de {ARCHIVO_LOG}:\n")
        for linea in ultimas:                     # Se imprimen sin el salto de línea final
            print("   " + linea.rstrip())


# Diccionario que relaciona cada opción con su función (evita una cadena de if/elif)
ACCIONES = {
    "1": registrar_cliente,
    "2": crear_servicio,
    "3": crear_reserva,
    "4": confirmar_reserva,
    "5": procesar_reserva,
    "6": cancelar_reserva,
    "7": ver_resumen,
    "8": cargar_demo,
    "9": ver_log,
}


def main():
    """Ciclo principal: muestra el menú hasta que el usuario elige salir."""
    sistema = SistemaSoftwareFJ()                 # Una sola instancia durante toda la sesión
    log = obtener_logger()                        # Para registrar eventos propios del menú
    log.info("Menú interactivo iniciado.")
    while True:                                   # El ciclo termina con la opción 0 o con Ctrl+C aquí
        print(OPCIONES)
        opcion = ""                               # Valor inicial para el registro del bloque finally
        try:                                      # Lectura de la opción en el menú principal
            opcion = pedir("Elija una opción")
        except EntradaCancelada:                  # Ctrl+C o fin de entrada en el menú principal
            print("   Saliendo del sistema...")
            break                                 # Se sale ordenadamente (evita un ciclo infinito)
        try:                                      # Todo lo que pase en una opción queda contenido aquí
            if opcion == "0":                     # Salida ordenada
                break
            accion = ACCIONES.get(opcion)         # Se busca la función de la opción
            if accion is None:                    # Opción que no existe en el menú
                print(f"   ✘ Opción '{opcion}' no válida. Intente de nuevo.")
                log.warning(f"Opción de menú no válida: '{opcion}'")
                continue                          # Se vuelve a mostrar el menú
            accion(sistema)                       # Se ejecuta la opción elegida
        except EntradaCancelada:                  # Ctrl+C dentro de una opción
            print("   (operación cancelada, volviendo al menú)")
            log.info("Operación cancelada por el usuario desde el menú.")
        except Exception as error:                # Último recurso: el menú nunca se cae
            print(f"   ✘ Error inesperado: {error!r} (el sistema continúa)")
            log.critical("Error inesperado en el menú", exc_info=True)
        finally:                                  # Se ejecuta siempre, haya error o no
            log.debug(f"Fin de interacción con el menú (opción '{opcion}').")
    log.info("Menú interactivo finalizado por el usuario.")
    print(f"\nHasta pronto. Los eventos quedaron en: {ARCHIVO_LOG}")


if __name__ == "__main__":                        # Solo se ejecuta si se llama directamente
    main()
