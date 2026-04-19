"""
██╗███████╗██╗  ██╗███████╗██╗  ██╗    ██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗ 
██║██╔════╝██║  ██║██╔════╝██║ ██╔╝    ██║  ██║╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
██║███████╗███████║███████╗█████╔╝     ███████║ ╚████╔╝ ██████╔╝█████╗  ██████╔╝
██║╚════██║██╔══██║╚════██║██╔═██╗     ██╔══██║  ╚██╔╝  ██╔═══╝ ██╔══╝  ██╔══██╗
██║███████║██║  ██║███████║██║  ██╗    ██║  ██║   ██║   ██║     ███████╗██║  ██║
╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝
================================================================================
SISTEMA: ISHAK HYPER-SAAS V400.0 - THE LEVIATHAN ENTERPRISE EDITION
VALORACIÓN DE MERCADO: €250,000 ARCHITECTURE - FULL B2B, CASINO & REDUNDANCY
PROPIETARIO Y DIRECTOR: Ishak Ezzahouani - Edad: 18.
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
        'psutil', 'Pillow', 'aiohttp', 'cryptography', 'qrcode', 'python-dotenv'
    ]
    for p in packages:
        try:
            __import__(p.replace('-', '_'))
        except ImportError:
            print(f"📦 [BOOTSTRAP] Instalando componente crítico B2B: {p}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", p, "--quiet"])
    
    global yt_dlp, requests, psutil, aiohttp, qrcode, load_dotenv
    import yt_dlp, requests, psutil, aiohttp, qrcode
    from dotenv import load_dotenv
    from flask_cors import CORS
    global CORS_APP
    CORS_APP = CORS

bootstrap_packages()
load_dotenv() # Cargar variables de entorno blindadas

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
# [1] ARQUITECTURA DE CONFIGURACIÓN CORPORATIVA (V400)
# =================================================================
class EmpireConfig:
    # BLINDAJE: Variables críticas ocultas en entorno
    ADMIN_ID = int(os.getenv("ADMIN_ID", "8398522835"))
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    VERSION = "400.0.0-LEVIATHAN-TITAN"
    
    if not TOKEN:
        print("❌ [ALERTA] TELEGRAM_TOKEN no definido en variables de entorno. Fallo crítico de seguridad.")
        sys.exit(1)
        
    ROOT = os.getcwd()
    VAULT_DIR = os.path.join(ROOT, "empire_vault")
    BUFFER_DIR = os.path.join(ROOT, "download_buffer")
    LOGS_DIR = os.path.join(ROOT, "system_logs")
    BACKUP_DIR = os.path.join(VAULT_DIR, "backups")
    
    # Sistema de Respaldo Redundante (Shadow Backups)
    DATABASE_PATH = os.path.join(VAULT_DIR, "empire_master_v400.json")
    SHADOW_DB_PATH = os.path.join(VAULT_DIR, "empire_shadow_v400.json")
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
        "CLAN_TICKET": {"name": "🛡️ Permiso Fundación Facción", "price": 10000, "desc": "Te permite crear tu propia Facción."},
        "RENAME_CARD": {"name": "📝 Tarjeta Cambio de Nombre", "price": 2000, "desc": "Cambia tu apodo en el Imperio."}
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
        "HACKER": {"name": "Cyber-Hacker", "desc": "Genera una API Key B2B.", "reward": 1000},
        "CARD_SHARK": {"name": "Tiburón de Cartas", "desc": "Gana 10 partidas de Blackjack.", "reward": 3000}
    }

    @classmethod
    def init_filesystem(cls):
        for d in [cls.VAULT_DIR, cls.BUFFER_DIR, cls.LOGS_DIR, cls.BACKUP_DIR, cls.QR_DIR]:
            os.makedirs(d, exist_ok=True)

EmpireConfig.init_filesystem()

# =================================================================
# [2] SISTEMA DE AUDITORÍA Y REGISTROS PROFUNDOS
# =================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "enterprise_audit_v400.log"), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ISHAK_LEVIATHAN")
logger.info(f"Arquitectura V400 iniciada. Sistemas de Respaldo Activados. Director: Ishak (18). Sede: España.")

# =================================================================
# [3] NÚCLEO DE BASE DE DATOS NOSQL CON SHADOW BACKUP (ASYNC I/O)
# =================================================================
class EmpireDatabase:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.data = self._get_default_structure()
        self.sync_load() # Carga inicial síncrona está bien en el arranque

    def _get_default_structure(self):
        return {
            "users": {}, "coupons": {}, "blacklist": [],
            "factions": {}, "transactions": [], "tickets": {},
            "b2b_api_keys": {}, # {api_key: uid}
            "market_stats": {"crypto_value": 150.0, "trend": "up", "history": []},
            "stats": {
                "total_downloads": 0, "total_users": 0, "bytes_processed": 0,
                "boot_time": str(datetime.datetime.now()), "commands_executed": 0,
                "stars_revenue": 0, "fraud_attempts_blocked": 0,
                "casino_spins": 0
            },
            "system": {
                "maint_mode": False,
                "global_welcome": "👑 **BIENVENIDO A ISHAK ENTERPRISE V400 (LEVIATHAN)**\nInfraestructura blindada. No hay fallos. No hay límites."
            }
        }

    def sync_load(self):
        """Carga la DB principal. Si falla, intenta restaurar desde el Shadow Backup."""
        loaded = False
        if os.path.exists(EmpireConfig.DATABASE_PATH):
            try:
                with open(EmpireConfig.DATABASE_PATH, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    self._merge_dicts(self.data, saved_data)
                    loaded = True
            except Exception as e:
                logger.error(f"⚠️ CORRUPCIÓN EN DB PRINCIPAL: {e}")
        
        # Recuperación de Desastres Automática
        if not loaded and os.path.exists(EmpireConfig.SHADOW_DB_PATH):
            logger.warning("🔄 INICIANDO RESTAURACIÓN DESDE SHADOW DB...")
            try:
                with open(EmpireConfig.SHADOW_DB_PATH, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    self._merge_dicts(self.data, saved_data)
                    logger.info("✅ RESTAURACIÓN SHADOW EXITOSA.")
            except Exception as e:
                logger.critical(f"❌ FALLO TOTAL DE DATOS: {e}")

    def _merge_dicts(self, default_dict, saved_dict):
        for k, v in saved_dict.items():
            if isinstance(v, dict) and k in default_dict and isinstance(default_dict[k], dict):
                self._merge_dicts(default_dict[k], v)
            else:
                default_dict[k] = v

    def _sync_save_logic(self, data_copy):
        """Lógica síncrona que será empujada a un hilo asíncrono para no bloquear."""
        temp_path = f"{EmpireConfig.DATABASE_PATH}.tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data_copy, f, indent=4, ensure_ascii=False)
        os.replace(temp_path, EmpireConfig.DATABASE_PATH)
        
        shadow_temp = f"{EmpireConfig.SHADOW_DB_PATH}.tmp"
        with open(shadow_temp, 'w', encoding='utf-8') as f:
            json.dump(data_copy, f, indent=4, ensure_ascii=False)
        os.replace(shadow_temp, EmpireConfig.SHADOW_DB_PATH)

    async def save(self):
        async with self._lock:
            try:
                # Copia superficial segura para que el thread no choque con el main loop
                data_copy = dict(self.data)
                await asyncio.to_thread(self._sync_save_logic, data_copy)
            except Exception as e:
                logger.error(f"Fallo crítico en persistencia redundante asíncrona: {e}")

    async def backup_job(self):
        while True:
            await asyncio.sleep(60 * 60 * 2) # Cada 2 horas
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(EmpireConfig.BACKUP_DIR, f"db_backup_{timestamp}.json")
                def _copy_backup():
                    shutil.copy2(EmpireConfig.DATABASE_PATH, backup_path)
                await asyncio.to_thread(_copy_backup)
                logger.info(f"💾 Respaldo profundo generado: {backup_path}")
            except Exception as e:
                logger.error(f"Error backup asíncrono: {e}")

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
                    "inventory": {"XP_BOOST_X2": 0, "BYPASS_QUEUE": 0, "CLAN_TICKET": 0, "RENAME_CARD": 0},
                    "active_buffs": {"xp_multiplier": 1.0, "buff_expiry": None},
                    "settings": {"watermark": None, "auto_transcribe": False, "ghost_mode": False, "send_as_doc": False},
                    "faction": None, "joined": str(datetime.date.today()),
                    "is_banned": False, "captcha_solved": False, "fraud_warnings": 0,
                    "stats": {"casino_played": 0, "bounties_done": 0, "stars_spent": 0, "blackjack_wins": 0},
                    "last_daily": None, "api_key": None,
                    "bounties": self._generate_daily_bounties()
                }
                self.data["stats"]["total_users"] += 1
        
        if is_new: await self.save()
        u = self.data["users"][uid]
        
        today = str(datetime.date.today())
        if u["daily_downloads"][1] != today:
            u["daily_downloads"] = [0, today]
            u["bounties"] = self._generate_daily_bounties() # Reset de misiones diarias
            await self.save()
            
        if u.get("plan_expiry") and datetime.datetime.now() > datetime.datetime.fromisoformat(u["plan_expiry"]):
            u["plan"] = "FREE"
            u["plan_expiry"] = None
            await self.save()
            
        if u["active_buffs"].get("buff_expiry") and datetime.datetime.now() > datetime.datetime.fromisoformat(u["active_buffs"]["buff_expiry"]):
            u["active_buffs"] = {"xp_multiplier": 1.0, "buff_expiry": None}
            await self.save()
            
        return u

    def _generate_daily_bounties(self):
        return [
            {"id": "dl_3", "desc": "Extrae 3 archivos de la red", "target": 3, "progress": 0, "reward": 500, "done": False},
            {"id": "casino_5", "desc": "Juega 5 veces al Casino Imperial", "target": 5, "progress": 0, "reward": 800, "done": False},
        ]

    async def add_xp(self, uid: str, amount: int):
        u = self.data["users"][uid]
        multi = u["active_buffs"]["xp_multiplier"]
        
        # Bono de Facción: Si la facción es nivel alto, da más XP
        fac_name = u.get("faction")
        if fac_name and fac_name in self.data["factions"]:
            fac_level = self.data["factions"][fac_name].get("level", 1)
            multi += (fac_level * 0.05) # 5% extra por nivel de facción
            
        final_xp = int(amount * multi)
        u["xp"] += final_xp
        xp_needed = u["level"] * 100
        leveled_up = False
        while u["xp"] >= xp_needed:
            u["xp"] -= xp_needed
            u["level"] += 1
            u["points"] += u["level"] * 100
            xp_needed = u["level"] * 100
            leveled_up = True
        await self.save()
        return leveled_up, u["level"]

    async def log_tx(self, uid, amount, desc):
        self.data["transactions"].append({
            "uid": uid, "amount": amount, "desc": desc, "date": str(datetime.datetime.now())
        })
        if len(self.data["transactions"]) > 5000: self.data["transactions"].pop(0)
        await self.save()

    async def update_bounty(self, uid, bounty_id, amount=1):
        u = self.data["users"].get(uid)
        if not u: return None
        for b in u.get("bounties", []):
            if b["id"] == bounty_id and not b["done"]:
                b["progress"] += amount
                if b["progress"] >= b["target"]:
                    b["done"] = True
                    u["points"] += b["reward"]
                    u["stats"]["bounties_done"] += 1
                    await self.save()
                    return b
        return None

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
# [4.5] SISTEMA DE LIMPIEZA AUTOMÁTICA (BUFFER CLEANER)
# =================================================================
async def buffer_cleanup_task():
    """Ejecuta una purga del buffer asíncrona y previene colapsos de almacenamiento"""
    while True:
        await asyncio.sleep(1800) # Cada 30 minutos
        try:
            disk_percent = psutil.disk_usage('/').percent
            force_clean = disk_percent > 90.0
            now = time.time()
            
            def _clean():
                purged_count = 0
                for filename in os.listdir(EmpireConfig.BUFFER_DIR):
                    filepath = os.path.join(EmpireConfig.BUFFER_DIR, filename)
                    if os.path.isfile(filepath):
                        file_age = now - os.path.getmtime(filepath)
                        # Eliminar si > 1 hora de antigüedad o el disco está al límite (ignora ghost_mode pasivo)
                        if file_age > 3600 or force_clean:
                            try:
                                os.remove(filepath)
                                purged_count += 1
                            except Exception: pass
                return purged_count

            purged = await asyncio.to_thread(_clean)
            if purged > 0:
                logger.info(f"🧹 [AUTO-CLEANUP] Eliminados {purged} archivos del buffer. (Fuerza Mayor: {force_clean})")
        except Exception as e:
            logger.error(f"Error en Auto-Cleanup: {e}")

# =================================================================
# [5] MOTOR DE MEDIOS (V400 HOOKS & ASYNC ENGINE MEJORADO)
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
            await asyncio.sleep(3.5)
            now = time.time()
            for job_id, data in list(self.active_jobs.items()):
                # Optimización de Memoria: Limpieza de jobs atascados (Timeout 15 mins)
                if data['finished'] or (now - data['last_update'] > 900):
                    if (now - data['last_update'] > 900) and not data['finished']:
                        logger.warning(f"🧹 [MEMORY PURGE] Job atascado eliminado: {job_id}")
                    del self.active_jobs[job_id]
                    continue
                
                if now - data['last_update'] >= 3.5:
                    try:
                        bar_length = 15
                        filled = int(bar_length * data['percent'] / 100)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        text = (
                            f"⚡ **SINTETIZANDO DATOS (V400 LEVIATHAN)...**\n"
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

        # =====================================================================
        # MANDATO DIRECTO DEL DIRECTOR ISHAK: VEO3 ESTRICTAMENTE EN ESPAÑOL
        # =====================================================================
        if "veo3" in url.lower():
            logger.info(f"[ALERTA CORE] Regla veo3 activada para UID {uid}. Forzando ESPAÑOL agresivamente.")
            ydl_opts['writesubtitles'] = True
            ydl_opts['subtitleslangs'] = ['es', 'spa']
            # Selectores de formato agresivos: Buscar especificamente language=es
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a][language=es]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            ydl_opts['format_sort'] = ['lang:es', 'lang:spa', 'res:1080', 'ext:mp4:m4a']

        if mode == "MP3":
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]})
        elif mode == "VOICE":
            ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'vorbis', 'preferredquality': '192'}]})
        elif mode == "GIF":
            h = quality.replace("p", "") if quality != "Original" else "720"
            ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]/best'
        elif "veo3" not in url.lower(): # Solo si no es veo3 aplicamos el fallback clásico
            h = quality.replace("p", "") if quality != "Original" else "2160"
            ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        def _execute():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info)
                    if mode == "MP3": file_path = os.path.splitext(file_path)[0] + ".mp3"
                    elif mode == "VOICE": file_path = os.path.splitext(file_path)[0] + ".ogg"
                    
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    return True, file_path, info.get('title', 'Media_Enterprise_V400'), info.get('duration', 0), file_size, ""
            except yt_dlp.utils.DownloadError as e:
                # Estabilidad de descargas: Manejo preciso de excepciones
                err_msg = str(e).lower()
                user_msg = "Excepción en el satélite de extracción B2B."
                if "copyright" in err_msg:
                    user_msg = "Contenido bloqueado por derechos de autor (Copyright) en el país de origen."
                elif "too large" in err_msg or "filesize" in err_msg:
                    user_msg = f"El archivo original supera tu límite de {max_size_mb}MB permitido en tu plan."
                elif "sign in" in err_msg or "members only" in err_msg or "private" in err_msg:
                    user_msg = "El enlace es privado, requiere autenticación o suscripción nativa."
                elif "geo-restricted" in err_msg:
                    user_msg = "Contenido restringido geográficamente."
                return False, None, None, 0, 0, user_msg
            except Exception as e:
                return False, None, None, 0, 0, f"Error general de sistema: {e}"

        return await asyncio.to_thread(_execute)

# =================================================================
# [6] INTERFAZ DE USUARIO (GUI ENTERPRISE V400)
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
            [KeyboardButton("🎁 TRIBUTO"), KeyboardButton("🎧 SOPORTE")],
            [KeyboardButton("🎮 MISIONES Y LOGROS")]
        ]
        
        if is_god:
            btns.append([KeyboardButton("🏢 ÁREA B2B")])
            
        if is_admin:
            btns.append([KeyboardButton("👑 PANEL OVERLORD 👑"), KeyboardButton("🌐 DATOS MATRIZ")])
            
        return ReplyKeyboardMarkup(btns, resize_keyboard=True)

    @staticmethod
    def overlord_panel(page=0):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 LISTA ESCLAVOS", callback_data=f"adm_list_{page}"), 
             InlineKeyboardButton("📢 TRANSMISIÓN", callback_data="adm_bc")],
            [InlineKeyboardButton("🚫 BANEAR", callback_data="adm_ban"), 
             InlineKeyboardButton("🔓 DESBANEAR", callback_data="adm_unban")],
            [InlineKeyboardButton("💰 DAR FONDOS", callback_data="adm_pts"), 
             InlineKeyboardButton("🎫 CREAR CUPÓN", callback_data="adm_cp")],
            [InlineKeyboardButton("🎭 EDITAR RANGO", callback_data="adm_edit_plan"), 
             InlineKeyboardButton("📂 TICKETS", callback_data="adm_tickets")],
            [InlineKeyboardButton("⚠️ MANTENIMIENTO", callback_data="adm_maint"), 
             InlineKeyboardButton("💾 BACKUP DB", callback_data="adm_backup")],
            [InlineKeyboardButton("❌ CERRAR TERMINAL", callback_data="u_close")]
        ])

    @staticmethod
    def factions_panel(has_faction):
        if has_faction:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Info de Facción", callback_data="fac_info"),
                 InlineKeyboardButton("💰 Donar a la Bóveda", callback_data="fac_donate")],
                [InlineKeyboardButton("⭐ Subir Nivel Clan (10k pts)", callback_data="fac_upgrade")],
                [InlineKeyboardButton("🚪 Abandonar", callback_data="fac_leave")],
                [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
            ])
        else:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("🛡️ Crear Facción (Req. Ticket)", callback_data="fac_create")],
                [InlineKeyboardButton("🤝 Unirse a Facción", callback_data="fac_join")],
                [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
            ])

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
            [InlineKeyboardButton("🃏 Blackjack (500 pts)", callback_data="casino_bj")],
            [InlineKeyboardButton("📈 Cripto Crash (500 pts)", callback_data="casino_crash")],
            [InlineKeyboardButton("❌ SALIR", callback_data="u_close")]
        ])
        
    @staticmethod
    def blackjack_panel(bet):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🃏 Pedir Carta", callback_data=f"bj_hit_{bet}"),
             InlineKeyboardButton("🛑 Plantarse", callback_data=f"bj_stand_{bet}")],
        ])

    @staticmethod
    def plan_selector_admin():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🆓 FREE", callback_data="setplan_FREE"),
             InlineKeyboardButton("💎 PRO", callback_data="setplan_PRO")],
            [InlineKeyboardButton("🔥 ULTRA", callback_data="setplan_ULTRA"),
             InlineKeyboardButton("👁️ GOD", callback_data="setplan_GOD")],
            [InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")]
        ])

    @staticmethod
    def ticket_panel(ticket_id):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔒 CERRAR TICKET", callback_data=f"tc_close_{ticket_id}")]
        ])

# =================================================================
# [7] MANEJADORES DE TELEGRAM STARS Y LÓGICA DE JUEGOS
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

# Helpers para Blackjack
def draw_card():
    cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return random.choice(cards)

def calculate_hand(hand):
    val = 0
    aces = 0
    for card in hand:
        if card in ['J', 'Q', 'K']: val += 10
        elif card == 'A': aces += 1; val += 11
        else: val += int(card)
    while val > 21 and aces:
        val -= 10; aces -= 1
    return val

# =================================================================
# [8] CONTROLADORES DE COMANDOS Y MENSAJES (NÚCLEO V400)
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
        await update.message.reply_text(f"🛡️ **VERIFICACIÓN ANTI-DDOS (V400).**\nResuelve:\n`{question}`\nResponde solo con el número.")
        context.user_data["state"] = "WAIT_CAPTCHA"
        return

    welcome_msg = db.data["system"]["global_welcome"]
    if user.id == EmpireConfig.ADMIN_ID:
        welcome_msg = "👁️ **SALVE, DIRECTOR ISHAK.**\nArquitectura V400 operativa. Redundancia asíncrona y Módulos de Comando en línea."

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

    MAIN_COMMANDS = [
        "📥 EXTRACCIÓN", "⭐️ TIENDA OFICIAL (STARS)", "💎 MERCADO NEGRO", 
        "⚙️ AJUSTES PRO", "🏢 ÁREA B2B", "🎰 CASINO IMPERIAL", "🛠️ CAJA DE HERRAMIENTAS", 
        "👤 PERFIL", "🎁 TRIBUTO", "🎮 MISIONES Y LOGROS", "🎧 SOPORTE", 
        "👑 PANEL OVERLORD 👑", "🌐 DATOS MATRIZ", "🛡️ FACCIONES"
    ]
    
    if text in MAIN_COMMANDS:
        context.user_data["state"] = None
        
    state = context.user_data.get("state")
    
    if state == "WAIT_CAPTCHA":
        if sec_core.verify_captcha(user.id, text):
            db.data["users"][uid_str]["captcha_solved"] = True
            await db.save()
            context.user_data["state"] = None
            await update.message.reply_text("✅ Acceso autorizado.", reply_markup=EmpireUI.main_keyboard(u_data))
        else:
            await update.message.reply_text("❌ Error en verificación.")
        return

    # AUTO-DETECCIÓN DE ENLACES
    if not state and re.match(r'^https?://', text):
        context.user_data["active_url"] = text
        await update.message.reply_text("🛠 **Enlace detectado automáticamente.** Selecciona formato:", reply_markup=EmpireUI.format_selector())
        return

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
        await update.message.reply_text("🎰 **BIENVENIDO AL CASINO V400**\nJuegos actualizados. Selecciona tu mesa:", reply_markup=EmpireUI.casino_panel())

    elif text == "🛠️ CAJA DE HERRAMIENTAS":
        await update.message.reply_text("🛠️ **UTILERÍA CYBERPUNK V400:**", reply_markup=EmpireUI.utils_panel())

    elif text == "👤 PERFIL":
        plan = EmpireConfig.PLANS[u_data["plan"]]
        fac = u_data.get("faction") or "Ninguna"
        msg = (
            f"👤 **PERFIL CORPORATIVO V400**\n"
            f"🆔 `{user.id}` | Alias: `{u_data['name']}`\n"
            f"🎖️ Nivel: `{u_data['level']}` | Rango: **{plan['name']}**\n"
            f"🛡️ Facción: `{fac}`\n"
            f"💰 Capital: `{u_data['points']} pts` | ⭐️ Stars: `{u_data['stats'].get('stars_spent', 0)}`\n"
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

    elif text == "🛡️ FACCIONES":
        await update.message.reply_text("🛡️ **SISTEMA DE FACCIONES (GREMIOS)**\nÚnete a un clan o forja tu propio destino.", reply_markup=EmpireUI.factions_panel(bool(u_data.get("faction"))))

    elif text == "🎮 MISIONES Y LOGROS":
        bounties = u_data.get("bounties", [])
        msg = "📜 **MISIONES DIARIAS:**\n"
        for b in bounties:
            status = "✅ Completado" if b["done"] else f"⏳ {b['progress']}/{b['target']}"
            msg += f"• {b['desc']} ({status}) -> +{b['reward']} pts\n"
            
        msg += "\n🎮 **SALÓN DE LA FAMA IMPERIAL:**\n"
        for k, v in EmpireConfig.ACHIEVEMENTS.items():
            status = "✅" if k in u_data["achievements"] else "🔒"
            msg += f"{status} **{v['name']}**: {v['desc']}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🎧 SOPORTE":
        await update.message.reply_text("📝 **Describe tu problema en 1 solo mensaje para el Alto Mando:**")
        context.user_data["state"] = "WAIT_TICKET"

    # --- COMANDOS ADMINISTRADOR ---
    elif text == "👑 PANEL OVERLORD 👑" and user.id == EmpireConfig.ADMIN_ID:
        await update.message.reply_text("🛠 **CENTRO DE COMANDO V400**", reply_markup=EmpireUI.overlord_panel())

    elif text == "🌐 DATOS MATRIZ" and user.id == EmpireConfig.ADMIN_ID:
        s = db.data["stats"]
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        msg = (
            f"🌐 **TELEMETRÍA EN TIEMPO REAL V400**\n"
            f"👥 Usuarios: `{s['total_users']}`\n"
            f"📥 Extracciones: `{s['total_downloads']}`\n"
            f"🎰 Giros Casino: `{s['casino_spins']}`\n"
            f"⭐️ Revenue Stars: `{s.get('stars_revenue', 0)}`\n"
            f"🖥️ CPU: `{psutil.cpu_percent()}%` | RAM: `{mem.percent}%`\n"
            f"💾 Disco: `{disk.percent}%` libre\n"
            f"🚀 OS: `{platform.system()} {platform.release()}`\n"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

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
        if thumb: await context.bot.send_photo(uid_str, thumb, caption="🖼️ Aquí tienes la miniatura.")
        else: await update.message.reply_text("❌ No se pudo extraer miniatura de ese enlace.")
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
        await update.message.reply_text(f"🗣️ **Voz Sintética Generada:**\n*(Simulación Text-to-Speech V400)*\n`{tts}`", parse_mode="Markdown")
        context.user_data["state"] = None

    elif state == "WAIT_TICKET":
        tid = f"TK-{random.randint(1000, 9999)}"
        db.data["tickets"][tid] = {"uid": uid_str, "text": text, "status": "OPEN"}
        await db.save()
        await update.message.reply_text(f"✅ Ticket `{tid}` enviado al Alto Mando.")
        try: await context.bot.send_message(EmpireConfig.ADMIN_ID, f"🚨 TICKET {tid} de {user.first_name}:\n{text}", reply_markup=EmpireUI.ticket_panel(tid))
        except: pass
        context.user_data["state"] = None

    # ESTADOS FACCIONES
    elif state == "WAIT_FAC_CREATE":
        fac_name = text.strip()
        if len(fac_name) < 3 or len(fac_name) > 20: return await update.message.reply_text("❌ Nombre debe tener entre 3 y 20 caracteres.")
        if fac_name in db.data["factions"]: return await update.message.reply_text("❌ Nombre en uso.")
        if u_data["inventory"]["CLAN_TICKET"] > 0:
            u_data["inventory"]["CLAN_TICKET"] -= 1
            db.data["factions"][fac_name] = {"owner": uid_str, "members": [uid_str], "vault": 0, "level": 1}
            u_data["faction"] = fac_name
            if "GUILD_MASTER" not in u_data["achievements"]:
                u_data["achievements"].append("GUILD_MASTER"); u_data["points"] += 3000
                await update.message.reply_text("🏆 ¡LOGRO: Maestro de Gremio! +3000 pts")
            await db.save()
            await update.message.reply_text(f"✅ Has fundado la facción **{fac_name}**.")
        else: await update.message.reply_text("❌ No tienes un Ticket de Fundación (Cómpralo en la tienda).")
        context.user_data["state"] = None

    elif state == "WAIT_FAC_JOIN":
        fac_name = text.strip()
        if fac_name in db.data["factions"]:
            db.data["factions"][fac_name]["members"].append(uid_str)
            u_data["faction"] = fac_name
            await db.save()
            await update.message.reply_text(f"✅ Te has unido a **{fac_name}**.")
        else: await update.message.reply_text("❌ Facción no encontrada.")
        context.user_data["state"] = None

    elif state == "WAIT_FAC_DONATE":
        try:
            amt = int(text)
            if amt > 0 and amt <= u_data["points"]:
                u_data["points"] -= amt
                fac_name = u_data["faction"]
                db.data["factions"][fac_name]["vault"] += amt
                await db.save()
                await update.message.reply_text(f"✅ Donaste {amt} pts a {fac_name}.")
            else: await update.message.reply_text("❌ Saldo insuficiente.")
        except: await update.message.reply_text("❌ Ingresa un número.")
        context.user_data["state"] = None

    # ESTADOS ADMIN
    elif state == "WAIT_BC" and user.id == EmpireConfig.ADMIN_ID:
        count = 0
        m = await update.message.reply_text("📡 Propagando...")
        for sid in list(db.data["users"].keys()):
            try:
                await context.bot.send_message(sid, f"📢 **MENSAJE DEL DIRECTOR ISHAK:**\n\n{text}")
                count += 1; await asyncio.sleep(0.05)
            except: pass
        await m.edit_text(f"✅ Entregados a {count} súbditos.")
        context.user_data["state"] = None
        
    elif state == "WAIT_BAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = True
            await update.message.reply_text("🚫 Usuario exiliado.")
            await db.save()
        context.user_data["state"] = None
        
    elif state == "WAIT_UNBAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = False
            await update.message.reply_text("🔓 Usuario rehabilitado.")
            await db.save()
        context.user_data["state"] = None

    elif state == "WAIT_PTS_ID" and user.id == EmpireConfig.ADMIN_ID:
        context.user_data["target_id"] = text.strip()
        await update.message.reply_text("💰 Monto:")
        context.user_data["state"] = "WAIT_PTS_VAL"
        
    elif state == "WAIT_PTS_VAL" and user.id == EmpireConfig.ADMIN_ID:
        try:
            val = int(text)
            tid = context.user_data["target_id"]
            if tid in db.data["users"]:
                db.data["users"][tid]["points"] += val
                await db.save()
                await update.message.reply_text(f"✅ Puntos inyectados a {tid}.")
        except: pass
        context.user_data["state"] = None

    elif state == "WAIT_CP_CODE" and user.id == EmpireConfig.ADMIN_ID:
        context.user_data["cp_code"] = text.upper().strip()
        await update.message.reply_text("🎫 Rango (FREE, PRO, ULTRA, GOD):")
        context.user_data["state"] = "WAIT_CP_PLAN"

    elif state == "WAIT_CP_PLAN" and user.id == EmpireConfig.ADMIN_ID:
        plan = text.upper().strip()
        if plan in EmpireConfig.PLANS:
            db.data["coupons"][context.user_data["cp_code"]] = plan
            await db.save()
            await update.message.reply_text(f"✅ Cupón creado.")
        context.user_data["state"] = None

    elif state == "WAIT_PLAN_EDIT_ID" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            context.user_data["target_user_id"] = text
            await update.message.reply_text(f"🎭 Redefiniendo a `{text}`:", reply_markup=EmpireUI.plan_selector_admin())
        else: await update.message.reply_text("❌ No encontrado.")
        context.user_data["state"] = None

# =================================================================
# [9] MOTOR DE CALLBACKS
# =================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    uid_str = str(uid)
    data = q.data
    await q.answer()

    u_data = await db.get_user(q.from_user)

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

    elif data == "b2b_gen_key":
        if u_data['plan'] != 'GOD':
            return await q.message.reply_text("❌ Acceso Denegado. Función de seguridad exclusiva para GOD.")
        
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

    # FACCIONES
    elif data.startswith("fac_"):
        action = data.split("_")[1]
        if action == "create":
            await q.message.reply_text("🛡️ Escribe el nombre de tu nueva Facción (3-20 letras):")
            context.user_data["state"] = "WAIT_FAC_CREATE"
        elif action == "join":
            await q.message.reply_text("🤝 Escribe el nombre exacto de la Facción:")
            context.user_data["state"] = "WAIT_FAC_JOIN"
        elif action == "info":
            f_name = u_data["faction"]
            fac = db.data["factions"][f_name]
            msg = f"🛡️ **FACCIÓN: {f_name}**\n👑 Dueño: `{fac['owner']}`\n👥 Miembros: `{len(fac['members'])}`\n💰 Bóveda: `{fac['vault']} pts`\n📈 Nivel: `{fac['level']}`"
            await q.message.reply_text(msg)
        elif action == "donate":
            await q.message.reply_text("💰 Escribe la cantidad de puntos a donar a la bóveda:")
            context.user_data["state"] = "WAIT_FAC_DONATE"
        elif action == "upgrade":
            f_name = u_data["faction"]
            fac = db.data["factions"][f_name]
            if fac['vault'] >= 10000:
                fac['vault'] -= 10000
                fac['level'] += 1
                await db.save()
                await q.message.reply_text(f"⭐ ¡La facción {f_name} ha subido al Nivel {fac['level']}!")
            else: await q.message.reply_text("❌ La bóveda no tiene 10,000 pts.")
        elif action == "leave":
            f_name = u_data["faction"]
            db.data["factions"][f_name]["members"].remove(uid_str)
            u_data["faction"] = None
            if uid_str == db.data["factions"][f_name]["owner"]:
                db.data["factions"][f_name]["owner"] = db.data["factions"][f_name]["members"][0] if db.data["factions"][f_name]["members"] else "Abandonada"
            await db.save()
            await q.edit_message_text("🚪 Has abandonado la facción.")

    # CASINO
    elif data.startswith("casino_"):
        db.data["stats"]["casino_spins"] = db.data["stats"].get("casino_spins", 0) + 1
        game = data.split("_")[1]
        
        await db.update_bounty(uid_str, "casino_5", 1)
        
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
            
        elif game == "bj":
            bet = 500
            if u_data["points"] < bet: return await q.message.reply_text("❌ Puntos insuficientes (500 req).")
            u_data["points"] -= bet
            p_hand = [draw_card(), draw_card()]
            d_hand = [draw_card()]
            context.user_data["bj_hand"] = p_hand
            context.user_data["bj_dealer"] = d_hand
            msg = f"🃏 **BLACKJACK (Apuesta 500)**\n\nTu Mano: {p_hand} (Valor: {calculate_hand(p_hand)})\nCrupier: {d_hand} [?]\n\n¿Qué deseas hacer?"
            await db.save()
            await q.edit_message_text(msg, reply_markup=EmpireUI.blackjack_panel(bet))
            
    elif data.startswith("bj_"):
        parts = data.split("_")
        action = parts[1]
        bet = int(parts[2])
        p_hand = context.user_data.get("bj_hand", [])
        d_hand = context.user_data.get("bj_dealer", [])
        
        if action == "hit":
            p_hand.append(draw_card())
            val = calculate_hand(p_hand)
            if val > 21:
                msg = f"💥 **TE PASASTE!**\n\nTu Mano: {p_hand} (Valor: {val})\n💀 Pierdes {bet} pts."
                await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())
            else:
                msg = f"🃏 **BLACKJACK**\n\nTu Mano: {p_hand} (Valor: {val})\nCrupier: {d_hand} [?]\n\n¿Qué deseas hacer?"
                await q.edit_message_text(msg, reply_markup=EmpireUI.blackjack_panel(bet))
                
        elif action == "stand":
            p_val = calculate_hand(p_hand)
            while calculate_hand(d_hand) < 17: d_hand.append(draw_card())
            d_val = calculate_hand(d_hand)
            
            msg = f"🃏 **BLACKJACK - RESULTADO**\n\nTu Mano: {p_hand} (Valor: {p_val})\nCrupier: {d_hand} (Valor: {d_val})\n\n"
            if d_val > 21 or p_val > d_val:
                win = bet * 2; u_data["points"] += win; u_data["stats"]["blackjack_wins"] += 1
                msg += f"🎉 **¡GANASTE!** +{win} pts."
                if u_data["stats"]["blackjack_wins"] >= 10 and "CARD_SHARK" not in u_data["achievements"]:
                    u_data["achievements"].append("CARD_SHARK"); u_data["points"]+=3000
                    await q.message.reply_text("🏆 ¡LOGRO: Tiburón de Cartas! +3000 pts")
            elif p_val == d_val:
                u_data["points"] += bet; msg += "🤝 **EMPATE.** Recuperas tu apuesta."
            else: msg += "💀 **EL CRUPIER GANA.**"
            
            await db.save()
            await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())

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
            await m.edit_text(f"📡 **Ping Test V400:**\nLatencia (España -> Telegram): `{int((end_time - start_time) * 1000)}ms`")

    # ADMIN RUTAS
    elif data.startswith("adm_") and uid == EmpireConfig.ADMIN_ID:
        if data.startswith("adm_list_"):
            page = int(data.split("_")[2])
            users = list(db.data["users"].items())
            start = page * 10
            end = start + 10
            msg = f"👥 **ESCLAVOS (Pág {page+1}):**\n"
            for sid, d in users[start:end]:
                msg += f"• `{sid}` | {d['name'][:10]} | Lvl:{d['level']} | {d['plan']}\n"
            kb = [[InlineKeyboardButton("⬅️ Ant", callback_data=f"adm_list_{max(0, page-1)}"), InlineKeyboardButton("Sig ➡️", callback_data=f"adm_list_{page+1}")]]
            kb.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
            await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
            
        elif data == "adm_bc":
            await q.message.reply_text("📢 Dicta mensaje:"); context.user_data["state"] = "WAIT_BC"
        elif data == "adm_ban":
            await q.message.reply_text("🚫 ID a banear:"); context.user_data["state"] = "WAIT_BAN"
        elif data == "adm_unban":
            await q.message.reply_text("🔓 ID a desbanear:"); context.user_data["state"] = "WAIT_UNBAN"
        elif data == "adm_pts":
            await q.message.reply_text("💰 ID al que fondear:"); context.user_data["state"] = "WAIT_PTS_ID"
        elif data == "adm_cp":
            await q.message.reply_text("🎫 Escribe la clave del nuevo cupón:"); context.user_data["state"] = "WAIT_CP_CODE"
        elif data == "adm_edit_plan":
            await q.message.reply_text("🎭 ID del usuario para cambiar rango:"); context.user_data["state"] = "WAIT_PLAN_EDIT_ID"
        elif data == "adm_maint":
            db.data["system"]["maint_mode"] = not db.data["system"]["maint_mode"]
            await db.save()
            estado = "ACTIVADO" if db.data["system"]["maint_mode"] else "DESACTIVADO"
            await q.edit_message_text(f"⚠️ Mantenimiento {estado}.", reply_markup=EmpireUI.overlord_panel(0))
        elif data == "adm_backup":
            await db.save()
            def _send_backup():
                 return open(EmpireConfig.DATABASE_PATH, 'rb')
            f_backup = await asyncio.to_thread(_send_backup)
            await context.bot.send_document(uid, f_backup, caption="💾 Core Vault V400")

    elif data.startswith("setplan_") and uid == EmpireConfig.ADMIN_ID:
        plan = data.split("_")[1]
        tid = context.user_data.get("target_user_id")
        if tid in db.data["users"]:
            db.data["users"][tid]["plan"] = plan
            expiry = datetime.datetime.now() + datetime.timedelta(days=365) if plan not in ["FREE", "GOD"] else None
            db.data["users"][tid]["plan_expiry"] = str(expiry) if expiry else None
            await db.save()
            await q.edit_message_text(f"✅ Rango de `{tid}` reescrito a **{plan}**.")
            try: await context.bot.send_message(tid, f"👁️ El Director Ishak ha elevado tu existencia al rango **{plan}**.")
            except: pass
        context.user_data["target_user_id"] = None

    elif data.startswith("tc_close_") and uid == EmpireConfig.ADMIN_ID:
        tid = data.replace("tc_close_", "")
        if tid in db.data["tickets"]:
            db.data["tickets"][tid]["status"] = "CLOSED"
            await db.save()
            user_ticket = db.data["tickets"][tid]["uid"]
            await q.edit_message_reply_markup(reply_markup=None)
            await q.message.reply_text(f"✅ Ticket {tid} clausurado.")
            try: await context.bot.send_message(user_ticket, f"✅ Tu ticket `{tid}` ha sido resuelto por el Alto Mando.")
            except: pass

    # EXTRACCIÓN
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

    msg = await q.edit_message_text(f"⚡ **MOTOR V400 INICIADO...**\n`[{fmt} | {qlty}]`")
    job_id = f"job_{uid_str}_{uuid.uuid4().hex[:6]}"
    progress_tracker.add_job(job_id, msg)
    
    try:
        success, path, title, duration, f_size, err_msg = await MediaEngine.run(url, fmt, qlty, uid_str, max_size, job_id, u_data['settings'])
        
        if job_id in progress_tracker.active_jobs:
            progress_tracker.active_jobs[job_id]['finished'] = True
            
        if not success:
            return await msg.edit_text(f"❌ **ERROR DEL NÚCLEO EXTRACCIÓN:**\n{err_msg}")
        
        size_mb = f_size / (1024 * 1024)
        if size_mb > max_size:
            if os.path.exists(path):
                await asyncio.to_thread(os.remove, path)
            return await msg.edit_text(f"❌ Archivo excede límite de {max_size}MB.")

        await msg.edit_text("📤 **SUBIENDO AL SATÉLITE CORPORATIVO...**", parse_mode="Markdown")
        
        def _get_file_reader():
            return open(path, 'rb')
            
        with await asyncio.to_thread(_get_file_reader) as f:
            wm_text = f"\n©️ Marca de Agua: `{u_data['settings']['watermark']}`" if u_data['settings'].get('watermark') else ""
            veo3_note = "\n🇪🇸 *Regla Directiva: Español (Veo3).* " if "veo3" in url.lower() else ""
            cap = (
                f"✅ **{title[:50]}...**\n"
                f"⏱️ `{str(datetime.timedelta(seconds=duration))}` | 💾 `{size_mb:.1f} MB`{wm_text}{veo3_note}\n"
            )
            
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
        await db.update_bounty(uid_str, "dl_3", 1)
        
        if os.path.exists(path) and not u_data['settings'].get('ghost_mode'):
            await asyncio.to_thread(os.remove, path)
        try: await msg.delete()
        except: pass

    except Exception as e:
        if job_id in progress_tracker.active_jobs: progress_tracker.active_jobs[job_id]['finished'] = True
        logger.error(f"Fallo general asíncrono UID {uid}: {e}")
        await msg.edit_text(f"❌ **ERROR DE SISTEMA:**\nHa ocurrido un fallo irrecuperable en la matriz.")

# =================================================================
# [11] PANEL SAAS WEB (LANDING PAGE 100K€ + B2B API REAL)
# =================================================================
web_app = Flask("Ishak_Enterprise_Web")
CORS_APP(web_app)

LANDING_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ishak Enterprise V400 | B2B Media Solutions</title>
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
    <div class="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
        <div class="absolute w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 top-0 left-0 animate-blob"></div>
        <div class="absolute w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 bottom-0 right-0 animate-blob animation-delay-2000"></div>
        
        <div class="z-10 text-center px-4 max-w-4xl glass-panel p-12 rounded-3xl shadow-2xl">
            <h1 class="text-6xl font-extrabold mb-4 tracking-tight"><span class="gradient-text">ISHAK</span> ENTERPRISE <span class="text-blue-400">V400</span></h1>
            <p class="text-xl text-gray-300 mb-8">La infraestructura de extracción multimedia más avanzada de España. Dirigida por Ishak (18). Valorada en 250.000€.</p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 text-left">
                <div class="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                    <i class="fas fa-rocket text-3xl text-blue-400 mb-3"></i>
                    <h3 class="text-xl font-bold mb-2">API B2B Funcional</h3>
                    <p class="text-sm text-gray-400">Endpoints REST reales para extraer URLs directas de CDNs (CORS Habilitado).</p>
                </div>
                <div class="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                    <i class="fas fa-shield-alt text-3xl text-purple-400 mb-3"></i>
                    <h3 class="text-xl font-bold mb-2">Shadow Backups</h3>
                    <p class="text-sm text-gray-400">Redundancia de datos asíncrona en tiempo real. Resistencia total a la corrupción.</p>
                </div>
                <div class="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                    <i class="fas fa-star text-3xl text-yellow-400 mb-3"></i>
                    <h3 class="text-xl font-bold mb-2">Telegram Stars</h3>
                    <p class="text-sm text-gray-400">Integración de pagos nativos y ecosistema financiero completo.</p>
                </div>
            </div>
            
            <a href="#" class="inline-block bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold py-4 px-10 rounded-full transition-all transform hover:scale-105 shadow-lg shadow-blue-500/30">
                INICIAR SISTEMA AHORA
            </a>
        </div>
    </div>

    <!-- Live Metrics Dashboard -->
    <div class="py-20 bg-slate-900 border-t border-slate-800">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <h2 class="text-3xl font-bold mb-12 glow-text">MÉTRICAS DEL NÚCLEO V400 (LIVE)</h2>
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
                const res = await fetch('/api/v4/metrics');
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

@web_app.route('/api/v4/metrics', methods=['GET'])
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

@web_app.route('/api/v1/extract', methods=['POST'])
def api_real_extract():
    api_key = request.headers.get('X-API-KEY')
    if not api_key or api_key not in db.data.get('b2b_api_keys', {}):
        return jsonify({"error": "No autorizado. Clave de API ausente o inválida."}), 401
    
    data = request.json or {}
    url = data.get('url')
    if not url:
        return jsonify({"error": "Parámetro 'url' es requerido."}), 400
        
    uid = db.data['b2b_api_keys'][api_key]
    
    try:
        opts = {'quiet': True, 'noplaylist': True}
        
        if "veo3" in url.lower():
            opts['format_sort'] = ['lang:es', 'lang:spa', 'res:1080', 'ext:mp4:m4a']
            
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            direct_url = info.get('url')
            if not direct_url and info.get('formats'):
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
# [12] SECUENCIA DE INICIO TITÁN LEVIATHAN
# =================================================================
async def post_init(app: Application):
    # Inicialización de tareas asíncronas vitales
    asyncio.create_task(db.backup_job())
    asyncio.create_task(progress_tracker.update_messages_loop())
    asyncio.create_task(buffer_cleanup_task())

def main():
    print("=" * 80)
    print(f"🚀 INICIANDO ISHAK HYPER-SAAS V{EmpireConfig.VERSION}")
    print("💎 CÓDIGO DE RESPALDO (SHADOW DB) ACTIVO Y PROTEGIDO.")
    print("🛡️ REGLA VEO3 (ESPAÑOL) BLINDADA. ASYNC I/O HABILITADO.")
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
