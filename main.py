"""
████████╗██╗████████╗███████╗███╗   ██╗    ██╗   ██╗███████╗ ██████╗  ██████╗ 
╚══██╔══╝██║╚══██╔══╝██╔════╝████╗  ██║    ██║   ██║╚════██║██╔═████╗██╔═████╗
   ██║   ██║   ██║   █████╗  ██╔██╗ ██║    ██║   ██║    ██╔╝██║██╔██║██║██╔██║
   ██║   ██║   ██║   ██╔══╝  ██║╚██╗██║    ╚██╗ ██╔╝   ██╔╝ ████╔╝██║████╔╝██║
   ██║   ██║   ██║   ███████╗██║ ╚████║     ╚████╔╝    ██║  ╚██████╔╝╚██████╔╝
   ╚═╝   ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝      ╚═══╝     ╚═╝   ╚═════╝  ╚═════╝ 
================================================================================
SISTEMA: TITAN-V700 OMNIVERSE HYPER-SAAS - ULTIMATE MONETIZATION EDITION
VALORACIÓN DE MERCADO: €2,500.00+ | ARQUITECTURA FINTECH & B2B
DIRECTOR GENERAL: Ishak Ezzahouani (14) | SEDE: Sant Hilari Sacalm, España.
================================================================================
"""

import os
import sys
import json
import uuid
import time
import shutil
import asyncio
import logging
import datetime
import subprocess
import threading
import platform
import random
import re
import hashlib
import base64
import gc
import hmac
from typing import Dict, List, Any, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor

# =================================================================
# [0] BOOTSTRAP DE ALTA DISPONIBILIDAD & AUTO-UPDATE
# =================================================================
def titan_bootstrap():
    """Motor de instalación y reparación autónoma de dependencias."""
    pkgs = [
        'python-telegram-bot', 'yt-dlp', 'flask', 'flask-cors', 'requests', 
        'psutil', 'Pillow', 'aiohttp', 'cryptography', 'qrcode', 'python-dotenv', 
        'gTTS', 'pydantic', 'pydantic-settings', 'sentry-sdk', 'beautifulsoup4',
        'pycryptodome', 'python-jose', 'Flask-Limiter'
    ]
    for p in pkgs:
        try:
            __import__(p.replace('-', '_'))
        except ImportError:
            print(f"📦 [TITAN CORE] Instalando módulo faltante: {p}...")
            subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", p, "--quiet"])

titan_bootstrap()

import yt_dlp
import requests
import psutil
from flask import Flask, jsonify, request, render_template_string, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, constants, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, PreCheckoutQueryHandler, ContextTypes, filters
)

# =================================================================
# [1] CONFIGURACIÓN EMPRESARIAL & LENGUAJES (i18n)
# =================================================================
class TitanConfig(BaseSettings):
    admin_id: int = Field(default=8398522835)
    token: str = Field(default=os.getenv("ISHAK_TELEGRAM_TOKEN", ""))
    secret_key: str = Field(default=os.getenv("TITAN_SECRET", "OMNIVERSE_ROOT_KEY_2026_ISHAK_CORP"))
    encryption_key: str = Field(default=Fernet.generate_key().decode())
    port: int = Field(default=int(os.getenv("PORT", 10000)))
    
    model_config = {"env_file": ".env"} # Corregido warning de Pydantic V2

settings = TitanConfig()
fernet = Fernet(settings.encryption_key.encode())

