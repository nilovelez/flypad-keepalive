---
estado: activo
siguiente_paso: Empaquetar flypad_bridge.py como .exe único con PyInstaller, con el keep-alive desactivado por defecto (--keepalive opcional).
bloqueo: ""
actualizado: 2026-10-08
---

# Estado

El bridge funciona: presenta el Flypad (BLE) como mando virtual de Xbox 360 y se ha probado más de 10 minutos seguidos en Uncrashed sin cortes. Falta convertirlo en algo distribuible: ejecutable, detección del driver ViGEmBus y README.

Pendiente:

- [ ] Empaquetar como `.exe` único con PyInstaller.
- [ ] Keep-alive desactivado por defecto (no hace falta), pero disponible con `--keepalive`.
- [ ] Guardar el instalador de ViGEmBus v1.22.0 en el repo y documentarlo en el README.
- [ ] Detectar si falta ViGEmBus y avisar con un mensaje claro en vez de un error críptico.
- [ ] README: requisitos, instalación del driver, uso, asignación de botones.
- Por decidir: ventana de consola (como ahora) o app sin ventana con icono en la bandeja.

## Diario

- 2026-10-08: guppy/STATUS.md creado.
