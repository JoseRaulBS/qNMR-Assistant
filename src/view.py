import csv
import os
import sys
from datetime import date

from config import Config
from i18n import I18n
from standards import Standards
from prefs import Prefs
import report
import style

from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QSize, QUrl, QSettings, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont, QColor, QTextDocument, QImage, QShortcut, QKeySequence, \
    QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStatusBar, QLabel, \
    QPushButton, QVBoxLayout, QTextEdit, QComboBox, QLineEdit, QMessageBox, QDialog, \
    QStackedWidget, QFrame, QGraphicsDropShadowEffect, QTableWidget, QTableWidgetItem, \
    QHeaderView, QAbstractItemView, QFileDialog, QButtonGroup, QGraphicsOpacityEffect, \
    QScrollArea
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog


def t(key):
    return I18n.t(key)


def _num(text):
    """Convierte texto a float aceptando coma o punto como separador decimal."""
    return float(str(text).strip().replace(",", "."))


class View(QMainWindow):
    """Ventana única con dos modos (preparación / cuantificación).
    Aspecto moderno (blanco -> azul marino) definido en style.py.
    Interfaz traducible (EN/ES) mediante retranslate()."""

    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        # Anclado a la carpeta de este archivo (no al cwd)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

    font = QFont(Config.font)

    icon_image = resource_path(os.path.join("assets", "images", "calculator.png"))
    logo_image = resource_path(os.path.join("assets", "images", "AppIcon.ico"))
    report_logo = resource_path(os.path.join("assets", "images", "app_logo.png"))
    calculate_image = resource_path(os.path.join("assets", "images", "calculate.png"))
    delete_image = resource_path(os.path.join("assets", "images", "delete.png"))
    print_image = resource_path(os.path.join("assets", "images", "printer.png"))
    not_found_image = resource_path(os.path.join("assets", "images", "not_found.png"))
    icon2_image = resource_path(os.path.join("assets", "images", "icon2.png"))
    about_image = resource_path(os.path.join("assets", "images", "about.png"))

    # ==================================================================
    # CONSTRUCCIÓN DE LA VENTANA
    # ==================================================================
    def __init__(self):
        super().__init__()

        self._tr_labels = []
        self._tr_buttons = []
        self._tr_placeholders = []
        self.last_quant = None          # snapshot del último cálculo (para el informe)
        self.last_prep_protocol = ""    # último protocolo de preparación (texto)
        self._flagged = []              # campos resaltados como inválidos
        self._num_validator = QRegularExpressionValidator(
            QRegularExpression(r"^-?\d*[.,]?\d*$"))  # solo números (coma o punto)

        Standards.load()
        Prefs.load()

        self.stacked_apps = QStackedWidget()
        self.prep_page = self._build_preparation_page()
        self.quant_page = self._build_quantitation_page()
        self.standards_page = self._build_standards_page()
        self.stacked_apps.addWidget(self.prep_page)
        self.stacked_apps.addWidget(self.quant_page)
        self.stacked_apps.addWidget(self.standards_page)
        central = QWidget()
        cv = QVBoxLayout(central)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(0)
        cv.addWidget(self._create_nav())
        cv.addWidget(self.stacked_apps)
        self.setCentralWidget(central)

        self.setWindowIcon(QtGui.QIcon(self.logo_image))
        self.setWindowTitle(Config.WindowTitle)
        self.setMinimumSize(1120, 700)

        self._apply_numeric_validators()
        self._create_status_bar()
        self._create_menu()
        self.retranslate()
        self._restore_geometry()
        self._install_shortcuts()
        self._restore_choices()
        self.show_page(self.quant_page)

    def _apply_numeric_validators(self):
        for w in (self.prep_input_mw, self.prep_input_protons, self.prep_input_conc,
                  self.prep_input_density, self.quant_input_target_mz, self.quant_input_protons,
                  self.quant_input_sample_density, self.std_in_mw, self.std_in_protons,
                  self.std_in_purity, self.std_in_shift):
            w.setValidator(self._num_validator)

    # ------------------------------------------------------------------
    # GEOMETRÍA DE VENTANA Y ATAJOS
    # ------------------------------------------------------------------
    def _restore_geometry(self):
        geo = QSettings().value("geometry")
        if geo is not None:
            self.restoreGeometry(geo)

    def closeEvent(self, event):
        s = QSettings()
        s.setValue("geometry", self.saveGeometry())
        s.setValue("quant_is", self.quant_IS_list.currentIndex())
        s.setValue("prep_is", self.prep_IS_list.currentIndex())
        s.setValue("prep_state", self.prep_state_combo.currentIndex())
        super().closeEvent(event)

    def _restore_choices(self):
        s = QSettings()

        def ival(key, default):
            try:
                return int(s.value(key, default))
            except (TypeError, ValueError):
                return default

        n = len(Standards.items)
        qi = ival("quant_is", -1)
        if 0 <= qi < n:
            self.quant_IS_list.setCurrentIndex(qi)
        pi = ival("prep_is", -1)
        if 0 <= pi < n:
            self.prep_IS_list.setCurrentIndex(pi)
        ps = ival("prep_state", 0)
        if ps in (0, 1):
            self.prep_state_combo.setCurrentIndex(ps)

    def _install_shortcuts(self):
        # Enter / Intro = calcular en la página activa
        for seq in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            sc = QShortcut(QKeySequence(seq), self)
            sc.activated.connect(self._enter_pressed)

    def _enter_pressed(self):
        current = self.stacked_apps.currentWidget()
        if current is self.prep_page:
            self.prep_calculate_btn.click()
        elif current is self.quant_page:
            self.quant_calculate_btn.click()

    def _flash(self, widget, base_style=""):
        """Destello breve para señalar que un valor se ha actualizado."""
        widget.setStyleSheet("background-color: #CDEBFF; border-radius: 8px;")
        QTimer.singleShot(450, lambda: widget.setStyleSheet(base_style))

    # ------------------------------------------------------------------
    # VALIDACIÓN Y RESALTADO DE CAMPOS
    # ------------------------------------------------------------------
    @staticmethod
    def _valid_num(text):
        try:
            return _num(text) > 0
        except (ValueError, AttributeError):
            return False

    def _clear_flags(self):
        for w in self._flagged:
            w.setStyleSheet("")
        self._flagged = []

    def _flag(self, widget):
        widget.setStyleSheet("border: 1.6px solid #E25555; background: #FFF4F4; border-radius: 9px;")
        self._flagged.append(widget)

    def flag_invalid_prep(self):
        self._clear_flags()
        if self.prep_IS_list.currentIndex() < 0:
            self._flag(self.prep_IS_list)
        for w in (self.prep_input_mw, self.prep_input_protons, self.prep_input_conc):
            if not self._valid_num(w.text()):
                self._flag(w)
        if self.prep_state_combo.currentIndex() == 1 and not self._valid_num(self.prep_input_density.text()):
            self._flag(self.prep_input_density)
        self.app_status.showMessage(t("msg_check_fields"), 4000)

    def flag_invalid_quant(self):
        self._clear_flags()
        if self.quant_IS_list.currentIndex() < 0:
            self._flag(self.quant_IS_list)
        for w in (self.quant_input_target_mz, self.quant_input_protons):
            if not self._valid_num(w.text()):
                self._flag(w)
        for r in self.replicate_rows:
            for k in ("is_w", "sample_w", "integral", "is_integral"):
                if not self._valid_num(r[k].text()):
                    self._flag(r[k])
        self.app_status.showMessage(t("msg_check_fields"), 4000)

    # ------------------------------------------------------------------
    # HELPERS DE ESTILO
    # ------------------------------------------------------------------
    def _shadow(self, widget, blur=26, dy=5, alpha=40):
        eff = QGraphicsDropShadowEffect(self)
        eff.setBlurRadius(blur)
        eff.setOffset(0, dy)
        eff.setColor(QColor(11, 37, 69, alpha))
        widget.setGraphicsEffect(eff)

    def _card(self, inner_layout, margins=(20, 18, 20, 18)):
        frame = QFrame()
        frame.setObjectName("card")
        inner_layout.setContentsMargins(*margins)
        frame.setLayout(inner_layout)
        self._shadow(frame)
        return frame

    # ------------------------------------------------------------------
    # HELPERS DE WIDGETS (registran sus textos para la traducción)
    # ------------------------------------------------------------------
    def _title(self, key):
        lab = QLabel(t(key))
        lab.setObjectName("blockTitle")
        lab.setContentsMargins(4, 6, 4, 2)
        self._tr_labels.append((lab, key))
        return lab

    def _field(self, key, fixed=None):
        box = QVBoxLayout()
        box.setSpacing(6)
        box.setContentsMargins(6, 4, 6, 4)
        lab = QLabel(t(key))
        lab.setObjectName("fieldLabel")
        edit = QLineEdit(placeholderText=t("ph_insert"))
        edit.setFont(self.font)
        if fixed:
            edit.setFixedWidth(fixed[0])
        box.addWidget(lab)
        box.addWidget(edit)
        self._tr_labels.append((lab, key))
        self._tr_placeholders.append((edit, "ph_insert"))
        return box, edit

    def _readonly(self, key):
        box = QVBoxLayout()
        box.setSpacing(6)
        box.setContentsMargins(6, 4, 6, 4)
        lab = QLabel(t(key))
        lab.setObjectName("fieldLabel")
        value = QLabel("-")
        value.setObjectName("readonlyValue")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(lab)
        box.addWidget(value)
        self._tr_labels.append((lab, key))
        return box, value

    def _result_value(self, key):
        box = QVBoxLayout()
        box.setSpacing(6)
        box.setContentsMargins(6, 4, 6, 4)
        lab = QLabel(t(key))
        lab.setObjectName("fieldLabel")
        value = QLabel("-")
        value.setObjectName("resultValue")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(lab)
        box.addWidget(value)
        self._tr_labels.append((lab, key))
        return box, value

    def _action_button(self, key, image, object_name="primaryButton",
                       size=(230, 60), icon=28, shadow=True):
        btn = QPushButton(t(key))
        btn.setObjectName(object_name)
        btn.setFont(self.font)
        btn.setIcon(QtGui.QIcon(image))
        btn.setIconSize(QSize(icon, icon))
        btn.setFixedSize(*size)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if shadow:
            self._shadow(btn, blur=18, dy=3, alpha=55)
        self._tr_buttons.append((btn, key))
        return btn

    # ==================================================================
    # PÁGINA 1 — PREPARACIÓN DE MUESTRA
    # ==================================================================
    def _build_preparation_page(self):
        page = QWidget()
        page.setFont(self.font)
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(14)
        page.setLayout(layout)

        layout.addWidget(self._title("title_sample_prep"))

        # Card de datos esenciales
        top = QHBoxLayout()
        top.setSpacing(18)
        is_box = QVBoxLayout()
        is_box.setSpacing(6)
        is_box.setContentsMargins(6, 4, 6, 4)
        self.prep_is_label = QLabel(t("lbl_available_is"))
        self.prep_is_label.setObjectName("fieldLabel")
        self._tr_labels.append((self.prep_is_label, "lbl_available_is"))
        self.prep_IS_list = QComboBox()
        self.prep_IS_list.addItems(Standards.labels())
        self.prep_IS_list.setCurrentIndex(-1)
        self.prep_IS_list.currentIndexChanged.connect(self._update_prep_IS_tooltip)
        is_box.addWidget(self.prep_is_label)
        is_box.addWidget(self.prep_IS_list)
        top.addLayout(is_box)

        box, self.prep_input_mw = self._field("lbl_target_mw")
        top.addLayout(box)
        box, self.prep_input_protons = self._field("lbl_nprotons_signal")
        top.addLayout(box)
        box, self.prep_input_conc = self._field("lbl_expected_conc")
        top.addLayout(box)
        layout.addWidget(self._card(top))

        # Card de estado de la muestra (+ densidad si es líquida)
        state_bar = QHBoxLayout()
        state_bar.setSpacing(18)
        st_box = QVBoxLayout()
        st_box.setSpacing(6)
        st_box.setContentsMargins(6, 4, 6, 4)
        self.prep_state_label = QLabel(t("lbl_sample_state"))
        self.prep_state_label.setObjectName("fieldLabel")
        self._tr_labels.append((self.prep_state_label, "lbl_sample_state"))
        self.prep_state_combo = QComboBox()
        self.prep_state_combo.addItems([t("opt_solid"), t("opt_liquid")])
        self.prep_state_combo.currentIndexChanged.connect(self._toggle_prep_density)
        st_box.addWidget(self.prep_state_label)
        st_box.addWidget(self.prep_state_combo)
        state_bar.addLayout(st_box)

        box, self.prep_input_density = self._field("lbl_sample_density")
        self.prep_density_container = QWidget()
        self.prep_density_container.setLayout(box)
        self.prep_density_container.setVisible(False)
        state_bar.addWidget(self.prep_density_container)
        state_bar.addStretch()
        layout.addWidget(self._card(state_bar))

        # Botones
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(24)
        btn_bar.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.prep_calculate_btn = self._action_button("btn_calculate", self.calculate_image,
                                                       size=(250, 64), icon=34)
        btn_bar.addWidget(self.prep_calculate_btn)
        self.prep_delete_btn = self._action_button("btn_restart", self.delete_image,
                                                   object_name="secondaryButton",
                                                   size=(250, 64), icon=34)
        btn_bar.addWidget(self.prep_delete_btn)
        layout.addLayout(btn_bar)

        # Protocolo (resultados)
        layout.addWidget(self._title("title_results"))
        logger_layout = QVBoxLayout()
        self.prep_logger = QTextEdit()
        self.prep_logger.setObjectName("prepLogger")
        self.prep_logger.setReadOnly(True)
        logger_layout.addWidget(self.prep_logger)
        layout.addWidget(self._card(logger_layout, margins=(14, 12, 14, 12)))

        return page

    def _update_prep_IS_tooltip(self):
        i = self.prep_IS_list.currentIndex()
        if 0 <= i < len(Standards.items):
            IS = Standards.items[i]
            self.prep_IS_list.setToolTip(t("tip_is").format(
                p=IS["purity"], mw=IS["molecular_weight"], n=IS["number_of_protons"]))
        else:
            self.prep_IS_list.setToolTip(t("tip_is_none"))

    def _toggle_prep_density(self):
        self.prep_density_container.setVisible(self.prep_state_combo.currentIndex() == 1)

    # ==================================================================
    # PÁGINA 2 — CUANTIFICACIÓN
    # ==================================================================
    # Anchos de columna (compartidos por la cabecera y las filas de réplica)
    REP_COLS = {"num": 30, "is_w": 120, "sample_w": 130,
                "integral": 120, "is_integral": 120, "result": 120}
    MAX_REPLICATES = 20

    def _build_quantitation_page(self):
        page = QWidget()
        page.setFont(self.font)
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)
        page.setLayout(layout)

        layout.addWidget(self._title("title_quantitation"))

        # ---- Card de datos COMUNES (una vez para todas las réplicas) ----
        common_bar = QHBoxLayout()
        common_bar.setSpacing(18)
        is_box = QVBoxLayout()
        is_box.setSpacing(6)
        is_box.setContentsMargins(6, 4, 6, 4)
        self.quant_is_label = QLabel(t("lbl_used_is"))
        self.quant_is_label.setObjectName("fieldLabel")
        self._tr_labels.append((self.quant_is_label, "lbl_used_is"))
        self.quant_IS_list = QComboBox()
        self.quant_IS_list.addItems(Standards.labels())
        self.quant_IS_list.setCurrentIndex(-1)
        self.quant_IS_list.currentIndexChanged.connect(self._update_quant_IS_tooltip)
        is_box.addWidget(self.quant_is_label)
        is_box.addWidget(self.quant_IS_list)
        common_bar.addLayout(is_box)

        box, self.quant_input_target_mz = self._field("lbl_target_mw")
        common_bar.addLayout(box)
        box, self.quant_input_protons = self._field("lbl_nprotons_signal")
        common_bar.addLayout(box)
        common_bar.addStretch()
        layout.addWidget(self._card(common_bar))

        # ---- Controles de número de réplicas ----
        rep_ctrl = QHBoxLayout()
        rep_ctrl.setContentsMargins(6, 0, 6, 0)
        rep_ctrl.setSpacing(10)
        rep_lbl = QLabel(t("lbl_replicates"))
        rep_lbl.setObjectName("blockTitle")
        self._tr_labels.append((rep_lbl, "lbl_replicates"))
        rep_ctrl.addWidget(rep_lbl)
        rep_ctrl.addSpacing(10)
        self.remove_rep_btn = QPushButton("−")
        self.remove_rep_btn.setObjectName("stepButton")
        self.remove_rep_btn.setFixedSize(40, 40)
        self.remove_rep_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_rep_btn.setToolTip(t("tip_remove_rep"))
        self.remove_rep_btn.clicked.connect(self._remove_replicate)
        rep_ctrl.addWidget(self.remove_rep_btn)
        self.rep_count_label = QLabel("1")
        self.rep_count_label.setObjectName("repCount")
        self.rep_count_label.setFixedWidth(34)
        self.rep_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rep_ctrl.addWidget(self.rep_count_label)
        self.add_rep_btn = QPushButton("+")
        self.add_rep_btn.setObjectName("stepButton")
        self.add_rep_btn.setFixedSize(40, 40)
        self.add_rep_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_rep_btn.setToolTip(t("tip_add_rep"))
        self.add_rep_btn.clicked.connect(self._add_replicate)
        rep_ctrl.addWidget(self.add_rep_btn)
        rep_ctrl.addStretch()
        layout.addLayout(rep_ctrl)

        # ---- Card con cabecera de columnas + filas de réplica ----
        rep_card_layout = QVBoxLayout()
        rep_card_layout.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(12, 0, 12, 0)
        header.setSpacing(10)
        for key, col in (("col_num", "num"), ("col_is_weight", "is_w"),
                         ("col_sample_weight", "sample_w"), ("col_target_integral", "integral"),
                         ("col_is_integral", "is_integral"), ("col_result", "result")):
            hl = QLabel(t(key))
            hl.setObjectName("fieldLabel")
            hl.setFixedWidth(self.REP_COLS[col])
            self._tr_labels.append((hl, key))
            header.addWidget(hl)
        header.addStretch()
        rep_card_layout.addLayout(header)

        # Filas dentro de un área desplazable: si no caben, aparece una barra;
        # si caben todas, no se ve nada.
        self.replicate_rows = []
        self._rep_inner = QWidget()
        self.replicates_layout = QVBoxLayout(self._rep_inner)
        self.replicates_layout.setContentsMargins(0, 0, 0, 0)
        self.replicates_layout.setSpacing(8)
        self.rep_scroll = QScrollArea()
        self.rep_scroll.setWidget(self._rep_inner)
        self.rep_scroll.setWidgetResizable(True)
        self.rep_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.rep_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.rep_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        rep_card_layout.addWidget(self.rep_scroll)
        layout.addWidget(self._card(rep_card_layout, margins=(14, 12, 14, 12)))

        self._add_replicate()  # una réplica por defecto

        # ---- Opcionales plegables ----
        self._optional_expanded = False
        self.optional_toggle = QPushButton(t("optional_show"))
        self.optional_toggle.setObjectName("linkButton")
        self.optional_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.optional_toggle.setFixedHeight(26)
        self.optional_toggle.clicked.connect(self._toggle_optional)
        opt_header = QHBoxLayout()
        opt_header.setContentsMargins(6, 0, 6, 0)
        opt_header.addWidget(self.optional_toggle)
        opt_header.addStretch()
        layout.addLayout(opt_header)

        opt_bar = QHBoxLayout()
        opt_bar.setSpacing(18)
        box, self.quant_input_sample_code = self._field("lbl_sample_code", fixed=(190, 40))
        opt_bar.addLayout(box)
        box, self.quant_input_analyte_name = self._field("lbl_analyte", fixed=(190, 40))
        opt_bar.addLayout(box)
        box, self.quant_input_sample_density = self._field("lbl_sample_density", fixed=(190, 40))
        opt_bar.addLayout(box)
        opt_bar.addStretch()
        self.optional_container = self._card(opt_bar)
        self.optional_container.setVisible(False)
        layout.addWidget(self.optional_container)

        # ---- Botones + resumen estadístico ----
        bottom = QHBoxLayout()
        bottom.setSpacing(18)

        buttons_box = QVBoxLayout()
        buttons_box.setSpacing(12)
        self.quant_calculate_btn = self._action_button("btn_calculate", self.calculate_image)
        buttons_box.addWidget(self.quant_calculate_btn)
        self.quant_print_btn = self._action_button("btn_print", self.print_image,
                                                   object_name="secondaryButton")
        buttons_box.addWidget(self.quant_print_btn)
        bottom.addLayout(buttons_box)
        bottom.addStretch()

        summary_bar = QHBoxLayout()
        summary_bar.setSpacing(26)
        box, self.summary_mean = self._summary_box("lbl_mean")
        summary_bar.addLayout(box)
        box, self.summary_sd = self._summary_box("lbl_sd")
        summary_bar.addLayout(box)
        box, self.summary_rsd = self._summary_box("lbl_rsd")
        summary_bar.addLayout(box)
        # Resultados por densidad (ocultos hasta que se rellene la densidad)
        self.summary_pv_container, self.summary_pv = self._summary_widget("lbl_mean_pv")
        self.summary_pv_container.setVisible(False)
        summary_bar.addWidget(self.summary_pv_container)
        self.summary_gl_container, self.summary_gl = self._summary_widget("lbl_conc_gl")
        self.summary_gl_container.setVisible(False)
        summary_bar.addWidget(self.summary_gl_container)
        bottom.addWidget(self._card(summary_bar))

        layout.addLayout(bottom)

        # Acciones secundarias: copiar / exportar
        actions = QHBoxLayout()
        actions.addStretch()
        self.copy_btn = QPushButton(t("btn_copy"))
        self.copy_btn.setObjectName("secondaryButton")
        self.copy_btn.setFixedSize(150, 38)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_result)
        self._tr_buttons.append((self.copy_btn, "btn_copy"))
        self.export_btn = QPushButton(t("btn_export_csv"))
        self.export_btn.setObjectName("secondaryButton")
        self.export_btn.setFixedSize(160, 38)
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.clicked.connect(self._export_csv)
        self._tr_buttons.append((self.export_btn, "btn_export_csv"))
        actions.addWidget(self.copy_btn)
        actions.addWidget(self.export_btn)
        layout.addLayout(actions)

        layout.addStretch()
        return page

    def _copy_result(self):
        if not self.last_quant:
            return
        d = self.last_quant
        dec = int(Prefs.result_decimals)
        parts = [f"{round(d['mean'], dec)} % p/p"]
        if d.get("pv") is not None:
            parts.append(f"{round(d['pv'], dec)} % p/v")
        if d.get("gl") is not None:
            parts.append(f"{round(d['gl'], dec)} g/L")
        QtGui.QGuiApplication.clipboard().setText("  |  ".join(parts))
        self.app_status.showMessage(t("msg_copied"), 3000)

    def _export_csv(self):
        if not self.last_quant:
            return
        d = self.last_quant
        default = (d.get("sample_code") or "qNMR_results") + ".csv"
        path, _ = QFileDialog.getSaveFileName(self, t("btn_export_csv"), default, t("csv_filter"))
        if not path:
            return
        dec = int(Prefs.result_decimals)
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as fh:
                w = csv.writer(fh, delimiter=";")
                w.writerow([t("report_sample_code"), d.get("sample_code", "")])
                w.writerow([t("report_analyte"), d.get("analyte", "")])
                w.writerow([t("report_is"), d.get("is_label", "")])
                w.writerow([])
                w.writerow([t("col_num"), t("col_is_weight"), t("col_sample_weight"),
                            t("col_target_integral"), t("col_is_integral"), t("lbl_conc_pp")])
                for i, r in enumerate(d.get("replicates", []), 1):
                    w.writerow([i, r["is_w"], r["sample_w"], r["integral"], r["is_integral"],
                                round(r["result"], dec)])
                w.writerow([])
                w.writerow([t("lbl_mean"), round(d["mean"], dec)])
                if d.get("sd") is not None:
                    w.writerow([t("lbl_sd"), round(d["sd"], dec)])
                if d.get("rsd") is not None:
                    w.writerow([t("lbl_rsd"), round(d["rsd"], 2)])
                if d.get("pv") is not None:
                    w.writerow([t("lbl_mean_pv"), round(d["pv"], dec)])
                if d.get("gl") is not None:
                    w.writerow([t("lbl_conc_gl"), round(d["gl"], dec)])
            self.app_status.showMessage(path, 4000)
        except OSError:
            pass

    def _summary_box(self, key):
        box = QVBoxLayout()
        box.setSpacing(4)
        lab = QLabel(t(key))
        lab.setObjectName("fieldLabel")
        value = QLabel("-")
        value.setObjectName("summaryValue")
        box.addWidget(lab)
        box.addWidget(value)
        self._tr_labels.append((lab, key))
        return box, value

    def _summary_widget(self, key):
        """Como _summary_box pero envuelto en un QWidget (para poder ocultarlo)."""
        box, value = self._summary_box(key)
        w = QWidget()
        w.setLayout(box)
        return w, value

    # ------------------------------------------------------------------
    # GESTIÓN DE FILAS DE RÉPLICA
    # ------------------------------------------------------------------
    def _make_replicate_row(self, number):
        frame = QFrame()
        frame.setObjectName("repRow")
        row = QHBoxLayout()
        row.setContentsMargins(10, 6, 10, 6)
        row.setSpacing(10)
        frame.setLayout(row)

        num = QLabel(str(number))
        num.setObjectName("repNum")
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setFixedSize(26, 26)
        row.addWidget(num)
        # hueco para alinear el número (col num) con la cabecera
        row.addSpacing(self.REP_COLS["num"] - 26)

        is_w = QLineEdit()
        is_w.setFixedWidth(self.REP_COLS["is_w"])
        sample_w = QLineEdit()
        sample_w.setFixedWidth(self.REP_COLS["sample_w"])
        integral = QLineEdit()
        integral.setFixedWidth(self.REP_COLS["integral"])
        is_integral = QLineEdit("1")
        is_integral.setFixedWidth(self.REP_COLS["is_integral"])
        for w in (is_w, sample_w, integral, is_integral):
            w.setFont(self.font)
            w.setValidator(self._num_validator)
            row.addWidget(w)

        result = QLabel("-")
        result.setObjectName("repResult")
        result.setFixedWidth(self.REP_COLS["result"])
        result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(result)
        row.addStretch()

        return {"frame": frame, "num": num, "is_w": is_w, "sample_w": sample_w,
                "integral": integral, "is_integral": is_integral, "result": result}

    def _add_replicate(self):
        if len(self.replicate_rows) >= self.MAX_REPLICATES:
            return
        rowdata = self._make_replicate_row(len(self.replicate_rows) + 1)
        self.replicate_rows.append(rowdata)
        self.replicates_layout.addWidget(rowdata["frame"])
        self._update_rep_controls()

    def _remove_replicate(self):
        if len(self.replicate_rows) <= 1:
            return
        rowdata = self.replicate_rows.pop()
        self.replicates_layout.removeWidget(rowdata["frame"])
        rowdata["frame"].deleteLater()
        self._update_rep_controls()

    REP_ROW_H = 58       # alto aprox. de una fila de réplica (px)
    REP_SCROLL_MAX = 320  # alto máximo antes de mostrar barra de desplazamiento

    def _update_rep_controls(self):
        n = len(self.replicate_rows)
        self.rep_count_label.setText(str(n))
        self.remove_rep_btn.setEnabled(n > 1)
        self.add_rep_btn.setEnabled(n < self.MAX_REPLICATES)
        # Altura del área = contenido, hasta un máximo (luego barra desplazable)
        content_h = n * self.REP_ROW_H + max(0, n - 1) * self.replicates_layout.spacing()
        self.rep_scroll.setFixedHeight(min(self.REP_SCROLL_MAX, max(self.REP_ROW_H, content_h + 4)))

    def _current_quant_IS(self):
        i = self.quant_IS_list.currentIndex()
        if 0 <= i < len(Standards.items):
            return Standards.items[i]
        return None

    def _update_quant_IS_tooltip(self):
        IS = self._current_quant_IS()
        if IS:
            tip = t("tip_is").format(p=IS["purity"], mw=IS["molecular_weight"],
                                     n=IS["number_of_protons"])
        else:
            tip = t("tip_is_none")
        self.quant_IS_list.setToolTip(tip)

    def _toggle_optional(self):
        self._optional_expanded = not self._optional_expanded
        self.optional_container.setVisible(self._optional_expanded)
        self.optional_toggle.setText(t("optional_hide") if self._optional_expanded
                                     else t("optional_show"))

    # ==================================================================
    # PÁGINA 3 — EDITOR DE ESTÁNDARES INTERNOS
    # ==================================================================
    STD_COLS = ("col_name", "col_mw", "col_protons", "col_purity", "col_shift")

    def _build_standards_page(self):
        page = QWidget()
        page.setFont(self.font)
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)
        page.setLayout(layout)

        layout.addWidget(self._title("title_standards"))

        self.std_hint = QLabel(t("standards_hint"))
        self.std_hint.setObjectName("fieldLabel")
        self._tr_labels.append((self.std_hint, "standards_hint"))
        layout.addWidget(self.std_hint)

        # Tabla de estándares
        self.std_table = QTableWidget()
        self.std_table.setColumnCount(len(self.STD_COLS))
        self.std_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.std_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.std_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.std_table.verticalHeader().setVisible(False)
        self.std_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.std_table)

        # Botón quitar
        remove_bar = QHBoxLayout()
        remove_bar.addStretch()
        self.remove_standard_btn = self._action_button("btn_remove_standard", self.delete_image,
                                                       object_name="secondaryButton",
                                                       size=(240, 52), icon=26, shadow=False)
        self.remove_standard_btn.clicked.connect(self._remove_standard_clicked)
        remove_bar.addWidget(self.remove_standard_btn)
        layout.addLayout(remove_bar)

        # Formulario de alta (una fila por señal)
        form = QHBoxLayout()
        form.setSpacing(14)
        box, self.std_in_name = self._field("col_name")
        form.addLayout(box)
        box, self.std_in_mw = self._field("col_mw")
        form.addLayout(box)
        box, self.std_in_protons = self._field("col_protons")
        form.addLayout(box)
        box, self.std_in_purity = self._field("col_purity")
        form.addLayout(box)
        box, self.std_in_shift = self._field("col_shift")
        form.addLayout(box)
        self.add_standard_btn = self._action_button("btn_add_standard", self.calculate_image,
                                                    size=(160, 52), icon=26, shadow=False)
        self.add_standard_btn.clicked.connect(self._add_standard_clicked)
        add_wrap = QVBoxLayout()
        add_wrap.addStretch()
        add_wrap.addWidget(self.add_standard_btn)
        form.addLayout(add_wrap)
        layout.addWidget(self._card(form, margins=(16, 14, 16, 14)))

        self._refresh_standards_table()
        return page

    def _refresh_standards_table(self):
        self.std_table.setHorizontalHeaderLabels([t(k) for k in self.STD_COLS])
        self.std_table.setRowCount(len(Standards.items))
        for r, IS in enumerate(Standards.items):
            cells = [IS["name"], f"{IS['molecular_weight']:g}", str(IS["number_of_protons"]),
                     f"{IS['purity']:g}", f"{IS['shift']:g}"]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if c != 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.std_table.setItem(r, c, item)

    def _add_standard_clicked(self):
        name = self.std_in_name.text().strip()
        try:
            if not name:
                raise ValueError("empty name")
            Standards.add(name, self.std_in_mw.text(), self.std_in_protons.text(),
                          self.std_in_purity.text(), self.std_in_shift.text())
        except ValueError:
            box = QMessageBox()
            box.setWindowIcon(QtGui.QIcon(self.icon_image))
            box.setWindowTitle(t("popup_std_invalid_title"))
            box.setText(t("popup_std_invalid_text"))
            box.exec()
            return
        for w in (self.std_in_name, self.std_in_mw, self.std_in_protons,
                  self.std_in_purity, self.std_in_shift):
            w.clear()
        self._refresh_standards_table()
        self._refresh_standard_combos()

    def _remove_standard_clicked(self):
        row = self.std_table.currentRow()
        if not (0 <= row < len(Standards.items)):
            return
        name = Standards.items[row]["name"]
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowIcon(QtGui.QIcon(self.icon_image))
        box.setWindowTitle(t("confirm_delete_title"))
        box.setText(t("confirm_delete_text").format(name=name))
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.setDefaultButton(QMessageBox.StandardButton.No)
        if box.exec() != QMessageBox.StandardButton.Yes:
            return
        Standards.remove(row)
        self._refresh_standards_table()
        self._refresh_standard_combos()

    def _refresh_standard_combos(self):
        for combo, updater in ((self.prep_IS_list, self._update_prep_IS_tooltip),
                               (self.quant_IS_list, self._update_quant_IS_tooltip)):
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(Standards.labels())
            combo.setCurrentIndex(-1)
            combo.blockSignals(False)
            updater()

    def show_standards(self):
        self.show_page(self.standards_page)

    # ==================================================================
    # BARRA DE ESTADO Y MENÚ
    # ==================================================================
    def _create_status_bar(self):
        status = QStatusBar()
        self.status_desc = QLabel()
        status.addPermanentWidget(self.status_desc, 0)
        self.app_status = QStatusBar()
        status.addWidget(self.app_status)
        self.setStatusBar(status)

    def _create_menu(self):
        self.topbar = self.menuBar()

        self.menu = self.topbar.addMenu("")
        self.act_decimals = self.menu.addAction("", self.pop_up_decimals)
        self.act_prep_settings = self.menu.addAction("", self.pop_up_prep_settings)
        self.act_exit = self.menu.addAction("", self.close)

        self.assistant_mode = self.topbar.addMenu("")
        self.act_sample_prep = self.assistant_mode.addAction("", self.show_preparation)
        self.act_quantitation = self.assistant_mode.addAction("", self.show_quantitation)

        self.act_standards = self.topbar.addAction("", self.show_standards)

        self.language_menu = self.topbar.addMenu("")
        self.act_lang_en = self.language_menu.addAction("", lambda: self.set_language("en"))
        self.act_lang_es = self.language_menu.addAction("", lambda: self.set_language("es"))

        self.act_instructions = self.topbar.addAction("", self.pop_up_instructions)
        self.act_about = self.topbar.addAction("", self.pop_up_about)

    # ------------------------------------------------------------------
    # NAVEGACIÓN (pestañas visibles) + transición de fundido
    # ------------------------------------------------------------------
    def _create_nav(self):
        bar = QFrame()
        bar.setObjectName("navBar")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(18, 8, 18, 8)
        lay.setSpacing(8)
        self.nav_prep_btn = self._nav_button("nav_prep", self.prep_page)
        self.nav_quant_btn = self._nav_button("nav_quant", self.quant_page)
        self.nav_std_btn = self._nav_button("nav_standards", self.standards_page)
        self._nav_map = {self.prep_page: self.nav_prep_btn,
                         self.quant_page: self.nav_quant_btn,
                         self.standards_page: self.nav_std_btn}
        group = QButtonGroup(self)
        for btn in self._nav_map.values():
            group.addButton(btn)
            lay.addWidget(btn)
        lay.addStretch()
        return bar

    def _nav_button(self, key, page):
        btn = QPushButton(t(key))
        btn.setObjectName("navButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.show_page(page))
        self._tr_buttons.append((btn, key))
        return btn

    def show_page(self, page):
        self.stacked_apps.setCurrentWidget(page)
        for p, btn in self._nav_map.items():
            btn.setChecked(p is page)
        self._fade(page)

    def _fade(self, page):
        eff = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity")
        anim.setDuration(160)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.finished.connect(lambda: page.setGraphicsEffect(None))
        anim.start()
        self._fade_anim = anim  # mantener referencia

    def show_preparation(self):
        self.show_page(self.prep_page)

    def show_quantitation(self):
        self.show_page(self.quant_page)

    def set_language(self, lang):
        I18n.set_language(lang)
        self.retranslate()

    # ==================================================================
    # TRADUCCIÓN EN CALIENTE
    # ==================================================================
    def retranslate(self):
        for widget, key in self._tr_labels:
            widget.setText(t(key))
        for btn, key in self._tr_buttons:
            btn.setText(t(key))
        for edit, key in self._tr_placeholders:
            edit.setPlaceholderText(t(key))

        self.menu.setTitle(t("menu_menu"))
        self.act_decimals.setText(t("menu_decimals"))
        self.act_prep_settings.setText(t("menu_prep_settings"))
        self.act_exit.setText(t("menu_exit"))
        self.assistant_mode.setTitle(t("menu_assistant"))
        self.act_sample_prep.setText(t("menu_sample_prep"))
        self.act_quantitation.setText(t("menu_quantitation"))
        self.act_standards.setText(t("menu_standards"))
        self.language_menu.setTitle(t("menu_language"))
        self.act_lang_en.setText(t("menu_lang_en"))
        self.act_lang_es.setText(t("menu_lang_es"))
        self.act_instructions.setText(t("menu_instructions"))
        self.act_about.setText(t("menu_about"))

        self.status_desc.setText(t("status_desc").format(app=Config.app_name, v=Config.version))
        self.app_status.showMessage(t("status_msg"))

        self.optional_toggle.setText(t("optional_hide") if self._optional_expanded
                                     else t("optional_show"))
        self._update_quant_IS_tooltip()
        self._update_prep_IS_tooltip()
        self.prep_state_combo.setItemText(0, t("opt_solid"))
        self.prep_state_combo.setItemText(1, t("opt_liquid"))
        self.std_table.setHorizontalHeaderLabels([t(k) for k in self.STD_COLS])

    # ==================================================================
    # VENTANAS EMERGENTES
    # ==================================================================
    def not_found_element_pop_up(self):
        box = QMessageBox()
        img = QtGui.QPixmap(self.not_found_image)
        box.setIconPixmap(img.scaled(200, 200))
        box.setWindowIcon(QtGui.QIcon(self.icon_image))
        box.setWindowTitle(t("popup_invalid_title"))
        box.setText(t("popup_invalid_text"))
        box.exec()

    # ==================================================================
    # INFORME DE CUANTIFICACIÓN
    # ==================================================================
    def open_report_dialog(self):
        if not self.last_quant:
            box = QMessageBox()
            box.setWindowIcon(QtGui.QIcon(self.icon_image))
            box.setWindowTitle(t("report_dialog_title"))
            box.setText(t("popup_no_calc"))
            box.exec()
            return

        self._report_dlg = QDialog(self)
        self._report_dlg.setWindowTitle(t("report_dialog_title"))
        self._report_dlg.setWindowIcon(QtGui.QIcon(self.logo_image))
        self._report_dlg.setMinimumWidth(560)
        lay = QVBoxLayout()
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(8)
        self._report_dlg.setLayout(lay)

        def field(key, value=""):
            lab = QLabel(t(key))
            lab.setObjectName("fieldLabel")
            edit = QLineEdit(value)
            lay.addWidget(lab)
            lay.addWidget(edit)
            return edit

        self._rep_sample = field("report_sample_code", self.last_quant.get("sample_code", ""))
        self._rep_analyte = field("report_analyte", self.last_quant.get("analyte", ""))
        self._rep_analyst = field("report_analyst", str(QSettings().value("last_analyst", "")))
        self._rep_solvent = field("report_solvent", str(QSettings().value("last_solvent", "")))
        self._rep_date = field("report_date_field", date.today().isoformat())

        lab = QLabel(t("lbl_prep_details"))
        lab.setObjectName("fieldLabel")
        lay.addWidget(lab)
        self._rep_prep = QTextEdit()
        self._rep_prep.setFixedHeight(80)
        lay.addWidget(self._rep_prep)
        imp = QPushButton(t("btn_import_prep"))
        imp.setObjectName("secondaryButton")
        imp.setFixedHeight(34)
        imp.setCursor(Qt.CursorShape.PointingHandCursor)
        imp.clicked.connect(lambda: self._rep_prep.setPlainText(self.last_prep_protocol))
        lay.addWidget(imp)

        lab = QLabel(t("lbl_notes"))
        lab.setObjectName("fieldLabel")
        lay.addWidget(lab)
        self._rep_notes = QTextEdit()
        self._rep_notes.setFixedHeight(56)
        lay.addWidget(self._rep_notes)

        btns = QHBoxLayout()
        prev = QPushButton(t("btn_preview"))
        prev.setObjectName("secondaryButton")
        prev.setFixedHeight(42)
        prev.setCursor(Qt.CursorShape.PointingHandCursor)
        prev.clicked.connect(self._preview_report)
        save = QPushButton(t("btn_save_pdf"))
        save.setObjectName("primaryButton")
        save.setFixedHeight(42)
        save.setCursor(Qt.CursorShape.PointingHandCursor)
        save.clicked.connect(self._save_report_pdf)
        btns.addWidget(prev)
        btns.addWidget(save)
        lay.addLayout(btns)

        self._report_dlg.exec()

    def _report_data(self):
        d = dict(self.last_quant)
        d["version"] = Config.version
        d["date"] = date.today().isoformat()
        d["sample_code"] = self._rep_sample.text().strip()
        d["analyte"] = self._rep_analyte.text().strip()
        d["analyst"] = self._rep_analyst.text().strip()
        d["solvent"] = self._rep_solvent.text().strip()
        s = QSettings()
        s.setValue("last_analyst", d["analyst"])
        s.setValue("last_solvent", d["solvent"])
        d["report_date"] = self._rep_date.text().strip()
        d["prep_details"] = self._rep_prep.toPlainText().strip()
        d["notes"] = self._rep_notes.toPlainText().strip()
        return d

    def _build_report_document(self, d):
        doc = QTextDocument()
        img = QImage(self.report_logo)
        doc.addResource(QTextDocument.ResourceType.ImageResource, QUrl("logo"), img)
        doc.setHtml(report.build_report_html(d, I18n.t, "logo"))
        return doc

    @staticmethod
    def _print_doc(doc, printer):
        try:
            doc.print_(printer)
        except AttributeError:
            doc.print(printer)

    def _preview_report(self):
        doc = self._build_report_document(self._report_data())
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintPreviewDialog(printer, self)
        dialog.paintRequested.connect(lambda p: self._print_doc(doc, p))
        dialog.exec()

    def _save_report_pdf(self):
        d = self._report_data()
        default = (d.get("sample_code") or "qNMR_report") + ".pdf"
        path, _ = QFileDialog.getSaveFileName(self, t("btn_save_pdf"), default, t("pdf_filter"))
        if not path:
            return
        doc = self._build_report_document(d)
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        self._print_doc(doc, printer)
        self._report_dlg.close()

    def pop_up_instructions(self):
        box = QMessageBox()
        img = QtGui.QPixmap(self.report_logo)
        box.setIconPixmap(img.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation))
        box.setWindowIcon(QtGui.QIcon(self.logo_image))
        box.setWindowTitle(t("popup_instructions_title"))
        box.setText(t("instructions_text"))
        box.exec()

    def pop_up_about(self):
        box = QMessageBox()
        img = QtGui.QPixmap(self.about_image)
        box.setIconPixmap(img.scaled(200, 200))
        box.setWindowIcon(QtGui.QIcon(self.icon_image))
        box.setWindowTitle(t("popup_about_title").format(app=Config.app_name))
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setText(t("about_text").format(v=Config.version))
        box.exec()

    def pop_up_decimals(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle(t("popup_decimals_title"))
        self.dialog.setWindowIcon(QtGui.QIcon(self.icon_image))
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        self.dialog.setLayout(layout)
        self.decimal_label = QLabel(t("popup_decimals_actual").format(n=int(Prefs.result_decimals)))
        layout.addWidget(self.decimal_label)
        self.decimals_line_edit = QLineEdit(placeholderText=t("popup_decimals_ph"))
        layout.addWidget(self.decimals_line_edit)
        self.decimals_button = QPushButton(t("popup_decimals_update"))
        self.decimals_button.setObjectName("primaryButton")
        self.decimals_button.setFixedHeight(40)
        self.decimals_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.decimals_button)
        self.decimals_button.clicked.connect(self.update_decimals)
        self.dialog.exec()

    def pop_up_prep_settings(self):
        self.prep_dialog = QDialog()
        self.prep_dialog.setWindowTitle(t("set_title"))
        self.prep_dialog.setWindowIcon(QtGui.QIcon(self.icon_image))
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        self.prep_dialog.setLayout(layout)

        # (clave de Prefs, clave i18n) por campo
        self._prep_setting_fields = []
        rows = [("is_min_mg", "set_is_min"),
                ("final_volume_min_ml", "set_vmin"), ("final_volume_max_ml", "set_vmax"),
                ("min_weighable_mg", "set_min_weighable"), ("pip_min_ul", "set_pip_min"),
                ("pip_max_ul", "set_pip_max"), ("max_sample_mg_per_ml", "set_max_conc")]
        for attr, key in rows:
            lab = QLabel(t(key))
            lab.setObjectName("fieldLabel")
            edit = QLineEdit(str(getattr(Prefs, attr)))
            edit.setFixedWidth(120)
            layout.addWidget(lab)
            layout.addWidget(edit)
            self._prep_setting_fields.append((attr, edit))

        save_btn = QPushButton(t("set_save"))
        save_btn.setObjectName("primaryButton")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_prep_settings)
        layout.addWidget(save_btn)
        self.prep_dialog.exec()

    def _save_prep_settings(self):
        try:
            for attr, edit in self._prep_setting_fields:
                setattr(Prefs, attr, float(edit.text()))
            Prefs.save()
        except ValueError:
            pass
        self.prep_dialog.close()

    def update_decimals(self):
        try:
            Prefs.result_decimals = max(0, int(self.decimals_line_edit.text()))
            Prefs.save()
        except ValueError:
            pass
        self.dialog.close()

    # ==================================================================
    # ACCIONES / GETTERS  (usados por el Controller)
    # ==================================================================
    def get_preparation_inputs(self):
        """(state, conc%, MW_a, n_a, MW_IS, n_IS, purity_IS, density|None)."""
        i = self.prep_IS_list.currentIndex()
        if not (0 <= i < len(Standards.items)):
            raise ValueError("No internal standard selected")
        IS = Standards.items[i]
        state = "liquid" if self.prep_state_combo.currentIndex() == 1 else "solid"
        conc = _num(self.prep_input_conc.text())
        mw_a = _num(self.prep_input_mw.text())
        n_a = _num(self.prep_input_protons.text())
        density = None
        if state == "liquid":
            dtext = self.prep_input_density.text().strip()
            density = _num(dtext) if dtext else None
        return (state, conc, mw_a, n_a, float(IS["molecular_weight"]),
                float(IS["number_of_protons"]), float(IS["purity"]), density)

    def show_preparation_protocol(self, steps):
        self._clear_flags()
        self.prep_logger.clear()
        self.prep_logger.append(t("prep_header"))
        self.prep_logger.append("")
        lines = [f"{n}.  {step}" for n, step in enumerate(steps, 1)]
        for line in lines:
            self.prep_logger.append(line)
        self.last_prep_protocol = "\n".join(lines)

    def get_quantitation_common(self):
        """Datos comunes a todas las réplicas:
        (target_mz, protons, purity, mw_IS, nprotons_IS)."""
        IS = self._current_quant_IS()
        if IS is None:
            raise ValueError("No internal standard selected")
        return (_num(self.quant_input_target_mz.text()), _num(self.quant_input_protons.text()),
                float(IS["purity"]), float(IS["molecular_weight"]), float(IS["number_of_protons"]))

    def get_replicates_input(self):
        """Lista de tuplas (IS_weight, sample_weight, integral, IS_integral) por réplica."""
        data = []
        for r in self.replicate_rows:
            data.append((_num(r["is_w"].text()), _num(r["sample_w"].text()),
                         _num(r["integral"].text()), _num(r["is_integral"].text())))
        return data

    def show_quantitation_results(self, values, summary):
        """Rellena el resultado de cada réplica y el resumen (media/SD/RSD).
        Si se ha introducido densidad de muestra, añade % p/v y g/L."""
        self._clear_flags()
        dec = int(Prefs.result_decimals)
        for row, value in zip(self.replicate_rows, values):
            row["result"].setText(f"{round(value, dec)} %")
        mean = summary["mean"]
        self.summary_mean.setText(f"{round(mean, dec)} %")
        self.summary_sd.setText("-" if summary["sd"] is None else f"{round(summary['sd'], dec)}")
        self.summary_rsd.setText("-" if summary["rsd"] is None else f"{round(summary['rsd'], 2)} %")
        self._flash(self.summary_mean)

        # Unidades por densidad (solo si se ha rellenado una densidad válida)
        show_density = False
        d = None
        dtext = self.quant_input_sample_density.text().strip()
        if dtext:
            try:
                d = _num(dtext)
            except ValueError:
                d = None
            if d is not None and d > 0:
                self.summary_pv.setText(f"{round(mean * d, dec)} %")          # % p/v = % p/p · d
                self.summary_gl.setText(f"{round(mean * d * 10, dec)} g/L")    # g/L = % p/p · d · 10
                show_density = True
            else:
                d = None
        self.summary_pv_container.setVisible(show_density)
        self.summary_gl_container.setVisible(show_density)

        # Snapshot para el informe
        IS = self._current_quant_IS() or {}
        reps = []
        for row, value in zip(self.replicate_rows, values):
            reps.append({"is_w": row["is_w"].text(), "sample_w": row["sample_w"].text(),
                         "integral": row["integral"].text(),
                         "is_integral": row["is_integral"].text(), "result": value})
        self.last_quant = {
            "is_label": self.quant_IS_list.currentText(),
            "is_purity": IS.get("purity"), "is_mw": IS.get("molecular_weight"),
            "is_n": IS.get("number_of_protons"), "is_shift": IS.get("shift"),
            "target_mw": self.quant_input_target_mz.text(),
            "target_n": self.quant_input_protons.text(),
            "replicates": reps, "mean": summary["mean"], "sd": summary["sd"], "rsd": summary["rsd"],
            "density": d,
            "pv": (mean * d) if (show_density and d) else None,
            "gl": (mean * d * 10) if (show_density and d) else None,
            "sample_code": self.quant_input_sample_code.text().strip(),
            "analyte": self.quant_input_analyte_name.text().strip(),
        }

    def print_preparation_result(self, text):
        self.prep_logger.append(text)

    def clear_preparation_logger(self):
        self.prep_logger.clear()
