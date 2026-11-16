"""
main.py
-------
Simulación de operaciones completas del sistema Software FJ:
registros válidos e inválidos, servicios correctos e incorrectos,
reservas exitosas y fallidas. El programa NUNCA se detiene por un error.

Ejecución:  python main.py
"""

from logger import ARCHIVO_LOG
from sistema import SistemaSoftwareFJ

_paso = 0


def operacion(titulo):
    global _paso
    _paso += 1
    print(f"\n[{_paso:02d}] {titulo}")


def main():
    sistema = SistemaSoftwareFJ()
    print("=" * 70)
    print(" SOFTWARE FJ - Sistema de Gestión de Clientes, Servicios y Reservas")
    print("=" * 70)

    # ------------------------- CLIENTES -------------------------
    operacion("Registrar cliente válido")
    sistema.registrar_cliente("Ana María Gómez", "1012345678", "ana.gomez@correo.com", "3001234567")

    operacion("Registrar segundo cliente válido")
    sistema.registrar_cliente("Carlos Pérez", "79856432", "carlos.perez@empresa.co", "310 555 1234")

    operacion("Registrar cliente con correo inválido")
    sistema.registrar_cliente("Luis Torres", "52123456", "luis.torres@@correo", "3159998877")

    operacion("Registrar cliente con documento con letras")
    sistema.registrar_cliente("Marta Ruiz", "ABC123", "marta@correo.com", "3201112233")

    operacion("Registrar cliente con nombre vacío")
    sistema.registrar_cliente("", "1098765432", "vacio@correo.com", "3012223344")

    operacion("Registrar cliente duplicado")
    sistema.registrar_cliente("Ana Gómez", "1012345678", "otra@correo.com", "3000000000")

    # ------------------------- SERVICIOS -------------------------
    operacion("Crear servicio: Sala de juntas")
    sala = sistema.crear_servicio("sala", nombre="Sala Ejecutiva", tarifa_base=80000, capacidad=30)

    operacion("Crear servicio: Alquiler de equipo")
    equipo = sistema.crear_servicio("equipo", nombre="Proyector 4K", tarifa_base=50000,
                                    tipo_equipo="Audiovisual", deposito=100000)

    operacion("Crear servicio: Asesoría especializada")
    asesoria = sistema.crear_servicio("asesoria", nombre="Consultoría Cloud", tarifa_base=120000,
                                      especialidad="Arquitectura AWS", nivel="senior")

    operacion("Crear servicio con tarifa negativa")
    sistema.crear_servicio("sala", nombre="Sala Mini", tarifa_base=-5000, capacidad=4)

    operacion("Crear servicio con parámetro faltante (encadenamiento)")
    sistema.crear_servicio("asesoria", nombre="Asesoría Legal", tarifa_base=90000)

    operacion("Crear servicio de tipo inexistente")
    sistema.crear_servicio("transporte", nombre="Van", tarifa_base=200000)

    operacion("Crear asesoría con nivel no válido")
    sistema.crear_servicio("asesoria", nombre="Asesoría Datos", tarifa_base=100000,
                           especialidad="Big Data", nivel="maestro")

    # ------------------------- RESERVAS -------------------------
    operacion("Reserva exitosa: Ana reserva la sala 3 horas y la confirma")
    r1 = sistema.crear_reserva("1012345678", sala.id, 3)
    sistema.confirmar_reserva(r1.id)

    operacion("Reserva fallida: Carlos intenta la misma sala (ocupada)")
    r2 = sistema.crear_reserva("79856432", sala.id, 2)
    sistema.confirmar_reserva(r2.id)

    operacion("Reserva fallida: duración fuera de rango (20 horas)")
    sistema.crear_reserva("79856432", sala.id, 20)

    operacion("Reserva fallida: cliente inexistente")
    sistema.crear_reserva("99999999", equipo.id, 2)

    operacion("Reserva fallida: servicio inexistente")
    sistema.crear_reserva("1012345678", "SRV-999", 2)

    operacion("Reserva fallida: duración no numérica")
    sistema.crear_reserva("1012345678", equipo.id, "tres")

    operacion("Procesar reserva de Ana con 10 % de descuento (libera la sala)")
    sistema.procesar_reserva(r1.id, descuento=0.10)

    operacion("Ahora Carlos sí puede confirmar la sala")
    sistema.confirmar_reserva(r2.id)

    operacion("Cancelar una reserva ya procesada (no permitido)")
    sistema.cancelar_reserva(r1.id)

    operacion("Reserva de asesoría con descuento inconsistente (150 %)")
    r3 = sistema.crear_reserva("79856432", asesoria.id, 4)
    sistema.confirmar_reserva(r3.id)
    sistema.procesar_reserva(r3.id, descuento=1.5)

    operacion("Reintento: procesar la asesoría con descuento válido (5 %)")
    sistema.procesar_reserva(r3.id, descuento=0.05)

    operacion("Alquiler de equipo y cancelación por el cliente")
    r4 = sistema.crear_reserva("1012345678", equipo.id, 5)
    sistema.confirmar_reserva(r4.id)
    sistema.cancelar_reserva(r4.id, "Cambio de fecha del evento")

    operacion("Confirmar dos veces la misma reserva (no permitido)")
    sistema.confirmar_reserva(r2.id)

    operacion("Procesar una reserva cancelada (no permitido)")
    sistema.procesar_reserva(r4.id)

    operacion("Demostración de sobrecarga de calcular_costo() (Proyector 4K, 2 días)")
    print(f"   Base:                      ${equipo.calcular_costo(2):,.2f}")
    print(f"   Con IVA 19 %:              ${equipo.calcular_costo(2, impuesto=True):,.2f}")
    print(f"   Con impuesto 8 %:          ${equipo.calcular_costo(2, impuesto=0.08):,.2f}")
    print(f"   Con 20 % de descuento:     ${equipo.calcular_costo(2, descuento=0.20):,.2f}")
    print(f"   Descuento 20 % + IVA:      ${equipo.calcular_costo(2, True, 0.20):,.2f}")

    sistema.resumen()
    print(f"\nEl sistema terminó sin interrupciones. Log de eventos: {ARCHIVO_LOG}")


if __name__ == "__main__":
    main()
