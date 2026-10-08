# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for FlypadKeepalive.exe (single file, graphical window, no console).
# Build with build.ps1, or: pyinstaller --clean --noconfirm flypad_keepalive.spec

import importlib.util
import os

# vgamepad loads ViGEmClient.dll from a path relative to its own package
# (vgamepad/win/vigem/client/<arch>/ViGEmClient.dll), so it must keep that path inside the .exe.
# Locate the package without importing it: importing vgamepad fails if ViGEmBus is not installed.
VGAMEPAD_DIR = importlib.util.find_spec("vgamepad").submodule_search_locations[0]
VIGEM_CLIENT_DLL = os.path.join(VGAMEPAD_DIR, "win", "vigem", "client", "x64", "ViGEmClient.dll")

a = Analysis(
    ["flypad_keepalive.py"],
    pathex=[],
    binaries=[(VIGEM_CLIENT_DLL, "vgamepad/win/vigem/client/x64")],
    # Window images. Only the DLL above from vgamepad: its old ViGEmBus MSIs are left out.
    datas=[
        (os.path.join("assets", "*.png"), "assets"),
        (os.path.join("assets", "app-icon", "icon.ico"), os.path.join("assets", "app-icon")),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["unittest", "pydoc", "test"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FlypadKeepalive",
    icon=os.path.join("assets", "app-icon", "icon.ico"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
