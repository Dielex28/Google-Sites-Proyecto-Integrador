"""Recorta y optimiza las fotografías (fuente: Unsplash) para el sitio y para Google Sites.

Uso:  python3 src/procesar_imagenes.py <carpeta_con_fotos_originales>

Genera:
    assets/img/fotos/<nombre>.jpg          portada 2:1 para el sitio web
    assets/img/fotos/<nombre>-card.jpg     tarjeta 3:2 para el sitio web
    google-sites/imagenes/encabezados/*.jpg  encabezados 3:1 con el tono de cada materia
"""
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
    """Foto 3:1 oscurecida hacia la izquierda, con brillo del color de la materia y cuadrícula."""
    w, h = 2400, 800
    base = recorte(img, 3.0, foco).resize((w, h), Image.LANCZOS).convert("RGBA")
    # degradado nocturno de izquierda a derecha + refuerzo inferior
    capa = Image.new("RGBA", (w, h))
    px = capa.load()
    for x in range(w):
        a_h = 0.9 - 0.55 * (x / w)
        for y in range(0, h, 1):
            a = min(0.95, a_h + 0.25 * (y / h) ** 2)
            px[x, y] = (*NOCHE, int(255 * a))
    base = Image.alpha_composite(base, capa)
    # brillo del color de la materia en la esquina inferior izquierda
    brillo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(brillo)
    d.ellipse((-700, h - 520, 900, h + 700), fill=(*hex_rgb(color), 150))
    brillo = brillo.filter(ImageFilter.GaussianBlur(160))
    base = Image.alpha_composite(base, brillo)
    # cuadrícula fina tipo hoja de ingeniería que se desvanece a la derecha
    rejilla = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(rejilla)
    paso = 44
    for x in range(0, w, paso):
        alfa = int(26 * max(0.0, 1 - x / (w * 0.75)))
        if alfa:
            d.line([(x, 0), (x, h)], fill=(160, 185, 255, alfa), width=1)
    for y in range(0, h, paso):
        d.line([(0, y), (int(w * 0.75), y)], fill=(160, 185, 255, 18), width=1)
    base = Image.alpha_composite(base, rejilla)
    return base.convert("RGB")


def main(origen):
    SALIDA.mkdir(parents=True, exist_ok=True)
    ENCABEZADOS.mkdir(parents=True, exist_ok=True)
    fotos = {f.stem: ImageOps.exif_transpose(Image.open(f)).convert("RGB") for f in sorted(Path(origen).glob("*.jpg"))}
    for nombre, img in fotos.items():
        foco = FOCO.get(nombre, 0.5)
        recorte(img, 2.0, foco).resize((2000, 1000), Image.LANCZOS).save(
            SALIDA / f"{nombre}.jpg", quality=76, optimize=True, progressive=True)
        recorte(img, 1.5, foco).resize((900, 600), Image.LANCZOS).save(
            SALIDA / f"{nombre}-card.jpg", quality=74, optimize=True, progressive=True)
        print("foto", nombre)
    extras = [("00-inicio", "inicio", "#2f5bff"), ("11-equipo", "equipo", "#2f5bff")]
    materias = [(f"{i:02d}-{m['slug']}", m["slug"], m["color"]) for i, m in enumerate(MATERIAS, 1)]
    for archivo, foto, color in extras + materias:
        if foto in fotos:
            encabezado(fotos[foto], color, FOCO.get(foto, 0.5)).save(
                ENCABEZADOS / f"{archivo}.jpg", quality=80, optimize=True, progressive=True)
            print("encabezado", archivo)


if __name__ == "__main__":
    main(sys.argv[1])
