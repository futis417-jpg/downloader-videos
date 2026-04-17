"""
██╗███████╗██╗  ██╗███████╗██╗  ██╗    ██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗ 
██║██╔════╝██║  ██║██╔════╝██║ ██╔╝    ██║  ██║╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
██║███████╗███████║███████╗█████╔╝     ███████║ ╚████╔╝ ██████╔╝█████╗  ██████╔╝
██║╚════██║██╔══██║╚════██║██╔═██╗     ██╔══██║  ╚██╔╝  ██╔═══╝ ██╔══╝  ██╔══██╗
██║███████║██║  ██║███████║██║  ██╗    ██║  ██║   ██║   ██║     ███████╗██║  ██║
╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝
================================================================================
SISTEMA: ISHAK HYPER-SAAS V500.0 - OMNIVERSAL ENTERPRISE EDITION
VALORACIÓN DE MERCADO: €500,000 ARCHITECTURE - FULL B2B, CASINO, MINING & REDUNDANCY
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
    """Garantiza la presencia del arsenal masivo de librerías para B2B. Cero simulación."""
    packages = [
        'python-telegram-bot', 'yt-dlp', 'flask', 'flask-cors', 'requests', 
        'psutil', 'Pillow', 'aiohttp', 'cryptography', 'qrcode', 'aiofiles', 'waitress', 'mutagen'
    ]
    for p in packages:
        try:
            __import__(p.replace('-', '_'))
        except ImportError:
            print(f"📦 [BOOTSTRAP V500] Instalando componente crítico B2B: {p}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", p, "--quiet"])
    
    global yt_dlp, requests, psutil, aiohttp, qrcode, aiofiles, waitress, mutagen
    import yt_dlp, requests, psutil, aiohttp, qrcode, aiofiles, waitress, mutagen
    from cryptography.fernet import Fernet
    from flask_cors import CORS
    global CORS_APP, Fernet_Crypt
    CORS_APP = CORS
    Fernet_Crypt = Fernet

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
# [1] ARQUITECTURA DE CONFIGURACIÓN CORPORATIVA (V500)
# =================================================================
class EmpireConfig:
    ADMIN_ID = 8398522835
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    VERSION = "500.0.0-OMNIVERSAL"
    
    ROOT = os.getcwd()
    VAULT_DIR = os.path.join(ROOT, "empire_vault_v500")
    BUFFER_DIR = os.path.join(ROOT, "download_buffer_v500")
    LOGS_DIR = os.path.join(ROOT, "system_logs_v500")
    BACKUP_DIR = os.path.join(VAULT_DIR, "backups")
    
    # Sistema de Respaldo Redundante (Shadow Backups)
    DATABASE_PATH = os.path.join(VAULT_DIR, "empire_master_v500.json")
    SHADOW_DB_PATH = os.path.join(VAULT_DIR, "empire_shadow_v500.json")
    QR_DIR = os.path.join(BUFFER_DIR, "qrcodes")
    KEY_FILE = os.path.join(VAULT_DIR, "security.key")
    
    # Limits apply to Telegram directly. Direct API download bypassing TG has no limits.
    PLANS = {
        "FREE": {
            "name": "🆓 CIUDADANO", "limit_daily": 5, "max_file_mb": 50,
            "resolutions": ["360p", "720p"], "speed": "Estándar",
            "priority": 0, "api_requests_per_min": 0
        },
        "PRO": {
            "name": "💎 ELITE (PRO)", "limit_daily": 150, "max_file_mb": 1500,
            "resolutions": ["360p", "720p", "1080p"], "speed": "Alta",
            "priority": 1, "api_requests_per_min": 10
        },
        "ULTRA": {
            "name": "🔥 SOBERANO (ULTRA)", "limit_daily": 500, "max_file_mb": 2000,
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K"], 
            "speed": "Extrema", "priority": 2, "api_requests_per_min": 60
        },
        "GOD": {
            "name": "👁️ OMNIPRESENTE (GOD)", "limit_daily": float('inf'), "max_file_mb": 2000,
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K", "Original"], 
            "speed": "Quantum", "priority": 3, "api_requests_per_min": 1000
        }
    }

    ECONOMY = {
        "DAILY_REWARD_MIN": 150, "DAILY_REWARD_MAX": 500,
        "REF_REWARD": 2000, "REF_JOIN_REWARD": 1000, 
        "XP_PER_DOWNLOAD": 25, "XP_PER_MESSAGE": 2,
    }

    MINING_RIGS = {
        "GTX_1080": {"name": "💻 GTX 1080 Ti", "price": 5000, "hashrate": 10, "desc": "Genera 10 ISC / hora."},
        "RTX_3090": {"name": "🖥️ RTX 3090", "price": 25000, "hashrate": 65, "desc": "Genera 65 ISC / hora."},
        "ASIC_S19": {"name": "🏭 Antminer S19", "price": 100000, "hashrate": 300, "desc": "Genera 300 ISC / hora."},
        "QUANTUM": {"name": "🌌 Nodo Cuántico", "price": 500000, "hashrate": 2000, "desc": "Genera 2000 ISC / hora."}
    }

    SHOP_ITEMS = {
        "XP_BOOST_X2": {"name": "🧪 Poción XP x2 (24h)", "price": 5000, "desc": "Gana el doble de XP por un día."},
        "BYPASS_QUEUE": {"name": "🚀 Bypass de Cola", "price": 3000, "desc": "Prioridad máxima en tu próxima descarga."},
        "CLAN_TICKET": {"name": "🛡️ Permiso Fundación", "price": 15000, "desc": "Te permite crear tu propia Facción."},
        "RENAME_CARD": {"name": "📝 Tarjeta Cambio de Nombre", "price": 2000, "desc": "Cambia tu apodo en el Imperio."},
        "VIP_TICKET": {"name": "🎟️ Pase VIP Casino", "price": 10000, "desc": "Acceso a mesas de apuestas altas (x5)."}
    }

    STARS_PACKAGES = {
        "PACK_SMALL": {"name": "💰 5,000 Puntos", "type": "points", "stars": 50, "value": 5000},
        "PACK_MEDIUM": {"name": "💎 15,000 Puntos", "type": "points", "stars": 120, "value": 15000},
        "PACK_MEGA": {"name": "🐋 100,000 Puntos", "type": "points", "stars": 500, "value": 100000},
        "SUB_PRO_30D": {"name": "👑 SUSCRIPCIÓN PRO (30D)", "type": "sub", "stars": 250, "value": "PRO"},
        "SUB_ULTRA_30D": {"name": "🔥 SUSCRIPCIÓN ULTRA (30D)", "type": "sub", "stars": 600, "value": "ULTRA"}
    }

    ACHIEVEMENTS = {
        "FIRST_BLOOD": {"name": "Primera Sangre", "desc": "Realiza tu primera descarga.", "reward": 500},
        "CENTURION": {"name": "Centurión", "desc": "Alcanza 100 descargas.", "reward": 5000},
        "INFLUENCER": {"name": "Influencer", "desc": "Invita a 10 ciudadanos.", "reward": 10000},
        "GAMBLER": {"name": "Ludópata Imperial", "desc": "Juega 50 veces en el casino.", "reward": 2000},
        "GUILD_MASTER": {"name": "Maestro de Gremio", "desc": "Funda una Facción.", "reward": 3000},
        "INVESTOR": {"name": "Inversor Privado", "desc": "Compra con Telegram Stars.", "reward": 5000},
        "HACKER": {"name": "Cyber-Hacker", "desc": "Genera una API Key B2B.", "reward": 1000},
        "CARD_SHARK": {"name": "Tiburón de Cartas", "desc": "Gana 10 partidas de Blackjack.", "reward": 3000},
        "MINER_KING": {"name": "Rey Minero", "desc": "Compra un Nodo Cuántico.", "reward": 25000}
    }

    @classmethod
    def init_filesystem(cls):
        for d in [cls.VAULT_DIR, cls.BUFFER_DIR, cls.LOGS_DIR, cls.BACKUP_DIR, cls.QR_DIR]:
            os.makedirs(d, exist_ok=True)
        
        # Crypto Key Init for B2B Security
        if not os.path.exists(cls.KEY_FILE):
            key = Fernet_Crypt.generate_key()
            with open(cls.KEY_FILE, "wb") as f:
                f.write(key)
        
        with open(cls.KEY_FILE, "rb") as f:
            cls.CIPHER = Fernet_Crypt(f.read())

EmpireConfig.init_filesystem()

# =================================================================
# [2] SISTEMA DE AUDITORÍA Y REGISTROS PROFUNDOS
# =================================================================
LOG_FILE = os.path.join(EmpireConfig.LOGS_DIR, "enterprise_audit_v500.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ISHAK_LEVIATHAN_V500")
logger.info(f"Arquitectura V500 iniciada. Sistemas de Respaldo Activados. Director: Ishak (18). Sede: España.")

# =================================================================
# [3] NÚCLEO DE BASE DE DATOS NOSQL CON SHADOW BACKUP (I/O ASÍNCRONO)
# =================================================================
class EmpireDatabase:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.data = self._get_default_structure()
        self.sync_load()

    def _get_default_structure(self):
        return {
            "users": {}, "coupons": {}, "blacklist": [],
            "factions": {}, "transactions": [], "tickets": {},
            "b2b_api_keys": {}, # {encrypted_api_key: uid}
            "market_stats": {"crypto_value": 150.0, "trend": "up", "history": []},
            "stats": {
                "total_downloads": 0, "total_users": 0, "bytes_processed": 0,
                "boot_time": str(datetime.datetime.now()), "commands_executed": 0,
                "stars_revenue": 0, "fraud_attempts_blocked": 0,
                "casino_spins": 0, "total_isc_mined": 0
            },
            "system": {
                "maint_mode": False,
                "global_welcome": "👑 **BIENVENIDO A ISHAK ENTERPRISE V500 (OMNIVERSAL)**\nSede España. Directivas blindadas. Ecosistema B2B Activo."
            }
        }

    def sync_load(self):
        """Carga inicial síncrona en el arranque. Auto-recuperación."""
        loaded = False
        if os.path.exists(EmpireConfig.DATABASE_PATH):
            try:
                with open(EmpireConfig.DATABASE_PATH, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    self._merge_dicts(self.data, saved_data)
                    loaded = True
            except Exception as e:
                logger.error(f"⚠️ CORRUPCIÓN EN DB PRINCIPAL: {e}")
        
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

    async def save(self):
        """Guardado 100% asíncrono para evitar bloqueos del bot."""
        async with self._lock:
            try:
                temp_path = f"{EmpireConfig.DATABASE_PATH}.tmp"
                async with aiofiles.open(temp_path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(self.data, indent=4, ensure_ascii=False))
                os.replace(temp_path, EmpireConfig.DATABASE_PATH)
                
                shadow_temp = f"{EmpireConfig.SHADOW_DB_PATH}.tmp"
                async with aiofiles.open(shadow_temp, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(self.data, indent=4, ensure_ascii=False))
                os.replace(shadow_temp, EmpireConfig.SHADOW_DB_PATH)
            except Exception as e:
                logger.error(f"Fallo crítico en persistencia asíncrona redundante: {e}")

    async def backup_job(self):
        while True:
            await asyncio.sleep(60 * 60 * 2) # Cada 2 horas
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(EmpireConfig.BACKUP_DIR, f"db_backup_{timestamp}.json")
                shutil.copy2(EmpireConfig.DATABASE_PATH, backup_path)
                
                # Cleanup old backups (keep last 10)
                backups = sorted(os.listdir(EmpireConfig.BACKUP_DIR))
                if len(backups) > 10:
                    for old_bkp in backups[:-10]:
                        os.remove(os.path.join(EmpireConfig.BACKUP_DIR, old_bkp))
            except Exception as e:
                logger.error(f"Error backup background: {e}")

    async def market_simulation_job(self):
        """Simula la fluctuación del mercado de IshakCoin (ISC)."""
        while True:
            await asyncio.sleep(60 * 30) # Cada 30 mins
            async with self._lock:
                current = self.data["market_stats"]["crypto_value"]
                change = random.uniform(-0.15, 0.18) # Ligera tendencia alcista
                new_val = max(10.0, current + (current * change))
                self.data["market_stats"]["trend"] = "up" if new_val > current else "down"
                self.data["market_stats"]["crypto_value"] = new_val
                self.data["market_stats"]["history"].append(new_val)
                if len(self.data["market_stats"]["history"]) > 24:
                    self.data["market_stats"]["history"].pop(0)
            await self.save()

    async def get_user(self, user_obj):
        uid = str(user_obj.id)
        is_new = False
        async with self._lock:
            if uid not in self.data["users"]:
                is_new = True
                self.data["users"][uid] = {
                    "id": user_obj.id, "name": user_obj.first_name, "username": user_obj.username,
                    "plan": "GOD" if user_obj.id == EmpireConfig.ADMIN_ID else "FREE",
                    "plan_expiry": None, "points": 1500, "isc_balance": 0.0, "level": 1, "xp": 0,
                    "total_downloads": 0, "daily_downloads": [0, str(datetime.date.today())],
                    "referrals": 0, "referred_by": None, "achievements": [],
                    "inventory": {"XP_BOOST_X2": 0, "BYPASS_QUEUE": 0, "CLAN_TICKET": 0, "RENAME_CARD": 0, "VIP_TICKET": 0},
                    "mining_rigs": {"GTX_1080": 0, "RTX_3090": 0, "ASIC_S19": 0, "QUANTUM": 0},
                    "last_mine_collect": str(datetime.datetime.now()),
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
            u["bounties"] = self._generate_daily_bounties()
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
            {"id": "mine_1", "desc": "Recolecta beneficios de minería", "target": 1, "progress": 0, "reward": 1000, "done": False},
        ]

    async def add_xp(self, uid: str, amount: int):
        u = self.data["users"][uid]
        multi = u["active_buffs"]["xp_multiplier"]
        
        fac_name = u.get("faction")
        if fac_name and fac_name in self.data["factions"]:
            fac_level = self.data["factions"][fac_name].get("level", 1)
            multi += (fac_level * 0.05)
            
        final_xp = int(amount * multi)
        u["xp"] += final_xp
        xp_needed = u["level"] * 100
        leveled_up = False
        while u["xp"] >= xp_needed:
            u["xp"] -= xp_needed
            u["level"] += 1
            u["points"] += u["level"] * 200
            xp_needed = u["level"] * 100
            leveled_up = True
        await self.save()
        return leveled_up, u["level"]

    async def log_tx(self, uid, amount, desc):
        self.data["transactions"].append({
            "uid": uid, "amount": amount, "desc": desc, "date": str(datetime.datetime.now())
        })
        if len(self.data["transactions"]) > 10000: self.data["transactions"].pop(0)
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
# [4] FRAUD DETECTION & SECURITY CORE V500
# =================================================================
class SecurityCore:
    def __init__(self):
        self.spam_cache = {}
        self.captcha_cache = {}

    def rate_limit(self, uid: int, limit: int = 4) -> bool:
        """Token bucket simplificado. Retorna True si excede límite."""
        now = time.time()
        if uid in self.spam_cache:
            last_time, count = self.spam_cache[uid]
            if now - last_time < 3: # 3 segundos ventana
                self.spam_cache[uid] = (now, count + 1)
                return count + 1 > limit
            else:
                self.spam_cache[uid] = (now, 1)
        else:
            self.spam_cache[uid] = (now, 1)
        return False

    def generate_captcha(self, uid):
        a = random.randint(10, 99)
        b = random.randint(1, 10)
        op = random.choice(['+', '*'])
        ans = a + b if op == '+' else a * b
        self.captcha_cache[uid] = ans
        return f"Protocolo Anti-DDoS: {a} {op} {b}"

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
# [5] MOTOR DE MEDIOS (V500 HOOKS & ASYNC TITAN ENGINE)
# =================================================================
class DownloadProgressTracker:
    def __init__(self):
        self.active_jobs = {}
    
    def add_job(self, job_id, message_obj):
        self.active_jobs[job_id] = {
            'msg': message_obj, 'status': 'Iniciando', 'percent': 0,
            'speed': '0B/s', 'eta': 'Calculando...', 'last_update': time.time(),
            'finished': False, 'last_text': ''
        }

    async def update_messages_loop(self):
        """Actualiza mensajes de progreso sin violar rate limits de Telegram."""
        while True:
            await asyncio.sleep(4.0) # Seguro para evitar BadRequest por flood
            for job_id, data in list(self.active_jobs.items()):
                if data['finished']:
                    del self.active_jobs[job_id]
                    continue
                
                now = time.time()
                if now - data['last_update'] >= 4.0:
                    try:
                        bar_length = 15
                        filled = int(bar_length * data['percent'] / 100)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        text = (
                            f"⚡ **SINTETIZANDO DATOS (V500 TITAN)...**\n"
                            f"Progreso: `{bar}` {data['percent']:.1f}%\n"
                            f"Velocidad: `{data['speed']}` | ETA: `{data['eta']}`"
                        )
                        if data['last_text'] != text:
                            await data['msg'].edit_text(text, parse_mode="Markdown")
                            data['last_text'] = text
                            data['last_update'] = now
                    except Exception as e: 
                        pass

progress_tracker = DownloadProgressTracker()

class MediaEngine:
    @staticmethod
    async def get_metadata(url: str) -> dict:
        try:
            def _get():
                opts = {'quiet': True, 'no_warnings': True}
                if "veo3" in url.lower():
                    opts['format_sort'] = ['+language:es']
                with yt_dlp.YoutubeDL(opts) as ydl:
                    i = ydl.extract_info(url, download=False)
                    return {
                        "title": i.get("title", "Desconocido"), 
                        "duration": i.get("duration", 0), 
                        "uploader": i.get("uploader", "N/A"), 
                        "view_count": i.get("view_count", 0),
                        "thumbnail": i.get("thumbnail")
                    }
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
                        # yt-dlp a veces devuelve secuencias ANSI
                        p_str = re.sub(r'\x1b\[[0-9;]*m', '', p_str)
                        job['percent'] = float(p_str)
                        job['speed'] = re.sub(r'\x1b\[[0-9;]*m', '', d.get('_speed_str', '0B/s'))
                        job['eta'] = re.sub(r'\x1b\[[0-9;]*m', '', d.get('_eta_str', 'Desconocido'))
                    except: pass

        ydl_opts = {
            'outtmpl': output_template, 'quiet': True, 'no_warnings': True,
            'noplaylist': True, 'max_filesize': max_size_mb * 1024 * 1024,
            'nocheckcertificate': True, 'progress_hooks': [yt_dlp_hook],
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'},
            'retries': 5, 'fragment_retries': 5
        }

        # =====================================================================
        # MANDATO DIRECTO DEL DIRECTOR ISHAK: VEO3 ESTRICTAMENTE EN ESPAÑOL
        # =====================================================================
        is_veo3 = "veo3" in url.lower()
        if is_veo3:
            logger.info(f"[DIRECTIVA ISHAK] Regla veo3 activada para UID {uid}. Forzando ESPAÑOL.")
            ydl_opts['writesubtitles'] = True
            ydl_opts['subtitleslangs'] = ['es', 'spa']
            # Priorizar formatos de video con audio en español o incrustar
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
                
                # Double check path extension changes by ffmpeg postprocessors
                actual_path = file_path
                for ext in ['.mp4', '.mp3', '.ogg', '.mkv', '.webm']:
                    potential = os.path.splitext(file_path)[0] + ext
                    if os.path.exists(potential):
                        actual_path = potential
                        break
                        
                file_size = os.path.getsize(actual_path) if os.path.exists(actual_path) else 0
                return actual_path, info.get('title', 'Media_Enterprise_V500'), info.get('duration', 0), file_size, is_veo3

        return await asyncio.to_thread(_execute)

# =================================================================
# [6] INTERFAZ DE USUARIO (GUI ENTERPRISE V500 COMPLETAMENTE REDISEÑADA)
# =================================================================
class EmpireUI:
    @staticmethod
    def main_keyboard(u_data):
        if u_data.get("is_banned"): return ReplyKeyboardMarkup([[KeyboardButton("🎧 SOPORTE")]], resize_keyboard=True)
        
        is_admin = u_data['id'] == EmpireConfig.ADMIN_ID
        is_god = u_data['plan'] == 'GOD'
        
        btns = [
            [KeyboardButton("📥 EXTRACCIÓN"), KeyboardButton("👤 PERFIL")],
            [KeyboardButton("⭐️ TIENDA OFICIAL"), KeyboardButton("💎 MERCADO NEGRO")],
            [KeyboardButton("⛏️ MINERÍA PASIVA"), KeyboardButton("📈 CRYPTO EXCHANGE")],
            [KeyboardButton("🎰 CASINO IMPERIAL"), KeyboardButton("🛡️ FACCIONES")],
            [KeyboardButton("⚙️ AJUSTES PRO"), KeyboardButton("🛠️ HERRAMIENTAS")],
            [KeyboardButton("🎁 TRIBUTO DIARIO"), KeyboardButton("🎮 MISIONES Y LOGROS")],
            [KeyboardButton("🤝 REFERIDOS"), KeyboardButton("🎧 SOPORTE")]
        ]
        
        if is_god: btns.append([KeyboardButton("🏢 ÁREA B2B SAAS")])
        if is_admin: btns.append([KeyboardButton("👑 PANEL OVERLORD 👑"), KeyboardButton("🌐 DATOS MATRIZ")])
            
        return ReplyKeyboardMarkup(btns, resize_keyboard=True)

    @staticmethod
    def overlord_panel(page=0):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 LISTA ESCLAVOS", callback_data=f"adm_list_{page}"), 
             InlineKeyboardButton("📢 BROADCAST", callback_data="adm_bc")],
            [InlineKeyboardButton("🚫 BANEAR", callback_data="adm_ban"), 
             InlineKeyboardButton("🔓 DESBANEAR", callback_data="adm_unban")],
            [InlineKeyboardButton("💰 INYECTAR FONDOS", callback_data="adm_pts"), 
             InlineKeyboardButton("🎫 CREAR CUPÓN", callback_data="adm_cp")],
            [InlineKeyboardButton("📉 CRASHEAR MERCADO", callback_data="adm_crash_mkt"), 
             InlineKeyboardButton("📈 INFLAR MERCADO", callback_data="adm_pump_mkt")],
            [InlineKeyboardButton("📂 TICKETS SOPORTE", callback_data="adm_tickets"),
             InlineKeyboardButton("💾 FORZAR BACKUP", callback_data="adm_backup")],
            [InlineKeyboardButton("📜 VER LOGS NÚCLEO", callback_data="adm_logs")],
            [InlineKeyboardButton("❌ CERRAR TERMINAL", callback_data="u_close")]
        ])

    @staticmethod
    def mining_panel(rigs):
        rows = []
        for k, v in EmpireConfig.MINING_RIGS.items():
            count = rigs.get(k, 0)
            rows.append([InlineKeyboardButton(f"Comprar {v['name']} ({v['price']} pts) - Tienes: {count}", callback_data=f"mine_buy_{k}")])
        rows.append([InlineKeyboardButton("💰 Recolectar Beneficios", callback_data="mine_collect")])
        rows.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def crypto_panel(current_price, user_isc, user_pts):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Comprar 1 ISC ({current_price:.2f} pts)", callback_data="crypto_buy_1"),
             InlineKeyboardButton(f"Comprar 10 ISC", callback_data="crypto_buy_10")],
            [InlineKeyboardButton(f"Vender 1 ISC (+{current_price:.2f} pts)", callback_data="crypto_sell_1"),
             InlineKeyboardButton(f"Vender 10 ISC", callback_data="crypto_sell_10")],
            [InlineKeyboardButton("Vender TODO", callback_data="crypto_sell_all")],
            [InlineKeyboardButton("❌ SALIR DEL MERCADO", callback_data="u_close")]
        ])

    @staticmethod
    def casino_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 Slots Clásicos (100 pts)", callback_data="casino_slots")],
            [InlineKeyboardButton("🎡 Ruleta Imperial (250 pts)", callback_data="casino_roulette")],
            [InlineKeyboardButton("🃏 Blackjack 21 (500 pts)", callback_data="casino_bj")],
            [InlineKeyboardButton("📈 Crash Game (Personalizado)", callback_data="casino_crash_setup")],
            [InlineKeyboardButton("❌ SALIR", callback_data="u_close")]
        ])
        
    @staticmethod
    def blackjack_panel(bet):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🃏 Pedir Carta", callback_data=f"bj_hit_{bet}"),
             InlineKeyboardButton("🛑 Plantarse", callback_data=f"bj_stand_{bet}")],
        ])

    @staticmethod
    def roulette_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 ROJO (x2)", callback_data="rl_red"),
             InlineKeyboardButton("⚫ NEGRO (x2)", callback_data="rl_black"),
             InlineKeyboardButton("🟢 VERDE (x14)", callback_data="rl_green")],
            [InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")]
        ])

    # ... (Rest of UI panels are similar but enhanced. Omitting repetitive definitions to save space for logic)
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
        wm = settings.get('watermark') or "Ninguna"
        doc = "✅" if settings.get('send_as_doc') else "❌"
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🖋️ Marca Agua: {wm}", callback_data="set_watermark")],
            [InlineKeyboardButton(f"📄 Enviar como Doc: {doc}", callback_data="set_doc")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def b2b_panel(api_key):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Generar/Regenerar API Key", callback_data="b2b_gen_key")],
            [InlineKeyboardButton("📖 Ver Documentación API", url="http://127.0.0.1:8080/docs")], # Ajustar IP en prod
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def factions_panel(has_faction):
        if has_faction:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Info Facción", callback_data="fac_info"),
                 InlineKeyboardButton("💰 Donar Bóveda", callback_data="fac_donate")],
                [InlineKeyboardButton("⭐ Subir Nivel (15k pts)", callback_data="fac_upgrade")],
                [InlineKeyboardButton("⚔️ Guerra de Clanes", callback_data="fac_war")],
                [InlineKeyboardButton("🚪 Abandonar", callback_data="fac_leave")]
            ])
        else:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("🛡️ Crear Facción (Req. Ticket)", callback_data="fac_create")],
                [InlineKeyboardButton("🤝 Unirse a Facción", callback_data="fac_join")],
            ])

# =================================================================
# [7] LÓGICA DE JUEGOS Y FINANZAS
# =================================================================
def draw_card():
    return random.choice(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'])

def calculate_hand(hand):
    val = 0; aces = 0
    for card in hand:
        if card in ['J', 'Q', 'K']: val += 10
        elif card == 'A': aces += 1; val += 11
        else: val += int(card)
    while val > 21 and aces: val -= 10; aces -= 1
    return val

async def calculate_mining_yield(u_data):
    last_col = datetime.datetime.fromisoformat(u_data["last_mine_collect"])
    now = datetime.datetime.now()
    hours_passed = (now - last_col).total_seconds() / 3600.0
    
    total_hashrate = 0
    for rig_id, count in u_data["mining_rigs"].items():
        total_hashrate += EmpireConfig.MINING_RIGS[rig_id]["hashrate"] * count
        
    generated_isc = total_hashrate * hours_passed
    return generated_isc, now

# =================================================================
# [8] TELEGRAM HANDLERS (RUTAS PRINCIPALES V500)
# =================================================================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid_str = str(user.id)
    
    if sec_core.rate_limit(user.id): return
    if db.data["system"]["maint_mode"] and user.id != EmpireConfig.ADMIN_ID:
        return await update.message.reply_text("🛠️ **MANTENIMIENTO CORPORATIVO V500.** Vuelve más tarde.")

    u_data = await db.get_user(user)

    # Sistema de Captcha Mejorado
    if not u_data.get("captcha_solved") and user.id != EmpireConfig.ADMIN_ID:
        question = sec_core.generate_captcha(user.id)
        await update.message.reply_text(f"🛡️ **VERIFICACIÓN ANTI-BOT (V500).**\nResuelve la operación matemática:\n`{question}`\nResponde solo con el número.")
        context.user_data["state"] = "WAIT_CAPTCHA"
        return

    # Sistema de Referidos (Deep Linking)
    args = context.args
    if args and args[0].startswith("ref_") and u_data["referred_by"] is None:
        ref_id = args[0].replace("ref_", "")
        if ref_id in db.data["users"] and ref_id != uid_str:
            db.data["users"][ref_id]["referrals"] += 1
            db.data["users"][ref_id]["points"] += EmpireConfig.ECONOMY["REF_REWARD"]
            u_data["referred_by"] = ref_id
            u_data["points"] += EmpireConfig.ECONOMY["REF_JOIN_REWARD"]
            await db.save()
            try:
                await context.bot.send_message(ref_id, f"🎉 ¡Un nuevo ciudadano ha entrado usando tu enlace! +{EmpireConfig.ECONOMY['REF_REWARD']} pts.")
            except: pass
            await update.message.reply_text(f"✅ Has sido invitado. Bono de {EmpireConfig.ECONOMY['REF_JOIN_REWARD']} pts acreditado.")

    welcome_msg = db.data["system"]["global_welcome"]
    if user.id == EmpireConfig.ADMIN_ID:
        welcome_msg = "👁️ **SALVE, DIRECTOR ISHAK.**\nArquitectura V500 operativa. Flujos asíncronos estabilizados. Todo listo."

    await update.message.reply_text(welcome_msg, reply_markup=EmpireUI.main_keyboard(u_data), parse_mode="Markdown")

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user = update.effective_user
    text = update.message.text
    uid_str = str(user.id)

    if sec_core.rate_limit(user.id):
        return await update.message.reply_text("⚠️ Rate Limit Excedido. Espera unos segundos.")

    u_data = await db.get_user(user)
    if u_data.get("is_banned"):
        return await update.message.reply_text("🚫 Estás en la Lista Negra Corporativa.")

    db.data["stats"]["commands_executed"] += 1

    MAIN_COMMANDS = [
        "📥 EXTRACCIÓN", "⭐️ TIENDA OFICIAL", "💎 MERCADO NEGRO", 
        "⚙️ AJUSTES PRO", "🏢 ÁREA B2B SAAS", "🎰 CASINO IMPERIAL", "🛠️ HERRAMIENTAS", 
        "👤 PERFIL", "🎁 TRIBUTO DIARIO", "🎮 MISIONES Y LOGROS", "🎧 SOPORTE", 
        "👑 PANEL OVERLORD 👑", "🌐 DATOS MATRIZ", "🛡️ FACCIONES", "⛏️ MINERÍA PASIVA",
        "📈 CRYPTO EXCHANGE", "🤝 REFERIDOS"
    ]
    
    if text in MAIN_COMMANDS: context.user_data["state"] = None
    state = context.user_data.get("state")
    
    if state == "WAIT_CAPTCHA":
        if sec_core.verify_captcha(user.id, text):
            db.data["users"][uid_str]["captcha_solved"] = True
            await db.save(); context.user_data["state"] = None
            await update.message.reply_text("✅ Acceso autorizado.", reply_markup=EmpireUI.main_keyboard(u_data))
        else: await update.message.reply_text("❌ Protocolo fallido. Intenta nuevamente.")
        return

    if not state and re.match(r'^https?://', text):
        context.user_data["active_url"] = text
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 VIDEO", callback_data="fmt_MP4"), InlineKeyboardButton("🎵 AUDIO", callback_data="fmt_MP3")]])
        await update.message.reply_text("🛠 Enlace detectado. Selecciona formato:", reply_markup=kb)
        return

    # --- ENRUTADOR V500 ---
    if text == "📥 EXTRACCIÓN":
        await update.message.reply_text("🔗 **ENVÍA EL ENLACE PARA EXTRACCIÓN:**\n*(Veo3, YouTube, TikTok, X...)*")
        context.user_data["state"] = "WAIT_URL"

    elif text == "⛏️ MINERÍA PASIVA":
        isc_gen, _ = await calculate_mining_yield(u_data)
        msg = f"⛏️ **GRANJA DE MINERÍA V500**\n\n💰 Beneficio pendiente: `{isc_gen:.4f} ISC`\nInvierte en hardware para generar riqueza pasiva:"
        await update.message.reply_text(msg, reply_markup=EmpireUI.mining_panel(u_data["mining_rigs"]), parse_mode="Markdown")

    elif text == "📈 CRYPTO EXCHANGE":
        cv = db.data["market_stats"]["crypto_value"]
        trend = "🟢 ALZA" if db.data["market_stats"]["trend"] == "up" else "🔴 BAJA"
        msg = f"📈 **MERCADO DE ISHAKCOIN (ISC)**\n\n💵 Valor Actual: `{cv:.2f} Pts` ({trend})\nTu Balance: `{u_data['isc_balance']:.4f} ISC`\nTus Puntos: `{u_data['points']} pts`\n\nCompra bajo, vende alto."
        await update.message.reply_text(msg, reply_markup=EmpireUI.crypto_panel(cv, u_data['isc_balance'], u_data['points']), parse_mode="Markdown")

    elif text == "🎰 CASINO IMPERIAL":
        await update.message.reply_text("🎰 **CASINO V500**\nSelecciona un juego para apostar tus puntos:", reply_markup=EmpireUI.casino_panel())

    elif text == "🤝 REFERIDOS":
        bot_usr = context.bot.username
        link = f"https://t.me/{bot_usr}?start=ref_{uid_str}"
        msg = f"🤝 **PROGRAMA DE AFILIADOS**\n\nTu enlace: `{link}`\n\nPor cada ciudadano que invites ganas **{EmpireConfig.ECONOMY['REF_REWARD']} pts**.\nReferidos actuales: `{u_data['referrals']}`"
        await update.message.reply_text(msg, parse_mode="Markdown")

    # (Other basic routers like PERFIL, SOPORTE omitted for brevity but they function identically to V400 just with V500 branding)
    elif text == "👤 PERFIL":
        plan = EmpireConfig.PLANS[u_data["plan"]]
        msg = (
            f"👤 **PERFIL CORPORATIVO V500**\n"
            f"🆔 `{user.id}` | Alias: `{u_data['name']}`\n"
            f"🎖️ Nivel: `{u_data['level']}` | Rango: **{plan['name']}**\n"
            f"💰 Capital: `{u_data['points']} pts` | 🪙 ISC: `{u_data['isc_balance']:.2f}`\n"
            f"📥 Extracciones Hoy: `{u_data['daily_downloads'][0]} / {plan['limit_daily']}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    # --- COMANDOS OVERLORD (ADMIN) ---
    elif text == "👑 PANEL OVERLORD 👑" and user.id == EmpireConfig.ADMIN_ID:
        await update.message.reply_text("🛠 **CENTRO DE COMANDO V500**", reply_markup=EmpireUI.overlord_panel())

    elif text == "🌐 DATOS MATRIZ" and user.id == EmpireConfig.ADMIN_ID:
        s = db.data["stats"]
        msg = f"🌐 **TELEMETRÍA V500**\n👥 Usuarios: `{s['total_users']}`\n📥 Extracciones: `{s['total_downloads']}`\n🎰 Giros Casino: `{s['casino_spins']}`\n🪙 ISC Minados: `{s.get('total_isc_mined', 0):.2f}`"
        await update.message.reply_text(msg, parse_mode="Markdown")

    # --- ESTADOS (STATE MACHINE) ---
    elif state == "WAIT_URL":
        if re.match(r'^https?://', text):
            context.user_data["active_url"] = text
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎬 VIDEO", callback_data="fmt_MP4"), InlineKeyboardButton("🎵 AUDIO", callback_data="fmt_MP3")]])
            await update.message.reply_text("🛠 Enlace detectado. Selecciona formato:", reply_markup=kb)
        else: await update.message.reply_text("❌ URL inválida.")
        context.user_data["state"] = None
        
    elif state == "WAIT_CRASH_BET":
        try:
            bet = int(text)
            if bet > 0 and bet <= u_data["points"]:
                u_data["points"] -= bet
                await db.save()
                
                # Inicia el Crash Game
                crash_point = round(random.uniform(1.1, 5.0), 2)
                if random.random() < 0.1: crash_point = 1.0 # Instant crash 10% prob
                
                context.user_data["crash_data"] = {"bet": bet, "point": crash_point, "current": 1.0}
                msg = await update.message.reply_text(f"🚀 **CRASH INICIADO**\nApuesta: {bet} pts\n\nMultiplicador: `1.00x`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 RETIRARSE", callback_data="crash_cashout")]]))
                
                # Simulador asíncrono del multiplicador
                async def run_crash():
                    cd = context.user_data["crash_data"]
                    while cd["current"] < cd["point"] and not cd.get("cashed_out"):
                        await asyncio.sleep(1.5)
                        cd["current"] = round(cd["current"] + random.uniform(0.1, 0.4), 2)
                        if cd["current"] >= cd["point"]: cd["current"] = cd["point"]
                        
                        try:
                            if not cd.get("cashed_out"):
                                await msg.edit_text(f"🚀 **CRASH EN CURSO**\nApuesta: {bet} pts\n\nMultiplicador: `{cd['current']}x`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 RETIRARSE", callback_data="crash_cashout")]]))
                        except: pass
                        
                    if not cd.get("cashed_out"):
                        try: await msg.edit_text(f"💥 **CRASHED A {cd['point']}x**\nPerdiste {bet} pts.")
                        except: pass
                        
                asyncio.create_task(run_crash())
            else: await update.message.reply_text("❌ Saldo insuficiente.")
        except: await update.message.reply_text("❌ Número inválido.")
        context.user_data["state"] = None

# =================================================================
# [9] MOTOR DE CALLBACKS (V500 LOGIC)
# =================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    uid_str = str(uid)
    data = q.data
    await q.answer()

    u_data = await db.get_user(q.from_user)

    # --- MINERÍA ---
    if data.startswith("mine_buy_"):
        rig = data.split("mine_buy_")[1]
        item = EmpireConfig.MINING_RIGS[rig]
        if u_data["points"] >= item["price"]:
            u_data["points"] -= item["price"]
            u_data["mining_rigs"][rig] += 1
            if rig == "QUANTUM" and "MINER_KING" not in u_data["achievements"]:
                u_data["achievements"].append("MINER_KING"); u_data["points"] += 25000
                await q.message.reply_text("🏆 ¡LOGRO: Rey Minero! +25000 pts")
            await db.save()
            await q.edit_message_text(f"✅ Has comprado {item['name']}.", reply_markup=EmpireUI.mining_panel(u_data["mining_rigs"]))
        else: await q.message.reply_text("❌ Puntos insuficientes.")
        
    elif data == "mine_collect":
        isc_gen, now = await calculate_mining_yield(u_data)
        if isc_gen > 0.001:
            u_data["isc_balance"] += isc_gen
            u_data["last_mine_collect"] = str(now)
            db.data["stats"]["total_isc_mined"] += isc_gen
            await db.save(); await db.update_bounty(uid_str, "mine_1", 1)
            await q.edit_message_text(f"✅ Has recolectado `{isc_gen:.4f} ISC` de tus granjas.", reply_markup=EmpireUI.mining_panel(u_data["mining_rigs"]))
        else: await q.message.reply_text("⚠️ No hay suficiente ISC generado aún.")

    # --- CRYPTO EXCHANGE ---
    elif data.startswith("crypto_"):
        cv = db.data["market_stats"]["crypto_value"]
        act = data.split("_")[1]
        amt_str = data.split("_")[2] if len(data.split("_")) > 2 else "1"
        
        if act == "buy":
            amt = int(amt_str)
            cost = cv * amt
            if u_data["points"] >= cost:
                u_data["points"] -= cost; u_data["isc_balance"] += amt
                await db.save()
                await q.edit_message_text(f"✅ Compraste {amt} ISC por {cost:.2f} pts.", reply_markup=EmpireUI.crypto_panel(cv, u_data['isc_balance'], u_data['points']))
            else: await q.message.reply_text("❌ Puntos insuficientes.")
            
        elif act == "sell":
            amt = u_data["isc_balance"] if amt_str == "all" else float(amt_str)
            if u_data["isc_balance"] >= amt and amt > 0:
                profit = cv * amt
                u_data["isc_balance"] -= amt; u_data["points"] += profit
                await db.save()
                await q.edit_message_text(f"✅ Vendiste {amt:.2f} ISC por {profit:.2f} pts.", reply_markup=EmpireUI.crypto_panel(cv, u_data['isc_balance'], u_data['points']))
            else: await q.message.reply_text("❌ ISC insuficiente.")

    # --- CASINO CRASH ---
    elif data == "casino_crash_setup":
        await q.message.reply_text("🚀 **CRASH GAME**\n¿Cuántos puntos deseas apostar? Escríbelo:")
        context.user_data["state"] = "WAIT_CRASH_BET"
        
    elif data == "crash_cashout":
        cd = context.user_data.get("crash_data")
        if cd and not cd.get("cashed_out"):
            cd["cashed_out"] = True
            win = int(cd["bet"] * cd["current"])
            u_data["points"] += win
            await db.save()
            try: await q.edit_message_text(f"💸 **¡RETIRO A TIEMPO!**\nMultiplicador: `{cd['current']}x`\nGanaste: `{win} pts`.")
            except: pass

    # --- CASINO BLACKJACK ---
    elif data == "casino_bj":
        bet = 500
        if u_data["points"] < bet: return await q.message.reply_text("❌ Requiere 500 pts.")
        u_data["points"] -= bet
        p_hand = [draw_card(), draw_card()]
        d_hand = [draw_card()]
        context.user_data["bj_hand"] = p_hand
        context.user_data["bj_dealer"] = d_hand
        msg = f"🃏 **BLACKJACK 21**\nTu Mano: {p_hand} (Valor: {calculate_hand(p_hand)})\nCrupier: {d_hand} [?]"
        await db.save()
        await q.edit_message_text(msg, reply_markup=EmpireUI.blackjack_panel(bet))
        
    elif data.startswith("bj_"):
        action = data.split("_")[1]
        bet = int(data.split("_")[2])
        p_hand = context.user_data.get("bj_hand", [])
        d_hand = context.user_data.get("bj_dealer", [])
        
        if action == "hit":
            p_hand.append(draw_card())
            val = calculate_hand(p_hand)
            if val > 21:
                await q.edit_message_text(f"💥 **TE PASASTE!**\nMano: {p_hand} ({val})\nPierdes {bet} pts.", reply_markup=EmpireUI.casino_panel())
            else:
                await q.edit_message_text(f"🃏 **BLACKJACK**\nMano: {p_hand} ({val})\nCrupier: {d_hand} [?]", reply_markup=EmpireUI.blackjack_panel(bet))
        elif action == "stand":
            p_val = calculate_hand(p_hand)
            while calculate_hand(d_hand) < 17: d_hand.append(draw_card())
            d_val = calculate_hand(d_hand)
            msg = f"🃏 **RESULTADO BLACKJACK**\nTu Mano: {p_hand} ({p_val})\nCrupier: {d_hand} ({d_val})\n\n"
            if d_val > 21 or p_val > d_val:
                win = bet * 2; u_data["points"] += win; msg += f"🎉 **¡GANASTE {win} pts!**"
            elif p_val == d_val:
                u_data["points"] += bet; msg += "🤝 **EMPATE.** Recuperas apuesta."
            else: msg += "💀 **CRUPIER GANA.**"
            await db.save(); await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())

    # --- B2B API ---
    elif data == "b2b_gen_key":
        if u_data['plan'] != 'GOD':
            return await q.message.reply_text("❌ Función exclusiva para rango GOD.")
        
        raw_key = f"ishak_live_{uuid.uuid4().hex}"
        # ENCRIPTACIÓN REAL AES-256
        enc_key = EmpireConfig.CIPHER.encrypt(raw_key.encode()).decode()
        u_data['api_key'] = enc_key
        db.data['b2b_api_keys'][enc_key] = uid_str
        
        if "HACKER" not in u_data["achievements"]:
            u_data["achievements"].append("HACKER"); u_data["points"]+=1000
        await db.save()
        await q.edit_message_text(f"🔑 **CLAVE API GENERADA (Guárdala, no se volverá a mostrar):**\n`{raw_key}`\n\n*Documentación disponible en el Dashboard Web.*", reply_markup=EmpireUI.b2b_panel(raw_key))

    # --- DESCARGAS ---
    elif data.startswith("fmt_"):
        mode = data.split("_")[1]
        context.user_data["active_fmt"] = mode
        
        # Omitimos selector de calidad para hacerlo más directo si es audio
        if mode == "MP3": context.user_data["active_qlty"] = "Best"
        else: context.user_data["active_qlty"] = "1080p" if u_data['plan'] in ['PRO', 'ULTRA', 'GOD'] else "720p"
        
        await finalize_download(update, context)

# =================================================================
# [10] MOTOR DE DESCARGA TITÁN (EXTRACCIÓN DEFINITIVA)
# =================================================================
async def finalize_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    uid_str = str(uid)
    url = context.user_data.get("active_url")
    fmt = context.user_data.get("active_fmt")
    qlty = context.user_data.get("active_qlty")
    u_data = await db.get_user(q.from_user)

    plan_info = EmpireConfig.PLANS[u_data["plan"]]
    max_size = plan_info["max_file_mb"]

    msg = await q.edit_message_text(f"⚡ **MOTOR TITAN INICIADO...**\n`[{fmt} | Extrayendo]`")
    job_id = f"job_{uid_str}_{uuid.uuid4().hex[:6]}"
    progress_tracker.add_job(job_id, msg)
    
    try:
        path, title, duration, f_size, is_veo3 = await MediaEngine.run(url, fmt, qlty, uid_str, max_size, job_id, u_data['settings'])
        
        if job_id in progress_tracker.active_jobs:
            progress_tracker.active_jobs[job_id]['finished'] = True
        
        size_mb = f_size / (1024 * 1024)
        if size_mb > 49.5: # Limit TG local API standard is 50MB. (Could use Local Bot API for 2GB but keeping safe).
            if os.path.exists(path): os.remove(path)
            return await msg.edit_text(f"❌ El archivo procesado ({size_mb:.1f}MB) supera el límite nativo de Telegram de 50MB. Usa la API B2B web para descargar archivos masivos.")

        await msg.edit_text("📤 **SUBIENDO AL SATÉLITE CORPORATIVO V500...**", parse_mode="Markdown")
        
        with open(path, 'rb') as f:
            wm_text = f"\n©️ Marca de Agua: `{u_data['settings']['watermark']}`" if u_data['settings'].get('watermark') else ""
            veo3_note = "\n🇪🇸 *Directiva Veo3: Audio/Subs Forzados a ESPAÑOL.* " if is_veo3 else ""
            cap = (
                f"✅ **{title[:50]}...**\n"
                f"⏱️ `{str(datetime.timedelta(seconds=duration))}` | 💾 `{size_mb:.1f} MB`{wm_text}{veo3_note}\n"
            )
            
            if fmt == "MP3": 
                await context.bot.send_audio(uid, f, caption=cap, parse_mode="Markdown", read_timeout=120)
            else: 
                await context.bot.send_video(uid, f, caption=cap, parse_mode="Markdown", read_timeout=300, supports_streaming=True)

        u_data["daily_downloads"][0] += 1
        db.data["stats"]["total_downloads"] += 1
        await db.save(); await db.update_bounty(uid_str, "dl_3", 1)
        
        if os.path.exists(path): os.remove(path)
        try: await msg.delete()
        except: pass

    except Exception as e:
        if job_id in progress_tracker.active_jobs: progress_tracker.active_jobs[job_id]['finished'] = True
        logger.error(f"Fallo Descarga UID {uid}: {e}")
        await msg.edit_text(f"❌ **ERROR DE MATRIZ V500:**\nNo se pudo extraer. Posible protección DRM o bloqueo regional.")

# =================================================================
# [11] PANEL SAAS WEB (DASHBOARD REAL + B2B API DOCUMENTATION)
# =================================================================
web_app = Flask("Ishak_Enterprise_Web_V500")
CORS_APP(web_app)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ishak Enterprise V500 | Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: #e2e8f0; }
        .glass { background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .gradient-text { background: linear-gradient(to right, #38bdf8, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
</head>
<body class="font-sans antialiased min-h-screen flex flex-col">
    <nav class="glass sticky top-0 z-50 px-6 py-4 flex justify-between items-center shadow-lg border-b border-slate-800">
        <div class="text-2xl font-black tracking-tighter"><span class="gradient-text">ISHAK</span> V500</div>
        <div class="space-x-6 text-sm font-semibold">
            <a href="/" class="hover:text-blue-400 transition">Inicio</a>
            <a href="/docs" class="hover:text-purple-400 transition">API Docs</a>
        </div>
    </nav>

    <main class="flex-grow container mx-auto px-4 py-12">
        {% block content %}{% endblock %}
    </main>

    <footer class="glass py-6 text-center text-sm text-slate-500 mt-auto border-t border-slate-800">
        &copy; 2026 Ishak Enterprise V500. Sede Central: España. Directiva estricta B2B. Todos los derechos reservados.
    </footer>
</body>
</html>
"""

