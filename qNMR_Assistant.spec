# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec portable (Windows / macOS / Linux).

Construir en CADA sistema (PyInstaller no compila de forma cruzada):
    cd QuantTool2026_modern
    pyinstaller --noconfirm --clean qNMR_Assistant.spec
El ejecutable queda en dist/.
"""
import sys

if sys.platform == "win32":
    icon = "assets/images/AppIcon.ico"
elif sys.platform == "darwin":
    icon = "assets/images/AppIcon.icns"
else:
    icon = None  # Linux: el icono se asocia con un .desktop, no se incrusta

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[("assets", "assets")],
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
