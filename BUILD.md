# Compilar qNMR Assistant (ejecutables)

> PyInstaller **no compila de forma cruzada**: hay que construir cada ejecutable
> **en su propio sistema operativo** (o usar CI con runners de cada SO).

## Requisitos (en cada máquina)
```bash
python -m venv venv
# activar el venv (Windows: venv\Scripts\activate ; Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt      # PyQt6 (runtime)
pip install pyinstaller              # herramienta de build
pip install pillow                   # solo si vas a regenerar los iconos/splash
```

## Regenerar iconos/splash (opcional)
```bash
python assets/make_assets.py
```
Crea `splash-image.png`, `app_logo.png`, `AppIcon.ico` (Windows) y `AppIcon.icns` (Mac).
En Linux se usa `app_logo.png` para el `.desktop`.

## Construir el ejecutable (igual en los tres SO)
```bash
# desde la raíz del repositorio
pyinstaller --noconfirm --clean qNMR_Assistant.spec
```
> Las Releases oficiales se construyen automáticamente con GitHub Actions
> (`.github/workflows/release.yml`) al subir una etiqueta `v*`.
Resultado en `dist/`:
- **Windows** → `dist/qNMR_Assistant.exe` (un solo archivo).
- **macOS**   → `dist/qNMR Assistant.app` (bundle). Para abrirlo sin firmar:
  clic derecho → *Abrir* (una vez).
- **Linux**   → `dist/qNMR_Assistant` (binario). Recomendado distribuir como
  **AppImage**; o crear un `.desktop` que apunte a él con `app_logo.png`.

## Datos de usuario
La app guarda estándares y ajustes en la carpeta de datos del SO (no junto al exe):
- Windows: `%APPDATA%\qNMR\qNMR Assistant\`
- macOS:   `~/Library/Application Support/qNMR Assistant/`
- Linux:   `~/.local/share/qNMR Assistant/`

## Avisos de seguridad (sin firmar)
- **Windows**: la primera vez SmartScreen muestra *"Windows protegió tu PC"* →
  *Más información* → *Ejecutar de todas formas* (una vez por equipo). No pide admin.
- **macOS**: *"desarrollador no identificado"* → clic derecho → *Abrir* (una vez).
- Para eliminarlos hace falta firma de código (ver notas del proyecto: SignPath
  gratis para open source en Windows; Apple Developer 99 $/año para Mac).