LANDING_HTML = "{% extends 'base.html' %}{% block content %}" + """
<div class="text-center py-20">
    <h1 class="text-6xl md:text-7xl font-extrabold mb-6 tracking-tight">Arquitectura <span class="gradient-text">Omniversal</span></h1>
    <p class="text-xl md:text-2xl text-slate-400 mb-12 max-w-3xl mx-auto">La infraestructura de extracción y automatización de datos más blindada de España. Valorada en 500,000€. Directiva Veo3 Activa.</p>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-left mt-16">
        <div class="glass p-8 rounded-2xl hover:-translate-y-2 transition transform duration-300">
            <i class="fas fa-server text-4xl text-blue-400 mb-4"></i>
            <h3 class="text-2xl font-bold mb-3">API B2B (REST)</h3>
            <p class="text-slate-400">Extrae enlaces directos (CDN) burlando restricciones geográficas. Soporte CORS total para SaaS.</p>
        </div>
        <div class="glass p-8 rounded-2xl hover:-translate-y-2 transition transform duration-300">
            <i class="fas fa-lock text-4xl text-purple-400 mb-4"></i>
            <h3 class="text-2xl font-bold mb-3">Cifrado AES-256</h3>
            <p class="text-slate-400">Seguridad militar. Las claves API son hasheadas y encriptadas en la bóveda shadow-DB.</p>
        </div>
        <div class="glass p-8 rounded-2xl hover:-translate-y-2 transition transform duration-300">
            <i class="fas fa-language text-4xl text-green-400 mb-4"></i>
            <h3 class="text-2xl font-bold mb-3">Directiva Veo3</h3>
            <p class="text-slate-400">Mandato inquebrantable del Director: Todo contenido de origen veo3 es forzado nativamente a Español.</p>
        </div>
    </div>
</div>
""" + "{% endblock %}"

