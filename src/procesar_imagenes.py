"""Recorta y optimiza las fotografías (fuente: Unsplash) para el sitio.

Uso:
    python3 src/procesar_imagenes.py <carpeta_con_fotos_originales>
    python3 src/procesar_imagenes.py --web        # regenera las versiones WebP y los fondos
    python3 src/procesar_imagenes.py --fondos     # solo regenera assets/js/fondos/
    python3 src/procesar_imagenes.py --encabezados [nombre ...]
                                                  # encabezados de página para Google Sites

Genera:
    assets/img/fotos/<nombre>.jpg          portada 2:1 para el sitio web
    assets/img/fotos/<nombre>-card.jpg     tarjeta 3:2 para el sitio web
    assets/img/fotos/*-<ancho>.webp        versiones WebP en varios anchos (srcset)
    assets/js/fondos/<nombre>.js           la foto incrustada (data URI) para que el agua WebGL
                                           la refracte también al abrir el sitio con doble clic
"""
import base64
import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contenido import MATERIAS  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "assets" / "img" / "fotos"
ENCABEZADOS = RAIZ / "google-sites" / "imagenes" / "encabezados"
NOCHE = (10, 18, 34)

# punto focal vertical (0 = arriba, 1 = abajo) para cada foto
FOCO = {
    "tutoria": 0.62, "historia": 0.42, "sexualidad": 0.36, "socioemocional": 0.55,
    "inicio": 0.55, "equipo": 0.5, "proyecto": 0.5, "fisica": 0.5,
}


def recorte(img, proporcion, foco_y):
    w, h = img.size
    if w / h > proporcion:            # demasiado ancha: recorta a los lados
        nw = int(h * proporcion)
        x = (w - nw) // 2
        return img.crop((x, 0, x + nw, h))
    nh = int(w / proporcion)          # demasiado alta: recorta arriba/abajo
    y = int((h - nh) * foco_y)
    return img.crop((0, y, w, y + nh))


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def encabezado(img, color, foco):
    """Foto 3:1 oscurecida hacia la izquierda, con brillo del color de la página y cuadrícula
    (para el encabezado tipo "Banner" de cada página de Google Sites)."""
    w, h = 2400, 800
    base = recorte(img, 3.0, foco).resize((w, h), Image.LANCZOS).convert("RGBA")
    capa = Image.new("RGBA", (w, h))
    px = capa.load()
    for x in range(w):
        a_h = 0.9 - 0.55 * (x / w)
        for y in range(h):
            px[x, y] = (*NOCHE, int(255 * min(0.95, a_h + 0.25 * (y / h) ** 2)))
    base = Image.alpha_composite(base, capa)
    brillo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(brillo).ellipse((-700, h - 520, 900, h + 700), fill=(*hex_rgb(color), 150))
    base = Image.alpha_composite(base, brillo.filter(ImageFilter.GaussianBlur(160)))
    rejilla = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(rejilla)
    for x in range(0, w, 44):
        alfa = int(26 * max(0.0, 1 - x / (w * 0.75)))
        if alfa:
            d.line([(x, 0), (x, h)], fill=(160, 185, 255, alfa), width=1)
    for y in range(0, h, 44):
        d.line([(0, y), (int(w * 0.75), y)], fill=(160, 185, 255, 18), width=1)
    return Image.alpha_composite(base, rejilla).convert("RGB")


def encabezados(solo=None):
    """Encabezados de Google Sites a partir de las fotos ya recortadas (assets/img/fotos)."""
    paginas = [("00-inicio", "inicio", "#3b5bff")]
    paginas += [(f"{i:02d}-{m['slug']}", m["slug"], m["color"]) for i, m in enumerate(MATERIAS, 1)]
    paginas += [("11-equipo", "equipo", "#3b5bff"), ("12-calendario", "proyecto", "#ff9a3d")]
    ENCABEZADOS.mkdir(parents=True, exist_ok=True)
    for archivo, foto, color in paginas:
        if solo and archivo.split("-", 1)[1] not in solo:
            continue
        img = Image.open(SALIDA / f"{foto}.jpg").convert("RGB")
        encabezado(img, color, FOCO.get(foto, 0.5)).save(ENCABEZADOS / f"{archivo}.jpg", quality=82, optimize=True, progressive=True)
        print("encabezado", archivo)


def main(origen):
    SALIDA.mkdir(parents=True, exist_ok=True)
    fotos = {f.stem: ImageOps.exif_transpose(Image.open(f)).convert("RGB") for f in sorted(Path(origen).glob("*.jpg"))}
    for nombre, img in fotos.items():
        foco = FOCO.get(nombre, 0.5)
        recorte(img, 2.0, foco).resize((2000, 1000), Image.LANCZOS).save(
            SALIDA / f"{nombre}.jpg", quality=76, optimize=True, progressive=True)
        recorte(img, 1.5, foco).resize((900, 600), Image.LANCZOS).save(
            SALIDA / f"{nombre}-card.jpg", quality=74, optimize=True, progressive=True)
        print("foto", nombre)
    variantes()
    fondos()


def variantes():
    """Versiones WebP en varios anchos para <picture> / srcset (cargan más rápido)."""
    for f in sorted(SALIDA.glob("*.jpg")):
        img = Image.open(f).convert("RGB")
        anchos = (600, 900) if f.stem.endswith("-card") else (800, 1280, 2000)
        for w in anchos:
            h = round(img.height * w / img.width)
            img.resize((w, h), Image.LANCZOS).save(SALIDA / f"{f.stem}-{w}.webp", "WEBP", quality=72, method=6)
        print("webp", f.stem, anchos)


def fondos():
    """Foto de fondo de cada página como data URI dentro de un .js (textura para el agua WebGL)."""
    destino = RAIZ / "assets" / "js" / "fondos"
    destino.mkdir(parents=True, exist_ok=True)
    for f in sorted(SALIDA.glob("*.jpg")):
        if f.stem.endswith("-card") or f.stem == "proyecto":  # "proyecto" no es fondo de página
            continue
        img = Image.open(f).convert("RGB").resize((1280, 640), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=62, optimize=True, progressive=True)
        datos = base64.b64encode(buf.getvalue()).decode("ascii")
        (destino / f"{f.stem}.js").write_text(
            f'/* Fondo de "{f.stem}" para el agua WebGL. Generado por src/procesar_imagenes.py */\n'
            f'window.FONDO = "data:image/jpeg;base64,{datos}";\n', encoding="utf-8")
        print("fondo", f.stem, len(datos) // 1024, "KB")


if __name__ == "__main__":
    if sys.argv[1:] == ["--fondos"]:
        fondos()
    elif sys.argv[1:2] == ["--encabezados"]:
        encabezados(sys.argv[2:] or None)
    elif sys.argv[1:] == ["--web"]:
        variantes()
        fondos()
    else:
        main(sys.argv[1])
