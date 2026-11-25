/* Genera los íconos de la app (PWA) y las vistas previas para compartir (Open Graph).

   Uso (después de  python3 src/build.py):
       node src/generar_imagenes.js

   Necesita Node.js y Playwright con Chromium:
       npm i -D playwright && npx playwright install chromium

   Lee src/og_paginas.json (lo escribe build.py) y produce:
       assets/img/icons/icon-192.png, icon-512.png, icon-maskable-512.png,
                        apple-touch-icon.png (180), favicon-32.png
       assets/img/og/<página>.jpg   1200 × 630, una por página
   Las imágenes ya vienen generadas en el repositorio; solo hace falta volver a
   ejecutarlo si cambian los nombres, el dominio o las fotos. */
const fs = require("fs");
const os = require("os");
const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

const RAIZ = path.resolve(__dirname, "..");
const url = (p) => pathToFileURL(path.join(RAIZ, p)).href;
const paginas = JSON.parse(fs.readFileSync(path.join(RAIZ, "src/og_paginas.json"), "utf8"));
const contenido = fs.readFileSync(path.join(RAIZ, "src/contenido.py"), "utf8");
const dominio = ((contenido.match(/"url":\s*"([^"]*)"/) || [])[1] || "").replace(/^https?:\/\//, "").replace(/\/$/, "");

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

const BASE = `
@font-face { font-family: Geist; src: url("${url("assets/fonts/geist.woff2")}") format("woff2"); font-weight: 100 900; }
@font-face { font-family: "Geist Mono"; src: url("${url("assets/fonts/geist-mono.woff2")}") format("woff2"); font-weight: 100 900; }
* { box-sizing: border-box; margin: 0; }
html, body { background: transparent; font-family: Geist, system-ui, sans-serif; color: #f5f7fc; -webkit-font-smoothing: antialiased; }
`;

/* ---------------- ícono: gota de vidrio azul con "1A" y una gota dorada ---------------- */
function icono(lado, { maskable = false, plano = false } = {}) {
  // maskable: fondo a sangre y contenido dentro del 80 % central (zona segura)
  const caja = maskable || plano ? lado : Math.round(lado * 0.9);
  const radio = maskable || plano ? 0 : Math.round(caja * 0.27);
  const escala = maskable ? 0.74 : plano ? 0.86 : 1;
  return `<!doctype html><html><head><style>${BASE}
  body { width: ${lado}px; height: ${lado}px; display: grid; place-items: center; }
  .i { position: relative; width: ${caja}px; height: ${caja}px; border-radius: ${radio}px; overflow: hidden;
       background:
         radial-gradient(120% 85% at 28% 4%, rgba(255,255,255,.55), rgba(255,255,255,0) 46%),
         radial-gradient(90% 70% at 85% 110%, rgba(139,79,240,.75), rgba(139,79,240,0) 60%),
         linear-gradient(150deg, #5d78ff, #2a3fc9 55%, #1a2690);
       box-shadow: inset 0 ${caja * 0.012}px ${caja * 0.012}px rgba(255,255,255,.7), inset 0 -${caja * 0.04}px ${caja * 0.09}px rgba(0,0,0,.28); }
  .i::before { content: ""; position: absolute; inset: 0; border-radius: inherit; box-shadow: inset 0 0 0 ${Math.max(1, caja * 0.008)}px rgba(255,255,255,.28); }
  .c { position: absolute; inset: 0; display: grid; place-items: center; transform: scale(${escala}); }
  .t { font-weight: 800; font-size: ${caja * 0.46}px; letter-spacing: -0.06em; line-height: 1; transform: translate(-${caja * 0.02}px, ${caja * 0.035}px);
       text-shadow: 0 ${caja * 0.02}px ${caja * 0.05}px rgba(10,20,80,.45); }
  .g { position: absolute; width: ${caja * 0.2}px; height: ${caja * 0.2}px; right: ${caja * 0.13}px; top: ${caja * 0.12}px; border-radius: 50%;
       background: radial-gradient(circle at 35% 30%, #fff6dc, #ffc35c 45%, #ff8a3d);
       box-shadow: 0 0 ${caja * 0.06}px rgba(255,195,92,.8), inset 0 -${caja * 0.01}px ${caja * 0.02}px rgba(160,60,0,.4); }
  .g::after { content: ""; position: absolute; left: 22%; top: 16%; width: 30%; height: 24%; border-radius: 50%; background: rgba(255,255,255,.85); filter: blur(${caja * 0.004}px); }
  .w { position: absolute; left: -10%; right: -10%; bottom: -${caja * 0.08}px; height: ${caja * 0.3}px; border-radius: 45%;
       background: linear-gradient(180deg, rgba(255,255,255,.22), rgba(255,255,255,0)); transform: rotate(-4deg); }
  </style></head><body><div class="i"><span class="w"></span><div class="c"><span class="t">1A</span><span class="g"></span></div></div></body></html>`;
}

/* ---------------- vista previa al compartir (1200 × 630) ---------------- */
function og(d) {
  const hex = d.color.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16));
  const rgb = `${r},${g},${b}`;
  return `<!doctype html><html><head><style>${BASE}
  body { width: 1200px; height: 630px; overflow: hidden; background: #05070d; position: relative; }
  .ph { position: absolute; inset: -20px; background: url("${url(`assets/img/fotos/${d.foto}.jpg`)}") center/cover; filter: saturate(1.15) brightness(.78); transform: scale(1.04); }
  .sh { position: absolute; inset: 0; background:
        linear-gradient(90deg, rgba(5,7,13,.92) 0%, rgba(5,7,13,.72) 42%, rgba(5,7,13,.18) 78%, rgba(5,7,13,.35) 100%),
        radial-gradient(60% 80% at 8% 100%, rgba(${rgb},.5), rgba(${rgb},0) 70%),
        linear-gradient(0deg, rgba(5,7,13,.6), rgba(5,7,13,0) 40%); }
  .rip { position: absolute; border-radius: 50%; border: 1.5px solid rgba(255,255,255,.18); box-shadow: 0 0 40px rgba(${rgb},.25) inset; }
  .orb { position: absolute; right: 120px; top: 150px; width: 260px; height: 260px; border-radius: 50%;
         background: radial-gradient(circle at 32% 26%, rgba(255,255,255,.55), rgba(255,255,255,.06) 32%, rgba(${rgb},.28) 70%, rgba(${rgb},.5));
         box-shadow: inset 0 2px 3px rgba(255,255,255,.7), inset 0 -24px 50px rgba(0,0,0,.35), 0 40px 80px -30px rgba(${rgb},.9);
         backdrop-filter: blur(6px) saturate(1.6); }
  .orb::after { content: ""; position: absolute; left: 18%; top: 12%; width: 34%; height: 20%; border-radius: 50%; background: rgba(255,255,255,.55); filter: blur(6px); transform: rotate(-24deg); }
  .card { position: absolute; left: 64px; top: 64px; bottom: 64px; width: 700px; padding: 44px 48px; border-radius: 36px;
          background: linear-gradient(160deg, rgba(255,255,255,.14), rgba(255,255,255,.04) 60%), rgba(10,14,26,.38);
          backdrop-filter: blur(28px) saturate(1.7);
          box-shadow: inset 0 1px 0 rgba(255,255,255,.35), inset 0 0 0 1px rgba(255,255,255,.1), 0 40px 90px -40px rgba(0,0,0,.9);
          display: flex; flex-direction: column; }
  .card::before { content: ""; position: absolute; inset: 0; border-radius: inherit; padding: 1.5px;
          background: conic-gradient(from 210deg, rgba(255,255,255,.65), rgba(255,255,255,.08) 25%, rgba(${rgb},.6) 50%, rgba(255,255,255,.08) 75%, rgba(255,255,255,.65));
          -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor; mask-composite: exclude; }
  .brand { display: flex; align-items: center; gap: 14px; font-weight: 650; font-size: 22px; letter-spacing: -.01em; }
  .mk { position: relative; width: 46px; height: 46px; border-radius: 14px; display: grid; place-items: center; font-weight: 800; font-size: 19px; letter-spacing: -.05em;
        background: radial-gradient(120% 90% at 30% 10%, rgba(255,255,255,.55), rgba(255,255,255,0) 45%), linear-gradient(150deg, #5d78ff, #2a3fc9);
        box-shadow: inset 0 1px 1px rgba(255,255,255,.6), 0 12px 24px -10px #3b5bff; }
  .mk::after { content: ""; position: absolute; top: -4px; right: -4px; width: 13px; height: 13px; border-radius: 50%; background: #ffc35c; box-shadow: 0 0 12px #ffc35c; }
  .eb { margin-top: auto; font: 500 17px "Geist Mono", monospace; letter-spacing: .16em; text-transform: uppercase; color: rgba(${rgb},1); filter: brightness(1.35) saturate(1.1); }
  h1 { margin-top: 14px; font-size: ${d.titulo.length > 30 ? 58 : d.titulo.length > 20 ? 66 : 74}px; line-height: 1.02; letter-spacing: -.04em; font-weight: 700;
       background: linear-gradient(180deg, #fff 30%, rgba(225,232,255,.82)); -webkit-background-clip: text; color: transparent; }
  .sub { margin-top: 18px; font-size: 23px; line-height: 1.35; color: rgba(245,247,252,.78); }
  .ft { margin-top: 30px; display: flex; gap: 10px; flex-wrap: wrap; }
  .pl { padding: 8px 16px; border-radius: 99px; font: 500 15px "Geist Mono", monospace; letter-spacing: .06em; color: rgba(245,247,252,.85);
        background: rgba(255,255,255,.08); box-shadow: inset 0 0 0 1px rgba(255,255,255,.14), inset 0 1px 0 rgba(255,255,255,.2); }
  .pl b { color: #ffc35c; font-weight: 600; }
  </style></head><body>
  <div class="ph"></div><div class="sh"></div>
  <span class="rip" style="right:30px;top:40px;width:520px;height:520px"></span>
  <span class="rip" style="right:100px;top:110px;width:380px;height:380px;opacity:.7"></span>
  <span class="rip" style="right:-120px;top:-110px;width:820px;height:820px;opacity:.4"></span>
  <div class="orb"></div>
  <div class="card">
    <div class="brand"><span class="mk">1A</span>Mapa del Semestre</div>
    <p class="eb">${esc(d.eyebrow)}</p>
    <h1>${esc(d.titulo)}</h1>
    <p class="sub">${esc(d.sub)}</p>
    <div class="ft"><span class="pl"><b>●</b> Ciclo 2026B</span><span class="pl">TSIN1AM</span>${dominio ? `<span class="pl">${esc(dominio)}</span>` : ""}</div>
  </div>
  </body></html>`;
}

