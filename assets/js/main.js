/* Mapa del Semestre 1A · interacción y animaciones
   Funciona igual en el sitio completo y en los bloques de Google Sites
   (en esos bloques <html> lleva la clase "embed"). */
(function () {
  "use strict";

  var root = document.documentElement;
  var EMBED = root.classList.contains("embed");
  var mm = function (q) { return window.matchMedia ? window.matchMedia(q) : { matches: false }; };
  var REDUCE = mm("(prefers-reduced-motion: reduce)").matches;
  var FINE = mm("(hover: hover) and (pointer: fine)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var INICIO = new Date(2026, 7, 17); // lunes de la semana 1 del ciclo 2026B
  var DIA = 864e5;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function pad(n) { return (n < 10 ? "0" : "") + n; }

  /* Semana del ciclo para una fecha: 0 = antes de iniciar, 19 = ciclo concluido */
  function semanaDe(fecha, inicio) {
    var base = inicio || INICIO;
    var hoy = new Date(fecha.getFullYear(), fecha.getMonth(), fecha.getDate());
    var dias = Math.floor((hoy - base) / DIA);
    if (dias < 0) return 0;
    return Math.min(19, Math.floor(dias / 7) + 1);
  }
  var SEMANA = semanaDe(new Date());

  /* ---------------------------------------------------------- tema */
  function esOscuro() {
    var t = root.getAttribute("data-theme");
    if (t) return t === "dark";
    return mm("(prefers-color-scheme: dark)").matches;
  }
  $$("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var nuevo = esOscuro() ? "light" : "dark";
      root.setAttribute("data-theme", nuevo);
      try { localStorage.setItem("tema", nuevo); } catch (e) { /* sin almacenamiento */ }
    });
  });

  /* ---------------------------------------------------------- barra, navegación y "volver arriba" */
  var nav = $("[data-nav]");
  var prog = $("[data-progress]");
  var totop = $("[data-totop]");
  var pendiente = false;
  function alDesplazar() {
    pendiente = false;
    var y = window.scrollY || window.pageYOffset;
    if (nav) nav.classList.toggle("is-solid", y > 24);
    if (prog) {
      var alto = document.documentElement.scrollHeight - window.innerHeight;
      prog.style.setProperty("--p", alto > 0 ? Math.min(1, y / alto).toFixed(4) : 0);
    }
    if (totop) totop.classList.toggle("is-on", y > 700);
  }
  window.addEventListener("scroll", function () {
    if (!pendiente) { pendiente = true; requestAnimationFrame(alDesplazar); }
  }, { passive: true });
  alDesplazar();

  var menuBtn = $("[data-menu-toggle]");
  function cerrarMenu() {
    if (!nav || !menuBtn) return;
    nav.classList.remove("menu-open");
    menuBtn.setAttribute("aria-expanded", "false");
    menuBtn.setAttribute("aria-label", "Abrir menú");
    document.body.style.overflow = "";
  }
  if (nav && menuBtn) {
    menuBtn.addEventListener("click", function () {
      var abrir = !nav.classList.contains("menu-open");
      if (!abrir) return cerrarMenu();
      nav.classList.add("menu-open");
      menuBtn.setAttribute("aria-expanded", "true");
      menuBtn.setAttribute("aria-label", "Cerrar menú");
      document.body.style.overflow = "hidden";
    });
    $$("[data-menu] a").forEach(function (a) { a.addEventListener("click", cerrarMenu); });
  }

  $$("[data-dd]").forEach(function (dd) {
    var btn = $(".dd__btn", dd);
    function poner(abierto) {
      dd.classList.toggle("is-open", abierto);
      btn.setAttribute("aria-expanded", abierto ? "true" : "false");
    }
    btn.addEventListener("click", function () { poner(!dd.classList.contains("is-open")); });
    document.addEventListener("click", function (e) { if (!dd.contains(e.target)) poner(false); });
    dd.addEventListener("keydown", function (e) { if (e.key === "Escape") { poner(false); btn.focus(); } });
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") cerrarMenu(); });

  /* ---------------------------------------------------------- aparición al desplazarse */
  var observar = function () {};
  if ("IntersectionObserver" in window && !REDUCE) {
    var io = new IntersectionObserver(function (entradas) {
      var n = 0;
      entradas.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        io.unobserve(el);
        var retraso = Math.min(n++, 5) * 80;
        setTimeout(function () {
          el.classList.add("in");
          setTimeout(function () { el.classList.remove("rv", "in"); }, 1000);
        }, retraso);
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.05 });
    observar = function (el) {
      var r = el.getBoundingClientRect();
      if (r.height === 0 || r.top < window.innerHeight * 0.92) return; // ya visible: no se oculta
      el.classList.add("rv");
      io.observe(el);
    };
  }
  $$("[data-reveal]").forEach(function (el) { observar(el); });

  /* ---------------------------------------------------------- contadores */
  function contar(el) {
    var fin = +el.getAttribute("data-count");
    if (!fin || REDUCE) return;
    var t0 = null;
    function paso(t) {
      if (!t0) t0 = t;
      var p = Math.min(1, (t - t0) / 1500);
      el.textContent = Math.round(fin * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
  }
  $$("[data-count]").forEach(function (el, i) { setTimeout(function () { contar(el); }, 500 + i * 90); });

  /* ---------------------------------------------------------- terminal de la portada */
  var term = $("[data-term]");
  if (term) {
    var ini = term.getAttribute("data-inicio");
    var s = ini ? semanaDe(new Date(), new Date(ini + "T00:00:00")) : SEMANA;
    var linea = $("[data-term-progress]", term);
    if (linea) {
      var k = Math.max(0, Math.min(18, s));
      var texto = s === 0 ? "el ciclo inicia el 17 de agosto" : s > 18 ? "ciclo concluido · 18 de 18" : "semana " + s + " de 18";
      linea.innerHTML = '<span class="t-bar">' + "█".repeat(k) + '<span class="t-dim">' + "░".repeat(18 - k) + "</span></span>  " + texto;
    }
    if (!REDUCE) {
      var caja = term.closest(".term");
      var lineas = $$(".tl", term);
      var textos = lineas.map(function (l) { var t = $(".t-typed", l); return t ? t.textContent : null; });
      lineas.forEach(function (l) { var t = $(".t-typed", l); if (t) t.textContent = ""; });
      caja.classList.add("is-typing");
      var i = 0;
      var siguiente = function () {
        if (i >= lineas.length) { caja.classList.remove("is-typing"); return; }
        var l = lineas[i];
        var destino = $(".t-typed", l);
        var txt = textos[i];
        l.classList.add("on");
        i++;
        if (destino && txt) {
          var c = 0;
          (function escribir() {
            destino.textContent = txt.slice(0, ++c);
            if (c < txt.length) setTimeout(escribir, 34 + Math.random() * 46);
            else setTimeout(siguiente, 420);
          })();
        } else {
          setTimeout(siguiente, l.classList.contains("tl--out") ? 150 : 320);
        }
      };
      setTimeout(siguiente, 900);
    }
  }

  /* ---------------------------------------------------------- luz que sigue al cursor en la portada */
  var spot = $("[data-spot]");
  if (spot && FINE && !REDUCE) {
    spot.addEventListener("pointermove", function (e) {
      var r = spot.getBoundingClientRect();
      spot.style.setProperty("--mx", (e.clientX - r.left) + "px");
      spot.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  }

  /* ---------------------------------------------------------- ¿en qué semana vamos? */
  var semana = $("[data-week]");
  if (semana) {
    var datos = [];
    try { datos = JSON.parse(semana.getAttribute("data-week")); } catch (e) { datos = []; }
    var celdas = $$(".week__bar li", semana);
    var aplicar = function () {
      celdas.forEach(function (li, idx) {
        var n = idx + 1;
        li.style.setProperty("--i", idx);
        li.classList.toggle("is-past", n < SEMANA);
        li.classList.toggle("is-now", n === SEMANA);
      });
    };
    var num = $("[data-week-n]", semana);
    var txt = $("[data-week-text]", semana);
    if (num) num.textContent = SEMANA >= 1 && SEMANA <= 18 ? SEMANA : "—";
    if (txt) {
      var w = datos[SEMANA - 1];
      if (SEMANA <= 0) txt.textContent = "El ciclo inicia el lunes 17 de agosto con la semana 1.";
      else if (SEMANA > 18) txt.textContent = "El ciclo 2026B ya concluyó. ¡Gracias por acompañarnos!";
      else if (SEMANA === 18) txt.textContent = "Semana 18 · " + w.f + ": fecha límite para el registro y publicación de la evaluación continua.";
      else if (w) txt.textContent = "Semana " + SEMANA + " · " + w.f + ". En Física toca: " + w.t + ". Faltan " + (18 - SEMANA) + " semanas para el cierre del ciclo.";
    }
    var r = semana.getBoundingClientRect();
    if (!REDUCE && "IntersectionObserver" in window && r.top > window.innerHeight * 0.9) {
      celdas.forEach(function (li) { li.classList.remove("is-past", "is-now"); });
      var iow = new IntersectionObserver(function (es) {
        if (es[0].isIntersecting) { iow.disconnect(); setTimeout(aplicar, 250); }
      }, { threshold: 0.3 });
      iow.observe(semana);
    } else {
      aplicar();
    }
  }

  /* ---------------------------------------------------------- filtro de materias */
  var mgrid = $("[data-mgrid]");
  if (mgrid) {
    var botones = $$("[data-filter]");
    botones.forEach(function (b) {
      b.addEventListener("click", function () {
        var f = b.getAttribute("data-filter");
        botones.forEach(function (x) {
          x.classList.toggle("is-on", x === b);
          x.setAttribute("aria-pressed", x === b ? "true" : "false");
        });
        var visibles = 0;
        $$(".mcard", mgrid).forEach(function (c) {
          var mostrar = f === "todas" || c.getAttribute("data-area") === f;
          c.classList.remove("rv", "in");
          if (mostrar) {
            visibles++;
            c.hidden = false;
            c.classList.add("is-out");
            requestAnimationFrame(function () { requestAnimationFrame(function () { c.classList.remove("is-out"); }); });
          } else {
            c.hidden = true;
          }
        });
        mgrid.classList.toggle("is-filtered", f !== "todas");
        mgrid.style.setProperty("--cols", Math.max(1, Math.min(4, visibles)));
      });
    });
  }

  /* ---------------------------------------------------------- inclinación 3D de tarjetas */
  if (FINE && !REDUCE) {
    $$("[data-tilt]").forEach(function (c) {
      c.addEventListener("pointermove", function (e) {
        var r = c.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width;
        var y = (e.clientY - r.top) / r.height;
        c.classList.add("is-tilting");
        c.style.setProperty("--ry", ((x - 0.5) * 7).toFixed(2) + "deg");
        c.style.setProperty("--rx", ((0.5 - y) * 7).toFixed(2) + "deg");
        c.style.setProperty("--gx", (x * 100).toFixed(1) + "%");
        c.style.setProperty("--gy", (y * 100).toFixed(1) + "%");
      });
      c.addEventListener("pointerleave", function () {
        c.classList.remove("is-tilting");
        c.style.setProperty("--rx", "0deg");
        c.style.setProperty("--ry", "0deg");
      });
    });
  }

  /* ---------------------------------------------------------- equipo (datos en equipo.js) */
  var COLORES = ["#E8962E", "#3B6FF5", "#E0517A", "#17A88A", "#D9473B", "#8B4FF0", "#2E9E57", "#1C97C9"];
  var SVG = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';
  var ICO_USER = "<svg class=\"ic\" " + SVG + '><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';
  var ICO_GIRO = "<svg class=\"ic ic--sm\" " + SVG + '><path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>';

  function iniciales(nombre) {
    return nombre.trim().split(/\s+/).filter(Boolean).slice(0, 2).map(function (p) { return p.charAt(0); }).join("").toUpperCase();
  }
  function dato(valor, vacio) {
    var v = (valor || "").trim();
    return '<dd class="' + (v ? "" : "is-empty") + '">' + esc(v || vacio) + "</dd>";
  }
  function tarjeta(m, i) {
    var nombre = (m.nombre || "").trim();
    var rol = (m.rol || "").trim();
    var avatar = m.foto
      ? '<img src="' + esc(m.foto) + '" alt="Foto de ' + esc(nombre || "integrante " + (i + 1)) + '" loading="lazy">'
      : nombre ? esc(iniciales(nombre)) : ICO_USER;
    var etiqueta = "Integrante " + pad(i + 1);
    return '<article class="tcard acc" style="--acc:' + COLORES[i % COLORES.length] + '" tabindex="0" role="button" aria-pressed="false" aria-label="' + esc(etiqueta + ": " + (nombre || "sin nombre") + ". Mostrar datos") + '">' +
      '<div class="tcard__in">' +
        '<div class="tcard__face tcard__front">' +
          '<div class="tcard__avatar">' + avatar + "</div>" +
          '<span class="tcard__num">' + etiqueta + "</span>" +
          '<h3 class="tcard__name' + (nombre ? "" : " is-empty") + '">' + esc(nombre || "Nombre del integrante") + "</h3>" +
          '<p class="tcard__rol' + (rol ? "" : " is-empty") + '">' + esc(rol || "Rol en el equipo") + "</p>" +
          '<span class="tcard__hint">' + ICO_GIRO + " Ver datos</span>" +
        "</div>" +
        '<div class="tcard__face tcard__back" aria-hidden="true">' +
          "<h4>" + esc(nombre || etiqueta) + "</h4>" +
          "<dl>" +
            "<div><dt>Código de alumno</dt>" + dato(m.codigo, "Por completar") + "</div>" +
            "<div><dt>Correo institucional</dt>" + dato(m.correo, "Por completar") + "</div>" +
            "<div><dt>Frase o pasatiempo</dt>" + dato(m.frase, "Por completar") + "</div>" +
          "</dl>" +
        "</div>" +
      "</div>" +
    "</article>";
  }
  $$("[data-equipo]").forEach(function (caja) {
    var lista = window.EQUIPO;
    if (!Array.isArray(lista) || !lista.length) return;
    caja.innerHTML = lista.map(tarjeta).join("");
    $$(".tcard", caja).forEach(function (t) {
      var girar = function () {
        var on = !t.classList.contains("is-flipped");
        t.classList.toggle("is-flipped", on);
        t.setAttribute("aria-pressed", on ? "true" : "false");
        $(".tcard__back", t).setAttribute("aria-hidden", on ? "false" : "true");
      };
      t.addEventListener("click", function () { if (!FINE) girar(); });
      t.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); girar(); }
      });
    });
    $$(".tcard", caja).forEach(function (t) { observar(t); });
  });

  /* ---------------------------------------------------------- índice lateral de cada materia */
  var enlaces = $$("[data-toc]");
  if (enlaces.length && !EMBED && "IntersectionObserver" in window) {
    var porId = {};
    enlaces.forEach(function (a) { porId[a.getAttribute("data-toc")] = a; });
    enlaces[0].classList.add("is-active");
    var spy = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        enlaces.forEach(function (a) { a.classList.remove("is-active"); });
        var a = porId[en.target.id];
        if (a) a.classList.add("is-active");
      });
    }, { rootMargin: "-30% 0px -62% 0px" });
    enlaces.forEach(function (a) {
      var sec = document.getElementById(a.getAttribute("data-toc"));
      if (sec) spy.observe(sec);
    });
  }

  /* ---------------------------------------------------------- pestañas (bloques de Google Sites) */
  var tabs = $$("[data-tab]");
  if (tabs.length) {
    var cont = $(".mcontent--embed");
    cont.classList.add("tabs-ready");
    var mostrar = function (id, enfocar) {
      tabs.forEach(function (t) {
        var on = t.getAttribute("data-tab") === id;
        t.classList.toggle("is-on", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        if (on && enfocar) t.focus();
      });
      $$(".unit", cont).forEach(function (u) { u.classList.toggle("is-on", u.id === id); });
    };
    mostrar(tabs[0].getAttribute("data-tab"));
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { mostrar(t.getAttribute("data-tab")); });
      t.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        var sig = tabs[(i + d + tabs.length) % tabs.length];
        mostrar(sig.getAttribute("data-tab"), true);
      });
    });
  }

  /* ---------------------------------------------------------- calendario de Física */
  var cal = $("[data-cal]");
  if (cal) {
    $$(".cal__w", cal).forEach(function (li, idx) {
      var n = idx + 1;
      li.classList.toggle("is-past", n < SEMANA);
      li.classList.toggle("is-now", n === SEMANA);
    });
    var calBtns = $$("[data-cal-filter]");
    calBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        var u = b.getAttribute("data-cal-filter");
        calBtns.forEach(function (x) {
          x.classList.toggle("is-on", x === b);
          x.setAttribute("aria-pressed", x === b ? "true" : "false");
        });
        $$(".cal__w", cal).forEach(function (li) { li.hidden = !(u === "0" || li.getAttribute("data-u") === u); });
        cal.scrollTop = 0;
      });
    });
    /* En Google Sites la lista tiene su propio desplazamiento: se centra en la semana actual */
    var alAbrirCal = function () {
      var hoy = $(".cal__w.is-now", cal);
      if (EMBED && hoy && cal.scrollHeight > cal.clientHeight) {
        cal.scrollTop = Math.max(0, hoy.offsetTop - cal.offsetTop - cal.clientHeight / 2 + hoy.offsetHeight / 2);
      }
    };
    $$('[data-tab="calendario"]').forEach(function (t) { t.addEventListener("click", function () { setTimeout(alAbrirCal, 30); }); });
  }

  /* ---------------------------------------------------------- copiar el ejemplo de código */
  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var code = $("[data-code]", b.closest(".codeblock"));
      var texto = $$(".ln", code).map(function (l) { return l.textContent; }).join("\n");
      var etiqueta = $("span", b);
      var aviso = function (msg) {
        etiqueta.textContent = msg;
        setTimeout(function () { etiqueta.textContent = "Copiar"; }, 1800);
      };
      var seleccionar = function () {
        var rango = document.createRange();
        rango.selectNodeContents(code);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(rango);
        aviso("Seleccionado");
      };
      try {
        navigator.clipboard.writeText(texto).then(function () { aviso("Copiado"); }, seleccionar);
      } catch (e) { seleccionar(); }
    });
  });
})();
