"""Tema visual moderno (blanco -> azul marino) para qNMR Assistant.

Paleta:
    navy oscuro  #0B2545   navy medio  #13315C   azul  #1B5299
    acento       #2E8BC0   acento claro #5BB0E0   fondo #EAF1F8
    tarjeta      #FFFFFF   borde       #D8E4F0    texto #0B2545   apagado #5A7184
"""

# Paleta (por si se necesita en código Python, p.ej. sombras)
NAVY = "#0B2545"
NAVY_MED = "#13315C"
BLUE = "#1B5299"
ACCENT = "#2E8BC0"
ACCENT_LIGHT = "#5BB0E0"
BG = "#EAF1F8"
CARD = "#FFFFFF"
BORDER = "#D8E4F0"
TEXT = "#0B2545"
MUTED = "#5A7184"

STYLESHEET = f"""
* {{
    font-family: 'Segoe UI', 'Segoe UI Variable', Arial, sans-serif;
    color: {TEXT};
}}

QMainWindow, QStackedWidget, QDialog {{
    background-color: {BG};
}}

/* ---- Barra de menú (degradado navy) ---- */
QMenuBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {NAVY_MED}, stop:1 {NAVY});
    color: white;
    padding: 4px 6px;
    font-size: 10pt;
}}
QMenuBar::item {{
    background: transparent;
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
}}
QMenuBar::item:selected {{
    background: rgba(255, 255, 255, 0.18);
}}
QMenu {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 22px;
    border-radius: 6px;
}}
QMenu::item:selected {{
    background: {ACCENT};
    color: white;
}}

/* ---- Barra de navegación (pestañas) ---- */
QFrame#navBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF, stop:1 #E8F0FA);
    border-bottom: 1px solid {BORDER};
}}
QPushButton#navButton {{
    background: transparent;
    color: {MUTED};
    border: none;
    border-radius: 9px;
    padding: 9px 20px;
    font-size: 11pt;
    font-weight: 600;
}}
QPushButton#navButton:hover {{
    background: rgba(46, 139, 192, 0.12);
    color: {BLUE};
}}
QPushButton#navButton:checked {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {ACCENT}, stop:1 {BLUE});
    color: white;
}}

/* ---- Tarjetas ---- */
QFrame#card {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

/* ---- Títulos de bloque ---- */
QLabel#blockTitle {{
    color: {NAVY};
    font-size: 15pt;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 2px 0;
}}
QLabel#subTitle {{
    color: {ACCENT};
    font-size: 11pt;
    font-weight: 600;
}}
QLabel#fieldLabel {{
    color: {MUTED};
    font-size: 10pt;
    font-weight: 600;
}}

/* ---- Entradas de texto y desplegables ---- */
QLineEdit {{
    background-color: #FBFDFF;
    border: 1.5px solid {BORDER};
    border-radius: 9px;
    padding: 8px 10px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus {{
    border: 1.5px solid {ACCENT};
    background-color: #FFFFFF;
}}
QLineEdit:hover {{
    border: 1.5px solid {ACCENT_LIGHT};
}}

QComboBox {{
    background-color: #FBFDFF;
    border: 1.5px solid {BORDER};
    border-radius: 9px;
    padding: 8px 10px;
}}
QComboBox:hover {{ border: 1.5px solid {ACCENT_LIGHT}; }}
QComboBox:focus {{ border: 1.5px solid {ACCENT}; }}
QComboBox::drop-down {{
    border: none;
    width: 26px;
}}
QComboBox QAbstractItemView {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: {ACCENT};
    selection-color: white;
    padding: 4px;
}}

/* ---- Valores de solo lectura (datos del IS) ---- */
QLabel#readonlyValue {{
    background-color: #F0F6FC;
    border: 1px solid {BORDER};
    border-radius: 9px;
    padding: 8px;
    color: {NAVY};
    font-weight: 600;
}}

/* ---- Resultados grandes ---- */
QLabel#resultValue {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF, stop:1 #E8F2FB);
    border: 1.5px solid {ACCENT_LIGHT};
    border-radius: 12px;
    padding: 14px;
    color: {NAVY};
    font-size: 22pt;
    font-weight: 700;
}}

/* ---- Botones primarios (degradado azul -> navy) ---- */
QPushButton#primaryButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {ACCENT}, stop:1 {BLUE});
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 12pt;
    font-weight: 700;
    letter-spacing: 0.5px;
}}
QPushButton#primaryButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {ACCENT_LIGHT}, stop:1 {ACCENT});
}}
QPushButton#primaryButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {BLUE}, stop:1 {NAVY});
}}

/* ---- Botón secundario (contorno) ---- */
QPushButton#secondaryButton {{
    background: #FFFFFF;
    color: {BLUE};
    border: 1.5px solid {ACCENT};
    border-radius: 12px;
    font-size: 12pt;
    font-weight: 700;
}}
QPushButton#secondaryButton:hover {{
    background: #EAF4FC;
}}
QPushButton#secondaryButton:pressed {{
    background: #D8EAF8;
}}

/* ---- Botón enlace (desplegar opcionales) ---- */
QPushButton#linkButton {{
    background: transparent;
    color: {ACCENT};
    border: none;
    font-size: 10pt;
    font-weight: 600;
    text-align: left;
}}
QPushButton#linkButton:hover {{
    color: {BLUE};
}}

/* ---- Filas de réplicas ---- */
QFrame#repRow {{
    background-color: #F6FAFE;
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
QLabel#repNum {{
    color: white;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {ACCENT}, stop:1 {BLUE});
    border-radius: 13px;
    font-weight: 700;
    font-size: 10pt;
}}
QLabel#repResult {{
    color: {NAVY};
    font-weight: 700;
    font-size: 12pt;
}}

/* ---- Botones +/- de réplicas ---- */
QPushButton#stepButton {{
    background: #FFFFFF;
    color: {BLUE};
    border: 1.5px solid {ACCENT};
    border-radius: 14px;
    font-size: 14pt;
    font-weight: 700;
}}
QPushButton#stepButton:hover {{ background: #EAF4FC; }}
QPushButton#stepButton:pressed {{ background: #D8EAF8; }}
QPushButton#stepButton:disabled {{
    color: #AEC2D6; border-color: #CFE0EF; background: #F4F8FC;
}}
QLabel#repCount {{
    color: {NAVY};
    font-size: 13pt;
    font-weight: 700;
}}

/* ---- Tarjeta resumen (media / RSD) ---- */
QLabel#summaryValue {{
    color: {NAVY};
    font-size: 20pt;
    font-weight: 700;
}}

/* ---- Área de resultados de preparación ---- */
QTextEdit#prepLogger {{
    background-color: #FBFDFF;
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 10px;
    font-size: 14pt;
    color: {NAVY};
}}

/* ---- Tabla del editor de estándares ---- */
QTableWidget {{
    background-color: #FBFDFF;
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: #E6EEF7;
    selection-background-color: {ACCENT_LIGHT};
    selection-color: {NAVY};
}}
QHeaderView::section {{
    background: {NAVY_MED};
    color: white;
    padding: 8px;
    border: none;
    font-weight: 600;
}}
QTableWidget::item {{
    padding: 6px;
}}

/* ---- Barra de estado ---- */
QStatusBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {NAVY_MED}, stop:1 {NAVY});
    color: #DCE8F4;
}}
QStatusBar QLabel {{
    color: #DCE8F4;
    font-size: 8pt;
}}
"""
