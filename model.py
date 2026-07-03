import math
import statistics

from prefs import Prefs
from i18n import I18n


def _mg(x):
    return f"{round(x, 2):g}"


def _ul(x):
    return f"{int(round(x))}"


def _ml(x):
    return f"{round(x, 2):g}"


class Model:
    """Lógica de cálculo. Sin estado: dos modos independientes."""

    def __init__(self):
        pass

    # ==================================================================
    # MODO 1 — PREPARACIÓN DE MUESTRA  (asistente práctico)
    # ==================================================================
    # Objetivo: señales de analito e IS de intensidad comparable, con una
    # receta factible en el laboratorio (restricciones en prefs.py).
    #
    # Para integrales comparables:  moles_analito · n_a ≈ moles_IS · n_IS
    #   m_analito_puro(mg) = m_IS · pureza · (MW_a/MW_IS) · (n_IS/n_a)
    #   m_muestra(mg)      = m_analito_puro / c        (c = fracción másica)
    # Se elige el IS (≥ mínimo) intentando que la muestra sea pesable; si no,
    # se prepara disolución madre y se pipetea una alícuota.
    # ------------------------------------------------------------------
    def calculate_preparation(self, state, conc_percent, mw_a, n_a,
                              mw_is, n_is, purity_is, density=None):
        c = conc_percent / 100.0
        if c <= 0 or mw_a <= 0 or mw_is <= 0 or n_a <= 0 or n_is <= 0:
            raise ValueError("invalid preparation inputs")
        if state == "liquid" and (density is None or density <= 0):
            raise ValueError("liquid sample needs density")

        t = I18n.t
        ratio = purity_is * (mw_a / mw_is) * (n_is / n_a)  # mg analito puro por mg IS
        max_conc = Prefs.max_sample_mg_per_ml
        vmin, vmax = Prefs.final_volume_min_ml, Prefs.final_volume_max_ml

        # IS: nunca por debajo de is_min; SIN tope superior. Se elige el mínimo que
        # haga la cantidad de muestra práctica (pesable si sólido; pipeteable si
        # líquido). Así no hacen falta diluciones.
        if state == "liquid":
            target_sample_mg = Prefs.pip_min_ul * density  # vol. mín. pipeteable -> masa
        else:
            target_sample_mg = Prefs.min_weighable_mg
        m_is = max(Prefs.is_min_mg, target_sample_mg * c / ratio)
        m_sample = m_is * ratio / c

        # El volumen final es un grado de libertad en [vmin, vmax]; se ajusta para
        # que la receta sea factible y sencilla, sin mensajes de aviso.
        if state == "liquid":
            v_sample = m_sample / density  # µL  (mg / (g/mL) = µL)
            limit_ul = min(Prefs.pip_max_ul, vmax * 1000.0 * 0.95)
            if v_sample > limit_ul:
                # demasiado diluido: máx. pipeteable que cabe, IS al mínimo
                m_is = Prefs.is_min_mg
                v_sample = limit_ul
                V = vmax
            else:
                V = self._pick_volume(v_sample / 1000.0 / 0.9)
            sample_step = t("prep_step_pipette_sample").format(v=_ul(v_sample))
        else:  # solid
            if m_sample > max_conc * vmax:
                # demasiado diluido: máx. muestra disoluble al volumen máximo, IS mínimo
                m_is = Prefs.is_min_mg
                m_sample = max_conc * vmax
                V = vmax
            else:
                V = self._pick_volume(m_sample / max_conc)
            sample_step = t("prep_step_weigh_sample").format(m=_mg(m_sample))

        return [t("prep_step_weigh_is").format(w=_mg(m_is)),
                sample_step,
                t("prep_step_dissolve").format(vol=_ml(V))]

    @staticmethod
    def _pick_volume(min_needed_ml):
        """Volumen final dentro de [vmin, vmax], redondeado hacia arriba a 0.1 mL."""
        vmin, vmax = Prefs.final_volume_min_ml, Prefs.final_volume_max_ml
        v = max(vmin, min_needed_ml)
        v = math.ceil(v * 10 - 1e-9) / 10.0
        return max(vmin, min(vmax, v))

    # ------------------------------------------------------------------
    # MODO 2 — CUANTIFICACIÓN (qNMR relativa con estándar interno)
    # A partir de las integrales medidas, devuelve la concentración % p/p.
    #
    #   P_x = (I_x/I_IS)·(N_IS/N_x)·(M_x/M_IS)·(m_IS/m_x)·P_IS·100
    # ------------------------------------------------------------------
    def calculate_quantitation(self, input_ISweight, input_sample_weight, input_target_mz,
                               input_protons, purity_value2, mw_ISvalue2, nprotons_value2,
                               input_integral, input_IS_integral):
        """Devuelve la concentración % p/p de UNA réplica (valor numérico)."""
        return (input_ISweight / mw_ISvalue2 * purity_value2 * 100
                * nprotons_value2 / input_IS_integral
                * input_integral / input_protons
                * input_target_mz / input_sample_weight)

    # ------------------------------------------------------------------
    # ESTADÍSTICA DE RÉPLICAS
    # ------------------------------------------------------------------
    def replicate_summary(self, values):
        """Media, desviación estándar (muestral) y RSD (%) de las réplicas.
        sd y rsd son None si hay menos de 2 réplicas."""
        n = len(values)
        mean = statistics.mean(values) if n else 0.0
        if n >= 2:
            sd = statistics.stdev(values)
            rsd = (sd / mean * 100) if mean else 0.0
        else:
            sd = None
            rsd = None
        return {"mean": mean, "sd": sd, "rsd": rsd, "n": n}
