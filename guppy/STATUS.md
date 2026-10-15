# Status

The bridge works: it presents the Flypad (BLE) as a virtual Xbox 360 controller and has been tested for more than 10 minutes in a row in Uncrashed without dropouts. Published as v1.0.0: executable with a graphical window, README and GPL-3.0 license. All milestones (H1–H7) are closed. Nothing is pending. Decided: the final executable is a small graphical window that stays open (no console, no tray icon), in the style of the Logitech Options main screen.

Milestone plan:

- [x] H1. Tidy up: keep-alive removed (tested: not needed), docstring up to date, `requirements.txt` with pinned versions, `.gitignore`.
- [x] H2. Clear error messages: ViGEmBus missing, Bluetooth off or no adapter; the window must not close abruptly on an error.
- [x] H3. Store the ViGEmBus v1.22.0 installer in `drivers/` with its license.
- [x] H4. Single `.exe` with PyInstaller (`.spec` + build script), without including `guppy/`.
- [x] H5. Graphical interface: small, polished window with the controller image in the center, a Bluetooth icon and a message area below (reference: Logitech Options). The final `.exe` is no longer a console app.
- [x] H6. Presentable repo: `LICENSE` with the GPL-3.0 (the window already says "GPL-3.0 Licensed"); README: requirements, driver installation, usage, button mapping, common problems, SmartScreen warning (the `.exe` is not signed).
- [x] H7. Publish a GitHub release with the `.exe`.

## Backlog (next version)

- Version number in the executable (.exe properties: Details) and in the window footer, next to the credit.

## Log

- 2026-10-16: migrated to the new Guppy format (STATUS.json).
- 2026-10-08: Backlog: version number in the .exe and in the window footer for the next version. 1.0.0 stays as it is.
- 2026-10-08: H7 closed: v1.0.0 release published by Nilo (https://github.com/nilovelez/flypad-keepalive/releases/tag/v1.0.0; .exe SHA-256 verified). README with a latest-version badge and a direct download of the latest release. All milestones completed.
- 2026-10-08: H6 closed. The button table stays as it is (it comes from the code).
- 2026-10-08: The driver link (app and README) becomes a direct download (/raw/main/drivers/...).
- 2026-10-08: Touch-ups: the driver error links to the repo's copy in drivers/ and splits the text into two lines; status texts moved up; README without the icon, without the link to Parrot, and with a framed screenshot of the window (docs/images/window.png).
- 2026-10-08: H6 done: README in English (introduction, why, installation, SmartScreen, usage with screenshots, buttons, troubleshooting, how it works, build, credits), GPL-3.0 LICENSE and screenshots in docs/images/. The download link points to Releases, which is still empty (H7).
- 2026-10-08: H5 closed: graphical window tested with the Flypad on the test machine.
- 2026-10-08: The repo link becomes a credit: "© Nilo Velez · GPL-3.0 Licensed". The GPL-3.0 LICENSE still has to be added to the repo (H6).
- 2026-10-08: Link to the GitHub repo in the bottom-left corner of the window.
- 2026-10-08: App icon (assets/app-icon/icon.ico, by Nilo) set on the window and the .exe.
- 2026-10-08: H5 done on Marcianito after the mockup was approved: flypad_keepalive.py (Tkinter, images from assets/) and a .exe without a console (15.2 MB). Tested here: driver error with link, real BLE scan and clean shutdown. Still to be tested with the Flypad.
- 2026-10-08: H4 closed: the .exe works in a game on the test machine. H5 decided: Tkinter; Nilo provides the controller image (photo on a white background).
- 2026-10-08: New milestone H5, graphical interface (the README moves to H6 and the release to H7). The .exe triggers SmartScreen on the test machine: to be documented in the README.
- 2026-10-08: H4 done on Marcianito: build.ps1 + flypad_keepalive.spec generate FlypadKeepalive.exe (11.8 MB). Tested here: --help, missing-driver error and BLE scan. Still to be tested with the Flypad on the test machine.
- 2026-10-08: H3 closed.
- 2026-10-08: New rule: everything public (README, app texts, help, comments) in English. flypad_bridge.py and drivers/README.md translated; rule noted in CLAUDE.md.
- 2026-10-08: H3 done: official ViGEmBus v1.22.0 installer (valid Nefarius signature, SHA-256 noted) and its BSD-3 license stored in drivers/.
- 2026-10-08: H2 closed. Tested on the test machine: normal use unchanged; when Bluetooth is turned off it warns and reconnects on its own when it is turned back on. Touch-up: the log shows "Flypad" when Windows does not provide the device name.
- 2026-10-08: H2 implemented and tested on Marcianito (missing ViGEmBus, Bluetooth off/absent simulated, the window waits for Enter on an error). Still to be tested on the test machine.
- 2026-10-08: H1 closed. Tested on the test machine: it works without keep-alive, so it is removed from the code. Pinned versions: bleak 3.0.2, vgamepad 0.1.0 (Python 3.14).
- 2026-10-08: H1 done: keep-alive becomes optional (`--keepalive`), script cleanup, `requirements.txt` and `.gitignore`. Decided: console, no tray icon. Milestone plan H1–H6.
- 2026-10-08: guppy/STATUS.md created.
