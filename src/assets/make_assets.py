"""Generador de recursos gráficos (splash + logo/icono) para qNMR Assistant.

Imágenes modernas en la paleta blanco -> azul marino. Usa Pillow (no necesita
pantalla ni Qt). Reejecutar para regenerar:

    python assets/make_assets.py      # requiere: pip install pillow

Salida (en assets/images):
    splash-image.png   pantalla de inicio (600x340)
    app_logo.png       logo 256x256 (icono de ventana / barra de tareas)
    AppIcon.ico        icono multi-tamaño (16..256) para empaquetar y ventana
"""
import os

from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
FONT_DIR = r"C:\Windows\Fonts"

NAVY = (11, 37, 69)
BLUE = (27, 82, 153)
ACCENT = (46, 139, 192)
ACCENT_L = (91, 176, 224)
WHITE = (255, 255, 255)

# Perfil de un "espectro" de RMN estilizado (x relativo, altura relativa)
PEAKS = [(0.05, 0.30), (0.13, 0.55), (0.20, 0.22), (0.29, 0.78), (0.37, 0.40),
         (0.47, 1.00), (0.55, 0.30), (0.63, 0.62), (0.71, 0.20), (0.80, 0.72),
         (0.88, 0.34), (0.95, 0.50)]


def font(size, bold=True):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


def _lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _grad_color(t, stops):
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if t <= p1:
            tt = (t - p0) / (p1 - p0) if p1 > p0 else 0.0
            return _lerp(c0, c1, tt)
    return stops[-1][1]


def gradient(W, H):
    stops = [(0.0, NAVY), (0.55, BLUE), (1.0, ACCENT)]
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=_grad_color(y / max(1, H - 1), stops))
    return img.convert("RGBA")


def draw_spectrum(d, rect, color, width):
    x0, y0, x1, y1 = rect
    w = x1 - x0
    h = y1 - y0
    base = y1
    r = width / 2
    for xf, hf in PEAKS:
        x = round(x0 + xf * w)
        ytop = round(base - hf * h)
        d.line([(x, round(base)), (x, ytop)], fill=color, width=width)
        d.ellipse([x - r, ytop - r, x + r, ytop + r], fill=color)  # cap redondeado
    d.line([(round(x0), round(base)), (round(x1), round(base))],
           fill=color, width=max(1, width // 2))


def make_splash(path, W=600, H=340):
    img = gradient(W, H)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Círculos decorativos tenues
    for cx, cy, rad, a in [(0.86, 0.18, 150, 22), (0.12, 0.92, 200, 15), (0.72, 0.97, 120, 17)]:
        x, y = cx * W, cy * H
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(255, 255, 255, a))

    # Espectro tenue de fondo
    draw_spectrum(d, (44, 168, W - 44, 286), (255, 255, 255, 55), 6)

    img = Image.alpha_composite(img, overlay)
    d = ImageDraw.Draw(img)

    # Línea de acento
    d.rectangle([46, 116, 176, 121], fill=ACCENT_L)
    # Título
    d.text((44, 50), "qNMR Assistant", font=font(52, bold=True), fill=WHITE)
    # Subtítulo
    d.text((46, 128), "Quantitative NMR  ·  sample preparation & quantitation",
           font=font(18, bold=False), fill=(222, 234, 246))
    # Versión (abajo derecha) y autor (abajo izquierda)
    ver = "v2026.1"
    vf = font(17, bold=True)
    vw = d.textlength(ver, font=vf)
    d.text((W - 44 - vw, H - 40), ver, font=vf, fill=(205, 226, 242))
    d.text((46, H - 38), "by J. R. Belmonte", font=font(15, bold=False), fill=(185, 208, 228))

    img.save(path, "PNG")


def make_logo(size):
    img = gradient(size, size)
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    # Círculo decorativo
    cx, cy, rad = size * 0.82, size * 0.18, size * 0.34
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(255, 255, 255, 24))
    # Espectro central
    m = size * 0.17
    draw_spectrum(d, (m, size * 0.30, size - m, size * 0.70), WHITE, max(2, round(size * 0.035)))
    img = Image.alpha_composite(img, overlay)

    # Esquinas redondeadas
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1],
                                           radius=int(size * 0.22), fill=255)
    img.putalpha(mask)
    return img


def main():
    make_splash(os.path.join(ASSETS, "splash-image.png"))
    logo = make_logo(256)
    logo.save(os.path.join(ASSETS, "app_logo.png"), "PNG")
    logo.save(os.path.join(ASSETS, "AppIcon.ico"),
              sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    # Icono de macOS (.icns) — best effort (requiere Pillow con soporte ICNS)
    try:
        make_logo(512).save(os.path.join(ASSETS, "AppIcon.icns"))
        print("AppIcon.icns generado")
    except Exception as e:  # noqa: BLE001
        print("AppIcon.icns NO generado (genéralo en Mac con iconutil):", e)
    print("Recursos generados en", ASSETS)


if __name__ == "__main__":
    main()
