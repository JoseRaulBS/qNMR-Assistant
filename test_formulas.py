# -*- coding: utf-8 -*-
"""Validación científica de las fórmulas de qNMR (QuantTool2026_modern).

Ejercita el código REAL de `model.py` (no una copia) y comprueba que:

  T1  Cuantificación == ecuación qNMR de literatura (identidad algebraica).
  T2  Round-trip sintético: mezcla de % conocido -> integrales teóricas -> modelo
      recupera exactamente el % de partida.
  T3  Caso de regresión documentado (todo=1, IS = TMB 3.7 ppm -> 5.35 %).
  T4  Consistencia con el modelo de referencia PyQNMR_Parallel (2023).
  T5  Preparación sólido (rama normal): señales analito/IS ~1:1 + restricciones.
  T6  Preparación líquido (rama normal): ídem con alícuota pipeteable.
  T7  Preparación ramas "demasiado diluido" (sólido y líquido): mejor receta factible.
  T8  Conversión densidad: % p/v = % p/p·d ; g/L = % p/p·d·10.
  T9  Estadística de réplicas (SD muestral, RSD).
  T10 Documentación cuantificada del sesgo de la fórmula de preparación de 2023.

Fundamento científico (qNMR relativa con estándar interno):
    P_x (% p/p) = (I_x/I_IS)·(N_IS/N_x)·(M_x/M_IS)·(m_IS/m_x)·P_IS·100

Uso:
    & C:/Users/Usuario/qnmr_venv/Scripts/python.exe QuantTool2026_modern/test_formulas.py
(se ejecuta desde la raíz del proyecto o desde dentro de la carpeta; añade su
propio directorio a sys.path para importar model/prefs sin tocar el entorno).
"""
import io
import os
import statistics
import sys

# Ejecutable con o sin consola Unicode
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except (AttributeError, io.UnsupportedOperation):
    pass

# Importar model/prefs de esta misma carpeta, se lance desde donde se lance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import model as model_mod
from model import Model
from prefs import Prefs


# --- I18n falso: plantillas controladas para poder extraer los números de vuelta ---
class FakeI18n:
    _T = {
        "prep_step_weigh_is": "IS_MG={w}",
        "prep_step_pipette_sample": "SAMPLE_UL={v}",
        "prep_step_weigh_sample": "SAMPLE_MG={m}",
        "prep_step_dissolve": "VOL_ML={vol}",
    }

    @staticmethod
    def t(key):
        return FakeI18n._T[key]


model_mod.I18n = FakeI18n
m = Model()

FAILS = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"   [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(name)


def lit_qnmr(Ix, Iis, Nx, Nis, Mx, Mis, mx, mis, Pis):
    """Ecuación qNMR relativa estándar (Bharti & Roy 2012; Pauli et al.)."""
    return (Ix / Iis) * (Nis / Nx) * (Mx / Mis) * (mis / mx) * Pis * 100.0


def parse_steps(steps):
    out = {}
    for s in steps:
        k, v = s.split("=")
        out[k] = float(v)
    return out


print("=" * 72)
print("T1 - Cuantificación vs ecuación de literatura (5 juegos de valores)")
cases = [
    # (Ix, Iis, Nx, Nis, Mx, Mis, mx_mg, mis_mg, Pis)
    (1.234, 0.987, 2, 9, 301.2, 172.28, 48.3, 5.1, 0.988),
    (0.512, 1.000, 3, 6, 116.07, 94.13, 102.7, 10.2, 0.9996),
    (2.750, 1.500, 1, 12, 450.5, 88.22, 33.3, 2.05, 0.9999),
    (0.033, 1.000, 6, 3, 194.19, 168.19, 250.0, 20.0, 0.9996),
    (5.600, 2.300, 4, 9, 180.16, 172.28, 12.5, 3.3, 0.988),
]
for i, (Ix, Iis, Nx, Nis, Mx, Mis, mx, mis, Pis) in enumerate(cases, 1):
    got = m.calculate_quantitation(mis, mx, Mx, Nx, Pis, Mis, Nis, Ix, Iis)
    want = lit_qnmr(Ix, Iis, Nx, Nis, Mx, Mis, mx, mis, Pis)
    check(f"T1.{i} identidad ({want:.6g} %)", abs(got - want) <= 1e-12 * abs(want))

print("=" * 72)
print("T2 - Round-trip sintético (mezcla 10.000 % p/p de ácido maleico)")
w, mx, Mx, Nx = 0.10, 50.0, 116.07, 2
mis, Mis, Nis, Pis = 5.0, 94.13, 6, 0.9996
protons_a = (w * mx / Mx) * Nx           # nº de protones del analito (u.a.)
protons_is = (Pis * mis / Mis) * Nis     # nº de protones del IS (u.a.)
Iis = 1.0
Ix = protons_a / protons_is              # integral relativa teórica
got = m.calculate_quantitation(mis, mx, Mx, Nx, Pis, Mis, Nis, Ix, Iis)
check(f"T2 recupera 10.0000 % (obtuvo {got:.6f} %)", abs(got - 10.0) < 1e-9)