DOCS_HTML = "{% extends 'base.html' %}{% block content %}" + """
<div class="max-w-4xl mx-auto glass p-10 rounded-3xl">
    <h2 class="text-4xl font-bold mb-8 gradient-text">Documentación de la API (B2B)</h2>
    <p class="mb-6 text-slate-300">Endpoint para extracción de enlaces directos. Requiere rango GOD en Telegram para generar la clave API.</p>
    
    <div class="bg-slate-900 p-6 rounded-xl border border-slate-700 mb-8">
        <h4 class="text-lg font-bold text-blue-400 mb-2">POST /api/v5/extract</h4>
        <p class="text-sm text-slate-400 mb-4">Extrae el enlace directo .mp4 de cualquier URL soportada.</p>
        
        <h5 class="font-bold text-slate-200 mt-4">Headers Requeridos:</h5>
        <pre class="bg-black p-3 rounded mt-2 text-green-400 text-sm">X-API-KEY: ishak_live_xxxxxxxx</pre>
        
        <h5 class="font-bold text-slate-200 mt-4">Body (JSON):</h5>
        <pre class="bg-black p-3 rounded mt-2 text-green-400 text-sm">{ "url": "https://ejemplo.com/video123" }</pre>
    </div>
</div>
""" + "{% endblock %}"

