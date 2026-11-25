# Mapa del Semestre 1A

Proyecto integrador del grupo **1A, turno matutino (TSIN1AM)** del
**Tecnólogo en Sistemas Informáticos**, Escuela Politécnica de Guadalajara, ciclo 2026B.

Es un sitio con el temario de las 10 materias del primer semestre, el calendario del
ciclo y las tarjetas de los integrantes del equipo: David, Alan, Armando, Isaac y Diego. Viene en dos versiones:

| Versión | Para qué sirve | Dónde está |
|---|---|---|
| **Kit para Google Sites** | Armar el sitio en Google Sites copiando y pegando bloques ya diseñados | [`google-sites/`](google-sites/) · empieza por [`google-sites/GUIA.md`](google-sites/GUIA.md) |
| **Sitio web completo** | Verlo en el navegador o publicarlo con GitHub Pages; tiene barra lateral, buscador de temas y pestañas por unidad | [`index.html`](index.html), [`equipo.html`](equipo.html), [`materias/`](materias/) |

## Diseño: liquid glass

- **Fondo líquido vivo**: la foto de cada materia con una capa de color fluido (WebGL)
  que se agita al mover el cursor y hace ondas al hacer clic.
- **Vidrio con desenfoque en tiempo real**: paneles esmerilados con borde de luz y un
  brillo que sigue al cursor.
- **Refracción en los bordes** de botones e indicadores (Chrome y Edge).
- **Indicadores que se comportan como gotas**: el marcador del menú, las pestañas y los
  filtros se deslizan y se estiran con física de resorte.
- **Aparición líquida**: las secciones pasan de borrosas a nítidas al llegar a ellas.
- Interruptor **Efecto líquido** en la barra lateral para pausar el movimiento; también
  respeta la opción del sistema de reducir movimiento.

## Materias incluidas

1. Tutoría de Ingreso I
2. Tecnologías de la Información (Prof. Tapia Sandoval D.)
3. Sexualidad y Perspectiva de Género
4. Algoritmos y Programación
5. Inglés Básico
6. Historia e Identidad Universitaria
7. Habilidad Numérica
8. Habilidad de Lectoescritura
9. Física y sus Aplicaciones (con calendario semanal y distribución de puntos)
10. Educación Socioemocional

## Ver el sitio en tu computadora

Descarga el repositorio y abre `index.html` con doble clic. No necesita instalar nada.

## Cambiar información

| Quiero cambiar… | Edita | Luego |
|---|---|---|
| Datos de los integrantes | `assets/js/equipo.js` (sitio web) o la lista `window.EQUIPO` dentro de `google-sites/codigos/equipo/equipo.html` | Guarda. Si editas `equipo.js`, ejecuta `python3 src/build.py` para actualizar también el bloque de Google Sites. |
| Fotos de los integrantes | Copia la foto en `assets/img/equipo/` y escribe la ruta en el campo `foto` de `equipo.js` | Guarda |
| Temas, unidades o descripciones | `src/contenido.py` | `python3 src/build.py` |
| Colores, tipografía o diseño | `assets/css/estilos.css` | `python3 src/build.py` |

`python3 src/build.py` vuelve a generar las 12 páginas del sitio y los 15 bloques
de Google Sites con el mismo contenido (requiere Python 3.10 o más reciente, sin
librerías extra).

## Estructura

```
index.html, equipo.html, materias/   páginas generadas del sitio web
assets/css/estilos.css               diseño liquid glass (adaptable a celular)
assets/js/main.js                    fondo líquido, animaciones e interacción
assets/js/datos.js                   calendario e índice del buscador (lo genera build.py)
assets/js/equipo.js                  datos del equipo (editable)
assets/img/fotos/                    fotografías por materia
google-sites/                        kit para Google Sites (guía, bloques, imágenes)
src/contenido.py                     temario de todas las materias
src/build.py                         generador del sitio y de los bloques
src/procesar_imagenes.py             recorte de fotos y encabezados para Google Sites
src/iconos/                          íconos SVG (Lucide, licencia ISC)
```

## Publicar con GitHub Pages (opcional)

En GitHub: **Settings → Pages → Build and deployment → Deploy from a branch**, elige
la rama principal y la carpeta `/ (root)`. En una cuenta gratuita, el repositorio
debe ser público.

## Créditos

- Fotografías: [Unsplash](https://unsplash.com) (Licencia Unsplash, uso libre).
- Íconos: [Lucide](https://lucide.dev) (licencia ISC).
- Tipografías: Geist y Geist Mono (Google Fonts).

Proyecto académico elaborado por estudiantes del grupo 1A. No es un sitio oficial de la institución.