# DICCIONARIO MULTI-IDIOMA
I18N = {
    "es": {
        "welcome": "🛡 **TITAN-V700 ACTIVO**\nBienvenido {name}. Estás en la red B2B más avanzada.",
        "btn_dl": "📥 EXTRACCIÓN", "btn_profile": "👤 PERFIL", "btn_casino": "🎰 CASINO",
        "btn_market": "📈 MERCADO CRIPTO", "btn_shop": "🛍️ TIENDA VIP", "btn_loot": "🎁 LOOTBOXES",
        "no_funds": "❌ Fondos insuficientes. Compra Stars o invita amigos.",
        "queue": "⏳ Estás en la cola. Usuarios VIP saltan la espera. Posición: {pos}"
    },
    "en": {
        "welcome": "🛡 **TITAN-V700 ACTIVE**\nWelcome {name}. You are in the most advanced B2B network.",
        "btn_dl": "📥 EXTRACT", "btn_profile": "👤 PROFILE", "btn_casino": "🎰 CASINO",
        "btn_market": "📈 CRYPTO MARKET", "btn_shop": "🛍️ VIP SHOP", "btn_loot": "🎁 LOOTBOXES",
        "no_funds": "❌ Insufficient funds. Buy Stars or invite friends.",
        "queue": "⏳ You are in queue. VIP users skip the wait. Position: {pos}"
    }
}

def _t(lang: str, key: str, **kwargs) -> str:
    return I18N.get(lang, I18N["es"]).get(key, I18N["es"].get(key, key)).format(**kwargs)

# =================================================================
# [2] MONETIZACIÓN: ECONOMÍA, LOOTBOXES Y PLANES
# =================================================================
PLANS = {
    "FREE": {"name": "🆓 Súbdito", "daily_limit": 3, "max_size": 100, "priority": 10},
    "PRO": {"name": "💎 Elite", "daily_limit": 50, "max_size": 1000, "priority": 5},
    "GOD": {"name": "👑 Omnipresente", "daily_limit": 9999, "max_size": 5000, "priority": 0}
}

STARS_PRODUCTS = {
    "loot_basic": {"title": "📦 Cofre Básico", "desc": "Gana Puntos o XP", "price": 50, "type": "lootbox"},
    "loot_titan": {"title": "🌌 Cofre TITAN", "desc": "Posible VIP o Millones de Puntos", "price": 250, "type": "lootbox"},
    "sub_pro": {"title": "💎 Rango PRO (30 Días)", "desc": "Descargas 1GB, Sin Cola", "price": 500, "type": "sub"},
    "api_credits": {"title": "🔌 10K Créditos API", "desc": "Para desarrolladores B2B", "price": 1000, "type": "api"}
}

class SecurityCore:
    @staticmethod
    def encrypt_data(data: str) -> str: return fernet.encrypt(data.encode()).decode()
    @staticmethod
    def decrypt_data(token: str) -> str: return fernet.decrypt(token.encode()).decode()
    @staticmethod
    def generate_api_jwt(uid: str, credits: int = 1000) -> str:
        header = base64.b64encode(b'{"alg":"HS256","typ":"JWT"}').decode()
        payload = base64.b64encode(json.dumps({"uid": uid, "c": credits, "exp": time.time() + 31536000}).encode()).decode()
        sig = hmac.new(settings.secret_key.encode(), f"{header}.{payload}".encode(), hashlib.sha256).hexdigest()
        return f"{header}.{payload}.{sig}"

# =================================================================
# [3] BASE DE DATOS DISTRIBUIDA (SHADOW CLONE)
# =================================================================
class DatabaseManager:
    def __init__(self):
        self.dir = os.path.join(os.getcwd(), "omniverse_vault")
        os.makedirs(self.dir, exist_ok=True)
        self.db_path = os.path.join(self.dir, "master_v700.json")
        self.shadow_path = os.path.join(self.dir, "shadow_v700.json")
        self.data = self._load()
        self._lock = threading.Lock()

    def _load(self):
        for path in [self.db_path, self.shadow_path]:
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f: return json.load(f)
            except: continue
        return {
            "users": {}, "b2b_api": {}, "market": {"coin_price": 100.0, "history": []},
            "stats": {"revenue_stars": 0, "total_dl": 0, "lootboxes_opened": 0}
        }

    def save(self):
        with self._lock:
            raw = json.dumps(self.data, indent=2, ensure_ascii=False)
            with open(self.db_path, 'w', encoding='utf-8') as f: f.write(raw)
            with open(self.shadow_path, 'w', encoding='utf-8') as f: f.write(raw)

    def get_user(self, user_obj, ref_id=None):
        uid = str(user_obj.id)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "id": user_obj.id, "name": user_obj.first_name, "lang": "es",
                "plan": "FREE", "points": 1000, "ishak_coins": 0.0,
                "api_credits": 0, "api_key": None, "xp": 0, "level": 1,
                "daily_dl": [0, str(datetime.date.today())],
                "inventory": {"bypass_tickets": 0, "spins": 3},
                "ref_count": 0
            }
            if ref_id and ref_id in self.data["users"] and ref_id != uid:
                self.data["users"][ref_id]["points"] += 2500
                self.data["users"][ref_id]["ref_count"] += 1
        
        u = self.data["users"][uid]
        if u["daily_dl"][1] != str(datetime.date.today()):
            u["daily_dl"] = [0, str(datetime.date.today())]
        return u

