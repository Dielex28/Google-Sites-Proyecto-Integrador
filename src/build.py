"""Generador del sitio "Mapa del Semestre 1A".

Uso:
    python3 src/build.py                 # genera el sitio web y el kit de Google Sites
    python3 src/build.py --artifact DIR  # además, una copia para vista previa en DIR

Salidas:
    index.html, equipo.html, materias/*.html      -> sitio web completo
    google-sites/codigos/**.html                  -> bloques para "Insertar > Código" de Google Sites
"""
import html
import json
import re
import shutil
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
    "family=Bricolage+Grotesque:opsz,wght@12..96,500..800"
    "&family=Instrument+Sans:ital,wght@0,400..700;1,400..700"
    "&family=Instrument+Serif:ital@0;1"
    '&family=JetBrains+Mono:wght@400;500;700&display=swap">'
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


def fmt(x):
    return f"{x:.1f}"


TOTAL_TEMAS = sum(total_temas(m) for m in MATERIAS)
FISICA = next(m for m in MATERIAS if m["slug"] == "fisica")


# ---------------------------------------------------------------- piezas comunes
def nav(p, activo):
    enlaces_materias = "".join(
        f'<a class="acc" style="--acc:{m["color"]}" href="{p}materias/{m["slug"]}.html"'
        f'{" aria-current=\"page\"" if activo == m["slug"] else ""}>'
        f'<span class="dd__ic">{icon(m["icono"])}</span>'
        f'<span class="dd__tx">{esc(m["nombre"])}<small>{esc(AREAS[m["area"]])}</small></span></a>'
        for m in MATERIAS
    )
    cur = lambda k: ' aria-current="page"' if activo == k else ""  # noqa: E731
    return f"""
<a class="skip" href="#contenido">Saltar al contenido</a>
<div class="progress" aria-hidden="true"><span data-progress></span></div>
<header class="nav" data-nav>
  <div class="wrap nav__in">
    <a class="brand" href="{p}index.html">
      <span class="brand__mark" aria-hidden="true">1A</span>
      <span class="brand__txt"><b>Mapa del Semestre</b><small>{SITIO["clave"]} · {SITIO["ciclo"]}</small></span>
    </a>
    <nav class="nav__links" id="menu" aria-label="Principal" data-menu>
      <a href="{p}index.html"{cur("inicio")}>Inicio</a>
      <div class="dd" data-dd>
        <button class="dd__btn" type="button" aria-expanded="false" aria-controls="dd-materias">Materias {icon("chevron-down", "ic ic--sm")}</button>
        <div class="dd__panel" id="dd-materias">{enlaces_materias}</div>
      </div>
      <a href="{p}index.html#semana">Calendario</a>
      <a href="{p}equipo.html"{cur("equipo")}>Equipo</a>
    </nav>
    <div class="nav__tools">
      <button class="icon-btn" type="button" data-theme-toggle aria-label="Cambiar entre tema claro y oscuro">{icon("sun", "ic ic--sun")}{icon("moon", "ic ic--moon")}</button>
      <button class="icon-btn nav__burger" type="button" data-menu-toggle aria-expanded="false" aria-controls="menu" aria-label="Abrir menú">{icon("menu", "ic ic--open")}{icon("x", "ic ic--close")}</button>
    </div>
  </div>
</header>"""


def footer(p):
    mitad = (len(MATERIAS) + 1) // 2

    def col(ms):
        return "".join(f'<li><a href="{p}materias/{m["slug"]}.html">{esc(m["nombre"])}</a></li>' for m in ms)

    return f"""
<footer class="foot">
  <div class="wrap foot__in">
    <div class="foot__brand">
      <a class="brand brand--foot" href="{p}index.html"><span class="brand__mark" aria-hidden="true">1A</span>
      <span class="brand__txt"><b>Mapa del Semestre</b><small>{SITIO["clave"]} · {SITIO["ciclo"]}</small></span></a>
      <p>{SITIO["escuela"]}<br>{SITIO["carrera"]}<br>Grupo {SITIO["grupo"]} · Turno {SITIO["turno"].lower()}</p>
    </div>
    <div class="foot__col"><p class="foot__h">Materias</p><ul>{col(MATERIAS[:mitad])}</ul></div>
    <div class="foot__col"><p class="foot__h" aria-hidden="true">&nbsp;</p><ul>{col(MATERIAS[mitad:])}</ul></div>
    <div class="foot__col"><p class="foot__h">Sitio</p><ul>
      <li><a href="{p}index.html#materias">Todas las materias</a></li>
      <li><a href="{p}index.html#semana">Calendario del ciclo</a></li>
      <li><a href="{p}index.html#proyecto">Sobre el proyecto</a></li>
      <li><a href="{p}equipo.html">Nuestro equipo</a></li></ul></div>
  </div>
  <div class="wrap foot__base">
    <p>Proyecto académico elaborado por estudiantes del grupo {SITIO["grupo"]}. No es un sitio oficial de la institución.</p>
    <p>Fotografías: Unsplash · Íconos: Lucide</p>
  </div>
</footer>
<a class="totop" href="#top" aria-label="Volver arriba" data-totop>{icon("arrow-up")}</a>"""


