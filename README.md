# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Aplicación orientada a objetos en Python 3 (sin base de datos) que gestiona clientes,
servicios (salas, equipos y asesorías) y reservas, con manejo robusto de excepciones
y registro de eventos en un archivo de logs.

## Ejecución

```bash
python main.py
```

Requiere Python 3.8 o superior. No usa librerías externas.
Los eventos y errores quedan en `logs/software_fj.log`.

## Estructura

| Archivo          | Contenido |
|------------------|-----------|
| `excepciones.py` | Jerarquía de excepciones personalizadas (base `SoftwareFJError`). |
| `logger.py`      | Configuración del archivo de logs (único uso de archivos). |
| `entidad.py`     | Clase abstracta `Entidad` (ID único, `validar()` y `describir()` abstractos). |
| `cliente.py`     | Clase `Cliente` con validaciones por expresiones regulares y datos encapsulados/enmascarados. |
| `servicios.py`   | Clase abstracta `Servicio` + `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`. |
| `reserva.py`     | Clase `Reserva` con estados y operaciones confirmar / cancelar / procesar. |
| `sistema.py`     | `SistemaSoftwareFJ`: listas internas y orquestación con captura de todos los errores. |
| `main.py`        | Simulación de 28 operaciones (válidas e inválidas). |

## Diagrama de clases (resumen)

```
                 Entidad (ABC)
           /          |          \
      Cliente   Servicio (ABC)   Reserva ──usa──> Cliente, Servicio
               /      |      \
     ReservaSala AlquilerEquipo AsesoriaEspecializada

SoftwareFJError
 ├── ClienteInvalidoError        ├── OperacionNoPermitidaError
 ├── ServicioInvalidoError       ├── CalculoInconsistenteError
 ├── ServicioNoDisponibleError   └── ParametroFaltanteError
 └── ReservaInvalidaError
```

## Cómo se cumple cada requisito

- **Abstracción:** `Entidad` y `Servicio` son clases abstractas (`ABC`, `@abstractmethod`).
- **Herencia:** `Cliente`, `Servicio` y `Reserva` heredan de `Entidad`; tres servicios heredan de `Servicio`.
- **Polimorfismo:** cada servicio sobrescribe `calcular_costo_base()`, `validar_parametros()` y `describir()`;
  `Reserva` los invoca sin conocer el tipo concreto.
- **Encapsulación:** atributos privados (`__atributo`) con `@property` y setters que validan;
  documento y correo del cliente se muestran enmascarados.
- **Sobrecarga:** `Servicio.calcular_costo()` declara variantes con `@overload`
  (base / con impuesto / con impuesto y descuento) y una implementación que decide según los argumentos.
- **Excepciones:**
  - Personalizadas: módulo `excepciones.py`.
  - `try/except/else/finally`: `SistemaSoftwareFJ.registrar_cliente()`.
  - `try/except/else`: `crear_reserva()`, `Reserva.confirmar()`.
  - `try/except/finally`: `confirmar_reserva()`, `Reserva.procesar()`.
  - Encadenamiento (`raise ... from ...`): `TypeError → ParametroFaltanteError` en `crear_servicio()`
    y `CalculoInconsistenteError → ReservaInvalidaError` en `Reserva.procesar()`.
  - Errores inesperados se registran como `CRITICAL` con traza completa y el sistema sigue.
- **Logs:** `logs/software_fj.log` con niveles INFO, WARNING, ERROR, CRITICAL y DEBUG.
- **Sin base de datos:** toda la información vive en listas dentro de `SistemaSoftwareFJ`.

## Reglas de negocio

| Servicio | Unidad | Rango | Cálculo base |
|----------|--------|-------|--------------|
| Sala | horas | 1–12 | tarifa × horas (+15 % si capacidad > 20) |
| Equipo | días | 1–30 | tarifa × días + depósito |
| Asesoría | horas | 1–8 | tarifa × horas × nivel (junior 1.0, senior 1.5, experto 2.0) |

IVA: 19 %. Descuento permitido: 0 a 99 %. Un servicio confirmado queda ocupado hasta que la
reserva se procesa o se cancela.

## Integrantes

- Integrante 1 – excepciones y logger
- Integrante 2 – Entidad y Cliente
- Integrante 3 – Servicios
- Integrante 4 – Reserva
- Integrante 5 – Sistema, simulación y documentación
