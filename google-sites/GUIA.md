# Guía: montar el sitio en Google Sites

Google Sites no permite que un programa cree el sitio por ustedes: hay que armarlo
desde la cuenta de Google de un integrante. Esta carpeta trae todo listo para
**copiar y pegar**. Con esta guía el sitio queda montado en unos 30 o 40 minutos.

```
google-sites/
├── GUIA.md                     ← esta guía
├── codigos/                    ← 15 bloques HTML para "Insertar código"
│   ├── inicio/                 (portada, materias, semana actual, sobre el proyecto)
│   ├── materias/               (uno por materia, con pestañas por unidad)
│   └── equipo/                 (tarjetas de los 8 integrantes)
└── imagenes/
    ├── encabezados/            ← fotos para el encabezado de cada página
    ├── logo-1A.png             ← logotipo cuadrado (también sirve como ícono)
    ├── logo-horizontal-oscuro.png
    └── logo-horizontal-claro.png
```

---

## 1. Crear el sitio y darle identidad

1. Entra a **sites.google.com** con tu cuenta y elige **Sitio en blanco**.
2. Arriba a la izquierda escribe el nombre del sitio: **Mapa del Semestre 1A**.
3. Panel derecho → **Temas** → elige **Simple**. En los círculos de color elige el
   de color personalizado y escribe **#2F5BFF** (el azul del proyecto).
4. Pasa el cursor sobre el nombre del sitio → **Agregar logotipo** → sube
   `imagenes/logo-1A.png`.
5. Engrane de **Configuración** (arriba) → **Marca** → **Favicon** → sube otra vez
   `imagenes/logo-1A.png`.

## 2. Crear las páginas

En el panel derecho, pestaña **Páginas**, crea esta estructura. Para que
*Materias* sea un menú desplegable, arrastra cada materia **encima** de la
página *Materias* (quedan como subpáginas).

| Página | Imagen de encabezado | Bloques que se pegan (en este orden) | Altura aprox. en computadora |
|---|---|---|---|
| **Inicio** | *(sin encabezado, ver nota)* | `inicio/1-portada.html` · `inicio/2-materias.html` · `inicio/3-semana.html` · `inicio/4-proyecto.html` | 790 · 1800 · 440 · 510 px |
| **Materias** | `00-inicio.jpg` | `inicio/2-materias.html` | 1800 px |
| ↳ Tutoría de Ingreso I | `01-tutoria.jpg` | `materias/01-tutoria.html` | 1590 px |
| ↳ Tecnologías de la Información | `02-tecnologias.jpg` | `materias/02-tecnologias.html` | 720 px |
| ↳ Sexualidad y Perspectiva de Género | `03-sexualidad.jpg` | `materias/03-sexualidad.html` | 670 px |
| ↳ Algoritmos y Programación | `04-algoritmos.jpg` | `materias/04-algoritmos.html` | 880 px |
| ↳ Inglés Básico | `05-ingles.jpg` | `materias/05-ingles.html` | 720 px |
| ↳ Historia e Identidad Universitaria | `06-historia.jpg` | `materias/06-historia.html` | 730 px |
| ↳ Habilidad Numérica | `07-numerica.jpg` | `materias/07-numerica.html` | 630 px |
| ↳ Habilidad de Lectoescritura | `08-lectoescritura.jpg` | `materias/08-lectoescritura.html` | 630 px |
| ↳ Física y sus Aplicaciones | `09-fisica.jpg` | `materias/09-fisica.html` | 1330 px |
| ↳ Educación Socioemocional | `10-socioemocional.jpg` | `materias/10-socioemocional.html` | 630 px |
| **Equipo** | `11-equipo.jpg` | `equipo/equipo.html` | 740 px |

**Encabezado de cada página.** Pasa el cursor sobre el encabezado → **Cambiar
imagen** → **Subir** y elige la foto de `imagenes/encabezados/`. En **Tipo de
encabezado** usa **Banner**. Las fotos ya vienen oscurecidas del lado izquierdo para
que el título blanco se lea bien.

