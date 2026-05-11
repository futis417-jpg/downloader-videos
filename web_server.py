import os
import datetime
import psutil
from flask import Flask, jsonify, render_template_string, Response
from flask_cors import CORS
from config import EmpireConfig, settings
from database_core import db

web_app = Flask("Ishak_Enterprise_Web")
CORS(web_app)

LANDING_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ishak Enterprise V400 | B2B Media Solutions</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        body { background-color: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        .glass-panel { background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .glow-text { text-shadow: 0 0 15px rgba(56, 189, 248, 0.8); }
        .gradient-text { background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero-bg { background: radial-gradient(circle at center, rgba(56, 189, 248, 0.15) 0%, transparent 60%); }
        code { font-family: 'Courier New', Courier, monospace; }
        .api-block { background: #0f172a; padding: 1rem; border-left: 4px solid #38bdf8; border-radius: 4px; }
        .health-ok { color: #22c55e; }
        .health-degraded { color: #facc15; }
        .health-down { color: #ef4444; }
    </style>
</head>
<body class="antialiased">
    <nav class="fixed w-full z-50 glass-panel py-4 px-8 flex justify-between items-center border-b border-slate-800">
        <div class="text-2xl font-extrabold tracking-tighter">
            <i class="fas fa-cube text-blue-500 mr-2"></i> ISHAK<span class="text-blue-500">.V400</span>
        </div>
        <div class="hidden md:flex space-x-6">
            <a href="#dashboard" class="hover:text-blue-400 transition">Dashboard</a>
            <a href="#api" class="hover:text-blue-400 transition">API REST</a>
            <a href="#health" class="hover:text-blue-400 transition">Health & Metrics</a>
        </div>
        <button class="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-lg font-semibold transition shadow-lg shadow-blue-500/30">
            Admin Login
        </button>
    </nav>

    <div class="relative min-h-screen flex items-center justify-center pt-20 hero-bg">
        <div class="absolute w-96 h-96 bg-blue-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 top-10 left-10 animate-blob"></div>
        <div class="absolute w-96 h-96 bg-indigo-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 bottom-10 right-10 animate-blob" style="animation-delay: 2s"></div>
        
        <div class="z-10 text-center px-4 max-w-5xl glass-panel p-16 rounded-[2rem] shadow-2xl border border-slate-700/50 relative overflow-hidden">
            <div class="absolute top-0 right-0 bg-blue-500 text-xs font-bold px-3 py-1 rounded-bl-lg">LIVE</div>
            <h1 class="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight"><span class="gradient-text">INFRAESTRUCTURA B2B</span> DEFINITIVA</h1>
            <p class="text-xl md:text-2xl text-slate-400 mb-10 max-w-3xl mx-auto font-light">
                Motor de extracción multimedia y transacciones criptográficas. Valoración de mercado: <strong class="text-white">€500,000</strong>.
                Creado y dirigido por <strong class="text-blue-400 glow-text">Ishak Ezzahouani (18)</strong> en España.
            </p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10 text-left">
                <div class="bg-slate-900/60 p-8 rounded-2xl border border-slate-700 hover:border-blue-500 transition-colors">
                    <i class="fas fa-server text-4xl text-blue-400 mb-4 drop-shadow-md"></i>
                    <h3 class="text-xl font-bold mb-2">Motor Asíncrono</h3>
                    <p class="text-sm text-slate-400">Procesamiento de peticiones concurrentes con optimización de memoria (Garbage Collector automático).</p>
                </div>
                <div class="bg-slate-900/60 p-8 rounded-2xl border border-slate-700 hover:border-purple-500 transition-colors">
                    <i class="fas fa-shield-virus text-4xl text-purple-400 mb-4 drop-shadow-md"></i>
                    <h3 class="text-xl font-bold mb-2">Self-Healing Core</h3>
                    <p class="text-sm text-slate-400">La base de datos se repara automáticamente. Bloqueos Anti-DDoS y validación estricta de variables.</p>
                </div>
                <div class="bg-slate-900/60 p-8 rounded-2xl border border-slate-700 hover:border-green-500 transition-colors">
                    <i class="fas fa-chart-line text-4xl text-green-400 mb-4 drop-shadow-md"></i>
                    <h3 class="text-xl font-bold mb-2">Economía Real</h3>
                    <p class="text-sm text-slate-400">Integración de Telegram Stars nativo y sistema de fluctuación de criptomoneda interna.</p>
                </div>
            </div>
        </div>
    </div>

    <div id="health" class="py-16 bg-slate-900/50 border-t border-slate-800">
        <div class="max-w-7xl mx-auto px-4">
            <h2 class="text-2xl font-bold mb-8 text-center gradient-text">ESTADO DEL SISTEMA</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-6" id="health-metrics">
                <div class="glass-panel p-6 rounded-xl text-center">
                    <div class="text-3xl mb-2" id="h-status">✅</div>
                    <div class="text-sm text-slate-400">Estado General</div>
                </div>
                <div class="glass-panel p-6 rounded-xl text-center">
                    <div class="text-3xl mb-2" id="h-latency">0ms</div>
                    <div class="text-sm text-slate-400">Latencia</div>
                </div>
                <div class="glass-panel p-6 rounded-xl text-center">
                    <div class="text-3xl mb-2" id="h-uptime">0%</div>
                    <div class="text-sm text-slate-400">Uptime</div>
                </div>
                <div class="glass-panel p-6 rounded-xl text-center">
                    <div class="text-3xl mb-2" id="h-queue">0</div>
                    <div class="text-sm text-slate-400">Cola Activa</div>
                </div>
            </div>
        </div>
    </div>

    <div id="dashboard" class="py-24 bg-slate-950 border-t border-slate-900">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <h2 class="text-3xl md:text-4xl font-bold mb-16 gradient-text">MÉTRICAS EN TIEMPO REAL</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
                <div class="glass-panel p-8 rounded-2xl relative overflow-hidden group">
                    <div class="absolute inset-0 bg-blue-500/10 translate-y-full group-hover:translate-y-0 transition-transform"></div>
                    <div class="text-5xl font-black text-blue-400 mb-2 font-mono" id="val-users">0</div>
                    <div class="text-sm font-semibold text-slate-500 uppercase tracking-widest">Ciudadanos</div>
                </div>
                <div class="glass-panel p-8 rounded-2xl relative overflow-hidden group">
                    <div class="absolute inset-0 bg-purple-500/10 translate-y-full group-hover:translate-y-0 transition-transform"></div>
                    <div class="text-5xl font-black text-purple-400 mb-2 font-mono" id="val-downloads">0</div>
                    <div class="text-sm font-semibold text-slate-500 uppercase tracking-widest">Extracciones</div>
                </div>
                <div class="glass-panel p-8 rounded-2xl relative overflow-hidden group">
                    <div class="absolute inset-0 bg-green-500/10 translate-y-full group-hover:translate-y-0 transition-transform"></div>
                    <div class="text-5xl font-black text-green-400 mb-2 font-mono" id="val-revenue">0</div>
                    <div class="text-sm font-semibold text-slate-500 uppercase tracking-widest">Stars Revenue</div>
                </div>
                <div class="glass-panel p-8 rounded-2xl relative overflow-hidden group">
                    <div class="absolute inset-0 bg-yellow-500/10 translate-y-full group-hover:translate-y-0 transition-transform"></div>
                    <div class="text-5xl font-black text-yellow-400 mb-2 font-mono" id="val-crypto">0.00</div>
                    <div class="text-sm font-semibold text-slate-500 uppercase tracking-widest">IshakCoin (Pts)</div>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="glass-panel p-6 rounded-2xl text-left">
                    <h3 class="text-lg font-bold mb-4 text-slate-300">Fluctuación de Mercado (IshakCoin)</h3>
                    <canvas id="cryptoChart" height="150"></canvas>
                </div>
                <div class="glass-panel p-6 rounded-2xl text-left">
                    <h3 class="text-lg font-bold mb-4 text-slate-300">Auditoría y Seguridad</h3>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                            <span class="text-slate-400">Intentos Fraude (Bloqueados)</span>
                            <span class="font-mono text-red-400 font-bold" id="val-fraud">0</span>
                        </div>
                        <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                            <span class="text-slate-400">Reparaciones de Base de Datos</span>
                            <span class="font-mono text-blue-400 font-bold" id="val-fixes">0</span>
                        </div>
                        <div class="flex justify-between items-center border-b border-slate-800 pb-2">
                            <span class="text-slate-400">Giros Totales Casino</span>
                            <span class="font-mono text-purple-400 font-bold" id="val-casino">0</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="api" class="py-24 bg-[#020617]">
        <div class="max-w-5xl mx-auto px-4">
            <h2 class="text-3xl font-bold mb-8 gradient-text">DOCUMENTACIÓN B2B API (REAL)</h2>
            <div class="glass-panel p-8 rounded-2xl mb-8">
                <div class="flex items-center mb-6">
                    <span class="bg-green-600 text-white text-xs font-bold px-3 py-1 rounded mr-4">POST</span>
                    <h3 class="text-xl font-mono text-slate-200">/api/v1/extract</h3>
                </div>
                <p class="text-slate-400 mb-4">
                    Endpoint corporativo para extracción pura de enlaces CDN de plataformas de vídeo. 
                    Requiere cabecera de autorización con una <code class="text-blue-400">API Key</code> hasheada en formato SHA-256 en nuestra base de datos.
                </p>
                <div class="api-block text-sm text-slate-300 overflow-x-auto">
<pre>curl -X POST https://api.ishak-enterprise.com/api/v1/extract \\
  -H "Content-Type: application/json" \\
  -H "X-API-KEY: sk_live_ejemplo1234" \\
  -d '{"url": "https://www.ejemplo.com/video"}'</pre>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="glass-panel p-8 rounded-2xl">
                    <h4 class="font-bold text-lg mb-4 text-slate-300">Respuestas Exitosas (200)</h4>
                    <div class="api-block text-xs text-green-300 overflow-x-auto">
<pre>{
  "status": "success",
  "code": 200,
  "data": {
    "title": "Video Título",
    "direct_cdn_url": "https://cdn...",
    "duration": 120
  }
}</pre>
                    </div>
                </div>
                <div class="glass-panel p-8 rounded-2xl">
                    <h4 class="font-bold text-lg mb-4 text-slate-300">Manejo de Errores (4xx/5xx)</h4>
                    <div class="api-block text-xs text-red-300 overflow-x-auto">
<pre>{
  "error": "No autorizado. Clave ausente o revocada.",
  "status": 401
}
// Rate limit (Anti-DDoS) -> 429
// Fallo extracción matriz -> 500</pre>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="py-12 bg-slate-950 border-t border-slate-900 text-center text-slate-500">
        <p class="mb-2">© 2026 Ishak Enterprise V400. Todos los derechos reservados.</p>
        <p class="text-sm">Sistema blindado y gobernado por Ishak Ezzahouani (Director, España).</p>
    </footer>

    <script>
        const ctx = document.getElementById('cryptoChart').getContext('2d');
        const cryptoChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array(20).fill(''),
                datasets: [{
                    label: 'Valor IshakCoin (Pts)',
                    data: Array(20).fill(150),
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { 
                        display: true, 
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#94a3b8' }
                    }
                },
                animation: { duration: 0 }
            }
        });

        async function fetchMetrics() {
            try {
                const start = performance.now();
                const res = await fetch('/api/v4/metrics');
                const data = await res.json();
                const latency = Math.round(performance.now() - start);
                
                document.getElementById('val-users').innerText = data.metrics.users;
                document.getElementById('val-downloads').innerText = data.metrics.downloads;
                document.getElementById('val-revenue').innerText = data.metrics.revenue + " ⭐️";
                document.getElementById('val-crypto').innerText = data.metrics.crypto.toFixed(2);
                document.getElementById('val-fraud').innerText = data.metrics.fraud_blocked;
                document.getElementById('val-fixes').innerText = data.metrics.self_healing;
                document.getElementById('val-casino').innerText = data.metrics.casino_spins;

                document.getElementById('h-latency').innerText = latency + 'ms';
                document.getElementById('h-status').innerText = data.health === 'ok' ? '✅' : '⚠️';
                
                const chartData = cryptoChart.data.datasets[0].data;
                chartData.push(data.metrics.crypto);
                if (chartData.length > 20) chartData.shift();
                cryptoChart.update();

            } catch (e) { 
                console.log("Core sync error - Posible Firewall activado."); 
            }
        }
        
        fetchMetrics();
        setInterval(fetchMetrics, 5000); 
    </script>
</body>
</html>
"""

@web_app.route('/', methods=['GET'])
def index():
    return render_template_string(LANDING_HTML)

@web_app.route('/api/v4/metrics', methods=['GET'])
def api_metrics():
    boot_time = datetime.datetime.fromisoformat(db.data["stats"]["boot_time"])
    uptime_hours = (datetime.datetime.now() - boot_time).total_seconds() / 3600
    return jsonify({
        "status": "ONLINE",
        "health": "ok" if psutil.cpu_percent() < 90 else "degraded",
        "metrics": {
            "users": db.data["stats"]["total_users"],
            "downloads": db.data["stats"]["total_downloads"],
            "revenue": db.data["stats"].get("stars_revenue", 0),
            "crypto": db.data["market_stats"]["crypto_value"],
            "fraud_blocked": db.data["stats"].get("fraud_attempts_blocked", 0),
            "self_healing": db.data["stats"].get("self_healing_fixes", 0),
            "casino_spins": db.data["stats"].get("casino_spins", 0),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "uptime_hours": round(uptime_hours, 2)
        }
    })

@web_app.route('/health', methods=['GET'])
def health_check():
    db_ok = os.path.exists(EmpireConfig.DATABASE_PATH)
    disk_ok = psutil.disk_usage('/').percent < 90
    mem_ok = psutil.virtual_memory().percent < 90
    
    status = "ok" if (db_ok and disk_ok and mem_ok) else "degraded"
    code = 200 if status == "ok" else 503
    
    return jsonify({
        "status": status,
        "version": EmpireConfig.VERSION,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "checks": {
            "database": "ok" if db_ok else "fail",
            "disk": "ok" if disk_ok else "fail",
            "memory": "ok" if mem_ok else "fail"
        }
    }), code

@web_app.route('/ready', methods=['GET'])
def readiness_check():
    return jsonify({"ready": True, "polling": "active"}), 200

@web_app.route('/metrics', methods=['GET'])
def prometheus_metrics():
    boot_time = datetime.datetime.fromisoformat(db.data["stats"]["boot_time"])
    uptime_seconds = (datetime.datetime.now() - boot_time).total_seconds()
    
    lines = [
        "# HELP ishak_users_total Total number of registered users",
        "# TYPE ishak_users_total gauge",
        f'ishak_users_total {db.data["stats"]["total_users"]}',
        "# HELP ishak_downloads_total Total media downloads",
        "# TYPE ishak_downloads_total counter",
        f'ishak_downloads_total {db.data["stats"]["total_downloads"]}',
        "# HELP ishak_revenue_stars_total Total stars revenue",
        "# TYPE ishak_revenue_stars_total counter",
        f'ishak_revenue_stars_total {db.data["stats"].get("stars_revenue", 0)}',
        "# HELP ishak_crypto_value Current value of IshakCoin",
        "# TYPE ishak_crypto_value gauge",
        f'ishak_crypto_value {db.data["market_stats"]["crypto_value"]}',
        "# HELP ishak_uptime_seconds System uptime in seconds",
        "# TYPE ishak_uptime_seconds counter",
        f'ishak_uptime_seconds {int(uptime_seconds)}',
        "# HELP ishak_cpu_usage_percent Current CPU usage",
        "# TYPE ishak_cpu_usage_percent gauge",
        f'ishak_cpu_usage_percent {psutil.cpu_percent()}',
        "# HELP ishak_memory_usage_percent Current memory usage",
        "# TYPE ishak_memory_usage_percent gauge",
        f'ishak_memory_usage_percent {psutil.virtual_memory().percent}',
        "# HELP ishak_disk_usage_percent Current disk usage",
        "# TYPE ishak_disk_usage_percent gauge",
        f'ishak_disk_usage_percent {psutil.disk_usage("/").percent}',
        "# HELP ishak_fraud_blocked_total Total fraud attempts blocked",
        "# TYPE ishak_fraud_blocked_total counter",
        f'ishak_fraud_blocked_total {db.data["stats"].get("fraud_attempts_blocked", 0)}',
    ]
    return Response('\n'.join(lines) + '\n', mimetype='text/plain')

@web_app.route('/api/docs', methods=['GET'])
def api_docs():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Ishak Enterprise API Docs</title>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
    <style>body { margin: 0; }</style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script>
        const spec = {{ spec|tojson }};
        SwaggerUIBundle({
            spec: spec,
            dom_id: '#swagger-ui',
            layout: 'BaseLayout',
            deepLinking: true
        });
    </script>
</body>
</html>
    """, spec={
        "openapi": "3.0.3",
        "info": {
            "title": "Ishak Enterprise B2B API",
            "version": "400.2",
            "description": "API REST para extracción multimedia y gestión de infraestructura.",
            "contact": {"name": "Ishak Ezzahouani", "email": "admin@ishak-enterprise.com"}
        },
        "servers": [{"url": "https://api.ishak-enterprise.com"}],
        "paths": {
            "/api/v1/extract": {
                "post": {
                    "summary": "Extraer enlace CDN de vídeo",
                    "security": [{"ApiKeyAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"type": "object", "properties": {"url": {"type": "string", "format": "uri"}}}}}
                    },
                    "responses": {
                        "200": {"description": "Extracción exitosa"},
                        "401": {"description": "No autorizado"},
                        "429": {"description": "Demasiadas peticiones"},
                        "500": {"description": "Error interno"}
                    }
                }
            },
            "/health": {"get": {"summary": "Health Check", "responses": {"200": {"description": "Sistema operativo"}}}},
            "/api/v4/metrics": {"get": {"summary": "Métricas JSON", "responses": {"200": {"description": "Métricas actuales"}}}},
           "/metrics": {"get": {"summary": "Métricas Prometheus", "responses": {"200": {"description": "Formato Prometheus"}}}}
    },
    "components": {}
})

def run_api():
    port = int(os.environ.get("PORT", settings.port))
    web_app.run(host="0.0.0.0", port=port, use_reloader=False)
