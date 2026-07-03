"""Almacén de estándares internos (IS), editable y persistente.

Los estándares se guardan en `internal_standards.json` (junto a este módulo).
Si el archivo no existe, se siembra con un conjunto por defecto.

Cada estándar es un dict:
    {"name": str, "molecular_weight": float, "number_of_protons": int,
     "purity": float, "shift": float}   # shift = desplazamiento químico (ppm)

Un estándar con varias señales se representa como varias entradas (una por señal).
"""
import json

from paths import data_file

_FILENAME = "internal_standards.json"

_DEFAULTS = [
    {"name": "TMSP", "molecular_weight": 172.28, "number_of_protons": 9, "purity": 0.988, "shift": 0.0},
    {"name": "TMS", "molecular_weight": 88.22, "number_of_protons": 12, "purity": 0.9999, "shift": 0.0},
    {"name": "1,3,5-Trimethoxybenzene", "molecular_weight": 168.19, "number_of_protons": 9, "purity": 0.9996, "shift": 3.7},
    {"name": "1,3,5-Trimethoxybenzene", "molecular_weight": 168.19, "number_of_protons": 3, "purity": 0.9996, "shift": 6.1},
    {"name": "Dimethyl sulfone", "molecular_weight": 94.13, "number_of_protons": 6, "purity": 0.9996, "shift": 3.0},
]


class Standards:
    items = []

    @classmethod
    def load(cls):
        try:
            with open(data_file(_FILENAME), "r", encoding="utf-8") as fh:
                cls.items = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            cls.items = [dict(d) for d in _DEFAULTS]
            cls.save()
        return cls.items

    @classmethod
    def save(cls):
        try:
            with open(data_file(_FILENAME), "w", encoding="utf-8") as fh:
                json.dump(cls.items, fh, indent=2, ensure_ascii=False)
        except OSError:
            pass

    @classmethod
    def label(cls, item):
        """Etiqueta para el desplegable: nombre · desplazamiento ppm (nº H)."""
        return f"{item['name']}  ·  {item['shift']:g} ppm  ({item['number_of_protons']}H)"

    @classmethod
    def labels(cls):
        return [cls.label(it) for it in cls.items]

    @classmethod
    def add(cls, name, molecular_weight, number_of_protons, purity, shift):
        cls.items.append({
            "name": name,
            "molecular_weight": float(molecular_weight),
            "number_of_protons": int(number_of_protons),
            "purity": float(purity),
            "shift": float(shift),
        })
        cls.save()

    @classmethod
    def remove(cls, index):
        if 0 <= index < len(cls.items):
            cls.items.pop(index)
            cls.save()
