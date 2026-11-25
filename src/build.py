"""Generador del sitio "Mapa del Semestre 1A" (liquid glass fluid).

Uso:
    python3 src/build.py

Genera todo lo que se publica en el dominio:
    index.html, calendario.html, equipo.html, materias/*.html, 404.html, offline.html
    assets/js/datos.js              calendario, evaluaciones, totales e índice del buscador
    assets/calendario-2026b.ics     calendario para importar en Google Calendar / Outlook
    manifest.webmanifest, sw.js     app instalable que funciona sin conexión
    robots.txt, sitemap.xml, CNAME  buscadores y dominio (sitemap y CNAME si hay SITIO["url"])
    _headers, .nojekyll             encabezados y ajustes para Netlify, Cloudflare Pages y GitHub Pages
    src/og_paginas.json             datos para src/generar_imagenes.js (vistas previas al compartir)
"""
import hashlib
import html
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contenido import AREAS, EJEMPLO_PSEINT, MATERIAS, SITIO  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ICONOS = Path(__file__).resolve().parent / "iconos"
URL = SITIO.get("url", "").rstrip("/")

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
EVALUABLES = ("examen", "tarea", "integrador")

COLORES_EQUIPO = ["#E8962E", "#3B6FF5", "#E0517A", "#17A88A", "#D9473B", "#8B4FF0", "#2E9E57", "#1C97C9"]
PALETA_INICIO = ["#3b5bff", "#8b4ff0", "#ff9a3d", "#17a88a"]
PALETA_EQUIPO = ["#3b5bff", "#8b4ff0", "#17a88a", "#ff9a3d"]
PALETA_CAL = ["#ff9a3d", "#3b5bff", "#8b4ff0", "#17a88a"]


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


def version(ruta):
    """Huella corta del archivo: cambia cuando cambia el contenido (evita cachés viejas)."""
    return hashlib.md5((RAIZ / ruta).read_bytes()).hexdigest()[:8]


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
HOY = date.today()


def semana_actual(hoy=HOY):
    cal = FISICA["calendario"]
    if hoy < date.fromisoformat(cal[0]["ini"]):
        return 0
    for w in cal:
        if (hoy - date.fromisoformat(w["ini"])).days < 7:
            return w["s"]
    return 19


SEMANA = semana_actual()
CIERRE = date.fromisoformat(FISICA["calendario"][-1]["ini"]) + timedelta(days=4)


def puntos_texto(w):
    return " · ".join(f'{x[2] if len(x) > 2 else EVAL_NOMBRE[x[0]]} {fmt(x[1])}' for x in w["p"])


def evaluaciones():
    evs = []
    for w in FISICA["calendario"]:
        for x in w["p"]:
            if x[0] in EVALUABLES:
                evs.append({"s": w["s"], "ini": w["ini"], "f": w["fechas"], "n": x[2] if len(x) > 2 else EVAL_NOMBRE[x[0]], "k": x[0], "pts": x[1]})
    return evs


def proxima_evaluacion():
    for e in evaluaciones():
        if e["s"] >= SEMANA:
            return e
    return None


