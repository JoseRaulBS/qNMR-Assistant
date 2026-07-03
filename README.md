<p align="center">
  <img src="assets/images/app_logo.png" width="96" alt="qNMR Assistant logo">
</p>

<h1 align="center">qNMR Assistant</h1>

<p align="center">
  Desktop tool for quantitative <sup>1</sup>H&nbsp;NMR (qNMR): sample-preparation planning and
  concentration calculation with an internal standard.<br>
  <em>Herramienta de escritorio para RMN cuantitativa: preparación de muestra y
  cuantificación con estándar interno. <a href="#español">Documentación en español ↓</a></em>
</p>

<p align="center">
  <a href="https://github.com/JoseRaulBS/qNMR-Assistant/releases/latest"><img src="https://img.shields.io/github/v/release/JoseRaulBS/qNMR-Assistant?label=release&color=1f4e79" alt="Latest release"></a>
  <a href="https://github.com/JoseRaulBS/qNMR-Assistant/actions/workflows/release.yml"><img src="https://github.com/JoseRaulBS/qNMR-Assistant/actions/workflows/release.yml/badge.svg" alt="Build status"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/GUI-PyQt6-2ea44f" alt="PyQt6">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
</p>

![qNMR Assistant — quantitation screen](docs/screenshot-quantitation.png)

## Download

Grab the latest build for your system from the
**[Releases page](https://github.com/JoseRaulBS/qNMR-Assistant/releases/latest)**:

| System | File | How to run |
|---|---|---|
| Windows 10/11 (64-bit) | `qNMR_Assistant-windows-x64.exe` | Double-click. Portable, no installation. |
| Linux (x86-64) | `qNMR_Assistant-linux-x64.tar.gz` | `tar -xzf` … then run `./qNMR_Assistant` |
| macOS (Apple Silicon) | `qNMR_Assistant-macos-arm64.zip` | Unzip → right-click `qNMR Assistant.app` → *Open* |

> **Unsigned binaries.** This is academic software and the executables are not
> code-signed. Windows SmartScreen will ask for *"More info → Run anyway"* the
> first time; macOS requires right-click → *Open* once. Intel-Mac users should
> [run from source](#run-from-source).

## Features

- **Quantitation** — relative qNMR with internal standard: enter the measured
  integrals for up to 10 replicates and get % w/w per replicate plus mean,
  standard deviation and RSD. Optional sample density adds % w/v and g/L.
- **Sample preparation assistant** — given the expected analyte concentration,
  it recommends how much internal standard and sample to weigh (or pipette,
  for liquids) and generates a step-by-step protocol.
- **Internal-standard editor** — add or remove standards (name, MW, protons,
  purity, chemical shift); stored persistently per user.
- **One-page PDF report** and **CSV export** (Excel-friendly).
- **Bilingual interface** (English / Spanish), switchable at runtime.
- Decimal comma or point accepted everywhere; invalid fields highlighted.

## How it works

The quantitation implements the standard relative qNMR equation:

```
P_x (% w/w) = (I_x / I_IS) · (N_IS / N_x) · (M_x / M_IS) · (m_IS / m_x) · P_IS · 100
```

where `I` are the measured integrals, `N` the number of protons of each signal,
`M` the molecular weights, `m` the weighed masses and `P_IS` the purity of the
internal standard. The formulas are validated by the test suite in
[`test_formulas.py`](test_formulas.py), which runs on every release build.

## Run from source

```bash
git clone https://github.com/JoseRaulBS/qNMR-Assistant.git
cd qNMR-Assistant
python -m venv venv
# Windows: venv\Scripts\activate   |   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Requires Python ≥ 3.10. The only runtime dependency is PyQt6.

## Build the executables

See [BUILD.md](BUILD.md). Releases are built automatically by
[GitHub Actions](.github/workflows/release.yml) on Windows, Linux and macOS
runners whenever a `v*` tag is pushed.

## User data

Standards and preferences are stored per user (not next to the executable):

- Windows: `%APPDATA%\qNMR\qNMR Assistant\`
- macOS: `~/Library/Application Support/qNMR Assistant/`
- Linux: `~/.local/share/qNMR Assistant/`

## License & author

[MIT](LICENSE) — created by **José Raúl Belmonte** (2023), unified and updated
in 2026. Contact: joseraulbs@gmail.com ·
[github.com/JoseRaulBS](https://github.com/JoseRaulBS)

---

<a name="español"></a>

# Español

**qNMR Assistant** es una aplicación de escritorio para **RMN cuantitativa de
protón (qNMR)** con estándar interno, pensada para el trabajo rutinario de
laboratorio.

## Descarga

En la **[página de Releases](https://github.com/JoseRaulBS/qNMR-Assistant/releases/latest)**:

| Sistema | Archivo | Cómo ejecutar |
|---|---|---|
| Windows 10/11 (64 bits) | `qNMR_Assistant-windows-x64.exe` | Doble clic. Portable, sin instalación. |
| Linux (x86-64) | `qNMR_Assistant-linux-x64.tar.gz` | `tar -xzf` … y ejecutar `./qNMR_Assistant` |
| macOS (Apple Silicon) | `qNMR_Assistant-macos-arm64.zip` | Descomprimir → clic derecho en `qNMR Assistant.app` → *Abrir* |

> **Ejecutables sin firmar.** La primera vez, Windows SmartScreen pedirá
> *"Más información → Ejecutar de todas formas"*; en macOS, clic derecho →
> *Abrir* (solo una vez). En Macs Intel, ejecutar desde el código fuente.

## Funciones

- **Cuantificación** — qNMR relativa con estándar interno: hasta 10 réplicas
  con % p/p por réplica, media, desviación estándar y RSD. Con la densidad
  opcional añade % p/v y g/L.
- **Asistente de preparación de muestra** — recomienda cuánto estándar interno
  y cuánta muestra pesar (o pipetear, si es líquida) y genera un protocolo
  paso a paso.
- **Editor de estándares internos** — alta y baja de estándares (nombre, PM,
  protones, pureza, desplazamiento químico), con almacenamiento persistente.
- **Informe PDF de una página** y **exportación CSV** (compatible con Excel).
- **Interfaz bilingüe** (español / inglés), conmutable en caliente.
- Acepta coma o punto decimal; resalta en rojo los campos inválidos.

## Ejecutar desde el código

```bash
git clone https://github.com/JoseRaulBS/qNMR-Assistant.git
cd qNMR-Assistant
python -m venv venv
# Windows: venv\Scripts\activate   |   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Licencia y autor

[MIT](LICENSE) — creado por **José Raúl Belmonte** (2023), unificado y
actualizado en 2026. Contacto: joseraulbs@gmail.com ·
[github.com/JoseRaulBS](https://github.com/JoseRaulBS)
