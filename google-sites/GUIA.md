# Guía: montar el sitio en Google Sites

Google Sites no permite que un programa cree el sitio por ustedes: hay que armarlo
desde la cuenta de Google de un integrante. Esta carpeta trae todo listo para
**copiar y pegar**. Con esta guía el sitio queda montado en unos 40 minutos.

> ¿Prefieres una lista para ir palomeando, con enlaces directos a cada bloque e
> imagen? Está en [LISTA.md](LISTA.md).

Cada bloque es un panel *liquid glass* completo: su propio fondo de agua con la foto
de la página (ondas al mover el cursor o tocar), vidrio con desenfoque y reflejos en
tiempo real e indicadores que se deslizan como gotas. Se ven bien sobre cualquier tema
de Google Sites porque son paneles oscuros independientes.

```
google-sites/
├── GUIA.md                      ← esta guía
├── codigos/                     ← 17 bloques HTML para "Insertar código"
│   ├── inicio/                  (portada, tu día, materias, semana, sobre el proyecto)
│   ├── materias/                (uno por materia, con pestañas por unidad y notas)
│   ├── calendario/              (las 18 semanas, evaluaciones y archivo para tu calendario)
│   └── equipo/                  (tarjetas de los integrantes)
└── imagenes/
    ├── encabezados/             ← foto para el encabezado de cada página
    ├── logo-1A.png              ← logotipo cuadrado (también sirve como ícono)
    ├── logo-horizontal-claro.png   (texto claro, para encabezados oscuros)
    └── logo-horizontal-oscuro.png  (texto oscuro, para fondos claros)
```

---

## 1. Crear el sitio y darle identidad

1. Entra a **sites.google.com** con tu cuenta y elige **Sitio en blanco**.
2. Arriba a la izquierda escribe el nombre del sitio: **Mapa del Semestre 1A**.
3. Panel derecho → **Temas** → elige **Simple**. En los círculos de color elige el
   personalizado y escribe **#3B5BFF** (el azul del proyecto).
   *Opcional, para que todo se vea oscuro:* selecciona cada sección que contiene un
   bloque y en **Fondo de la sección** prueba el estilo más oscuro.
4. Pasa el cursor sobre el nombre del sitio → **Agregar logotipo** → sube
   `imagenes/logo-1A.png` (o `logo-horizontal-claro.png` si el encabezado es oscuro).
5. Engrane de **Configuración** → **Marca** → **Favicon** → sube `imagenes/logo-1A.png`.

## 2. Crear las páginas

En el panel derecho, pestaña **Páginas**, crea esta estructura. Para que *Materias*
sea un menú desplegable, arrastra cada materia **encima** de la página *Materias*
(quedan como subpáginas).

| Página | Imagen de encabezado | Bloques (en este orden) | Altura de cada bloque en computadora |
|---|---|---|---|
| **Inicio** | *(sin encabezado, ver nota)* | `inicio/1-portada.html` · `inicio/2-tu-dia.html` · `inicio/3-materias.html` · `inicio/4-semana.html` · `inicio/5-proyecto.html` | 610 · 330 · 1940 · 600 · 480 px |
| **Materias** | `00-inicio.jpg` | `inicio/3-materias.html` | 1940 px |
| ↳ Tutoría de Ingreso I | `01-tutoria.jpg` | `materias/01-tutoria.html` | 1740 px |
| ↳ Tecnologías de la Información | `02-tecnologias.jpg` | `materias/02-tecnologias.html` | 1190 px |
| ↳ Sexualidad y Perspectiva de Género | `03-sexualidad.jpg` | `materias/03-sexualidad.html` | 1170 px |
| ↳ Programación Básica | `04-programacion.jpg` | `materias/04-programacion.html` | 1120 px |
| ↳ Inglés Básico | `05-ingles.jpg` | `materias/05-ingles.html` | 1090 px |
| ↳ Historia e Identidad Universitaria | `06-historia.jpg` | `materias/06-historia.html` | 1150 px |
| ↳ Habilidad Numérica | `07-numerica.jpg` | `materias/07-numerica.html` | 1090 px |
| ↳ Habilidad de Lectoescritura | `08-lectoescritura.jpg` | `materias/08-lectoescritura.html` | 1090 px |
| ↳ Física y sus Aplicaciones | `09-fisica.jpg` | `materias/09-fisica.html` | 1460 px |
| ↳ Educación Socioemocional | `10-socioemocional.jpg` | `materias/10-socioemocional.html` | 1090 px |
| **Calendario** | `12-calendario.jpg` | `calendario/calendario.html` | 2120 px |
| **Equipo** | `11-equipo.jpg` | `equipo/equipo.html` | 1000 px |

**Encabezado de cada página.** Pasa el cursor sobre el encabezado → **Cambiar
imagen** → **Subir** y elige la foto de `imagenes/encabezados/`. En **Tipo de
encabezado** usa **Banner**. Las fotos ya vienen oscurecidas del lado izquierdo para
que el título blanco se lea bien.

**Nota para Inicio.** La portada (`1-portada.html`) ya funciona como encabezado.
En la página Inicio pasa el cursor sobre el encabezado y elimínalo con el bote de
basura, o elige el tipo **Solo título**.

## 3. Pegar un bloque de código (se repite en cada página)

1. Abre el archivo del bloque. En GitHub: entra al archivo y usa el botón **Copy raw
   file** (ícono de dos hojas). En tu computadora: ábrelo con el Bloc de notas,
   **Ctrl + A** y **Ctrl + C**. Copia **todo**, desde `<!doctype html>` hasta `</html>`.
