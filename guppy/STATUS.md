---
estado: activo
siguiente_paso: Confirmar H3 (instalador de ViGEmBus en drivers/) y pasar a H4, el .exe con PyInstaller.
bloqueo: ""
actualizado: 2026-10-08
---

# Estado

El bridge funciona: presenta el Flypad (BLE) como mando virtual de Xbox 360 y se ha probado más de 10 minutos seguidos en Uncrashed sin cortes. Ahora se está convirtiendo en algo distribuible, por hitos y de uno en uno. Decidido: se queda como programa de consola en una ventana pequeña que se deja abierta; no habrá icono en la bandeja.

Plan por hitos:

- [x] H1. Poner orden: keep-alive eliminado (probado: no hace falta), docstring al día, `requirements.txt` con versiones fijadas, `.gitignore`.
- [x] H2. Mensajes de error claros: falta ViGEmBus, Bluetooth apagado o sin adaptador; que la ventana no se cierre de golpe ante un error.
- [ ] H3. Guardar el instalador de ViGEmBus v1.22.0 en `drivers/` con su licencia.
- [ ] H4. `.exe` único con PyInstaller (`.spec` + script de build), sin incluir `guppy/`.
- [ ] H5. README: requisitos, instalación del driver, uso, asignación de botones, problemas habituales.
- [ ] H6 (opcional). Publicar una release en GitHub con el `.exe`.

## Diario

- 2026-10-08: Regla nueva: todo lo público (README, textos de la app, ayuda, comentarios) en inglés. Traducidos flypad_bridge.py y drivers/README.md; regla anotada en CLAUDE.md.
- 2026-10-08: H3 hecho: instalador oficial de ViGEmBus v1.22.0 (firma válida de Nefarius, SHA-256 anotado) y su licencia BSD-3 guardados en drivers/.
- 2026-10-08: H2 cerrado. Probado en el equipo de pruebas: uso normal sin cambios; al apagar el Bluetooth avisa y reconecta solo al encenderlo. Retoque: el log muestra «Flypad» cuando Windows no da el nombre del dispositivo.
- 2026-10-08: H2 implementado y probado en Marcianito (falta ViGEmBus, Bluetooth apagado/ausente simulado, la ventana espera a Intro ante un error). Pendiente de probar en el equipo de pruebas.
- 2026-10-08: H1 cerrado. Probado en el equipo de pruebas: funciona sin keep-alive, así que se elimina del código. Versiones fijadas: bleak 3.0.2, vgamepad 0.1.0 (Python 3.14).
- 2026-10-08: H1 hecho: keep-alive pasa a ser opcional (`--keepalive`), limpieza del script, `requirements.txt` y `.gitignore`. Decidido: consola, sin icono de bandeja. Plan por hitos H1–H6.
- 2026-10-08: guppy/STATUS.md creado.
