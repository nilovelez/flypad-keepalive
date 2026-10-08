# -*- coding: utf-8 -*-
"""
flypad_bridge.py — Puente Parrot Flypad (BLE) -> mando virtual Xbox 360

Que hace
--------
1. Busca el Flypad por Bluetooth LE (nombre "FLYPAD" o servicio 9e35fa00) y se conecta.
2. Lee sus entradas (frames de 7 bytes en la caracteristica 9e35fa01) y las vuelca
   a un mando virtual de Xbox 360 (ViGEmBus), que es lo que ven Liftoff/Uncrashed.
3. Si el mando se desconecta, vuelve a buscarlo y se reconecta solo.

Protocolo sacado de FreeFlight Mini 5.5.9 (com.parrot.freeflight3.RemoteController
y FrameResolver).

Requisitos
----------
    pip install -r requirements.txt
y el driver ViGEmBus (v1.22.0) instalado en el sistema.

Uso
---
    python flypad_bridge.py                 # normal
    python flypad_bridge.py --no-gamepad    # solo diagnostico: imprime frames, sin mando virtual
    python flypad_bridge.py --address C6:41:41:93:4B:73   # si hay varios Flypad

Antes de lanzarlo: enciende el Flypad (LED verde parpadeando) y NO lo tengas
conectado a ninguna otra app/movil. Si lo emparejaste antes en Ajustes de Windows,
no hace falta quitarlo, pero si da problemas al conectar, prueba a eliminarlo de ahi.
"""

import argparse
import asyncio
import sys
import time

from bleak import BleakClient, BleakScanner

SERVICE_UUID = "9e35fa00-4344-44d4-a2e2-0c7f6046878b"
INPUT_UUID   = "9e35fa01-4344-44d4-a2e2-0c7f6046878b"   # notificaciones mando -> PC

# Mascaras de botones (FrameResolver.Button)
BTN_TAKEOFF   = 0x0001
BTN_1         = 0x0002
BTN_2         = 0x0004
BTN_3         = 0x0008
BTN_4         = 0x0010
BTN_R1        = 0x0020
BTN_R2        = 0x0040
BTN_L1        = 0x0080
BTN_L2        = 0x0100
BTN_JOY_LEFT  = 0x0200
BTN_JOY_RIGHT = 0x0400


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def axis(b, invert=False):
    v = (b - 128) / 127.0
    v = max(-1.0, min(1.0, v))
    return -v if invert else v


class Pad:
    """Mando virtual Xbox 360. Si enabled=False solo imprime."""

    def __init__(self, enabled):
        self.enabled = enabled
        self.last = None
        self.battery = None
        if enabled:
            import vgamepad as vg
            self.vg = vg
            self.gp = vg.VX360Gamepad()
            B = vg.XUSB_BUTTON
            self.map = [
                (BTN_TAKEOFF,   B.XUSB_GAMEPAD_START),
                (BTN_1,         B.XUSB_GAMEPAD_X),
                (BTN_2,         B.XUSB_GAMEPAD_Y),
                (BTN_3,         B.XUSB_GAMEPAD_B),
                (BTN_4,         B.XUSB_GAMEPAD_A),
                (BTN_R1,        B.XUSB_GAMEPAD_RIGHT_SHOULDER),
                (BTN_L1,        B.XUSB_GAMEPAD_LEFT_SHOULDER),
                (BTN_JOY_LEFT,  B.XUSB_GAMEPAD_LEFT_THUMB),
                (BTN_JOY_RIGHT, B.XUSB_GAMEPAD_RIGHT_THUMB),
            ]

    def on_frame(self, data):
        if len(data) != 7:
            return
        battery = data[0]
        buttons = data[1] | (data[2] << 8)
        rx, ry, lx, ly = data[3], data[4], data[5], data[6]

        if battery != self.battery:
            self.battery = battery
            log("Bateria del mando: %d%%" % battery)

        if not self.enabled:
            frame = bytes(data)
            if frame != self.last:
                self.last = frame
                print("\r  frame: %s   botones=0x%04X   " % (frame.hex(" "), buttons), end="", flush=True)
            return

        gp = self.gp
        for mask, xbtn in self.map:
            if buttons & mask:
                gp.press_button(button=xbtn)
            else:
                gp.release_button(button=xbtn)
        gp.left_trigger(value=255 if buttons & BTN_L2 else 0)
        gp.right_trigger(value=255 if buttons & BTN_R2 else 0)
        gp.left_joystick_float(x_value_float=axis(lx), y_value_float=axis(ly, invert=True))
        gp.right_joystick_float(x_value_float=axis(rx), y_value_float=axis(ry, invert=True))
        gp.update()

    def reset(self):
        """Suelta todo al desconectarse, para que el dron virtual no se quede con el stick pegado."""
        if self.enabled:
            self.gp.reset()
            self.gp.update()


async def find_flypad(address):
    if address:
        return await BleakScanner.find_device_by_address(address, timeout=8.0)

    def match(dev, adv):
        name = (dev.name or adv.local_name or "").upper()
        uuids = [u.lower() for u in (adv.service_uuids or [])]
        return "FLYPAD" in name or SERVICE_UUID in uuids

    return await BleakScanner.find_device_by_filter(match, timeout=8.0)


async def run(args):
    pad = Pad(enabled=not args.no_gamepad)
    if pad.enabled:
        log("Mando virtual Xbox 360 creado.")

    while True:
        log("Buscando el Flypad... (enciendelo si no lo esta)")
        dev = await find_flypad(args.address)
        if dev is None:
            await asyncio.sleep(2)
            continue

        log("Encontrado: %s (%s). Conectando..." % (dev.name, dev.address))
        loop = asyncio.get_running_loop()
        disconnected = asyncio.Event()

        def on_disconnect(_client):
            loop.call_soon_threadsafe(disconnected.set)

        t0 = time.monotonic()
        try:
            async with BleakClient(dev, disconnected_callback=on_disconnect, timeout=20.0) as client:
                t0 = time.monotonic()
                await client.start_notify(INPUT_UUID, lambda _s, d: pad.on_frame(d))
                log("Conectado. Ya puedes usar el mando.")
                await disconnected.wait()
        except Exception as e:
            log("Error de conexion: %s" % e)
        finally:
            pad.reset()

        if args.no_gamepad:
            print()  # cierra la linea de frames que se va sobrescribiendo con \r
        log("Desconectado tras %d s. Reintentando..." % (time.monotonic() - t0))
        await asyncio.sleep(2)


def main():
    ap = argparse.ArgumentParser(description="Puente Parrot Flypad BLE -> mando Xbox 360 virtual")
    ap.add_argument("--address", help="MAC del Flypad (si hay varios)")
    ap.add_argument("--no-gamepad", action="store_true", help="no crear mando virtual; solo imprimir frames")
    args = ap.parse_args()
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        print("\nSaliendo.")


if __name__ == "__main__":
    main()
