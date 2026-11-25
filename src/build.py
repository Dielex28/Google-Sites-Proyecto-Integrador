"""Generador del sitio "Mapa del Semestre 1A" (estilo liquid glass).

Uso:
    python3 src/build.py      # genera el sitio web y el kit de Google Sites

Salidas:
    index.html, equipo.html, materias/*.html   -> sitio web completo
    assets/js/datos.js                         -> calendario e índice del buscador
    google-sites/codigos/**.html               -> bloques para "Insertar > Código" de Google Sites
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contenido import AREAS, EJEMPLO_PSEINT, MATERIAS, SITIO  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ICONOS = Path(__file__).resolve().parent / "iconos"
CODIGOS = RAIZ / "google-sites" / "codigos"

FUENTES = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Geist:wght@300..800&family=Geist+Mono:wght@400..600&display=swap">'
)

# Categorías de evaluación de Física: orden fijo = orden de color (paleta validada)
EVAL = [
    ("examen", "Exámenes", "s1"),
    ("act", "Actividades", "s2"),
    ("tarea", "Tareas", "s3"),
    ("integrador", "Integrador", "s4"),
    ("part", "Participación", "s5"),
]
EVAL_NOMBRE = {k: n for k, n, _ in EVAL}
EVAL_SLOT = {k: s for k, _, s in EVAL}

COLORES_EQUIPO = ["#E8962E", "#3B6FF5", "#E0517A", "#17A88A", "#D9473B", "#8B4FF0", "#2E9E57", "#1C97C9"]
PALETA_INICIO = ["#3b5bff", "#8b4ff0", "#ff9a3d", "#17a88a"]


def esc(s):
    return html.escape(str(s), quote=True)


_cache_iconos = {}


def icon(nombre, cls="ic"):
    if nombre not in _cache_iconos:
        svg = (ICONOS / f"{nombre}.svg").read_text(encoding="utf-8")
        svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
        svg = re.sub(r'\s*class="[^"]*"', "", svg)
        svg = re.sub(r'\s*(width|height)="24"', "", svg)
        svg = re.sub(r"\s+", " ", svg).replace("> <", "><").strip()
        _cache_iconos[nombre] = svg
    return _cache_iconos[nombre].replace("<svg", f'<svg class="{cls}" aria-hidden="true" focusable="false"', 1)


def contar(temas):
    return sum(1 + contar(t["sub"]) for t in temas)


def total_temas(m):
    return sum(contar(s["temas"]) for s in m["secciones"])


def etiqueta_secciones(m, n=None):
    n = len(m["secciones"]) if n is None else n
    if m["tipo_seccion"] == "Unidad":
        return "unidad" if n == 1 else "unidades"
    return "eje temático" if n == 1 else "ejes temáticos"


def tipo_seccion(m):
    if m["slug"] == "fisica":
        return "Unidad de competencia"
    return "Unidad" if m["tipo_seccion"] == "Unidad" else "Eje temático"


def fmt(x):
    return f"{x:.1f}"


TOTAL_TEMAS = sum(total_temas(m) for m in MATERIAS)
MAX_TEMAS = max(total_temas(m) for m in MATERIAS)
FISICA = next(m for m in MATERIAS if m["slug"] == "fisica")

# Los integrantes se leen de assets/js/equipo.js (un renglón por persona)
NOMBRES_EQUIPO = re.findall(r'nombre:\s*"([^"]*)"', (RAIZ / "assets/js/equipo.js").read_text(encoding="utf-8"))
N_EQUIPO = len(NOMBRES_EQUIPO)
PALABRAS = {1: "Un", 2: "Dos", 3: "Tres", 4: "Cuatro", 5: "Cinco", 6: "Seis", 7: "Siete", 8: "Ocho", 9: "Nueve", 10: "Diez"}


def por_fila(n):
    """Tarjetas por fila en pantallas anchas, para que ninguna quede sola."""
    return max(1, n) if n <= 5 else 3 if n == 6 else 4 if n <= 8 else 5


def integrantes_texto(n=N_EQUIPO):
    return f'{PALABRAS.get(n, n)} {"integrante" if n == 1 else "integrantes"}'


def iniciales(nombre):
    partes = nombre.split()
    return "".join(p[0] for p in partes[:2]).upper() if partes else ""


# ---------------------------------------------------------------- identificadores de temas
def asignar_ids():
    """Da un id estable a cada tema (t<sección>-<n>) para enlazarlo desde el buscador."""
    for m in MATERIAS:
        for i, s in enumerate(m["secciones"], 1):
            contador = [0]

            def recorrer(temas):
                for t in temas:
                    contador[0] += 1
                    t["id"] = f"t{i}-{contador[0]}"
                    recorrer(t["sub"])

            recorrer(s["temas"])


asignar_ids()


# ---------------------------------------------------------------- calendario (Física = calendario del ciclo)
def semana_actual(hoy=None):
    hoy = hoy or date.today()
    cal = FISICA["calendario"]
    if hoy < date.fromisoformat(cal[0]["ini"]):
        return 0
    for w in cal:
        if (hoy - date.fromisoformat(w["ini"])).days < 7:
            return w["s"]
    return 19


SEMANA = semana_actual()


def puntos_texto(w):
    return " · ".join(f'{x[2] if len(x) > 2 else EVAL_NOMBRE[x[0]]} {fmt(x[1])}' for x in w["p"])


def datos_semanas():
    return [
        {"s": w["s"], "ini": w["ini"], "f": w["fechas"], "t": w["temas"], "p": puntos_texto(w), "u": w["u"]}
        for w in FISICA["calendario"]
    ]


def texto_semana(s):
    cal = FISICA["calendario"]
    if s <= 0:
        return "El ciclo inicia el lunes 17 de agosto con la semana 1."
    if s > 18:
        return "El ciclo 2026B ya concluyó. ¡Gracias por acompañarnos!"
    w = cal[s - 1]
    if s == 18:
        return f"Semana 18 · {w['fechas']}: fecha límite para el registro y publicación de la evaluación continua."
    return f"Semana {s} · {w['fechas']}. Faltan {18 - s} semanas para el cierre del ciclo."


def indice_busqueda():
    items = []
    for m in MATERIAS:
        base = f"materias/{m['slug']}.html"
        items.append({"t": m["nombre"], "m": "Materia", "h": base, "c": m["color"]})
        for i, s in enumerate(m["secciones"], 1):
            etiqueta = f"{m['corto']} · {tipo_seccion(m)} {i}"
            items.append({"t": s["titulo"], "m": etiqueta, "h": f"{base}#u{i}", "c": m["color"]})

            def recorrer(temas):
                for t in temas:
                    texto = f'{t["c"]} {t["t"]}'.strip()
                    items.append({"t": texto, "m": etiqueta, "h": f"{base}#{t['id']}", "c": m["color"]})
                    recorrer(t["sub"])

            recorrer(s["temas"])
    return items


# ---------------------------------------------------------------- piezas comunes
def _mapa(id_):
    return (f'<feImage data-lgmap href="" x="0" y="0" width="100%" height="100%" '
            f'preserveAspectRatio="none" result="{id_}"/>')


def _canal(escala, matriz, nombre):
    return (f'<feDisplacementMap in="SourceGraphic" in2="map" scale="{escala}" xChannelSelector="R" yChannelSelector="G" result="d{nombre}"/>'
            f'<feColorMatrix in="d{nombre}" type="matrix" values="{matriz}" result="{nombre}"/>')


# Filtros SVG de refracción (los usa backdrop-filter en Chromium; main.js genera el mapa).
#   #lg   -> refracción de borde para vidrio grande
#   #lg-c -> refracción con dispersión cromática (lentes, gota del cursor)
SVG_DEFS = (
    '<svg class="defs" width="0" height="0" aria-hidden="true" focusable="false">'
    '<filter id="lg" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
    + _mapa("map") +
    '<feDisplacementMap in="SourceGraphic" in2="map" scale="34" xChannelSelector="R" yChannelSelector="G"/>'
    "</filter>"
    '<filter id="lg-c" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
    + _mapa("map")
    + _canal(46, "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0", "r")
    + _canal(38, "0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0", "g")
    + _canal(30, "0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0", "b")
    + '<feBlend in="r" in2="g" mode="screen" result="rg"/><feBlend in="rg" in2="b" mode="screen"/>'
    "</filter></svg>"
)


def fondo(foto, colores, p=""):
    """Capa fija detrás del vidrio: foto + agua WebGL + tinte + grano."""
    img = f'<img class="bg__photo" src="{p}assets/img/fotos/{foto}.jpg" alt="" decoding="async">' if foto else ""
    clase = "bg bg--photo" if foto else "bg"
    textura = f'\n<script src="{p}assets/js/fondos/{foto}.js" defer></script>' if foto and (RAIZ / f"assets/js/fondos/{foto}.js").exists() else ""
    return (
        f'<div class="{clase}" aria-hidden="true">{img}'
        f'<canvas class="bg__liquid" data-liquid data-colors="{",".join(colores)}"></canvas>'
        '<div class="bg__blobs"><i></i><i></i><i></i></div>'
        '<div class="bg__tint"></div><div class="bg__grain"></div></div>'
        f"{textura}"
    )


def avatares(p="", limite=6):
    caras = "".join(
        f'<span class="av" style="--c:{COLORES_EQUIPO[i % len(COLORES_EQUIPO)]}" title="{esc(n)}">{esc(iniciales(n) or "?")}</span>'
        for i, n in enumerate(NOMBRES_EQUIPO[:limite])
    )
    extra = f'<span class="av av--more">+{N_EQUIPO - limite}</span>' if N_EQUIPO > limite else ""
    return f'<span class="avs">{caras}{extra}</span>'


def sidebar(p, activo):
    generales = [
        ("inicio", "Inicio", "house", f"{p}index.html"),
        ("calendario", "Calendario", "calendar-days", f"{p}index.html#semana"),
        ("equipo", "Equipo", "users", f"{p}equipo.html"),
    ]
    def item(clave, texto, ico, href, color=None):
        actual = ' aria-current="page"' if clave == activo else ""
        estilo = f' style="--acc:{color}"' if color else ""
        clase = "side__item acc" + (" is-active" if clave == activo else "")
        prog = f' data-prog="{clave}"' if color else ""
        punto = f'<span class="side__ic"{prog}>{icon(ico)}</span>'
        return f'<a class="{clase}"{estilo} href="{href}" data-li{actual}>{punto}<span class="side__tx">{esc(texto)}</span></a>'

    gen = "".join(item(*g) for g in generales)
    mats = "".join(item(m["slug"], m["corto"], m["icono"], f"{p}materias/{m['slug']}.html", m["color"]) for m in MATERIAS)
    w = FISICA["calendario"][min(max(SEMANA, 1), 18) - 1]
    pct = min(max(SEMANA, 0), 18) / 18
    return f"""