print("=" * 72)
print("T3 - Caso de regresión: todo=1, IS = TMB 3.7 ppm -> 5.35 %")
got = m.calculate_quantitation(1, 1, 1, 1, 0.9996, 168.19, 9, 1, 1)
check(f"T3 = {round(got, 2)} %", round(got, 2) == 5.35)

print("=" * 72)
print("T4 - Consistencia con PyQNMR_Parallel/model.py (referencia 2023)")


def parallel_2023(input_ISweight, input_sample_weight, input_target_mz, input_protons,
                  purity_value2, mw_ISvalue2, nprotons_value2,
                  input_integral, input_IS_integral):
    return (input_ISweight / mw_ISvalue2 * purity_value2 * 100
            * nprotons_value2 / input_IS_integral
            * input_integral / input_protons
            * input_target_mz / input_sample_weight)


for i, (Ix, Iis, Nx, Nis, Mx, Mis, mx, mis, Pis) in enumerate(cases, 1):
    new = m.calculate_quantitation(mis, mx, Mx, Nx, Pis, Mis, Nis, Ix, Iis)
    old = parallel_2023(mis, mx, Mx, Nx, Pis, Mis, Nis, Ix, Iis)
    check(f"T4.{i} nuevo == Parallel", new == old)

print("=" * 72)
print("T5 - Preparación SÓLIDO, rama normal (c=50 %, MW 300, 2H, IS TMSP)")
Mx, Nx, c = 300.0, 2, 50.0
Mis, Nis, Pis = 172.28, 9, 0.988
steps = parse_steps(m.calculate_preparation("solid", c, Mx, Nx, Mis, Nis, Pis))
mis_r, ms_r, V = steps["IS_MG"], steps["SAMPLE_MG"], steps["VOL_ML"]
print(f"    receta: IS={mis_r} mg, muestra={ms_r} mg, V={V} mL")
pa = (ms_r * c / 100 / Mx) * Nx      # protones del analito (u.a.)
pis = (Pis * mis_r / Mis) * Nis      # protones del IS (u.a.)
check(f"T5 señales ~1:1 (I_a/I_IS={pa / pis:.4f})", abs(pa / pis - 1) < 0.01)
check("T5 IS >= mínimo", mis_r >= Prefs.is_min_mg - 1e-9)
check("T5 muestra pesable", ms_r >= Prefs.min_weighable_mg - 1e-9)
check("T5 volumen en rango",
      Prefs.final_volume_min_ml - 1e-9 <= V <= Prefs.final_volume_max_ml + 1e-9)
check("T5 disoluble", ms_r <= Prefs.max_sample_mg_per_ml * V + 1e-6)

print("=" * 72)
print("T6 - Preparación LÍQUIDO, rama normal (c=10 %, d=0.9, MW 200, 3H, IS DMS)")
Mx, Nx, c, d = 200.0, 3, 10.0, 0.9
Mis, Nis, Pis = 94.13, 6, 0.9996
steps = parse_steps(m.calculate_preparation("liquid", c, Mx, Nx, Mis, Nis, Pis, density=d))
mis_r, vs_ul, V = steps["IS_MG"], steps["SAMPLE_UL"], steps["VOL_ML"]
ms_r = vs_ul * d
print(f"    receta: IS={mis_r} mg, alícuota={vs_ul} µL ({ms_r:.1f} mg), V={V} mL")
pa = (ms_r * c / 100 / Mx) * Nx
pis = (Pis * mis_r / Mis) * Nis
check(f"T6 señales ~1:1 (I_a/I_IS={pa / pis:.4f})", abs(pa / pis - 1) < 0.01)
check("T6 alícuota pipeteable", Prefs.pip_min_ul - 0.5 <= vs_ul <= Prefs.pip_max_ul + 0.5)
check("T6 alícuota cabe en V", vs_ul <= V * 1000 * 0.95 + 0.5)
check("T6 volumen en rango",
      Prefs.final_volume_min_ml - 1e-9 <= V <= Prefs.final_volume_max_ml + 1e-9)

