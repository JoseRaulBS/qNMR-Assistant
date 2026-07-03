class Config:
    """Constantes de marca y formato. Los datos editables viven en otros sitios:
    estándares internos -> standards.py / JSON;  ajustes -> prefs.py / JSON;
    textos de interfaz -> i18n.py."""

    # LICENCIA
    deadline_date = (2099, 12, 31)

    # TEXTOS Y FORMATO
    WindowTitle = "qNMR Assistant 2026"
    app_name = "qNMR Assistant"
    version = "2026.1"
    font = "Segoe UI"  # tipografía moderna (el aspecto general lo define style.py)
    blocks_title_size = 20
    results_size = 30
    button_colors = "#00B7DD"