<aside class="side glass" id="menu" aria-label="Navegación principal" data-drawer>
  <a class="brand" href="{p}index.html">
    <span class="brand__mark" aria-hidden="true">1A</span>
    <span class="brand__txt"><b>Mapa del Semestre</b><small>{SITIO["clave"]} · {SITIO["ciclo"]}</small></span>
  </a>
  <nav class="side__nav" data-lens="v" data-hover>
    <span class="lens" aria-hidden="true"></span>
    <p class="side__label">General</p>{gen}
    <p class="side__label">Materias</p>{mats}
  </nav>
  <div class="side__foot">
    <a class="side__week" href="{p}index.html#semana">
      <span class="gauge gauge--sm" style="--p:{pct:.3f}" data-gauge><span class="gauge__fill"><i></i><i></i></span><b data-week-n>{SEMANA if 1 <= SEMANA <= 18 else "—"}</b></span>
      <span class="side__weektx"><b>Semana <span data-week-n>{SEMANA if 1 <= SEMANA <= 18 else "—"}</span> de 18</b><small data-week-dates>{esc(w["fechas"])}</small></span>
    </a>
    <button class="side__motion" type="button" data-calma aria-pressed="false">{icon("droplets")}<span>Efecto líquido</span><i class="switch" aria-hidden="true"></i></button>
  </div>
</aside>
<div class="scrim" data-drawer-close hidden></div>"""


def topbar(p, migas):
    return f"""
<header class="top">
  <button class="iconbtn glass-pill top__menu" type="button" data-drawer-open aria-label="Abrir menú" aria-controls="menu" aria-expanded="false">{icon("menu")}</button>
  <div class="top__crumbs">
    <nav class="crumbs" aria-label="Ruta de navegación">{migas}</nav>
    <p class="top__date" data-hoy></p>
  </div>
  <div class="top__tools">
    <div class="search-wrap" data-search data-base="{p}">
      <label class="search glass-pill" for="buscar">{icon("search")}<input id="buscar" type="search" placeholder="Buscar un tema…" autocomplete="off" spellcheck="false" role="combobox" aria-autocomplete="list" aria-controls="resultados" aria-expanded="false"><kbd>/</kbd></label>
      <div class="search__res glass" id="resultados" role="listbox" aria-label="Resultados" hidden></div>
    </div>
    <a class="avatars glass-pill" href="{p}equipo.html" aria-label="Ver al equipo: {esc(", ".join(NOMBRES_EQUIPO))}">{avatares(p)}</a>
  </div>