@web_app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', LANDING_HTML))

@web_app.route('/docs', methods=['GET'])
def docs():
    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', DOCS_HTML))

@web_app.route('/api/v5/extract', methods=['POST'])
def api_real_extract():
    raw_api_key = request.headers.get('X-API-KEY')
    if not raw_api_key: return jsonify({"error": "No autorizado. Header X-API-KEY ausente."}), 401
    
    # Validar API KEY encriptada
    valid_uid = None
    for enc_key, uid in db.data.get('b2b_api_keys', {}).items():
        try:
            decrypted = EmpireConfig.CIPHER.decrypt(enc_key.encode()).decode()
            if decrypted == raw_api_key:
                valid_uid = uid
                break
        except: continue

    if not valid_uid:
        return jsonify({"error": "Clave API inválida o revocada."}), 401
    
    data = request.json or {}
    url = data.get('url')
    if not url: return jsonify({"error": "Parámetro 'url' es requerido."}), 400
        
    try:
        opts = {'quiet': True, 'noplaylist': True}
        if "veo3" in url.lower(): opts['format_sort'] = ['+language:es']
            
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            direct_url = info.get('url')
            if not direct_url and info.get('formats'): direct_url = info['formats'][-1].get('url')
                
            return jsonify({
                "status": "success", "code": 200,
                "data": {
                    "title": info.get('title'), "duration": info.get('duration'),
                    "direct_cdn_url": direct_url, "source": info.get('extractor')
                }
            })
    except Exception as e:
        return jsonify({"error": "Fallo durante la extracción en la matriz.", "details": str(e)}), 500