def documento(titulo, descripcion, cuerpo, p="", clase="", envoltura=True):
    head = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(titulo)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{esc(descripcion)}">
<meta name="theme-color" content="#0a1222">
<link rel="icon" href="{p}assets/img/favicon.svg" type="image/svg+xml">
{FUENTES}
<link rel="stylesheet" href="{p}assets/css/estilos.css">
<script>try{{var t=localStorage.getItem("tema");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>"""
    scripts = f'<script src="{p}assets/js/equipo.js"></script>\n<script src="{p}assets/js/main.js" defer></script>'
    if not envoltura:  # página principal de la vista previa (el visor agrega doctype/head/body)
        return f'{head}\n<div class="page {clase}" id="top">\n{cuerpo}\n</div>\n{scripts}\n'
    return (
        f'<!doctype html>\n<html lang="es">\n<head>\n{head}\n</head>\n'
        f'<body class="{clase}" id="top">\n{cuerpo}\n{scripts}\n</body>\n</html>\n'
    )


# ---------------------------------------------------------------- portada
def terminal(embed):
    nombres = []
    for m in MATERIAS:
        nombre = m["slug"]
        if embed:
            nombres.append(f'<span class="t-m" style="--acc:{m["color"]}">{nombre}</span>')
        else:
            nombres.append(f'<a class="t-m" style="--acc:{m["color"]}" href="materias/{m["slug"]}.html">{nombre}</a>')
    filas = "".join(f'<p class="tl tl--out">{"  ".join(nombres[a:b])}</p>' for a, b in ((0, 3), (3, 7), (7, 10)))
    prompt = '<span class="t-p">tsin1am@poli</span><span class="t-c">:~/1A$</span> '
    rol = 'role="img"' if embed else 'role="region"'
    return f"""
<div class="term" {rol} aria-label="Terminal decorativa: lista de las diez materias y avance del semestre">
  <div class="term__bar"><i></i><i></i><i></i><span>tsin1am@politecnica — bash</span></div>
  <div class="term__body" data-term data-inicio="{FISICA["calendario"][0]["ini"]}">
    <p class="tl tl--cmd">{prompt}<span class="t-typed">ls materias/</span></p>
    {filas}
    <p class="tl tl--cmd">{prompt}<span class="t-typed">grep -c "tema" temario.txt</span></p>
    <p class="tl tl--out"><span class="t-n">{TOTAL_TEMAS}</span></p>
    <p class="tl tl--cmd">{prompt}<span class="t-typed">./semestre --progreso</span></p>
    <p class="tl tl--out" data-term-progress>{barra_progreso_texto()}</p>
    <p class="tl tl--cmd tl--last">{prompt}<span class="t-cursor" aria-hidden="true"></span></p>
  </div>
</div>"""


def semana_actual(hoy=None):
    hoy = hoy or date.today()
    cal = FISICA["calendario"]
    if hoy < date.fromisoformat(cal[0]["ini"]):
        return 0
    for w in cal:
        ini = date.fromisoformat(w["ini"])
        if (hoy - ini).days < 7:
            return w["s"]
    return 19


def barra_progreso_texto():
    s = min(max(semana_actual(), 0), 18)
    llenos = round(s / 18 * 18)
    return f'<span class="t-bar">{"█" * llenos}<span class="t-dim">{"░" * (18 - llenos)}</span></span>  semana {s} de 18'


def hero_inicio(embed):
    cta_equipo = "" if embed else '<a class="btn btn--ghost" href="equipo.html">Conocer al equipo</a>'
    cta_mat = "" if embed else f'<a class="btn btn--primary" href="#materias">Explorar materias {icon("arrow-right")}</a>'
    ctas = f'<div class="hero__cta">{cta_mat}{cta_equipo}</div>' if not embed else ""
    return f"""
<section class="hero" data-spot>
  <div class="hero__bg" aria-hidden="true"><div class="hero__grid"></div><div class="glow glow--a"></div><div class="glow glow--b"></div></div>
  <div class="wrap hero__in">
    <div class="hero__copy">
      <p class="eyebrow eyebrow--night"><span class="pulse"></span>{SITIO["escuela"]}</p>
      <h1 class="hero__title"><span class="ln">El mapa de nuestro</span> <span class="ln"><em>primer semestre</em></span></h1>
      <p class="hero__lead">Proyecto integrador del grupo {SITIO["grupo"]}, turno {SITIO["turno"].lower()}, del {SITIO["carrera"]}. Reunimos las diez materias del ciclo {SITIO["ciclo"]} con sus unidades y temas para consultarlas en un solo lugar.</p>
      {ctas}
      <div class="hero__stats">
        <div class="stat"><span class="stat__n" data-count="{len(MATERIAS)}">{len(MATERIAS)}</span><span class="stat__l">materias</span></div>
        <div class="stat"><span class="stat__n" data-count="{TOTAL_TEMAS}">{TOTAL_TEMAS}</span><span class="stat__l">temas y subtemas</span></div>
        <div class="stat"><span class="stat__n" data-count="18">18</span><span class="stat__l">semanas</span></div>
        <div class="stat"><span class="stat__n" data-count="8">8</span><span class="stat__l">integrantes</span></div>
      </div>
    </div>
    {terminal(embed)}
  </div>
</section>"""


def marquesina():
    items = "".join(
        f'<span class="mq__item">{esc(m["nombre"])}</span><span class="mq__sep">{icon("sparkles", "ic ic--sm")}</span>'
        for m in MATERIAS
    )
    return f'<div class="mq" aria-hidden="true"><div class="mq__track">{items}{items}</div></div>'


ANCHAS = {"tutoria", "fisica"}


def tarjeta_materia(m, embed):
    n, t = len(m["secciones"]), total_temas(m)
    meta = f'{n} {etiqueta_secciones(m)} · {t} temas'
    ancha = " mcard--wide" if m["slug"] in ANCHAS else ""
    if embed:
        lista = "".join(f"<li>{esc(s['titulo'])}</li>" for s in m["secciones"])
        return f"""
<article class="mcard mcard--flat acc{ancha}" style="--acc:{m['color']}" data-area="{m['area']}" data-reveal>
  <div class="mcard__art" aria-hidden="true">{icon(m["icono"], "ic mcard__bigic")}</div>
  <div class="mcard__body">
    <div class="mcard__top"><span class="mcard__ic">{icon(m["icono"])}</span><span class="mcard__area">{esc(AREAS[m["area"]])}</span></div>
    <h3>{esc(m["nombre"])}</h3>
    <ol class="mcard__list">{lista}</ol>
    <div class="mcard__foot"><span>{meta}</span></div>
  </div>
</article>"""
    unidades = ""
    if ancha:
        unidades = '<ol class="mcard__list mcard__list--wide">' + "".join(f"<li>{esc(s['titulo'])}</li>" for s in m["secciones"]) + "</ol>"
    return f"""
<a class="mcard acc{ancha}" style="--acc:{m['color']}" href="materias/{m['slug']}.html" data-area="{m['area']}" data-tilt data-reveal>
  <div class="mcard__media"><img src="assets/img/fotos/{m['slug']}-card.jpg" alt="" loading="lazy" decoding="async" width="900" height="600"></div>
  <div class="mcard__body">
    <div class="mcard__top"><span class="mcard__ic">{icon(m["icono"])}</span><span class="mcard__area">{esc(AREAS[m["area"]])}</span></div>
    <h3>{esc(m["nombre"])}</h3>
    <p>{esc(m["resumen"])}</p>{unidades}
    <div class="mcard__foot"><span>{meta}</span><span class="mcard__go">{icon("arrow-up-right")}</span></div>
  </div>
</a>"""


def seccion_materias(embed):
    conteo = {k: sum(1 for m in MATERIAS if m["area"] == k) for k in AREAS}
    filtros = f'<button class="chip is-on" type="button" data-filter="todas" aria-pressed="true">Todas <span>{len(MATERIAS)}</span></button>' + "".join(
        f'<button class="chip" type="button" data-filter="{k}" aria-pressed="false">{esc(v)} <span>{conteo[k]}</span></button>'
        for k, v in AREAS.items()
    )
    tarjetas = "".join(tarjeta_materia(m, embed) for m in MATERIAS)
    lead = (
        "Cada materia con sus unidades o ejes temáticos. Filtra por área para encontrar rápido la que buscas."
        if embed
        else "Cada materia tiene su propia página con unidades, ejes temáticos y temas. Filtra por área o entra directo a la que buscas."
    )
    return f"""
<section class="section" id="materias">
  <div class="wrap">
    <header class="sec-head" data-reveal>
      <p class="eyebrow">Ciclo {SITIO["ciclo"]} · {len(MATERIAS)} materias</p>
      <h2>Lo que vamos a aprender</h2>
      <p class="lead">{lead}</p>
    </header>
    <div class="filters" role="group" aria-label="Filtrar materias por área">{filtros}</div>
    <div class="mgrid" data-mgrid>{tarjetas}</div>
  </div>
</section>"""


def seccion_semana():
    cal = FISICA["calendario"]
    datos = [{"s": w["s"], "ini": w["ini"], "f": w["fechas"], "t": w["temas"][0]} for w in cal]
    s = semana_actual()
    celdas = "".join(
        f'<li class="{"is-past" if w["s"] < s else ("is-now" if w["s"] == s else "")}" data-s="{w["s"]}" title="Semana {w["s"]} · {w["fechas"]}"><span>{w["s"]}</span></li>'
        for w in cal
    )
    meses = [("Ago", 1), ("Sep", 3), ("Oct", 7), ("Nov", 12), ("Dic", 16)]
    etiquetas = "".join(f'<span style="grid-column:{c}">{n}</span>' for n, c in meses)
    texto = texto_semana(s)
    return f"""
<section class="section section--tight" id="semana">
  <div class="wrap">
    <div class="week" data-week='{esc(json.dumps(datos, ensure_ascii=False))}' data-reveal>
      <div class="week__head">
        <div>
          <p class="eyebrow">Calendario del ciclo {SITIO["ciclo"]}</p>
          <h2>¿En qué semana vamos?</h2>
          <p class="week__now" data-week-text>{texto}</p>
        </div>
        <div class="week__big" aria-hidden="true"><span data-week-n>{s if 1 <= s <= 18 else "—"}</span><small>/18</small></div>
      </div>
      <div class="week__track">
        <ol class="week__bar" aria-label="Semanas del ciclo">{celdas}</ol>
        <div class="week__months" aria-hidden="true">{etiquetas}</div>
      </div>
    </div>
  </div>
</section>"""


def texto_semana(s):
    cal = FISICA["calendario"]
    if s <= 0:
        return "El ciclo inicia el lunes 17 de agosto con la semana 1."
    if s > 18:
        return "El ciclo 2026B ya concluyó. ¡Gracias por acompañarnos!"
    w = cal[s - 1]
    if s == 18:
        return f"Semana 18 · {w['fechas']}: fecha límite para el registro y publicación de la evaluación continua."
    faltan = 18 - s
    return f"Semana {s} · {w['fechas']}. En Física toca: {w['temas'][0]}. Faltan {faltan} semanas para el cierre del ciclo."


def seccion_proyecto(embed):
    datos = [
        ("Escuela", SITIO["escuela"]),
        ("Carrera", SITIO["carrera"]),
        ("Grupo y turno", f'{SITIO["grupo"]} · {SITIO["turno"]}'),
        ("Clave del grupo", SITIO["clave"]),
        ("Ciclo escolar", SITIO["ciclo"]),
    ]
    dl = "".join(f"<div><dt>{a}</dt><dd>{esc(b)}</dd></div>" for a, b in datos)
    media = (
        ""
        if embed
        else f"""<figure class="about__media" data-reveal>
        <img src="assets/img/fotos/proyecto.jpg" alt="Estudiantes trabajando en equipo con sus laptops" loading="lazy" decoding="async" width="2000" height="1000">
        <figcaption class="about__badge">{icon("award")}<span>Proyecto integrador<br><b>Ciclo {SITIO["ciclo"]}</b></span></figcaption>
      </figure>"""
    )
    return f"""
<section class="section about{" about--solo" if embed else ""}" id="proyecto">
  <div class="wrap about__in">
    {media}
    <div class="about__copy" data-reveal>
      <p class="eyebrow">Sobre el proyecto</p>
      <h2>Un sitio hecho por y para el {SITIO["grupo"]}</h2>
      <p>Este sitio es nuestro proyecto integrador. Organiza el temario de cada materia del primer semestre para consultarlo rápido, repasar antes de un examen y saber qué tema viene después.</p>
      <dl class="facts">{dl}</dl>
    </div>
  </div>
</section>"""


def tarjetas_equipo_estaticas():
    """Tarjetas de respaldo; main.js las reemplaza con los datos de equipo.js."""
    out = []
    for i in range(1, 9):
        out.append(f"""
<article class="tcard" tabindex="0">
  <div class="tcard__in"><div class="tcard__face tcard__front">
    <div class="tcard__avatar">{icon("user")}</div>
    <span class="tcard__num">Integrante {i:02d}</span>
    <h3 class="tcard__name is-empty">Nombre del integrante</h3>
    <p class="tcard__rol is-empty">Rol en el equipo</p>
  </div></div>
</article>""")
    return "".join(out)


def seccion_equipo(pagina=False):
    if pagina:
        cab = ""
    else:
        cab = f"""
    <header class="sec-head sec-head--row" data-reveal>
      <div><p class="eyebrow">Equipo · {SITIO["grupo"]} {SITIO["turno"]}</p>
      <h2>Quienes hicimos este sitio</h2>
      <p class="lead">Pasa el cursor o toca una tarjeta para ver los datos de cada integrante.</p></div>
      <a class="btn btn--line" href="equipo.html">Ver la página del equipo {icon("arrow-right")}</a>
    </header>"""
    return f"""
<section class="section" id="equipo">
  <div class="wrap">{cab}
    <div class="team" data-equipo>{tarjetas_equipo_estaticas()}</div>
  </div>
</section>"""


# ---------------------------------------------------------------- páginas de materia
def arbol(temas, nivel=0):
    items = []
    for t in temas:
        sub = t["sub"]
        chips = bool(sub) and all(not s["c"] and not s["sub"] for s in sub)
        marca = f'<span class="code">{esc(t["c"])}</span>' if t["c"] else '<span class="bullet" aria-hidden="true"></span>'
        dentro = f'<div class="node">{marca}<span class="node__t">{esc(t["t"])}</span></div>'
        if chips:
            dentro += '<ul class="tags">' + "".join(f"<li>{esc(s['t'])}</li>" for s in sub) + "</ul>"
        elif sub:
            dentro += arbol(sub, nivel + 1)
        items.append(f"<li>{dentro}</li>")
    return f'<ol class="tree tree--l{nivel}">' + "".join(items) + "</ol>"


def cabecera_seccion(etiqueta, titulo, icono, nivel="h2"):
    return f"""<header class="unit__head">
      <span class="unit__ic">{icon(icono)}</span>
      <div><p class="unit__label">{esc(etiqueta)}</p><{nivel} class="unit__title">{esc(titulo)}</{nivel}></div>
    </header>"""


def seccion_unidad(m, i, s):
    tipo = "Unidad de competencia" if m["slug"] == "fisica" else ("Unidad" if m["tipo_seccion"] == "Unidad" else "Eje temático")
    partes = [cabecera_seccion(f"{tipo} {i}", s["titulo"], s["icono"])]
    if s.get("objetivo"):
        partes.append(f'<div class="objective"><p class="objective__k">{icon("target", "ic ic--sm")} Objetivo</p><p>{esc(s["objetivo"])}</p></div>')
    if s.get("descripcion"):
        partes.append(f'<p class="unit__desc">{esc(s["descripcion"])}</p>')
    partes.append(arbol(s["temas"]))
    if s.get("insignia"):
        partes.append(f'<p class="badge">{icon("flag", "ic ic--sm")} {esc(s["insignia"])}</p>')
    if s.get("nota"):
        partes.append(f'<aside class="note">{icon("info")}<p><b>Nota.</b> {esc(s["nota"])}</p></aside>')
    return f'<section class="unit" id="u{i}" data-panel data-reveal>\n' + "\n".join(partes) + "\n</section>"


def seccion_presentacion(m):
    tarjetas = "".join(
        f"""<article class="indic__card">
          <div class="indic__top"><span class="indic__ic">{icon(g["icono"])}</span><h3>{esc(g["titulo"])}</h3></div>
          <ul class="tags tags--soft">{"".join(f"<li>{esc(x)}</li>" for x in g["items"])}</ul>
        </article>"""
        for g in m["indicadores"]
    )
    return f"""<section class="unit" id="presentacion" data-panel data-reveal>
    {cabecera_seccion("Presentación", "Propósito e indicadores de logro", "target")}
    <blockquote class="purpose"><p>{esc(m["proposito"])}</p></blockquote>
    <p class="sub-h">Indicadores de logro · rasgos esenciales del programa</p>
    <div class="indic">{tarjetas}</div>
  </section>"""


def seccion_linea_tiempo(m):
    hitos = "".join(f'<li><b>{esc(h["anio"])}</b><span>{esc(h["texto"])}</span></li>' for h in m["linea_tiempo"])
    return f"""<section class="unit" id="linea" data-panel data-reveal>
    {cabecera_seccion("Línea del tiempo", "Momentos clave de la UDG", "hourglass")}
    <ol class="tline">{hitos}</ol>
    <p class="fine">Fechas tomadas de los temas de la unidad 1.</p>
  </section>"""


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
    return f"""<section class="unit" id="ejemplo" data-panel data-reveal>
    {cabecera_seccion("Ejemplo", "Así se ve un algoritmo en PSeInt", "terminal")}
    <div class="codeblock">
      <div class="code__bar"><span>{icon("file-text", "ic ic--sm")} promedio.psc</span><button class="code__copy" type="button" data-copy>{icon("clipboard-list", "ic ic--sm")}<span>Copiar</span></button></div>
      <pre><code data-code>{resaltar_pseint(EJEMPLO_PSEINT)}</code></pre>
    </div>
    <p class="fine">Ejemplo ilustrativo: lee tres calificaciones, calcula el promedio y decide si se aprueba con 60 o más. Usa estructura secuencial y selectiva.</p>
  </section>"""


def seccion_calendario(m):
    s_hoy = semana_actual()
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
        filas.append(f"""<li class="cal__w {estado}" data-u="{w['u']}" data-ini="{w['ini']}">
        <div class="cal__n"><small>Sem</small><b>{w['s']:02d}</b></div>
        <div class="cal__main"><p class="cal__d">{esc(w['fechas'])} · {unidad}<em class="cal__now">Esta semana</em></p><p class="cal__t">{temas}</p>
          {f'<ul class="cal__pts">{pts}</ul>' if pts else ''}</div>
        <div class="cal__sum">{f'<b>{fmt(suma)}</b><small>pts</small>' if suma else '<small>—</small>'}</div>
      </li>""")
    chips = '<button class="chip is-on" type="button" data-cal-filter="0" aria-pressed="true">Todas</button>' + "".join(
        f'<button class="chip" type="button" data-cal-filter="{u}" aria-pressed="false">Unidad {u}</button>' for u in range(1, 5)
    )
    return f"""<section class="unit unit--wide" id="calendario" data-panel data-reveal>
    {cabecera_seccion("Semana a semana", "Calendario de temas y puntos", "calendar-days")}
    <div class="filters filters--sm" role="group" aria-label="Filtrar semanas por unidad">{chips}</div>
    <ol class="cal" data-cal>{"".join(filas)}</ol>
  </section>"""


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
            f'<div class="seg__part" style="flex:{v};--c:var(--{slot})" tabindex="0" '
            f'aria-label="{nombre}: {fmt(v)} puntos, {pct:.0f} %" data-tip="{nombre} · {fmt(v)} pts · {pct:.0f} %"><span>{v:g}</span></div>'
        )
        leyenda.append(f'<li><i style="--c:var(--{slot})"></i>{nombre}<span>{pct:.0f} %</span></li>')
    tiles = "".join(
        f"""<div class="utile"><p class="utile__k">Unidad {u}</p><p class="utile__v">{fmt(por_unidad[u])}<small> pts</small></p><p class="utile__s">{semanas_u[u]} semanas · {esc(m["secciones"][u - 1]["titulo"])}</p></div>"""
        for u in range(1, 5)
    )
    filas = "".join(f"<tr><th scope='row'>{n}</th><td>{fmt(totales[k])}</td><td>{totales[k] / total * 100:.1f} %</td></tr>" for k, n, _ in EVAL)
    return f"""<section class="unit unit--wide" id="evaluacion" data-panel data-reveal>
    {cabecera_seccion("Evaluación", "Distribución de los puntos", "gauge")}
    <div class="seg" role="group" aria-label="Distribución de {fmt(total)} puntos programados por tipo de evaluación">{"".join(partes)}</div>
    <ul class="legend">{"".join(leyenda)}</ul>
    <div class="utiles">{tiles}</div>
    <details class="table-view"><summary>Ver como tabla</summary>
      <table><thead><tr><th scope="col">Tipo</th><th scope="col">Puntos</th><th scope="col">Porcentaje</th></tr></thead>
      <tbody>{filas}</tbody><tfoot><tr><th scope="row">Total</th><td>{fmt(total)}</td><td>100 %</td></tr></tfoot></table>
    </details>
    <p class="fine">Puntos según el desglose semanal del programa. La suma de lo programado es {fmt(total)} puntos.</p>
  </section>"""


def secciones_materia(m):
    """Lista de (id, etiqueta corta, html) en el orden de la página."""
    out = []
    if m.get("indicadores"):
        out.append(("presentacion", "Presentación", seccion_presentacion(m)))
    if m.get("linea_tiempo"):
        out.append(("linea", "Línea del tiempo", seccion_linea_tiempo(m)))
    for i, s in enumerate(m["secciones"], 1):
        pref = "U" if m["tipo_seccion"] == "Unidad" else "Eje"
        out.append((f"u{i}", f"{pref} {i} · {s['titulo']}", seccion_unidad(m, i, s)))
    if m["slug"] == "algoritmos":
        out.append(("ejemplo", "Ejemplo en PSeInt", seccion_ejemplo()))
    if m.get("calendario"):
        out.append(("calendario", "Calendario semanal", seccion_calendario(m)))
        out.append(("evaluacion", "Evaluación", seccion_evaluacion(m)))
    return out


def hero_materia(m, p):
    n, t = len(m["secciones"]), total_temas(m)
    docente = f'<li>{icon("user", "ic ic--sm")}<span>{esc(m["docente"])}</span></li>' if m["docente"] else ""
    return f"""
<section class="mhero acc" style="--acc:{m['color']}">
  <div class="mhero__bg" aria-hidden="true"><img src="{p}assets/img/fotos/{m['slug']}.jpg" alt="" fetchpriority="high" width="2000" height="1000"></div>
  <div class="mhero__shade" aria-hidden="true"></div>
  <div class="wrap mhero__in">
    <nav class="crumbs" aria-label="Ruta de navegación"><a href="{p}index.html">Inicio</a><span aria-hidden="true">/</span><a href="{p}index.html#materias">Materias</a><span aria-hidden="true">/</span><span aria-current="page">{esc(m['corto'])}</span></nav>
    <p class="mhero__tag"><span class="mhero__ic">{icon(m["icono"])}</span>{esc(AREAS[m['area']])}</p>
    <h1 class="mhero__title">{esc(m['nombre'])}</h1>
    <p class="mhero__lead">{esc(m['intro'])}</p>
    <ul class="mhero__facts">
      <li>{icon("layers", "ic ic--sm")}<span><b>{n}</b> {etiqueta_secciones(m)}</span></li>
      <li>{icon("list-checks", "ic ic--sm")}<span><b>{t}</b> temas y subtemas</span></li>
      {docente}
      <li>{icon("calendar-days", "ic ic--sm")}<span>Ciclo <b>{SITIO['ciclo']}</b></span></li>
    </ul>
  </div>
</section>"""


def intro_embed(m):
    n, t = len(m["secciones"]), total_temas(m)
    docente = f'<li>{icon("user", "ic ic--sm")}<span>{esc(m["docente"])}</span></li>' if m["docente"] else ""
    return f"""
<section class="eintro acc" style="--acc:{m['color']}">
  <div class="wrap eintro__in">
    <span class="eintro__ic">{icon(m["icono"])}</span>
    <div class="eintro__tx">
      <p class="eyebrow">{esc(AREAS[m['area']])} · {SITIO['clave']}</p>
      <p class="eintro__lead">{esc(m['intro'])}</p>
      <ul class="eintro__facts">
        <li>{icon("layers", "ic ic--sm")}<span><b>{n}</b> {etiqueta_secciones(m)}</span></li>
        <li>{icon("list-checks", "ic ic--sm")}<span><b>{t}</b> temas y subtemas</span></li>
        {docente}
      </ul>
    </div>
  </div>
</section>"""


def pagina_materia(m, embed=False):
    idx = MATERIAS.index(m)
    secs = secciones_materia(m)
    toc = "".join(f'<li><a href="#{i}" data-toc="{i}">{esc(e)}</a></li>' for i, e, _ in secs)
    contenido = "\n".join(h for _, _, h in secs)
    if embed:
        tabs = "".join(
            f'<button class="tab{" is-on" if k == 0 else ""}" type="button" role="tab" data-tab="{i}" aria-selected="{"true" if k == 0 else "false"}">{esc(e)}</button>'
            for k, (i, e, _) in enumerate(secs)
        )
        return f"""{intro_embed(m)}
<main id="contenido" class="acc" style="--acc:{m['color']}">
  <div class="wrap">
    <div class="tabs" role="tablist" aria-label="Secciones de {esc(m['nombre'])}">{tabs}</div>
    <div class="mcontent mcontent--embed">{contenido}</div>
  </div>
</main>"""
    ant, sig = MATERIAS[idx - 1], MATERIAS[(idx + 1) % len(MATERIAS)]
    return f"""{nav("../", m["slug"])}
{hero_materia(m, "../")}
<main id="contenido" class="acc" style="--acc:{m['color']}">
  <div class="wrap mlayout">
    <aside class="toc" aria-label="Contenido de la página">
      <p class="toc__title">En esta página</p>
      <ol>{toc}</ol>
    </aside>
    <div class="mcontent">{contenido}</div>
  </div>
  <nav class="wrap pn" aria-label="Otras materias">
    <a class="pn__a acc" style="--acc:{ant['color']}" href="{ant['slug']}.html"><span class="pn__k">{icon("arrow-left", "ic ic--sm")} Materia anterior</span><b>{esc(ant['nombre'])}</b></a>
    <a class="pn__a pn__a--next acc" style="--acc:{sig['color']}" href="{sig['slug']}.html"><span class="pn__k">Siguiente materia {icon("arrow-right", "ic ic--sm")}</span><b>{esc(sig['nombre'])}</b></a>
  </nav>
</main>
{footer("../")}"""


# ---------------------------------------------------------------- páginas
def pagina_inicio():
    return f"""{nav("", "inicio")}
<main id="contenido">
{hero_inicio(False)}
{marquesina()}
{seccion_materias(False)}
{seccion_semana()}
{seccion_proyecto(False)}
{seccion_equipo()}
</main>
{footer("")}"""


def pagina_equipo():
    return f"""{nav("", "equipo")}
<section class="mhero mhero--team acc" style="--acc:#2f5bff">
  <div class="mhero__bg" aria-hidden="true"><img src="assets/img/fotos/equipo.jpg" alt="" fetchpriority="high" width="2000" height="1000"></div>
  <div class="mhero__shade" aria-hidden="true"></div>
  <div class="wrap mhero__in">
    <nav class="crumbs" aria-label="Ruta de navegación"><a href="index.html">Inicio</a><span aria-hidden="true">/</span><span aria-current="page">Equipo</span></nav>
    <p class="mhero__tag"><span class="mhero__ic">{icon("users")}</span>Equipo del proyecto</p>
    <h1 class="mhero__title">Nuestro equipo</h1>
    <p class="mhero__lead">Ocho integrantes del grupo {SITIO["grupo"]}, turno {SITIO["turno"].lower()}, del {SITIO["carrera"]}. Pasa el cursor o toca cada tarjeta para ver sus datos.</p>
    <ul class="mhero__facts">
      <li>{icon("users", "ic ic--sm")}<span><b>8</b> integrantes</span></li>
      <li>{icon("hash", "ic ic--sm")}<span>Grupo <b>{SITIO["clave"]}</b></span></li>
      <li>{icon("calendar-days", "ic ic--sm")}<span>Ciclo <b>{SITIO["ciclo"]}</b></span></li>
    </ul>
  </div>
</section>
<main id="contenido">
{seccion_equipo(pagina=True)}
{seccion_proyecto(False).replace('id="proyecto"', 'id="grupo"')}
</main>
{footer("")}"""


# ---------------------------------------------------------------- bloques para Google Sites
def bloque_embed(titulo, cuerpo, css, js_equipo, js_main):
    return f"""<!doctype html>
<!--
  {titulo}
  Bloque para Google Sites: Insertar > Insertar código (pestaña "Insertar código").
  Pega TODO este archivo, presiona Siguiente > Insertar y ajusta la altura del cuadro.
  Generado con src/build.py — Mapa del Semestre {SITIO["grupo"]} ({SITIO["clave"]}).
-->
<html lang="es" class="embed" data-theme="light">
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
{cuerpo}
<script>
{js_equipo}
</script>
<script>
{js_main}
</script>
</body>
</html>
"""


def compactar_css(css):
    """Quita comentarios y espacios sobrantes para que cada bloque pese menos."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def generar_embeds():
    css = compactar_css((RAIZ / "assets/css/estilos.css").read_text(encoding="utf-8"))
    js_main = (RAIZ / "assets/js/main.js").read_text(encoding="utf-8")
    js_equipo = (RAIZ / "assets/js/equipo.js").read_text(encoding="utf-8")
    bloques = {
        "inicio/1-portada.html": ("Inicio · Portada", f"{hero_inicio(True)}\n{marquesina()}"),
        "inicio/2-materias.html": ("Inicio · Materias", seccion_materias(True)),
        "inicio/3-semana.html": ("Inicio · ¿En qué semana vamos?", seccion_semana()),
        "inicio/4-proyecto.html": ("Inicio · Sobre el proyecto", seccion_proyecto(True)),
        "equipo/equipo.html": ("Equipo", seccion_equipo(pagina=True)),
    }
    for i, m in enumerate(MATERIAS, 1):
        bloques[f"materias/{i:02d}-{m['slug']}.html"] = (m["nombre"], pagina_materia(m, embed=True))
    for ruta, (titulo, cuerpo) in bloques.items():
        destino = CODIGOS / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(bloque_embed(titulo, cuerpo, css, js_equipo, js_main), encoding="utf-8")
    return bloques


# ---------------------------------------------------------------- principal
def escribir(ruta, texto):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


def construir(destino, artifact=False):
    titulo = SITIO["titulo"]
    desc = f'Temario de las {len(MATERIAS)} materias del primer semestre del grupo {SITIO["grupo"]} ({SITIO["clave"]}), {SITIO["carrera"]}, {SITIO["escuela"]}.'
    escribir(destino / "index.html", documento(titulo, desc, pagina_inicio(), "", "home", envoltura=not artifact))
    escribir(destino / "equipo.html", documento(f"Equipo · {titulo}", "Integrantes del equipo del proyecto integrador.", pagina_equipo(), "", "team-page"))
    for m in MATERIAS:
        escribir(
            destino / "materias" / f"{m['slug']}.html",
            documento(f"{m['nombre']} · {titulo}", m["resumen"], pagina_materia(m), "../", f"materia materia--{m['slug']}"),
        )


def main():
    construir(RAIZ)
    bloques = generar_embeds()
    print(f"Sitio generado: {len(MATERIAS) + 2} páginas · {TOTAL_TEMAS} temas · {len(bloques)} bloques para Google Sites")
    if "--artifact" in sys.argv:
        dest = Path(sys.argv[sys.argv.index("--artifact") + 1])
        construir(dest, artifact=True)
        shutil.copytree(RAIZ / "assets", dest / "assets", dirs_exist_ok=True)
        print("Vista previa en", dest)


if __name__ == "__main__":
    main()
