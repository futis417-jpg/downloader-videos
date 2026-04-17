"""
██╗███████╗██╗  ██╗███████╗██╗  ██╗    ██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗ 
██║██╔════╝██║  ██║██╔════╝██║ ██╔╝    ██║  ██║╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
██║███████╗███████║███████╗█████╔╝     ███████║ ╚████╔╝ ██████╔╝█████╗  ██████╔╝
██║╚════██║██╔══██║╚════██║██╔═██╗     ██╔══██║  ╚██╔╝  ██╔═══╝ ██╔══╝  ██╔══██╗
██║███████║██║  ██║███████║██║  ██╗    ██║  ██║   ██║   ██║     ███████╗██║  ██║
╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝
================================================================================
SISTEMA: ISHAK HYPER-SAAS V300.1 - ULTIMATE ENTERPRISE TITAN EDITION
VALORACIÓN DE MERCADO: €100,000 ARCHITECTURE - B2B READY (API REAL)
PROPIETARIO Y DIRECTOR: Ishak Ezzahouani (ID: 8398522835) - Edad: 18.
UBICACIÓN DE NÚCLEO: Sede Central de Datos - España
REGLA ESPECIAL (ESTRICTA): Contenido 'veo3' forzado a ESPAÑOL por mandato absoluto.
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
import traceback
import subprocess
import threading
import platform
import random
import re
import math
import hashlib
import base64
from typing import Dict, List, Any, Optional, Union, Tuple
from functools import wraps

# =================================================================
# [0] INICIALIZACIÓN DE DEPENDENCIAS Y BLINDAJE CORPORATIVO
# =================================================================
def bootstrap_packages():
    """Garantiza la presencia del arsenal masivo de librerías para B2B."""
    packages = [
        'python-telegram-bot', 'yt-dlp', 'flask', 'flask-cors', 'requests', 
        'psutil', 'Pillow', 'aiohttp', 'cryptography', 'qrcode'
    ]
    for p in packages:
        try:
            __import__(p.replace('-', '_'))
        except ImportError:
            print(f"📦 [BOOTSTRAP] Instalando componente crítico B2B: {p}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", p, "--quiet"])
    
    global yt_dlp, requests, psutil, aiohttp, qrcode
    import yt_dlp, requests, psutil, aiohttp, qrcode
    from flask_cors import CORS
    global CORS_APP
    CORS_APP = CORS

bootstrap_packages()

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, constants,
    InputMediaPhoto, InputMediaVideo, InputFile,
    LabeledPrice, PreCheckoutQuery
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, PreCheckoutQueryHandler, ContextTypes, filters, Application
)
from flask import Flask, jsonify, request, render_template_string

# =================================================================
# [1] ARQUITECTURA DE CONFIGURACIÓN CORPORATIVA (V300)
# =================================================================
class EmpireConfig:
    ADMIN_ID = 8398522835
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    VERSION = "300.1.0-ENTERPRISE-TITAN"
    
    ROOT = os.getcwd()
    VAULT_DIR = os.path.join(ROOT, "empire_vault")
    BUFFER_DIR = os.path.join(ROOT, "download_buffer")
    LOGS_DIR = os.path.join(ROOT, "system_logs")
    BACKUP_DIR = os.path.join(VAULT_DIR, "backups")
    DATABASE_PATH = os.path.join(VAULT_DIR, "empire_master_v300.json")
    QR_DIR = os.path.join(BUFFER_DIR, "qrcodes")
    
    PLANS = {
        "FREE": {
            "name": "🆓 CIUDADANO", "limit_daily": 5, "max_file_mb": 150,
            "resolutions": ["360p", "720p"], "speed": "Estándar (2MB/s)",
            "priority": 0, "max_duration_min": 15
        },
        "PRO": {
            "name": "💎 ELITE (PRO)", "limit_daily": 150, "max_file_mb": 1500,
            "resolutions": ["360p", "720p", "1080p"], "speed": "Alta (25MB/s)",
            "priority": 1, "max_duration_min": 120
        },
        "ULTRA": {
            "name": "🔥 SOBERANO (ULTRA)", "limit_daily": 500, "max_file_mb": 10000,
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K"], 
            "speed": "Instántanea", "priority": 2, "max_duration_min": 600
        },
        "GOD": {
            "name": "👁️ OMNIPRESENTE (GOD)", "limit_daily": float('inf'), "max_file_mb": float('inf'),
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K", "Original"], 
            "speed": "Quantum", "priority": 3, "max_duration_min": float('inf')
        }
    }

    ECONOMY = {
        "DAILY_REWARD_MIN": 150, "DAILY_REWARD_MAX": 500,
        "REF_REWARD": 1500, "PRICE_PRO_DAY": 1000, "PRICE_ULTRA_DAY": 3500,
        "XP_PER_DOWNLOAD": 25, "XP_PER_MESSAGE": 2,
    }

    SHOP_ITEMS = {
        "XP_BOOST_X2": {"name": "🧪 Multiplicador XP x2 (24h)", "price": 5000, "desc": "Gana el doble de XP por un día."},
        "BYPASS_QUEUE": {"name": "🚀 Bypass de Cola", "price": 3000, "desc": "Prioridad máxima en tu próxima descarga."},
        "CLAN_TICKET": {"name": "🛡️ Permiso Fundación Facción", "price": 10000, "desc": "Te permite crear tu propia Facción."}
    }

    STARS_PACKAGES = {
        "PACK_SMALL": {"name": "💰 5,000 Puntos (Packs)", "type": "points", "stars": 50, "value": 5000},
        "PACK_MEDIUM": {"name": "💎 15,000 Puntos (Packs)", "type": "points", "stars": 120, "value": 15000},
        "SUB_PRO_30D": {"name": "👑 SUSCRIPCIÓN PRO (30 DÍAS)", "type": "sub", "stars": 250, "value": "PRO"}
    }

    ACHIEVEMENTS = {
        "FIRST_BLOOD": {"name": "Primera Sangre", "desc": "Realiza tu primera descarga.", "reward": 500},
        "CENTURION": {"name": "Centurión", "desc": "Alcanza 100 descargas.", "reward": 5000},
        "INFLUENCER": {"name": "Influencer", "desc": "Invita a 10 ciudadanos.", "reward": 10000},
        "GAMBLER": {"name": "Ludópata Imperial", "desc": "Juega 50 veces en el casino.", "reward": 2000},
        "GUILD_MASTER": {"name": "Maestro de Gremio", "desc": "Funda una Facción.", "reward": 3000},
        "INVESTOR": {"name": "Inversor Privado", "desc": "Compra con Telegram Stars.", "reward": 5000},
        "HACKER": {"name": "Cyber-Hacker", "desc": "Genera una API Key B2B.", "reward": 1000}
    }

    @classmethod
    def init_filesystem(cls):
        for d in [cls.VAULT_DIR, cls.BUFFER_DIR, cls.LOGS_DIR, cls.BACKUP_DIR, cls.QR_DIR]:
            os.makedirs(d, exist_ok=True)

EmpireConfig.init_filesystem()

# =================================================================
# [2] SISTEMA DE AUDITORÍA
# =================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "enterprise_audit.log"), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ISHAK_ENTERPRISE_V300")
logger.info(f"Arquitectura SaaS V300.1 iniciada. Sede: España. Bienvenido, Director Ishak (18).")

# =================================================================
# [3] BASE DE DATOS NOSQL EN MEMORIA (ENTERPRISE SYNC)
# =================================================================
class EmpireDatabase:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.data = {
            "users": {}, "coupons": {}, "blacklist": [],
            "factions": {}, "transactions": [], "tickets": {},
            "b2b_api_keys": {}, # Diccionario {api_key: uid}
            "market_stats": {"crypto_value": 150.0, "trend": "up", "history": []},
            "stats": {
                "total_downloads": 0, "total_users": 0, "bytes_processed": 0,
                "boot_time": str(datetime.datetime.now()), "commands_executed": 0,
                "stars_revenue": 0, "fraud_attempts_blocked": 0
            },
            "system": {
                "maint_mode": False,
                "global_welcome": "👑 **BIENVENIDO A ISHAK ENTERPRISE V300**\nLa plataforma definitiva de gestión multimedia.\nVelocidad, seguridad y control absoluto."
            }
        }
        self.sync_load()

    def sync_load(self):
        if os.path.exists(EmpireConfig.DATABASE_PATH):
            try:
                with open(EmpireConfig.DATABASE_PATH, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    self._merge_dicts(self.data, saved_data)
            except Exception as e:
                logger.error(f"Error crítico cargando DB: {e}")

    def _merge_dicts(self, default_dict, saved_dict):
        for k, v in saved_dict.items():
            if isinstance(v, dict) and k in default_dict and isinstance(default_dict[k], dict):
                self._merge_dicts(default_dict[k], v)
            else:
                default_dict[k] = v

    async def save(self):
        async with self._lock:
            try:
                temp_path = f"{EmpireConfig.DATABASE_PATH}.tmp"
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=4, ensure_ascii=False)
                os.replace(temp_path, EmpireConfig.DATABASE_PATH)
            except Exception as e:
                logger.error(f"Fallo persistencia DB: {e}")

    async def backup_job(self):
        while True:
            await asyncio.sleep(60 * 60 * 2)
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(EmpireConfig.BACKUP_DIR, f"db_backup_{timestamp}.json")
                shutil.copy2(EmpireConfig.DATABASE_PATH, backup_path)
            except Exception as e:
                logger.error(f"Error backup: {e}")

    async def get_user(self, user_obj):
        uid = str(user_obj.id)
        is_new = False
        async with self._lock:
            if uid not in self.data["users"]:
                is_new = True
                self.data["users"][uid] = {
                    "id": user_obj.id, "name": user_obj.first_name, "username": user_obj.username,
                    "plan": "GOD" if user_obj.id == EmpireConfig.ADMIN_ID else "FREE",
                    "plan_expiry": None, "points": 1500, "level": 1, "xp": 0,
                    "total_downloads": 0, "daily_downloads": [0, str(datetime.date.today())],
                    "referrals": 0, "referred_by": None, "achievements": [],
                    "inventory": {"XP_BOOST_X2": 0, "BYPASS_QUEUE": 0, "CLAN_TICKET": 0},
                    "active_buffs": {"xp_multiplier": 1.0, "buff_expiry": None},
                    "settings": {"watermark": None, "auto_transcribe": False, "ghost_mode": False, "send_as_doc": False},
                    "faction": None, "joined": str(datetime.date.today()),
                    "is_banned": False, "captcha_solved": False, "fraud_warnings": 0,
                    "stats": {"casino_played": 0, "bounties_done": 0, "stars_spent": 0},
                    "last_daily": None, "api_key": None
                }
                self.data["stats"]["total_users"] += 1
        
        if is_new: await self.save()
        u = self.data["users"][uid]
        
        today = str(datetime.date.today())
        if u["daily_downloads"][1] != today:
            u["daily_downloads"] = [0, today]
            await self.save()
            
        if u.get("plan_expiry") and datetime.datetime.now() > datetime.datetime.fromisoformat(u["plan_expiry"]):
            u["plan"] = "FREE"
            u["plan_expiry"] = None
            await self.save()
            
        if u["active_buffs"].get("buff_expiry") and datetime.datetime.now() > datetime.datetime.fromisoformat(u["active_buffs"]["buff_expiry"]):
            u["active_buffs"] = {"xp_multiplier": 1.0, "buff_expiry": None}
            await self.save()
            
        return u

    async def log_tx(self, uid, amount, desc):
        self.data["transactions"].append({
            "uid": uid, "amount": amount, "desc": desc, "date": str(datetime.datetime.now())
        })
        if len(self.data["transactions"]) > 5000: self.data["transactions"].pop(0)
        await self.save()

db = EmpireDatabase()

# =================================================================
# [4] FRAUD DETECTION & SECURITY CORE
# =================================================================
class SecurityCore:
    def __init__(self):
        self.spam_cache = {}
        self.captcha_cache = {}

    def rate_limit(self, uid: int, limit: int = 5) -> bool:
        now = time.time()
        if uid in self.spam_cache:
            last_time, count = self.spam_cache[uid]
            if now - last_time < 2:
                self.spam_cache[uid] = (now, count + 1)
                return count + 1 > limit
            else:
                self.spam_cache[uid] = (now, 1)
        else:
            self.spam_cache[uid] = (now, 1)
        return False

    def generate_captcha(self, uid):
        a = random.randint(10, 50)
        b = random.randint(1, 10)
        ans = a + b
        self.captcha_cache[uid] = ans
        return f"Suma de verificación Anti-Bot: {a} + {b}"

    def verify_captcha(self, uid, text):
        if uid in self.captcha_cache:
            try:
                if int(text.strip()) == self.captcha_cache[uid]:
                    del self.captcha_cache[uid]
                    return True
            except: pass
        return False

sec_core = SecurityCore()

# =================================================================
# [5] MOTOR DE MEDIOS (V300 HOOKS & ASYNC ENGINE)
# =================================================================
class DownloadProgressTracker:
    def __init__(self):
        self.active_jobs = {}
    
    def add_job(self, job_id, message_obj):
        self.active_jobs[job_id] = {
            'msg': message_obj, 'status': 'Iniciando', 'percent': 0,
            'speed': '0B/s', 'eta': 'Calculando...', 'last_update': time.time(),
            'finished': False
        }

    async def update_messages_loop(self):
        while True:
            await asyncio.sleep(3)
            for job_id, data in list(self.active_jobs.items()):
                if data['finished']:
                    del self.active_jobs[job_id]
                    continue
                
                now = time.time()
                if now - data['last_update'] >= 3:
                    try:
                        bar_length = 15
                        filled = int(bar_length * data['percent'] / 100)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        text = (
                            f"⚡ **SINTETIZANDO DATOS (V300)...**\n"
                            f"Progreso: `{bar}` {data['percent']:.1f}%\n"
                            f"Velocidad: `{data['speed']}` | ETA: `{data['eta']}`"
                        )
                        if data.get('last_text') != text:
                            await data['msg'].edit_text(text, parse_mode="Markdown")
                            data['last_text'] = text
                            data['last_update'] = now
                    except: pass

progress_tracker = DownloadProgressTracker()

class MediaEngine:
    @staticmethod
    async def get_thumbnail(url: str, uid: str) -> Optional[str]:
        try:
            def _get():
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    return ydl.extract_info(url, download=False).get('thumbnail')
            return await asyncio.to_thread(_get)
        except: return None

    @staticmethod
    async def get_metadata(url: str) -> dict:
        try:
            def _get():
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    i = ydl.extract_info(url, download=False)
                    return {"title": i.get("title"), "duration": i.get("duration"), "uploader": i.get("uploader"), "view_count": i.get("view_count")}
            return await asyncio.to_thread(_get)
        except: return {}

    @staticmethod
    async def run(url: str, mode: str, quality: str, uid: str, max_size_mb: int, job_id: str, settings: dict):
        output_template = os.path.join(EmpireConfig.BUFFER_DIR, f"{job_id}.%(ext)s")
        
        def yt_dlp_hook(d):
            if d['status'] == 'downloading':
                job = progress_tracker.active_jobs.get(job_id)
                if job:
                    try:
                        p_str = d.get('_percent_str', '0.0%').replace('%', '').strip()
                        job['percent'] = float(p_str)
                        job['speed'] = d.get('_speed_str', '0B/s')
                        job['eta'] = d.get('_eta_str', 'Desconocido')
                    except: pass

        ydl_opts = {
            'outtmpl': output_template, 'quiet': True, 'no_warnings': True,
            'noplaylist': True, 'max_filesize': max_size_mb * 1024 * 1024,
            'nocheckcertificate': True, 'progress_hooks': [yt_dlp_hook],
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}
        }

        # REGLA VEO3: FORZADO A ESPAÑOL
        if "veo3" in url.lower():
            logger.info(f"[ALERTA CORE] Regla veo3 activada para UID {uid}. Forzando ESPAÑOL.")
            ydl_opts['writesubtitles'] = True
            ydl_opts['subtitleslangs'] = ['es', 'spa']
            ydl_opts['format_sort'] = ['+language:es', 'res:1080', 'ext:mp4:m4a']

        if mode == "MP3":
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]})
        elif mode == "VOICE":
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'vorbis', 'preferredquality': '192'}]})
        elif mode == "GIF":
            h = quality.replace("p", "") if quality != "Original" else "720"
            ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]/best'
        else:
            h = quality.replace("p", "") if quality != "Original" else "2160"
            ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        def _execute():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if mode == "MP3": file_path = os.path.splitext(file_path)[0] + ".mp3"
                elif mode == "VOICE": file_path = os.path.splitext(file_path)[0] + ".ogg"
                
                # Check existance before getting size to avoid crashes
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                return file_path, info.get('title', 'Media_Enterprise_V300'), info.get('duration', 0), file_size

        return await asyncio.to_thread(_execute)

# =================================================================
# [6] INTERFAZ DE USUARIO (GUI ENTERPRISE V300)
# =================================================================
class EmpireUI:
    @staticmethod
    def main_keyboard(u_data):
        if u_data.get("is_banned"): return ReplyKeyboardMarkup([[KeyboardButton("🎧 SOPORTE")]], resize_keyboard=True)
        
        is_admin = u_data['id'] == EmpireConfig.ADMIN_ID
        is_god = u_data['plan'] == 'GOD'
        
        btns = [
            [KeyboardButton("📥 EXTRACCIÓN"), KeyboardButton("👤 PERFIL")],
            [KeyboardButton("⭐️ TIENDA OFICIAL (STARS)"), KeyboardButton("💎 MERCADO NEGRO")],
            [KeyboardButton("⚙️ AJUSTES PRO"), KeyboardButton("🎰 CASINO IMPERIAL")],
            [KeyboardButton("🛠️ CAJA DE HERRAMIENTAS"), KeyboardButton("🛡️ FACCIONES")],
            [KeyboardButton("🎁 TRIBUTO"), KeyboardButton("🎧 SOPORTE")]
        ]
        
        # EL ÁREA B2B SOLO APARECE PARA RANGOS GOD (CORRECCIÓN DE RESTRICCIÓN)
        if is_god:
            btns.append([KeyboardButton("🏢 ÁREA B2B")])
            
        if is_admin:
            btns.append([KeyboardButton("👑 PANEL OVERLORD 👑"), KeyboardButton("🌐 DATOS MATRIZ")])
            
        return ReplyKeyboardMarkup(btns, resize_keyboard=True)

    @staticmethod
    def format_selector():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 VIDEO (MP4)", callback_data="fmt_MP4"),
             InlineKeyboardButton("🎵 AUDIO (MP3)", callback_data="fmt_MP3")],
            [InlineKeyboardButton("🎙️ NOTA DE VOZ (OGG)", callback_data="fmt_VOICE"),
             InlineKeyboardButton("🎞️ ANIMACIÓN (GIF)", callback_data="fmt_GIF")],
            [InlineKeyboardButton("❌ ABORTAR", callback_data="u_close")]
        ])

    @staticmethod
    def quality_selector(plan_id):
        qualities = EmpireConfig.PLANS.get(plan_id, EmpireConfig.PLANS["FREE"])["resolutions"]
        rows = []
        for i in range(0, len(qualities), 2):
            rows.append([InlineKeyboardButton(f"🎥 {q}", callback_data=f"ql_{q}") for q in qualities[i:i+2]])
        rows.append([InlineKeyboardButton("⬅️ ATRÁS", callback_data="fmt_back")])
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def stars_shop():
        rows = []
        for k, v in EmpireConfig.STARS_PACKAGES.items():
            rows.append([InlineKeyboardButton(f"{v['name']} - {v['stars']} ⭐️", callback_data=f"stars_{k}")])
        rows.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def shop_panel():
        rows = []
        for k, v in EmpireConfig.SHOP_ITEMS.items():
            rows.append([InlineKeyboardButton(f"🛒 {v['name']} ({v['price']} pts)", callback_data=f"buy_item_{k}")])
        rows.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def settings_panel(settings):
        wm_status = settings['watermark'] if settings.get('watermark') else "Ninguna"
        transcribe = "✅" if settings.get('auto_transcribe') else "❌"
        ghost = "✅" if settings.get('ghost_mode') else "❌"
        doc_mode = "✅" if settings.get('send_as_doc') else "❌"
        
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🖋️ Marca de Agua: {wm_status}", callback_data="set_watermark")],
            [InlineKeyboardButton(f"📝 Auto-Transcribir IA: {transcribe}", callback_data="set_transcribe")],
            [InlineKeyboardButton(f"👻 Modo Fantasma: {ghost}", callback_data="set_ghost")],
            [InlineKeyboardButton(f"📄 Enviar como Documento: {doc_mode}", callback_data="set_doc")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def utils_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔐 Password", callback_data="util_pass"),
             InlineKeyboardButton("🔳 QR Code", callback_data="util_qr")],
            [InlineKeyboardButton("📜 Enc B64", callback_data="util_b64_enc"),
             InlineKeyboardButton("🔓 Dec B64", callback_data="util_b64_dec")],
            [InlineKeyboardButton("🖼️ Extraer Miniatura", callback_data="util_thumb"),
             InlineKeyboardButton("📊 Info Metadatos", callback_data="util_meta")],
            [InlineKeyboardButton("🗣️ Text to Speech", callback_data="util_tts"),
             InlineKeyboardButton("📡 Ping Test", callback_data="util_ping")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def b2b_panel(api_key):
        key_display = api_key if api_key else "No generada"
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Generar/Regenerar API Key", callback_data="b2b_gen_key")],
            [InlineKeyboardButton(f"Clave actual: {key_display[:8]}...", callback_data="dummy_btn") if api_key else InlineKeyboardButton("Sin clave", callback_data="dummy_btn")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def casino_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 Slots (100 pts)", callback_data="casino_slots")],
            [InlineKeyboardButton("🎡 Ruleta (250 pts)", callback_data="casino_roulette")],
            [InlineKeyboardButton("📈 Cripto Crash (500 pts)", callback_data="casino_crash")],
            [InlineKeyboardButton("❌ SALIR", callback_data="u_close")]
        ])

# =================================================================
# [7] MANEJADORES DE TELEGRAM STARS (MONETIZACIÓN OFICIAL V300)
# =================================================================
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload.startswith("stars_pack_"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Carga útil del paquete inválida.")

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid_str = str(update.message.from_user.id)
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    
    if payload.startswith("stars_pack_"):
        pack_key = payload.replace("stars_pack_", "")
        pack = EmpireConfig.STARS_PACKAGES.get(pack_key)
        
        if pack:
            u_data = await db.get_user(update.message.from_user)
            u_data["stats"]["stars_spent"] += payment.total_amount
            db.data["stats"]["stars_revenue"] += payment.total_amount
            
            if pack["type"] == "points":
                u_data["points"] += pack["value"]
                await db.log_tx(uid_str, pack["value"], f"Compra Stars: {pack['name']}")
                msg = f"✅ Has adquirido `{pack['value']} Puntos Imperiales`."
            
            elif pack["type"] == "sub":
                u_data["plan"] = pack["value"]
                current_expiry = u_data.get("plan_expiry")
                base_date = datetime.datetime.fromisoformat(current_expiry) if current_expiry else datetime.datetime.now()
                new_expiry = base_date + datetime.timedelta(days=30)
                u_data["plan_expiry"] = str(new_expiry)
                await db.log_tx(uid_str, 0, f"Suscripción PRO x30 días (Stars)")
                msg = f"✅ **SUSCRIPCIÓN ACTIVADA**. Eres PRO hasta `{new_expiry.date()}`."
            
            if "INVESTOR" not in u_data["achievements"]:
                u_data["achievements"].append("INVESTOR")
                u_data["points"] += 5000
                msg += "\n🏆 ¡LOGRO: Inversor Privado! +5000 pts"
            
            await db.save()
            await update.message.reply_text(f"💎 **TRANSACCIÓN CONFIRMADA**\n{msg}", parse_mode="Markdown")

# =================================================================
# [8] CONTROLADORES DE COMANDOS Y MENSAJES (EL NÚCLEO ARREGLADO)
# =================================================================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid_str = str(user.id)
    
    if sec_core.rate_limit(user.id): return
    if db.data["system"]["maint_mode"] and user.id != EmpireConfig.ADMIN_ID:
        return await update.message.reply_text("🛠️ **SISTEMA EN MANTENIMIENTO CORPORATIVO.** Vuelve más tarde.")

    u_data = await db.get_user(user)

    if not u_data.get("captcha_solved") and user.id != EmpireConfig.ADMIN_ID:
        question = sec_core.generate_captcha(user.id)
        await update.message.reply_text(f"🛡️ **VERIFICACIÓN ANTI-DDOS (V300).**\nResuelve:\n`{question}`\nResponde solo con el número.")
        context.user_data["state"] = "WAIT_CAPTCHA"
        return

    welcome_msg = db.data["system"]["global_welcome"]
    if user.id == EmpireConfig.ADMIN_ID:
        welcome_msg = "👁️ **SALVE, DIRECTOR ISHAK.**\nArquitectura V300 operativa. Sistemas B2B enrutados."

    await update.message.reply_text(welcome_msg, reply_markup=EmpireUI.main_keyboard(u_data), parse_mode="Markdown")

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user = update.effective_user
    text = update.message.text
    uid_str = str(user.id)

    if sec_core.rate_limit(user.id): return

    u_data = await db.get_user(user)
    if u_data.get("is_banned"):
        return await update.message.reply_text("🚫 Cuenta suspendida por infracción corporativa.")

    db.data["stats"]["commands_executed"] += 1

    # =====================================================================
    # CORRECCIÓN V300.1: STATE INTERRUPTER (PRIORIDAD ABSOLUTA DE BOTONES)
    # =====================================================================
    MAIN_COMMANDS = [
        "📥 EXTRACCIÓN", "⭐️ TIENDA OFICIAL (STARS)", "💎 MERCADO NEGRO", 
        "⚙️ AJUSTES PRO", "🏢 ÁREA B2B", "🎰 CASINO IMPERIAL", "🛠️ CAJA DE HERRAMIENTAS", 
        "👤 PERFIL", "🎁 TRIBUTO", "🎮 LOGROS", "🎧 SOPORTE", 
        "👑 PANEL OVERLORD 👑", "🌐 DATOS MATRIZ", "🛡️ FACCIONES"
    ]
    
    if text in MAIN_COMMANDS:
        # Si el usuario pulsó un botón principal, limpiamos cualquier estado activo
        context.user_data["state"] = None
        
    state = context.user_data.get("state")
    
    # Manejo de Captcha Independiente
    if state == "WAIT_CAPTCHA":
        if sec_core.verify_captcha(user.id, text):
            db.data["users"][uid_str]["captcha_solved"] = True
            await db.save()
            context.user_data["state"] = None
            await update.message.reply_text("✅ Acceso autorizado.", reply_markup=EmpireUI.main_keyboard(u_data))
        else:
            await update.message.reply_text("❌ Error en verificación.")
        return

    # =====================================================================
    # CORRECCIÓN V300.1: AUTO-DETECCIÓN DE ENLACES (SIN NECESIDAD DE ESTADO)
    # =====================================================================
    if not state and re.match(r'^https?://', text):
        context.user_data["active_url"] = text
        await update.message.reply_text("🛠 **Enlace detectado automáticamente.** Selecciona formato:", reply_markup=EmpireUI.format_selector())
        return

    # --- NAVEGACIÓN PRINCIPAL V300 ---
    if text == "📥 EXTRACCIÓN":
        await update.message.reply_text("🔗 **PROTOCOLOS LISTOS. ENVÍA EL ENLACE:**\n*(Veo3, YT, IG, TikTok...)*")
        context.user_data["state"] = "WAIT_URL"

    elif text == "⭐️ TIENDA OFICIAL (STARS)":
        await update.message.reply_text("⭐️ **MERCADO DIGITAL OFICIAL**\nSuscripciones y puntos mediante pagos seguros nativos (Telegram Stars):", reply_markup=EmpireUI.stars_shop())

    elif text == "💎 MERCADO NEGRO":
        cv = round(db.data["market_stats"]["crypto_value"], 2)
        msg = f"💎 **MERCADO CLANDESTINO**\nTu capital: `{u_data['points']} pts`.\nValor IshakCoin: `{cv}`\nUsa tus puntos para comprar ítems:"
        await update.message.reply_text(msg, reply_markup=EmpireUI.shop_panel(), parse_mode="Markdown")

    elif text == "⚙️ AJUSTES PRO":
        await update.message.reply_text("⚙️ **PANEL DE CONFIGURACIÓN AVANZADA:**", reply_markup=EmpireUI.settings_panel(u_data['settings']))

    elif text == "🏢 ÁREA B2B":
        if u_data['plan'] == 'GOD':
            await update.message.reply_text("🏢 **ENTORNO EMPRESARIAL B2B**\nGenera claves API reales para interactuar con nuestro endpoint remoto.", reply_markup=EmpireUI.b2b_panel(u_data.get('api_key')))
        else:
            await update.message.reply_text("🚫 Acceso restringido. Esta área es exclusiva para el rango GOD.")

    elif text == "🎰 CASINO IMPERIAL":
        await update.message.reply_text("🎰 **BIENVENIDO AL CASINO**\nMultiplica tus riquezas. Selecciona tu veneno:", reply_markup=EmpireUI.casino_panel())

    elif text == "🛠️ CAJA DE HERRAMIENTAS":
        await update.message.reply_text("🛠️ **UTILERÍA CYBERPUNK V300:**", reply_markup=EmpireUI.utils_panel())

    elif text == "👤 PERFIL":
        plan = EmpireConfig.PLANS[u_data["plan"]]
        msg = (
            f"👤 **PERFIL CORPORATIVO V300**\n"
            f"🆔 `{user.id}` | Rango: **{plan['name']}**\n"
            f"💰 Capital: `{u_data['points']} pts` | ⭐️ Stars Invertidas: `{u_data['stats'].get('stars_spent', 0)}`\n"
            f"📥 Extracciones Hoy: `{u_data['daily_downloads'][0]} / {plan['limit_daily']}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🎁 TRIBUTO":
        today = str(datetime.date.today())
        if u_data.get("last_daily") == today:
            await update.message.reply_text("❌ Tributo ya reclamado hoy.")
        else:
            u_data["last_daily"] = today
            r = random.randint(150, 500)
            if u_data["plan"] == "PRO": r = int(r * 1.5)
            elif u_data["plan"] in ["ULTRA", "GOD"]: r = int(r * 3)
            u_data["points"] += r
            await db.log_tx(uid_str, r, "Tributo Diario")
            await db.save()
            await update.message.reply_text(f"✅ El Imperio te otorga **{r} pts**.")

    # --- ESTADOS DE ENTRADA (FSM) ---
    elif state == "WAIT_URL":
        if re.match(r'^https?://', text):
            context.user_data["active_url"] = text
            await update.message.reply_text("🛠 Selecciona formato de salida:", reply_markup=EmpireUI.format_selector())
        else: await update.message.reply_text("❌ URL no válida.")
        context.user_data["state"] = None

    elif state == "WAIT_WATERMARK":
        u_data['settings']['watermark'] = text[:30]
        await db.save()
        await update.message.reply_text(f"✅ Marca de agua configurada a: `{text[:30]}`", parse_mode="Markdown")
        context.user_data["state"] = None
        
    elif state == "WAIT_UTIL_URL_THUMB":
        url = text.strip()
        m = await update.message.reply_text("⏳ Extrayendo miniatura máxima resolución...")
        thumb = await MediaEngine.get_thumbnail(url, uid_str)
        if thumb:
            await context.bot.send_photo(uid_str, thumb, caption="🖼️ Aquí tienes la miniatura.")
        else:
            await update.message.reply_text("❌ No se pudo extraer miniatura de ese enlace.")
        await m.delete(); context.user_data["state"] = None
        
    elif state == "WAIT_UTIL_URL_META":
        url = text.strip()
        m = await update.message.reply_text("⏳ Analizando metadatos...")
        meta = await MediaEngine.get_metadata(url)
        if meta:
            res = f"📊 **METADATOS EXTRAÍDOS**\n• Título: `{meta.get('title')}`\n• Autor: `{meta.get('uploader')}`\n• Duración: `{meta.get('duration')}s`\n• Vistas: `{meta.get('view_count')}`"
            await update.message.reply_text(res, parse_mode="Markdown")
        else: await update.message.reply_text("❌ Fallo en la extracción.")
        await m.delete(); context.user_data["state"] = None

    elif state == "WAIT_UTIL_TTS":
        tts = text[:500]
        await update.message.reply_text(f"🗣️ **Voz Sintética Generada:**\n*(Simulación Text-to-Speech V300)*\n`{tts}`", parse_mode="Markdown")
        context.user_data["state"] = None

# =================================================================
# [9] MOTOR DE CALLBACKS Y LÓGICA DE NEGOCIO
# =================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    uid_str = str(uid)
    data = q.data
    await q.answer()

    u_data = await db.get_user(q.from_user)

    # --- COMPRA DE STARS ---
    if data.startswith("stars_"):
        pack_key = data.replace("stars_", "")
        pack = EmpireConfig.STARS_PACKAGES.get(pack_key)
        if pack:
            title = pack["name"]
            description = f"Pago oficial para: {pack['name']} en Ishak SaaS."
            payload = f"stars_pack_{pack_key}"
            currency = "XTR"
            price = pack["stars"]
            prices = [LabeledPrice(title, price)]
            await context.bot.send_invoice(chat_id=uid, title=title, description=description, payload=payload, provider_token="", currency=currency, prices=prices)

    # --- TIENDA POR PUNTOS ---
    elif data.startswith("buy_item_"):
        item_key = data.replace("buy_item_", "")
        item = EmpireConfig.SHOP_ITEMS[item_key]
        if u_data["points"] >= item["price"]:
            u_data["points"] -= item["price"]
            if item_key == "XP_BOOST_X2":
                u_data["active_buffs"]["xp_multiplier"] = 2.0
                u_data["active_buffs"]["buff_expiry"] = str(datetime.datetime.now() + datetime.timedelta(days=1))
                await q.message.reply_text("🧪 Multiplicador de XP x2 activado por 24 horas.")
            else:
                u_data["inventory"][item_key] += 1
                await q.message.reply_text(f"📦 Añadido a tu inventario: {item['name']}")
            await db.save()
        else: await q.message.reply_text("❌ Puntos insuficientes.")

    # --- AJUSTES Y CONFIGURACIÓN ---
    elif data.startswith("set_"):
        action = data.split("_")[1]
        if action == "watermark":
            await q.message.reply_text("✍️ Escribe tu nueva Marca de Agua (Max 30 char):")
            context.user_data["state"] = "WAIT_WATERMARK"
        elif action == "transcribe":
            u_data['settings']['auto_transcribe'] = not u_data['settings'].get('auto_transcribe')
            await db.save(); await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))
        elif action == "ghost":
            if u_data['plan'] in ['ULTRA', 'GOD']:
                u_data['settings']['ghost_mode'] = not u_data['settings'].get('ghost_mode')
                await db.save(); await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))
            else: await q.message.reply_text("❌ El Modo Fantasma es exclusivo para rangos ULTRA o GOD.")
        elif action == "doc":
            u_data['settings']['send_as_doc'] = not u_data['settings'].get('send_as_doc')
            await db.save(); await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))

    # --- ÁREA B2B ---
    elif data == "b2b_gen_key":
        if u_data['plan'] != 'GOD':
            return await q.message.reply_text("❌ Acceso Denegado. Función de seguridad exclusiva para GOD.")
        
        # Eliminar clave vieja del diccionario global si existe
        old_key = u_data.get('api_key')
        if old_key and old_key in db.data['b2b_api_keys']:
            del db.data['b2b_api_keys'][old_key]
            
        new_key = f"ishak_live_{uuid.uuid4().hex}"
        u_data['api_key'] = new_key
        db.data['b2b_api_keys'][new_key] = uid_str
        
        if "HACKER" not in u_data["achievements"]:
            u_data["achievements"].append("HACKER"); u_data["points"]+=1000
        await db.save()
        await q.edit_message_text(f"🔑 **CLAVE API GENERADA:**\n`{new_key}`\n\n*Úsala para hacer POST a /api/v1/extract*\n*Requiere cabecera: X-API-KEY*", reply_markup=EmpireUI.b2b_panel(new_key))

    # --- CASINO ---
    elif data.startswith("casino_"):
        db.data["stats"]["casino_spins"] = db.data["stats"].get("casino_spins", 0) + 1
        game = data.split("_")[1]
        if game == "slots":
            bet = 100
            if u_data["points"] < bet: return await q.message.reply_text("❌ Puntos insuficientes.")
            u_data["points"] -= bet
            syms = ["🍒", "🍋", "🔔", "💎", "👑"]
            res = [random.choice(syms) for _ in range(3)]
            msg = f"🎰 **SLOTS**\n[ {res[0]} | {res[1]} | {res[2]} ]\n"
            if res[0] == res[1] == res[2]:
                w = bet * 10 if res[0] != "👑" else bet * 50
                u_data["points"] += w; msg += f"🎉 **¡JACKPOT!** Ganaste {w} pts."
            elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
                w = int(bet * 1.5)
                u_data["points"] += w; msg += f"👍 Recuperas {w} pts."
            else: msg += "💀 Perdiste."
            await db.save(); await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())

    # --- NUEVAS UTILIDADES ---
    elif data.startswith("util_"):
        act = data.split("_")[1]
        if act == "thumb":
            await q.message.reply_text("🖼️ Envía el enlace para extraer su miniatura:"); context.user_data["state"] = "WAIT_UTIL_URL_THUMB"
        elif act == "meta":
            await q.message.reply_text("📊 Envía el enlace para inspeccionar metadatos:"); context.user_data["state"] = "WAIT_UTIL_URL_META"
        elif act == "tts":
            await q.message.reply_text("🗣️ Escribe el texto para convertir a voz:"); context.user_data["state"] = "WAIT_UTIL_TTS"
        elif act == "ping":
            start_time = time.time()
            m = await q.message.reply_text("📡 Haciendo ping a los servidores núcleo...")
            end_time = time.time()
            await m.edit_text(f"📡 **Ping Test V300:**\nLatencia (Madrid -> Telegram): `{int((end_time - start_time) * 1000)}ms`")

    # --- EXTRACCIÓN ---
    elif data.startswith("fmt_"):
        mode = data.split("_")[1]
        if mode == "back": return await q.edit_message_text("🎬 Selecciona formato:", reply_markup=EmpireUI.format_selector())
        context.user_data["active_fmt"] = mode
        if mode in ["MP3", "GIF", "VOICE"]: await finalize_download(update, context)
        else: await q.edit_message_text("🎥 Selecciona resolución óptica:", reply_markup=EmpireUI.quality_selector(u_data["plan"]))

    elif data.startswith("ql_"):
        context.user_data["active_qlty"] = data.split("_")[1]
        await finalize_download(update, context)

    elif data == "u_close":
        try: await q.message.delete()
        except: pass

# =================================================================
# [10] MOTOR DE DESCARGA TITÁN (ARCHIVOS, VOZ, GIF)
# =================================================================
async def finalize_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    uid_str = str(uid)
    url = context.user_data.get("active_url")
    fmt = context.user_data.get("active_fmt")
    qlty = context.user_data.get("active_qlty", "720p")
    u_data = await db.get_user(q.from_user)

    plan_info = EmpireConfig.PLANS[u_data["plan"]]
    max_size = plan_info["max_file_mb"]

    msg = await q.edit_message_text(f"⚡ **MOTOR V300 INICIADO...**\n`[{fmt} | {qlty}]`")
    job_id = f"job_{uid_str}_{uuid.uuid4().hex[:6]}"
    progress_tracker.add_job(job_id, msg)
    
    try:
        path, title, duration, f_size = await MediaEngine.run(url, fmt, qlty, uid_str, max_size, job_id, u_data['settings'])
        
        if job_id in progress_tracker.active_jobs:
            progress_tracker.active_jobs[job_id]['finished'] = True
        
        size_mb = f_size / (1024 * 1024)
        if size_mb > max_size:
            if os.path.exists(path): os.remove(path)
            return await msg.edit_text(f"❌ Archivo excede límite de {max_size}MB.")

        await msg.edit_text("📤 **SUBIENDO AL SATÉLITE CORPORATIVO...**", parse_mode="Markdown")
        
        with open(path, 'rb') as f:
            wm_text = f"\n©️ Marca de Agua: `{u_data['settings']['watermark']}`" if u_data['settings'].get('watermark') else ""
            veo3_note = "\n🇪🇸 *Regla Directiva: Español (Veo3).* " if "veo3" in url.lower() else ""
            cap = (
                f"✅ **{title[:50]}...**\n"
                f"⏱️ `{str(datetime.timedelta(seconds=duration))}` | 💾 `{size_mb:.1f} MB`{wm_text}{veo3_note}\n"
            )
            
            # Modalidades avanzadas de entrega
            if u_data['settings'].get('send_as_doc'):
                await context.bot.send_document(uid, f, caption=cap, parse_mode="Markdown", read_timeout=300)
            elif fmt == "MP3": 
                await context.bot.send_audio(uid, f, caption=cap, parse_mode="Markdown", read_timeout=120)
            elif fmt == "VOICE":
                await context.bot.send_voice(uid, f, caption=cap, parse_mode="Markdown", read_timeout=120)
            elif fmt == "GIF":
                await context.bot.send_animation(uid, f, caption=cap, parse_mode="Markdown", read_timeout=300)
            else: 
                await context.bot.send_video(uid, f, caption=cap, parse_mode="Markdown", read_timeout=300, supports_streaming=True)

        u_data["daily_downloads"][0] += 1
        db.data["stats"]["total_downloads"] += 1
        await db.save()
        
        if os.path.exists(path) and not u_data['settings'].get('ghost_mode'): os.remove(path)
        try: await msg.delete()
        except: pass

    except Exception as e:
        if job_id in progress_tracker.active_jobs: progress_tracker.active_jobs[job_id]['finished'] = True
        logger.error(f"Fallo UID {uid}: {e}")
        await msg.edit_text(f"❌ **ERROR DE MATRIZ V300:**\nEl archivo está protegido o supera los límites de Telegram.")

# =================================================================
# [11] PANEL SAAS WEB (LANDING PAGE 100K€ + B2B API REAL)
# =================================================================
web_app = Flask("Ishak_Enterprise_Web")

# Habilitar CORS para que la API pueda ser consumida por otras webs
CORS_APP(web_app)

LANDING_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ishak Enterprise V300 | B2B Media Solutions</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: white; overflow-x: hidden; }
        .glass-panel { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .glow-text { text-shadow: 0 0 10px rgba(56, 189, 248, 0.8); }
        .gradient-text { background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
</head>
<body class="antialiased font-sans">
    
    <!-- Hero Section -->
    <div class="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
        <div class="absolute w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 top-0 left-0 animate-blob"></div>
        <div class="absolute w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 bottom-0 right-0 animate-blob animation-delay-2000"></div>
        
        <div class="z-10 text-center px-4 max-w-4xl glass-panel p-12 rounded-3xl shadow-2xl">
            <h1 class="text-6xl font-extrabold mb-4 tracking-tight"><span class="gradient-text">ISHAK</span> ENTERPRISE <span class="text-blue-400">V300</span></h1>
            <p class="text-xl text-gray-300 mb-8">La infraestructura de extracción multimedia más avanzada de España. Dirigida por Ishak (18). Valorada en 100.000€.</p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 text-left">
                <div class="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                    <i class="fas fa-rocket text-3xl text-blue-400 mb-3"></i>
                    <h3 class="text-xl font-bold mb-2">API B2B Funcional</h3>
                    <p class="text-sm text-gray-400">Endpoints REST reales para extraer URLs directas de CDNs (CORS Habilitado).</p>
                </div>
                <div class="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                    <i class="fas fa-shield-alt text-3xl text-purple-400 mb-3"></i>
                    <h3 class="text-xl font-bold mb-2">Seguridad SOC</h3>
                    <p class="text-sm text-gray-400">Protección Anti-DDoS, cancelación de hilos y modo fantasma.</p>
                </div>
                <div class="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                    <i class="fas fa-star text-3xl text-yellow-400 mb-3"></i>
                    <h3 class="text-xl font-bold mb-2">Telegram Stars</h3>
                    <p class="text-sm text-gray-400">Integración de pagos nativos y ecosistema financiero completo.</p>
                </div>
            </div>
            
            <a href="https://t.me/TuBotUsername" class="inline-block bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold py-4 px-10 rounded-full transition-all transform hover:scale-105 shadow-lg shadow-blue-500/30">
                INICIAR SISTEMA AHORA
            </a>
        </div>
    </div>

    <!-- Live Metrics Dashboard -->
    <div class="py-20 bg-slate-900 border-t border-slate-800">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <h2 class="text-3xl font-bold mb-12 glow-text">MÉTRICAS DEL NÚCLEO (LIVE)</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
                <div class="glass-panel p-6 rounded-2xl">
                    <div class="text-4xl font-bold text-blue-400 mb-2" id="val-users">0</div>
                    <div class="text-sm text-gray-400 uppercase tracking-wider">Ciudadanos</div>
                </div>
                <div class="glass-panel p-6 rounded-2xl">
                    <div class="text-4xl font-bold text-purple-400 mb-2" id="val-downloads">0</div>
                    <div class="text-sm text-gray-400 uppercase tracking-wider">Extracciones</div>
                </div>
                <div class="glass-panel p-6 rounded-2xl">
                    <div class="text-4xl font-bold text-green-400 mb-2" id="val-revenue">0 ⭐️</div>
                    <div class="text-sm text-gray-400 uppercase tracking-wider">Revenue Stars</div>
                </div>
                <div class="glass-panel p-6 rounded-2xl">
                    <div class="text-4xl font-bold text-yellow-400 mb-2" id="val-crypto">0</div>
                    <div class="text-sm text-gray-400 uppercase tracking-wider">IshakCoin Valor</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function fetchMetrics() {
            try {
                const res = await fetch('/api/v3/metrics');
                const data = await res.json();
                document.getElementById('val-users').innerText = data.metrics.users;
                document.getElementById('val-downloads').innerText = data.metrics.downloads;
                document.getElementById('val-revenue').innerText = data.metrics.revenue + " ⭐️";
                document.getElementById('val-crypto').innerText = data.metrics.crypto.toFixed(2);
            } catch (e) { console.log("Core sync error"); }
        }
        setInterval(fetchMetrics, 3000);
        fetchMetrics();
    </script>
</body>
</html>
"""