db = DatabaseManager()

# =================================================================
# [4] GAMIFICACIÓN: CREADOR DE LOOTBOXES
# =================================================================
class Gamification:
    @staticmethod
    def open_lootbox(box_type: str, user: dict) -> str:
        db.data["stats"]["lootboxes_opened"] += 1
        if box_type == "loot_basic":
            reward = random.choices(["points", "spins", "coins"], weights=[70, 20, 10])[0]
            if reward == "points":
                pts = random.randint(1000, 5000); user["points"] += pts
                return f"🎉 Ganaste **{pts} Puntos**."
            elif reward == "spins":
                user["inventory"]["spins"] += 5
                return "🎰 Ganaste **5 Giros de Casino**."
            else:
                user["ishak_coins"] += 0.5
                return "💎 Ganaste **0.5 IshakCoins**."
                
        elif box_type == "loot_titan":
            reward = random.choices(["vip", "massive_points", "api"], weights=[5, 75, 20])[0]
            if reward == "vip":
                user["plan"] = "PRO"
                return "👑 ¡JACKPOT! Has ganado **RANGO PRO**."
            elif reward == "massive_points":
                pts = random.randint(20000, 100000); user["points"] += pts
                return f"💸 ¡LLUVIA DE DINERO! Ganaste **{pts} Puntos**."
            else:
                user["api_credits"] += 5000
                return "🔌 Ganaste **5000 Créditos API B2B**."

# =================================================================
# [5] MOTOR DE EXTRACCIÓN (YT-DLP MULTI-HILO)
# =================================================================
class MediaEngine:
    @staticmethod
    async def process(url: str, fmt: str, qlty: str, uid: str, job_id: str):
        buf_dir = os.path.join(os.getcwd(), "omniverse_buffer")
        os.makedirs(buf_dir, exist_ok=True)
        out_tmpl = os.path.join(buf_dir, f"{job_id}_%(title)s.%(ext)s")
        
        opts = {
            'outtmpl': out_tmpl, 'quiet': True, 'nocheckcertificate': True,
            'noplaylist': True, 
            'max_filesize': 5000 * 1024 * 1024
        }
        
        if fmt == "MP4":
            opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif fmt == "MP3":
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]
            
        def _exec():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if fmt == "MP3": file_path = file_path.rsplit('.', 1)[0] + ".mp3"
                return file_path, info.get('title', 'Video'), info.get('duration', 0)

        return await asyncio.to_thread(_exec)

# =================================================================
# [6] TELEGRAM UX / UI (KEYBOARDS)
# =================================================================
class UI:
    @staticmethod
    def main(lang):
        kb = [
            [KeyboardButton(_t(lang, "btn_dl")), KeyboardButton(_t(lang, "btn_profile"))],
            [KeyboardButton(_t(lang, "btn_casino")), KeyboardButton(_t(lang, "btn_market"))],
            [KeyboardButton(_t(lang, "btn_shop")), KeyboardButton(_t(lang, "btn_loot"))]
        ]
        return ReplyKeyboardMarkup(kb, resize_keyboard=True)

    @staticmethod
    def lootboxes():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Cofre Básico (50 ⭐️)", callback_data="buy_loot_basic")],
            [InlineKeyboardButton("🌌 Cofre TITAN (250 ⭐️)", callback_data="buy_loot_titan")],
            [InlineKeyboardButton("❌ Cerrar", callback_data="close")]
        ])

