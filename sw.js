/* Service worker del Mapa del Semestre 1A (generado por src/build.py).
   Guarda el sitio para usarlo sin conexión y lo actualiza cuando hay una versión nueva. */
const VERSION = "3513d44677";
const PRECACHE = ["./", "offline.html", "index.html", "calendario.html", "equipo.html", "materias/tutoria.html", "materias/tecnologias.html", "materias/sexualidad.html", "materias/programacion.html", "materias/ingles.html", "materias/historia.html", "materias/numerica.html", "materias/lectoescritura.html", "materias/fisica.html", "materias/socioemocional.html", "assets/css/estilos.css?v=ccfd1d49", "assets/js/main.js?v=cb2eba4b", "assets/js/datos.js?v=91c9275e", "assets/js/equipo.js?v=dbb96df0", "assets/fonts/geist.woff2", "assets/fonts/geist-mono.woff2", "assets/img/favicon.svg", "assets/img/icons/icon-192.png", "manifest.webmanifest", "assets/img/fotos/tutoria-card-600.webp", "assets/img/fotos/tecnologias-card-600.webp", "assets/img/fotos/sexualidad-card-600.webp", "assets/img/fotos/programacion-card-600.webp", "assets/img/fotos/ingles-card-600.webp", "assets/img/fotos/historia-card-600.webp", "assets/img/fotos/numerica-card-600.webp", "assets/img/fotos/lectoescritura-card-600.webp", "assets/img/fotos/fisica-card-600.webp", "assets/img/fotos/socioemocional-card-600.webp"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open("base-" + VERSION).then((c) => c.addAll(PRECACHE)));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => !k.endsWith(VERSION)).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("message", (e) => { if (e.data === "actualizar") self.skipWaiting(); });

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req)
        .then((r) => { const copia = r.clone(); caches.open("paginas-" + VERSION).then((c) => c.put(req, copia)); return r; })
        .catch(() => caches.match(req, { ignoreSearch: true }).then((r) => r || caches.match("offline.html")))
    );
    return;
  }
  e.respondWith(
    caches.match(req).then((hit) => {
      const red = fetch(req)
        .then((r) => { if (r.ok) { const copia = r.clone(); caches.open("recursos-" + VERSION).then((c) => c.put(req, copia)); } return r; })
        .catch(() => hit);
      return hit || red;
    })
  );
});