@web_app.route('/', methods=['GET'])
def index():
    return render_template_string(LANDING_HTML)

@web_app.route('/api/v3/metrics', methods=['GET'])
def api_metrics():
    return jsonify({
        "status": "ONLINE",
        "metrics": {
            "users": db.data["stats"]["total_users"],
            "downloads": db.data["stats"]["total_downloads"],
            "revenue": db.data["stats"].get("stars_revenue", 0),
            "crypto": db.data["market_stats"]["crypto_value"]
        }
    })

# =================================================================
# [11.1] ENDPOINT DE API B2B REAL (LA MAGIA CORPORATIVA)
# =================================================================
@web_app.route('/api/v1/extract', methods=['POST'])
def api_real_extract():
    """
    API Funcional para clientes B2B. Recibe una URL y devuelve el CDN Link directo.
    Requiere una API Key válida del rango GOD en los Headers.
    Header: X-API-KEY: ishak_live_xxxxxxxx
    """
    api_key = request.headers.get('X-API-KEY')
    if not api_key or api_key not in db.data.get('b2b_api_keys', {}):
        return jsonify({"error": "No autorizado. Clave de API ausente o inválida."}), 401
    
    data = request.json or {}
    url = data.get('url')
    if not url:
        return jsonify({"error": "Parámetro 'url' es requerido."}), 400
        
    uid = db.data['b2b_api_keys'][api_key]
    
    try:
        # Se ejecuta en hilo de Flask de forma sincrónica para devolver la respueta HTTP
        opts = {'quiet': True, 'noplaylist': True}
        
        if "veo3" in url.lower():
            opts['format_sort'] = ['+language:es', 'res:1080', 'ext:mp4:m4a']
            
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Buscamos la mejor URL del formato (URL cruda lista para reproducir en reproductores web o VLC)
            direct_url = info.get('url')
            if not direct_url and info.get('formats'):
                # Coger el último formato disponible si no hay url root
                direct_url = info['formats'][-1].get('url')
                
            return jsonify({
                "status": "success",
                "code": 200,
                "data": {
                    "title": info.get('title'),
                    "duration": info.get('duration'),
                    "direct_cdn_url": direct_url,
                    "thumbnail": info.get('thumbnail'),
                    "source": info.get('extractor')
                },
                "owner_id": uid
            })
    except Exception as e:
        return jsonify({"error": "Fallo durante la extracción en la matriz.", "details": str(e)}), 500

