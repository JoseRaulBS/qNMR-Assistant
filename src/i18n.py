"""Traducciones de la interfaz (EN / ES).

Uso:  from i18n import I18n;  I18n.t("btn_calculate")
Cambiar idioma:  I18n.set_language("es")  y luego View.retranslate().
"""


class I18n:
    language = "es"  # idioma por defecto al abrir

    STRINGS = {
        "en": {
            # Menús
            "menu_menu": "&Menu",
            "menu_decimals": "&Decimals",
            "menu_exit": "&Exit",
            "menu_assistant": "&Assistant mode",
            "menu_sample_prep": "&Sample preparation",
            "menu_quantitation": "&Quantitation",
            "menu_language": "&Language",
            "menu_lang_en": "&English",
            "menu_lang_es": "&Spanish",
            "menu_instructions": "&Instructions",
            "menu_about": "&About",
            "nav_prep": "Sample preparation",
            "nav_quant": "Quantitation",
            "nav_standards": "Internal standards",
            "msg_check_fields": "Check the highlighted fields.",
            "btn_copy": "Copy",
            "msg_copied": "Result copied to clipboard.",
            "btn_export_csv": "Export CSV",
            "csv_filter": "CSV file (*.csv)",
            # Barra de estado
            "status_desc": "This is the {app} software. Version {v}",
            "status_msg": "Feel free to quantify!",
            # Títulos de bloque
            "title_sample_prep": "SAMPLE PREPARATION",
            "title_is_data": "IS DATA",
            "title_quantitation": "QUANTITATION",
            "title_results": "RESULTS",
            # Campos comunes
            "ph_insert": "Insert here",
            "lbl_purity": "Purity (%)",
            "lbl_mw": "Molecular weight (g/mol)",
            "lbl_nprotons": "Nº protons",
            "lbl_weighed_is": "Weighed IS (mg)",
            "lbl_nprotons_signal": "Nº of protons of the signal of interest",
            "btn_calculate": "CALCULATE",
            # Preparación
            "lbl_expected_conc": "Sample expected concentration (%)",
            "lbl_final_volume": "Final volume (mL)",
            "lbl_available_is": "Available ISs",
            "btn_restart": "Restart data",
            "lbl_sample_state": "Sample state",
            "opt_solid": "Solid",
            "opt_liquid": "Liquid",
            # Protocolo de preparación
            "prep_header": "Preparation protocol (aiming for similar analyte / IS intensities):",
            "prep_step_weigh_is": "Weigh ~{w} mg of internal standard.",
            "prep_step_weigh_sample": "Weigh ~{m} mg of sample.",
            "prep_step_pipette_sample": "Pipette {v} µL of sample.",
            "prep_step_dissolve": "Make up to {vol} mL with deuterated solvent.",
            # Ajustes de preparación
            "menu_prep_settings": "&Preparation settings",
            "set_title": "Preparation settings",
            "set_is_min": "Minimum IS weight (mg)",
            "set_vmin": "Final volume min (mL)",
            "set_vmax": "Final volume max (mL)",
            "set_min_weighable": "Min. weighable sample (mg)",
            "set_pip_min": "Pipette min (µL)",
            "set_pip_max": "Pipette max (µL)",
            "set_max_conc": "Max sample conc. (mg/mL)",
            "set_save": "Save",
            # Informe / impresión
            "report_title": "qNMR Quantitation Report",
            "report_generated": "Generated {date}  ·  qNMR Assistant v{ver}",
            "report_sample_code": "Sample code",
            "report_analyte": "Analyte",
            "report_analyst": "Analyst",
            "report_solvent": "Deuterated solvent",
            "report_date_field": "Date",
            "report_method": "Method",
            "report_is": "Internal standard",
            "report_purity": "Purity",
            "report_target_signal": "Target signal",
            "report_rep": "#",
            "report_results": "Results",
            "report_preparation": "Sample preparation",
            "report_notes": "Notes",
            "report_footer": "Generated with qNMR Assistant — relative qNMR with internal standard.",
            "report_signature": "Signature",
            "report_dialog_title": "Report details",
            "lbl_analyst": "Analyst",
            "lbl_solvent": "Deuterated solvent",
            "lbl_date": "Date",
            "lbl_notes": "Notes",
            "lbl_prep_details": "Sample preparation details",
            "btn_import_prep": "Import from Sample preparation",
            "btn_preview": "Preview",
            "btn_save_pdf": "Save PDF",
            "popup_no_calc": "Calculate a result first.",
            "pdf_filter": "PDF document (*.pdf)",
            # Cuantificación
            "lbl_used_is": "Used IS",
            "lbl_weighed_sample": "Weighed sample (mg)",
            "lbl_target_mw": "Target molecular weight (g/mol)",
            "lbl_target_integral": "Target integral value",
            "lbl_is_integral": "IS integral value",
            "btn_print": "PRINT",
            "lbl_conc_pp": "Concentration (% w/w)",
            "lbl_conc_pv": "Concentration (% w/v)",
            "lbl_conc_vv": "Concentration (% v/v)",
            # Réplicas
            "lbl_replicates": "Replicates",
            "col_num": "#",
            "col_is_weight": "Weighed IS (mg)",
            "col_sample_weight": "Weighed sample (mg)",
            "col_target_integral": "Analyte integral",
            "col_is_integral": "IS integral",
            "col_result": "Result (% w/w)",
            "lbl_mean": "Mean (% w/w)",
            "lbl_sd": "Std. deviation",
            "lbl_rsd": "RSD (%)",
            "lbl_mean_pv": "Mean (% w/v)",
            "lbl_conc_gl": "Conc. (g/L)",
            "tip_add_rep": "Add replicate",
            "tip_remove_rep": "Remove replicate",
            # Editor de estándares internos
            "menu_standards": "&Internal standards",
            "title_standards": "INTERNAL STANDARDS EDITOR",
            "standards_hint": "Add a standard. A standard with several signals = one row per signal.",
            "col_name": "Name",
            "col_mw": "MW (g/mol)",
            "col_protons": "Protons (signal)",
            "col_purity": "Purity (0–1)",
            "col_shift": "Shift (ppm)",
            "btn_add_standard": "Add",
            "btn_remove_standard": "Remove selected",
            "popup_std_invalid_title": "Invalid standard",
            "popup_std_invalid_text": "Enter a name and valid numbers for MW, protons, purity and shift.",
            "confirm_delete_title": "Delete standard",
            "confirm_delete_text": "Delete the selected internal standard \"{name}\"?",
            # Opcionales (plegable)
            "optional_show": "▸  Optional fields",
            "optional_hide": "▾  Optional fields",
            "lbl_sample_code": "Laboratory sample code",
            "lbl_analyte": "Target analyte name",
            "lbl_sample_density": "Sample density (g/mL)",
            # Tooltip del IS
            "tip_is": "Purity {p}   ·   MW {mw} g/mol   ·   {n} H",
            "tip_is_none": "Select an internal standard",
            # Popups
            "popup_invalid_title": "Invalid data",
            "popup_invalid_text": "\n\nPlease check that all the data is entered and that its format is correct.",
            "popup_instructions_title": "Instructions",
            "popup_about_title": "About {app}",
            "popup_decimals_title": "Decimals",
            "popup_decimals_actual": "Current number: {n}",
            "popup_decimals_ph": "Insert the desired number",
            "popup_decimals_update": "Update",
            "instructions_text": (
                "Welcome to qNMR Assistant.\n\n"
                "This tool has two modes (see the 'Assistant mode' menu):\n\n"
                "1) SAMPLE PREPARATION: given an expected sample concentration, it "
                "estimates how much sample to weigh so the signal of interest has an "
                "intensity similar to that of the weighed internal standard. It is an "
                "orientative guide, not an exact calculation.\n\n"
                "2) QUANTITATION: from the measured integrals, it calculates the real "
                "concentration of the analyte in the sample (% w/w)."
            ),
            "about_text": (
                "qNMR Assistant v{v}<br><br>"
                "Created by Jose Raul Belmonte (2023).<br>"
                "Unified and updated in 2026.<br><br>"
                "Email: joseraulbs@gmail.com<br>"
                "GitHub: <a href=\"https://github.com/JoseRaulBS\">github.com/JoseRaulBS</a>"
            ),
        },
        "es": {
            # Menús
            "menu_menu": "&Menú",
            "menu_decimals": "&Decimales",
            "menu_exit": "&Salir",
            "menu_assistant": "&Modo asistente",
            "menu_sample_prep": "&Preparación de muestra",
            "menu_quantitation": "&Cuantificación",
            "menu_language": "&Idioma",
            "menu_lang_en": "&Inglés",
            "menu_lang_es": "&Español",
            "menu_instructions": "&Instrucciones",
            "menu_about": "&Acerca de",
            "nav_prep": "Preparación",
            "nav_quant": "Cuantificación",
            "nav_standards": "Estándares",
            "msg_check_fields": "Revisa los campos resaltados.",
            "btn_copy": "Copiar",
            "msg_copied": "Resultado copiado al portapapeles.",
            "btn_export_csv": "Exportar CSV",
            "csv_filter": "Archivo CSV (*.csv)",
            # Barra de estado
            "status_desc": "Software {app}. Versión {v}",
            "status_msg": "¡A cuantificar!",
            # Títulos de bloque
            "title_sample_prep": "PREPARACIÓN DE MUESTRA",
            "title_is_data": "DATOS DEL IS",
            "title_quantitation": "CUANTIFICACIÓN",
            "title_results": "RESULTADOS",
            # Campos comunes
            "ph_insert": "Escribe aquí",
            "lbl_purity": "Pureza (%)",
            "lbl_mw": "Peso molecular (g/mol)",
            "lbl_nprotons": "Nº protones",
            "lbl_weighed_is": "IS pesado (mg)",
            "lbl_nprotons_signal": "Nº de protones de la señal de interés",
            "btn_calculate": "CALCULAR",
            # Preparación
            "lbl_expected_conc": "Concentración esperada de la muestra (%)",
            "lbl_final_volume": "Volumen final (mL)",
            "lbl_available_is": "IS disponibles",
            "btn_restart": "Reiniciar datos",
            "lbl_sample_state": "Estado de la muestra",
            "opt_solid": "Sólido",
            "opt_liquid": "Líquido",
            # Protocolo de preparación
            "prep_header": "Protocolo de preparación (buscando intensidades analito / IS similares):",
            "prep_step_weigh_is": "Pesa ~{w} mg de estándar interno.",
            "prep_step_weigh_sample": "Pesa ~{m} mg de muestra.",
            "prep_step_pipette_sample": "Pipetea {v} µL de muestra.",
            "prep_step_dissolve": "Enrasa a {vol} mL con disolvente deuterado.",
            # Ajustes de preparación
            "menu_prep_settings": "&Ajustes de preparación",
            "set_title": "Ajustes de preparación",
            "set_is_min": "Peso mínimo de IS (mg)",
            "set_vmin": "Volumen final mín (mL)",
            "set_vmax": "Volumen final máx (mL)",
            "set_min_weighable": "Muestra mínima pesable (mg)",
            "set_pip_min": "Mínimo de pipeta (µL)",
            "set_pip_max": "Máximo de pipeta (µL)",
            "set_max_conc": "Conc. máx. de muestra (mg/mL)",
            "set_save": "Guardar",
            # Informe / impresión
            "report_title": "Informe de cuantificación qNMR",
            "report_generated": "Generado {date}  ·  qNMR Assistant v{ver}",
            "report_sample_code": "Código de muestra",
            "report_analyte": "Analito",
            "report_analyst": "Analista",
            "report_solvent": "Disolvente deuterado",
            "report_date_field": "Fecha",
            "report_method": "Método",
            "report_is": "Estándar interno",
            "report_purity": "Pureza",
            "report_target_signal": "Señal del analito",
            "report_rep": "#",
            "report_results": "Resultados",
            "report_preparation": "Preparación de la muestra",
            "report_notes": "Notas",
            "report_footer": "Generado con qNMR Assistant — qNMR relativa con estándar interno.",
            "report_signature": "Firma",
            "report_dialog_title": "Datos del informe",
            "lbl_analyst": "Analista",
            "lbl_solvent": "Disolvente deuterado",
            "lbl_date": "Fecha",
            "lbl_notes": "Notas",
            "lbl_prep_details": "Datos de preparación de la muestra",
            "btn_import_prep": "Importar de Preparación de muestra",
            "btn_preview": "Vista previa",
            "btn_save_pdf": "Guardar PDF",
            "popup_no_calc": "Calcula un resultado primero.",
            "pdf_filter": "Documento PDF (*.pdf)",
            # Cuantificación
            "lbl_used_is": "IS utilizado",
            "lbl_weighed_sample": "Muestra pesada (mg)",
            "lbl_target_mw": "Peso molecular del analito (g/mol)",
            "lbl_target_integral": "Valor de la integral del analito",
            "lbl_is_integral": "Valor de la integral del IS",
            "btn_print": "IMPRIMIR",
            "lbl_conc_pp": "Concentración (% p/p)",
            "lbl_conc_pv": "Concentración (% p/v)",
            "lbl_conc_vv": "Concentración (% v/v)",
            # Réplicas
            "lbl_replicates": "Réplicas",
            "col_num": "#",
            "col_is_weight": "IS pesado (mg)",
            "col_sample_weight": "Muestra pesada (mg)",
            "col_target_integral": "Int. analito",
            "col_is_integral": "Int. IS",
            "col_result": "Resultado (% p/p)",
            "lbl_mean": "Media (% p/p)",
            "lbl_sd": "Desv. estándar",
            "lbl_rsd": "RSD (%)",
            "lbl_mean_pv": "Media (% p/v)",
            "lbl_conc_gl": "Conc. (g/L)",
            "tip_add_rep": "Añadir réplica",
            "tip_remove_rep": "Quitar réplica",
            # Editor de estándares internos
            "menu_standards": "&Estándares internos",
            "title_standards": "EDITOR DE ESTÁNDARES INTERNOS",
            "standards_hint": "Añade un estándar. Un estándar con varias señales = una fila por señal.",
            "col_name": "Nombre",
            "col_mw": "PM (g/mol)",
            "col_protons": "Protones (señal)",
            "col_purity": "Pureza (0–1)",
            "col_shift": "Desplazamiento (ppm)",
            "btn_add_standard": "Añadir",
            "btn_remove_standard": "Quitar seleccionado",
            "popup_std_invalid_title": "Estándar no válido",
            "popup_std_invalid_text": "Introduce un nombre y números válidos para PM, protones, pureza y desplazamiento.",
            "confirm_delete_title": "Eliminar estándar",
            "confirm_delete_text": "¿Eliminar el estándar interno seleccionado «{name}»?",
            # Opcionales (plegable)
            "optional_show": "▸  Campos opcionales",
            "optional_hide": "▾  Campos opcionales",
            "lbl_sample_code": "Código de muestra de laboratorio",
            "lbl_analyte": "Nombre del analito",
            "lbl_sample_density": "Densidad de la muestra (g/mL)",
            # Tooltip del IS
            "tip_is": "Pureza {p}   ·   PM {mw} g/mol   ·   {n} H",
            "tip_is_none": "Selecciona un estándar interno",
            # Popups
            "popup_invalid_title": "Datos no válidos",
            "popup_invalid_text": "\n\nComprueba que todos los datos están introducidos y que su formato es correcto.",
            "popup_instructions_title": "Instrucciones",
            "popup_about_title": "Acerca de {app}",
            "popup_decimals_title": "Decimales",
            "popup_decimals_actual": "Número actual: {n}",
            "popup_decimals_ph": "Introduce el número deseado",
            "popup_decimals_update": "Actualizar",
            "instructions_text": (
                "Bienvenido a qNMR Assistant.\n\n"
                "Esta herramienta tiene dos modos (menú 'Modo asistente'):\n\n"
                "1) PREPARACIÓN DE MUESTRA: dada una concentración esperada, estima "
                "cuánta muestra pesar para que la señal de interés tenga una intensidad "
                "similar a la del estándar interno pesado. Es una guía orientativa, no "
                "un cálculo exacto.\n\n"
                "2) CUANTIFICACIÓN: a partir de las integrales medidas, calcula la "
                "concentración real del analito en la muestra (% p/p)."
            ),
            "about_text": (
                "qNMR Assistant v{v}<br><br>"
                "Creado por José Raúl Belmonte (2023).<br>"
                "Unificado y actualizado en 2026.<br><br>"
                "Email: joseraulbs@gmail.com<br>"
                "GitHub: <a href=\"https://github.com/JoseRaulBS\">github.com/JoseRaulBS</a>"
            ),
        },
    }

    @classmethod
    def t(cls, key):
        lang = cls.STRINGS.get(cls.language, cls.STRINGS["en"])
        return lang.get(key, cls.STRINGS["en"].get(key, key))

    @classmethod
    def set_language(cls, lang):
        if lang in cls.STRINGS:
            cls.language = lang
