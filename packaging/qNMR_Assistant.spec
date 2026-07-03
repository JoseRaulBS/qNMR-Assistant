# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec portable (Windows / macOS / Linux).

Construir en CADA sistema (PyInstaller no compila de forma cruzada), desde la
raíz del repositorio:
    pyinstaller --noconfirm --clean packaging/qNMR_Assistant.spec
El ejecutable queda en dist/.
"""
import os
import sys

# SPECPATH = carpeta de este archivo (packaging/); el código vive en ../src
SRC = os.path.abspath(os.path.join(SPECPATH, "..", "src"))

if sys.platform == "win32":
    icon = os.path.join(SRC, "assets", "images", "AppIcon.ico")
elif sys.platform == "darwin":
    icon = os.path.join(SRC, "assets", "images", "AppIcon.icns")
else:
    icon = None  # Linux: el icono se asocia con un .desktop, no se incrusta

a = Analysis(
    [os.path.join(SRC, "app.py")],
    pathex=[SRC],
    binaries=[],
    datas=[(os.path.join(SRC, "assets"), "assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PIL", "tkinter", "numpy", "pytest", "pandas"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="qNMR_Assistant",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="qNMR Assistant.app",
        icon=icon,
        bundle_identifier="es.ual.qnmr.assistant",
    )