def run_web():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    try: 
        port = int(os.getenv("PORT", 8080))
        web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Fallo iniciando Dashboard Flask: {e}")

# =================================================================
# [12] SECUENCIA DE INICIO TITÁN (THE GOD DEPLOYMENT)
# =================================================================
async def post_init(app: Application):
    asyncio.create_task(db.backup_job())
    asyncio.create_task(progress_tracker.update_messages_loop())

def main():
    print("=" * 80)
    print(f"🚀 INICIANDO ISHAK HYPER-SAAS ENTERPRISE V{EmpireConfig.VERSION}")
    print("💎 INTEGRACIÓN TELEGRAM STARS (XTR) ACTIVA + DASHBOARD 100K€.")
    print("🛡️ REGLA VEO3 (ESPAÑOL) BLINDADA. FUNCIONALIDADES DE B2B ACTIVAS.")
    print("=" * 80)
    
    threading.Thread(target=run_web, daemon=True).start()
    
    application = (
        ApplicationBuilder()
        .token(EmpireConfig.TOKEN)
        .pool_timeout(60.0).read_timeout(60.0).write_timeout(60.0)
        .connection_pool_size(4096)
        .post_init(post_init)
        .build()
    )
    
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Apagado de emergencia por el Director Ishak.")
    except Exception as e:
        logger.critical(f"COLAPSO DEL CORE B2B: {traceback.format_exc()}")
