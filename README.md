# Mapa del Semestre 1A

Proyecto integrador del grupo **1A, turno matutino (TSIN1AM)** del
**Tecnólogo en Sistemas Informáticos**, Escuela Politécnica de Guadalajara, ciclo 2026B.

Sitio con el temario de las 10 materias del primer semestre, herramientas de
estudio, el calendario del ciclo y las tarjetas del equipo: David, Alan, Armando,
Isaac, Diego y Uziel. Viene en dos versiones con el mismo diseño y contenido:

| Versión | Para qué sirve | Dónde está |
|---|---|---|
| **Google Sites** (la que se entrega) | Armar el sitio en Google Sites pegando 17 bloques ya diseñados | [`google-sites/`](google-sites/) · empieza por [`google-sites/GUIA.md`](google-sites/GUIA.md) |
| **Sitio web completo** (opcional) | Publicarlo con dominio propio; agrega app instalable, modo sin conexión, paleta de comandos y barra lateral | [`index.html`](index.html) y [`DESPLIEGUE.md`](DESPLIEGUE.md) |

En Google Sites cada bloque es un panel independiente: conserva el diseño, el agua,
el modo repaso, las notas, el temporizador y el calendario, pero no la app instalable,
la paleta de comandos ni la barra lateral (la navegación la pone Google Sites).

## Diseño: liquid glass fluid

- **Agua de verdad**: el fondo es una simulación de ondas (WebGL2) que refracta la
  foto de cada materia. El cursor deja estela, cada toque abre ondas que se propagan y
  rebotan, caen gotas sueltas y hay destellos de luz (cáusticas).
- **Vidrio real**: desenfoque en tiempo real; el borde brillante y el reflejo de cada
  panel giran hacia la luz, con un leve arcoíris en el borde; en Chrome y Edge los
  bordes además refractan y dispersan lo que hay detrás.
- **Indicadores que se comportan como gotas** (menú, pestañas, filtros) con física de
  resorte, gota de cristal que sigue al cursor y una micro-animación en cada
  interacción.
- **Transiciones entre páginas**: la barra lateral se queda fija y la tarjeta de una
  materia crece hasta convertirse en su portada (Chrome y Edge).
- **Calidad automática** según el equipo, interruptor **Efecto líquido** para pausar el
  movimiento y respeto a las opciones del sistema de reducir movimiento y de más
  contraste.

## Funciones

| Función | Cómo se usa |
|---|---|
| **Paleta de comandos** | `Ctrl K` (o `⌘ K`, o `/`): busca entre los 230 temas, abre materias, el calendario o cualquier acción. |
| **Tu día** (portada) | Cuenta regresiva a la próxima evaluación, avance de repaso de las 10 materias con sugerencia de qué seguir y acceso rápido al temporizador. |
| **Modo repaso** | Toca el círculo de cada tema para marcarlo. La esfera de la materia se llena; la portada, las tarjetas y la barra lateral muestran el avance. |
| **Temporizador de estudio** | Tecla `T` o el reloj de la barra superior. Sesiones 25·5, 50·10 o 15·3; sigue corriendo al cambiar de página, avisa con sonido, vibración y notificación, y el agua se calma mientras estudias. |
| **Mis notas** | Pestaña en cada materia: se guardan solas, se pueden copiar, descargar en `.txt` o borrar (con opción de deshacer). |
| **Calendario** | Página con las 18 semanas, evaluaciones, filtro por unidad o evaluaciones, «Ir a esta semana» y archivo `.ics` para Google Calendar u Outlook. |
| **App instalable** | Se instala en el celular o la computadora y funciona sin conexión; avisa cuando hay una versión nueva. |
| **Compartir e imprimir** | Cada materia tiene botones para compartir el enlace e imprimir el temario en papel blanco. |
| **Sonidos de agua** | Interruptor en la barra lateral (apagado por omisión). |
| **En el celular** | Barra inferior, menú lateral deslizable y cambio de pestaña deslizando el dedo. |

Todo lo personal (repaso, notas, temporizador) se guarda **solo en el navegador** de
cada persona; el sitio no tiene servidor ni recopila datos.

## Ver el sitio en tu computadora

Abre `index.html` con doble clic. Para probarlo tal como quedará publicado (app
instalable y modo sin conexión), sírvelo desde la carpeta del proyecto:

```bash
python3 -m http.server 8000
```

y abre <http://localhost:8000>.

## Cambiar información

| Quiero cambiar… | Edita | Luego |
|---|---|---|
| Datos de los integrantes | En Google Sites: el bloque `equipo/equipo.html` (ver la guía). En el sitio web: `assets/js/equipo.js` | Para el sitio web, `python3 src/build.py` |
| Fotos de los integrantes | Copia la foto en `assets/img/equipo/` y escribe su ruta en el campo `foto` de `equipo.js` | `python3 src/build.py` |
| Temas, unidades o descripciones | `src/contenido.py` | `python3 src/build.py` |
| El dominio del sitio | `SITIO["url"]` en `src/contenido.py` | `python3 src/build.py` (ver `DESPLIEGUE.md`) |
| Colores, tipografía o diseño | `assets/css/estilos.css` | `python3 src/build.py` |

`python3 src/build.py` genera los 17 bloques de Google Sites y, para la versión web,
las páginas, el calendario `.ics`, el manifiesto de la app, el service worker y los
archivos para buscadores (requiere Python 3.10 o más
reciente, sin librerías extra). Ejecútalo después de **cualquier** cambio: así cambia
la huella de los archivos y nadie se queda con una versión vieja guardada.

## Estructura

```
google-sites/GUIA.md                       guía paso a paso para Google Sites
google-sites/codigos/                      17 bloques para "Insertar código" (generados)
google-sites/imagenes/                     encabezados de página y logotipos
index.html, calendario.html, equipo.html   páginas generadas
materias/                                  una página por materia
404.html, offline.html                     página no encontrada y sin conexión
manifest.webmanifest, sw.js                app instalable y modo sin conexión (generados)
robots.txt, _headers, .nojekyll            buscadores y ajustes del hospedaje
assets/css/estilos.css                     diseño liquid glass (adaptable a celular)
assets/js/main.js                          agua, animaciones, paleta, temporizador, notas…
assets/js/datos.js                         calendario, evaluaciones e índice (generado)
assets/js/equipo.js                        datos del equipo (editable)
assets/js/fondos/                          fotos incrustadas para el agua al abrir con doble clic
assets/calendario-2026b.ics                calendario para importar (generado)
assets/fonts/                              tipografías Geist y Geist Mono (licencia OFL)
assets/img/fotos/                          fotografías en JPG y WebP de varios tamaños
assets/img/icons/, assets/img/og/          íconos de la app y vistas previas al compartir
src/contenido.py                           temario de todas las materias y datos del sitio
src/build.py                               generador del sitio
src/procesar_imagenes.py                   fotos, fondos del agua y encabezados de Google Sites
src/generar_imagenes.js                    íconos, logotipos y vistas previas (Node + Playwright)
src/iconos/                                íconos SVG (Lucide, licencia ISC)
```

## Créditos

- Fotografías: [Unsplash](https://unsplash.com) (Licencia Unsplash, uso libre).
- Íconos: [Lucide](https://lucide.dev) (licencia ISC).
- Tipografías: [Geist y Geist Mono](https://vercel.com/font) (SIL Open Font License).

Proyecto académico elaborado por estudiantes del grupo 1A. No es un sitio oficial de la institución.
