"""
Calculadora interactiva de Series de Taylor / Maclaurin
========================================================
Un solo archivo.
IMPORTANTE
Ejecuta:
    pip install flask sympy
    python taylor_app.py
Abre http://127.0.0.1:5000
"""

try:
    from flask import Flask, request, jsonify, render_template_string
    import sympy as sp
except ImportError as e:
    print(f"\n Falta una dependencia: {e}")
    print("Instálala con:  pip install flask sympy\n")
    raise

import math

app = Flask(__name__)


#  Parte del FrontEnd
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Calculadora Taylor / Maclaurin</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {
    --bg: #0f172a; --panel: #1e293b; --accent: #38bdf8; --accent2: #a78bfa;
    --text: #e2e8f0; --muted: #94a3b8; --border: #334155;
    --ok: #22c55e; --err: #ef4444; --warn: #f59e0b;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    color: var(--text); min-height: 100vh; padding: 24px;
  }
  .container { max-width: 1400px; margin: 0 auto; }
  header { text-align: center; margin-bottom: 30px; }
  header h1 {
    margin: 0; font-size: 2rem;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  header p { color: var(--muted); margin: 6px 0 0; }

  .grid-inputs {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px; background: var(--panel); padding: 20px;
    border-radius: 12px; border: 1px solid var(--border);
  }
  .field { display: flex; flex-direction: column; gap: 6px; }
  .field label { font-size: 0.85rem; color: var(--muted); font-weight: 600; }
  .field input, .field select {
    padding: 10px 12px; background: #0f172a; color: var(--text);
    border: 1px solid var(--border); border-radius: 8px;
    font-size: 0.95rem; font-family: 'Courier New', monospace;
  }
  .field input:focus {
    outline: none; border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(56,189,248,0.15);
  }
  .field input:disabled { opacity: 0.5; cursor: not-allowed; }
  .checkbox-row { display: flex; align-items: center; gap: 8px; margin-top: 12px; }
  .checkbox-row input[type="checkbox"] { width: auto; cursor: pointer; }

  .actions { display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
  button {
    padding: 11px 22px; border: none; border-radius: 8px;
    font-weight: 600; cursor: pointer; font-size: 0.95rem;
    transition: transform 0.1s, box-shadow 0.2s;
  }
  button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
  button:active { transform: translateY(0); }
  button.primary { background: linear-gradient(90deg, var(--accent), var(--accent2)); color: #0f172a; }
  button.secondary { background: #334155; color: var(--text); }
  button:disabled { opacity: 0.5; cursor: not-allowed; }

  .hint {
    font-size: 0.8rem; color: var(--muted); margin-top: 14px; padding: 10px 14px;
    background: rgba(56,189,248,0.06); border-left: 3px solid var(--accent);
    border-radius: 4px; line-height: 1.7;
  }
  .hint code { background: #0f172a; padding: 2px 6px; border-radius: 3px; color: var(--accent); }

  /* ---- Seccion de ejemplos ---- */
  .examples {
    margin-top: 16px;
    padding: 16px;
    background: #0f172a;
    border: 1px solid var(--border);
    border-radius: 10px;
  }
  .examples-title {
    font-size: 0.9rem;
    color: var(--accent2);
    font-weight: 700;
    margin-bottom: 12px;
    letter-spacing: 0.3px;
  }
  .examples-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 14px;
  }
  .example-col {
    padding: 12px 14px;
    border-radius: 8px;
    background: var(--panel);
    border-left: 4px solid var(--border);
  }
  .example-col.ok  { border-left-color: var(--ok); }
  .example-col.bad { border-left-color: var(--err); }
  .example-col .col-title {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 10px;
  }
  .example-col.ok  .col-title { color: var(--ok); }
  .example-col.bad .col-title { color: var(--err); }
  .example-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    padding: 5px 0;
    font-size: 0.82rem;
    border-bottom: 1px dashed rgba(148,163,184,0.15);
  }
  .example-item:last-child { border-bottom: none; }
  .example-item code {
    background: #0f172a;
    padding: 2px 8px;
    border-radius: 4px;
    color: var(--accent);
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    white-space: nowrap;
    flex-shrink: 0;
  }
  .example-col.bad .example-item code { color: #fca5a5; }
  .example-item span {
    color: var(--muted);
    font-size: 0.76rem;
    text-align: right;
    line-height: 1.35;
  }
  .examples-note {
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
    font-size: 0.8rem;
    color: var(--muted);
    line-height: 1.8;
  }
  .examples-note strong { color: var(--accent); }
  .examples-note code {
    background: var(--panel);
    padding: 2px 6px;
    border-radius: 3px;
    color: var(--accent);
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
  }

  .error-box {
    background: rgba(239,68,68,0.15); border: 1px solid var(--err);
    padding: 12px 16px; border-radius: 8px; color: #fca5a5;
    margin-top: 16px; display: none;
  }
  .error-box.show { display: block; }

  .metrics {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 12px; margin-top: 20px;
  }
  .metric {
    background: var(--panel); padding: 14px; border-radius: 10px;
    border: 1px solid var(--border);
  }
  .metric .label {
    font-size: 0.72rem; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .metric .value {
    font-size: 1.15rem; font-weight: 700; margin-top: 4px;
    color: var(--accent); font-family: 'Courier New', monospace;
    word-break: break-all;
  }
  .metric .value.ok { color: var(--ok); }
  .metric .value.warn { color: var(--warn); }

  .panel {
    background: var(--panel); border-radius: 12px;
    border: 1px solid var(--border); padding: 20px; margin-top: 20px;
  }
  .panel h2 { margin: 0 0 14px 0; font-size: 1.1rem; color: var(--accent); }

  .table-wrap { overflow: auto; max-height: 520px; }
  table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  th, td {
    padding: 8px 10px; text-align: right;
    border-bottom: 1px solid var(--border);
    font-family: 'Courier New', monospace;
  }
  th {
    background: #0f172a; position: sticky; top: 0;
    color: var(--accent2); font-weight: 700; z-index: 1;
  }
  td:first-child, th:first-child { text-align: center; }
  tbody tr:hover { background: rgba(56,189,248,0.05); }
  td.neg { color: #fca5a5; }
  td.pos { color: #86efac; }
  td.num { color: #93c5fd; }
  td.deriv { text-align: left; color: var(--muted); font-size: 0.72rem; max-width: 180px; overflow: hidden; text-overflow: ellipsis; }
  tr.best { background: rgba(34,197,94,0.08); }

  .charts-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
    gap: 20px;
  }
  .chart-card {
    background: #0f172a; border-radius: 10px; padding: 14px;
    border: 1px solid var(--border);
  }
  .chart-card h3 { margin: 0 0 10px; font-size: 0.92rem; color: var(--muted); }
  .chart-container { position: relative; height: 300px; }

  .loading { display: none; margin-top: 16px; color: var(--accent); font-weight: 600; }
  .loading.show { display: block; }

  .success-info {
    display: flex; gap: 20px; flex-wrap: wrap;
    padding: 12px 16px; background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.3); border-radius: 8px;
    margin-top: 16px; font-size: 0.88rem;
  }
  .success-info span strong { color: var(--ok); }
  .success-info span { font-family: 'Courier New', monospace; }

  .badge {
    display: inline-block; padding: 2px 10px; border-radius: 12px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.5px;
  }
  .badge.maclaurin { background: rgba(167,139,250,0.2); color: var(--accent2); }
  .badge.taylor    { background: rgba(56,189,248,0.2); color: var(--accent); }
  .badge.conv      { background: rgba(34,197,94,0.2); color: var(--ok); }
  .badge.div       { background: rgba(239,68,68,0.2); color: var(--err); }
  .badge.stable    { background: rgba(245,158,11,0.2); color: var(--warn); }
  footer { text-align: center; color: var(--muted); font-size: 0.78rem; margin-top: 30px; padding: 20px; }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1> Calculadora de Series de Taylor / Maclaurin</h1>
    <p>Análisis de convergencia, error absoluto y relativo de la aproximación</p>
  </header>

  <div class="panel">
    <h2> Parámetros de entrada</h2>
    <div class="grid-inputs">
      <div class="field" style="grid-column: span 2;">
        <label for="funcion">f(x) — función a aproximar</label>
        <input type="text" id="funcion" value="sin(x)" placeholder="Ej: sin(x), exp(x), ln(1+x)">
      </div>
      <div class="field">
        <label for="a">Centro a (Taylor)</label>
        <input type="text" id="a" value="0" placeholder="0 = Maclaurin">
      </div>
      <div class="field">
        <label for="x">Punto x de evaluación</label>
        <input type="text" id="x" value="1" placeholder="Ej: 0.5, pi/4">
      </div>
      <div class="field">
        <label for="n">N° de términos</label>
        <input type="number" id="n" min="1" max="80" value="10">
      </div>
      <div class="field">
        <label for="tolerancia">Tolerancia objetivo</label>
        <input type="text" id="tolerancia" value="1e-6">
      </div>
    </div>

    <div class="checkbox-row">
      <input type="checkbox" id="maclaurin" checked>
      <label for="maclaurin">Modo Maclaurin (fuerza a = 0)</label>
    </div>

    <div class="actions">
      <button class="primary" id="btnCalc">Calcular serie</button>
      <button class="secondary" id="btnCSV" disabled>Exportar CSV</button>
      <button class="secondary" id="btnLimpiar">Limpiar</button>
    </div>

    <div class="hint">
      <strong>Sintaxis:</strong>
      <code>sin, cos, tan, asin, acos, atan, exp, log (=ln), sqrt, abs, sinh, cosh, tanh, pi, e</code>.
      Potencias con <code>**</code> o <code>^</code>. Multiplicación explícita con <code>*</code>
      (ej. <code>3*x</code>, no <code>3x</code>). En <code>a</code> y <code>x</code>
      se aceptan expresiones como <code>pi/4</code> o <code>0.5</code>.
    </div>

    <!-- ==================== SECCION DE EJEMPLOS ==================== -->
    <div class="examples">
      <div class="examples-title">Ejemplos de uso — guía rápida</div>
      <div class="examples-grid">

        <div class="example-col ok">
          <div class="col-title">Correcto — sí funciona</div>
          <div class="example-item"><code>sin(x)</code><span>Función trigonométrica</span></div>
          <div class="example-item"><code>exp(x) + cos(x)</code><span>Suma de funciones</span></div>
          <div class="example-item"><code>ln(1 + x)</code><span>Logaritmo natural</span></div>
          <div class="example-item"><code>x^3 - 2*x + 1</code><span>Polinomio con potencias</span></div>
          <div class="example-item"><code>1 / (1 - x)</code><span>Fracción (serie geométrica)</span></div>
          <div class="example-item"><code>sqrt(x + 1)</code><span>Raíz cuadrada</span></div>
          <div class="example-item"><code>tan(x)</code><span>Tangente</span></div>
          <div class="example-item"><code>abs(x)</code><span>Valor absoluto</span></div>
        </div>

        <div class="example-col bad">
          <div class="col-title">Incorrecto — no funciona</div>
          <div class="example-item"><code>3x</code><span>Falta el asterisco: escribe <code>3*x</code></span></div>
          <div class="example-item"><code>sin x</code><span>Faltan paréntesis: escribe <code>sin(x)</code></span></div>
          <div class="example-item"><code>sin(y)</code><span>Solo se permite la variable <code>x</code></span></div>
          <div class="example-item"><code>2xy</code><span>Variables múltiples: solo se permite <code>x</code></span></div>
          <div class="example-item"><code>x**</code><span>Expresión incompleta</span></div>
          <div class="example-item"><code>log(x, 10)</code><span>No se admite base; usa <code>log(x)</code> para ln</span></div>
          <div class="example-item"><code>(x + 1</code><span>Paréntesis sin cerrar</span></div>
          <div class="example-item"><code>sen x</code><span>Falta paréntesis: <code>sen(x)</code> o <code>sin(x)</code></span></div>
        </div>

      </div>

      <div class="examples-note">
        <strong>Campos a y x:</strong> se aceptan números (<code>0</code>, <code>1.5</code>, <code>-2</code>),
        constantes (<code>pi</code>, <code>e</code>) y expresiones como <code>pi/4</code> o <code>2*pi</code>.
        Si <code>x = a</code>, la serie coincide exactamente con la función en ese punto (error 0 desde el término k=0).
        <br>
        <strong>Modo Maclaurin:</strong> si está marcado, se ignora el campo <code>a</code> y se fuerza <code>a = 0</code>.
        <br>
        <strong>Rango de términos:</strong> <code>1</code> a <code>80</code>. Valores fuera de ese rango devuelven un error.
      </div>
    </div>
    <!-- ============================================================= -->

    <div class="error-box" id="errBox"></div>
    <div class="loading" id="loading"> Calculando derivadas simbólicas y evaluando...</div>
  </div>

  <div id="resultados" style="display:none;">
    <div class="success-info" id="infoResumen"></div>
    <div class="metrics" id="metricas"></div>

    <div class="panel">
      <h2> Tabla de iteraciones</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>k</th>
              <th>f⁽ᵏ⁾(x)</th>
              <th>f⁽ᵏ⁾(a)</th>
              <th>Término Tₖ</th>
              <th>Sumatoria Sₙ</th>
              <th>Error Abs.</th>
              <th>Error Rel.</th>
            </tr>
          </thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
    </div>

    <div class="panel">
      <h2> Gráficas de convergencia</h2>
      <div class="charts-grid">
        <div class="chart-card">
          <h3>Iteración vs Término Tₖ</h3>
          <div class="chart-container"><canvas id="chartTerminos"></canvas></div>
        </div>
        <div class="chart-card">
          <h3>Iteración vs Sumatoria Sₙ</h3>
          <div class="chart-container"><canvas id="chartSumatoria"></canvas></div>
        </div>
        <div class="chart-card">
          <h3>Iteración vs Errores (Abs & Rel, log)</h3>
          <div class="chart-container"><canvas id="chartErrores"></canvas></div>
        </div>
        <div class="chart-card">
          <h3>Convergencia: |Error Abs.| vs tolerancia</h3>
          <div class="chart-container"><canvas id="chartConvergencia"></canvas></div>
        </div>
      </div>
    </div>
  </div>

  <footer>
    Desarrollado con Flask + SymPy + Chart.js · Los errores se calculan contra el valor real
    <em>f(x₀)</em> evaluado simbólicamente.
  </footer>
</div>

<script>
let charts = {};
let ultimosDatos = null;

let prevA = '0';
document.getElementById('maclaurin').addEventListener('change', e => {
  const aInp = document.getElementById('a');
  if (e.target.checked) {
    prevA = aInp.value;
    aInp.value = '0';
    aInp.disabled = true;
  } else {
    aInp.value = prevA || '0';
    aInp.disabled = false;
  }
});
document.getElementById('a').disabled = true;

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function fmt(v, d = 8) {
  if (v === null || v === undefined) return '—';
  if (typeof v !== 'number') return v;
  if (!isFinite(v)) return '∞';
  if (v === 0) return '0';
  const abs = Math.abs(v);
  if (abs < 1e-4 || abs >= 1e7) return v.toExponential(4);
  return parseFloat(v.toFixed(d)).toString();
}

function showError(msg) {
  const box = document.getElementById('errBox');
  box.textContent = 'Error: ' + msg;
  box.classList.add('show');
}
function hideError() { document.getElementById('errBox').classList.remove('show'); }

async function calcular() {
  hideError();
  const body = {
    funcion:    document.getElementById('funcion').value,
    a:          document.getElementById('a').value,
    x:          document.getElementById('x').value,
    n:          document.getElementById('n').value,
    tolerancia: document.getElementById('tolerancia').value
  };
  document.getElementById('loading').classList.add('show');
  document.getElementById('btnCalc').disabled = true;
  try {
    const res = await fetch('/api/calcular', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!data.ok) { showError(data.error || 'Error desconocido'); return; }
    renderResultados(data);
  } catch (e) {
    showError('Error de conexión: ' + e.message);
  } finally {
    document.getElementById('loading').classList.remove('show');
    document.getElementById('btnCalc').disabled = false;
  }
}

document.getElementById('btnCalc').addEventListener('click', calcular);

document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && e.target && e.target.matches('input')) calcular();
});

document.getElementById('btnLimpiar').addEventListener('click', () => {
  document.getElementById('resultados').style.display = 'none';
  hideError();
  Object.values(charts).forEach(c => c && c.destroy());
  charts = {};
  document.getElementById('btnCSV').disabled = true;
  ultimosDatos = null;
});

document.getElementById('btnCSV').addEventListener('click', () => {
  if (!ultimosDatos) return;
  const d = ultimosDatos;
  let csv = 'k,derivada,valor_derivada,termino,sumatoria,error_abs,error_rel\n';
  d.iteraciones.forEach(it => {
    csv += [
      it.k,
      JSON.stringify(it.derivada_expr),
      it.valor_derivada ?? '',
      it.termino ?? '',
      it.sumatoria ?? '',
      it.err_abs ?? '',
      it.err_rel ?? ''
    ].join(',') + '\n';
  });
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'taylor_iteraciones.csv';
  a.click();
  URL.revokeObjectURL(url);
});

function renderResultados(data) {
  ultimosDatos = data;
  document.getElementById('resultados').style.display = 'block';
  document.getElementById('btnCSV').disabled = false;

  const m = data.metricas;
  const tipo = m.es_maclaurin
    ? '<span class="badge maclaurin">MACLAURIN</span>'
    : '<span class="badge taylor">TAYLOR</span>';
  const conv = m.tendencia === 'convergente'
    ? '<span class="badge conv">CONVERGENTE</span>'
    : (m.tendencia === 'divergente'
        ? '<span class="badge div">DIVERGENTE</span>'
        : '<span class="badge stable">ESTABLE</span>');

  document.getElementById('infoResumen').innerHTML = `
    <span><strong>f(x):</strong> ${esc(data.funcion_original)}</span>
    <span><strong>a =</strong> ${fmt(data.a, 10)}</span>
    <span><strong>x =</strong> ${fmt(data.x, 10)}</span>
    <span><strong>N =</strong> ${data.n}</span>
    <span>${tipo} ${conv}</span>
    <span><strong>f(x) real =</strong> ${fmt(data.valor_real, 12)}</span>
  `;

  const metricas = [
    ['Valor real f(x₀)',        fmt(data.valor_real, 12), ''],
    ['Error abs. final',         fmt(m.err_final_abs, 6), ''],
    ['Error rel. final',         fmt(m.error_relativo_final, 6), ''],
    ['Error mínimo alcanzado',   fmt(m.err_min_abs, 6), 'ok'],
    ['Términos para tolerancia', m.terminos_para_tolerancia ?? 'No alcanzada',
        m.terminos_para_tolerancia !== null ? 'ok' : 'warn'],
    ['Tasa convergencia (eₙ/eₙ₋₁)', fmt(m.tasa_convergencia, 4), ''],
    ['Tolerancia',               fmt(data.tolerancia), ''],
    ['Tipo de serie',            m.es_maclaurin ? 'Maclaurin' : 'Taylor', '']
  ];
  document.getElementById('metricas').innerHTML = metricas.map(([l, v, c]) =>
    `<div class="metric"><div class="label">${l}</div><div class="value ${c}">${v}</div></div>`
  ).join('');

  const tbody = document.getElementById('tbody');
  tbody.innerHTML = data.iteraciones.map(it => {
    const claseT = it.termino === null ? '' : (it.termino < 0 ? 'neg' : 'pos');
    const best = (it.err_abs !== null && it.err_abs === m.err_min_abs) ? 'class="best"' : '';
    const derivSafe = esc(it.derivada_expr);
    return `<tr ${best}>
      <td>${it.k}</td>
      <td class="deriv" title="${derivSafe}">${derivSafe}</td>
      <td class="num">${fmt(it.valor_derivada)}</td>
      <td class="${claseT}">${fmt(it.termino)}</td>
      <td class="num">${fmt(it.sumatoria)}</td>
      <td>${fmt(it.err_abs)}</td>
      <td>${fmt(it.err_rel)}</td>
    </tr>`;
  }).join('');

  renderCharts(data);
}

function renderCharts(data) {
  Object.values(charts).forEach(c => c && c.destroy());
  charts = {};

  const labels   = data.iteraciones.map(it => it.k);
  const terminos = data.iteraciones.map(it => it.termino);
  const sumas    = data.iteraciones.map(it => it.sumatoria);
  const errAbs   = data.iteraciones.map(it => it.err_abs);
  const errRel   = data.iteraciones.map(it => it.err_rel);

  const baseOpts = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#cbd5e1', font: { size: 11 } } },
      tooltip: {
        backgroundColor: 'rgba(15,23,42,0.95)',
        borderColor: '#334155', borderWidth: 1,
        callbacks: {
          label: ctx => `${ctx.dataset.label}: ${fmt(ctx.parsed.y)}`
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(148,163,184,0.08)' },
        title: { display: true, text: 'Iteración k', color: '#94a3b8' }
      },
      y: {
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(148,163,184,0.08)' }
      }
    }
  };

  charts.term = new Chart(document.getElementById('chartTerminos'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Término Tₖ',
        data: terminos,
        backgroundColor: terminos.map(v =>
          v === null ? '#64748b' : (v >= 0 ? 'rgba(56,189,248,0.7)' : 'rgba(239,68,68,0.7)')),
        borderColor: terminos.map(v => (v === null ? '#64748b' : (v >= 0 ? '#38bdf8' : '#ef4444'))),
        borderWidth: 1
      }]
    },
    options: {
      ...baseOpts,
      plugins: { ...baseOpts.plugins, legend: { display: false } }
    }
  });

  charts.sum = new Chart(document.getElementById('chartSumatoria'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Sumatoria Sₙ',
          data: sumas,
          borderColor: '#a78bfa',
          backgroundColor: 'rgba(167,139,250,0.18)',
          tension: 0.3, fill: true,
          pointRadius: 4, pointBackgroundColor: '#a78bfa'
        },
        {
          label: 'Valor real f(x₀)',
          data: sumas.map(() => data.valor_real),
          borderColor: '#22c55e',
          borderDash: [6, 4], borderWidth: 2,
          pointRadius: 0, fill: false
        }
      ]
    },
    options: baseOpts
  });

  const errAbsLog = errAbs.map(v => (v === null || v <= 0) ? null : v);
  const errRelLog = errRel.map(v => (v === null || v <= 0) ? null : v);
  charts.err = new Chart(document.getElementById('chartErrores'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Error Absoluto',
          data: errAbsLog,
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239,68,68,0.1)',
          tension: 0.3, pointRadius: 3
        },
        {
          label: 'Error Relativo',
          data: errRelLog,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245,158,11,0.1)',
          tension: 0.3, pointRadius: 3
        }
      ]
    },
    options: {
      ...baseOpts,
      scales: {
        x: baseOpts.scales.x,
        y: {
          type: 'logarithmic',
          ticks: { color: '#94a3b8' },
          grid: { color: 'rgba(148,163,184,0.08)' },
          title: { display: true, text: 'Error (log)', color: '#94a3b8' }
        }
      }
    }
  });

  charts.conv = new Chart(document.getElementById('chartConvergencia'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: '|Error Abs.|',
          data: errAbsLog,
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34,197,94,0.15)',
          fill: true, tension: 0.3, pointRadius: 3
        },
        {
          label: 'Tolerancia objetivo',
          data: errAbs.map(() => data.tolerancia),
          borderColor: '#38bdf8',
          borderDash: [4, 4], pointRadius: 0, fill: false
        }
      ]
    },
    options: {
      ...baseOpts,
      scales: {
        x: baseOpts.scales.x,
        y: {
          type: 'logarithmic',
          ticks: { color: '#94a3b8' },
          grid: { color: 'rgba(148,163,184,0.08)' }
        }
      }
    }
  });
}
</script>
</body>
</html>
"""


#  Definiciones de Procesos (Parte del BackEnd)

def preprocess_function(expr_str: str) -> str:
    """Convierte notaciones comunes a sintaxis sympy."""
    s = expr_str.strip()
    s = s.replace('sen(', 'sin(').replace('tg(', 'tan(')
    s = s.replace('ln(', 'log(')
    s = s.replace('^', '**')
    return s


def finite_or_none(v):
    """Devuelve float finito o None. Descarta complejos."""
    if v is None:
        return None
    if isinstance(v, complex):
        return None
    try:
        f = float(v)
        return f if math.isfinite(f) else None
    except Exception:
        return None


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    try:
        data = request.get_json(force=True, silent=True) or {}

        func_str = str(data.get('funcion', '')).strip()
        a_str    = str(data.get('a', '0')).strip() or '0'
        x_str    = str(data.get('x', '1')).strip() or '1'

        try:
            tolerancia = float(data.get('tolerancia', 1e-6) or 1e-6)
        except (TypeError, ValueError):
            return jsonify(ok=False, error='La tolerancia debe ser un número válido.'), 400

        try:
            n = int(data.get('n', 10))
        except Exception:
            return jsonify(ok=False, error='El número de términos debe ser un entero.'), 400

        if not func_str:
            return jsonify(ok=False, error='Debes ingresar una función f(x).'), 400
        if n < 1:
            return jsonify(ok=False, error='El número de términos debe ser ≥ 1.'), 400
        if n > 80:
            return jsonify(ok=False, error='Por rendimiento, el máximo de términos es 80.'), 400
        if tolerancia <= 0:
            return jsonify(ok=False, error='La tolerancia debe ser positiva.'), 400

        x = sp.Symbol('x')
        local_dict = {
            'x': x, 'pi': sp.pi, 'E': sp.E, 'e': sp.E,
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
            'sen': sp.sin, 'tg': sp.tan,
            'exp': sp.exp, 'log': sp.log, 'ln': sp.log,
            'sqrt': sp.sqrt, 'abs': sp.Abs,
            'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh
        }

        try:
            f = sp.sympify(preprocess_function(func_str), locals=local_dict)
        except Exception as e:
            return jsonify(ok=False,
                           error=f'No se pudo interpretar la función "{func_str}": {e}'), 400

        extra = f.free_symbols - {x}
        if extra:
            return jsonify(ok=False,
                           error=f'La función solo debe depender de x. Variables no reconocidas: {extra}'), 400

        try:
            a_val = float(sp.sympify(a_str, locals=local_dict).evalf())
        except Exception as e:
            return jsonify(ok=False, error=f'Valor de "a" inválido: {e}'), 400
        try:
            x_val = float(sp.sympify(x_str, locals=local_dict).evalf())
        except Exception as e:
            return jsonify(ok=False, error=f'Valor de "x" inválido: {e}'), 400

        if not (math.isfinite(a_val) and math.isfinite(x_val)):
            return jsonify(ok=False, error='"a" y "x" deben ser números reales finitos.'), 400

        try:
            valor_real = float(f.subs(x, x_val).evalf())
        except Exception as e:
            return jsonify(ok=False,
                           error=f'No se pudo evaluar f en x={x_val}: {e}'), 400

        if not math.isfinite(valor_real):
            return jsonify(ok=False,
                           error='El valor real de la función no es finito en el punto dado '
                                 '(posible singularidad).'), 400

        derivada = f
        suma = 0.0
        iteraciones = []

        for k in range(n):
            deriv_val = None
            termino = None

            try:
                deriv_val = float(derivada.subs(x, a_val).evalf())
                if not math.isfinite(deriv_val):
                    deriv_val = None
            except Exception:
                deriv_val = None

            if deriv_val is not None:
                try:
                    fact = math.factorial(k)
                    termino = deriv_val / fact * ((x_val - a_val) ** k)
                    if not math.isfinite(termino):
                        termino = None
                except Exception:
                    termino = None

            if termino is not None:
                suma += termino
                suma_val = suma if math.isfinite(suma) else None
            else:
                suma_val = suma if math.isfinite(suma) else None

            if suma_val is not None:
                err_abs = abs(suma_val - valor_real)
                err_rel = (err_abs / abs(valor_real)) if abs(valor_real) > 1e-15 else None
            else:
                err_abs = err_rel = None

            iteraciones.append({
                'k': k,
                'derivada_expr': str(derivada),
                'valor_derivada': finite_or_none(deriv_val),
                'termino': finite_or_none(termino),
                'sumatoria': finite_or_none(suma_val),
                'err_abs': finite_or_none(err_abs),
                'err_rel': finite_or_none(err_rel)
            })

            try:
                derivada = sp.diff(derivada, x)
                if derivada == 0:
                    derivada = sp.Integer(0)
            except Exception:
                derivada = sp.Integer(0)

        errores = [it['err_abs'] for it in iteraciones if it['err_abs'] is not None]
        err_final = errores[-1] if errores else None
        err_min = min(errores) if errores else None

        n_tol = None
        for it in iteraciones:
            if it['err_abs'] is not None and it['err_abs'] <= tolerancia:
                n_tol = it['k'] + 1
                break

        tasa = None
        if len(errores) >= 2 and errores[-2] > 0:
            try:
                tasa = errores[-1] / errores[-2]
            except Exception:
                tasa = None

        tendencia = 'estable'
        if len(errores) >= 3:
            if errores[-1] > errores[0] * 1.5:
                tendencia = 'divergente'
            elif errores[-1] < errores[0] * 0.1:
                tendencia = 'convergente'

        return jsonify({
            'ok': True,
            'iteraciones': iteraciones,
            'valor_real': valor_real,
            'a': a_val,
            'x': x_val,
            'n': n,
            'funcion_original': str(f),
            'tolerancia': tolerancia,
            'metricas': {
                'err_final_abs': finite_or_none(err_final),
                'err_min_abs': finite_or_none(err_min),
                'error_relativo_final': iteraciones[-1]['err_rel'] if iteraciones else None,
                'terminos_para_tolerancia': n_tol,
                'tasa_convergencia': finite_or_none(tasa),
                'es_maclaurin': abs(a_val) < 1e-15,
                'tendencia': tendencia
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error=f'Error inesperado en el servidor: {e}'), 500


#  Main
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("    Calculadora de Series de Taylor / Maclaurin")
    print("=" * 60)
    print("  → Abre en tu navegador:  http://127.0.0.1:5000")
    print("  → Presiona Ctrl+C para detener el servidor")
    print("=" * 60 + "\n")
    app.run(host='127.0.0.1', port=5000, debug=False)