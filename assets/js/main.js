/* Mapa del Semestre 1A · Liquid Glass
   Interacción y animaciones. Funciona igual en el sitio completo y en los
   bloques de Google Sites (ahí <html> lleva la clase "embed"). */
(function () {
  "use strict";

  var root = document.documentElement;
  var EMBED = root.classList.contains("embed");
  var mm = function (q) { return window.matchMedia ? window.matchMedia(q) : { matches: false }; };
  var REDUCE = mm("(prefers-reduced-motion: reduce)").matches;
  var FINE = mm("(hover: hover) and (pointer: fine)").matches;
  var COARSE = mm("(pointer: coarse)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var SEMANAS = window.SEMANAS || [];
  var INICIO = new Date(2026, 7, 17); // lunes de la semana 1 del ciclo 2026B
  var DIA = 864e5;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function guardar(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* sin almacenamiento */ } }
  function leer(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  function semanaDe(fecha) {
    var hoy = new Date(fecha.getFullYear(), fecha.getMonth(), fecha.getDate());
    var dias = Math.floor((hoy - INICIO) / DIA);
    if (dias < 0) return 0;
    return Math.min(19, Math.floor(dias / 7) + 1);
  }
  var SEMANA = semanaDe(new Date());

  /* =========================================================== modo calma (sin movimiento continuo) */
  var calma = REDUCE || leer("calma") === "1";
  root.classList.toggle("calma", calma);

  /* =========================================================== refracción líquida (Chromium) */
  function mapaRefraccion(size, radio, borde) {
    var c = document.createElement("canvas");
    c.width = c.height = size;
    var g = c.getContext("2d");
    var im = g.createImageData(size, size);
    var d = im.data;
    for (var y = 0; y < size; y++) {
      for (var x = 0; x < size; x++) {
        var nx = (x + 0.5) / size * 2 - 1, ny = (y + 0.5) / size * 2 - 1;
        var qx = Math.abs(nx) - (1 - radio), qy = Math.abs(ny) - (1 - radio);
        var ox = Math.max(qx, 0), oy = Math.max(qy, 0);
        var dist = Math.hypot(ox, oy) + Math.min(Math.max(qx, qy), 0) - radio;
        var t = Math.min(1, Math.max(0, 1 + dist / borde));
        t = t * t * (3 - 2 * t);
        var dx, dy;
        if (ox > 0 || oy > 0) { var l = Math.hypot(ox, oy) || 1; dx = Math.sign(nx) * ox / l; dy = Math.sign(ny) * oy / l; }
        else if (qx > qy) { dx = Math.sign(nx); dy = 0; } else { dx = 0; dy = Math.sign(ny); }
        var i = (y * size + x) * 4;
        d[i] = 128 - dx * t * 127;
        d[i + 1] = 128 - dy * t * 127;
        d[i + 2] = 128;
        d[i + 3] = 255;
      }
    }
    g.putImageData(im, 0, 0);
    return c.toDataURL();
  }
  (function () {
    var img = document.getElementById("lg-map");
    var ok = img && window.chrome && window.CSS && CSS.supports && CSS.supports("backdrop-filter", "url(#lg)") && !COARSE;
    if (!ok) return;
    img.setAttribute("href", mapaRefraccion(160, 0.5, 0.42));
    root.classList.add("lr");
  })();

  /* =========================================================== fondo líquido (WebGL) */
  var VERT = "attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}";
  var FRAG = [
    "precision mediump float;",
    "uniform vec2 r;uniform float t;uniform vec2 m;uniform float ms;uniform vec3 drop;",
    "uniform vec3 c0;uniform vec3 c1;uniform vec3 c2;uniform vec3 c3;uniform vec3 base;",
    "float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}",
    "float n(vec2 p){vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.-2.*f);",
    "return mix(mix(h(i),h(i+vec2(1.,0.)),u.x),mix(h(i+vec2(0.,1.)),h(i+vec2(1.,1.)),u.x),u.y);}",
    "float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<4;i++){v+=a*n(p);p=p*2.03+vec2(1.7,9.2);a*=.5;}return v;}",
    "void main(){",
    " vec2 uv=gl_FragCoord.xy/r;float asp=r.x/r.y;vec2 p=vec2(uv.x*asp,uv.y);",
    " vec2 mp=vec2(m.x*asp,m.y);vec2 d=p-mp;float dl=length(d);",
    " float a=ms*exp(-dl*dl*7.)*2.4;float ca=cos(a),sa=sin(a);p=mp+mat2(ca,-sa,sa,ca)*d;",
    " float dt=t-drop.z;",
    " if(dt>0.&&dt<3.){vec2 dp=vec2(drop.x*asp,drop.y);vec2 dd=p-dp;float rr=length(dd);",
    "  float w=sin(rr*36.-dt*9.)*exp(-rr*3.2)*exp(-dt*1.3);p+=dd/(rr+.0001)*w*.04;}",
    " float tt=t*.045;",
    " vec2 q=vec2(fbm(p*1.3+vec2(0.,tt)),fbm(p*1.3+vec2(5.2,-tt)));",
    " vec2 w2=vec2(fbm(p*1.1+1.8*q+vec2(1.7,9.2)+tt*1.2),fbm(p*1.1+1.8*q+vec2(8.3,2.8)-tt));",
    " float f=fbm(p*1.2+2.2*w2);",
    " vec3 col=base;",
    " col=mix(col,c0,smoothstep(.34,.86,f));",
    " col=mix(col,c1,smoothstep(.45,.95,w2.x)*.85);",
    " col=mix(col,c2,smoothstep(.5,.95,q.y)*.7);",
    " col=mix(col,c3,smoothstep(.5,.9,w2.y*f*1.6)*.55);",
    " col+=smoothstep(.6,.72,fbm(p*3.+w2*2.+tt*2.))*.07;",
    " col*=.42+.58*smoothstep(1.25,.2,length(uv-vec2(.5,.45))*1.3);",
    " gl_FragColor=vec4(col,1.);",
    "}"
  ].join("\n");

  function hexVec(hex, k) {
    var h = hex.replace("#", "");
    return [parseInt(h.substr(0, 2), 16) / 255 * k, parseInt(h.substr(2, 2), 16) / 255 * k, parseInt(h.substr(4, 2), 16) / 255 * k];
  }

  var liquido = (function () {
    var canvas = $("[data-liquid]");
    if (!canvas) return null;
    var capa = canvas.closest(".bg");
    var conFoto = capa && capa.classList.contains("bg--photo");
    var gl = null;
    try { gl = canvas.getContext("webgl", { antialias: false, alpha: false, depth: false, powerPreference: "low-power" }); } catch (e) { gl = null; }
    if (!gl) { if (capa) capa.classList.add("no-gl"); return null; }
    function shader(tipo, src) {
      var s = gl.createShader(tipo);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null;
    }
    var vs = shader(gl.VERTEX_SHADER, VERT), fs = shader(gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) { if (capa) capa.classList.add("no-gl"); return null; }
    var prog = gl.createProgram();
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { if (capa) capa.classList.add("no-gl"); return null; }
    gl.useProgram(prog);
    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, "a");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var U = {};
    ["r", "t", "m", "ms", "drop", "c0", "c1", "c2", "c3", "base"].forEach(function (k) { U[k] = gl.getUniformLocation(prog, k); });
    var colores = (canvas.getAttribute("data-colors") || "#3b5bff,#8b4ff0,#ff9a3d,#17a88a").split(",");
    var brillo = conFoto ? 1 : 0.78;
    ["c0", "c1", "c2", "c3"].forEach(function (k, i) { gl.uniform3fv(U[k], hexVec(colores[i % colores.length], brillo)); });
    gl.uniform3fv(U.base, conFoto ? [0, 0, 0] : hexVec("#070a14", 1));
    gl.uniform3fv(U.drop, [0.5, 0.5, -10]);

    var escala = COARSE ? 0.26 : 0.4;
    function medir() {
      var w = Math.max(2, Math.round(window.innerWidth * escala));
      var h = Math.max(2, Math.round(window.innerHeight * escala));
      if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
      gl.viewport(0, 0, w, h);
      gl.uniform2f(U.r, w, h);
    }
    medir();
    window.addEventListener("resize", function () { medir(); if (!corriendo) dibujar(performance.now()); });

    var t0 = performance.now();
    var mx = 0.5, my = 0.55, tx = 0.5, ty = 0.55, fuerza = 0, ultimoMov = 0, previo = null;
    window.addEventListener("pointermove", function (e) {
      var x = e.clientX / window.innerWidth, y = 1 - e.clientY / window.innerHeight;
      var ahora = performance.now();
      if (previo) {
        var dt = Math.max(16, ahora - previo.t) / 1000;
        var v = Math.hypot(x - previo.x, y - previo.y) / dt;
        fuerza = Math.min(1.5, fuerza + v * 0.06);
      }
      previo = { x: x, y: y, t: ahora };
      tx = x; ty = y; ultimoMov = ahora;
    }, { passive: true });
    window.addEventListener("pointerdown", function (e) {
      if (e.target.closest("input, textarea")) return;
      gl.uniform3f(U.drop, e.clientX / window.innerWidth, 1 - e.clientY / window.innerHeight, (performance.now() - t0) / 1000);
    }, { passive: true });

    function dibujar(ahora) {
      mx += (tx - mx) * 0.08;
      my += (ty - my) * 0.08;
      fuerza *= 0.955;
      gl.uniform1f(U.t, (ahora - t0) / 1000);
      gl.uniform2f(U.m, mx, my);
      gl.uniform1f(U.ms, fuerza);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }
    var corriendo = false, ultimo = 0, intervalo = COARSE ? 50 : 33;
    function bucle(ahora) {
      if (!corriendo) return;
      if (ahora - ultimo >= intervalo) { ultimo = ahora; dibujar(ahora); }
      requestAnimationFrame(bucle);
    }
    return {
      iniciar: function () { if (corriendo) return; corriendo = true; requestAnimationFrame(bucle); },
      detener: function () { corriendo = false; dibujar(performance.now()); }
    };
  })();
  if (liquido) { if (calma) liquido.detener(); else liquido.iniciar(); }

  /* el botón "Efecto líquido" alterna el modo calma */
  $$("[data-calma]").forEach(function (b) {
    b.setAttribute("aria-pressed", calma ? "false" : "true");
    b.addEventListener("click", function () {
      calma = !calma;
      root.classList.toggle("calma", calma);
      guardar("calma", calma ? "1" : "0");
      $$("[data-calma]").forEach(function (x) { x.setAttribute("aria-pressed", calma ? "false" : "true"); });
      if (liquido) { if (calma) liquido.detener(); else liquido.iniciar(); }
    });
  });

  /* =========================================================== foto con paralaje + brillo del vidrio */
  var foto = $(".bg__photo");
  var actual = null;
  if (FINE) {
    window.addEventListener("pointermove", function (e) {
      if (foto && !calma) {
        foto.style.setProperty("--px", ((0.5 - e.clientX / window.innerWidth) * 26).toFixed(1) + "px");
        foto.style.setProperty("--py", ((0.5 - e.clientY / window.innerHeight) * 18).toFixed(1) + "px");
      }
      var g = e.target.closest && e.target.closest(".glass");
      if (actual && actual !== g) actual.style.removeProperty("--spec");
      actual = g;
      if (g) {
        var r = g.getBoundingClientRect();
        g.style.setProperty("--mx", (e.clientX - r.left).toFixed(0) + "px");
        g.style.setProperty("--my", (e.clientY - r.top).toFixed(0) + "px");
        g.style.setProperty("--spec", "1");
      }
    }, { passive: true });
  }

  /* =========================================================== tarjetas gelatina (inclinación con resorte) */
  if (FINE && !REDUCE) {
    $$("[data-jelly]").forEach(function (c) {
      c.addEventListener("pointermove", function (e) {
        var r = c.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        c.style.setProperty("--ry", ((x - 0.5) * 7).toFixed(2) + "deg");
        c.style.setProperty("--rx", ((0.5 - y) * 7).toFixed(2) + "deg");
        c.style.setProperty("--sc", "1.015");
      });
      c.addEventListener("pointerleave", function () {
        c.style.setProperty("--rx", "0deg");
        c.style.setProperty("--ry", "0deg");
        c.style.setProperty("--sc", "1");
      });
    });
  }

  /* =========================================================== gota (onda al tocar) */
  var CON_ONDA = "[data-ripple], .seg__btn, .side__item, .dock__item, .mcard, .tcard, .pill, .code__copy, .side__motion";
  document.addEventListener("pointerdown", function (e) {
    var el = e.target.closest && e.target.closest(CON_ONDA);
    if (!el || REDUCE) return;
    var r = el.getBoundingClientRect();
    var s = document.createElement("span");
    s.className = "ripple";
    s.style.left = (e.clientX - r.left) + "px";
    s.style.top = (e.clientY - r.top) + "px";
    s.style.setProperty("--rs", (Math.max(r.width, r.height) / 24 * 2.4).toFixed(1));
    el.appendChild(s);
    setTimeout(function () { s.remove(); }, 950);
    if (el.matches(".btn, .seg__btn, .dock__item, .pill")) {
      el.classList.remove("is-jelly");
      void el.offsetWidth;
      el.classList.add("is-jelly");
    }
  });

  /* =========================================================== lente líquido (indicador con resortes) */
  var LENTES = [];
  function lente(cont) {
    var lens = $(":scope > .lens", cont);
    if (!lens) return null;
    var vertical = cont.getAttribute("data-lens") === "v";
    var conHover = cont.hasAttribute("data-hover") && FINE;
    var items = function () { return $$(":scope > [data-li]", cont); };
    var activo = items().filter(function (i) { return i.classList.contains("is-active"); })[0] || null;
    var objetivo = activo;
    var E = { l: { x: 0, v: 0 }, r: { x: 0, v: 0 }, t: { x: 0, v: 0 }, b: { x: 0, v: 0 } };
    var corriendo = false, ultimo = 0, listo = false;
    function caja(el) { return { l: el.offsetLeft, t: el.offsetTop, r: el.offsetLeft + el.offsetWidth, b: el.offsetTop + el.offsetHeight }; }
    function pintar() {
      lens.style.transform = "translate(" + E.l.x.toFixed(2) + "px," + E.t.x.toFixed(2) + "px)";
      lens.style.width = Math.max(0, E.r.x - E.l.x).toFixed(2) + "px";
      lens.style.height = Math.max(0, E.b.x - E.t.x).toFixed(2) + "px";
    }
    function colorear() {
      if (!objetivo) return;
      var c = getComputedStyle(objetivo).getPropertyValue("--acc").trim();
      if (c) lens.style.setProperty("--lens-acc", c);
    }
    function fijar() {
      if (!objetivo || !objetivo.offsetWidth) { lens.classList.remove("is-ready"); return; }
      var k = caja(objetivo);
      E.l.x = k.l; E.r.x = k.r; E.t.x = k.t; E.b.x = k.b;
      E.l.v = E.r.v = E.t.v = E.b.v = 0;
      pintar();
      colorear();
      lens.classList.add("is-ready");
    }
    function paso(ts) {
      if (!objetivo) { corriendo = false; return; }
      var dt = ultimo ? Math.min(0.034, (ts - ultimo) / 1000) : 0.016;
      ultimo = ts;
      var k = caja(objetivo);
      var dir = vertical ? Math.sign((k.t + k.b) - (E.t.x + E.b.x)) : Math.sign((k.l + k.r) - (E.l.x + E.r.x));
      var rapido = 620, lento = 190;
      var rig = vertical
        ? { t: dir < 0 ? rapido : lento, b: dir > 0 ? rapido : lento, l: 420, r: 420 }
        : { l: dir < 0 ? rapido : lento, r: dir > 0 ? rapido : lento, t: 420, b: 420 };
      var quieto = true;
      ["l", "r", "t", "b"].forEach(function (lado) {
        var s = E[lado], kk = rig[lado], c = 2 * Math.sqrt(kk) * 0.72;
        s.v += ((k[lado] - s.x) * kk - s.v * c) * dt;
        s.x += s.v * dt;
        if (Math.abs(k[lado] - s.x) > 0.25 || Math.abs(s.v) > 0.25) quieto = false;
      });
      pintar();
      if (quieto) { corriendo = false; ultimo = 0; fijar(); return; }
      requestAnimationFrame(paso);
    }
    function ir(el) {
      objetivo = el;
      if (!el) return;
      colorear();
      if (REDUCE || !listo || !lens.classList.contains("is-ready")) { fijar(); return; }
      if (!corriendo) { corriendo = true; ultimo = 0; requestAnimationFrame(paso); }
    }
    if (conHover) {
      items().forEach(function (it) { it.addEventListener("pointerenter", function () { ir(it); }); });
      cont.addEventListener("pointerleave", function () { ir(activo); });
    }
    var api = {
      cont: cont,
      activar: function (el) {
        items().forEach(function (i) { i.classList.toggle("is-active", i === el); });
        activo = el;
        ir(el);
      },
      fijar: function () { objetivo = activo; fijar(); }
    };
    fijar();
    listo = true;
    LENTES.push(api);
    return api;
  }
  $$("[data-lens]").forEach(lente);
  function lenteDe(cont) { return LENTES.filter(function (l) { return l.cont === cont; })[0]; }
  function refijar() { LENTES.forEach(function (l) { l.fijar(); }); }
  window.addEventListener("resize", refijar);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(refijar);
  window.addEventListener("load", refijar);

  /* =========================================================== cajón lateral (celular) */
  var scrim = $("[data-drawer-close]");
  var side = $("[data-drawer]");
  function abrirCajon() {
    if (!side) return;
    if (scrim) scrim.hidden = false;
    requestAnimationFrame(function () { root.classList.add("drawer-open"); });
    $$("[data-drawer-open]").forEach(function (b) { b.setAttribute("aria-expanded", "true"); });
    setTimeout(function () { var a = $(".side__item.is-active", side) || $(".side__item", side); if (a) a.focus({ preventScroll: true }); refijar(); }, 120);
  }
  function cerrarCajon() {
    root.classList.remove("drawer-open");
    $$("[data-drawer-open]").forEach(function (b) { b.setAttribute("aria-expanded", "false"); });
    setTimeout(function () { if (scrim && !root.classList.contains("drawer-open")) scrim.hidden = true; }, 450);
  }
  $$("[data-drawer-open]").forEach(function (b) { b.addEventListener("click", abrirCajon); });
  if (scrim) scrim.addEventListener("click", cerrarCajon);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") cerrarCajon(); });
  if (side) $$("a", side).forEach(function (a) { a.addEventListener("click", cerrarCajon); });

  /* =========================================================== volver arriba */
  var totop = $("[data-totop]");
  if (totop) {
    var vista = false;
    window.addEventListener("scroll", function () {
      var on = (window.scrollY || window.pageYOffset) > 700;
      if (on !== vista) { vista = on; totop.classList.toggle("is-on", on); }
    }, { passive: true });
  }

  /* =========================================================== aparición líquida (desenfoque → nitidez) */
  var observar = function () {};
  if ("IntersectionObserver" in window && !REDUCE) {
    var io = new IntersectionObserver(function (entradas) {
      var n = 0;
      entradas.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        io.unobserve(el);
        var retraso = Math.min(n++, 6) * 80;
        setTimeout(function () {
          el.classList.add("in");
          setTimeout(function () { el.classList.remove("rv", "in"); }, 1150);
        }, retraso);
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.04 });
    observar = function (el) {
      var r = el.getBoundingClientRect();
      if (r.height === 0 || r.top < window.innerHeight * 0.92) return;
      el.classList.add("rv");
      io.observe(el);
    };
  }
  $$("[data-reveal]").forEach(function (el) { observar(el); });

  /* =========================================================== contadores */
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
  if ("IntersectionObserver" in window) {
    var ioc = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { ioc.unobserve(en.target); contar(en.target); } });
    }, { threshold: 0.4 });
    $$("[data-count]").forEach(function (el) { ioc.observe(el); });
  }
  $$(".bars .bar").forEach(function (b, i) { b.style.setProperty("--i", i); });

  /* =========================================================== saludo con la fecha */
  $$("[data-hoy]").forEach(function (el) {
    var hoy = new Date();
    var h = hoy.getHours();
    var saludo = h < 12 ? "Buenos días" : h < 19 ? "Buenas tardes" : "Buenas noches";
    var fecha = "";
    try { fecha = new Intl.DateTimeFormat("es-MX", { weekday: "long", day: "numeric", month: "long" }).format(hoy); } catch (e) { fecha = hoy.toLocaleDateString(); }
    el.textContent = saludo + ", 1A · " + fecha.charAt(0).toUpperCase() + fecha.slice(1);
  });

  /* =========================================================== terminal de la portada */
  var term = $("[data-term]");
  if (term) {
    var linea = $("[data-term-progress]", term);
    if (linea) {
      var k = Math.max(0, Math.min(18, SEMANA));
      var texto = SEMANA === 0 ? "el ciclo inicia el 17 de agosto" : SEMANA > 18 ? "ciclo concluido · 18 de 18" : "semana " + SEMANA + " de 18";
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
        var l = lineas[i], destino = $(".t-typed", l), txt = textos[i];
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

  /* =========================================================== semana del ciclo */
  (function () {
    var S = SEMANA;
    var w = SEMANAS[Math.min(Math.max(S, 1), 18) - 1];
    $$("[data-week-n]").forEach(function (el) { el.textContent = S >= 1 && S <= 18 ? S : "—"; });
    if (w) $$("[data-week-dates]").forEach(function (el) { el.textContent = w.f; });
    var p = Math.min(Math.max(S, 0), 18) / 18;
    $$("[data-gauge]").forEach(function (g) {
      g.classList.toggle("is-high", p > 0.56);
      if (REDUCE) { g.style.setProperty("--p", p.toFixed(3)); return; }
      g.style.setProperty("--p", "0");
      setTimeout(function () { g.style.setProperty("--p", p.toFixed(3)); }, 350);
    });
    $$("[data-ticks]").forEach(function (t) {
      $$(".tick", t).forEach(function (x, i) { x.classList.toggle("is-past", i + 1 < S); x.classList.toggle("is-now", i + 1 === S); });
    });
    $$("[data-weekbar]").forEach(function (bar) {
      var celdas = $$("li", bar);
      var aplicar = function () {
        celdas.forEach(function (li, i) {
          li.style.setProperty("--i", i);
          li.classList.toggle("is-past", i + 1 < S);
          li.classList.toggle("is-now", i + 1 === S);
        });
      };
      if (!REDUCE && "IntersectionObserver" in window) {
        celdas.forEach(function (li) { li.classList.remove("is-past", "is-now"); });
        var iow = new IntersectionObserver(function (es) {
          if (es[0].isIntersecting) { iow.disconnect(); setTimeout(aplicar, 250); }
        }, { threshold: 0.3 });
        iow.observe(bar);
      } else aplicar();
    });
    $$("[data-week-done]").forEach(function (el) { el.textContent = Math.max(0, Math.min(S, 19) - 1); });
    $$("[data-week-left]").forEach(function (el) { el.textContent = S >= 1 ? Math.max(0, 18 - S) : 18; });
    $$("[data-week-pct]").forEach(function (el) { el.textContent = Math.round(p * 100) + " %"; });
    $$("[data-week-text]").forEach(function (el) {
      if (S <= 0) el.textContent = "El ciclo inicia el lunes 17 de agosto con la semana 1.";
      else if (S > 18) el.textContent = "El ciclo 2026B ya concluyó. ¡Gracias por acompañarnos!";
      else if (S === 18) el.textContent = "Semana 18 · " + w.f + ": fecha límite para el registro y publicación de la evaluación continua.";
      else el.textContent = "Semana " + S + " · " + w.f + ". Faltan " + (18 - S) + " semanas para el cierre del ciclo.";
    });
    $$("[data-upnext]").forEach(function (ol) {
      if (!SEMANAS.length) return;
      var desde = S >= 1 ? Math.max(1, Math.min(S, 16)) : 1;
      ol.innerHTML = SEMANAS.slice(desde - 1, desde + 2).map(function (x) {
        var etiqueta = x.s === S ? "Esta semana" : "Semana " + x.s;
        return '<li class="' + (x.s === S ? "is-now" : "") + '"><span class="upnext__k">' + etiqueta + " · " + esc(x.f) + "</span><b>" +
          esc(x.t.join(" · ")) + "</b>" + (x.p ? "<small>" + esc(x.p) + "</small>" : "") + "</li>";
      }).join("");
    });
  })();

  /* =========================================================== filtro de materias */
  var mgrid = $("[data-mgrid]");
  var filtros = $("[data-filters]");
  if (mgrid && filtros) {
    var lf = lenteDe(filtros);
    $$("[data-filter]", filtros).forEach(function (b) {
      b.addEventListener("click", function () {
        var f = b.getAttribute("data-filter");
        if (lf) lf.activar(b);
        $$("[data-filter]", filtros).forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        var visibles = [];
        $$(".mcard", mgrid).forEach(function (c) {
          var mostrar = f === "todas" || c.getAttribute("data-area") === f;
          c.classList.remove("rv", "in");
          c.hidden = !mostrar;
          if (mostrar) visibles.push(c);
        });
        mgrid.classList.toggle("is-filtered", f !== "todas");
        mgrid.style.gridTemplateColumns = "";
        if (f !== "todas") {
          var cols = getComputedStyle(mgrid).gridTemplateColumns.split(" ").length;
          if (visibles.length < cols) mgrid.style.gridTemplateColumns = "repeat(" + visibles.length + ", minmax(0, 1fr))";
        }
        if (!REDUCE && mgrid.animate) {
          visibles.forEach(function (c, i) {
            c.animate([
              { opacity: 0, filter: "blur(14px)", transform: "translateY(18px) scale(.96)" },
              { opacity: 1, filter: "blur(0px)", transform: "none" }
            ], { duration: 650, delay: i * 55, easing: "cubic-bezier(.22,.8,.24,1)", fill: "backwards" });
          });
        }
      });
    });
  }

  /* =========================================================== equipo (datos en equipo.js) */
  var COLORES = ["#E8962E", "#3B6FF5", "#E0517A", "#17A88A", "#D9473B", "#8B4FF0", "#2E9E57", "#1C97C9"];
  var SVG = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';
  var ICO_USER = '<svg class="ic" ' + SVG + '><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';
  var ICO_GIRO = '<svg class="ic ic--xs" ' + SVG + '><path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>';
  function iniciales(nombre) {
    return nombre.trim().split(/\s+/).filter(Boolean).slice(0, 2).map(function (p) { return p.charAt(0); }).join("").toUpperCase();
  }
  function dato(valor, vacio) {
    var v = (valor || "").trim();
    return '<dd class="' + (v ? "" : "is-empty") + '">' + esc(v || vacio) + "</dd>";
  }
  function tarjeta(m, i) {
    var nombre = (m.nombre || "").trim(), rol = (m.rol || "").trim();
    var base = root.getAttribute("data-base") || "";
    var foto = m.foto ? (/^(https?:|data:|\/)/.test(m.foto) ? m.foto : base + m.foto) : "";
    var orb = foto ? '<img src="' + esc(foto) + '" alt="Foto de ' + esc(nombre || "integrante " + (i + 1)) + '" loading="lazy">' : nombre ? esc(iniciales(nombre)) : ICO_USER;
    var etiqueta = "Integrante " + pad(i + 1);
    return '<article class="tcard glass acc" style="--acc:' + COLORES[i % COLORES.length] + '" tabindex="0" role="button" aria-pressed="false" data-jelly ' +
      'aria-label="' + esc(etiqueta + ": " + (nombre || "sin nombre") + ". Mostrar datos") + '">' +
      '<div class="tcard__front">' +
        '<span class="tcard__orb">' + orb + "</span>" +
        '<span class="tcard__num">' + etiqueta + "</span>" +
        '<h3 class="tcard__name' + (nombre ? "" : " is-empty") + '">' + esc(nombre || "Nombre del integrante") + "</h3>" +
        '<p class="tcard__rol' + (rol ? "" : " is-empty") + '">' + esc(rol || "Rol en el equipo") + "</p>" +
        '<span class="tcard__hint">' + ICO_GIRO + " Ver datos</span>" +
      "</div>" +
      '<div class="tcard__back" aria-hidden="true">' +
        "<h4>" + esc(nombre || etiqueta) + "</h4>" +
        "<dl>" +
          "<div><dt>Código de alumno</dt>" + dato(m.codigo, "Por completar") + "</div>" +
          "<div><dt>Correo institucional</dt>" + dato(m.correo, "Por completar") + "</div>" +
          "<div><dt>Frase o pasatiempo</dt>" + dato(m.frase, "Por completar") + "</div>" +
        "</dl>" +
      "</div>" +
    "</article>";
  }
  $$("[data-equipo]").forEach(function (caja) {
    var lista = window.EQUIPO;
    if (!Array.isArray(lista) || !lista.length) return;
    caja.innerHTML = lista.map(tarjeta).join("");
    var n = lista.length;
    caja.style.setProperty("--n-row", n <= 5 ? n : n === 6 ? 3 : n <= 8 ? 4 : 5);
    $$(".tcard", caja).forEach(function (t) {
      var girar = function () {
        var on = !t.classList.contains("is-open");
        t.classList.toggle("is-open", on);
        t.setAttribute("aria-pressed", on ? "true" : "false");
        $(".tcard__back", t).setAttribute("aria-hidden", on ? "false" : "true");
      };
      t.addEventListener("click", function () { if (!FINE) girar(); });
      t.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); girar(); } });
      if (FINE && !REDUCE) {
        t.addEventListener("pointermove", function (e) {
          var r = t.getBoundingClientRect();
          t.style.setProperty("--ry", (((e.clientX - r.left) / r.width - 0.5) * 8).toFixed(2) + "deg");
          t.style.setProperty("--rx", ((0.5 - (e.clientY - r.top) / r.height) * 8).toFixed(2) + "deg");
          t.style.setProperty("--sc", "1.02");
        });
        t.addEventListener("pointerleave", function () { t.style.setProperty("--rx", "0deg"); t.style.setProperty("--ry", "0deg"); t.style.setProperty("--sc", "1"); });
      }
      observar(t);
    });
  });

  /* =========================================================== pestañas de cada materia */
  var tabsCont = $("[data-tabs]");
  var paneles = $("[data-panels]");
  var mostrarPanel = function () {};
  if (tabsCont && paneles) {
    var lt = lenteDe(tabsCont);
    var botones = $$("[data-tab]", tabsCont);
    paneles.classList.add("tabs-ready");
    mostrarPanel = function (id, enfocar) {
      var b = botones.filter(function (x) { return x.getAttribute("data-tab") === id; })[0];
      if (!b) return;
      botones.forEach(function (x) {
        var on = x === b;
        x.setAttribute("aria-selected", on ? "true" : "false");
        x.tabIndex = on ? 0 : -1;
      });
      if (lt) lt.activar(b);
      $$(":scope > [data-panel]", paneles).forEach(function (p) { p.classList.toggle("is-on", p.id === id); });
      if (enfocar) b.focus();
      var izq = b.offsetLeft - tabsCont.clientWidth / 2 + b.offsetWidth / 2;
      tabsCont.scrollTo({ left: Math.max(0, izq), behavior: REDUCE ? "auto" : "smooth" });
      if (id === "calendario") setTimeout(centrarSemana, 40);
    };
    mostrarPanel(botones[0].getAttribute("data-tab"));
    botones.forEach(function (b, i) {
      b.addEventListener("click", function () {
        var id = b.getAttribute("data-tab");
        mostrarPanel(id);
        if (!EMBED && history.replaceState) history.replaceState(null, "", "#" + id);
      });
      b.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        var sig = botones[(i + d + botones.length) % botones.length];
        mostrarPanel(sig.getAttribute("data-tab"), true);
      });
    });
  }

  /* abre la pestaña y resalta el tema que pide la dirección (#u2, #t2-5…) */
  function abrirHash() {
    if (EMBED) return;
    var id = decodeURIComponent((location.hash || "").slice(1));
    if (!id) return;
    var el = document.getElementById(id);
    if (!el) return;
    var panel = el.closest("[data-panel]");
    if (panel) mostrarPanel(panel.id);
    if (panel && el !== panel) {
      setTimeout(function () {
        el.scrollIntoView({ block: "center", behavior: REDUCE ? "auto" : "smooth" });
        el.classList.remove("is-hit");
        void el.offsetWidth;
        el.classList.add("is-hit");
      }, 160);
    } else if (panel) {
      var barra = $(".tabsbar");
      if (barra) setTimeout(function () { barra.scrollIntoView({ block: "start", behavior: REDUCE ? "auto" : "smooth" }); }, 60);
    }
  }
  abrirHash();
  window.addEventListener("hashchange", abrirHash);

  /* =========================================================== calendario de Física */
  var cal = $("[data-cal]");
  function centrarSemana() {
    var hoy = cal && $(".cal__w.is-now", cal);
    if (EMBED && hoy && cal.scrollHeight > cal.clientHeight) {
      cal.scrollTop = Math.max(0, hoy.offsetTop - cal.offsetTop - cal.clientHeight / 2 + hoy.offsetHeight / 2);
    }
  }
  if (cal) {
    $$(".cal__w", cal).forEach(function (li, idx) {
      li.classList.toggle("is-past", idx + 1 < SEMANA);
      li.classList.toggle("is-now", idx + 1 === SEMANA);
    });
    var segCal = cal.parentNode.querySelector("[data-lens]");
    var lc = segCal && lenteDe(segCal);
    $$("[data-cal-filter]").forEach(function (b) {
      b.addEventListener("click", function () {
        var u = b.getAttribute("data-cal-filter");
        if (lc) lc.activar(b);
        $$("[data-cal-filter]").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        $$(".cal__w", cal).forEach(function (li) { li.hidden = !(u === "0" || li.getAttribute("data-u") === u); });
        cal.scrollTop = 0;
      });
    });
  }

  /* =========================================================== copiar el ejemplo de código */
  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var code = $("[data-code]", b.closest(".codeblock"));
      var texto = $$(".ln", code).map(function (l) { return l.textContent; }).join("\n");
      var etiqueta = $("span", b);
      var aviso = function (msg) { etiqueta.textContent = msg; setTimeout(function () { etiqueta.textContent = "Copiar"; }, 1800); };
      var seleccionar = function () {
        var rango = document.createRange();
        rango.selectNodeContents(code);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(rango);
        aviso("Seleccionado");
      };
      try { navigator.clipboard.writeText(texto).then(function () { aviso("Copiado"); }, seleccionar); } catch (e) { seleccionar(); }
    });
  });

  /* =========================================================== buscador de temas */
  var buscador = $("[data-search]");
  var INDICE = window.INDICE || [];
  if (buscador && INDICE.length) {
    var input = $("input", buscador);
    var caja2 = $(".search__res", buscador);
    var base = buscador.getAttribute("data-base") || "";
    var sinAcento = function (s) { return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
    INDICE.forEach(function (it) { it.n = sinAcento(it.t + " " + it.m); it.nt = sinAcento(it.t); });
    var sel = -1, resultados = [];
    var resaltar = function (texto, terminos) {
      var chars = Array.from(texto);
      var norm = chars.map(function (c) { return sinAcento(c) || c; });
      var marca = new Array(chars.length).fill(false);
      var plano = norm.join("");
      var mapa = [];
      norm.forEach(function (s, i) { for (var k = 0; k < s.length; k++) mapa.push(i); });
      terminos.forEach(function (t) {
        var desde = 0, pos;
        while (t && (pos = plano.indexOf(t, desde)) !== -1) {
          for (var k = pos; k < pos + t.length; k++) marca[mapa[k]] = true;
          desde = pos + t.length;
        }
      });
      var out = "", abierto = false;
      chars.forEach(function (c, i) {
        if (marca[i] && !abierto) { out += "<mark>"; abierto = true; }
        if (!marca[i] && abierto) { out += "</mark>"; abierto = false; }
        out += esc(c);
      });
      return out + (abierto ? "</mark>" : "");
    };
    var pintarRes = function () {
      $$(".res", caja2).forEach(function (r, i) { r.setAttribute("aria-selected", i === sel ? "true" : "false"); });
      var r = $$(".res", caja2)[sel];
      if (r) { r.scrollIntoView({ block: "nearest" }); input.setAttribute("aria-activedescendant", r.id); }
    };
    var buscar = function () {
      var q = input.value.trim();
      if (q.length < 2) { caja2.hidden = true; input.setAttribute("aria-expanded", "false"); return; }
      var terminos = sinAcento(q).split(/\s+/).filter(Boolean);
      resultados = INDICE.filter(function (it) { return terminos.every(function (t) { return it.n.indexOf(t) !== -1; }); })
        .map(function (it) {
          var p = 0;
          if (it.nt.indexOf(terminos[0]) === 0) p -= 3;
          if (it.m === "Materia") p -= 2;
          p += it.t.length / 200;
          return { it: it, p: p };
        })
        .sort(function (a, b) { return a.p - b.p; }).slice(0, 8).map(function (x) { return x.it; });
      sel = resultados.length ? 0 : -1;
      caja2.innerHTML = resultados.length
        ? resultados.map(function (it, i) {
          return '<a class="res" role="option" id="res-' + i + '" href="' + esc(base + it.h) + '" style="--c:' + it.c + '"><i></i><span><b>' +
            resaltar(it.t, terminos) + "</b><small>" + esc(it.m) + "</small></span></a>";
        }).join("")
        : '<p class="res-empty">No encontramos «' + esc(q) + '». Prueba con otra palabra.</p>';
      caja2.hidden = false;
      input.setAttribute("aria-expanded", "true");
      pintarRes();
    };
    input.addEventListener("input", buscar);
    input.addEventListener("focus", function () { if (input.value.trim().length >= 2) buscar(); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" && resultados.length) { e.preventDefault(); sel = (sel + 1) % resultados.length; pintarRes(); }
      else if (e.key === "ArrowUp" && resultados.length) { e.preventDefault(); sel = (sel - 1 + resultados.length) % resultados.length; pintarRes(); }
      else if (e.key === "Enter" && sel >= 0) { e.preventDefault(); var r = $$(".res", caja2)[sel]; if (r) { caja2.hidden = true; location.href = r.href; } }
      else if (e.key === "Escape") { caja2.hidden = true; input.blur(); }
    });
    caja2.addEventListener("click", function (e) { if (e.target.closest(".res")) { caja2.hidden = true; input.blur(); } });
    document.addEventListener("click", function (e) { if (!buscador.contains(e.target)) { caja2.hidden = true; input.setAttribute("aria-expanded", "false"); } });
    document.addEventListener("keydown", function (e) {
      var escribiendo = /input|textarea|select/i.test((document.activeElement || {}).tagName || "");
      if (e.key === "/" && !escribiendo) { e.preventDefault(); input.focus(); }
    });
  }
})();
