# Flypad Bridge

Puente que permite usar el mando **Parrot Flypad** (Bluetooth LE) en simuladores de dron de PC
(Liftoff, Uncrashed) presentándolo como un mando virtual de Xbox 360.

Código principal: `flypad_bridge.py` (Python, `bleak` + `vgamepad`). Ya funciona: probado
10+ minutos seguidos en Uncrashed sin cortes.

## Idioma

Todo lo público va en **inglés**: README y demás páginas públicas, textos de la aplicación (mensajes,
logs, ayuda de la línea de comandos), docstrings, comentarios del código y mensajes de commit.
En español solo lo interno: este `CLAUDE.md` y `guppy/`.

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
  ningún heartbeat periódico. El bridge tuvo un keep-alive que reenviaba `A7 00`; se quitó
  (2026-10-08) porque se comprobó que la conexión GATT aguanta sin él.
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
  Copia guardada en `drivers/` (instalador, licencia BSD-3 y `drivers/README.md` con SHA-256 y firma).
- **Error cuando falta el driver** (reproducido en Marcianito, sin ViGEmBus): salta ya en
  `import vgamepad` (no al crear el mando), porque `vgamepad/win/virtual_gamepad.py` crea un bus
  global `VBUS = VBus()` al importarse. Es una `Exception` genérica con el texto
  `VIGEM_ERROR_BUS_NOT_FOUND` (código `0xE0000001`). El bridge la reconoce por ese texto y muestra
  un mensaje con el enlace a ViGEmBus v1.22.0.
- `pip install vgamepad` (al compilar el paquete desde fuente) lanza el instalador MSI de ViGEmBus
  que trae dentro, y no es la v1.22.0. Si aparece al preparar un entorno, cancelarlo: el paquete se
  instala igual.
- ViGEmBus está descontinuado por su autor (Nefarius, 2023), pero sigue funcionando en
  Windows 10 y 11. Por eso conviene guardar una copia del instalador en el repo.

## Build del .exe

- `.\build.ps1` → `dist\FlypadKeepalive.exe` (un solo archivo, con consola, ~12 MB). Crea `.venv` con
  `requirements-build.txt` (PyInstaller 6.22.3) si no existe. Se compila en Marcianito.
- `flypad_keepalive.spec` mete a mano `vgamepad/win/vigem/client/x64/ViGEmClient.dll` en esa misma
  ruta (vgamepad la carga relativa a su paquete). El spec localiza vgamepad con `find_spec` sin
  importarlo, porque importarlo falla si no está ViGEmBus (Marcianito no lo tiene).
- No se incluyen los MSI viejos de ViGEmBus que trae vgamepad, ni `guppy/` ni `drivers/`
  (comprobado con `pyi-archive_viewer --list`).
- Los avisos de `winrt.windows.*` que salen en `build\...\warn-*.txt` son paquetes opcionales que
  tampoco están en el entorno normal; el escaneo BLE funciona desde el .exe.
- El `build.ps1` no usa `$ErrorActionPreference = "Stop"`: PyInstaller escribe en stderr y
  PowerShell lo cortaría. Los fallos se detectan con `$LASTEXITCODE`.

## Entorno

- Windows 11, Python 3. Dependencias: `bleak`, `vgamepad`.
- Para ahorrar batería, el Flypad puede ir enchufado por USB solo para cargar mientras los datos
  van por Bluetooth. Tiene que estar encendido en modo Bluetooth y sin conectar a ningún móvil.
