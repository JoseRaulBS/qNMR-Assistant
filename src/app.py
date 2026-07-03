import os
import sys
import time
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6 import QtWidgets, QtGui

from controller import Controller
from model import Model
from view import View
from config import Config
import style


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    # Anclado a la carpeta de este archivo (no al cwd): la app puede lanzarse
    # desde cualquier directorio con `python src/app.py`.
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def set_taskbar_app_id():
    """En Windows, declara un AppUserModelID propio para que la barra de tareas
    use el icono de la app (y no el del intérprete de Python)."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("qnmr.assistant.2026")
        except Exception:
            pass


class SplashScreen(QtWidgets.QSplashScreen):
    path_splash = resource_path('assets/images/splash-image.png')

    def __init__(self):
        super().__init__(QtGui.QPixmap(self.path_splash))


def main():
    set_taskbar_app_id()
    app = QApplication(sys.argv)
    app.setOrganizationName("qNMR")
    app.setApplicationName("qNMR Assistant")
    app.setStyleSheet(style.STYLESHEET)
    app.setWindowIcon(QtGui.QIcon(resource_path('assets/images/AppIcon.ico')))
    splash = SplashScreen()
    splash.show()
    time.sleep(3)

    # LICENCIA
    if datetime.now() > datetime(*Config.deadline_date):
        QMessageBox.critical(None, "Error", "License has expired.")
        return

    model = Model()
    view = View()
    view.show()
    splash.finish(view)

    controller = Controller(view, model)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
