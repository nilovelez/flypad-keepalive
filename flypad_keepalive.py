# -*- coding: utf-8 -*-
"""
flypad_keepalive.py — Flypad Keepalive, graphical version (the one packaged as FlypadKeepalive.exe).

A small window that shows the Flypad, the Bluetooth state, the controller battery and the
status messages. The bridge itself (flypad_bridge.run) runs in a background thread with its
own asyncio loop and reports back through a queue that the Tk main loop polls.

    python flypad_keepalive.py                # normal
    python flypad_keepalive.py --no-gamepad   # diagnostics: no virtual controller
    python flypad_keepalive.py --address C6:41:41:93:4B:73
"""

import argparse
import asyncio
import ctypes
import os
import queue
import sys
import threading
import tkinter as tk
import webbrowser

import flypad_bridge as bridge

WIDTH, HEIGHT = 480, 360
MARGIN = 16
ICON = 32

TEXT_COLOR = "#333333"
SUB_COLOR = "#777777"
ERROR_COLOR = "#C62828"
LINK_COLOR = "#1565C0"

REPO_URL = "https://github.com/nilovelez/flypad-keepalive/"

# Texts shown under the controller for each state: (title, subtitle)
STATE_TEXTS = {
    bridge.SEARCHING:    ("Looking for the Flypad...", "Turn it on if it isn't."),
    bridge.BT_OFF:       ("Bluetooth is turned off.", "Turn it on in Windows; the program keeps waiting."),
    bridge.CONNECTING:   ("Connecting...", ""),
    bridge.CONNECTED:    ("Connected. The controller is ready to use.", ""),
    bridge.DISCONNECTED: ("Disconnected.", "Looking for it again..."),
}


def asset(name):
    """Path to a file in assets/, both from source and from the PyInstaller .exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets", name)


def split_message(message):
    """Split an error message into a short title (first sentence) and the rest."""
    head, sep, rest = message.partition(". ")
    return (head + "." if sep else head), rest


class QueueReporter:
    """Reporter for flypad_bridge.run that hands every event to the GUI thread."""

    def __init__(self, q):
        self.q = q

    def status(self, state, message):
        self.q.put(("status", state, message))

    def info(self, message):
        pass

    def battery(self, percent):
        self.q.put(("battery", percent))


class BridgeThread(threading.Thread):
    """Runs the bridge's asyncio loop off the Tk thread."""

    def __init__(self, q, address, gamepad):
        super().__init__(daemon=True)
        self.q = q
        self.address = address
        self.gamepad = gamepad
        self.loop = None
        self.task = None

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.task = self.loop.create_task(
            bridge.run(address=self.address, gamepad=self.gamepad, reporter=QueueReporter(self.q)))
        try:
            self.loop.run_until_complete(self.task)
        except asyncio.CancelledError:
            pass
        except bridge.FatalError as e:
            self.q.put(("fatal", str(e), e.url))
        except Exception as e:
            self.q.put(("fatal", "Unexpected error. %s" % e, None))
        finally:
            self.loop.close()

    def stop(self):
        if self.loop and self.task and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.task.cancel)