**Nota para Inicio.** La portada (`1-portada.html`) ya funciona como encabezado.
En la página Inicio pasa el cursor sobre el encabezado y elimínalo con el ícono del
bote de basura, o elige el tipo **Solo título**.

## 3. Pegar un bloque de código (se repite en cada página)

1. Abre el archivo del bloque. En GitHub: entra al archivo y usa el botón
   **Copy raw file** (ícono de dos hojas). En tu computadora: ábrelo con el Bloc de
   notas, **Ctrl + A** y **Ctrl + C**.
2. En Google Sites: panel derecho **Insertar** → **Incorporar** → pestaña
   **Insertar código** → pega con **Ctrl + V** → **Siguiente** → **Insertar**.
3. Haz el cuadro más ancho arrastrando sus bordes laterales hasta ocupar todo el
   ancho de la sección.
4. Arrastra el borde inferior hacia abajo hasta que **ya no aparezca una barra de
   desplazamiento** dentro del cuadro. La tabla de arriba trae la altura aproximada de
   cada bloque como referencia.

> Los bloques de materias tienen **pestañas** (una por unidad o eje temático), así
> que no necesitan ser muy altos. En Física, el calendario semanal tiene su propio
> desplazamiento y se coloca solo en la semana actual.

## 4. Datos del equipo

Antes de pegar `equipo/equipo.html`, ábrelo y busca casi al final la lista
`window.EQUIPO = [`. Hay **8 renglones**, uno por integrante:

```js
{ nombre: "Ana López Martínez", codigo: "226012345", correo: "ana.lopez@alumnos.udg.mx", rol: "Diseño y contenido", frase: "Me gusta programar videojuegos", foto: "" },
```

- Escribe los datos **entre las comillas**. Lo que dejes vacío (`""`) aparece como un
  espacio punteado "Por completar".
- `foto` necesita un enlace público a una imagen cuadrada. Si no tienen uno, déjalo
  vacío: la tarjeta muestra las iniciales con el color del integrante.
- ¿Ya lo pegaste? Selecciona el bloque en Google Sites → ícono de lápiz
  (**Editar código**) → cambia los datos → **Siguiente** → **Insertar**.

Las tarjetas giran al pasar el cursor (o al tocarlas en el celular) para mostrar
código, correo y frase.

## 5. Publicar y compartir

1. Botón **Publicar** (arriba a la derecha).
2. Escribe la dirección web, por ejemplo `mapa-semestre-1a`.
3. En **Quién puede ver mi sitio** elige quién podrá abrirlo (por ejemplo,
   cualquier persona con el enlace) y comparte la liga con su profesor o profesora.
4. Para que los demás integrantes editen: botón **Compartir con otros** (ícono de
   persona con +) y agrega sus correos como **Editores**.

---

## Preguntas frecuentes

**El cuadro muestra una barra para desplazarse.** Hazlo más alto arrastrando su
borde inferior.

**En el celular algunos bloques se desplazan por dentro.** Es normal: Google Sites
mantiene la misma altura del cuadro en todos los dispositivos y en pantallas angostas
el contenido ocupa más espacio.

**"¿En qué semana vamos?" muestra otra semana.** Se calcula con la fecha del
dispositivo de quien visita el sitio, usando el calendario del ciclo 2026B
(17 de agosto al 18 de diciembre).

**Quiero cambiar un texto de una materia.** Lo más fácil: en Google Sites selecciona
el bloque → **Editar código** → busca el texto y cámbialo. Si prefieren regenerar
todo, edita `src/contenido.py` y ejecuta `python3 src/build.py` (ver `README.md`).

**¿Se puede usar el sitio web completo en lugar de Google Sites?** Sí. En la raíz
del repositorio está la versión completa (`index.html`), con menú, páginas por
materia, modo oscuro y animaciones. Pueden publicarla gratis con GitHub Pages y
poner un botón en Google Sites que lleve a ella.