async function foto(navegador, htmlTexto, { ancho, alto, salida, tipo = "png", transparente = false }) {
  const tmp = path.join(os.tmpdir(), `img-${process.pid}-${Math.random().toString(36).slice(2)}.html`);
  fs.writeFileSync(tmp, htmlTexto);
  const page = await navegador.newPage({ viewport: { width: ancho, height: alto }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(tmp).href);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(150);
  fs.mkdirSync(path.dirname(salida), { recursive: true });
  await page.screenshot({ path: salida, type: tipo, quality: tipo === "jpeg" ? 84 : undefined, omitBackground: transparente });
  await page.close();
  fs.unlinkSync(tmp);
  console.log("✓", path.relative(RAIZ, salida));
}

(async () => {
  const navegador = await chromium.launch();
  const ic = (n) => path.join(RAIZ, "assets/img/icons", n);
  await foto(navegador, icono(512), { ancho: 512, alto: 512, salida: ic("icon-512.png"), transparente: true });
  await foto(navegador, icono(192), { ancho: 192, alto: 192, salida: ic("icon-192.png"), transparente: true });
  await foto(navegador, icono(512, { maskable: true }), { ancho: 512, alto: 512, salida: ic("icon-maskable-512.png") });
  await foto(navegador, icono(180, { plano: true }), { ancho: 180, alto: 180, salida: ic("apple-touch-icon.png") });
  await foto(navegador, icono(32), { ancho: 32, alto: 32, salida: ic("favicon-32.png"), transparente: true });
  for (const d of paginas) {
    await foto(navegador, og(d), { ancho: 1200, alto: 630, salida: path.join(RAIZ, `assets/img/og/${d.nombre}.jpg`), tipo: "jpeg" });
  }
  await navegador.close();
})().catch((e) => { console.error(e); process.exit(1); });
