# Publicar el sitio con su propio dominio

El sitio es **estático**: solo archivos HTML, CSS, JS e imágenes. No necesita base de
datos ni servidor propio, así que se puede publicar gratis en GitHub Pages, Netlify o
Cloudflare Pages y conectarle el dominio que compren.

> Requisito: **HTTPS** (los tres servicios lo dan gratis). Sin HTTPS no funcionan la
> app instalable, el modo sin conexión ni las notificaciones del temporizador.

## 1. Preparar el sitio con el dominio

1. Abran `src/contenido.py` y escriban el dominio en `SITIO["url"]`, con `https://` y
   sin `/` al final:

   ```python
   "url": "https://www.mapa1a.com",
   ```

2. Generen el sitio de nuevo:

   ```bash
   python3 src/build.py
   ```

   Con el dominio escrito, el generador crea además `sitemap.xml` (para Google),
   `CNAME` (para GitHub Pages), las direcciones canónicas y las vistas previas con
   dirección completa (lo que se ve al compartir el enlace en WhatsApp o redes).

3. *(Opcional)* Para que la imagen de vista previa muestre el dominio:

   ```bash
   npm i -D playwright && npx playwright install chromium
   node src/generar_imagenes.js
   ```

4. Guarden los cambios en Git y súbanlos (`git add -A`, `git commit`, `git push`).

## 2. Elegir dónde publicarlo

### Opción A · GitHub Pages (recomendada si ya usan GitHub)

1. Fusionen esta rama con `main`.
2. En GitHub: **Settings → Pages → Build and deployment → Deploy from a branch**,
   rama `main`, carpeta `/ (root)` → **Save**. (Con una cuenta gratuita el
   repositorio debe ser público.)
3. En **Custom domain** escriban el dominio (por ejemplo `www.mapa1a.com`) y guarden.
4. En el panel de su proveedor de dominio agreguen estos registros DNS:

   | Tipo | Nombre | Valor |
   |---|---|---|
   | `CNAME` | `www` | `<su-usuario>.github.io` |
   | `A` | `@` | `185.199.108.153` |
   | `A` | `@` | `185.199.109.153` |
   | `A` | `@` | `185.199.110.153` |
   | `A` | `@` | `185.199.111.153` |

5. Cuando GitHub verifique el dominio (de minutos a unas horas), activen
   **Enforce HTTPS**.

GitHub Pages ignora el archivo `_headers`; no pasa nada, el sitio funciona igual.

### Opción B · Netlify

1. En [app.netlify.com](https://app.netlify.com): **Add new site → Import an existing
   project** y elijan el repositorio (o arrastren la carpeta del proyecto a la página
   de *Deploys*).
2. *Build command*: vacío. *Publish directory*: `.` (la raíz).
3. **Domain management → Add a domain** y sigan las instrucciones de DNS que les da
   Netlify. El HTTPS se activa solo.

Netlify sí usa `_headers`: las imágenes, fuentes y scripts quedan en caché un año y
las páginas siempre se revisan, así que cada actualización se ve de inmediato.

### Opción C · Cloudflare Pages

1. En el panel de Cloudflare: **Workers & Pages → Create → Pages → Connect to Git**.
2. *Build command*: vacío. *Build output directory*: `/`.
3. **Custom domains → Set up a custom domain**. Si el dominio ya está en Cloudflare,
   el DNS se configura solo.

## 3. Comprobar que todo funciona

- Abran el sitio con `https://` y revisen que se vea el agua y que el candado del
  navegador esté activo.
- En el celular, el menú del navegador debe ofrecer **Instalar app** o **Agregar a
  pantalla de inicio**. En la computadora aparece el botón **Instalar como app** en la
  barra lateral.
- Recarguen una vez, activen el modo avión y naveguen: las páginas visitadas siguen
  funcionando.
- Peguen el enlace en un chat de WhatsApp: debe aparecer la vista previa con la foto.
- *(Opcional)* En [Google Search Console](https://search.google.com/search-console)
  agreguen el dominio y envíen `https://su-dominio/sitemap.xml` para que Google lo
  encuentre antes.

## 4. Actualizar el sitio después

1. Cambien lo que necesiten (temario en `src/contenido.py`, equipo en
   `assets/js/equipo.js`, diseño en `assets/css/estilos.css`).
2. Ejecuten `python3 src/build.py` **siempre**, aunque solo hayan cambiado el equipo:
   así cambia la huella de los archivos y nadie se queda con la versión vieja.
3. Suban los cambios. Quien ya tenga el sitio abierto verá el aviso **«Hay una versión
   nueva del sitio · Actualizar»**.