</header>"""


def migas(p, *partes):
    out = [f'<a href="{p}index.html">Inicio</a>']
    for texto, href in partes:
        out.append(f'<span aria-hidden="true">{icon("chevron-right", "ic ic--xs")}</span>')
        out.append(f'<a href="{href}">{esc(texto)}</a>' if href else f'<span aria-current="page">{esc(texto)}</span>')
    return "".join(out)


def dock(p, activo):
    def a(clave, texto, ico, href):
        on = " is-active" if clave == activo else ""
        return f'<a class="dock__item{on}" href="{href}" data-li>{icon(ico)}<span>{texto}</span></a>'
    return f"""
<nav class="dock glass" aria-label="Accesos rápidos" data-lens="h">
  <span class="lens" aria-hidden="true"></span>
  {a("inicio", "Inicio", "house", f"{p}index.html")}
  <button class="dock__item{" is-active" if activo in [m["slug"] for m in MATERIAS] else ""}" type="button" data-drawer-open data-li>{icon("layout-grid")}<span>Materias</span></button>
  {a("calendario", "Semana", "calendar-days", f"{p}index.html#semana")}
  {a("equipo", "Equipo", "users", f"{p}equipo.html")}
</nav>"""


def footer():
    return f"""
<footer class="foot">
  <p>{SITIO["escuela"]} · {SITIO["carrera"]} · Grupo {SITIO["grupo"]}, turno {SITIO["turno"].lower()} · Ciclo {SITIO["ciclo"]}</p>
  <p>Proyecto académico elaborado por estudiantes del grupo {SITIO["grupo"]}. No es un sitio oficial de la institución. Fotografías: Unsplash · Íconos: Lucide</p>
</footer>
<a class="totop iconbtn glass-pill" href="#top" aria-label="Volver arriba" data-totop><svg class="totop__ring" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="22" pathLength="100"/></svg>{icon("arrow-up")}</a>"""


def documento(titulo, descripcion, cuerpo, p="", clase=""):
    return f"""<!doctype html>
<html lang="es" data-base="{p}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(descripcion)}">
<meta name="theme-color" content="#06080f">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_MX">
<meta property="og:site_name" content="{esc(SITIO["titulo"])}">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descripcion)}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{p}assets/img/favicon.svg" type="image/svg+xml">
{FUENTES}
<link rel="stylesheet" href="{p}assets/css/estilos.css">
<script>try{{if(localStorage.getItem("calma")==="1")document.documentElement.classList.add("calma")}}catch(e){{}}</script>
</head>
<body class="{clase}" id="top">
{cuerpo}
<script src="{p}assets/js/equipo.js"></script>
<script src="{p}assets/js/datos.js"></script>
<script src="{p}assets/js/main.js" defer></script>
</body>
</html>
"""


def app(p, activo, rutas, contenido, foto, colores):
    return f"""{SVG_DEFS}
{fondo(foto, colores, p)}
<a class="skip" href="#contenido">Saltar al contenido</a>
{sidebar(p, activo)}
<div class="app">
  {topbar(p, rutas)}
  <main id="contenido" class="main">
{contenido}
  </main>
  {footer()}
</div>
{dock(p, activo)}"""


# ---------------------------------------------------------------- portada
def terminal(embed):
    nombres = []
    for m in MATERIAS:
        if embed:
            nombres.append(f'<span class="t-m" style="--acc:{m["color"]}">{m["slug"]}</span>')
        else:
            nombres.append(f'<a class="t-m" style="--acc:{m["color"]}" href="materias/{m["slug"]}.html">{m["slug"]}</a>')
    filas = "".join(f'<p class="tl tl--out">{"  ".join(nombres[a:b])}</p>' for a, b in ((0, 3), (3, 7), (7, 10)))
    prompt = '<span class="t-p">tsin1am@poli</span><span class="t-c">:~/1A$</span> '
    rol = 'role="img"' if embed else 'role="region"'
    s = min(max(SEMANA, 0), 18)
    barra = f'<span class="t-bar">{"█" * s}<span class="t-dim">{"░" * (18 - s)}</span></span>  semana {s} de 18'
    return f"""
<div class="term glass span-5" {rol} aria-label="Terminal decorativa: lista de las diez materias y avance del semestre" data-reveal>
  <div class="term__bar"><i></i><i></i><i></i><span>tsin1am@politecnica — bash</span></div>
  <div class="term__body" data-term data-inicio="{FISICA["calendario"][0]["ini"]}">
    <p class="tl tl--cmd">{prompt}<span class="t-typed">ls materias/</span></p>
    {filas}
    <p class="tl tl--cmd">{prompt}<span class="t-typed">grep -c "tema" temario.txt</span></p>
    <p class="tl tl--out"><span class="t-n">{TOTAL_TEMAS}</span></p>
    <p class="tl tl--cmd">{prompt}<span class="t-typed">./semestre --progreso</span></p>
    <p class="tl tl--out" data-term-progress>{barra}</p>
    <p class="tl tl--cmd tl--last">{prompt}<span class="t-cursor" aria-hidden="true"></span></p>
  </div>
</div>"""


def hero_inicio(embed):
    ctas = "" if embed else (
        f'<div class="hero__cta"><a class="btn btn--liquid" href="#materias" data-ripple>Explorar materias {icon("arrow-right")}</a>'
        f'<a class="btn btn--glass" href="equipo.html" data-ripple>Conocer al equipo</a></div>'
    )
    return f"""
<section class="grid hero" aria-labelledby="titulo">
  <div class="glass panel hero__panel span-7" data-reveal>
    <p class="eyebrow"><span class="pulse"></span>{SITIO["escuela"]}</p>
    <h1 class="hero__title" id="titulo">El mapa de nuestro <span class="liquid-text">primer semestre</span></h1>
    <p class="hero__lead">Proyecto integrador del grupo {SITIO["grupo"]}, turno {SITIO["turno"].lower()}, del {SITIO["carrera"]}. Las diez materias del ciclo {SITIO["ciclo"]} con sus unidades y temas, en un solo lugar.</p>
    {ctas}
  </div>
  {terminal(embed)}
</section>"""


def tarjetas_estadisticas(p, embed):
    conteo = {k: sum(1 for m in MATERIAS if m["area"] == k) for k in AREAS}
    cortos = {"tecnologia": "Tecnología", "ciencias": "Ciencias", "comunicacion": "Lenguaje", "integral": "Integral"}
    areas = "".join(f'<li title="{esc(v)}"><i style="--c:{c}"></i>{cortos[k]} <b>{conteo[k]}</b></li>' for (k, v), c in zip(AREAS.items(), ["#3b6ff5", "#8b4ff0", "#d9473b", "#e8962e"]))
    barras = "".join(
        f'<span class="bar" style="--h:{total_temas(m) / MAX_TEMAS:.3f}" tabindex="0" data-tip="{esc(m["corto"])} · {total_temas(m)} temas" aria-label="{esc(m["nombre"])}: {total_temas(m)} temas"></span>'
        for m in MATERIAS
    )
    s = SEMANA
    ticks = "".join(
        f'<span class="tick{" is-past" if i < s else (" is-now" if i == s else "")}"></span>' for i in range(1, 19)
    )
    ver = "" if embed else f'<a class="pill pill--link" href="{p}equipo.html" data-ripple>Ver equipo {icon("arrow-up-right", "ic ic--xs")}</a>'
    return f"""