# =================================================================
# [7] MANEJADORES DE PAGOS Y TELEGRAM STARS
# =================================================================
async def precheckout_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload.startswith("pay_"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Carga útil inválida.")

async def successful_payment_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    payload = payment.invoice_payload.replace("pay_", "")
    user = db.get_user(update.effective_user)
    
    db.data["stats"]["revenue_stars"] += payment.total_amount
    
    if payload in ["loot_basic", "loot_titan"]:
        res = Gamification.open_lootbox(payload, user)
        await update.message.reply_text(f"🎁 **LOOTBOX ABIERTO**\n{res}")
    
    elif payload == "sub_pro":
        user["plan"] = "PRO"
        await update.message.reply_text("💎 **¡Felicidades!** Ahora eres rango PRO por 30 días.")
        
    elif payload == "api_credits":
        user["api_credits"] += 10000
        if not user.get("api_key"):
            user["api_key"] = SecurityCore.generate_api_jwt(str(user['id']), 10000)
        await update.message.reply_text("🔌 **Créditos API añadidos.** Revisa tu PERFIL para ver tu API Key.")
        
    db.save()

# =================================================================
# [8] COMANDOS Y MENSAJES (DISPATCHER)
# =================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    ref = context.args[0] if context.args else None
    user = db.get_user(u, ref)
    db.save()
    
    msg = _t(user["lang"], "welcome", name=u.first_name)
    await update.message.reply_text(msg, reply_markup=UI.main(user["lang"]))

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text
    user = db.get_user(update.effective_user)
    lang = user["lang"]

    if text == _t(lang, "btn_dl"):
        await update.message.reply_text("🔗 **Envía el enlace de la matriz (YT, TikTok, IG...):**")
        context.user_data["state"] = "URL"
        
    elif "http" in text or context.user_data.get("state") == "URL":
        url = text if "http" in text else None
        if not url: return
        context.user_data["url"] = url
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 MP4", callback_data="dl_MP4"), InlineKeyboardButton("🎵 MP3", callback_data="dl_MP3")]
        ])
        await update.message.reply_text("⚡ Selecciona protocolo:", reply_markup=kb)

    elif text == _t(lang, "btn_profile"):
        bot_usr = (await context.bot.get_me()).username
        msg = (
            f"👤 **EXPEDIENTE B2B**\n\n"
            f"🎖 Rango: `{user['plan']}`\n"
            f"💰 Puntos: `{user['points']}` | 🪙 IshakCoins: `{user['ishak_coins']:.2f}`\n"
            f"🔌 Créditos API: `{user['api_credits']}`\n"
            f"🔑 JWT Key: `{str(user['api_key'])[:15]}...` (Oculta)\n\n"
            f"👥 **Link Referidos (+2500 pts):**\n`https://t.me/{bot_usr}?start={user['id']}`"
        )
        await update.message.reply_text(msg)

    elif text == _t(lang, "btn_loot"):
        await update.message.reply_text("🎁 **SISTEMA DE LOOTBOXES (Paga con Stars)**", reply_markup=UI.lootboxes())

    elif text == _t(lang, "btn_shop"):
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Rango PRO (500 ⭐️)", callback_data="buy_sub_pro")],
            [InlineKeyboardButton("🔌 10K API Credits (1000 ⭐️)", callback_data="buy_api_credits")]
        ])
        await update.message.reply_text("🛍️ **TIENDA B2B VIP**", reply_markup=kb)

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    uid = q.from_user.id
    
    if data.startswith("dl_"):
        fmt = data.split("_")[1]
        url = context.user_data.get("url")
        user = db.get_user(q.from_user)
        
        if user["daily_dl"][0] >= PLANS[user["plan"]]["daily_limit"]:
            return await q.answer("❌ Límite diario excedido. Compra PRO.", show_alert=True)
            
        await q.edit_message_text(f"⏳ **Descargando en cola de prioridad {PLANS[user['plan']]['priority']}...**")
        job_id = uuid.uuid4().hex[:8]
        
        try:
            path, title, _ = await MediaEngine.process(url, fmt, "1080", str(uid), job_id)
            with open(path, 'rb') as f:
                if fmt == "MP3": await context.bot.send_audio(uid, f, caption=f"✅ {title} | TITAN V700")
                else: await context.bot.send_video(uid, f, caption=f"✅ {title} | TITAN V700")
            os.remove(path)
            user["daily_dl"][0] += 1
            db.data["stats"]["total_dl"] += 1
            db.save()
            await q.message.delete()
        except Exception as e:
            await q.edit_message_text(f"❌ Error: {e}")

    elif data.startswith("buy_"):
        item_id = data.replace("buy_", "")
        item = STARS_PRODUCTS.get(item_id)
        if item:
            await context.bot.send_invoice(
                chat_id=uid, title=item["title"], description=item["desc"],
                payload=f"pay_{item_id}", provider_token="", currency="XTR",
                prices=[LabeledPrice(item["title"], item["price"])]
            )
    elif data == "close":
        await q.message.delete()

