r"""Rutas de datos de usuario (persistencia robusta y multiplataforma).

Los archivos editables (estándares internos, ajustes) NO deben guardarse junto al
código: en un ejecutable PyInstaller esa carpeta es temporal o de solo lectura.
Usamos la carpeta de datos de la aplicación del sistema operativo:
  Windows: %APPDATA%\qNMR\qNMR Assistant
  macOS:   ~/Library/Application Support/qNMR Assistant
  Linux:   ~/.local/share/qNMR Assistant
"""
import os

from PyQt6.QtCore import QStandardPaths


def data_dir():
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if not base:  # fallback por si Qt no resuelve la ruta
        base = os.path.join(os.path.expanduser("~"), ".qnmr_assistant")
    try:
        os.makedirs(base, exist_ok=True)
    except OSError:
        pass
    return base


def data_file(name):
    return os.path.join(data_dir(), name)
