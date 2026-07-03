class Controller:

    def __init__(self, view, model):
        self._view = view
        self._model = model
        self._connect_signals()

    # ---- PREPARACIÓN DE MUESTRA ----
    def preparation_actions(self):
        try:
            state, conc, mw_a, n_a, mw_is, n_is, purity_is, density = \
                self._view.get_preparation_inputs()
            steps = self._model.calculate_preparation(
                state, conc, mw_a, n_a, mw_is, n_is, purity_is, density)
            self._view.show_preparation_protocol(steps)
        except (ValueError, ZeroDivisionError):
            self._view.flag_invalid_prep()

    # ---- CUANTIFICACIÓN (con réplicas) ----
    def quantitation_actions(self):
        try:
            target_mz, protons, purity, mw_IS, nprotons_IS = \
                self._view.get_quantitation_common()
            replicates = self._view.get_replicates_input()  # lista de tuplas (IS_w, sample_w, integral, IS_integral)

            values = [
                self._model.calculate_quantitation(
                    is_w, sample_w, target_mz, protons,
                    purity, mw_IS, nprotons_IS, integral, is_integral)
                for (is_w, sample_w, integral, is_integral) in replicates
            ]
            summary = self._model.replicate_summary(values)
            self._view.show_quantitation_results(values, summary)
        except (ValueError, ZeroDivisionError):
            self._view.flag_invalid_quant()

    def _connect_signals(self):
        # Preparación
        self._view.prep_calculate_btn.clicked.connect(self.preparation_actions)
        self._view.prep_delete_btn.clicked.connect(self._view.clear_preparation_logger)
        # Cuantificación
        self._view.quant_calculate_btn.clicked.connect(self.quantitation_actions)
        self._view.quant_print_btn.clicked.connect(self._view.open_report_dialog)