<section class="grid stats" aria-label="Resumen del semestre">
  <article class="glass stat span-3" data-reveal data-jelly>
    <p class="stat__k">Materias</p>
    <p class="stat__v"><span data-count="{len(MATERIAS)}">{len(MATERIAS)}</span><small>en 4 áreas</small></p>
    <ul class="stat__areas">{areas}</ul>
  </article>
  <article class="glass stat span-3" data-reveal data-jelly>
    <p class="stat__k">Temas y subtemas</p>
    <p class="stat__v"><span data-count="{TOTAL_TEMAS}">{TOTAL_TEMAS}</span>{"" if embed else '<small data-repaso-global>por repasar</small>'}</p>
    <div class="bars" role="group" aria-label="Temas por materia">{barras}</div>
  </article>
  <article class="glass stat span-3" data-reveal data-jelly>
    <p class="stat__k">Semana del ciclo</p>
    <p class="stat__v"><span data-week-n>{s if 1 <= s <= 18 else "—"}</span><small>de 18</small></p>
    <div class="ticks" data-ticks aria-hidden="true">{ticks}</div>
  </article>
  <article class="glass stat span-3" data-reveal data-jelly>
    <p class="stat__k">Equipo</p>
    <p class="stat__v"><span data-count="{N_EQUIPO}">{N_EQUIPO}</span><small>integrantes</small></p>
    <div class="stat__team">{avatares(p)}{ver}</div>
  </article>
</section>"""


ANCHAS = {"tutoria", "fisica"}


def tarjeta_materia(m, embed):
    n, t = len(m["secciones"]), total_temas(m)
    meta = f'{n} {etiqueta_secciones(m)} · {t} temas'
    ancha = " mcard--wide" if m["slug"] in ANCHAS else ""
    unidades = '<ol class="mcard__list">' + "".join(f"<li>{esc(s['titulo'])}</li>" for s in m["secciones"]) + "</ol>"
    resumen = "" if embed else f'<p class="mcard__sum">{esc(m["resumen"])}</p>'
    foto = "" if embed else f'<img class="mcard__photo" src="assets/img/fotos/{m["slug"]}-card.jpg" alt="" loading="lazy" decoding="async">'
    ir = "" if embed else f'<span class="mcard__go">{icon("arrow-up-right")}</span>'
    etiqueta, cierre = ("article", "article") if embed else (f'a href="materias/{m["slug"]}.html"', "a")
    progreso = "" if embed else (
        f'<div class="mprog" data-prog-card="{m["slug"]}" data-total="{t}" hidden>'
        '<span class="mprog__bar"><i></i></span><small></small></div>'
    )
    return f"""
<{etiqueta} class="mcard glass acc{ancha}" style="--acc:{m['color']}" data-area="{m['area']}" data-reveal data-jelly>
  {foto}
  <div class="mcard__top"><span class="orb">{icon(m["icono"])}</span><span class="mcard__area">{esc(AREAS[m["area"]])}</span>{ir}</div>
  <h3 class="mcard__title">{esc(m["nombre"])}</h3>
  {resumen}{unidades}
  {progreso}
  <p class="mcard__foot">{meta}</p>
</{cierre}>"""


def seccion_materias(embed):
    conteo = {k: sum(1 for m in MATERIAS if m["area"] == k) for k in AREAS}
    filtros = (
        f'<button class="seg__btn is-active" type="button" data-filter="todas" aria-pressed="true" data-li>Todas <small>{len(MATERIAS)}</small></button>'
        + "".join(
            f'<button class="seg__btn" type="button" data-filter="{k}" aria-pressed="false" data-li>{esc(v)} <small>{conteo[k]}</small></button>'
            for k, v in AREAS.items()
        )
    )
    tarjetas = "".join(tarjeta_materia(m, embed) for m in MATERIAS)
    return f"""
<section class="block" id="materias" aria-labelledby="t-materias">
  <header class="block__head">
    <div>
      <p class="eyebrow">Ciclo {SITIO["ciclo"]} · {len(MATERIAS)} materias</p>
      <h2 id="t-materias">Lo que vamos a aprender</h2>
    </div>
    <div class="seg glass-pill" role="group" aria-label="Filtrar materias por área" data-lens="h" data-filters>
      <span class="lens" aria-hidden="true"></span>{filtros}
    </div>
  </header>
  <div class="mgrid" data-mgrid>{tarjetas}</div>
</section>"""


def seccion_semana():
    s = SEMANA
    pct = min(max(s, 0), 18) / 18
    celdas = "".join(
        f'<li class="{"is-past" if w["s"] < s else ("is-now" if w["s"] == s else "")}" title="Semana {w["s"]} · {w["fechas"]}"><span>{w["s"]}</span></li>'
        for w in FISICA["calendario"]
    )
    meses = [("Ago", 1), ("Sep", 3), ("Oct", 7), ("Nov", 12), ("Dic", 16)]
    etiquetas = "".join(f'<span style="grid-column:{c}">{n}</span>' for n, c in meses)
    proximas = lista_proximas(s)
    return f"""
<section class="grid" id="semana" aria-labelledby="t-semana">
  <div class="glass panel week span-8" data-reveal>
    <div class="week__head">
      <div>
        <p class="eyebrow">Calendario del ciclo {SITIO["ciclo"]}</p>
        <h2 id="t-semana">¿En qué semana vamos?</h2>
        <p class="week__now" data-week-text>{texto_semana(s)}</p>
      </div>
      <div class="gauge gauge--lg" style="--p:{pct:.3f}" data-gauge role="img" aria-label="Avance del ciclo: semana {s} de 18">
        <span class="gauge__fill"><i></i><i></i></span>
        <span class="gauge__txt"><b data-week-n>{s if 1 <= s <= 18 else "—"}</b><small>de 18</small></span>
      </div>
    </div>
    <dl class="week__nums">
      <div><dt>Semanas cursadas</dt><dd data-week-done>{max(0, min(s, 19) - 1)}</dd></div>
      <div><dt>Semanas restantes</dt><dd data-week-left>{max(0, 18 - s) if s >= 1 else 18}</dd></div>
      <div><dt>Avance del ciclo</dt><dd data-week-pct>{round(min(max(s, 0), 18) / 18 * 100)} %</dd></div>
    </dl>
    <div class="week__track">
      <ol class="week__bar" data-weekbar aria-label="Semanas del ciclo">{celdas}</ol>
      <div class="week__months" aria-hidden="true">{etiquetas}</div>
    </div>
  </div>
  <div class="glass panel upnext span-4" data-reveal>
    <p class="eyebrow">{icon("atom", "ic ic--xs")} Física · semana a semana</p>
    <h3 class="upnext__title">Esta semana y lo que sigue</h3>
    <ol class="upnext__list" data-upnext>{proximas}</ol>
  </div>
