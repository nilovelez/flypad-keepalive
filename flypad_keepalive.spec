# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for FlypadKeepalive.exe (single file, console window).
# Build with build.ps1, or: pyinstaller --clean --noconfirm flypad_keepalive.spec

import importlib.util
import os

# vgamepad loads ViGEmClient.dll from a path relative to its own package
# (vgamepad/win/vigem/client/<arch>/ViGEmClient.dll), so it must keep that path inside the .exe.
# Locate the package without importing it: importing vgamepad fails if ViGEmBus is not installed.
VGAMEPAD_DIR = importlib.util.find_spec("vgamepad").submodule_search_locations[0]
VIGEM_CLIENT_DLL = os.path.join(VGAMEPAD_DIR, "win", "vigem", "client", "x64", "ViGEmClient.dll")

a = Analysis(
    ["flypad_bridge.py"],
    pathex=[],
    binaries=[(VIGEM_CLIENT_DLL, "vgamepad/win/vigem/client/x64")],
    datas=[],  # only the DLL above: the old ViGEmBus MSIs bundled with vgamepad are left out
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "pydoc", "test"],
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
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