class App:
    def __init__(self, root, worker):
        self.root = root
        self.worker = worker
        self.q = worker.q
        self.battery = None
        self.connected = False

        root.title("Flypad Keepalive")
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self.close)

        self.img = {name: tk.PhotoImage(file=asset(name + ".png")) for name in (
            "background", "background-off", "bluetooth", "bluetooth-off", "battery", "battery-off")}
        root.iconbitmap(default=asset(os.path.join("app-icon", "icon.ico")))

        c = self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, highlightthickness=0, bg="white")
        c.pack()
        self.bg = c.create_image(0, 0, image=self.img["background-off"], anchor="nw")
        self.bt = c.create_image(MARGIN, MARGIN, image=self.img["bluetooth"], anchor="nw")
        self.batt = c.create_image(WIDTH - MARGIN, MARGIN, image=self.img["battery-off"], anchor="ne")
        self.pct = c.create_text(WIDTH - MARGIN - ICON - 6, MARGIN + ICON // 2, text="", anchor="e",
                                 font=("Segoe UI Semibold", 11), fill=TEXT_COLOR)
        self.title = c.create_text(WIDTH // 2, 260, text="", font=("Segoe UI Semibold", 11),
                                   fill=TEXT_COLOR, width=WIDTH - 40, justify="center")
        self.sub = c.create_text(WIDTH // 2, 285, text="", font=("Segoe UI", 9),
                                 fill=SUB_COLOR, width=WIDTH - 40, justify="center")
        self.link = c.create_text(WIDTH // 2, 308, text="", font=("Segoe UI", 9, "underline"),
                                  fill=LINK_COLOR)
        self.link_url = None
        c.tag_bind(self.link, "<Button-1>", lambda _e: self.link_url and webbrowser.open(self.link_url))
        c.tag_bind(self.link, "<Enter>", lambda _e: c.config(cursor="hand2" if self.link_url else ""))
        c.tag_bind(self.link, "<Leave>", lambda _e: c.config(cursor=""))

        # Credit in the bottom-left corner, linking to the project page
        self.repo = c.create_text(MARGIN, HEIGHT - MARGIN + 4, text="© Nilo Velez · GPL-3.0 Licensed",
                                  anchor="sw", font=("Segoe UI", 8), fill=SUB_COLOR)
        c.tag_bind(self.repo, "<Button-1>", lambda _e: webbrowser.open(REPO_URL))
        c.tag_bind(self.repo, "<Enter>", lambda _e: (c.config(cursor="hand2"),
                                                     c.itemconfigure(self.repo, fill=LINK_COLOR)))
        c.tag_bind(self.repo, "<Leave>", lambda _e: (c.config(cursor=""),
                                                     c.itemconfigure(self.repo, fill=SUB_COLOR)))

        self.show_status(bridge.SEARCHING)
        self.poll()

    # --- updates -----------------------------------------------------------------------------

    def set_texts(self, title, sub="", color=TEXT_COLOR, link_url=None):
        c = self.canvas
        c.itemconfigure(self.title, text=title, fill=color)
        c.itemconfigure(self.sub, text=sub)
        # Keep the link right under the subtitle, which may wrap to several lines
        bottom = c.bbox(self.sub)[3] if sub else c.bbox(self.title)[3]
        c.coords(self.link, WIDTH // 2, bottom + 14)
        self.link_url = link_url
        c.itemconfigure(self.link, text="Download ViGEmBus" if link_url else "")

    def show_status(self, state):
        self.connected = state == bridge.CONNECTED
        c = self.canvas
        c.itemconfigure(self.bg, image=self.img["background" if self.connected else "background-off"])
        c.itemconfigure(self.bt, image=self.img["bluetooth-off" if state == bridge.BT_OFF else "bluetooth"])
        self.show_battery()
        self.set_texts(*STATE_TEXTS[state])

    def show_battery(self):
        c = self.canvas
        if self.connected and self.battery is not None:
            c.itemconfigure(self.batt, image=self.img["battery"])
            c.itemconfigure(self.pct, text="%d%%" % self.battery)
        else:
            c.itemconfigure(self.batt, image=self.img["battery-off"])
            c.itemconfigure(self.pct, text="")

    def show_fatal(self, message, url):
        self.connected = False
        self.canvas.itemconfigure(self.bg, image=self.img["background-off"])
        self.show_battery()
        title, sub = split_message(message)
        self.set_texts(title, sub, ERROR_COLOR, url)

    def poll(self):
        try:
            while True:
                event = self.q.get_nowait()
                if event[0] == "status":
                    self.show_status(event[1])
                elif event[0] == "battery":
                    self.battery = event[1]
                    self.show_battery()
                elif event[0] == "fatal":
                    self.show_fatal(event[1], event[2])
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def close(self):
        # Cancelling the bridge task disconnects and releases the virtual controller
        self.worker.stop()
        self.worker.join(timeout=3)
        self.root.destroy()


def main():
    ap = argparse.ArgumentParser(description="Flypad Keepalive: Parrot Flypad BLE -> virtual Xbox 360 controller")
    ap.add_argument("--address", help="Flypad MAC address (if there is more than one)")
    ap.add_argument("--no-gamepad", action="store_true", help="don't create a virtual controller (diagnostics)")
    args = ap.parse_args()

    # Crisp images and text on scaled displays: render at real pixels instead of being stretched
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    worker = BridgeThread(queue.Queue(), args.address, not args.no_gamepad)
    App(root, worker)
    worker.start()
    root.mainloop()


if __name__ == "__main__":
    main()