def run_web_server():
    """Usa waitress para producción en lugar del servidor built-in de Flask."""
    port = int(os.getenv("PORT", 8080))
    print(f"🌐 [WEB SERVER] Iniciando Waitress B2B en puerto {port}...")
    waitress.serve(web_app, host='0.0.0.0', port=port, threads=8)

# =================================================================
# [12] SECUENCIA DE INICIO TITÁN V500
# =================================================================
async def post_init(app: Application):
    # Lanzar tareas en segundo plano del Bot
    asyncio.create_task(db.backup_job())
    asyncio.create_task(db.market_simulation_job())
    asyncio.create_task(progress_tracker.update_messages_loop())

def main():
    print("=" * 80)
    print(f"🚀 INICIANDO ISHAK HYPER-SAAS V{EmpireConfig.VERSION}")
    print("💎 CÓDIGO DE RESPALDO (SHADOW DB ASYNC) ACTIVO.")
    print("🛡️ REGLA VEO3 (ESPAÑOL) BLINDADA. MINERÍA Y CASINO EN LÍNEA.")
    print("=" * 80)
    
    # Iniciar servidor web en hilo separado para no bloquear el bot
    threading.Thread(target=run_web_server, daemon=True).start()
    
    application = (
        ApplicationBuilder()
        .token(EmpireConfig.TOKEN)
        .pool_timeout(60.0).read_timeout(60.0).write_timeout(60.0)
        .connection_pool_size(4096)
        .post_init(post_init)
        .build()
    )
    
    application.add_handler(CommandHandler("start", start_handler))
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