print("=" * 72)
print("T7 - Ramas 'demasiado diluido' (mejor receta factible)")
steps = parse_steps(m.calculate_preparation("solid", 0.05, 500.0, 1, 172.28, 9, 0.988))
mis_r, ms_r, V = steps["IS_MG"], steps["SAMPLE_MG"], steps["VOL_ML"]
print(f"    sólido diluido: IS={mis_r} mg, muestra={ms_r} mg, V={V} mL")
check("T7a IS al mínimo", abs(mis_r - Prefs.is_min_mg) < 1e-9)
check("T7a muestra = máx. disoluble",
      abs(ms_r - Prefs.max_sample_mg_per_ml * Prefs.final_volume_max_ml) < 0.01)
check("T7a V = vmax", abs(V - Prefs.final_volume_max_ml) < 1e-9)
steps = parse_steps(m.calculate_preparation("liquid", 0.2, 400.0, 1, 172.28, 9, 0.988, density=1.0))
mis_r, vs_ul, V = steps["IS_MG"], steps["SAMPLE_UL"], steps["VOL_ML"]
print(f"    líquido diluido: IS={mis_r} mg, alícuota={vs_ul} µL, V={V} mL")
limit = min(Prefs.pip_max_ul, Prefs.final_volume_max_ml * 1000 * 0.95)
check("T7b IS al mínimo", abs(mis_r - Prefs.is_min_mg) < 1e-9)
check("T7b alícuota = límite pipeteable", abs(vs_ul - limit) < 0.51)
check("T7b V = vmax", abs(V - Prefs.final_volume_max_ml) < 1e-9)

print("=" * 72)
print("T8 - Conversión por densidad (aritmética de show_quantitation_results)")
mean_pp, dens = 5.0, 1.2
pv = mean_pp * dens          # % p/v  (g/100 mL)
gl = mean_pp * dens * 10     # g/L
check(f"T8 % p/v = {pv} (esperado 6.0)", abs(pv - 6.0) < 1e-12)
check(f"T8 g/L = {gl} (esperado 60.0)", abs(gl - 60.0) < 1e-12)

print("=" * 72)
print("T9 - Estadística de réplicas")
vals = [5.1, 5.3, 5.2]
s = m.replicate_summary(vals)
check(f"T9 media = {s['mean']:.4f}", abs(s["mean"] - 5.2) < 1e-12)
check(f"T9 SD muestral = {s['sd']:.4f}", abs(s["sd"] - statistics.stdev(vals)) < 1e-15)
check(f"T9 RSD = {s['rsd']:.4f} %", abs(s["rsd"] - statistics.stdev(vals) / 5.2 * 100) < 1e-12)
s1 = m.replicate_summary([5.1])
check("T9 n=1 -> SD/RSD None", s1["sd"] is None and s1["rsd"] is None)

print("=" * 72)
print("T10 - Sesgo de la fórmula de PREPARACIÓN de 2023 (documentación)")


def prep_2023(sample_conc, n_protons, targetmz, weighed_IS,
              purity_value, mw_ISvalue, nprotons_value,
              avogadro_number=6.022E+26, proton_weight=1.00794):
    IS_quantity_grams = (100 * purity_value) * weighed_IS / 100000
    IS_mols = IS_quantity_grams / mw_ISvalue
    molecue_number = IS_mols * avogadro_number
    target_protons = ((proton_weight * nprotons_value) / mw_ISvalue) * molecue_number
    neccessary_sample_molecues = (target_protons / n_protons) * targetmz
    sample_mol = neccessary_sample_molecues / avogadro_number
    sample_quantity = sample_mol * targetmz
    return sample_quantity / (sample_conc / 100) * 1000  # mg


def prep_correcta(sample_conc, n_protons, targetmz, weighed_IS,
                  purity_value, mw_ISvalue, nprotons_value):
    ratio = purity_value * (targetmz / mw_ISvalue) * (nprotons_value / n_protons)
    return weighed_IS * ratio / (sample_conc / 100)


for Mx, Mis, name in ((300.0, 172.28, "MW300/TMSP"), (90.0, 172.28, "MW90/TMSP"),
                      (172.28, 172.28, "MW=MW_IS"), (168.19, 94.13, "MW168/DMS")):
    old = prep_2023(10.0, 2, Mx, 5.0, 0.988, Mis, 9)
    good = prep_correcta(10.0, 2, Mx, 5.0, 0.988, Mis, 9)
    factor_teorico = 1.00794 * Mx / Mis
    print(f"    {name:12s}: 2023={old:9.2f} mg  correcta={good:8.2f} mg  "
          f"desvío x{old / good:.3f} (teórico x{factor_teorico:.3f})")
    check(f"T10 {name} desvío == 1.00794·MW_a/MW_IS", abs(old / good - factor_teorico) < 1e-9)

print("=" * 72)
print(f"RESULTADO: {'TODOS LOS TESTS PASAN' if not FAILS else 'FALLOS: ' + ', '.join(FAILS)}")
sys.exit(1 if FAILS else 0)