</section>"""


def lista_proximas(s):
    cal = FISICA["calendario"]
    inicio = max(1, min(s, 16)) if s >= 1 else 1
    out = []
    for w in cal[inicio - 1:inicio + 2]:
        etiqueta = "Esta semana" if w["s"] == s else f"Semana {w['s']}"
        pts = puntos_texto(w)
        out.append(
            f'<li class="{"is-now" if w["s"] == s else ""}"><span class="upnext__k">{etiqueta} · {esc(w["fechas"])}</span>'
            f'<b>{esc(" · ".join(w["temas"]))}</b>{f"<small>{esc(pts)}</small>" if pts else ""}</li>'
        )
    return "".join(out)


def seccion_proyecto(embed):
    datos = [
        ("Escuela", SITIO["escuela"]),
        ("Carrera", SITIO["carrera"]),
        ("Grupo y turno", f'{SITIO["grupo"]} · {SITIO["turno"]}'),
        ("Clave del grupo", SITIO["clave"]),
        ("Ciclo escolar", SITIO["ciclo"]),
    ]
    dl = "".join(f"<div><dt>{a}</dt><dd>{esc(b)}</dd></div>" for a, b in datos)
    media = "" if embed else f"""
  <figure class="glass media span-5" data-reveal>
    <img src="assets/img/fotos/proyecto.jpg" alt="Estudiantes trabajando en equipo con sus laptops" loading="lazy" decoding="async">
    <figcaption class="media__cap glass-pill">{icon("award", "ic ic--sm")} Proyecto integrador · {SITIO["ciclo"]}</figcaption>
  </figure>"""
    return f"""
<section class="grid" id="proyecto" aria-labelledby="t-proyecto">{media}
  <div class="glass panel about {"span-12" if embed else "span-7"}" data-reveal>
    <p class="eyebrow">Sobre el proyecto</p>
    <h2 id="t-proyecto">Un sitio hecho por y para el {SITIO["grupo"]}</h2>
    <p class="about__p">Este sitio es nuestro proyecto integrador. Organiza el temario de cada materia del primer semestre para consultarlo rápido, repasar antes de un examen y saber qué tema viene después.</p>
    <dl class="facts">{dl}</dl>
  </div>
</section>"""


def tarjetas_equipo_estaticas():
    """Tarjetas de respaldo; main.js las reemplaza con los datos de equipo.js."""
    out = []
    for i, nombre in enumerate(NOMBRES_EQUIPO, 1):
        n = nombre.strip()
        out.append(f"""
<article class="tcard glass acc" style="--acc:{COLORES_EQUIPO[(i - 1) % len(COLORES_EQUIPO)]}" tabindex="0">
  <div class="tcard__front">
    <span class="tcard__orb">{esc(iniciales(n)) if n else icon("user")}</span>
    <span class="tcard__num">Integrante {i:02d}</span>
    <h3 class="tcard__name{"" if n else " is-empty"}">{esc(n or "Nombre del integrante")}</h3>
    <p class="tcard__rol is-empty">Rol en el equipo</p>
  </div>
</article>""")
    return "".join(out)


def seccion_equipo(pagina=False):
    cab = "" if pagina else f"""
  <header class="block__head">
    <div><p class="eyebrow">Equipo · {SITIO["grupo"]} {SITIO["turno"]}</p>
    <h2 id="t-equipo">Quienes hicimos este sitio</h2>
    <p class="lead">Pasa el cursor o toca una tarjeta para ver los datos de cada integrante.</p></div>
    <a class="btn btn--glass" href="equipo.html" data-ripple>Página del equipo {icon("arrow-right")}</a>
  </header>"""
    return f"""
<section class="block" id="equipo"{"" if pagina else ' aria-labelledby="t-equipo"'}>{cab}
  <div class="team" data-equipo style="--n-row:{por_fila(N_EQUIPO)}">{tarjetas_equipo_estaticas()}</div>