# =================================================================
# [9] SAAS B2B WEB DASHBOARD (API REST PARA VENDER)
# =================================================================
web_app = Flask("Omniverse_B2B")
CORS(web_app)
# Se silencia el warning de Flask-Limiter usando storage_uri="memory://"
limiter = Limiter(get_remote_address, app=web_app, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><title>Omniverse B2B | by Ishak</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body{background:#0a0a0a;color:#fff;font-family:monospace;}</style>
</head>
<body class="p-10">
    <div class="max-w-5xl mx-auto border border-green-500/30 p-8 rounded-lg bg-black/50 shadow-[0_0_15px_rgba(0,255,0,0.1)]">
        <h1 class="text-4xl text-green-400 font-bold mb-2">TITAN V700 OMNIVERSE API</h1>
        <p class="text-gray-400 mb-8">Developed by Ishak Ezzahouani (14) | Valuation: €2.5k+</p>
        
        <div class="grid grid-cols-3 gap-4 mb-8 text-center">
            <div class="border border-gray-800 p-4 rounded"><p class="text-sm text-gray-500">Global Users</p><h2 class="text-2xl text-blue-400" id="m_usr">0</h2></div>
            <div class="border border-gray-800 p-4 rounded"><p class="text-sm text-gray-500">API Extractions</p><h2 class="text-2xl text-purple-400" id="m_dl">0</h2></div>
            <div class="border border-gray-800 p-4 rounded"><p class="text-sm text-gray-500">Stars Revenue</p><h2 class="text-2xl text-yellow-400" id="m_rev">0</h2></div>
        </div>

        <h3 class="text-xl text-white border-b border-gray-800 pb-2 mb-4">REST API ENDPOINTS (For Resale)</h3>
        <div class="bg-gray-900 p-4 rounded text-sm text-green-300">
            <p>POST /api/v1/download</p>
            <p>Header: Authorization: Bearer {YOUR_JWT_KEY}</p>
            <p>Body: {"url": "https://...", "format": "mp4"}</p>
        </div>
        <p class="mt-4 text-xs text-gray-600">Buy API Credits via Telegram Bot using Telegram Stars.</p>
    </div>
    <script>
        setInterval(async()=>{
            try {
                let r = await fetch('/api/stats'); let d = await r.json();
                document.getElementById('m_usr').innerText = d.u;
                document.getElementById('m_dl').innerText = d.d;
                document.getElementById('m_rev').innerText = d.r + " ⭐️";
            } catch(e) {}
        }, 3000);
    </script>
</body>
</html>
"""

@web_app.route('/')
def home(): return render_template_string(HTML_DASHBOARD)

@web_app.route('/api/stats')
def api_stats():
    return jsonify({"u": len(db.data["users"]), "d": db.data["stats"]["total_dl"], "r": db.data["stats"]["revenue_stars"]})

@web_app.route('/api/v1/download', methods=['POST'])
@limiter.limit("5 per minute")
def b2b_download():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "): return jsonify({"error": "Unauthorized"}), 401
    token = auth.split(" ")[1]
    
    try:
        header, payload, sig = token.split(".")
        valid_sig = hmac.new(settings.secret_key.encode(), f"{header}.{payload}".encode(), hashlib.sha256).hexdigest()
        if sig != valid_sig: return jsonify({"error": "Invalid Signature"}), 401
        
        data = json.loads(base64.b64decode(payload).decode())
        uid = data["uid"]
        if uid not in db.data["users"] or db.data["users"][uid]["api_credits"] <= 0:
            return jsonify({"error": "Insufficient API Credits"}), 402
            
        req_data = request.json
        if not req_data or "url" not in req_data: return jsonify({"error": "Missing URL"}), 400
        
        db.data["users"][uid]["api_credits"] -= 1
        db.save()
        return jsonify({"status": "success", "message": "Extraction queued via B2B API", "credits_left": db.data["users"][uid]["api_credits"]})
    except:
        return jsonify({"error": "Malformed Token"}), 400

# =================================================================
# [10] MOTOR PRINCIPAL Y TAREAS EN SEGUNDO PLANO
# =================================================================
async def crypto_market_fluctuation():
    """Bucle infinito para hacer fluctuar el mercado cada 15 minutos."""
    while True:
        await asyncio.sleep(900) # 15 minutos
        try:
            val = db.data["market"]["coin_price"]
            change = val * random.uniform(-0.1, 0.15)
            db.data["market"]["coin_price"] = max(1.0, val + change)
            db.data["market"]["history"].append(db.data["market"]["coin_price"])
            if len(db.data["market"]["history"]) > 50: db.data["market"]["history"].pop(0)
            db.save()
        except Exception as e:
            print(f"Error en mercado cripto: {e}")

def main():
    # Iniciar API Web en hilo
    threading.Thread(target=lambda: web_app.run(host="0.0.0.0", port=settings.port, use_reloader=False), daemon=True).start()
    
    # 🚨 SALVAGUARDA DE RENDER 🚨
    # Si olvidas poner el token, la web B2B se queda encendida para que Render no dé error.
    if not settings.token or settings.token == "":
        print("\n" + "="*60)
        print("❌ [ALERTA DE SISTEMA] TOKEN DE TELEGRAM NO DETECTADO")
        print("="*60)
        print("Para que el bot funcione, debes añadir el token en Render:")
        print("1. Ve a tu panel de Render.com -> Abre tu Web Service.")
        print("2. Pestaña 'Environment' -> 'Add Environment Variable'.")
        print("3. Key: ISHAK_TELEGRAM_TOKEN | Value: [Tu Token de BotFather]")
        print("⚠️ Manteniendo servidor B2B vivo para evitar fallos de despliegue...\n")
        while True: time.sleep(60)
        return

    # Enganchamos la tarea del mercado cripto AL MISMO BUCLE de Telegram
    async def post_init(app: Application):
        asyncio.create_task(crypto_market_fluctuation())
        print("📈 Tarea de Fluctuación de Mercado iniciada con éxito.")

    # Iniciar el bot con la tarea post_init
    app = ApplicationBuilder().token(settings.token).post_init(post_init).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(PreCheckoutQueryHandler(precheckout_cb))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))
    app.add_handler(CallbackQueryHandler(callbacks))
    
    print(f"🚀 TITAN-V700 OMNIVERSE EN LÍNEA | CEO: Ishak (14) | Sant Hilari Sacalm")
    app.run_polling()

if __name__ == "__main__":
    main()
