# -*- coding: utf-8 -*-
"""
flypad_bridge.py — Flypad Keepalive: Parrot Flypad (BLE) -> virtual Xbox 360 controller

What it does
------------
1. Finds the Flypad over Bluetooth LE (name "FLYPAD" or service 9e35fa00) and connects to it.
2. Reads its inputs (7-byte frames on characteristic 9e35fa01) and feeds them to a
   virtual Xbox 360 controller (ViGEmBus), which is what Liftoff/Uncrashed see.
3. If the controller disconnects, it looks for it again and reconnects on its own.

Protocol taken from FreeFlight Mini 5.5.9 (com.parrot.freeflight3.RemoteController
and FrameResolver).

Requirements
------------
    pip install -r requirements.txt
plus the ViGEmBus driver (v1.22.0) installed on the system.

Usage
-----
    python flypad_bridge.py                 # normal
    python flypad_bridge.py --no-gamepad    # diagnostics only: print frames, no virtual controller
    python flypad_bridge.py --address C6:41:41:93:4B:73   # if there is more than one Flypad

Before starting it: turn the Flypad on (green LED blinking) and do NOT have it
connected to any other app/phone. If you paired it before in Windows Settings,
there is no need to remove it, but if it has trouble connecting, try removing it there.
"""

import argparse
import asyncio
import sys
import time

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakBluetoothNotAvailableError, BleakBluetoothNotAvailableReason

VIGEMBUS_URL = "https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0"

SERVICE_UUID = "9e35fa00-4344-44d4-a2e2-0c7f6046878b"
INPUT_UUID   = "9e35fa01-4344-44d4-a2e2-0c7f6046878b"   # notifications controller -> PC

# Button masks (FrameResolver.Button)
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


class FatalError(Exception):
    """Error the user has to fix; the message is shown as is and the program exits."""


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


def pause_before_exit():
    """Let the user read the error; when the .exe is double-clicked the window would close.
    (We don't try to detect whether the console is ours: the venv and the PyInstaller .exe
    spawn a child process, so GetConsoleProcessList is no use.)"""
    if sys.stdin and sys.stdin.isatty():
        try:
            input("\nPress Enter to close this window...")
        except (EOFError, KeyboardInterrupt):
            pass


def axis(b, invert=False):
    v = (b - 128) / 127.0
    v = max(-1.0, min(1.0, v))
    return -v if invert else v


class Pad:
    """Virtual Xbox 360 controller. If enabled=False it only prints."""

    def __init__(self, enabled):
        self.enabled = enabled
        self.last = None
        self.battery = None
        if enabled:
            # vgamepad connects to the ViGEmBus driver as soon as it is imported
            try:
                import vgamepad as vg
                self.gp = vg.VX360Gamepad()
            except Exception as e:
                if "VIGEM_ERROR_BUS_NOT_FOUND" in str(e):
                    raise FatalError(
                        "The ViGEmBus driver was not found. It is needed to create the virtual\n"
                        "Xbox 360 controller. Install ViGEmBus v1.22.0 and open the program again:\n"
                        "    " + VIGEMBUS_URL)
                raise FatalError(
                    "Could not create the virtual Xbox 360 controller (%s).\n"
                    "Check that the ViGEmBus v1.22.0 driver is installed:\n"
                    "    %s" % (e, VIGEMBUS_URL))
            self.vg = vg
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
            log("Controller battery: %d%%" % battery)

        if not self.enabled:
            frame = bytes(data)
            if frame != self.last:
                self.last = frame
                print("\r  frame: %s   buttons=0x%04X   " % (frame.hex(" "), buttons), end="", flush=True)
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
        """Release everything on disconnect, so the virtual drone isn't left with a stuck stick."""
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


def bluetooth_error(e):
    """FatalError with an understandable message for a BleakBluetoothNotAvailableError."""
    R = BleakBluetoothNotAvailableReason
    if e.reason == R.NO_BLUETOOTH:
        msg = ("No Bluetooth adapter was found on this PC.\n"
               "Bluetooth 4.0 (BLE) or later is required; if the PC doesn't have it,\n"
               "a USB Bluetooth adapter will do.")
    elif e.reason == R.NO_BLE_CENTRAL_ROLE:
        msg = ("This PC's Bluetooth adapter can't connect to Bluetooth LE controllers.\n"
               "Try a different adapter (Bluetooth 4.0 or later).")
    elif e.reason in (R.DENIED_BY_USER, R.DENIED_BY_SYSTEM, R.DENIED_BY_UNKNOWN):
        msg = ("Windows is not allowing this program to use Bluetooth.\n"
               "Check the Bluetooth permissions in Windows Settings.")
    else:
        msg = "Bluetooth is not available (%s)." % (e.args[0] if e.args else e)
    return FatalError(msg)


async def run(args):
    pad = Pad(enabled=not args.no_gamepad)
    if pad.enabled:
        log("Virtual Xbox 360 controller created.")

    bt_off = False
    while True:
        if not bt_off:
            log("Looking for the Flypad... (turn it on if it isn't)")
        try:
            dev = await find_flypad(args.address)
        except BleakBluetoothNotAvailableError as e:
            if e.reason != BleakBluetoothNotAvailableReason.POWERED_OFF:
                raise bluetooth_error(e)
            # Powered off can be fixed without restarting: warn once and keep waiting
            if not bt_off:
                log("Bluetooth is turned off. Turn it on in Windows; the program keeps waiting.")
                bt_off = True
            await asyncio.sleep(2)
            continue
        if bt_off:
            log("Bluetooth turned on.")
            bt_off = False
        if dev is None:
            await asyncio.sleep(2)
            continue

        # When found by service UUID, Windows may not provide the name
        log("Found: %s (%s). Connecting..." % (dev.name or "Flypad", dev.address))
        loop = asyncio.get_running_loop()
        disconnected = asyncio.Event()

        def on_disconnect(_client):
            loop.call_soon_threadsafe(disconnected.set)

        t0 = time.monotonic()
        try:
            async with BleakClient(dev, disconnected_callback=on_disconnect, timeout=20.0) as client:
                t0 = time.monotonic()
                await client.start_notify(INPUT_UUID, lambda _s, d: pad.on_frame(d))
                log("Connected. The controller is ready to use.")
                await disconnected.wait()
        except Exception as e:
            log("Connection error: %s" % e)
        finally:
            pad.reset()

        if args.no_gamepad:
            print()  # end the frame line that keeps being overwritten with \r
        log("Disconnected after %d s. Retrying..." % (time.monotonic() - t0))
        await asyncio.sleep(2)


def main():
    ap = argparse.ArgumentParser(description="Flypad Keepalive: Parrot Flypad BLE -> virtual Xbox 360 controller")
    ap.add_argument("--address", help="Flypad MAC address (if there is more than one)")
    ap.add_argument("--no-gamepad", action="store_true", help="don't create a virtual controller; only print frames")
    args = ap.parse_args()
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        print("\nExiting.")
    except FatalError as e:
        print("\nERROR: %s" % e, flush=True)
        pause_before_exit()
        sys.exit(1)
    except Exception:
        import traceback
        print("\nUnexpected ERROR:", flush=True)
        traceback.print_exc()
        pause_before_exit()
        sys.exit(1)


if __name__ == "__main__":
    main()