</section>"""


# ---------------------------------------------------------------- páginas de materia
CHECK = '<svg class="chk__ic" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 12.6l4.3 4.3L19 7.2" pathLength="1"/></svg>'


def arbol(temas, nivel=0):
    """Árbol de temas. Cada tema y subtema tiene un botón para marcarlo como repasado."""
    items = []
    for t in temas:
        sub = t["sub"]
        chips = bool(sub) and all(not s["c"] and not s["sub"] for s in sub)
        marca = f'<span class="code">{esc(t["c"])}</span>' if t["c"] else '<span class="bullet" aria-hidden="true"></span>'
        texto = f'{t["c"]} {t["t"]}'.strip()
        boton = (f'<button class="chk" type="button" data-tema="{t["id"]}" aria-pressed="false" '
                 f'aria-label="Marcar como repasado: {esc(texto)}">{CHECK}</button>')
        dentro = f'<div class="node" id="{t["id"]}">{boton}{marca}<span class="node__t">{esc(t["t"])}</span></div>'
        if chips:
            dentro += '<ul class="tags">' + "".join(
                f'<li id="{s["id"]}"><button class="tag" type="button" data-tema="{s["id"]}" aria-pressed="false" '
                f'title="Marcar como repasado">{CHECK}<span>{esc(s["t"])}</span></button></li>'
                for s in sub) + "</ul>"
        elif sub:
            dentro += arbol(sub, nivel + 1)
        items.append(f"<li>{dentro}</li>")
    return f'<ol class="tree tree--l{nivel}">' + "".join(items) + "</ol>"


def cabecera_seccion(etiqueta, titulo, icono):
    return f"""<header class="unit__head">
      <span class="orb orb--lg">{icon(icono)}</span>
      <div><p class="unit__label">{esc(etiqueta)}</p><h2 class="unit__title">{esc(titulo)}</h2></div>
      <span class="unit__prog" data-unit-prog hidden></span>
    </header>"""


def panel(id_, contenido, ancho=False):
    return (f'<section class="glass panel unit{" unit--wide" if ancho else ""}" id="{id_}" data-panel '
            f'role="tabpanel" aria-labelledby="tab-{id_}" tabindex="-1">\n{contenido}\n</section>')


def seccion_unidad(m, i, s):
    partes = [cabecera_seccion(f"{tipo_seccion(m)} {i}", s["titulo"], s["icono"])]
    if s.get("objetivo"):
        partes.append(f'<div class="objective"><p class="objective__k">{icon("target", "ic ic--sm")} Objetivo</p><p>{esc(s["objetivo"])}</p></div>')
    if s.get("descripcion"):
        partes.append(f'<p class="unit__desc">{esc(s["descripcion"])}</p>')
    partes.append(arbol(s["temas"]))
    if s.get("insignia"):
        partes.append(f'<p class="badge">{icon("flag", "ic ic--sm")} {esc(s["insignia"])}</p>')
    if s.get("nota"):
        partes.append(f'<aside class="note">{icon("info")}<p><b>Nota.</b> {esc(s["nota"])}</p></aside>')
    return panel(f"u{i}", "\n".join(partes))


def seccion_presentacion(m):
    tarjetas = "".join(
        f"""<article class="indic__card">
          <div class="indic__top"><span class="orb orb--sm">{icon(g["icono"])}</span><h3>{esc(g["titulo"])}</h3></div>
          <ul class="tags tags--flat">{"".join(f"<li>{esc(x)}</li>" for x in g["items"])}</ul>
        </article>"""
        for g in m["indicadores"]
    )
    return panel("presentacion", f"""{cabecera_seccion("Presentación", "Propósito e indicadores de logro", "target")}
    <blockquote class="purpose"><p>{esc(m["proposito"])}</p></blockquote>
    <p class="sub-h">Indicadores de logro · rasgos esenciales del programa</p>
    <div class="indic">{tarjetas}</div>""")


def seccion_linea_tiempo(m):
    hitos = "".join(f'<li><b>{esc(h["anio"])}</b><span>{esc(h["texto"])}</span></li>' for h in m["linea_tiempo"])
    return panel("linea", f"""{cabecera_seccion("Línea del tiempo", "Momentos clave de la UDG", "hourglass")}
    <ol class="tline">{hitos}</ol>
    <p class="fine">Fechas tomadas de los temas de la unidad 1.</p>""")


PSEINT_TOKEN = re.compile(
    r'(?P<s>"[^"]*")'
    r"|\b(?P<k>Algoritmo|FinAlgoritmo|Definir|Como|Real|Entero|Escribir|Leer|Si|Entonces|SiNo|FinSi|Mientras|FinMientras|Para|FinPara)\b"
    r"|(?P<o><-|>=|<=|\+|/|\*)"
    r"|\b(?P<n>\d+)\b"
)


def resaltar_pseint(codigo):
    """Resalta el pseudocódigo en una sola pasada (cada fragmento se escapa una vez)."""
    lineas = []
    for ln in codigo.split("\n"):
        out, pos = [], 0
        for m in PSEINT_TOKEN.finditer(ln):
            out.append(esc(ln[pos:m.start()]))
            out.append(f'<span class="{m.lastgroup}">{esc(m.group())}</span>')
            pos = m.end()
        out.append(esc(ln[pos:]))
        lineas.append(f'<span class="ln">{"".join(out)}</span>')
    return "".join(lineas)  # cada .ln es un bloque: sin saltos extra entre líneas


def seccion_ejemplo():
    return panel("ejemplo", f"""{cabecera_seccion("Ejemplo", "Así se ve un algoritmo en PSeInt", "terminal")}
    <div class="codeblock">
      <div class="code__bar"><span>{icon("file-text", "ic ic--sm")} promedio.psc</span><button class="code__copy" type="button" data-copy data-ripple>{icon("clipboard-list", "ic ic--sm")}<span>Copiar</span></button></div>
      <pre><code data-code>{resaltar_pseint(EJEMPLO_PSEINT)}</code></pre>
    </div>
    <p class="fine">Ejemplo ilustrativo: lee tres calificaciones, calcula el promedio y decide si se aprueba con 60 o más. Usa estructura secuencial y selectiva.</p>""")


def seccion_calendario(m):
    s_hoy = SEMANA
    filas = []
    for w in m["calendario"]:
        suma = sum(x[1] for x in w["p"])
        pts = "".join(
            f'<li class="pt" style="--c:var(--{EVAL_SLOT[x[0]]})"><i></i>{esc(x[2] if len(x) > 2 else EVAL_NOMBRE[x[0]])} <b>{fmt(x[1])}</b></li>'
            for x in w["p"]
        )
        estado = "is-past" if w["s"] < s_hoy else ("is-now" if w["s"] == s_hoy else "")
        unidad = f"Unidad {w['u']}" if w["u"] else "Cierre del ciclo"
        temas = "".join(f"<span>{esc(t)}</span>" for t in w["temas"])
        filas.append(f"""<li class="cal__w {estado}" data-u="{w['u']}">
        <div class="cal__n"><small>Sem</small><b>{w['s']:02d}</b></div>
        <div class="cal__main"><p class="cal__d">{esc(w['fechas'])} · {unidad}<em class="cal__now">Esta semana</em></p><p class="cal__t">{temas}</p>
          {f'<ul class="cal__pts">{pts}</ul>' if pts else ''}</div>
        <div class="cal__sum">{f'<b>{fmt(suma)}</b><small>pts</small>' if suma else '<small>—</small>'}</div>
      </li>""")
    chips = '<button class="seg__btn is-active" type="button" data-cal-filter="0" aria-pressed="true" data-li>Todas</button>' + "".join(
        f'<button class="seg__btn" type="button" data-cal-filter="{u}" aria-pressed="false" data-li>Unidad {u}</button>' for u in range(1, 5)
    )
    return panel("calendario", f"""{cabecera_seccion("Semana a semana", "Calendario de temas y puntos", "calendar-days")}
    <div class="seg seg--sm glass-pill" role="group" aria-label="Filtrar semanas por unidad" data-lens="h"><span class="lens" aria-hidden="true"></span>{chips}</div>
    <ol class="cal" data-cal>{"".join(filas)}</ol>""", ancho=True)


def seccion_evaluacion(m):
    totales = {k: 0.0 for k, _, _ in EVAL}
    por_unidad = {u: 0.0 for u in range(1, 5)}
    semanas_u = {u: 0 for u in range(1, 5)}
    for w in m["calendario"]:
        if w["u"]:
            semanas_u[w["u"]] += 1
        for x in w["p"]:
            totales[x[0]] += x[1]
            por_unidad[w["u"]] += x[1]
    total = sum(totales.values())
    partes, leyenda = [], []
    for k, nombre, slot in EVAL:
        v = totales[k]
        pct = v / total * 100
        partes.append(
            f'<div class="seg-bar__part" style="flex:{v};--c:var(--{slot})" tabindex="0" data-k="{k}" '
            f'aria-label="{nombre}: {fmt(v)} puntos, {pct:.0f} %" data-tip="{nombre} · {fmt(v)} pts · {pct:.0f} %"><span>{v:g}</span></div>'
        )
        leyenda.append(f'<li data-k="{k}"><i style="--c:var(--{slot})"></i>{nombre}<span>{pct:.0f} %</span></li>')
    tiles = "".join(
        f"""<div class="utile"><p class="utile__k">Unidad {u}</p><p class="utile__v">{fmt(por_unidad[u])}<small> pts</small></p><p class="utile__s">{semanas_u[u]} semanas · {esc(m["secciones"][u - 1]["titulo"])}</p></div>"""
        for u in range(1, 5)
    )
    filas = "".join(f"<tr><th scope='row'>{n}</th><td>{fmt(totales[k])}</td><td>{totales[k] / total * 100:.1f} %</td></tr>" for k, n, _ in EVAL)
    return panel("evaluacion", f"""{cabecera_seccion("Evaluación", "Distribución de los puntos", "gauge")}
    <div class="seg-bar" role="group" aria-label="Distribución de {fmt(total)} puntos programados por tipo de evaluación">{"".join(partes)}</div>
    <ul class="legend">{"".join(leyenda)}</ul>
    <div class="utiles">{tiles}</div>
    <details class="table-view"><summary>Ver como tabla</summary>
      <table><thead><tr><th scope="col">Tipo</th><th scope="col">Puntos</th><th scope="col">Porcentaje</th></tr></thead>
      <tbody>{filas}</tbody><tfoot><tr><th scope="row">Total</th><td>{fmt(total)}</td><td>100 %</td></tr></tfoot></table>
    </details>
    <p class="fine">Puntos según el desglose semanal del programa. La suma de lo programado es {fmt(total)} puntos.</p>""", ancho=True)


def secciones_materia(m):
    """Lista de (id, etiqueta de la pestaña, título completo, html)."""
    out = []
    if m.get("indicadores"):
        out.append(("presentacion", "Presentación", "Propósito e indicadores de logro", seccion_presentacion(m)))
    if m.get("linea_tiempo"):
        out.append(("linea", "Línea del tiempo", "Momentos clave de la UDG", seccion_linea_tiempo(m)))
    corto = "Unidad" if m["tipo_seccion"] == "Unidad" else "Eje"
    for i, s in enumerate(m["secciones"], 1):
        out.append((f"u{i}", f"{corto} {i}", s["titulo"], seccion_unidad(m, i, s)))
    if m["slug"] == "programacion":
        out.append(("ejemplo", "Ejemplo", "Así se ve un algoritmo en PSeInt", seccion_ejemplo()))
    if m.get("calendario"):
        out.append(("calendario", "Calendario", "Calendario de temas y puntos", seccion_calendario(m)))
        out.append(("evaluacion", "Evaluación", "Distribución de los puntos", seccion_evaluacion(m)))
    return out


def cabecera_materia(m, embed):
    n, t = len(m["secciones"]), total_temas(m)
    docente = f'<li>{icon("user", "ic ic--sm")}<span>{esc(m["docente"])}</span></li>' if m["docente"] else ""
    titulo = (f'<p class="mhero__name">{esc(m["nombre"])}</p>' if embed
              else f'<h1 class="mhero__title">{esc(m["nombre"])}</h1>')
    return f"""
