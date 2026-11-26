/* Mapa del Semestre 1A · Liquid Glass Fluid
   Interacción y animaciones del sitio.

   Piezas principales:
   - Agua: simulación de ondas en WebGL2 que refracta la foto de fondo, con
     destellos, cáusticas y gotas al mover el cursor, hacer clic o desplazarse.
   - Luz: el cursor (o, en pantallas táctiles, el desplazamiento) es la luz que
     hace girar el borde brillante y el reflejo de cada panel de vidrio.
   - Lentes: indicadores que se deslizan y se estiran con física de resorte.
   - Repaso: casillas para marcar temas repasados (se guarda en el navegador).
   - Herramientas: paleta de comandos (Ctrl K), temporizador de estudio, notas
     por materia, sonidos de agua, avisos, app instalable y modo sin conexión. */
(function () {
  "use strict";

  var root = document.documentElement;
  var mm = function (q) { return window.matchMedia ? window.matchMedia(q) : { matches: false }; };
  var REDUCE = mm("(prefers-reduced-motion: reduce)").matches;
  var FINE = mm("(hover: hover) and (pointer: fine)").matches;
  var COARSE = mm("(pointer: coarse)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var SEMANAS = window.SEMANAS || [];
  var INICIO = new Date(2026, 7, 17); // lunes de la semana 1 del ciclo 2026B
  var DIA = 864e5;
  var BASE = root.getAttribute("data-base") || "";
  var WEB = /^https?:$/.test(location.protocol);
  /* en Google Sites cada bloque vive en su propio marco (<html class="embed">) */
  var EMBED = root.classList.contains("embed");
  function marcarHash(h) {
    if (EMBED || !history.replaceState) return;
    try { history.replaceState(null, "", h); } catch (e) { /* sin historial */ }
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function guardar(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* sin almacenamiento */ } }
  function leer(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function clamp(x, a, b) { return Math.max(a, Math.min(b, x)); }
  function rebotar(el, clase) {
    if (!el) return;
    el.classList.remove(clase);
    void el.offsetWidth;
    el.classList.add(clase);
  }

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
        var t = clamp(1 + dist / borde, 0, 1);
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
    var mapas = $$("[data-lgmap]");
    var ok = mapas.length && window.chrome && window.CSS && CSS.supports && CSS.supports("backdrop-filter", "url(#lg)") && !COARSE;
    if (!ok) return;
    var url = mapaRefraccion(160, 0.5, 0.42);
    mapas.forEach(function (m) { m.setAttribute("href", url); });
    root.classList.add("lr");
  })();

  /* =========================================================== luz global (cursor u órbita) */
  var LUZ = { x: window.innerWidth * 0.32, y: -window.innerHeight * 0.15, activa: false, ultimo: 0 };

  /* =========================================================== agua: simulación de ondas (WebGL2) */
  var VS2 = "#version 300 es\nin vec2 a;out vec2 v;void main(){v=a*.5+.5;gl_Position=vec4(a,0.,1.);}";
  var SIM = [
    "#version 300 es",
    "precision highp float;uniform sampler2D s;uniform vec2 px;in vec2 v;out vec4 o;",
    "void main(){vec4 c=texture(s,v);",
    "float m=(texture(s,v+vec2(px.x,0.)).r+texture(s,v-vec2(px.x,0.)).r+texture(s,v+vec2(0.,px.y)).r+texture(s,v-vec2(0.,px.y)).r)*.25;",
    "c.g+=(m-c.r)*2.;c.g*=.988;c.r+=c.g;c.r*=.997;o=c;}"
  ].join("\n");
  var GOTA = [
    "#version 300 es",
    "precision highp float;uniform sampler2D s;uniform vec3 d;uniform float k;uniform float asp;in vec2 v;out vec4 o;",
    "void main(){vec4 c=texture(s,v);vec2 q=(v-d.xy)*vec2(asp,1.);float f=max(0.,1.-length(q)/d.z);",
    "f=.5-cos(f*3.14159265)*.5;c.r+=f*k;o=c;}"
  ].join("\n");
  var VER = [
    "#version 300 es",
    "precision highp float;",
    "uniform sampler2D s;uniform sampler2D img;",
    "uniform float img_on;uniform float t;uniform float asp;uniform float img_asp;uniform float cau;uniform float zoom;",
    "uniform vec2 px;uniform vec2 luz;uniform vec2 par;",
    "uniform vec3 c0;uniform vec3 c1;uniform vec3 c2;uniform vec3 c3;uniform vec3 base;",
    "in vec2 v;out vec4 o;",
    "float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}",
    "float n(vec2 p){vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.-2.*f);",
    " return mix(mix(h(i),h(i+vec2(1.,0.)),u.x),mix(h(i+vec2(0.,1.)),h(i+vec2(1.,1.)),u.x),u.y);}",
    "float fbm(vec2 p){float r=0.,a=.5;for(int i=0;i<3;i++){r+=a*n(p);p=p*2.03+vec2(1.7,9.2);a*=.5;}return r;}",
    "vec3 campo(vec2 uv){vec2 p=vec2(uv.x*asp,uv.y);float tt=t*.04;",
    " vec2 q=vec2(fbm(p*1.3+vec2(0.,tt)),fbm(p*1.3+vec2(5.2,-tt)));",
    " float f=fbm(p*1.2+2.1*q+vec2(tt,-tt*.5));",
    " vec3 c=base;c=mix(c,c0,smoothstep(.34,.84,f));c=mix(c,c1,smoothstep(.45,.95,q.x)*.8);",
    " c=mix(c,c2,smoothstep(.5,.95,q.y)*.65);c=mix(c,c3,smoothstep(.5,.9,f*q.x*1.8)*.5);",
    " c*=.45+.55*smoothstep(1.25,.2,length(uv-vec2(.5,.45))*1.3);return c;}",
    "float caustica(vec2 p,float time){vec2 i=p;float c=1.;",
    " for(int k=0;k<4;k++){float tt=time*(1.-(3.5/float(k+1)));",
    "  i=p+vec2(cos(tt-i.x)+sin(tt+i.y),sin(tt-i.y)+cos(tt+i.x));",
    "  c+=1./length(vec2(p.x/(sin(i.x+tt)/.005),p.y/(cos(i.y+tt)/.005)));}",
    " c/=4.;c=1.17-pow(c,1.4);return pow(abs(c),8.);}",
    "void main(){",
    " float hl=texture(s,v-vec2(px.x,0.)).r,hr=texture(s,v+vec2(px.x,0.)).r;",
    " float hd=texture(s,v-vec2(0.,px.y)).r,hu=texture(s,v+vec2(0.,px.y)).r,hc=texture(s,v).r;",
    " vec2 g=vec2(hr-hl,hu-hd);",
    " vec3 nr=normalize(vec3(-g*8.,1.));",
    " vec2 uv=v+nr.xy*.05;",
    " vec3 fl=campo(uv);vec3 col;",
    " if(img_on>.5){vec2 sc=vec2(min(1.,asp/img_asp),min(1.,img_asp/asp))*zoom;",
    "  vec2 iu=(uv-.5)*sc+.5+par;iu.y=1.-iu.y;col=texture(img,iu).rgb;",
    "  col=(1.-(1.-col*.9)*(1.-fl*.3));}",
    " else col=fl;",
    " vec3 L=normalize(vec3((luz-v)*vec2(asp,1.),.6));",
    " float sp=pow(max(dot(reflect(-L,nr),vec3(0.,0.,1.)),0.),70.);",
    " float on=clamp(length(g)*45.,0.,1.);",
    " col+=sp*(.18+1.1*on)*vec3(1.,.97,.9);",
    " float lap=hl+hr+hd+hu-4.*hc;",
    " col+=clamp(-lap*16.,0.,.45)*vec3(.82,.92,1.);",
    " col-=clamp(lap*12.,0.,.22);",
    " if(cau>.5){vec2 cp=mod(vec2(v.x*asp,v.y)*5.6+nr.xy*.8,6.2831853)-250.;",
    "  col+=caustica(cp,t*.32)*(img_on>.5?.085:.06)*vec3(.9,.96,1.);}",
    " o=vec4(col,1.);",
    "}"
  ].join("\n");

  function hexVec(hex, k) {
    var h = hex.replace("#", "");
    return [parseInt(h.substr(0, 2), 16) / 255 * k, parseInt(h.substr(2, 2), 16) / 255 * k, parseInt(h.substr(4, 2), 16) / 255 * k];
  }

  function crearAgua(canvas) {
    var capa = canvas.closest(".bg");
    var conFoto = capa && capa.classList.contains("bg--photo");
    var gl = null;
    try { gl = canvas.getContext("webgl2", { antialias: false, alpha: false, depth: false, stencil: false }); } catch (e) { gl = null; }
    if (!gl || !gl.getExtension("EXT_color_buffer_float")) return null;

    function sh(tipo, src) {
      var s = gl.createShader(tipo);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null;
    }
    function programa(fsrc) {
      var vs = sh(gl.VERTEX_SHADER, VS2), fs = sh(gl.FRAGMENT_SHADER, fsrc);
      if (!vs || !fs) return null;
      var p = gl.createProgram();
      gl.attachShader(p, vs);
      gl.attachShader(p, fs);
      gl.bindAttribLocation(p, 0, "a");
      gl.linkProgram(p);
      if (!gl.getProgramParameter(p, gl.LINK_STATUS)) return null;
      var u = {};
      var total = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
      for (var i = 0; i < total; i++) { var inf = gl.getActiveUniform(p, i); u[inf.name] = gl.getUniformLocation(p, inf.name); }
      return { p: p, u: u };
    }
    var P = { sim: programa(SIM), gota: programa(GOTA), ver: programa(VER) };
    if (!P.sim || !P.gota || !P.ver) return null;

    var vao = gl.createVertexArray();
    gl.bindVertexArray(vao);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);

    function textura() {
      var tx = gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D, tx);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      return tx;
    }
    var SW = 0, SH = 0, tex = [null, null], fbo = [null, null], lee = 0;
    function crearSim() {
      SW = Math.max(64, Math.round(window.innerWidth / (COARSE ? 6 : 4.5)));
      SH = Math.max(64, Math.round(window.innerHeight / (COARSE ? 6 : 4.5)));
      for (var i = 0; i < 2; i++) {
        if (tex[i]) gl.deleteTexture(tex[i]);
        if (fbo[i]) gl.deleteFramebuffer(fbo[i]);
        tex[i] = textura();
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, SW, SH, 0, gl.RGBA, gl.HALF_FLOAT, null);
        fbo[i] = gl.createFramebuffer();
        gl.bindFramebuffer(gl.FRAMEBUFFER, fbo[i]);
        gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex[i], 0);
        if (gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE) return false;
        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
      }
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      return true;
    }
    if (!crearSim()) return null;

    function pasada(prog, prep) {
      gl.useProgram(prog.p);
      gl.bindFramebuffer(gl.FRAMEBUFFER, fbo[1 - lee]);
      gl.viewport(0, 0, SW, SH);
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, tex[lee]);
      gl.uniform1i(prog.u.s, 0);
      prep(prog.u);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      lee = 1 - lee;
    }
    function pasoSim() { pasada(P.sim, function (u) { gl.uniform2f(u.px, 1 / SW, 1 / SH); }); }
    function soltar(x, y, r, k) {
      pasada(P.gota, function (u) {
        gl.uniform3f(u.d, x, y, r);
        gl.uniform1f(u.k, k);
        gl.uniform1f(u.asp, window.innerWidth / window.innerHeight);
      });
    }

    /* foto de fondo como textura. En el dominio se usa la misma <img> (WebP del tamaño
       justo); al abrir el archivo con doble clic el navegador la trata como de otro
       origen, así que se carga la copia incrustada (assets/js/fondos/). */
    var imgTex = null, imgAsp = 2;
    function usarFoto(im) {
      try {
        var tx = textura();
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, im);
        imgTex = tx;
        imgAsp = (im.naturalWidth || im.width) / (im.naturalHeight || im.height);
        capa.classList.add("is-water");
      } catch (e) { imgTex = null; }
      capa.classList.remove("is-loading");
      if (!corriendo) dibujar(performance.now());
    }
    function sinFoto() { capa.classList.remove("is-loading"); }
    if (conFoto) {
      capa.classList.add("is-loading");
      var fotoEl = $(".bg__photo", capa);
      if (fotoEl && (WEB || /^data:/.test(fotoEl.getAttribute("src") || ""))) {
        var lista = function () { if (fotoEl.decode) fotoEl.decode().then(function () { usarFoto(fotoEl); }, function () { usarFoto(fotoEl); }); else usarFoto(fotoEl); };
        if (fotoEl.complete && fotoEl.naturalWidth) lista();
        else { fotoEl.addEventListener("load", lista, { once: true }); fotoEl.addEventListener("error", sinFoto, { once: true }); }
      } else {
        var incrustada = function () { var im = new Image(); im.onload = function () { usarFoto(im); }; im.onerror = sinFoto; im.src = window.FONDO; };
        var guion = capa.getAttribute("data-fondo");
        if (window.FONDO) incrustada();
        else if (guion) { var sc = document.createElement("script"); sc.src = guion; sc.onload = incrustada; sc.onerror = sinFoto; document.head.appendChild(sc); }
        else sinFoto();
      }
    } else {
      capa.classList.add("is-water");
    }

    var colores = (canvas.getAttribute("data-colors") || "#3b5bff,#8b4ff0,#ff9a3d,#17a88a").split(",");
    var brillo = conFoto ? 1 : 0.8;
    var base = conFoto ? [0, 0, 0] : hexVec("#070a14", 1);

    /* calidad que se ajusta sola: si el equipo no da el ritmo, baja resolución y efectos */
    var niveles = COARSE ? [{ e: 0.42, c: 1, fps: 40 }, { e: 0.32, c: 0, fps: 30 }] : [{ e: 0.62, c: 1, fps: 60 }, { e: 0.46, c: 1, fps: 40 }, { e: 0.34, c: 0, fps: 30 }];
    var nivel = 0;
    function medir() {
      var q = niveles[nivel];
      var w = Math.max(2, Math.round(window.innerWidth * q.e)), h = Math.max(2, Math.round(window.innerHeight * q.e));
      if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    }
    medir();
    var reajuste = 0;
    window.addEventListener("resize", function () {
      clearTimeout(reajuste);
      reajuste = setTimeout(function () { medir(); crearSim(); if (!corriendo) dibujar(performance.now()); }, 200);
    });

    var t0 = performance.now();
    var cola = [];
    var luzS = [0.32, 1.1], parS = [0, 0], ptr = null;
    function dibujar(ahora) {
      var t = (ahora - t0) / 1000;
      var lx = LUZ.x / window.innerWidth, ly = 1 - LUZ.y / window.innerHeight;
      luzS[0] += (lx - luzS[0]) * 0.12; luzS[1] += (ly - luzS[1]) * 0.12;
      var px = FINE && ptr ? (0.5 - ptr[0]) * 0.018 : 0, py = FINE && ptr ? (ptr[1] - 0.5) * 0.012 : 0;
      parS[0] += (px - parS[0]) * 0.05; parS[1] += (py - parS[1]) * 0.05;
      var u = P.ver.u;
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.useProgram(P.ver.p);
      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, tex[lee]);
      gl.uniform1i(u.s, 0);
      gl.activeTexture(gl.TEXTURE1);
      gl.bindTexture(gl.TEXTURE_2D, imgTex || tex[lee]);
      gl.uniform1i(u.img, 1);
      gl.uniform1f(u.img_on, imgTex ? 1 : 0);
      gl.uniform1f(u.t, t);
      gl.uniform1f(u.asp, window.innerWidth / window.innerHeight);
      gl.uniform1f(u.img_asp, imgAsp);
      gl.uniform1f(u.cau, niveles[nivel].c);
      gl.uniform1f(u.zoom, 0.93 - 0.025 * Math.sin(t * 0.035));
      gl.uniform2f(u.px, 1 / SW, 1 / SH);
      gl.uniform2f(u.luz, luzS[0], luzS[1]);
      gl.uniform2f(u.par, parS[0], parS[1]);
      gl.uniform3fv(u.c0, hexVec(colores[0], brillo));
      gl.uniform3fv(u.c1, hexVec(colores[1 % colores.length], brillo));
      gl.uniform3fv(u.c2, hexVec(colores[2 % colores.length], brillo));
      gl.uniform3fv(u.c3, hexVec(colores[3 % colores.length], brillo));
      gl.uniform3fv(u.base, base);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }

    var corriendo = false, ultimo = 0, acum = 0, muestras = [], proximaLluvia = 0, suave = false;
    function cuadro(ahora) {
      if (!corriendo) return;
      requestAnimationFrame(cuadro);
      /* el primer cuadro siempre se dibuja (antes, a 40 o 30 cuadros por segundo nunca arrancaba) */
      var primero = !ultimo;
      var dt = primero ? 1000 / niveles[nivel].fps : ahora - ultimo;
      if (!primero && dt < 1000 / niveles[nivel].fps - 3) return;
      if (!primero && ahora - t0 > 2500) {
        muestras.push(dt);
        if (muestras.length >= 90) {
          var prom = muestras.reduce(function (a, b) { return a + b; }, 0) / muestras.length;
          muestras = [];
          if (prom > 1000 / niveles[nivel].fps * 1.6 && nivel < niveles.length - 1) { nivel++; medir(); }
        }
      }
      ultimo = ahora;
      if (ahora > proximaLluvia) {
        proximaLluvia = ahora + (suave ? 4200 : 900) + Math.random() * 1600;
        cola.push([Math.random(), Math.random(), 0.012 + Math.random() * 0.016, (0.03 + Math.random() * 0.05) * (suave ? 0.4 : 1)]);
      }
      cola.splice(0, 14).forEach(function (g) { soltar(g[0], g[1], g[2], g[3]); });
      acum += Math.min(dt, 100);
      var pasos = 0;
      while (acum >= 16 && pasos < 4) { pasoSim(); acum -= 16; pasos++; }
      dibujar(ahora);
    }

    /* las gotas: al mover el cursor, al tocar y al desplazarse */
    var prev = null;
    window.addEventListener("pointermove", function (e) {
      var x = e.clientX / window.innerWidth, y = 1 - e.clientY / window.innerHeight;
      ptr = [x, y];
      var ahora = performance.now();
      if (!prev) { prev = { x: e.clientX, y: e.clientY, t: ahora }; return; }
      var dist = Math.hypot(e.clientX - prev.x, e.clientY - prev.y);
      if (dist < 7) return;
      var vel = dist / Math.max(8, ahora - prev.t);
      cola.push([x, y, 0.014 + Math.min(0.012, vel * 0.004), Math.min(0.07, 0.008 + vel * 0.016) * (suave ? 0.35 : 1)]);
      prev = { x: e.clientX, y: e.clientY, t: ahora };
    }, { passive: true });
    window.addEventListener("pointerdown", function (e) {
      if (e.target.closest && e.target.closest("input, textarea")) return;
      cola.push([e.clientX / window.innerWidth, 1 - e.clientY / window.innerHeight, 0.04, 0.26]);
    }, { passive: true });
    var yPrev = window.scrollY;
    window.addEventListener("scroll", function () {
      var dy = window.scrollY - yPrev;
      yPrev = window.scrollY;
      var f = Math.min(0.06, Math.abs(dy) * 0.0012);
      if (f > 0.004) cola.push([Math.random(), dy > 0 ? 0.04 : 0.96, 0.03, f]);
    }, { passive: true });
    canvas.addEventListener("webglcontextlost", function (e) {
      e.preventDefault();
      corriendo = false;
      capa.classList.remove("is-water", "is-loading");
    });

    return {
      iniciar: function () { if (corriendo) return; corriendo = true; ultimo = 0; requestAnimationFrame(cuadro); },
      detener: function () { corriendo = false; dibujar(performance.now()); },
      calmar: function (on) { suave = !!on; },
      salpicar: function (xpx, ypx, k) {
        cola.push([xpx / window.innerWidth, 1 - ypx / window.innerHeight, 0.05, k || 0.4]);
        if (!corriendo) { soltar(xpx / window.innerWidth, 1 - ypx / window.innerHeight, 0.05, k || 0.4); dibujar(performance.now()); }
      }
    };
  }

  /* respaldo (WebGL 1): campo de color fluido que se arremolina con el cursor */
  var FRAG1 = [
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
    " col=mix(col,c0,smoothstep(.34,.86,f));col=mix(col,c1,smoothstep(.45,.95,w2.x)*.85);",
    " col=mix(col,c2,smoothstep(.5,.95,q.y)*.7);col=mix(col,c3,smoothstep(.5,.9,w2.y*f*1.6)*.55);",
    " col*=.42+.58*smoothstep(1.25,.2,length(uv-vec2(.5,.45))*1.3);",
    " gl_FragColor=vec4(col,1.);",
    "}"
  ].join("\n");
  function crearLiquidoSimple(canvas) {
    var capa = canvas.closest(".bg");
    var conFoto = capa && capa.classList.contains("bg--photo");
    var gl = null;
    try { gl = canvas.getContext("webgl", { antialias: false, alpha: false, depth: false }); } catch (e) { gl = null; }
    if (!gl) { if (capa) capa.classList.add("no-gl"); return null; }
    function shader(tipo, src) { var s = gl.createShader(tipo); gl.shaderSource(s, src); gl.compileShader(s); return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null; }
    var vs = shader(gl.VERTEX_SHADER, "attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}"), fs = shader(gl.FRAGMENT_SHADER, FRAG1);
    if (!vs || !fs) { if (capa) capa.classList.add("no-gl"); return null; }
    var prog = gl.createProgram();
    gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { if (capa) capa.classList.add("no-gl"); return null; }
    gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, "a");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var U = {};
    ["r", "t", "m", "ms", "drop", "c0", "c1", "c2", "c3", "base"].forEach(function (k) { U[k] = gl.getUniformLocation(prog, k); });
    var colores = (canvas.getAttribute("data-colors") || "#3b5bff,#8b4ff0,#ff9a3d,#17a88a").split(",");
    ["c0", "c1", "c2", "c3"].forEach(function (k, i) { gl.uniform3fv(U[k], hexVec(colores[i % colores.length], conFoto ? 1 : 0.78)); });
    gl.uniform3fv(U.base, conFoto ? [0, 0, 0] : hexVec("#070a14", 1));
    gl.uniform3fv(U.drop, [0.5, 0.5, -10]);
    var escala = COARSE ? 0.26 : 0.4;
    function medir() {
      var w = Math.max(2, Math.round(window.innerWidth * escala)), h = Math.max(2, Math.round(window.innerHeight * escala));
      canvas.width = w; canvas.height = h; gl.viewport(0, 0, w, h); gl.uniform2f(U.r, w, h);
    }
    medir();
    window.addEventListener("resize", medir);
    var t0 = performance.now(), mx = 0.5, my = 0.55, tx = 0.5, ty = 0.55, fuerza = 0, previo = null;
    window.addEventListener("pointermove", function (e) {
      var x = e.clientX / window.innerWidth, y = 1 - e.clientY / window.innerHeight, ahora = performance.now();
      if (previo) fuerza = Math.min(1.5, fuerza + Math.hypot(x - previo.x, y - previo.y) / Math.max(0.016, (ahora - previo.t) / 1000) * 0.06);
      previo = { x: x, y: y, t: ahora }; tx = x; ty = y;
    }, { passive: true });
    window.addEventListener("pointerdown", function (e) {
      gl.uniform3f(U.drop, e.clientX / window.innerWidth, 1 - e.clientY / window.innerHeight, (performance.now() - t0) / 1000);
    }, { passive: true });
    function dibujar(ahora) {
      mx += (tx - mx) * 0.08; my += (ty - my) * 0.08; fuerza *= 0.955;
      gl.uniform1f(U.t, (ahora - t0) / 1000); gl.uniform2f(U.m, mx, my); gl.uniform1f(U.ms, fuerza);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }
    var corriendo = false, ultimo = 0;
    function bucle(ahora) {
      if (!corriendo) return;
      if (ahora - ultimo >= 33) { ultimo = ahora; dibujar(ahora); }
      requestAnimationFrame(bucle);
    }
    return {
      iniciar: function () { if (corriendo) return; corriendo = true; requestAnimationFrame(bucle); },
      detener: function () { corriendo = false; dibujar(performance.now()); },
      calmar: function () {},
      salpicar: function (x, y) { gl.uniform3f(U.drop, x / window.innerWidth, 1 - y / window.innerHeight, (performance.now() - t0) / 1000); }
    };
  }

  var agua = (function () {
    var canvas = $("[data-liquid]");
    if (!canvas) return null;
    var a = null;
    try { a = crearAgua(canvas); } catch (e) { a = null; }
    if (a) return a;
    var c2 = canvas.cloneNode(false); // un lienzo con contexto WebGL2 fallido no admite otro contexto
    canvas.parentNode.replaceChild(c2, canvas);
    return crearLiquidoSimple(c2);
  })();
  if (agua) { if (calma) agua.detener(); else agua.iniciar(); }
  /* en Google Sites hay varios bloques por página: cada uno mueve su agua solo mientras se ve */
  if (EMBED && agua && "IntersectionObserver" in window) {
    new IntersectionObserver(function (es) {
      if (calma) return;
      if (es[es.length - 1].isIntersecting) agua.iniciar(); else agua.detener();
    }).observe(document.body);
  }

  /* el botón "Efecto líquido" alterna el modo calma */
  $$("[data-calma]").forEach(function (b) {
    b.setAttribute("aria-pressed", calma ? "false" : "true");
    b.addEventListener("click", function () {
      calma = !calma;
      root.classList.toggle("calma", calma);
      guardar("calma", calma ? "1" : "0");
      $$("[data-calma]").forEach(function (x) { x.setAttribute("aria-pressed", calma ? "false" : "true"); });
      if (agua) { if (calma) agua.detener(); else agua.iniciar(); }
      if (!calma) orbitar();
    });
  });

  /* =========================================================== reflejos en tiempo real */
  var visibles = new Set();
  if ("IntersectionObserver" in window) {
    var iog = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) visibles.add(en.target); else visibles.delete(en.target); });
    }, { rootMargin: "120px" });
    $$(".glass, .glass-pill").forEach(function (el) { iog.observe(el); });
  }
  var foto = $(".bg__photo");
  var bajoCursor = null;
  function iluminar() {
    visibles.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (!r.width) return;
      var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
      var ang = Math.atan2(LUZ.y - cy, LUZ.x - cx) * 180 / Math.PI + 90;
      var dx = Math.max(r.left - LUZ.x, 0, LUZ.x - r.right), dy = Math.max(r.top - LUZ.y, 0, LUZ.y - r.bottom);
      var dentro = dx === 0 && dy === 0;
      var li = dentro ? 1 : clamp(1 - Math.hypot(dx, dy) / 900, 0.22, 0.95);
      el.style.setProperty("--ang", ang.toFixed(1) + "deg");
      el.style.setProperty("--li", li.toFixed(3));
      el.style.setProperty("--mx", clamp(LUZ.x - r.left, -r.width * 0.25, r.width * 1.25).toFixed(0) + "px");
      el.style.setProperty("--my", clamp(LUZ.y - r.top, -r.height * 0.25, r.height * 1.25).toFixed(0) + "px");
      el.style.setProperty("--spec", dentro && el === bajoCursor ? "1" : (0.22 + li * 0.42).toFixed(3));
    });
  }
  var pendienteLuz = false;
  function pedirLuz() {
    if (pendienteLuz) return;
    pendienteLuz = true;
    requestAnimationFrame(function () { pendienteLuz = false; iluminar(); });
  }
  window.addEventListener("pointermove", function (e) {
    if (e.pointerType === "touch") return;
    LUZ.x = e.clientX; LUZ.y = e.clientY; LUZ.activa = true; LUZ.ultimo = performance.now();
    bajoCursor = e.target.closest ? e.target.closest(".glass, .glass-pill") : null;
    if (foto && !calma) {
      foto.style.setProperty("--px", ((0.5 - e.clientX / window.innerWidth) * 26).toFixed(1) + "px");
      foto.style.setProperty("--py", ((0.5 - e.clientY / window.innerHeight) * 18).toFixed(1) + "px");
    }
    pedirLuz();
  }, { passive: true });
  document.addEventListener("pointerleave", function () { LUZ.activa = false; bajoCursor = null; });
  window.addEventListener("scroll", pedirLuz, { passive: true });
  window.addEventListener("resize", pedirLuz);
  /* sin cursor (o quieto), la luz orbita despacio y en el celular sigue al desplazamiento */
  var orbitando = false;
  function orbitar() {
    if (orbitando || calma) return;
    orbitando = true;
    var ultimoO = 0;
    (function paso(ahora) {
      if (calma) { orbitando = false; return; }
      requestAnimationFrame(paso);
      if (ahora - ultimoO < 60) return;
      ultimoO = ahora;
      var quieto = !LUZ.activa || ahora - LUZ.ultimo > 4000;
      if (!quieto) return;
      var t = ahora / 1000 * 0.18 + window.scrollY / 520;
      LUZ.x = window.innerWidth * (0.5 + 0.48 * Math.cos(t));
      LUZ.y = window.innerHeight * (0.28 + 0.4 * Math.sin(t * 0.8)) - 120;
      iluminar();
    })(0);
  }
  iluminar();
  if (!REDUCE) orbitar();

  /* =========================================================== gota de cristal que sigue al cursor */
  if (FINE && !REDUCE) {
    var gota = document.createElement("div");
    gota.className = "gota";
    gota.setAttribute("aria-hidden", "true");
    document.body.appendChild(gota);
    var gx = -100, gy = -100, gvx = 0, gvy = 0, gtx = -100, gty = -100, gMov = false, gVisible = false;
    var INTERACTIVO = "a, button, [role='button'], summary, label, .bar, .seg-bar__part, .tick, .week__bar li, [data-jelly], .gauge, .liquid-orb";
    var animarGota = function () {
      if (calma) { gMov = false; return; }
      gvx += (gtx - gx) * 0.2; gvy += (gty - gy) * 0.2;
      gvx *= 0.6; gvy *= 0.6;
      gx += gvx; gy += gvy;
      var vel = Math.hypot(gvx, gvy);
      var est = Math.min(vel * 0.03, 0.55);
      var ang = Math.atan2(gvy, gvx);
      gota.style.transform = "translate(" + gx.toFixed(1) + "px," + gy.toFixed(1) + "px) rotate(" + ang.toFixed(3) + "rad) scale(" + (1 + est).toFixed(3) + "," + (1 - est * 0.45).toFixed(3) + ")";
      if (vel > 0.05 || Math.abs(gtx - gx) > 0.3 || Math.abs(gty - gy) > 0.3) requestAnimationFrame(animarGota);
      else gMov = false;
    };
    window.addEventListener("pointermove", function (e) {
      if (e.pointerType !== "mouse") return;
      gtx = e.clientX; gty = e.clientY;
      if (!gVisible) { gx = gtx; gy = gty; gVisible = true; gota.classList.add("is-on"); }
      var t = e.target;
      var texto = t.closest && t.closest("input, textarea");
      gota.classList.toggle("is-text", !!texto);
      gota.classList.toggle("is-hover", !texto && !!(t.closest && t.closest(INTERACTIVO)));
      if (!gMov) { gMov = true; requestAnimationFrame(animarGota); }
    }, { passive: true });
    window.addEventListener("pointerdown", function () { gota.classList.add("is-down"); }, { passive: true });
    window.addEventListener("pointerup", function () { gota.classList.remove("is-down"); }, { passive: true });
    document.addEventListener("mouseleave", function () { gVisible = false; gota.classList.remove("is-on"); });
  }

  /* =========================================================== botones magnéticos + tarjetas gelatina */
  if (FINE && !REDUCE) {
    $$(".btn, .iconbtn").forEach(function (b) {
      b.addEventListener("pointermove", function (e) {
        var r = b.getBoundingClientRect();
        b.style.setProperty("--tx", ((e.clientX - r.left - r.width / 2) * 0.22).toFixed(1) + "px");
        b.style.setProperty("--ty", ((e.clientY - r.top - r.height / 2) * 0.3).toFixed(1) + "px");
      });
      b.addEventListener("pointerleave", function () { b.style.setProperty("--tx", "0px"); b.style.setProperty("--ty", "0px"); });
    });
    $$("[data-jelly]").forEach(function (c) { gelatina(c); });
  }
  function gelatina(c) {
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
  }

  /* =========================================================== gota (onda al tocar) */
  var CON_ONDA = "[data-ripple], .seg__btn, .side__item, .dock__item, .mcard, .tcard, .pill, .code__copy, .side__motion, .chk, .tag, .side__week";
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
    setTimeout(function () { s.remove(); }, 1000);
    if (el.matches(".btn, .seg__btn, .dock__item, .pill, .tag, .side__week")) rebotar(el, "is-jelly");
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
    function pintar(apl, brillo) {
      lens.style.transform = "translate(" + E.l.x.toFixed(2) + "px," + E.t.x.toFixed(2) + "px)" +
        (apl ? (vertical ? " scale(" + (1 - apl).toFixed(3) + ",1)" : " scale(1," + (1 - apl).toFixed(3) + ")") : "");
      lens.style.width = Math.max(0, E.r.x - E.l.x).toFixed(2) + "px";
      lens.style.height = Math.max(0, E.b.x - E.t.x).toFixed(2) + "px";
      lens.style.setProperty("--lx", (brillo == null ? 30 : brillo).toFixed(1) + "%");
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
      pintar(0, 30);
      colorear();
      lens.classList.add("is-ready");
    }
    function paso(ts) {
      if (!objetivo) { corriendo = false; return; }
      var dt = ultimo ? Math.min(0.034, (ts - ultimo) / 1000) : 0.016;
      ultimo = ts;
      var k = caja(objetivo);
      var dir = vertical ? Math.sign((k.t + k.b) - (E.t.x + E.b.x)) : Math.sign((k.l + k.r) - (E.l.x + E.r.x));
      var rapido = 640, lento = 180;
      var rig = vertical
        ? { t: dir < 0 ? rapido : lento, b: dir > 0 ? rapido : lento, l: 420, r: 420 }
        : { l: dir < 0 ? rapido : lento, r: dir > 0 ? rapido : lento, t: 420, b: 420 };
      var quieto = true;
      ["l", "r", "t", "b"].forEach(function (lado) {
        var s = E[lado], kk = rig[lado], c = 2 * Math.sqrt(kk) * 0.7;
        s.v += ((k[lado] - s.x) * kk - s.v * c) * dt;
        s.x += s.v * dt;
        if (Math.abs(k[lado] - s.x) > 0.25 || Math.abs(s.v) > 0.25) quieto = false;
      });
      var vel = vertical ? (E.t.v + E.b.v) / 2 : (E.l.v + E.r.v) / 2;
      var apl = Math.min(0.16, Math.abs(vel) * 0.00032);
      pintar(apl, clamp(30 - vel * 0.02, 5, 70));
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

  /* =========================================================== volver arriba con anillo de avance */
  var totop = $("[data-totop]");
  if (totop) {
    var vista = false, pendTop = false;
    window.addEventListener("scroll", function () {
      if (pendTop) return;
      pendTop = true;
      requestAnimationFrame(function () {
        pendTop = false;
        var y = window.scrollY || window.pageYOffset;
        var alto = document.documentElement.scrollHeight - window.innerHeight;
        totop.style.setProperty("--sp", alto > 0 ? clamp(y / alto, 0, 1).toFixed(4) : "0");
        var on = y > 700;
        if (on !== vista) { vista = on; totop.classList.toggle("is-on", on); }
      });
    }, { passive: true });
  }

  /* =========================================================== aparición líquida (desenfoque → nitidez) */
  var observar = function () {};
  var intro = 0;
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
      if (r.height === 0) return;
      if (r.top < window.innerHeight * 0.92) {
        /* lo que ya se ve al cargar se condensa como gotas, en cascada */
        el.style.setProperty("--d", (0.08 + intro++ * 0.07).toFixed(2) + "s");
        el.classList.add("is-intro");
        el.addEventListener("animationend", function fin(ev) {
          if (ev.target !== el) return;
          el.classList.remove("is-intro");
          el.removeEventListener("animationend", fin);
        });
        return;
      }
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
    var fecha = "", corta = mm("(max-width: 600px)").matches;
    try { fecha = new Intl.DateTimeFormat("es-MX", { weekday: "long", day: "numeric", month: corta ? "short" : "long" }).format(hoy); } catch (e) { fecha = hoy.toLocaleDateString(); }
    fecha = fecha.charAt(0).toUpperCase() + fecha.slice(1);
    el.textContent = corta ? fecha : saludo + ", 1A · " + fecha;
    el.title = saludo + ", 1A";
    if (!REDUCE) el.classList.add("is-in");
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
      var cajaT = term.closest(".term");
      var lineas = $$(".tl", term);
      var textos = lineas.map(function (l) { var t = $(".t-typed", l); return t ? t.textContent : null; });
      lineas.forEach(function (l) { var t = $(".t-typed", l); if (t) t.textContent = ""; });
      cajaT.classList.add("is-typing");
      var i = 0;
      var siguiente = function () {
        if (i >= lineas.length) { cajaT.classList.remove("is-typing"); return; }
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

  /* tocar un indicador líquido lo agita y salpica el agua de fondo */
  $$(".gauge, .liquid-orb").forEach(function (g) {
    g.addEventListener("click", function () {
      rebotar(g, "is-splash");
      setTimeout(function () { g.classList.remove("is-splash"); }, 1800);
      var r = g.getBoundingClientRect();
      if (agua && agua.salpicar) agua.salpicar(r.left + r.width / 2, r.top + r.height / 2, 0.45);
    });
  });

  /* =========================================================== filtro de materias */
  var mgrid = $("[data-mgrid]");
  var filtros = $("[data-filters]");
  if (mgrid && filtros) {
    var lf = lenteDe(filtros);
    $$("[data-filter]", filtros).forEach(function (b) {
      b.addEventListener("click", function () {
        var f = b.getAttribute("data-filter");
        if (lf) lf.activar(b);
        sonar("tab");
        $$("[data-filter]", filtros).forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        var visiblesM = [];
        $$(".mcard", mgrid).forEach(function (c) {
          var mostrar = f === "todas" || c.getAttribute("data-area") === f;
          c.classList.remove("rv", "in", "is-intro");
          c.hidden = !mostrar;
          if (mostrar) visiblesM.push(c);
        });
        mgrid.classList.toggle("is-filtered", f !== "todas");
        mgrid.style.gridTemplateColumns = "";
        if (f !== "todas") {
          var cols = getComputedStyle(mgrid).gridTemplateColumns.split(" ").length;
          if (visiblesM.length < cols) mgrid.style.gridTemplateColumns = "repeat(" + visiblesM.length + ", minmax(0, 1fr))";
        }
        if (!REDUCE && mgrid.animate) {
          visiblesM.forEach(function (c, i) {
            c.animate([
              { opacity: 0, filter: "blur(16px)", transform: "translateY(22px) scale(.94)", borderRadius: "40px" },
              { opacity: 1, filter: "blur(0px)", transform: "none", borderRadius: "26px" }
            ], { duration: 700, delay: i * 55, easing: "cubic-bezier(.22,.8,.24,1)", fill: "backwards" });
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
    var fotoM = m.foto ? (/^(https?:|data:|\/)/.test(m.foto) ? m.foto : base + m.foto) : "";
    var orb = fotoM ? '<img src="' + esc(fotoM) + '" alt="Foto de ' + esc(nombre || "integrante " + (i + 1)) + '" loading="lazy">' : nombre ? esc(iniciales(nombre)) : ICO_USER;
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
  $$("[data-equipo]").forEach(function (cajaE) {
    var lista = window.EQUIPO;
    if (!Array.isArray(lista) || !lista.length) return;
    cajaE.innerHTML = lista.map(tarjeta).join("");
    var n = lista.length;
    cajaE.style.setProperty("--n-row", n <= 5 ? n : n === 6 ? 3 : n <= 8 ? 4 : 5);
    $$(".tcard", cajaE).forEach(function (t) {
      var girar = function () {
        var on = !t.classList.contains("is-open");
        t.classList.toggle("is-open", on);
        t.setAttribute("aria-pressed", on ? "true" : "false");
        $(".tcard__back", t).setAttribute("aria-hidden", on ? "false" : "true");
      };
      t.addEventListener("click", function () { if (!FINE) girar(); });
      t.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); girar(); } });
      if (FINE && !REDUCE) gelatina(t);
      if (window.IntersectionObserver) iog && iog.observe(t);
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
      pedirLuz();
    };
    mostrarPanel(botones[0].getAttribute("data-tab"));
    botones.forEach(function (b, i) {
      b.addEventListener("click", function () {
        var id = b.getAttribute("data-tab");
        mostrarPanel(id);
        marcarHash("#" + id);
        sonar("tab");
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
    if (!panel && el.classList.contains("cal__w")) { resaltarSemana(el); return; }
    if (panel) mostrarPanel(panel.id);
    if (panel && el !== panel) {
      setTimeout(function () {
        el.scrollIntoView({ block: "center", behavior: REDUCE ? "auto" : "smooth" });
        rebotar(el, "is-hit");
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
  function centrarSemana() {}
  function resaltarSemana(el) {
    if (!el) return;
    if (el.hidden) { var todas = $('[data-cal-filter="0"]'); if (todas) todas.click(); }
    setTimeout(function () {
      el.scrollIntoView({ block: "center", behavior: REDUCE ? "auto" : "smooth" });
      rebotar(el, "is-hit");
    }, 80);
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
        sonar("tab");
        $$("[data-cal-filter]").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        var n = 0;
        $$(".cal__w", cal).forEach(function (li) {
          var ver = u === "0" || (u === "ev" ? li.getAttribute("data-ev") === "1" : li.getAttribute("data-u") === u);
          li.hidden = !ver;
          if (ver && !REDUCE) { li.style.animationDelay = (n++ * 40) + "ms"; rebotar(li, "is-in"); }
        });
      });
    });
  }

  /* leyenda de la evaluación: al pasar sobre un tipo se resalta su parte de la barra */
  $$(".legend li[data-k]").forEach(function (li) {
    var barra = $(".seg-bar", li.closest("[data-panel]") || document);
    if (!barra) return;
    var parte = $('.seg-bar__part[data-k="' + li.getAttribute("data-k") + '"]', barra);
    var on = function () { barra.classList.add("is-focusing"); if (parte) parte.classList.add("is-focus"); };
    var off = function () { barra.classList.remove("is-focusing"); if (parte) parte.classList.remove("is-focus"); };
    li.addEventListener("pointerenter", on);
    li.addEventListener("pointerleave", off);
  });

  /* =========================================================== copiar el ejemplo de código */
  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var code = $("[data-code]", b.closest(".codeblock"));
      var texto = $$(".ln", code).map(function (l) { return l.textContent; }).join("\n");
      var etiqueta = $("span", b);
      var aviso = function (msg, ok) {
        etiqueta.textContent = msg;
        b.classList.toggle("is-ok", !!ok);
        setTimeout(function () { etiqueta.textContent = "Copiar"; b.classList.remove("is-ok"); }, 1800);
      };
      var seleccionar = function () {
        var rango = document.createRange();
        rango.selectNodeContents(code);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(rango);
        aviso("Seleccionado");
      };
      try { navigator.clipboard.writeText(texto).then(function () { aviso("Copiado", true); }, seleccionar); } catch (e) { seleccionar(); }
    });
  });

  /* =========================================================== repaso: marcar temas repasados */
  function vistos(slug) {
    try { return JSON.parse(leer("repaso:" + slug) || "[]"); } catch (e) { return []; }
  }
  (function () {
    var caja = $("[data-repaso]");
    var botonesR = $$("[data-tema]");
    if (!caja || !botonesR.length) return;
    var slug = caja.getAttribute("data-repaso");
    var marcados = {};
    vistos(slug).forEach(function (id) { marcados[id] = true; });
    var orb = $("[data-orb]", caja);
    var numero = $("[data-repaso-n]", caja);
    var pct = $("[data-repaso-pct]", caja);
    var pista = $("[data-repaso-hint]", caja);
    var reiniciar = $("[data-repaso-reset]", caja);
    var pistaOriginal = pista ? pista.textContent : "";
    function pintar(b) {
      var on = !!marcados[b.getAttribute("data-tema")];
      b.setAttribute("aria-pressed", on ? "true" : "false");
      if (b.classList.contains("chk")) { var nodo = b.closest(".node"); if (nodo) nodo.classList.toggle("is-done", on); }
    }
    function actualizar(animar) {
      var total = botonesR.length;
      var n = botonesR.filter(function (b) { return marcados[b.getAttribute("data-tema")]; }).length;
      var p = total ? n / total : 0;
      if (orb) { orb.style.setProperty("--p", p.toFixed(3)); orb.setAttribute("aria-label", "Avance de repaso: " + Math.round(p * 100) + " %"); }
      if (pct) pct.textContent = Math.round(p * 100) + " %";
      if (numero) { numero.textContent = n; if (animar) rebotar(numero, "is-bump"); }
      if (pista) pista.textContent = n === 0 ? pistaOriginal : n === total ? "¡Repasaste toda la materia! Excelente trabajo." : "Te faltan " + (total - n) + " temas. ¡Sigue así!";
      if (reiniciar) reiniciar.hidden = n === 0;
      $$("[data-panel]").forEach(function (panel) {
        var insignia = $("[data-unit-prog]", panel);
        var propios = $$("[data-tema]", panel);
        if (!insignia || !propios.length) return;
        var hechos = propios.filter(function (b) { return marcados[b.getAttribute("data-tema")]; }).length;
        insignia.hidden = false;
        insignia.style.setProperty("--p", (hechos / propios.length).toFixed(3));
        insignia.innerHTML = "<i></i>" + hechos + "/" + propios.length;
        insignia.classList.toggle("is-done", hechos === propios.length);
        if (animar && panel.classList.contains("is-on")) rebotar(insignia, "is-bump");
      });
    }
    botonesR.forEach(function (b) {
      pintar(b);
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        var id = b.getAttribute("data-tema");
        if (marcados[id]) delete marcados[id]; else marcados[id] = true;
        guardar("repaso:" + slug, JSON.stringify(Object.keys(marcados)));
        pintar(b);
        b.classList.remove("is-pop");
        if (marcados[id]) { rebotar(b, "is-pop"); if (orb) rebotar(orb, "is-splash"); sonar("gota"); vibrar(10); }
        else sonar("suave");
        actualizar(true);
      });
    });
    if (reiniciar) {
      var confirmar = 0;
      reiniciar.addEventListener("click", function () {
        var etq = $("span", reiniciar);
        if (!reiniciar.classList.contains("is-confirm")) {
          reiniciar.classList.add("is-confirm");
          etq.textContent = "Toca otra vez para borrar";
          confirmar = setTimeout(function () { reiniciar.classList.remove("is-confirm"); etq.textContent = "Reiniciar repaso"; }, 3000);
          return;
        }
        clearTimeout(confirmar);
        reiniciar.classList.remove("is-confirm");
        etq.textContent = "Reiniciar repaso";
        marcados = {};
        guardar("repaso:" + slug, "[]");
        botonesR.forEach(pintar);
        actualizar(true);
        avisar("Repaso reiniciado. ¡A empezar de nuevo!");
      });
    }
    actualizar(false);
  })();

  /* avance de repaso en la barra lateral, las tarjetas y el resumen de la portada */
  (function () {
    var TOT = window.TOTALES || {};
    var suma = 0;
    Object.keys(TOT).forEach(function (slug) {
      var n = vistos(slug).length, p = TOT[slug] ? Math.min(1, n / TOT[slug]) : 0;
      suma += n;
      $$('[data-prog="' + slug + '"]').forEach(function (ic) {
        ic.classList.toggle("has-prog", n > 0);
        ic.style.setProperty("--pr", p.toFixed(3));
      });
      $$('[data-prog-card="' + slug + '"]').forEach(function (b) {
        if (!n) return;
        b.hidden = false;
        $("small", b).textContent = Math.round(p * 100) + " % repasado";
        var barra = $(".mprog__bar i", b);
        b.style.setProperty("--p", "0");
        setTimeout(function () { b.style.setProperty("--p", p.toFixed(3)); }, 400);
        if (barra) barra.title = n + " de " + TOT[slug] + " temas";
      });
    });
    var total = Object.keys(TOT).reduce(function (a, k) { return a + TOT[k]; }, 0);
    $$("[data-repaso-global]").forEach(function (el) {
      if (suma > 0) el.textContent = suma + " repasados · " + Math.round(suma / total * 100) + " %";
    });
  })();

  /* =========================================================== avisos flotantes */
  var toasts = $("[data-toasts]");
  function avisar(msg, op) {
    op = op || {};
    if (!toasts) return function () {};
    var t = document.createElement("div");
    t.className = "toast glass" + (op.tipo ? " toast--" + op.tipo : "");
    t.setAttribute("role", "status");
    t.innerHTML = '<span class="toast__dot" aria-hidden="true"></span><span class="toast__t">' + esc(msg) + "</span>" +
      (op.accion ? '<button class="toast__btn" type="button">' + esc(op.accion) + "</button>" : "") +
      '<button class="toast__x" type="button" aria-label="Cerrar aviso"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>';
    toasts.appendChild(t);
    if (iog) iog.observe(t);
    var cerrar = function () {
      if (t.classList.contains("is-out")) return;
      t.classList.add("is-out");
      setTimeout(function () { t.remove(); }, 420);
    };
    $(".toast__x", t).addEventListener("click", cerrar);
    if (op.accion) $(".toast__btn", t).addEventListener("click", function () { cerrar(); if (op.fn) op.fn(); });
    var vida = setTimeout(cerrar, op.ms || 3800);
    t.addEventListener("pointerenter", function () { clearTimeout(vida); });
    t.addEventListener("pointerleave", function () { vida = setTimeout(cerrar, 1800); });
    while (toasts.children.length > 3) toasts.firstChild.remove();
    pedirLuz();
    return cerrar;
  }

  /* =========================================================== sonidos de agua (Web Audio, apagados por omisión) */
  var sonidoOn = leer("sonido") === "1";
  var actx = null;
  function audio() {
    if (!actx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      try { actx = new AC(); } catch (e) { return null; }
    }
    if (actx.state === "suspended") actx.resume();
    return actx;
  }
  /* una gota real suena como una burbuja que resuena: tono que sube muy rápido y se apaga */
  function burbuja(ctx, t, f0, f1, dur, vol) {
    var o = ctx.createOscillator(), g = ctx.createGain();
    o.type = "sine";
    o.frequency.setValueAtTime(f0, t);
    o.frequency.exponentialRampToValueAtTime(f1, t + dur * 0.8);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol, t + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g);
    g.connect(ctx.destination);
    o.start(t);
    o.stop(t + dur + 0.03);
  }
  function sonar(tipo, forzar) {
    if (!sonidoOn && !forzar) return;
    var ctx = audio();
    if (!ctx) return;
    var t = ctx.currentTime + 0.01, r = Math.random();
    if (tipo === "campana") {
      [0, 0.45].forEach(function (d, k) {
        [[660, 0.15], [990, 0.06], [1320, 0.045], [1980, 0.018]].forEach(function (p) {
          var o = ctx.createOscillator(), g = ctx.createGain();
          o.type = "sine";
          o.frequency.value = p[0] * (k ? 1.26 : 1);
          g.gain.setValueAtTime(0.0001, t + d);
          g.gain.exponentialRampToValueAtTime(p[1], t + d + 0.012);
          g.gain.exponentialRampToValueAtTime(0.0001, t + d + 2);
          o.connect(g);
          g.connect(ctx.destination);
          o.start(t + d);
          o.stop(t + d + 2.1);
        });
      });
      return;
    }
    var f = { gota: [430 + r * 90, 2.7, 0.13, 0.2], suave: [300 + r * 40, 1.7, 0.1, 0.08], tab: [640 + r * 70, 1.9, 0.07, 0.06], abrir: [380, 2.4, 0.15, 0.12] }[tipo] || [520, 2, 0.08, 0.07];
    burbuja(ctx, t, f[0], f[0] * f[1], f[2], f[3]);
    if (tipo === "abrir") burbuja(ctx, t + 0.08, 560, 1500, 0.1, 0.07);
  }
  function vibrar(ms) {
    if (!COARSE || !navigator.vibrate) return;
    try { navigator.vibrate(ms); } catch (e) { /* sin vibración */ }
  }
  $$("[data-sonido]").forEach(function (b) {
    b.setAttribute("aria-pressed", sonidoOn ? "true" : "false");
    b.addEventListener("click", function () {
      sonidoOn = !sonidoOn;
      guardar("sonido", sonidoOn ? "1" : "0");
      $$("[data-sonido]").forEach(function (x) { x.setAttribute("aria-pressed", sonidoOn ? "true" : "false"); });
      if (sonidoOn) sonar("gota");
      avisar(sonidoOn ? "Sonidos de agua activados" : "Sonidos desactivados");
    });
  });
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest(".btn, .pill, .iconbtn, .dock__item, .side__motion, .side__install");
    if (b && !b.hasAttribute("data-sonido")) sonar("tab");
  });

  /* =========================================================== notificaciones del sistema (temporizador) */
  function notificar(titulo, cuerpo) {
    if (!window.Notification || Notification.permission !== "granted" || !document.hidden) return;
    var op = { body: cuerpo, icon: BASE + "assets/img/icons/icon-192.png", badge: BASE + "assets/img/icons/favicon-32.png", tag: "temporizador" };
    try {
      if (navigator.serviceWorker && navigator.serviceWorker.controller) navigator.serviceWorker.ready.then(function (r) { r.showNotification(titulo, op); });
      else new Notification(titulo, op);
    } catch (e) { /* sin notificaciones */ }
  }

  /* =========================================================== temporizador de estudio */
  var T = (function () {
    var pop = $("[data-timer]");
    var abrirB = $("[data-timer-open]");
    var chip = $("[data-timer-chip]");
    var gauge = $("[data-timer-gauge]");
    var txt = $("[data-timer-t]"), modoTxt = $("[data-timer-modo]");
    var toggle = $("[data-timer-toggle]");
    var presets = $("[data-timer-presets]");
    var lp = presets && lenteDe(presets);
    var titulo = document.title;
    var st = null, reloj = 0;
    function cargar() {
      try { st = JSON.parse(leer("temporizador") || "null"); } catch (e) { st = null; }
      if (!st || !st.preset) st = { preset: [25, 5], modo: "enfoque", fin: 0, resta: 25 * 60000 };
    }
    cargar();
    function total() { return (st.modo === "enfoque" ? st.preset[0] : st.preset[1]) * 60000; }
    function restante() { return st.fin ? Math.max(0, st.fin - Date.now()) : Math.min(st.resta, total()); }
    function hoyClave() { var d = new Date(); return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
    function sesionesHoy() {
      try { var h = JSON.parse(leer("temporizador:hoy") || "{}"); return h.d === hoyClave() ? h.n : 0; } catch (e) { return 0; }
    }
    function salvar() { guardar("temporizador", JSON.stringify(st)); }
    function mmss(ms) { var s = Math.ceil(ms / 1000); return pad(Math.floor(s / 60)) + ":" + pad(s % 60); }
    function pintar() {
      var r = restante(), corre = !!st.fin, m = mmss(r), enf = st.modo === "enfoque";
      if (txt) txt.textContent = m;
      if (modoTxt) modoTxt.textContent = enf ? "Enfoque" : "Descanso";
      if (gauge) {
        gauge.style.setProperty("--p", (r / total()).toFixed(4));
        gauge.classList.toggle("is-break", !enf);
        gauge.classList.toggle("is-high", r / total() > 0.56);
        gauge.setAttribute("aria-label", (enf ? "Enfoque" : "Descanso") + ": quedan " + m);
      }
      if (chip) { chip.hidden = !corre && r >= total(); chip.textContent = m; }
      if (abrirB) { abrirB.classList.toggle("is-running", corre); abrirB.classList.toggle("is-break", !enf); }
      if (toggle) {
        toggle.classList.toggle("is-running", corre);
        $("span", toggle).textContent = corre ? "Pausar" : r < total() ? "Continuar" : "Iniciar";
      }
      $$("[data-timer-start]").forEach(function (b) {
        b.classList.toggle("is-running", corre);
        $("span", b).textContent = corre ? (enf ? "Enfoque · " : "Descanso · ") + m : r < total() ? "Continuar · " + m : "Empezar";
      });
      $$("[data-timer-hoy]").forEach(function (el) { el.textContent = sesionesHoy(); });
      document.title = corre ? "⏱ " + m + " · " + (enf ? "Enfoque" : "Descanso") + " — " + titulo : titulo;
      var calmo = corre && enf;
      root.classList.toggle("enfoque", calmo);
      if (agua && agua.calmar) agua.calmar(calmo);
    }
    function terminar() {
      sonar("campana", true);
      vibrar([180, 90, 180]);
      if (st.modo === "enfoque") {
        guardar("temporizador:hoy", JSON.stringify({ d: hoyClave(), n: sesionesHoy() + 1 }));
        st.modo = "descanso";
        st.resta = total();
        st.fin = Date.now() + st.resta;
        avisar("¡Sesión completada! Descansa " + st.preset[1] + " minutos.", { tipo: "ok", ms: 7000 });
        notificar("¡Sesión de enfoque completada!", "Descansa " + st.preset[1] + " minutos.");
      } else {
        st.modo = "enfoque";
        st.fin = 0;
        st.resta = total();
        avisar("Se acabó el descanso. ¿Otra sesión?", { accion: "Iniciar", fn: iniciar, ms: 9000 });
        notificar("Descanso terminado", "Cuando quieras, empieza otra sesión de estudio.");
      }
      salvar();
      if (gauge) rebotar(gauge, "is-splash");
    }
    function tic() {
      if (st.fin && restante() <= 0) terminar();
      pintar();
    }
    function correr() { clearInterval(reloj); if (st.fin) reloj = setInterval(tic, 250); }
    function iniciar() {
      if (!st.fin) st.fin = Date.now() + (restante() > 0 ? restante() : total());
      salvar();
      correr();
      pintar();
      sonar("gota");
      if (!EMBED && window.Notification && Notification.permission === "default") { try { Notification.requestPermission(); } catch (e) { /* nada */ } }
    }
    function pausar() { st.resta = restante(); st.fin = 0; salvar(); correr(); pintar(); sonar("suave"); }
    function reiniciar() { st.fin = 0; st.modo = "enfoque"; st.resta = total(); salvar(); correr(); pintar(); if (gauge) rebotar(gauge, "is-splash"); }
    function saltar() {
      var corre = !!st.fin;
      st.modo = st.modo === "enfoque" ? "descanso" : "enfoque";
      st.resta = total();
      st.fin = corre ? Date.now() + st.resta : 0;
      salvar(); correr(); pintar();
    }
    function abrir(on) {
      if (!pop || pop.classList.contains("timer--inline")) return;
      var mostrar = on == null ? pop.hidden : on;
      if (mostrar === !pop.hidden) return;
      if (mostrar) {
        pop.hidden = false;
        requestAnimationFrame(function () { pop.classList.add("is-open"); });
        if (lp) lp.fijar();
        if (iog) iog.observe(pop);
        pedirLuz();
        sonar("abrir");
      } else {
        pop.classList.remove("is-open");
        setTimeout(function () { if (!pop.classList.contains("is-open")) pop.hidden = true; }, 360);
      }
      if (abrirB) abrirB.setAttribute("aria-expanded", mostrar ? "true" : "false");
    }
    if (presets) {
      $$("[data-timer-preset]", presets).forEach(function (b) {
        var v = b.getAttribute("data-timer-preset").split(",").map(Number);
        if (v[0] === st.preset[0] && v[1] === st.preset[1]) {
          if (lp) lp.activar(b);
          $$("[data-timer-preset]", presets).forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        }
        b.addEventListener("click", function () {
          st.preset = v;
          st.modo = "enfoque";
          st.fin = 0;
          st.resta = total();
          salvar(); correr();
          if (lp) lp.activar(b);
          $$("[data-timer-preset]", presets).forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
          pintar();
          sonar("tab");
          if (gauge) rebotar(gauge, "is-splash");
        });
      });
    }
    if (abrirB) abrirB.addEventListener("click", function () { abrir(); });
    document.addEventListener("click", function (e) {
      if (pop && !pop.hidden && !pop.contains(e.target) && !e.target.closest("[data-timer-open]")) abrir(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && pop && !pop.hidden) { abrir(false); if (abrirB) abrirB.focus(); }
    });
    if (toggle) toggle.addEventListener("click", function () { if (st.fin) pausar(); else iniciar(); });
    $$("[data-timer-reset]").forEach(function (b) { b.addEventListener("click", reiniciar); });
    $$("[data-timer-skip]").forEach(function (b) { b.addEventListener("click", saltar); });
    $$("[data-timer-start]").forEach(function (b) {
      b.addEventListener("click", function () {
        if (st.fin) { pausar(); return; }
        iniciar();
        if (restante() >= total() - 1500) avisar("Sesión de " + (st.modo === "enfoque" ? st.preset[0] : st.preset[1]) + " minutos en marcha. El agua se calma mientras estudias.", { accion: "Ver", fn: function () { window.scrollTo({ top: 0, behavior: REDUCE ? "auto" : "smooth" }); abrir(true); } });
      });
    });
    /* la sesión sigue en otras pestañas y al volver a la página */
    window.addEventListener("storage", function (e) { if (e.key === "temporizador" || e.key === "temporizador:hoy") { cargar(); correr(); pintar(); } });
    document.addEventListener("visibilitychange", function () { if (!document.hidden) tic(); });
    if (st.fin && Date.now() - st.fin > 10 * 60000) { st.fin = 0; st.modo = "enfoque"; st.resta = total(); salvar(); }
    correr();
    tic();
    return {
      abrir: abrir,
      enfocar: function () {
        if (st.fin && st.modo === "enfoque") { abrir(true); return; }
        st.modo = "enfoque"; st.fin = 0; st.resta = total();
        iniciar();
        abrir(true);
      }
    };
  })();

  /* =========================================================== notas por materia */
  $$("[data-notas]").forEach(function (caja) {
    var slug = caja.getAttribute("data-notas"), clave = "notas:" + slug;
    var ta = $("textarea", caja);
    var estadoEl = $("[data-notas-estado]", caja), estado = $("span", estadoEl);
    var cuenta = $("[data-notas-cuenta]", caja);
    var tab = $('[data-tab="notas"]');
    var nombre = (($(".mhero__title") || {}).textContent || slug).trim();
    ta.value = leer(clave) || "";
    function contarP() {
      var n = (ta.value.trim().match(/\S+/g) || []).length;
      cuenta.textContent = n + (n === 1 ? " palabra" : " palabras");
      if (tab) tab.classList.toggle("has-dot", n > 0);
      caja.classList.toggle("is-empty", !n);
    }
    function hora() { var d = new Date(); return pad(d.getHours()) + ":" + pad(d.getMinutes()); }
    function alto() { if (!ta.offsetParent) return; ta.style.height = "auto"; ta.style.height = Math.max(280, ta.scrollHeight + 4) + "px"; }
    estado.textContent = ta.value ? "Guardado en este navegador" : "Sin notas todavía";
    contarP();
    var espera = 0;
    function escribir(v) {
      guardar(clave, v);
      caja.classList.remove("is-saving");
      estado.textContent = v ? "Guardado · " + hora() : "Sin notas todavía";
      rebotar(estadoEl, "is-bump");
    }
    ta.addEventListener("input", function () {
      caja.classList.add("is-saving");
      estado.textContent = "Guardando…";
      clearTimeout(espera);
      espera = setTimeout(function () { escribir(ta.value); }, 450);
      contarP();
      alto();
    });
    ta.addEventListener("focus", alto);
    $$("[data-tab]").forEach(function (b) { b.addEventListener("click", function () { setTimeout(alto, 30); }); });
    $("[data-notas-copiar]", caja).addEventListener("click", function () {
      if (!ta.value.trim()) { avisar("Todavía no hay nada que copiar"); return; }
      copiarTexto(ta.value, "Notas copiadas al portapapeles");
    });
    $("[data-notas-bajar]", caja).addEventListener("click", function () {
      if (!ta.value.trim()) { avisar("Todavía no hay nada que descargar"); return; }
      var fecha = new Date().toLocaleDateString("es-MX");
      var blob = new Blob(["Mis notas · " + nombre + "\nMapa del Semestre 1A · " + fecha + "\n\n" + ta.value + "\n"], { type: "text/plain;charset=utf-8" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "notas-" + slug + ".txt";
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 400);
      avisar("Descargando notas-" + slug + ".txt", { tipo: "ok" });
    });
    var borrar = $("[data-notas-borrar]", caja), confirmar = 0;
    borrar.addEventListener("click", function () {
      if (!ta.value.trim()) { avisar("No hay notas que borrar"); return; }
      var etq = $("span", borrar);
      if (!borrar.classList.contains("is-confirm")) {
        borrar.classList.add("is-confirm");
        etq.textContent = "¿Seguro? Toca otra vez";
        confirmar = setTimeout(function () { borrar.classList.remove("is-confirm"); etq.textContent = "Borrar"; }, 3000);
        return;
      }
      clearTimeout(confirmar);
      borrar.classList.remove("is-confirm");
      etq.textContent = "Borrar";
      var antes = ta.value;
      ta.value = "";
      escribir("");
      contarP();
      alto();
      avisar("Notas borradas", { accion: "Deshacer", ms: 7000, fn: function () { ta.value = antes; escribir(antes); contarP(); alto(); } });
    });
  });

  /* =========================================================== compartir, imprimir y atajos de la materia */
  function copiarTexto(texto, msg) {
    var fallo = function () { avisar("No se pudo copiar. Selecciona el texto y cópialo a mano."); };
    try { navigator.clipboard.writeText(texto).then(function () { avisar(msg, { tipo: "ok" }); }, fallo); } catch (e) { fallo(); }
  }
  function compartir() {
    var desc = $('meta[name="description"]');
    var datos = { title: document.title, text: desc ? desc.content : "", url: location.href.split("#")[0] };
    if (navigator.share) { navigator.share(datos).catch(function () { /* cancelado */ }); return; }
    try {
      navigator.clipboard.writeText(datos.url).then(function () { avisar("Enlace copiado. ¡Compártelo con tu equipo!", { tipo: "ok" }); },
        function () { avisar("Copia este enlace: " + datos.url, { ms: 9000 }); });
    } catch (e) { avisar("Copia este enlace: " + datos.url, { ms: 9000 }); }
  }
  $$("[data-share]").forEach(function (b) { b.addEventListener("click", compartir); });
  $$("[data-print]").forEach(function (b) { b.addEventListener("click", function () { window.print(); }); });
  function irPestana(id) {
    mostrarPanel(id);
    marcarHash("#" + id);
    var barra = $(".tabsbar");
    if (barra) barra.scrollIntoView({ block: "start", behavior: REDUCE ? "auto" : "smooth" });
    if (id === "notas") setTimeout(function () { var ta = $("[data-notas] textarea"); if (ta) ta.focus({ preventScroll: true }); }, 450);
  }
  $$("[data-ir-tab]").forEach(function (b) { b.addEventListener("click", function () { irPestana(b.getAttribute("data-ir-tab")); }); });

  /* deslizar el dedo sobre el contenido cambia de pestaña */
  (function () {
    var tabsC = $("[data-tabs]"), pan = $("[data-panels]");
    if (!tabsC || !pan) return;
    var x0 = null, y0 = 0, t0 = 0;
    pan.addEventListener("touchstart", function (e) {
      if (e.touches.length !== 1 || e.target.closest("textarea, input, pre, table, .seg")) { x0 = null; return; }
      x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; t0 = Date.now();
    }, { passive: true });
    pan.addEventListener("touchend", function (e) {
      if (x0 == null) return;
      var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
      x0 = null;
      if (Math.abs(dx) < 70 || Math.abs(dy) > Math.abs(dx) * 0.6 || Date.now() - t0 > 700) return;
      var bs = $$("[data-tab]", tabsC);
      var i = bs.map(function (b) { return b.getAttribute("aria-selected"); }).indexOf("true");
      var sig = bs[i + (dx < 0 ? 1 : -1)];
      if (!sig) { rebotar(pan, dx < 0 ? "is-edge-r" : "is-edge-l"); return; }
      var id = sig.getAttribute("data-tab");
      mostrarPanel(id);
      marcarHash("#" + id);
      var p = document.getElementById(id);
      if (p) rebotar(p, dx < 0 ? "is-swipe-l" : "is-swipe-r");
      sonar("tab");
      vibrar(6);
      var barra = $(".tabsbar");
      if (barra && pan.getBoundingClientRect().top < 0) barra.scrollIntoView({ block: "start", behavior: REDUCE ? "auto" : "smooth" });
    }, { passive: true });
  })();

  /* =========================================================== portada: "tu día" */
  (function () {
    var hoy0 = new Date();
    hoy0.setHours(0, 0, 0, 0);
    function fechaLocal(iso) { var p = iso.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }

    var caja = $("[data-nexteval]");
    if (caja) {
      var e = (window.EVALUACIONES || []).filter(function (x) { return x.s >= Math.max(SEMANA, 1); })[0];
      var set = function (sel, v) { var el = $(sel, caja); if (el) el.textContent = v; };
      var g = $("[data-nexteval-gauge]", caja), p = 1;
      if (!e) {
        set("[data-nexteval-t]", "Sin evaluaciones pendientes");
        set("[data-nexteval-m]", "El plan de Física ya terminó. ¡Buen cierre de ciclo!");
        set("[data-nexteval-c]", "");
        set("[data-nexteval-d]", "✓");
        set("[data-nexteval-u]", "listo");
      } else {
        var dias = Math.round((fechaLocal(e.ini) - hoy0) / DIA);
        set("[data-nexteval-t]", e.n);
        set("[data-nexteval-m]", "Física · Semana " + e.s + " · " + e.f + " · " + e.pts.toFixed(1) + " pts");
        if (e.s === SEMANA || dias <= 0) {
          set("[data-nexteval-c]", "Esta semana · ¡prepárate!");
          set("[data-nexteval-d]", "¡Ya!");
          set("[data-nexteval-u]", "esta semana");
          caja.classList.add("is-soon");
        } else {
          set("[data-nexteval-c]", dias <= 7 ? "La próxima semana" : "En " + Math.round(dias / 7) + " semanas");
          set("[data-nexteval-d]", dias);
          set("[data-nexteval-u]", dias === 1 ? "día" : "días");
          p = clamp(1 - dias / 42, 0.06, 1);
          caja.classList.toggle("is-soon", dias <= 7);
        }
        var mas = $("[data-nexteval-more]", caja);
        var SLOT = { examen: "s1", act: "s2", tarea: "s3", integrador: "s4", part: "s5" };
        var lista = window.EVALUACIONES || [];
        var siguientes = lista.slice(lista.indexOf(e) + 1, lista.indexOf(e) + 3);
        var cierre = SEMANAS[17];
        if (mas) {
          mas.innerHTML = '<li class="nexteval__k">Después</li>' + siguientes.map(function (x) {
            return '<li style="--c:var(--' + (SLOT[x.k] || "s1") + ')"><i></i><span>' + esc(x.n) + "</span><small>Sem " + x.s + " · " + esc(x.f) + "</small></li>";
          }).join("") + (siguientes.length < 2 && cierre ? '<li style="--c:#5fd38a"><i></i><span>Cierre del ciclo y calificaciones</span><small>Sem 18 · ' + esc(cierre.f) + "</small></li>" : "");
        }
      }
      if (g) {
        g.style.setProperty("--p", "0");
        setTimeout(function () { g.style.setProperty("--p", p.toFixed(3)); }, REDUCE ? 0 : 500);
      }
    }

    var minis = $$("[data-mini]");
    if (minis.length) {
      var TOT = window.TOTALES || {}, suma = 0, tot = 0, sugerida = null, empezadas = 0;
      (window.MATERIAS || []).forEach(function (m) {
        var T2 = TOT[m.s] || 1, n = Math.min(vistos(m.s).length, T2), pr = n / T2;
        suma += n; tot += T2;
        if (n > 0 && pr < 1) empezadas++;
        var el = $('[data-mini="' + m.s + '"]');
        if (el) {
          var o = $(".mini__orb", el);
          setTimeout(function () { o.style.setProperty("--p", pr.toFixed(3)); }, REDUCE ? 0 : 600);
          $("[data-mini-p]", el).textContent = Math.round(pr * 100) + " %";
          el.classList.toggle("is-done", pr >= 1);
          el.setAttribute("aria-label", m.n + ": " + Math.round(pr * 100) + " % repasado");
        }
        var cand = { m: m, p: pr, n: n };
        if (pr < 1 && (!sugerida || (n > 0 && (sugerida.n === 0 || pr < sugerida.p)))) sugerida = cand;
      });
      $$("[data-repaso-total]").forEach(function (el) { el.textContent = Math.round(suma / tot * 100) + " %"; });
      var sug = $("[data-repaso-sug]");
      if (sug) {
        var enlace = sugerida ? '<a href="materias/' + sugerida.m.s + '.html" style="--acc:' + sugerida.m.col + '">' + esc(sugerida.m.n) + "</a>" : "";
        if (!sugerida) sug.textContent = "¡Repasaste todo el temario del semestre! Excelente trabajo.";
        else if (!suma) sug.innerHTML = "Aún no marcas temas. Empieza por " + enlace + " y toca el círculo de cada tema que repases.";
        else sug.innerHTML = "Sugerencia: sigue con " + enlace + ", llevas " + Math.round(sugerida.p * 100) + " %." + (empezadas > 1 ? " Tienes " + empezadas + " materias en curso." : "");
      }
    }
  })();

  /* =========================================================== página del calendario */
  (function () {
    $$("[data-cierre]").forEach(function (el) {
      var hoy0 = new Date();
      hoy0.setHours(0, 0, 0, 0);
      el.textContent = Math.max(0, Math.round((new Date(2026, 11, 18) - hoy0) / DIA));
    });
    $$(".evl").forEach(function (li) {
      var a = $("a", li), s = +(a.getAttribute("href").split("sem-")[1] || 0);
      li.classList.toggle("is-past", s < SEMANA);
      li.classList.toggle("is-now", s === SEMANA);
    });
    $$("[data-ir-semana]").forEach(function (b) {
      b.addEventListener("click", function () {
        var w = $(".cal__w.is-now") || (SEMANA > 18 ? $("#sem-18") : $("#sem-1"));
        if (w) marcarHash("#" + w.id);
        resaltarSemana(w);
      });
    });
    $$('a[href^="#sem-"]').forEach(function (a) {
      a.addEventListener("click", function (e) {
        var w = document.getElementById(a.getAttribute("href").slice(1));
        if (!w) return;
        e.preventDefault();
        marcarHash(a.getAttribute("href"));
        resaltarSemana(w);
        sonar("gota");
      });
    });
  })();

  /* =========================================================== páginas recientes (para la paleta) */
  var ACTUAL = null;
  (function () {
    var cls = document.body.classList, h = null, t = "", c = "#ffc35c";
    var rep = $("[data-repaso]");
    if (rep) {
      var sl = rep.getAttribute("data-repaso");
      var M = (window.MATERIAS || []).filter(function (x) { return x.s === sl; })[0];
      if (M) { h = "materias/" + sl + ".html"; t = M.n; c = M.col; }
    } else if (cls.contains("cal-page")) { h = "calendario.html"; t = "Calendario del ciclo"; c = "#ff9a3d"; }
    else if (cls.contains("team-page")) { h = "equipo.html"; t = "Equipo"; c = "#3b5bff"; }
    else if (cls.contains("home")) { ACTUAL = "index.html"; }
    if (!h) return;
    ACTUAL = h;
    var lista = [];
    try { lista = JSON.parse(leer("recientes") || "[]"); } catch (e) { lista = []; }
    lista = lista.filter(function (x) { return x && x.h !== h; });
    lista.unshift({ h: h, t: t, c: c });
    guardar("recientes", JSON.stringify(lista.slice(0, 6)));
  })();

  /* =========================================================== app instalable */
  var instalar = null;
  function pedirInstalar() {
    if (instalar) {
      instalar.prompt();
      instalar.userChoice.then(function () { instalar = null; $$("[data-install]").forEach(function (b) { b.hidden = true; }); }, function () {});
    } else if (/iphone|ipad|ipod/i.test(navigator.userAgent)) {
      avisar("En iPhone: toca Compartir y luego «Agregar a pantalla de inicio».", { ms: 8000 });
    } else {
      avisar("Abre el menú del navegador y elige «Instalar» o «Agregar a la pantalla de inicio».", { ms: 8000 });
    }
  }
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    instalar = e;
    $$("[data-install]").forEach(function (b) { b.hidden = false; rebotar(b, "is-jelly"); });
  });
  $$("[data-install]").forEach(function (b) { b.addEventListener("click", pedirInstalar); });
  window.addEventListener("appinstalled", function () {
    instalar = null;
    $$("[data-install]").forEach(function (b) { b.hidden = true; });
    avisar("¡Listo! El Mapa del Semestre ya está instalado como app.", { tipo: "ok" });
  });

  /* =========================================================== sin conexión y actualizaciones */
  if (WEB && !EMBED && "serviceWorker" in navigator) {
    var recargar = false;
    window.addEventListener("load", function () {
      navigator.serviceWorker.register(BASE + "sw.js").then(function (reg) {
        var ofrecer = function (w) {
          avisar("Hay una versión nueva del sitio.", { accion: "Actualizar", ms: 15000, fn: function () { recargar = true; w.postMessage("actualizar"); } });
        };
        if (reg.waiting && navigator.serviceWorker.controller) ofrecer(reg.waiting);
        reg.addEventListener("updatefound", function () {
          var w = reg.installing;
          if (!w) return;
          w.addEventListener("statechange", function () {
            if (w.state !== "installed") return;
            if (navigator.serviceWorker.controller) ofrecer(w);
            else if (leer("sin-conexion") !== "1") { guardar("sin-conexion", "1"); avisar("Listo: el sitio ya funciona sin internet en este dispositivo.", { tipo: "ok", ms: 5000 }); }
          });
        });
      }).catch(function () { /* sin service worker */ });
      navigator.serviceWorker.addEventListener("controllerchange", function () { if (recargar) location.reload(); });
    });
  }
  window.addEventListener("offline", function () { avisar("Sin conexión. Las páginas que ya visitaste siguen disponibles."); });
  window.addEventListener("online", function () { avisar("Conexión recuperada", { tipo: "ok" }); });

  /* =========================================================== paleta de comandos (Ctrl K) */
  var MAC = /mac|iphone|ipad/i.test(navigator.platform || navigator.userAgent);
  $$("[data-kbd]").forEach(function (k) { k.textContent = MAC ? "⌘ K" : "Ctrl K"; });
  $$(".foot__key kbd").forEach(function (k) { if (k.textContent === "Ctrl K") k.textContent = MAC ? "⌘ K" : "Ctrl K"; });
  var pal = $("[data-pal]");
  var abrirPal = function () {}, cerrarPal = function () {};
  if (pal) (function () {
    var q = $("#pal-q", pal), lista = $("#pal-lista", pal), cuentaP = $("[data-pal-count]", pal);
    var plantilla = $("#pal-iconos", pal);
    var ICON = {};
    if (plantilla && plantilla.content) $$("[data-i]", plantilla.content).forEach(function (i) { ICON[i.getAttribute("data-i")] = i.innerHTML; });
    var sinAcento = function (s) { return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
    var INDICE = window.INDICE || [];
    INDICE.forEach(function (it) { it.n = sinAcento(it.t + " " + it.m); it.nt = sinAcento(it.t); });
    var ICON_MATERIA = {};
    $$(".side__item[data-li]").forEach(function (a) {
      var m = (a.getAttribute("href") || "").match(/materias\/([a-z]+)\.html$/);
      var svg = $(".side__ic svg", a);
      if (m && svg) ICON_MATERIA[m[1]] = svg.outerHTML;
    });
    var semanaIr = clamp(SEMANA, 1, 18);
    var ACCIONES = [
      { t: "Ir al inicio", m: "Página", i: "house", h: "index.html", k: "inicio portada principal home" },
      { t: "Calendario del ciclo", m: "Página", i: "calendar-days", h: "calendario.html", k: "semanas fechas examenes evaluaciones fisica" },
      { t: "Ir a esta semana (" + semanaIr + ")", m: "Calendario", i: "crosshair", h: "calendario.html#sem-" + semanaIr, k: "hoy semana actual que toca" },
      { t: "Equipo", m: "Página", i: "users", h: "equipo.html", k: "integrantes nombres companeros" },
      { t: "Empezar sesión de estudio", m: "Temporizador", i: "timer", fn: function () { T.enfocar(); }, k: "pomodoro enfoque estudiar concentrar timer reloj" },
      { t: "Abrir temporizador", m: "Temporizador", i: "clock-3", fn: function () { T.abrir(true); }, k: "pomodoro timer descanso tecla t" },
      { t: function () { return calma ? "Activar efecto líquido" : "Pausar efecto líquido"; }, m: "Ajustes", i: "droplets", fn: function () { var b = $("[data-calma]"); if (b) b.click(); }, k: "agua animaciones movimiento calma rendimiento" },
      { t: function () { return sonidoOn ? "Desactivar sonidos" : "Activar sonidos de agua"; }, m: "Ajustes", i: "volume-2", fn: function () { var b = $("[data-sonido]"); if (b) b.click(); }, k: "audio sonido silencio" },
      { t: "Descargar calendario (.ics)", m: "Calendario", i: "download", h: "assets/calendario-2026b.ics", descarga: true, k: "google calendar outlook recordatorios agregar" },
      { t: "Instalar como app", m: "Ajustes", i: "monitor-down", fn: pedirInstalar, k: "pwa instalar celular escritorio sin conexion offline" }
    ];
    if ($("[data-notas]")) ACCIONES.unshift({ t: "Mis notas de esta materia", m: "Materia", i: "notebook-pen", fn: function () { irPestana("notas"); }, k: "apuntes notas escribir" });
    if ($("[data-print]")) ACCIONES.push({ t: "Imprimir temario", m: "Materia", i: "printer", fn: function () { setTimeout(function () { window.print(); }, 380); }, k: "imprimir pdf papel" });
    if ($("[data-share]")) ACCIONES.push({ t: "Compartir esta página", m: "Página", i: "share-2", fn: compartir, k: "compartir enlace link whatsapp" });
    ACCIONES.forEach(function (a) { a.accion = true; });
    function titulo(a) { return typeof a.t === "function" ? a.t() : a.t; }

    var opciones = [], sel = 0, abridor = null;
    function resaltar(texto, terminos) {
      if (!terminos.length) return esc(texto);
      var chars = Array.from(texto);
      var norm = chars.map(function (c) { return sinAcento(c) || c; });
      var marca = new Array(chars.length).fill(false);
      var plano = norm.join(""), mapa = [];
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
    }
    function icono(o) {
      if (o.i && ICON[o.i]) return '<span class="pal__ic">' + ICON[o.i] + "</span>";
      if (o.k === "materia") { var slug = (o.h.match(/materias\/([a-z]+)\.html/) || [])[1]; if (ICON_MATERIA[slug]) return '<span class="pal__ic pal__ic--acc">' + ICON_MATERIA[slug] + "</span>"; }
      if (o.k === "unidad" && ICON.layers) return '<span class="pal__ic pal__ic--acc">' + ICON.layers + "</span>";
      return '<span class="pal__ic pal__ic--dot"><i></i></span>';
    }
    function fila(o, i, terminos) {
      var dentro = icono(o) + '<span class="pal__tx"><b>' + resaltar(titulo(o), terminos) + "</b><small>" + esc(o.m) + "</small></span>" +
        '<kbd class="pal__go" aria-hidden="true">↵</kbd>';
      var attrs = ' class="pal__it" role="option" id="pal-o-' + i + '" data-o="' + i + '" aria-selected="false" style="--c:' + (o.c || "var(--gold)") + ";--i:" + Math.min(i, 12) + '"';
      if (o.h) return "<a" + attrs + ' href="' + esc(BASE + o.h) + '"' + (o.descarga ? " download" : "") + ">" + dentro + "</a>";
      return '<button type="button"' + attrs + ">" + dentro + "</button>";
    }
    function grupo(nombre, items, terminos) {
      if (!items.length) return "";
      var html = '<p class="pal__g">' + nombre + "</p>";
      items.forEach(function (o) { opciones.push(o); html += fila(o, opciones.length - 1, terminos); });
      return html;
    }
    function buscar() {
      var texto = q.value.trim();
      var terminos = sinAcento(texto).split(/\s+/).filter(Boolean);
      opciones = [];
      var html = "";
      if (!terminos.length) {
        var rec = [];
        try { rec = JSON.parse(leer("recientes") || "[]"); } catch (e) { rec = []; }
        rec = rec.filter(function (r) { return r && r.h && r.h !== ACTUAL; }).slice(0, 4).map(function (r) {
          var esM = /^materias\//.test(r.h);
          return { t: r.t, m: esM ? "Visitada hace poco · Materia" : "Visitada hace poco", h: r.h, c: r.c, k: esM ? "materia" : "", i: esM ? null : (r.h === "equipo.html" ? "users" : "calendar-days") };
        });
        html += grupo("Recientes", rec, []);
        html += grupo("Acciones", ACCIONES.slice(0, 7), []);
        html += grupo("Materias", INDICE.filter(function (it) { return it.k === "materia"; }), []);
      } else {
        var acc = ACCIONES.filter(function (a) {
          var n = sinAcento(titulo(a) + " " + a.m + " " + a.k);
          return terminos.every(function (t) { return n.indexOf(t) !== -1; });
        }).slice(0, 4);
        var res = INDICE.filter(function (it) { return terminos.every(function (t) { return it.n.indexOf(t) !== -1; }); })
          .map(function (it) {
            var p = 0;
            if (it.nt.indexOf(terminos[0]) === 0) p -= 3;
            else if (it.nt.indexOf(" " + terminos[0]) !== -1) p -= 1.5;
            if (it.k === "materia") p -= 2.5;
            if (it.k === "unidad") p -= 1;
            p += it.t.length / 200;
            return { it: it, p: p };
          })
          .sort(function (a, b) { return a.p - b.p; });
        var total = res.length;
        html += grupo("Temario", res.slice(0, 12).map(function (x) { return x.it; }), terminos);
        html += grupo("Acciones", acc, terminos);
        if (!opciones.length) html = '<div class="pal__empty"><b>Sin resultados para «' + esc(texto) + '»</b><span>Prueba con otra palabra, por ejemplo «vectores», «PSeInt» o «examen».</span></div>';
        if (cuentaP) cuentaP.textContent = total ? total + (total === 1 ? " tema" : " temas") : "";
      }
      if (!terminos.length && cuentaP) cuentaP.textContent = INDICE.length + " temas en el índice";
      lista.innerHTML = html;
      sel = 0;
      pintarSel(false);
    }
    function pintarSel(desplazar) {
      $$(".pal__it", lista).forEach(function (el, i) { el.setAttribute("aria-selected", i === sel ? "true" : "false"); });
      var el = $("#pal-o-" + sel, lista);
      if (el) {
        q.setAttribute("aria-activedescendant", el.id);
        if (desplazar !== false) el.scrollIntoView({ block: "nearest" });
      } else q.removeAttribute("aria-activedescendant");
    }
    function activar(i, nueva) {
      var o = opciones[i];
      if (!o) return;
      var el = $("#pal-o-" + i, lista);
      if (o.h) {
        cerrarPal(true);
        if (o.descarga) { el.click(); return; }
        if (nueva) window.open(BASE + o.h, "_blank");
        else location.href = BASE + o.h;
        return;
      }
      cerrarPal(true);
      if (o.fn) o.fn();
    }
    abrirPal = function () {
      if (!pal.hidden) { q.select(); return; }
      abridor = document.activeElement;
      pal.hidden = false;
      root.classList.add("pal-open");
      q.value = "";
      buscar();
      requestAnimationFrame(function () { pal.classList.add("is-open"); });
      q.focus();
      sonar("abrir");
      vibrar(8);
    };
    cerrarPal = function (sinFoco) {
      if (pal.hidden) return;
      pal.classList.remove("is-open");
      root.classList.remove("pal-open");
      setTimeout(function () { if (!pal.classList.contains("is-open")) pal.hidden = true; }, 300);
      if (!sinFoco && abridor && abridor.focus) abridor.focus({ preventScroll: true });
    };
    q.addEventListener("input", buscar);
    q.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!opciones.length) return;
        sel = (sel + (e.key === "ArrowDown" ? 1 : -1) + opciones.length) % opciones.length;
        pintarSel();
      } else if (e.key === "Enter") {
        e.preventDefault();
        activar(sel, e.ctrlKey || e.metaKey);
      } else if (e.key === "Escape") {
        e.preventDefault();
        cerrarPal();
      } else if (e.key === "Tab") {
        e.preventDefault();
      }
    });
    lista.addEventListener("pointermove", function (e) {
      var it = e.target.closest(".pal__it");
      if (!it) return;
      var i = +it.getAttribute("data-o");
      if (i !== sel) { sel = i; pintarSel(false); }
    });
    lista.addEventListener("click", function (e) {
      var it = e.target.closest(".pal__it");
      if (!it) return;
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1) return;
      e.preventDefault();
      activar(+it.getAttribute("data-o"));
    });
    $$("[data-pal-close]", pal).forEach(function (s) { s.addEventListener("click", function () { cerrarPal(); }); });
    $$("[data-pal-open]").forEach(function (b) { b.addEventListener("click", function () { abrirPal(); }); });
  })();

  /* =========================================================== atajos de teclado */
  document.addEventListener("keydown", function (e) {
    if (EMBED) return;
    var a = document.activeElement || {};
    var escribiendo = /input|textarea|select/i.test(a.tagName || "") || a.isContentEditable;
    if ((e.ctrlKey || e.metaKey) && !e.altKey && (e.key === "k" || e.key === "K")) {
      e.preventDefault();
      if (pal && !pal.hidden) cerrarPal(); else abrirPal();
      return;
    }
    if (escribiendo || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key === "/") { e.preventDefault(); abrirPal(); }
    else if (e.key === "t" || e.key === "T") { e.preventDefault(); T.abrir(); }
  });
})();
