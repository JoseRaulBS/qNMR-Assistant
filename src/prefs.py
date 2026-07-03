"""Preferencias de preparación de muestra (configurables y persistentes).

Se guardan en `prep_settings.json` (junto a este módulo). Permiten ajustar las
restricciones prácticas del laboratorio (mínimo de IS pesable, volumen final,
rango de la micropipeta, etc.) sin tocar el código.
"""
import json

from paths import data_file

_FILENAME = "prep_settings.json"

_FIELDS = ("is_min_mg", "final_volume_min_ml", "final_volume_max_ml",
           "min_weighable_mg", "pip_min_ul", "pip_max_ul", "max_sample_mg_per_ml",
           "result_decimals")


class Prefs:
    # Valores por defecto (laboratorio actual)
    result_decimals = 2         # nº de decimales en los resultados (persistente)
    is_min_mg = 2.0              # mínimo de estándar interno a pesar (nunca menos de 2-3 mg)
    final_volume_min_ml = 0.6    # volumen final mínimo (tubo de RMN)
    final_volume_max_ml = 1.0    # volumen final máximo (margen para ajustar la receta)
    min_weighable_mg = 1.0       # mínima masa de muestra que pesamos con fiabilidad
    pip_min_ul = 10.0            # micropipeta: mínimo fiable
    pip_max_ul = 1000.0          # micropipeta: máximo
    max_sample_mg_per_ml = 250.0  # máx. masa de muestra disoluble por mL (solubilidad)
    # Nota: el IS no tiene tope superior; crece lo necesario para que las
    # cantidades de muestra sean prácticas (se ha llegado a 20-30 mg).

    @classmethod
    def load(cls):
        try:
            with open(data_file(_FILENAME), "r", encoding="utf-8") as fh:
                data = json.load(fh)
            for k in _FIELDS:
                if k in data:
                    setattr(cls, k, float(data[k]))
        except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError, TypeError):
            cls.save()

    @classmethod
    def save(cls):
        try:
            with open(data_file(_FILENAME), "w", encoding="utf-8") as fh:
                json.dump({k: getattr(cls, k) for k in _FIELDS}, fh, indent=2)
        except OSError:
            pass