<section class="grid mhead acc" style="--acc:{m['color']}">
  <div class="glass panel mhero span-8" data-reveal>
    <p class="chip-area"><span class="orb orb--xs">{icon(m["icono"])}</span>{esc(AREAS[m['area']])}</p>
    {titulo}
    <p class="mhero__lead">{esc(m['intro'])}</p>
    <ul class="facts-pills">
      <li>{icon("layers", "ic ic--sm")}<span><b>{n}</b> {etiqueta_secciones(m)}</span></li>
      <li>{icon("list-checks", "ic ic--sm")}<span><b>{t}</b> temas y subtemas</span></li>
      {docente}
      <li>{icon("calendar-days", "ic ic--sm")}<span>Ciclo <b>{SITIO['ciclo']}</b></span></li>
    </ul>
  </div>
  <div class="glass panel morb span-4" data-reveal data-jelly data-repaso="{m['slug']}" data-total="{t}">
    <div class="liquid-orb liquid-orb--gauge" style="--p:0" data-orb role="img" aria-label="Avance de repaso: 0 %">
      <span class="liquid-orb__core"></span>
      <span class="liquid-orb__fill"><i></i><i></i></span>
      <span class="liquid-orb__ic">{icon(m["icono"])}</span>
      <span class="liquid-orb__pct" data-repaso-pct>0 %</span>
    </div>
    <div class="morb__tx">
      <p class="morb__k">Mi repaso · {esc(m["corto"])}</p>
      <p class="morb__v"><b data-repaso-n>0</b> de {t} temas repasados</p>
      <p class="morb__hint" data-repaso-hint>Toca el círculo junto a cada tema para marcarlo. Se guarda en este navegador.</p>
      <button class="pill morb__reset" type="button" data-repaso-reset hidden>{icon("repeat", "ic ic--xs")}<span>Reiniciar repaso</span></button>
    </div>
  </div>
</section>"""


def pagina_materia(m, embed=False):
    secs = secciones_materia(m)
    tabs = "".join(
        f'<button class="seg__btn{" is-active" if k == 0 else ""}" type="button" role="tab" id="tab-{i}" '
        f'aria-controls="{i}" aria-selected="{"true" if k == 0 else "false"}" title="{esc(titulo)}" data-tab="{i}" data-li>{esc(etq)}</button>'
        for k, (i, etq, titulo, _) in enumerate(secs)
    )
    paneles = "\n".join(h for *_, h in secs)
    cuerpo = f"""{cabecera_materia(m, embed)}
<div class="tabsbar acc" style="--acc:{m['color']}">
  <div class="seg seg--tabs glass-pill" role="tablist" aria-label="Secciones de {esc(m['nombre'])}" data-lens="h" data-tabs>
    <span class="lens" aria-hidden="true"></span>{tabs}
  </div>
</div>
<div class="panels acc" style="--acc:{m['color']}" data-panels>
{paneles}
</div>"""
    if embed:
        return cuerpo
    idx = MATERIAS.index(m)
    ant, sig = MATERIAS[idx - 1], MATERIAS[(idx + 1) % len(MATERIAS)]
    return f"""{cuerpo}
<nav class="pn" aria-label="Otras materias">
  <a class="glass pn__a acc" style="--acc:{ant['color']}" href="{ant['slug']}.html" data-jelly><span class="pn__k">{icon("arrow-left", "ic ic--sm")} Materia anterior</span><b>{esc(ant['nombre'])}</b></a>
  <a class="glass pn__a pn__a--next acc" style="--acc:{sig['color']}" href="{sig['slug']}.html" data-jelly><span class="pn__k">Siguiente materia {icon("arrow-right", "ic ic--sm")}</span><b>{esc(sig['nombre'])}</b></a>