2. En Google Sites: panel derecho **Insertar** → **Incorporar** → pestaña
   **Insertar código** → pega con **Ctrl + V** → **Siguiente** → **Insertar**.
3. Arrastra los bordes laterales del cuadro hasta que ocupe **todo el ancho** de la
   sección.
4. Arrastra el borde inferior hasta la **altura de la tabla**, o hasta que ya no
   aparezca una barra de desplazamiento dentro del cuadro.

> Los bloques de materias tienen **pestañas** (una por unidad), así que no necesitan
> ser muy altos. La altura de la tabla alcanza para la pestaña más larga. En el
> calendario, la lista de semanas tiene su propio desplazamiento.

## 4. Datos del equipo

Abre `codigos/equipo/equipo.html` y busca, casi al principio, el bloque marcado con
**✏️ DATOS DEL EQUIPO**. Hay un renglón por integrante con los nombres ya puestos
(David, Alan, Armando, Isaac, Diego y Uziel). Completa el resto, por ejemplo:

```js
{ nombre: "David López Martínez", codigo: "226012345", correo: "david.lopez@alumnos.udg.mx", rol: "Diseño y contenido", frase: "Me gusta programar videojuegos", foto: "" },
```

- Escribe los datos **entre las comillas**. Lo que dejes vacío (`""`) aparece como
  "Por completar".
- `foto` necesita un enlace público a una imagen cuadrada. Si lo dejan vacío, la
  tarjeta muestra las iniciales con el color del integrante.
- Para agregar a alguien, copia un renglón completo (de `{` a `},`) y cámbiale los
  datos. Las tarjetas se acomodan solas.
- ¿Ya lo pegaste? Selecciona el bloque en Google Sites → ícono de lápiz (**Editar
  código**) → cambia los datos → **Siguiente** → **Insertar**.

## 5. Publicar y compartir

1. Botón **Publicar** (arriba a la derecha).
2. Escribe la dirección web, por ejemplo `mapa-semestre-1a`.
3. En **Quién puede ver mi sitio** elige quién podrá abrirlo (por ejemplo, cualquier
   persona con el enlace) y compartan la liga con su profesor o profesora.
4. Para que los demás integrantes editen: **Compartir con otros** (persona con +) y
   agreguen sus correos como **Editores**.
5. *(Opcional)* Si compran un dominio, Google Sites permite conectarlo en
   **Configuración → Dominios personalizados**.

---

## Qué hace cada bloque

| Bloque | Qué incluye |
|---|---|
| Portada | Título, terminal animada con las 10 materias y tarjetas de resumen. |
| Tu día | Cuenta regresiva a la próxima evaluación de Física y **temporizador de estudio** (25·5, 50·10 o 15·3, con sonido al terminar; el agua se calma mientras estudias). |
| Materias | Las 10 materias con sus unidades y filtro por área. |
| Semana | En qué semana del ciclo vamos, las 18 semanas y lo que toca en Física. |
| Cada materia | Pestañas por unidad, **modo repaso** (círculo junto a cada tema), **Mis notas** (se guardan solas y se pueden copiar o descargar), y en Física el calendario y la distribución de puntos. |
| Calendario | Las 18 semanas, evaluaciones, filtros por unidad o evaluaciones, «Ir a esta semana» y botón para agregar el ciclo a Google Calendar u Outlook. |
| Equipo | Tarjetas de los integrantes que se transforman al pasar el cursor o tocarlas. |

## Preguntas frecuentes

**El cuadro muestra una barra para desplazarse.** Hazlo más alto arrastrando su borde
inferior.

**En el celular algunos bloques se desplazan por dentro.** Es normal: Google Sites
mantiene la misma altura del cuadro en todos los dispositivos y en pantallas angostas
el contenido ocupa más espacio.

**¿Se guarda lo que marco o escribo?** Sí, en el navegador de cada persona: el repaso
y las notas de una materia se quedan en el bloque de esa materia. Cada bloque guarda
sus datos por separado; por eso la portada no muestra el avance de las 10 materias
juntas como en el sitio web completo.

**"¿En qué semana vamos?" muestra otra semana.** Se calcula con la fecha del
dispositivo, usando el calendario del ciclo 2026B (17 de agosto al 18 de diciembre).

**Un botón de copiar o descargar no hace nada.** Algunos navegadores bloquean copiar o
descargar dentro de los bloques de Google Sites. En ese caso selecciona el texto y
cópialo a mano. El archivo del calendario también está en la carpeta del proyecto:
`assets/calendario-2026b.ics`.

**Quiero cambiar un texto de una materia.** Lo más limpio: editen `src/contenido.py`,
ejecuten `python3 src/build.py` y vuelvan a pegar el bloque de esa materia (lápiz →
**Editar código**). También se puede buscar el texto directamente en el código del
bloque y cambiarlo ahí.

**¿Por qué en algunos navegadores los bordes del vidrio "doblan" lo que hay detrás?**
Es la refracción líquida. Funciona en Chrome y Edge; en Safari y Firefox se ve el
vidrio esmerilado normal.

**Las animaciones van lentas en una computadora vieja.** Cada bloque mueve su agua
solo mientras está a la vista y baja la calidad si el equipo no da el ritmo. Si el
dispositivo tiene activada la opción de reducir movimiento, los bloques lo respetan.