def datos_semanas():
    return [
        {"s": w["s"], "ini": w["ini"], "f": w["fechas"], "t": w["temas"], "p": puntos_texto(w), "u": w["u"],
         "ev": [x[2] if len(x) > 2 else EVAL_NOMBRE[x[0]] for x in w["p"] if x[0] in EVALUABLES]}
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
        items.append({"t": m["nombre"], "m": "Materia", "h": base, "c": m["color"], "k": "materia"})
        for i, s in enumerate(m["secciones"], 1):
            etiqueta = f"{m['corto']} · {tipo_seccion(m)} {i}"
            items.append({"t": s["titulo"], "m": etiqueta, "h": f"{base}#u{i}", "c": m["color"], "k": "unidad"})

            def recorrer(temas):
                for t in temas:
                    texto = f'{t["c"]} {t["t"]}'.strip()
                    items.append({"t": texto, "m": etiqueta, "h": f"{base}#{t['id']}", "c": m["color"], "k": "tema"})
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
#   #lg   -> refracción de borde para vidrio
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


def picture(nombre, p, cls="", alt="", sizes="100vw", carga="lazy", prioridad=False, tarjeta=False):
    """<picture> con WebP en varios anchos y JPG de respaldo."""
    base = f"{p}assets/img/fotos/{nombre}"
    if tarjeta:
        srcset, jpg = f"{base}-card-600.webp 600w, {base}-card-900.webp 900w", f"{base}-card.jpg"
    else:
        srcset, jpg = f"{base}-800.webp 800w, {base}-1280.webp 1280w, {base}-2000.webp 2000w", f"{base}.jpg"
    extra = ' fetchpriority="high"' if prioridad else ""
    clase = f' class="{cls}"' if cls else ""
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img{clase} src="{jpg}" alt="{esc(alt)}" loading="{carga}" decoding="async"{extra}></picture>')


def fondo(foto, colores, p=""):
    """Capa fija detrás del vidrio: foto + agua WebGL + tinte + grano."""
    img = picture(foto, p, "bg__photo", carga="eager", prioridad=True) if foto else ""
    clase = "bg bg--photo" if foto else "bg"
    respaldo = f' data-fondo="{p}assets/js/fondos/{foto}.js"' if foto and (RAIZ / f"assets/js/fondos/{foto}.js").exists() else ""
    return (
        f'<div class="{clase}" aria-hidden="true"{respaldo}>{img}'
        f'<canvas class="bg__liquid" data-liquid data-colors="{",".join(colores)}"></canvas>'
        '<div class="bg__blobs"><i></i><i></i><i></i></div>'
        '<div class="bg__tint"></div><div class="bg__grain"></div></div>'
    )


def avatares(p="", limite=6):
    caras = "".join(
        f'<span class="av" style="--c:{COLORES_EQUIPO[i % len(COLORES_EQUIPO)]}" title="{esc(n)}">{esc(iniciales(n) or "?")}</span>'
        for i, n in enumerate(NOMBRES_EQUIPO[:limite])
    )
    extra = f'<span class="av av--more">+{N_EQUIPO - limite}</span>' if N_EQUIPO > limite else ""
    return f'<span class="avs">{caras}{extra}</span>'


def interruptor(attr, ico, texto, presionado="false"):
    return (f'<button class="side__motion" type="button" {attr} aria-pressed="{presionado}">{icon(ico)}<span>{texto}</span>'
            '<i class="switch" aria-hidden="true"></i></button>')


def sidebar(p, activo):
    generales = [
        ("inicio", "Inicio", "house", f"{p}index.html"),
        ("calendario", "Calendario", "calendar-days", f"{p}calendario.html"),
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
    <a class="side__week" href="{p}calendario.html">
      <span class="gauge gauge--sm" style="--p:{pct:.3f}" data-gauge><span class="gauge__fill"><i></i><i></i></span><b data-week-n>{SEMANA if 1 <= SEMANA <= 18 else "—"}</b></span>
      <span class="side__weektx"><b>Semana <span data-week-n>{SEMANA if 1 <= SEMANA <= 18 else "—"}</span> de 18</b><small data-week-dates>{esc(w["fechas"])}</small></span>
    </a>
    <button class="side__install" type="button" data-install hidden>{icon("monitor-down")}<span>Instalar como app</span></button>
    <div class="side__toggles">
      {interruptor("data-calma", "droplets", "Efecto líquido")}
      {interruptor("data-sonido", "volume-2", "Sonidos de agua")}
    </div>
  </div>
</aside>
<div class="scrim" data-drawer-close hidden></div>"""


def temporizador():
    presets = [("25", "5", "25 · 5"), ("50", "10", "50 · 10"), ("15", "3", "15 · 3")]
    botones = "".join(
        f'<button class="seg__btn{" is-active" if i == 0 else ""}" type="button" data-li data-timer-preset="{a},{b}" aria-pressed="{"true" if i == 0 else "false"}">{t}</button>'
        for i, (a, b, t) in enumerate(presets)
    )
    return f"""
    <div class="timer-wrap">
      <button class="iconbtn glass-pill timer-btn" type="button" data-timer-open aria-expanded="false" aria-controls="temporizador" aria-label="Temporizador de estudio">{icon("timer")}<span class="timer-btn__t" data-timer-chip hidden></span></button>
      <div class="timer glass" id="temporizador" data-timer role="dialog" aria-label="Temporizador de estudio" hidden>
        <p class="eyebrow">{icon("brain-circuit", "ic ic--xs")} Sesión de estudio</p>
        <div class="gauge gauge--timer" data-timer-gauge style="--p:1" role="timer" aria-live="off">
          <span class="gauge__fill"><i></i><i></i></span>
          <span class="gauge__txt"><b data-timer-t>25:00</b><small data-timer-modo>Enfoque</small></span>
        </div>
        <div class="seg seg--sm glass-pill" role="group" aria-label="Minutos de enfoque y descanso" data-lens="h" data-timer-presets>
          <span class="lens" aria-hidden="true"></span>{botones}
        </div>
        <div class="timer__ctl">
          <button class="btn btn--liquid btn--sm" type="button" data-timer-toggle>{icon("play", "ic ic--sm ic--play")}{icon("pause", "ic ic--sm ic--pause")}<span>Iniciar</span></button>
          <button class="iconbtn glass-pill" type="button" data-timer-reset aria-label="Reiniciar temporizador">{icon("rotate-ccw")}</button>
          <button class="iconbtn glass-pill" type="button" data-timer-skip aria-label="Pasar al siguiente bloque">{icon("skip-forward")}</button>
        </div>
        <p class="timer__stats">Sesiones de enfoque hoy: <b data-timer-hoy>0</b></p>
        <p class="timer__hint">Mientras estudias, el agua del fondo se calma.</p>
      </div>
    </div>"""


def topbar(p, migas):
    return f"""
<header class="top">
  <button class="iconbtn glass-pill top__menu" type="button" data-drawer-open aria-label="Abrir menú" aria-controls="menu" aria-expanded="false">{icon("menu")}</button>
  <div class="top__crumbs">
    <nav class="crumbs" aria-label="Ruta de navegación">{migas}</nav>
    <p class="top__date" data-hoy></p>
  </div>
  <div class="top__tools">
    <button class="search glass-pill" type="button" data-pal-open aria-label="Buscar temas, materias o acciones (Ctrl + K)">{icon("search")}<span class="search__ph">Buscar temas o acciones…</span><kbd data-kbd>Ctrl K</kbd></button>
    {temporizador()}
    <a class="avatars glass-pill" href="{p}equipo.html" aria-label="Ver al equipo: {esc(", ".join(NOMBRES_EQUIPO))}">{avatares(p)}</a>
  </div>
</header>"""


PAL_ICONOS = ["house", "calendar-days", "crosshair", "users", "timer", "droplets", "volume-2", "download", "printer",
              "share-2", "notebook-pen", "monitor-down", "layers", "hash", "clock-3"]


def paleta_comandos():
    return f"""
<div class="pal" data-pal hidden>
  <div class="pal__scrim" data-pal-close></div>
  <div class="pal__box glass" role="dialog" aria-modal="true" aria-label="Buscar temas, materias y acciones">
    <label class="pal__in" for="pal-q">{icon("search")}<input id="pal-q" type="text" placeholder="Busca un tema, una materia o una acción…" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="true" aria-controls="pal-lista" aria-autocomplete="list"><kbd>Esc</kbd></label>
    <div class="pal__list" id="pal-lista" role="listbox" aria-label="Resultados"></div>
    <p class="pal__foot"><span><kbd>↑</kbd><kbd>↓</kbd> moverse</span><span><kbd>Enter</kbd> abrir</span><span><kbd>Esc</kbd> cerrar</span><span class="pal__count" data-pal-count aria-live="polite"></span></p>
  </div>
  <template id="pal-iconos">{"".join(f'<i data-i="{n}">{icon(n)}</i>' for n in PAL_ICONOS)}</template>
</div>
<div class="toasts" data-toasts aria-live="polite"></div>"""


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
  {a("calendario", "Calendario", "calendar-days", f"{p}calendario.html")}
  {a("equipo", "Equipo", "users", f"{p}equipo.html")}
</nav>"""


def footer(p):
    return f"""
<footer class="foot">
  <div class="foot__links">
    <a href="{p}index.html">Inicio</a><a href="{p}calendario.html">Calendario</a><a href="{p}equipo.html">Equipo</a>
    <a href="{p}assets/calendario-2026b.ics" download>Calendario .ics</a>
    <button type="button" class="foot__key" data-pal-open>{icon("command", "ic ic--xs")} Atajos: <kbd>Ctrl K</kbd> buscar · <kbd>/</kbd> buscar · <kbd>T</kbd> temporizador</button>
  </div>
  <p>{SITIO["escuela"]} · {SITIO["carrera"]} · Grupo {SITIO["grupo"]}, turno {SITIO["turno"].lower()} · Ciclo {SITIO["ciclo"]}</p>
  <p>Proyecto académico elaborado por estudiantes del grupo {SITIO["grupo"]}. No es un sitio oficial de la institución. Fotografías: Unsplash · Íconos: Lucide · Tipografía: Geist</p>
</footer>
<a class="totop iconbtn glass-pill" href="#top" aria-label="Volver arriba" data-totop><svg class="totop__ring" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="22" pathLength="100"/></svg>{icon("arrow-up")}</a>"""


def absoluta(ruta):
    return f"{URL}/{ruta}" if URL else ""


def documento(titulo, descripcion, cuerpo, p="", clase="", ruta="index.html", og="inicio", ld=None):
    canon = absoluta("" if ruta == "index.html" else ruta)
    og_img = f"assets/img/og/{og}.jpg"
    og_abs = absoluta(og_img) if URL else f"{p}{og_img}"
    meta_url = (f'\n<link rel="canonical" href="{canon}">\n<meta property="og:url" content="{canon}">' if URL else "")
    ld_txt = f'\n<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    css_v, js_v, datos_v, equipo_v = version("assets/css/estilos.css"), version("assets/js/main.js"), version("assets/js/datos.js"), version("assets/js/equipo.js")
    return f"""<!doctype html>
<html lang="es-MX" data-base="{p}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(descripcion)}">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#05070d">{meta_url}
<meta property="og:type" content="website">
<meta property="og:locale" content="es_MX">
<meta property="og:site_name" content="{esc(SITIO["titulo"])}">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descripcion)}">
<meta property="og:image" content="{og_abs}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{p}assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{p}assets/img/icons/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{p}assets/img/icons/apple-touch-icon.png">
<link rel="manifest" href="{p}manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Semestre 1A">
<link rel="preload" href="{p}assets/fonts/geist.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p}assets/css/estilos.css?v={css_v}">
<script>var d=document.documentElement;try{{if(localStorage.getItem("calma")==="1")d.classList.add("calma")}}catch(e){{}}addEventListener("pagereveal",function(e){{if(e.viewTransition)d.classList.add("vt")}});</script>{ld_txt}
</head>
<body class="{clase}" id="top">
{cuerpo}
<script src="{p}assets/js/equipo.js?v={equipo_v}"></script>
<script src="{p}assets/js/datos.js?v={datos_v}"></script>
<script src="{p}assets/js/main.js?v={js_v}" defer></script>
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
  {footer(p)}
</div>
{dock(p, activo)}
{paleta_comandos()}"""


# ---------------------------------------------------------------- portada
def terminal():
    nombres = [f'<a class="t-m" style="--acc:{m["color"]}" href="materias/{m["slug"]}.html">{m["slug"]}</a>' for m in MATERIAS]
    filas = "".join(f'<p class="tl tl--out">{"  ".join(nombres[a:b])}</p>' for a, b in ((0, 3), (3, 7), (7, 10)))
    prompt = '<span class="t-p">tsin1am@poli</span><span class="t-c">:~/1A$</span> '
    s = min(max(SEMANA, 0), 18)
    barra = f'<span class="t-bar">{"█" * s}<span class="t-dim">{"░" * (18 - s)}</span></span>  semana {s} de 18'
    return f"""
<div class="term glass span-5" role="region" aria-label="Terminal decorativa: lista de las diez materias y avance del semestre" data-reveal>
  <div class="term__bar"><i></i><i></i><i></i><span>tsin1am@politecnica — bash</span></div>
  <div class="term__body" data-term>
    <p class="tl tl--cmd">{prompt}<span class="t-typed">ls materias/</span></p>
    {filas}
    <p class="tl tl--cmd">{prompt}<span class="t-typed">grep -c "tema" temario.txt</span></p>
    <p class="tl tl--out"><span class="t-n">{TOTAL_TEMAS}</span></p>
    <p class="tl tl--cmd">{prompt}<span class="t-typed">./semestre --progreso</span></p>
    <p class="tl tl--out" data-term-progress>{barra}</p>
    <p class="tl tl--cmd tl--last">{prompt}<span class="t-cursor" aria-hidden="true"></span></p>
  </div>
</div>"""


def hero_inicio():
    return f"""
<section class="grid hero" aria-labelledby="titulo">
  <div class="glass panel hero__panel span-7" data-reveal>
    <p class="eyebrow"><span class="pulse"></span>{SITIO["escuela"]}</p>
    <h1 class="hero__title" id="titulo">El mapa de nuestro <span class="liquid-text">primer semestre</span></h1>
    <p class="hero__lead">Proyecto integrador del grupo {SITIO["grupo"]}, turno {SITIO["turno"].lower()}, del {SITIO["carrera"]}. Las diez materias del ciclo {SITIO["ciclo"]} con sus unidades y temas, tu avance de repaso y el calendario, en un solo lugar.</p>
    <div class="hero__cta">
      <a class="btn btn--liquid" href="#materias" data-ripple>Explorar materias {icon("arrow-right")}</a>
      <a class="btn btn--glass" href="calendario.html" data-ripple>{icon("calendar-days", "ic ic--sm")} Ver calendario</a>
    </div>
  </div>
  {terminal()}
</section>"""


def tarjetas_estadisticas():
    conteo = {k: sum(1 for m in MATERIAS if m["area"] == k) for k in AREAS}
    cortos = {"tecnologia": "Tecnología", "ciencias": "Ciencias", "comunicacion": "Lenguaje", "integral": "Integral"}
    areas = "".join(f'<li title="{esc(v)}"><i style="--c:{c}"></i>{cortos[k]} <b>{conteo[k]}</b></li>' for (k, v), c in zip(AREAS.items(), ["#3b6ff5", "#8b4ff0", "#d9473b", "#e8962e"]))
    barras = "".join(
        f'<a class="bar" href="materias/{m["slug"]}.html" style="--h:{total_temas(m) / MAX_TEMAS:.3f}" data-tip="{esc(m["corto"])} · {total_temas(m)} temas" aria-label="{esc(m["nombre"])}: {total_temas(m)} temas"></a>'
        for m in MATERIAS
    )
    s = SEMANA
    ticks = "".join(f'<span class="tick{" is-past" if i < s else (" is-now" if i == s else "")}"></span>' for i in range(1, 19))
    return f"""
<section class="grid stats" aria-label="Resumen del semestre">
  <article class="glass stat span-3" data-reveal data-jelly>
    <p class="stat__k">Materias</p>
    <p class="stat__v"><span data-count="{len(MATERIAS)}">{len(MATERIAS)}</span><small>en 4 áreas</small></p>
    <ul class="stat__areas">{areas}</ul>
  </article>
  <article class="glass stat span-3" data-reveal data-jelly>
    <p class="stat__k">Temas y subtemas</p>
    <p class="stat__v"><span data-count="{TOTAL_TEMAS}">{TOTAL_TEMAS}</span><small data-repaso-global>por repasar</small></p>
    <div class="bars" role="group" aria-label="Temas por materia">{barras}</div>
  </article>
  <a class="glass stat span-3" href="calendario.html" data-reveal data-jelly aria-label="Semana {s} de 18: ver calendario">
    <p class="stat__k">Semana del ciclo</p>
    <p class="stat__v"><span data-week-n>{s if 1 <= s <= 18 else "—"}</span><small>de 18</small></p>
    <div class="ticks" data-ticks aria-hidden="true">{ticks}</div>
  </a>
  <article class="glass stat span-3" data-reveal data-jelly>
    <p class="stat__k">Equipo</p>
    <p class="stat__v"><span data-count="{N_EQUIPO}">{N_EQUIPO}</span><small>integrantes</small></p>
    <div class="stat__team">{avatares()}<a class="pill pill--link" href="equipo.html" data-ripple>Ver equipo {icon("arrow-up-right", "ic ic--xs")}</a></div>
  </article>
</section>"""


def seccion_hoy():
    e = proxima_evaluacion()
    if e:
        dias = max(0, (date.fromisoformat(e["ini"]) - HOY).days)
        cuando = "Esta semana" if e["s"] == SEMANA else f"en {dias} días"
        tit, meta = e["n"], f'Física · Semana {e["s"]} · {e["f"]} · {fmt(e["pts"])} pts'
        num, unidad, p = ("0", "días", 1) if e["s"] == SEMANA else (str(dias), "días", max(0.05, 1 - dias / 35))
    else:
        tit, meta, cuando, num, unidad, p = "Sin evaluaciones pendientes", "El plan de Física ya terminó", "", "—", "", 1
    minis = "".join(
        f'<li><a class="mini acc" style="--acc:{m["color"]}" href="materias/{m["slug"]}.html" data-mini="{m["slug"]}" title="{esc(m["nombre"])}">'
        f'<span class="mini__orb" style="--p:0"><span class="mini__fill"><i></i></span>{icon(m["icono"])}</span>'
        f'<span class="mini__n">{esc(m["corto"])}</span><span class="mini__p" data-mini-p>0 %</span></a></li>'
        for m in MATERIAS
    )
    return f"""
<section class="grid hoy" aria-label="Tu día">
  <a class="glass panel nexteval span-4 acc" style="--acc:#8B4FF0" href="calendario.html" data-reveal data-jelly data-nexteval>
    <p class="eyebrow">{icon("bell", "ic ic--xs")} Próxima evaluación</p>
    <div class="nexteval__main">
      <div class="gauge gauge--md" style="--p:{p:.3f}" data-nexteval-gauge><span class="gauge__fill"><i></i><i></i></span><span class="gauge__txt"><b data-nexteval-d>{num}</b><small data-nexteval-u>{unidad}</small></span></div>
      <div class="nexteval__tx"><p class="nexteval__cuando" data-nexteval-c>{esc(cuando)}</p><h3 class="nexteval__t" data-nexteval-t>{esc(tit)}</h3><p class="nexteval__m" data-nexteval-m>{esc(meta)}</p></div>
    </div>
    <ul class="nexteval__more" data-nexteval-more aria-label="Evaluaciones siguientes"></ul>
    <span class="nexteval__go">Ver calendario {icon("arrow-right", "ic ic--sm")}</span>
  </a>
  <article class="glass panel repaso-home span-5" data-reveal>
    <div class="repaso-home__head">
      <div><p class="eyebrow">{icon("list-checks", "ic ic--xs")} Tu repaso</p><h3 class="repaso-home__t"><b data-repaso-total>0 %</b> del temario repasado</h3></div>
      <p class="repaso-home__sug" data-repaso-sug>Entra a una materia y marca los temas que ya repasaste.</p>
    </div>
    <ul class="minis">{minis}</ul>
  </article>
  <article class="glass panel enfoque span-3" data-reveal data-jelly>
    <p class="eyebrow">{icon("timer", "ic ic--xs")} Sesión de estudio</p>
    <h3 class="enfoque__t">Concéntrate 25 minutos</h3>
    <p class="enfoque__p">Al terminar te avisamos para descansar 5. Mientras estudias, el agua se calma.</p>
    <button class="btn btn--liquid btn--sm" type="button" data-timer-start>{icon("play", "ic ic--sm")}<span>Empezar</span></button>
    <p class="enfoque__s">Hoy llevas <b data-timer-hoy>0</b> sesiones</p>
  </article>
</section>"""


ANCHAS = {"tutoria", "fisica"}


def tarjeta_materia(m):
    n, t = len(m["secciones"]), total_temas(m)
    meta = f'{n} {etiqueta_secciones(m)} · {t} temas'
    ancha = " mcard--wide" if m["slug"] in ANCHAS else ""
    unidades = '<ol class="mcard__list">' + "".join(f"<li>{esc(s['titulo'])}</li>" for s in m["secciones"]) + "</ol>"
    return f"""
<a class="mcard glass acc{ancha}" style="--acc:{m['color']};view-transition-name:m-{m['slug']}" href="materias/{m['slug']}.html" data-area="{m['area']}" data-reveal data-jelly>
  {picture(m["slug"], "", "mcard__photo", tarjeta=True, sizes="(min-width: 1180px) 30vw, 90vw")}
  <div class="mcard__top"><span class="orb">{icon(m["icono"])}</span><span class="mcard__area">{esc(AREAS[m["area"]])}</span><span class="mcard__go">{icon("arrow-up-right")}</span></div>
  <h3 class="mcard__title">{esc(m["nombre"])}</h3>
  <p class="mcard__sum">{esc(m["resumen"])}</p>{unidades}
  <div class="mprog" data-prog-card="{m["slug"]}" data-total="{t}" hidden><span class="mprog__bar"><i></i></span><small></small></div>
  <p class="mcard__foot">{meta}</p>
</a>"""


def seccion_materias():
    conteo = {k: sum(1 for m in MATERIAS if m["area"] == k) for k in AREAS}
    filtros = (
        f'<button class="seg__btn is-active" type="button" data-filter="todas" aria-pressed="true" data-li>Todas <small>{len(MATERIAS)}</small></button>'
        + "".join(
            f'<button class="seg__btn" type="button" data-filter="{k}" aria-pressed="false" data-li>{esc(v)} <small>{conteo[k]}</small></button>'
            for k, v in AREAS.items()
        )
    )
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
  <div class="mgrid" data-mgrid>{"".join(tarjeta_materia(m) for m in MATERIAS)}</div>
</section>"""


def pista_semanas():
    s = SEMANA
    celdas = "".join(
        f'<li class="{"is-past" if w["s"] < s else ("is-now" if w["s"] == s else "")}{" has-ev" if any(x[0] in EVALUABLES for x in w["p"]) else ""}" '
        f'title="Semana {w["s"]} · {w["fechas"]}"><a href="calendario.html#sem-{w["s"]}" aria-label="Semana {w["s"]}, {w["fechas"]}">{w["s"]}</a></li>'
        for w in FISICA["calendario"]
    )
    meses = [("Ago", 1), ("Sep", 3), ("Oct", 7), ("Nov", 12), ("Dic", 16)]
    etiquetas = "".join(f'<span style="grid-column:{c}">{n}</span>' for n, c in meses)
    return f"""<div class="week__track">
      <ol class="week__bar" data-weekbar aria-label="Semanas del ciclo">{celdas}</ol>
      <div class="week__months" aria-hidden="true">{etiquetas}</div>
    </div>"""


def numeros_semana():
    s = SEMANA
    return f"""<dl class="week__nums">
      <div><dt>Semanas cursadas</dt><dd data-week-done>{max(0, min(s, 19) - 1)}</dd></div>
      <div><dt>Semanas restantes</dt><dd data-week-left>{max(0, 18 - s) if s >= 1 else 18}</dd></div>
      <div><dt>Avance del ciclo</dt><dd data-week-pct>{round(min(max(s, 0), 18) / 18 * 100)} %</dd></div>
    </dl>"""


def gauge_semana(cls="gauge--lg"):
    s = SEMANA
    pct = min(max(s, 0), 18) / 18
    return f"""<div class="gauge {cls}" style="--p:{pct:.3f}" data-gauge role="img" aria-label="Avance del ciclo: semana {s} de 18">
        <span class="gauge__fill"><i></i><i></i></span>
        <span class="gauge__txt"><b data-week-n>{s if 1 <= s <= 18 else "—"}</b><small>de 18</small></span>
      </div>"""


def seccion_semana():
    s = SEMANA
    return f"""
<section class="grid" id="semana" aria-labelledby="t-semana">
  <div class="glass panel week span-8" data-reveal>
    <div class="week__head">
      <div>
        <p class="eyebrow">Calendario del ciclo {SITIO["ciclo"]}</p>
        <h2 id="t-semana">¿En qué semana vamos?</h2>
        <p class="week__now" data-week-text>{texto_semana(s)}</p>
        <a class="pill week__link" href="calendario.html" data-ripple>{icon("calendar-days", "ic ic--xs")} Abrir el calendario completo</a>
      </div>
      {gauge_semana()}
    </div>
    {numeros_semana()}
    {pista_semanas()}
  </div>
  <div class="glass panel upnext span-4" data-reveal>
    <p class="eyebrow">{icon("atom", "ic ic--xs")} Física · semana a semana</p>
    <h3 class="upnext__title">Esta semana y lo que sigue</h3>
    <ol class="upnext__list" data-upnext>{lista_proximas(s)}</ol>
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


def seccion_proyecto(id_="proyecto"):
    datos = [
        ("Escuela", SITIO["escuela"]),
        ("Carrera", SITIO["carrera"]),
        ("Grupo y turno", f'{SITIO["grupo"]} · {SITIO["turno"]}'),
        ("Clave del grupo", SITIO["clave"]),
        ("Ciclo escolar", SITIO["ciclo"]),
    ]
    dl = "".join(f"<div><dt>{a}</dt><dd>{esc(b)}</dd></div>" for a, b in datos)
    return f"""
<section class="grid" id="{id_}" aria-labelledby="t-{id_}">
  <figure class="glass media span-5" data-reveal>
    {picture("proyecto", "", "", "Estudiantes trabajando en equipo con sus laptops", sizes="(min-width: 1100px) 40vw, 92vw")}
    <figcaption class="media__cap glass-pill">{icon("award", "ic ic--sm")} Proyecto integrador · {SITIO["ciclo"]}</figcaption>
  </figure>
  <div class="glass panel about span-7" data-reveal>
    <p class="eyebrow">Sobre el proyecto</p>
    <h2 id="t-{id_}">Un sitio hecho por y para el {SITIO["grupo"]}</h2>
    <p class="about__p">Este sitio es nuestro proyecto integrador. Organiza el temario de cada materia del primer semestre para consultarlo rápido, marcar lo que ya repasaste, tomar notas, estudiar con temporizador y saber qué tema viene después. También se puede instalar como app y funciona sin conexión.</p>
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


def cabecera_seccion(etiqueta, titulo, icono, prog=True):
    return f"""<header class="unit__head">
      <span class="orb orb--lg">{icon(icono)}</span>
      <div><p class="unit__label">{esc(etiqueta)}</p><h2 class="unit__title">{esc(titulo)}</h2></div>
      {'<span class="unit__prog" data-unit-prog hidden></span>' if prog else ""}
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
    return panel("presentacion", f"""{cabecera_seccion("Presentación", "Propósito e indicadores de logro", "target", prog=False)}
    <blockquote class="purpose"><p>{esc(m["proposito"])}</p></blockquote>
    <p class="sub-h">Indicadores de logro · rasgos esenciales del programa</p>
    <div class="indic">{tarjetas}</div>""")


def seccion_linea_tiempo(m):
    hitos = "".join(f'<li><b>{esc(h["anio"])}</b><span>{esc(h["texto"])}</span></li>' for h in m["linea_tiempo"])
    return panel("linea", f"""{cabecera_seccion("Línea del tiempo", "Momentos clave de la UDG", "hourglass", prog=False)}
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
    return panel("ejemplo", f"""{cabecera_seccion("Ejemplo", "Así se ve un algoritmo en PSeInt", "terminal", prog=False)}
    <div class="codeblock">
      <div class="code__bar"><span>{icon("file-text", "ic ic--sm")} promedio.psc</span><button class="code__copy" type="button" data-copy data-ripple>{icon("clipboard-list", "ic ic--sm")}<span>Copiar</span></button></div>
      <pre><code data-code>{resaltar_pseint(EJEMPLO_PSEINT)}</code></pre>
    </div>
    <p class="fine">Ejemplo ilustrativo: lee tres calificaciones, calcula el promedio y decide si se aprueba con 60 o más. Usa estructura secuencial y selectiva.</p>""")


def filas_calendario(m, enlaces=False):
    s_hoy = SEMANA
    filas = []
    for w in m["calendario"]:
        suma = sum(x[1] for x in w["p"])
        pts = "".join(
            f'<li class="pt{" pt--ev" if x[0] in EVALUABLES else ""}" style="--c:var(--{EVAL_SLOT[x[0]]})"><i></i>{esc(x[2] if len(x) > 2 else EVAL_NOMBRE[x[0]])} <b>{fmt(x[1])}</b></li>'
            for x in w["p"]
        )
        estado = "is-past" if w["s"] < s_hoy else ("is-now" if w["s"] == s_hoy else "")
        unidad = f"Unidad {w['u']}" if w["u"] else "Cierre del ciclo"
        temas = "".join(f"<span>{esc(t)}</span>" for t in w["temas"])
        ev = any(x[0] in EVALUABLES for x in w["p"])
        filas.append(f"""<li class="cal__w {estado}" id="{"sem-" if enlaces else "w-"}{w['s']}" data-u="{w['u']}" data-ev="{1 if ev else 0}">
        <div class="cal__n"><small>Sem</small><b>{w['s']:02d}</b></div>
        <div class="cal__main"><p class="cal__d">{esc(w['fechas'])} · {unidad}<em class="cal__now">Esta semana</em>{'<em class="cal__evb">Evaluación</em>' if ev else ''}</p><p class="cal__t">{temas}</p>
          {f'<ul class="cal__pts">{pts}</ul>' if pts else ''}</div>
        <div class="cal__sum">{f'<b>{fmt(suma)}</b><small>pts</small>' if suma else '<small>—</small>'}</div>
      </li>""")
    return "".join(filas)


def filtros_calendario(con_ev=False):
    chips = '<button class="seg__btn is-active" type="button" data-cal-filter="0" aria-pressed="true" data-li>Todas</button>' + "".join(
        f'<button class="seg__btn" type="button" data-cal-filter="{u}" aria-pressed="false" data-li>Unidad {u}</button>' for u in range(1, 5)
    )
    if con_ev:
        chips += '<button class="seg__btn" type="button" data-cal-filter="ev" aria-pressed="false" data-li>Evaluaciones</button>'
    return f'<div class="seg seg--sm glass-pill" role="group" aria-label="Filtrar semanas" data-lens="h"><span class="lens" aria-hidden="true"></span>{chips}</div>'


def seccion_calendario(m):
    return panel("calendario", f"""{cabecera_seccion("Semana a semana", "Calendario de temas y puntos", "calendar-days", prog=False)}
    <div class="cal__tools">{filtros_calendario()}<a class="pill" href="../calendario.html">{icon("calendar-plus", "ic ic--xs")} Calendario completo y .ics</a></div>
    <ol class="cal" data-cal>{filas_calendario(m)}</ol>""", ancho=True)


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
    return panel("evaluacion", f"""{cabecera_seccion("Evaluación", "Distribución de los puntos", "gauge", prog=False)}
    <div class="seg-bar" role="group" aria-label="Distribución de {fmt(total)} puntos programados por tipo de evaluación">{"".join(partes)}</div>
    <ul class="legend">{"".join(leyenda)}</ul>
    <div class="utiles">{tiles}</div>
    <details class="table-view"><summary>Ver como tabla</summary>
      <table><thead><tr><th scope="col">Tipo</th><th scope="col">Puntos</th><th scope="col">Porcentaje</th></tr></thead>
      <tbody>{filas}</tbody><tfoot><tr><th scope="row">Total</th><td>{fmt(total)}</td><td>100 %</td></tr></tfoot></table>
    </details>
    <p class="fine">Puntos según el desglose semanal del programa. La suma de lo programado es {fmt(total)} puntos.</p>""", ancho=True)


def seccion_notas(m):
    return panel("notas", f"""{cabecera_seccion("Mis notas", f"Apuntes de {m['corto']}", "notebook-pen", prog=False)}
    <div class="notas" data-notas="{m['slug']}">
      <label class="sr-only" for="notas-{m['slug']}">Mis notas de {esc(m['nombre'])}</label>
      <textarea class="notas__txt" id="notas-{m['slug']}" rows="12" placeholder="Escribe aquí tus apuntes, dudas o fórmulas. Se guardan solos en este navegador." spellcheck="true"></textarea>
      <div class="notas__bar">
        <span class="notas__estado" data-notas-estado aria-live="polite">{icon("check", "ic ic--xs")}<span>Sin notas todavía</span></span>
        <span class="notas__cuenta" data-notas-cuenta>0 palabras</span>
        <div class="notas__acts">
          <button class="pill" type="button" data-notas-copiar>{icon("copy", "ic ic--xs")}<span>Copiar</span></button>
          <button class="pill" type="button" data-notas-bajar>{icon("download", "ic ic--xs")}<span>Descargar .txt</span></button>
          <button class="pill" type="button" data-notas-borrar>{icon("trash-2", "ic ic--xs")}<span>Borrar</span></button>
        </div>
      </div>
    </div>
    <p class="fine">Tus notas se guardan solo en este dispositivo y navegador; nadie más las ve.</p>""")


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
    out.append(("notas", "Mis notas", f"Mis notas de {m['corto']}", seccion_notas(m)))
    return out


def cabecera_materia(m):
    n, t = len(m["secciones"]), total_temas(m)
    docente = f'<li>{icon("user", "ic ic--sm")}<span>{esc(m["docente"])}</span></li>' if m["docente"] else ""
    return f"""
<section class="grid mhead acc" style="--acc:{m['color']}">
  <div class="glass panel mhero span-8" style="view-transition-name:m-{m['slug']}" data-reveal>
    <p class="chip-area"><span class="orb orb--xs">{icon(m["icono"])}</span>{esc(AREAS[m['area']])}</p>
    <h1 class="mhero__title">{esc(m['nombre'])}</h1>
    <p class="mhero__lead">{esc(m['intro'])}</p>
    <ul class="facts-pills">
      <li>{icon("layers", "ic ic--sm")}<span><b>{n}</b> {etiqueta_secciones(m)}</span></li>
      <li>{icon("list-checks", "ic ic--sm")}<span><b>{t}</b> temas y subtemas</span></li>
      {docente}
      <li>{icon("calendar-days", "ic ic--sm")}<span>Ciclo <b>{SITIO['ciclo']}</b></span></li>
    </ul>
    <div class="mhero__acts">
      <button class="pill" type="button" data-share>{icon("share-2", "ic ic--xs")}<span>Compartir</span></button>
      <button class="pill" type="button" data-print>{icon("printer", "ic ic--xs")}<span>Imprimir temario</span></button>
      <button class="pill" type="button" data-ir-tab="notas">{icon("notebook-pen", "ic ic--xs")}<span>Mis notas</span></button>
    </div>
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


def pagina_materia(m):
    secs = secciones_materia(m)
    tabs = "".join(
        f'<button class="seg__btn{" is-active" if k == 0 else ""}" type="button" role="tab" id="tab-{i}" '
        f'aria-controls="{i}" aria-selected="{"true" if k == 0 else "false"}" title="{esc(titulo)}" data-tab="{i}" data-li>{esc(etq)}</button>'
        for k, (i, etq, titulo, _) in enumerate(secs)
    )
    paneles = "\n".join(h for *_, h in secs)
    idx = MATERIAS.index(m)
    ant, sig = MATERIAS[idx - 1], MATERIAS[(idx + 1) % len(MATERIAS)]
    return f"""{cabecera_materia(m)}
<div class="tabsbar acc" style="--acc:{m['color']}">
  <div class="seg seg--tabs glass-pill" role="tablist" aria-label="Secciones de {esc(m['nombre'])}" data-lens="h" data-tabs>
    <span class="lens" aria-hidden="true"></span>{tabs}
  </div>
</div>
<div class="panels acc" style="--acc:{m['color']}" data-panels>
{paneles}
</div>
<nav class="pn" aria-label="Otras materias">
  <a class="glass pn__a acc" style="--acc:{ant['color']}" href="{ant['slug']}.html" data-jelly><span class="pn__k">{icon("arrow-left", "ic ic--sm")} Materia anterior</span><b>{esc(ant['nombre'])}</b></a>
  <a class="glass pn__a pn__a--next acc" style="--acc:{sig['color']}" href="{sig['slug']}.html" data-jelly><span class="pn__k">Siguiente materia {icon("arrow-right", "ic ic--sm")}</span><b>{esc(sig['nombre'])}</b></a>
</nav>"""


def paleta(color):
    return [color, "#3b5bff", "#8b4ff0", "#ff9a3d"]


# ---------------------------------------------------------------- páginas completas
def pagina_inicio():
    contenido = f"""{hero_inicio()}
{tarjetas_estadisticas()}
{seccion_hoy()}
{seccion_materias()}
{seccion_semana()}
{seccion_proyecto()}
{seccion_equipo()}"""
    return app("", "inicio", migas("", ("Panel del semestre", None)), contenido, "inicio", PALETA_INICIO)


def pagina_calendario():
    evs = evaluaciones()
    dias_cierre = max(0, (CIERRE - HOY).days)
    ev_html = "".join(
        f'<li class="evl{" is-past" if e["s"] < SEMANA else (" is-now" if e["s"] == SEMANA else "")}" style="--c:var(--{EVAL_SLOT[e["k"]]})">'
        f'<a href="#sem-{e["s"]}"><i></i><span class="evl__n">{esc(e["n"])}</span><span class="evl__f">Sem {e["s"]} · {esc(e["f"])}</span><b>{fmt(e["pts"])}</b></a></li>'
        for e in evs
    )
    contenido = f"""
<section class="grid mhead acc" style="--acc:#ff9a3d">
  <div class="glass panel mhero span-8" data-reveal>
    <p class="chip-area"><span class="orb orb--xs">{icon("calendar-days")}</span>Ciclo {SITIO["ciclo"]}</p>
    <h1 class="mhero__title">Calendario del ciclo</h1>
    <p class="mhero__lead">Las 18 semanas del ciclo, del 17 de agosto al 18 de diciembre, con el plan semanal de Física: temas, actividades, tareas y exámenes. Agrégalo a tu calendario para recibir los recordatorios en el celular.</p>
    <ul class="facts-pills">
      <li>{icon("layers", "ic ic--sm")}<span><b>18</b> semanas</span></li>
      <li>{icon("bell", "ic ic--sm")}<span><b>{len(evs)}</b> evaluaciones de Física</span></li>
      <li>{icon("hourglass", "ic ic--sm")}<span>Cierre en <b data-cierre>{dias_cierre}</b> días</span></li>
    </ul>
    <div class="hero__cta">
      <a class="btn btn--liquid" href="assets/calendario-2026b.ics" download data-ripple>{icon("calendar-plus", "ic ic--sm")} Agregar a mi calendario</a>
      <button class="btn btn--glass" type="button" data-ir-semana data-ripple>{icon("crosshair", "ic ic--sm")} Ir a esta semana</button>
    </div>
  </div>
  <div class="glass panel morb morb--cal span-4" data-reveal data-jelly>
    {gauge_semana()}
    <div class="morb__tx">
      <p class="morb__k">Semana actual</p>
      <p class="morb__v" data-week-text>{texto_semana(SEMANA)}</p>
    </div>
  </div>
</section>
<section class="grid calgrid">
  <div class="glass panel week span-8" data-reveal>
    <p class="eyebrow">Vista rápida · toca una semana para ir a ella</p>
    {numeros_semana()}
    {pista_semanas().replace('calendario.html#', '#')}
    <div class="calnext">
      <p class="eyebrow">{icon("atom", "ic ic--xs")} Esta semana y lo que sigue</p>
      <ol class="upnext__list upnext__list--row" data-upnext>{lista_proximas(SEMANA)}</ol>
    </div>
  </div>
  <div class="glass panel evlist span-4" data-reveal>
    <p class="eyebrow">{icon("bell", "ic ic--xs")} Evaluaciones de Física</p>
    <ol class="evls">{ev_html}</ol>
  </div>
</section>
<section class="glass panel unit unit--wide calpage acc" style="--acc:#8B4FF0" aria-labelledby="t-plan" data-reveal>
  {cabecera_seccion("Plan semanal", "Semana a semana", "calendar-days", prog=False).replace('class="unit__title"', 'class="unit__title" id="t-plan"')}
  <div class="cal__tools">{filtros_calendario(con_ev=True)}</div>
  <ol class="cal" data-cal>{filas_calendario(FISICA, enlaces=True)}</ol>
  <p class="fine">El plan semanal proviene del desglose de la materia de Física y sus Aplicaciones; es el calendario del ciclo que comparten todas las materias.</p>
</section>"""
    return app("", "calendario", migas("", ("Calendario", None)), contenido, "fisica", PALETA_CAL)


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
{seccion_proyecto("grupo")}"""
    return app("", "equipo", migas("", ("Equipo", None)), contenido, "equipo", PALETA_EQUIPO)


def pagina_materia_completa(m):
    rutas = migas("../", ("Materias", "../index.html#materias"), (m["corto"], None))
    return app("../", m["slug"], rutas, pagina_materia(m), m["slug"], paleta(m["color"]))


def pagina_aviso(clase, eyebrow, titulo, texto, botones):
    """404 y sin conexión: rutas absolutas desde la raíz del dominio."""
    contenido = f"""
<section class="aviso glass panel" data-reveal>
  <p class="eyebrow">{eyebrow}</p>
  <h1 class="aviso__t"><span class="liquid-text">{titulo}</span></h1>
  <p class="aviso__p">{texto}</p>
  <div class="hero__cta">{botones}</div>
</section>"""
    return app("/", clase, migas("/", (eyebrow, None)), contenido, "inicio", PALETA_INICIO)


# ---------------------------------------------------------------- archivos del dominio
def json_ld_materia(m):
    ld = {
        "@context": "https://schema.org", "@type": "Course", "name": m["nombre"], "description": m["intro"],
        "inLanguage": "es-MX",
        "provider": {"@type": "EducationalOrganization", "name": SITIO["escuela"]},
        "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "onsite", "startDate": FISICA["calendario"][0]["ini"], "endDate": CIERRE.isoformat()},
        "syllabusSections": [{"@type": "Syllabus", "name": f"{tipo_seccion(m)} {i}: {s['titulo']}"} for i, s in enumerate(m["secciones"], 1)],
        "teaches": [t["t"] for s in m["secciones"] for t in s["temas"]],
    }
    if URL:
        ld["url"] = absoluta(f"materias/{m['slug']}.html")
    return ld


def ics_texto(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def ics_linea(linea):
    """Dobla líneas a 75 octetos como pide el estándar iCalendar."""
    datos = linea.encode("utf-8")
    if len(datos) <= 75:
        return linea
    partes, actual = [], b""
    for ch in linea:
        b = ch.encode("utf-8")
        if len(actual) + len(b) > (75 if not partes else 74):
            partes.append(actual.decode("utf-8"))
            actual = b""
        actual += b
    partes.append(actual.decode("utf-8"))
    return "\r\n ".join(partes)


def generar_ics():
    sello = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lineas = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Mapa del Semestre 1A//Calendario 2026B//ES", "CALSCALE:GREGORIAN",
              "METHOD:PUBLISH", f"X-WR-CALNAME:{ics_texto('Ciclo 2026B · 1A (Física)')}", "X-WR-TIMEZONE:America/Mexico_City"]
    for w in FISICA["calendario"]:
        ini = date.fromisoformat(w["ini"])
        evs = [x[2] if len(x) > 2 else EVAL_NOMBRE[x[0]] for x in w["p"] if x[0] in EVALUABLES]
        resumen = f"Física · Semana {w['s']}: {' / '.join(w['temas'])}" + (f" · {', '.join(evs)}" if evs else "")
        desc = (puntos_texto(w) + "\n" if w["p"] else "") + "Mapa del Semestre 1A"
        lineas += ["BEGIN:VEVENT", f"UID:semana-{w['s']}-2026b@mapa-semestre-1a", f"DTSTAMP:{sello}",
                   f"DTSTART;VALUE=DATE:{ini:%Y%m%d}", f"DTEND;VALUE=DATE:{ini + timedelta(days=5):%Y%m%d}",
                   f"SUMMARY:{ics_texto(resumen)}", f"DESCRIPTION:{ics_texto(desc)}", "TRANSP:TRANSPARENT", "END:VEVENT"]
    lineas.append("END:VCALENDAR")
    return "\r\n".join(ics_linea(x) for x in lineas) + "\r\n"


PAGINAS = []  # (ruta, archivo og) que van en el sitemap y en la caché sin conexión


def generar_manifest():
    return json.dumps({
        "name": SITIO["titulo"], "short_name": "Semestre 1A",
        "description": "Temario, repaso, notas y calendario del primer semestre del grupo 1A.",
        "lang": "es-MX", "dir": "ltr", "start_url": "./index.html", "scope": "./", "id": "./",
        "display": "standalone", "orientation": "any", "background_color": "#05070d", "theme_color": "#05070d",
        "categories": ["education", "productivity"],
        "icons": [
            {"src": "assets/img/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "assets/img/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "assets/img/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "shortcuts": [
            {"name": "Calendario", "url": "./calendario.html", "icons": [{"src": "assets/img/icons/icon-192.png", "sizes": "192x192"}]},
            {"name": "Equipo", "url": "./equipo.html", "icons": [{"src": "assets/img/icons/icon-192.png", "sizes": "192x192"}]},
        ],
    }, ensure_ascii=False, indent=2)


def generar_sw():
    recursos = ["assets/css/estilos.css", "assets/js/main.js", "assets/js/datos.js", "assets/js/equipo.js"]
    precache = ["./", "offline.html"] + [r for r, _ in PAGINAS]
    precache += [f"{r}?v={version(r)}" for r in recursos]
    precache += ["assets/fonts/geist.woff2", "assets/fonts/geist-mono.woff2", "assets/img/favicon.svg",
                 "assets/img/icons/icon-192.png", "manifest.webmanifest"]
    precache += [f"assets/img/fotos/{m['slug']}-card-600.webp" for m in MATERIAS]
    huella = hashlib.md5("".join(precache).encode() + b"".join((RAIZ / r).read_bytes() for r in recursos + [r for r, _ in PAGINAS])).hexdigest()[:10]
    return f"""/* Service worker del Mapa del Semestre 1A (generado por src/build.py).
   Guarda el sitio para usarlo sin conexión y lo actualiza cuando hay una versión nueva. */
const VERSION = "{huella}";
const PRECACHE = {json.dumps(precache, ensure_ascii=False)};

self.addEventListener("install", (e) => {{
  e.waitUntil(caches.open("base-" + VERSION).then((c) => c.addAll(PRECACHE)));
}});

self.addEventListener("activate", (e) => {{
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => !k.endsWith(VERSION)).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
}});

self.addEventListener("message", (e) => {{ if (e.data === "actualizar") self.skipWaiting(); }});

self.addEventListener("fetch", (e) => {{
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (req.mode === "navigate") {{
    e.respondWith(
      fetch(req)
        .then((r) => {{ const copia = r.clone(); caches.open("paginas-" + VERSION).then((c) => c.put(req, copia)); return r; }})
        .catch(() => caches.match(req, {{ ignoreSearch: true }}).then((r) => r || caches.match("offline.html")))
    );
    return;
  }}
  e.respondWith(
    caches.match(req).then((hit) => {{
      const red = fetch(req)
        .then((r) => {{ if (r.ok) {{ const copia = r.clone(); caches.open("recursos-" + VERSION).then((c) => c.put(req, copia)); }} return r; }})
        .catch(() => hit);
      return hit || red;
    }})
  );
}});
"""


def generar_sitemap():
    hoy = HOY.isoformat()
    urls = "".join(
        f"  <url><loc>{absoluta('' if r == 'index.html' else r)}</loc><lastmod>{hoy}</lastmod>"
        f"<priority>{'1.0' if r == 'index.html' else '0.8'}</priority></url>\n"
        for r, _ in PAGINAS
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


HEADERS = """# Encabezados para Netlify y Cloudflare Pages (GitHub Pages los ignora).
# Las reglas no se enciman a propósito: si dos reglas ponen el mismo encabezado,
# esos servicios juntan los valores.
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  X-Frame-Options: SAMEORIGIN

/assets/css/*
  Cache-Control: public, max-age=31536000, immutable

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/img/*
  Cache-Control: public, max-age=2592000

/assets/js/*
  Cache-Control: public, max-age=3600

/assets/calendario-2026b.ics
  Cache-Control: public, max-age=86400
  Content-Type: text/calendar; charset=utf-8

/sw.js
  Cache-Control: no-cache
"""


# ---------------------------------------------------------------- principal
def escribir(ruta, texto):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8", newline="")


def construir():
    titulo = SITIO["titulo"]
    desc = (f'Temario de las {len(MATERIAS)} materias del primer semestre del grupo {SITIO["grupo"]} ({SITIO["clave"]}), '
            f'{SITIO["carrera"]}, {SITIO["escuela"]}: unidades, temas, repaso, notas y calendario.')
    datos = (
        "/* Generado por src/build.py: calendario, evaluaciones, totales e índice del buscador. */\n"
        f"window.SEMANAS = {json.dumps(datos_semanas(), ensure_ascii=False)};\n"
        f"window.EVALUACIONES = {json.dumps(evaluaciones(), ensure_ascii=False)};\n"
        f"window.TOTALES = {json.dumps({m['slug']: total_temas(m) for m in MATERIAS})};\n"
        f"window.MATERIAS = {json.dumps([{'s': m['slug'], 'n': m['nombre'], 'c': m['corto'], 'col': m['color']} for m in MATERIAS], ensure_ascii=False)};\n"
        f"window.INDICE = {json.dumps(indice_busqueda(), ensure_ascii=False)};\n"
    )
    escribir(RAIZ / "assets/js/datos.js", datos)
    escribir(RAIZ / "assets/calendario-2026b.ics", generar_ics())

    PAGINAS.clear()
    og = []
    ld_sitio = {"@context": "https://schema.org", "@type": "WebSite", "name": titulo, "description": desc, "inLanguage": "es-MX"}
    if URL:
        ld_sitio["url"] = URL + "/"

    def pagina(ruta, tit, descripcion, html_, p, clase, og_nombre, ld=None, og_datos=None):
        escribir(RAIZ / ruta, documento(tit, descripcion, html_, p, clase, ruta, og_nombre, ld))
        PAGINAS.append((ruta, og_nombre))
        if og_datos:
            og.append(dict(og_datos, nombre=og_nombre))

    pagina("index.html", titulo, desc, pagina_inicio(), "", "home", "inicio", ld_sitio,
           {"eyebrow": f'{SITIO["escuela"]} · {SITIO["clave"]}', "titulo": "El mapa de nuestro primer semestre",
            "sub": f"{len(MATERIAS)} materias · {TOTAL_TEMAS} temas · repaso, notas y calendario", "foto": "inicio", "color": "#ff9a3d"})
    pagina("calendario.html", f"Calendario del ciclo · {titulo}", "Las 18 semanas del ciclo 2026B con el plan semanal de Física, evaluaciones y archivo para tu calendario.",
           pagina_calendario(), "", "cal-page", "calendario", None,
           {"eyebrow": f"Ciclo {SITIO['ciclo']} · 18 semanas", "titulo": "Calendario del ciclo", "sub": "Temas, evaluaciones y recordatorios semana a semana", "foto": "fisica", "color": "#ff9a3d"})
    pagina("equipo.html", f"Equipo · {titulo}", "Integrantes del equipo del proyecto integrador.", pagina_equipo(), "", "team-page", "equipo", None,
           {"eyebrow": f"Grupo {SITIO['clave']}", "titulo": "Nuestro equipo", "sub": f"{integrantes_texto()} · {SITIO['carrera']}", "foto": "equipo", "color": "#3b5bff"})
    for m in MATERIAS:
        pagina(f"materias/{m['slug']}.html", f"{m['nombre']} · {titulo}", m["resumen"], pagina_materia_completa(m), "../",
               f"materia materia--{m['slug']}", m["slug"], json_ld_materia(m),
               {"eyebrow": AREAS[m["area"]], "titulo": m["nombre"], "sub": f"{len(m['secciones'])} {etiqueta_secciones(m)} · {total_temas(m)} temas",
                "foto": m["slug"], "color": m["color"]})

    escribir(RAIZ / "404.html", documento(f"Página no encontrada · {titulo}", "Esta página no existe.", pagina_aviso(
        "aviso", "Error 404", "Esta página se fue por el desagüe",
        "No encontramos lo que buscabas. Quizá el enlace cambió o tiene un error. Busca el tema o vuelve al inicio.",
        f'<a class="btn btn--liquid" href="/index.html" data-ripple>{icon("house", "ic ic--sm")} Volver al inicio</a>'
        f'<button class="btn btn--glass" type="button" data-pal-open data-ripple>{icon("search", "ic ic--sm")} Buscar un tema</button>'),
        "/", "aviso-page", "404.html", "inicio"))
    escribir(RAIZ / "offline.html", documento(f"Sin conexión · {titulo}", "No hay conexión a internet.", pagina_aviso(
        "aviso", "Sin conexión", "No hay internet por ahora",
        "Esta página todavía no estaba guardada en tu dispositivo. Las páginas que ya visitaste siguen disponibles sin conexión.",
        f'<a class="btn btn--liquid" href="/index.html" data-ripple>{icon("house", "ic ic--sm")} Ir al inicio</a>'
        f'<button class="btn btn--glass" type="button" onclick="location.reload()" data-ripple>{icon("refresh-cw", "ic ic--sm")} Reintentar</button>'),
        "/", "aviso-page", "offline.html", "inicio"))

    escribir(RAIZ / "manifest.webmanifest", generar_manifest())
    escribir(RAIZ / "sw.js", generar_sw())
    escribir(RAIZ / "robots.txt", "User-agent: *\nAllow: /\n" + (f"\nSitemap: {URL}/sitemap.xml\n" if URL else ""))
    escribir(RAIZ / "_headers", HEADERS)
    escribir(RAIZ / ".nojekyll", "")
    escribir(RAIZ / "src/og_paginas.json", json.dumps(og, ensure_ascii=False, indent=1))
    if URL:
        escribir(RAIZ / "sitemap.xml", generar_sitemap())
        escribir(RAIZ / "CNAME", re.sub(r"^https?://", "", URL) + "\n")


def main():
    construir()
    print(f"Sitio generado: {len(PAGINAS)} páginas + 404 y sin conexión · {TOTAL_TEMAS} temas · "
          f"{'dominio ' + URL if URL else 'sin dominio todavía (SITIO[\"url\"] vacío)'}")


if __name__ == "__main__":
    main()