</nav>"""


def paleta(color):
    return [color, "#3b5bff", "#8b4ff0", "#ff9a3d"]


# ---------------------------------------------------------------- páginas completas
def pagina_inicio():
    contenido = f"""{hero_inicio(False)}
{tarjetas_estadisticas("", False)}
{seccion_materias(False)}
{seccion_semana()}
{seccion_proyecto(False)}
{seccion_equipo()}"""
    return app("", "inicio", migas("", ("Panel del semestre", None)), contenido, "inicio", PALETA_INICIO)


def pagina_equipo():
    contenido = f"""
<section class="grid mhead">
  <div class="glass panel mhero span-8" data-reveal>
    <p class="chip-area"><span class="orb orb--xs" style="--acc:#3b5bff">{icon("users")}</span>Equipo del proyecto</p>
    <h1 class="mhero__title">Nuestro equipo</h1>
    <p class="mhero__lead">{integrantes_texto()} del grupo {SITIO["grupo"]}, turno {SITIO["turno"].lower()}, del {SITIO["carrera"]}. Pasa el cursor o toca cada tarjeta para ver sus datos.</p>
    <ul class="facts-pills">
      <li>{icon("users", "ic ic--sm")}<span><b>{N_EQUIPO}</b> integrantes</span></li>
      <li>{icon("hash", "ic ic--sm")}<span>Grupo <b>{SITIO["clave"]}</b></span></li>
      <li>{icon("calendar-days", "ic ic--sm")}<span>Ciclo <b>{SITIO["ciclo"]}</b></span></li>
    </ul>
  </div>
  <div class="glass panel morb span-4" data-reveal data-jelly style="--acc:#3b5bff">
    <div class="liquid-orb" aria-hidden="true"><span class="liquid-orb__core"></span><span class="liquid-orb__ic">{icon("users")}</span></div>
    <p class="morb__k">{SITIO["clave"]}</p>
    <div class="morb__avs">{avatares()}</div>
  </div>
</section>
{seccion_equipo(pagina=True)}
{seccion_proyecto(False).replace('id="proyecto"', 'id="grupo"')}"""
    return app("", "equipo", migas("", ("Equipo", None)), contenido, "equipo", ["#3b5bff", "#8b4ff0", "#17a88a", "#ff9a3d"])


def pagina_materia_completa(m):
    rutas = migas("../", ("Materias", "../index.html#materias"), (m["corto"], None))
    return app("../", m["slug"], rutas, pagina_materia(m), m["slug"], paleta(m["color"]))


# ---------------------------------------------------------------- bloques para Google Sites
def compactar_css(css):
    """Quita comentarios y espacios sobrantes para que cada bloque pese menos."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def bloque_embed(titulo, cuerpo, colores, css, js_equipo, js_main, js_datos):
    return f"""<!doctype html>
<!--
  {titulo}
  Bloque para Google Sites: Insertar > Incorporar > pestaña "Insertar código".
  Pega TODO este archivo, presiona Siguiente > Insertar y ajusta la altura del cuadro.
  Generado con src/build.py — Mapa del Semestre {SITIO["grupo"]} ({SITIO["clave"]}).
-->
<html lang="es" class="embed">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
{FUENTES}
<style>
{css}
</style>
</head>
<body>
{SVG_DEFS}
{fondo(None, colores)}
<div class="embed-wrap">
{cuerpo}
</div>
<script>
{js_equipo}
</script>
<script>
{js_datos}
</script>
<script>
{js_main}
</script>
</body>
</html>
"""


def generar_embeds():
    css = compactar_css((RAIZ / "assets/css/estilos.css").read_text(encoding="utf-8"))
    js_main = (RAIZ / "assets/js/main.js").read_text(encoding="utf-8")
    js_equipo = (RAIZ / "assets/js/equipo.js").read_text(encoding="utf-8")
    js_datos = "window.SEMANAS = " + json.dumps(datos_semanas(), ensure_ascii=False) + ";"
    bloques = {
        "inicio/1-portada.html": ("Inicio · Portada", f"{hero_inicio(True)}\n{tarjetas_estadisticas('', True)}", PALETA_INICIO),
        "inicio/2-materias.html": ("Inicio · Materias", seccion_materias(True), PALETA_INICIO),
        "inicio/3-semana.html": ("Inicio · ¿En qué semana vamos?", seccion_semana(), PALETA_INICIO),
        "inicio/4-proyecto.html": ("Inicio · Sobre el proyecto", seccion_proyecto(True), PALETA_INICIO),
        "equipo/equipo.html": ("Equipo", seccion_equipo(pagina=True), ["#3b5bff", "#8b4ff0", "#17a88a", "#ff9a3d"]),
    }
    for i, m in enumerate(MATERIAS, 1):
        bloques[f"materias/{i:02d}-{m['slug']}.html"] = (m["nombre"], pagina_materia(m, embed=True), paleta(m["color"]))
    for ruta, (titulo, cuerpo, colores) in bloques.items():
        destino = CODIGOS / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(bloque_embed(titulo, cuerpo, colores, css, js_equipo, js_main, js_datos), encoding="utf-8")
    return bloques


# ---------------------------------------------------------------- principal
def escribir(ruta, texto):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


def construir():
    titulo = SITIO["titulo"]
    desc = f'Temario de las {len(MATERIAS)} materias del primer semestre del grupo {SITIO["grupo"]} ({SITIO["clave"]}), {SITIO["carrera"]}, {SITIO["escuela"]}.'
    datos = (
        "/* Generado por src/build.py: calendario del ciclo e índice del buscador. */\n"
        f"window.SEMANAS = {json.dumps(datos_semanas(), ensure_ascii=False)};\n"
        f"window.TOTALES = {json.dumps({m['slug']: total_temas(m) for m in MATERIAS})};\n"
        f"window.INDICE = {json.dumps(indice_busqueda(), ensure_ascii=False)};\n"
    )
    escribir(RAIZ / "assets/js/datos.js", datos)
    escribir(RAIZ / "index.html", documento(titulo, desc, pagina_inicio(), "", "home"))
    escribir(RAIZ / "equipo.html", documento(f"Equipo · {titulo}", "Integrantes del equipo del proyecto integrador.", pagina_equipo(), "", "team-page"))
    for m in MATERIAS:
        escribir(
            RAIZ / "materias" / f"{m['slug']}.html",
            documento(f"{m['nombre']} · {titulo}", m["resumen"], pagina_materia_completa(m), "../", f"materia materia--{m['slug']}"),
        )


def main():
    construir()
    bloques = generar_embeds()
    print(f"Sitio generado: {len(MATERIAS) + 2} páginas · {TOTAL_TEMAS} temas · {len(bloques)} bloques para Google Sites")


if __name__ == "__main__":
    main()
