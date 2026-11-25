"""Recorta y optimiza las fotografías (fuente: Unsplash) para el sitio.

Uso:
    python3 src/procesar_imagenes.py <carpeta_con_fotos_originales>
    python3 src/procesar_imagenes.py --web        # regenera las versiones WebP y los fondos
    python3 src/procesar_imagenes.py --fondos     # solo regenera assets/js/fondos/

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

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contenido import MATERIAS  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "assets" / "img" / "fotos"

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
    elif sys.argv[1:] == ["--web"]:
        variantes()
        fondos()
    else:
        main(sys.argv[1])
