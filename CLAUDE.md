# Flypad Bridge

Puente que permite usar el mando **Parrot Flypad** (Bluetooth LE) en simuladores de dron de PC
(Liftoff, Uncrashed) presentándolo como un mando virtual de Xbox 360.

Código principal: `flypad_bridge.py` (Python, `bleak` + `vgamepad`). Ya funciona: probado
10+ minutos seguidos en Uncrashed sin cortes.

## Estado y próximos pasos

Ver `guppy/STATUS.md`.

## Estado del proyecto (Guppy)

Todo lo relacionado con Guppy, el gestor de proyectos de Nilo, vive en el directorio `guppy/` de la raíz del repo, separado de los archivos del proyecto. No guardes datos de Guppy fuera de ese directorio ni datos del proyecto dentro de él.

El estado del proyecto está en `guppy/STATUS.md`. Al terminar cualquier sesión que cambie el estado del proyecto:
1. Actualiza la cabecera de `guppy/STATUS.md` (estado, siguiente_paso, bloqueo, actualizado).
2. Añade una entrada breve al principio de su Diario.
3. Incluye el cambio en el commit.

Estados: activo, bloqueado, en-pausa, pendiente, terminado. Si está bloqueado, di qué se espera y de quién.
No uses CHANGELOG.md para esto: es para usuarios.

## Protocolo BLE del Flypad

Extraído decompilando FreeFlight Mini 5.5.9 (`com.parrot.freeflight3.RemoteController` y
`FrameResolver`). Internamente Parrot llama al Flypad "Tinos". El chip es un CSR uEnergy.

| Qué | UUID |
|---|---|
| Servicio | `9e35fa00-4344-44d4-a2e2-0c7f6046878b` |
| Entradas, mando → PC (notify) | `9e35fa01-4344-44d4-a2e2-0c7f6046878b` |
| Comandos, PC → mando (write) | `9e35fa02-4344-44d4-a2e2-0c7f6046878b` |

- Se anuncia con un nombre que contiene `FLYPAD`. No requiere emparejamiento.
- **Frame de entrada**: 7 bytes `[batería, botones_lo, botones_hi, der_X, der_Y, izq_X, izq_Y]`.
  - Batería en %.
  - Ejes: centro 128. Valor = (b - 128). En los ejes Y hay que invertir el signo (arriba = positivo).
  - Botones (máscara de 16 bits `lo | hi<<8`):
    `TAKEOFF 0x001, B1 0x002, B2 0x004, B3 0x008, B4 0x010, R1 0x020, R2 0x040, L1 0x080, L2 0x100,
    JOY_LEFT (pulsar) 0x200, JOY_RIGHT (pulsar) 0x400`.
- **Comando LED** (2 bytes a `9e35fa02`): byte0 `0xA7` = verde, `0xC7` = rojo; byte1 `0xD1` = vibrar,
  `0x00` = no vibrar. La app oficial solo lo envía al conectar y cuando cambia la batería; no hay
  ningún heartbeat periódico. El "keep-alive" opcional del bridge reenvía `A7 00`.
- Existe además un servicio OTA de actualización de firmware (`9e35fb01-…`, bootloader CSR).
  No tocarlo.

## Lo que NO funciona (no repetir)

- **Emparejarlo en Windows o conectarlo por USB**: en los dos casos Windows lo ve como un mando HID
  nativo, pero se desconecta a los 60-120 s. Por eso se usa la conexión GATT directa.
- **Mantenerlo vivo por USB**: por USB es `VID 0x19CF / PID 0x5200` ("FLYPAD Controller"). Declara
  un output report de 5 bytes, pero escribir en él **cuelga el proceso**, que ni siquiera responde a
  Ctrl+C. Por USB no hay canal de escritura útil.
- **Firmware alternativo**: no existe. La app no trae ninguna imagen del firmware del Flypad (solo
  las de los drones Mambo y Swing). Descartado.

## Driver ViGEmBus

- `vgamepad` necesita el driver de sistema **ViGEmBus**. El `.exe` de PyInstaller NO lo instala: en un
  PC sin el driver, fallará al crear el mando virtual.
- **Versión de referencia: ViGEmBus v1.22.0**
  (https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0). Comprobado: se desinstaló el driver que
  instala `pip install vgamepad`, se instaló esta versión y el bridge sigue funcionando perfectamente.
  Es la que hay que guardar en el repo y documentar en el README.
- ViGEmBus está descontinuado por su autor (Nefarius, 2023), pero sigue funcionando en
  Windows 10 y 11. Por eso conviene guardar una copia del instalador en el repo.

## Entorno

- Windows 11, Python 3. Dependencias: `bleak`, `vgamepad`.
- Para ahorrar batería, el Flypad puede ir enchufado por USB solo para cargar mientras los datos
  van por Bluetooth. Tiene que estar encendido en modo Bluetooth y sin conectar a ningún móvil.
