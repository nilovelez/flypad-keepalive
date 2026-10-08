---
estado: activo
siguiente_paso: Revisar el README publicado en GitHub y cerrar H6; luego H7, publicar la release con el .exe (el README ya enlaza a Releases).
bloqueo: ""
actualizado: 2026-10-08
---

# Estado

El bridge funciona: presenta el Flypad (BLE) como mando virtual de Xbox 360 y se ha probado más de 10 minutos seguidos en Uncrashed sin cortes. Ahora se está convirtiendo en algo distribuible, por hitos y de uno en uno. Decidido: el ejecutable final será una ventana gráfica pequeña que se deja abierta (no consola, no icono en la bandeja), al estilo de la pantalla principal de Logitech Options.

Plan por hitos:

- [x] H1. Poner orden: keep-alive eliminado (probado: no hace falta), docstring al día, `requirements.txt` con versiones fijadas, `.gitignore`.
- [x] H2. Mensajes de error claros: falta ViGEmBus, Bluetooth apagado o sin adaptador; que la ventana no se cierre de golpe ante un error.
- [x] H3. Guardar el instalador de ViGEmBus v1.22.0 en `drivers/` con su licencia.
- [x] H4. `.exe` único con PyInstaller (`.spec` + script de build), sin incluir `guppy/`.
- [x] H5. Interfaz gráfica: ventana pequeña y cuidada con la imagen del mando en el centro, icono de Bluetooth y zona de mensajes debajo (referencia: Logitech Options). El `.exe` final deja de ser de consola.
- [ ] H6. Repo presentable: `LICENSE` con la GPL-3.0 (la ventana ya dice «GPL-3.0 Licensed»); README: requisitos, instalación del driver, uso, asignación de botones, problemas habituales, aviso de SmartScreen (el `.exe` no está firmado).
- [ ] H7 (opcional). Publicar una release en GitHub con el `.exe`.

## Diario

- 2026-10-08: El enlace del driver (app y README) pasa a descarga directa (/raw/main/drivers/...).
- 2026-10-08: Retoques: el error de driver enlaza a la copia de drivers/ del repo y parte el texto en dos líneas; textos de estado más arriba; README sin icono, sin enlace a Parrot y con captura de la ventana con marco (docs/images/window.png).
- 2026-10-08: H6 hecho: README en inglés (presentación, por qué, instalación, SmartScreen, uso con capturas, botones, troubleshooting, cómo funciona, build, créditos), LICENSE GPL-3.0 y capturas en docs/images/. El enlace de descarga apunta a Releases, que aún está vacío (H7).
- 2026-10-08: H5 cerrado: ventana gráfica probada con el Flypad en el equipo de pruebas.
- 2026-10-08: El enlace al repo pasa a ser un crédito: «© Nilo Velez · GPL-3.0 Licensed». Falta añadir el LICENSE GPL-3.0 al repo (H6).
- 2026-10-08: Enlace al repo de GitHub en la esquina inferior izquierda de la ventana.
- 2026-10-08: Icono de la app (assets/app-icon/icon.ico, de Nilo) puesto en la ventana y en el .exe.
- 2026-10-08: H5 hecho en Marcianito tras aprobar el mockup: flypad_keepalive.py (Tkinter, imágenes de assets/) y .exe sin consola (15,2 MB). Probado aquí: error de driver con enlace, búsqueda BLE real y cierre limpio. Pendiente de probar con el Flypad.
- 2026-10-08: H4 cerrado: el .exe funciona en una partida en el equipo de pruebas. H5 decidido: Tkinter; la imagen del mando la aporta Nilo (foto con fondo blanco).
- 2026-10-08: Nuevo hito H5, interfaz gráfica (el README pasa a H6 y la release a H7). El .exe salta SmartScreen en el equipo de pruebas: se documentará en el README.
- 2026-10-08: H4 hecho en Marcianito: build.ps1 + flypad_keepalive.spec generan FlypadKeepalive.exe (11,8 MB). Probado aquí: --help, error de driver ausente y escaneo BLE. Pendiente de probar con el Flypad en el equipo de pruebas.
- 2026-10-08: H3 cerrado.
- 2026-10-08: Regla nueva: todo lo público (README, textos de la app, ayuda, comentarios) en inglés. Traducidos flypad_bridge.py y drivers/README.md; regla anotada en CLAUDE.md.
- 2026-10-08: H3 hecho: instalador oficial de ViGEmBus v1.22.0 (firma válida de Nefarius, SHA-256 anotado) y su licencia BSD-3 guardados en drivers/.
- 2026-10-08: H2 cerrado. Probado en el equipo de pruebas: uso normal sin cambios; al apagar el Bluetooth avisa y reconecta solo al encenderlo. Retoque: el log muestra «Flypad» cuando Windows no da el nombre del dispositivo.
- 2026-10-08: H2 implementado y probado en Marcianito (falta ViGEmBus, Bluetooth apagado/ausente simulado, la ventana espera a Intro ante un error). Pendiente de probar en el equipo de pruebas.
- 2026-10-08: H1 cerrado. Probado en el equipo de pruebas: funciona sin keep-alive, así que se elimina del código. Versiones fijadas: bleak 3.0.2, vgamepad 0.1.0 (Python 3.14).
- 2026-10-08: H1 hecho: keep-alive pasa a ser opcional (`--keepalive`), limpieza del script, `requirements.txt` y `.gitignore`. Decidido: consola, sin icono de bandeja. Plan por hitos H1–H6.
- 2026-10-08: guppy/STATUS.md creado.
