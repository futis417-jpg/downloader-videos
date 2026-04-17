"""
██╗███████╗██╗  ██╗███████╗██╗  ██╗    ██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗ 
██║██╔════╝██║  ██║██╔════╝██║ ██╔╝    ██║  ██║╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
██║███████╗███████║███████╗█████╔╝     ███████║ ╚████╔╝ ██████╔╝█████╗  ██████╔╝
██║╚════██║██╔══██║╚════██║██╔═██╗     ██╔══██║  ╚██╔╝  ██╔═══╝ ██╔══╝  ██╔══██╗
██║███████║██║  ██║███████║██║  ██╗    ██║  ██║   ██║   ██║     ███████╗██║  ██║
╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝
SISTEMA: ISHAK HYPER-SAAS V80.0 - THE OMNIVERSAL EDITION
ESTADO: SUPREME CONTROL - GOD MODE ENFORCED
PROPIETARIO: Ishak Ezzahouani (ID: 8398522835) - 18 Años.
PAÍS: España (Control Central de Datos)
REGLA ESPECIAL: Contenido 'veo3' procesado estrictamente en ESPAÑOL.
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
from typing import Dict, List, Any, Optional, Union, Tuple
from functools import wraps

# =================================================================
# [0] INICIALIZACIÓN DE DEPENDENCIAS Y BLINDAJE DE ENTORNOS
# =================================================================
def bootstrap_packages():
    """Garantiza que el arsenal de librerías esté listo para el despliegue masivo."""
    packages = [
        'python-telegram-bot', 'yt-dlp', 'flask', 'requests', 
        'psutil', 'Pillow', 'aiohttp', 'cryptography'
    ]
    for p in packages:
        try:
            __import__(p.replace('-', '_'))
        except ImportError:
            print(f"📦 [BOOTSTRAP] Instalando componente crítico: {p}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", p, "--quiet"])
    
    global yt_dlp, requests, psutil, aiohttp
    import yt_dlp, requests, psutil, aiohttp

bootstrap_packages()

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, constants,
    InputMediaPhoto, InputMediaVideo, InputFile
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters, Application
)
from flask import Flask, jsonify, request

# =================================================================
# [1] ARQUITECTURA DE CONFIGURACIÓN (CENTRO DE DATOS)
# =================================================================
class EmpireConfig:
    ADMIN_ID = 8398522835
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4" # Token del Creador
    VERSION = "80.0.0-OMNIVERSAL"
    
    # Rutas de Infraestructura
    ROOT = os.getcwd()
    VAULT_DIR = os.path.join(ROOT, "empire_vault")
    BUFFER_DIR = os.path.join(ROOT, "download_buffer")
    LOGS_DIR = os.path.join(ROOT, "system_logs")
    BACKUP_DIR = os.path.join(VAULT_DIR, "backups")
    DATABASE_PATH = os.path.join(VAULT_DIR, "empire_master_v80.json")
    
    # Estructura de Planes y Limitaciones (Expansión Masiva)
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
            "name": "🔥 SOBERANO (ULTRA)", "limit_daily": 999999, "max_file_mb": 10000,
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K"], 
            "speed": "Instántanea (Sin límites)", "priority": 2, "max_duration_min": 600
        },
        "GOD": {
            "name": "👁️ OMNIPRESENTE (GOD)", "limit_daily": float('inf'), "max_file_mb": float('inf'),
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K", "Original"], 
            "speed": "Quantum", "priority": 3, "max_duration_min": float('inf')
        }
    }

    # Economía Imperial y Sistema de RPG
    ECONOMY = {
        "DAILY_REWARD_MIN": 100,
        "DAILY_REWARD_MAX": 300,
        "REF_REWARD": 1000,
        "PRICE_PRO_DAY": 1000,
        "PRICE_ULTRA_DAY": 3000,
        "PRICE_XP_BOOST": 5000,
        "XP_PER_DOWNLOAD": 15,
        "XP_PER_MESSAGE": 1,
    }

    # Sistema de Logros
    ACHIEVEMENTS = {
        "FIRST_BLOOD": {"name": "Primera Sangre", "desc": "Realiza tu primera descarga.", "reward": 500},
        "CENTURION": {"name": "Centurión", "desc": "Alcanza 100 descargas.", "reward": 5000},
        "INFLUENCER": {"name": "Influencer", "desc": "Invita a 10 ciudadanos.", "reward": 10000},
        "LOYALTY": {"name": "Lealtad Imperial", "desc": "Reclama recompensa 7 días seguidos.", "reward": 3000}
    }

    @classmethod
    def init_filesystem(cls):
        """Prepara el entorno de almacenamiento de alto rendimiento."""
        for d in [cls.VAULT_DIR, cls.BUFFER_DIR, cls.LOGS_DIR, cls.BACKUP_DIR]:
            os.makedirs(d, exist_ok=True)
        # Purgatorio de buffers huérfanos
        for f in os.listdir(cls.BUFFER_DIR):
            try: os.remove(os.path.join(cls.BUFFER_DIR, f))
            except: pass

EmpireConfig.init_filesystem()

# =================================================================
# [2] SISTEMA DE LOGS Y AUDITORÍA QUANTUM
# =================================================================
audit_handler = logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "empire_audit.log"), encoding='utf-8')

error_handler = logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "empire_errors.log"), encoding='utf-8')
error_handler.setLevel(logging.ERROR)

stream_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[audit_handler, error_handler, stream_handler]
)
logger = logging.getLogger("ISHAK_OVERLORD")
logger.info("Iniciando secuencias de arranque del Imperio...")

# =================================================================
# [3] NÚCLEO DE BASE DE DATOS Y GESTIÓN DE ESTADO MASIVO
# =================================================================
class EmpireDatabase:
    """Motor de base de datos en memoria con sincronización persistente y backups automáticos."""
    def __init__(self):
        self._lock = asyncio.Lock()
        self.data = {
            "users": {},
            "coupons": {},
            "blacklist": [],
            "transactions": [],
            "tickets": {},
            "market_stats": {"crypto_value": 100.0, "trend": "up"},
            "stats": {
                "total_downloads": 0, "total_users": 0, "bytes_processed": 0,
                "boot_time": str(datetime.datetime.now()), "commands_executed": 0
            },
            "system": {
                "maint_mode": False, "announcement": None,
                "global_welcome": "👑 **BIENVENIDO AL IMPERIO OMNIVERSAL V80**\nCreado por el Soberano Ishak.\nDominio absoluto sobre los medios digitales."
            }
        }
        self.sync_load()

    def sync_load(self):
        if os.path.exists(EmpireConfig.DATABASE_PATH):
            try:
                with open(EmpireConfig.DATABASE_PATH, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    # Merge recursivo básico para mantener estructuras nuevas en updates
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
                # Escribir en un archivo temporal primero para evitar corrupción por apagón
                temp_path = f"{EmpireConfig.DATABASE_PATH}.tmp"
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=4, ensure_ascii=False)
                os.replace(temp_path, EmpireConfig.DATABASE_PATH)
            except Exception as e:
                logger.error(f"Error de persistencia de datos: {e}")

    async def backup_job(self):
        """Tarea asíncrona que hace backup de la DB cada 6 horas."""
        while True:
            await asyncio.sleep(60 * 60 * 6) # 6 horas
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(EmpireConfig.BACKUP_DIR, f"db_backup_{timestamp}.json")
                shutil.copy2(EmpireConfig.DATABASE_PATH, backup_path)
                logger.info(f"Backup automático creado: {backup_path}")
            except Exception as e:
                logger.error(f"Fallo en backup automático: {e}")

    async def get_user(self, user_obj):
        uid = str(user_obj.id)
        is_new = False
        async with self._lock:
            if uid not in self.data["users"]:
                is_new = True
                self.data["users"][uid] = {
                    "id": user_obj.id,
                    "name": user_obj.first_name,
                    "username": user_obj.username,
                    "plan": "GOD" if user_obj.id == EmpireConfig.ADMIN_ID else "FREE",
                    "plan_expiry": None,
                    "points": 1000, # Bono inicial Imperial
                    "level": 1,
                    "xp": 0,
                    "total_downloads": 0,
                    "daily_downloads": [0, str(datetime.date.today())],
                    "referrals": 0,
                    "referred_by": None,
                    "achievements": [],
                    "inventory": [],
                    "joined": str(datetime.date.today()),
                    "is_banned": False,
                    "warnings": 0,
                    "last_daily": None,
                    "history": []
                }
                self.data["stats"]["total_users"] += 1
                
        if is_new:
            await self.save()

        u = self.data["users"][uid]
        
        # Sincronización de variables diarias
        today = str(datetime.date.today())
        if u["daily_downloads"][1] != today:
            u["daily_downloads"] = [0, today]
            await self.save()
            
        # Verificar expiración de plan
        if u.get("plan_expiry"):
            expiry = datetime.datetime.fromisoformat(u["plan_expiry"])
            if datetime.datetime.now() > expiry:
                u["plan"] = "FREE"
                u["plan_expiry"] = None
                await self.save()
                
        return u

    async def add_xp(self, uid: str, amount: int):
        u = self.data["users"][uid]
        u["xp"] += amount
        xp_needed = u["level"] * 100
        leveled_up = False
        while u["xp"] >= xp_needed:
            u["xp"] -= xp_needed
            u["level"] += 1
            u["points"] += u["level"] * 50 # Recompensa por nivel
            xp_needed = u["level"] * 100
            leveled_up = True
        await self.save()
        return leveled_up, u["level"]

    async def log_transaction(self, uid, amount, description):
        self.data["transactions"].append({
            "uid": uid, "amount": amount, "desc": description,
            "date": str(datetime.datetime.now())
        })
        # Mantener solo las últimas 1000 transacciones para no saturar memoria
        if len(self.data["transactions"]) > 1000:
            self.data["transactions"].pop(0)
        await self.save()

db = EmpireDatabase()

# =================================================================
# [4] SEGURIDAD Y CONTROL DE FLUJO (MIDDLEWARES)
# =================================================================
class SecurityCore:
    def __init__(self):
        self.spam_cache = {}
    
    def rate_limit(self, uid: int, limit: int = 2) -> bool:
        """Evita que el usuario inunde el bot. Retorna True si está en spam."""
        now = time.time()
        if uid in self.spam_cache:
            last_time, count = self.spam_cache[uid]
            if now - last_time < 3:
                self.spam_cache[uid] = (now, count + 1)
                if count + 1 > limit:
                    return True
            else:
                self.spam_cache[uid] = (now, 1)
        else:
            self.spam_cache[uid] = (now, 1)
        return False

sec_core = SecurityCore()

def ishak_protected(func):
    """Decorador para proteger comandos exclusivos del Creador."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id != EmpireConfig.ADMIN_ID:
            await update.message.reply_text("⛔ **ACCESO DENEGADO:** Este comando está restringido al Soberano Ishak.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# =================================================================
# [5] MOTOR DE EXTRACCIÓN Y PROCESAMIENTO (ISHAK-ENGINE V8)
# =================================================================
class MediaEngine:
    """Núcleo de procesamiento avanzado de medios. Soporta Veo3, YT, TikTok, IG."""
    
    @staticmethod
    async def get_info(url: str):
        opts = {
            'quiet': True, 'no_warnings': True, 'noplaylist': True,
            'extract_flat': True # Para rapidez en info
        }
        def _get():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        try:
            return await asyncio.to_thread(_get)
        except Exception as e:
            logger.error(f"Error extrayendo info MediaEngine: {e}")
            return None

    @staticmethod
    async def run(url: str, mode: str, quality: str, uid: str, max_size_mb: int):
        """Descarga el medio y lo guarda en el buffer. Aplica reglas especiales."""
        job_id = f"ishak_{uid}_{uuid.uuid4().hex[:10]}"
        output_template = os.path.join(EmpireConfig.BUFFER_DIR, f"{job_id}.%(ext)s")
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'max_filesize': max_size_mb * 1024 * 1024,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            # Evasión de bloqueos básica
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }

        # REGLA ESPECIAL VEO3: Asegurar idioma español
        if "veo3" in url.lower():
            logger.info(f"Detectado enlace veo3 para UID {uid}. Aplicando override a ESPAÑOL.")
            ydl_opts['writesubtitles'] = True
            ydl_opts['subtitleslangs'] = ['es', 'spa']
            # Forzar formato de audio español si está disponible
            ydl_opts['format_sort'] = ['+language:es', 'res:1080']

        if mode == "MP3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            })
        elif mode == "MP4":
            h = quality.replace("p", "") if quality != "Original" else "2160"
            ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        def _execute():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if mode == "MP3":
                    file_path = os.path.splitext(file_path)[0] + ".mp3"
                
                # Obtener tamaño real
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                return file_path, info.get('title', 'Media_Ishak_V80'), info.get('duration', 0), file_size

        return await asyncio.to_thread(_execute)

# =================================================================
# [6] DISEÑADOR DE INTERFACES E INGENIERÍA SOCIAL
# =================================================================
class EmpireUI:
    """Generador dinámico de UI de Telegram adaptado al rango del usuario."""
    
    @staticmethod
    def main_keyboard(uid):
        is_admin = uid == EmpireConfig.ADMIN_ID
        btns = [
            [KeyboardButton("📥 INICIAR EXTRACCIÓN"), KeyboardButton("👤 MI EXPEDIENTE")],
            [KeyboardButton("💎 MERCADO NEGRO"), KeyboardButton("🎁 TRIBUTO DIARIO")],
            [KeyboardButton("🎮 MISIONES Y LOGROS"), KeyboardButton("🎫 CANJEAR CÓDIGO")],
            [KeyboardButton("👥 RED DE AFILIADOS"), KeyboardButton("🎧 SOPORTE / TICKETS")]
        ]
        if is_admin:
            btns.append([KeyboardButton("👑 PANEL OVERLORD 👑")])
            btns.append([KeyboardButton("🌐 TELEMETRÍA GLOBAL")])
        return ReplyKeyboardMarkup(btns, resize_keyboard=True)

    @staticmethod
    def overlord_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 LISTA ESCLAVOS", callback_data="adm_list"), 
             InlineKeyboardButton("📢 TRANSMISIÓN MUNDIAL", callback_data="adm_bc")],
            [InlineKeyboardButton("🚫 EJECUTAR BAN", callback_data="adm_ban"), 
             InlineKeyboardButton("🔓 PERDONAR (UNBAN)", callback_data="adm_unban")],
            [InlineKeyboardButton("💰 INYECTAR FONDOS", callback_data="adm_pts"), 
             InlineKeyboardButton("🎫 FORJAR CUPÓN", callback_data="adm_cp")],
            [InlineKeyboardButton("🎭 ALTERAR RANGO", callback_data="adm_edit_plan"), 
             InlineKeyboardButton("📂 GESTIÓN TICKETS", callback_data="adm_tickets")],
            [InlineKeyboardButton("💾 FORZAR BACKUP", callback_data="adm_backup"), 
             InlineKeyboardButton("🧹 PURGAR CACHÉ", callback_data="adm_clean")],
            [InlineKeyboardButton("❌ CERRAR TERMINAL", callback_data="u_close")]
        ])

    @staticmethod
    def market_panel(crypto_val):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💎 1 DÍA PRO ({EmpireConfig.ECONOMY['PRICE_PRO_DAY']} pts)", callback_data="buy_PRO_1")],
            [InlineKeyboardButton(f"💎 7 DÍAS PRO ({EmpireConfig.ECONOMY['PRICE_PRO_DAY'] * 6} pts - ¡Oferta!)", callback_data="buy_PRO_7")],
            [InlineKeyboardButton(f"🔥 1 DÍA ULTRA ({EmpireConfig.ECONOMY['PRICE_ULTRA_DAY']} pts)", callback_data="buy_ULTRA_1")],
            [InlineKeyboardButton(f"📈 INVERTIR EN ISHAK-COIN (Valor: {crypto_val} pts)", callback_data="market_crypto")],
            [InlineKeyboardButton("❌ SALIR DEL MERCADO", callback_data="u_close")]
        ])

    @staticmethod
    def format_selector():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 VIDEO (MP4)", callback_data="fmt_MP4"),
             InlineKeyboardButton("🎵 AUDIO (MP3)", callback_data="fmt_MP3")],
            [InlineKeyboardButton("❌ ABORTAR OPERACIÓN", callback_data="u_close")]
        ])

    @staticmethod
    def quality_selector(plan_id):
        qualities = EmpireConfig.PLANS.get(plan_id, EmpireConfig.PLANS["FREE"])["resolutions"]
        rows = []
        # Agrupar en pares
        for i in range(0, len(qualities), 2):
            row = [InlineKeyboardButton(f"🎥 {q}", callback_data=f"ql_{q}") for q in qualities[i:i+2]]
            rows.append(row)
        rows.append([InlineKeyboardButton("⬅️ ATRÁS", callback_data="fmt_back")])
        return InlineKeyboardMarkup(rows)

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
# [7] HANDLERS Y LÓGICA DE USUARIO (EL CEREBRO DE ISHAK)
# =================================================================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid_str = str(user.id)
    
    if sec_core.rate_limit(user.id): return
    
    u_data = await db.get_user(user)
    
    # Sistema de Referidos Avanzado
    if context.args and context.args[0].isdigit():
        ref_id = context.args[0]
        if ref_id != str(user.id) and not u_data.get("referred_by"):
            u_data["referred_by"] = ref_id
            if ref_id in db.data["users"]:
                db.data["users"][ref_id]["points"] += EmpireConfig.ECONOMY["REF_REWARD"]
                db.data["users"][ref_id]["referrals"] += 1
                await db.log_transaction(ref_id, EmpireConfig.ECONOMY["REF_REWARD"], f"Bono por reclutar a {user.first_name}")
                
                # Check Logro Influencer
                if db.data["users"][ref_id]["referrals"] >= 10 and "INFLUENCER" not in db.data["users"][ref_id]["achievements"]:
                    db.data["users"][ref_id]["achievements"].append("INFLUENCER")
                    db.data["users"][ref_id]["points"] += EmpireConfig.ACHIEVEMENTS["INFLUENCER"]["reward"]
                    try:
                        await context.bot.send_message(
                            ref_id, 
                            f"🏆 **¡NUEVO LOGRO DESBLOQUEADO: Influencer!**\nHas reclutado a 10 ciudadanos. +{EmpireConfig.ACHIEVEMENTS['INFLUENCER']['reward']} pts."
                        )
                    except: pass
                
                try:
                    await context.bot.send_message(
                        ref_id, 
                        f"🎊 **¡NUEVO CIUDADANO EN TU RED!**\nEl usuario {user.first_name} se ha unido gracias a ti. +{EmpireConfig.ECONOMY['REF_REWARD']} puntos añadidos a tu cuenta."
                    )
                except: pass
            await db.save()

    welcome_msg = db.data["system"]["global_welcome"]
    if user.id == EmpireConfig.ADMIN_ID:
        welcome_msg = "👁️ **SALVE, SOBERANO ISHAK.**\nLos sistemas están listos para acatar sus órdenes."

    await update.message.reply_text(
        welcome_msg,
        reply_markup=EmpireUI.main_keyboard(user.id),
        parse_mode="Markdown"
    )
    
    # Sistema pasivo de criptomercado (fluctuación)
    if random.random() > 0.7:
        fluctuation = random.uniform(-15.0, 20.0)
        db.data["market_stats"]["crypto_value"] = max(10.0, db.data["market_stats"]["crypto_value"] + fluctuation)
        db.data["market_stats"]["trend"] = "up" if fluctuation > 0 else "down"

async def check_achievements(uid: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica y otorga logros en segundo plano."""
    u_data = db.data["users"][uid]
    ach_gained = []
    
    if u_data["total_downloads"] >= 1 and "FIRST_BLOOD" not in u_data["achievements"]:
        ach_gained.append("FIRST_BLOOD")
    if u_data["total_downloads"] >= 100 and "CENTURION" not in u_data["achievements"]:
        ach_gained.append("CENTURION")
        
    for ach in ach_gained:
        u_data["achievements"].append(ach)
        reward = EmpireConfig.ACHIEVEMENTS[ach]["reward"]
        u_data["points"] += reward
        name = EmpireConfig.ACHIEVEMENTS[ach]["name"]
        await db.log_transaction(uid, reward, f"Logro: {name}")
        await context.bot.send_message(
            int(uid), 
            f"🏅 **¡LOGRO DESBLOQUEADO: {name}!**\nRecompensa: +{reward} puntos.",
            parse_mode="Markdown"
        )
    if ach_gained:
        await db.save()

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    uid_str = str(user.id)
    state = context.user_data.get("state")

    if sec_core.rate_limit(user.id): return

    u_data = await db.get_user(user)
    if u_data.get("is_banned"):
        return await update.message.reply_text("🚫 **ACCESO DENEGADO.** Estás exiliado del Imperio. Contacta soporte vía email si crees que es un error.")

    db.data["stats"]["commands_executed"] += 1
    
    # Dar algo de XP por interactuar
    leveled, new_lvl = await db.add_xp(uid_str, EmpireConfig.ECONOMY["XP_PER_MESSAGE"])
    if leveled:
        await update.message.reply_text(f"🆙 **¡NIVEL AUMENTADO!** Ahora eres nivel {new_lvl}. Puntos añadidos a tu cartera.")

    # -------------------------------------------------------------
    # [A] RUTAS DEL MENÚ PRINCIPAL
    # -------------------------------------------------------------
    if text == "📥 INICIAR EXTRACCIÓN":
        await update.message.reply_text("🔗 **SISTEMAS PREPARADOS. ENVÍA EL ENLACE DEL MEDIO:**\n*(Soporta YT, TikTok, IG, Veo3 y más...)*")
        context.user_data["state"] = "WAIT_URL"

    elif text == "👤 MI EXPEDIENTE":
        plan = EmpireConfig.PLANS[u_data["plan"]]
        expiry = f"\n⏳ Expiración: `{u_data['plan_expiry'][:10]}`" if u_data['plan_expiry'] else "\n⏳ Expiración: `PERMANENTE`"
        prog = f"{u_data['xp']}/{u_data['level']*100} XP"
        
        msg = (
            f"👤 **EXPEDIENTE IMPERIAL CLASIFICADO**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: `{user.id}`\n"
            f"🛡️ Ciudadano: `{user.first_name}`\n"
            f"📈 Nivel: **{u_data['level']}** ({prog})\n"
            f"🎭 Rango Activo: **{plan['name']}**{expiry}\n"
            f"💰 Capital: `{u_data['points']} pts`\n"
            f"📥 Extracciones Hoy: `{u_data['daily_downloads'][0]} / {plan['limit_daily']}`\n"
            f"🏅 Logros Obtenidos: `{len(u_data['achievements'])}`\n"
            f"👥 Red de Esclavos (Referidos): `{u_data['referrals']}`\n"
            f"📅 Fecha de Ingreso: `{u_data['joined']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🎁 TRIBUTO DIARIO":
        today = str(datetime.date.today())
        if u_data.get("last_daily") == today:
            await update.message.reply_text("❌ Ya has recibido tu tributo imperial hoy. El sistema rota a medianoche.")
        else:
            u_data["last_daily"] = today
            reward = random.randint(EmpireConfig.ECONOMY["DAILY_REWARD_MIN"], EmpireConfig.ECONOMY["DAILY_REWARD_MAX"])
            
            # Bono por rango
            if u_data["plan"] == "PRO": reward = int(reward * 1.5)
            elif u_data["plan"] in ["ULTRA", "GOD"]: reward = int(reward * 2.5)
            
            u_data["points"] += reward
            await db.log_transaction(uid_str, reward, "Tributo Diario")
            await db.save()
            await update.message.reply_text(f"✅ Los tesoros del imperio te otorgan **{reward} puntos** hoy.")

    elif text == "💎 MERCADO NEGRO":
        cv = round(db.data["market_stats"]["crypto_value"], 2)
        await update.message.reply_text(
            f"💎 **MERCADO NEGRO V80**\n\nAdquiere mejoras para tu cuenta. Tu capital: `{u_data['points']} pts`.\nValor de IshakCoin hoy: {cv}",
            reply_markup=EmpireUI.market_panel(cv),
            parse_mode="Markdown"
        )

    elif text == "🎫 CANJEAR CÓDIGO":
        await update.message.reply_text("🎟️ **Introduce la clave criptográfica del cupón:**")
        context.user_data["state"] = "WAIT_COUPON"

    elif text == "👥 RED DE AFILIADOS":
        me = await context.bot.get_me()
        link = f"https://t.me/{me.username}?start={user.id}"
        await update.message.reply_text(
            f"🕸️ **EXPANDE EL IMPERIO**\n\nPor cada humano que inicie el bot con tu enlace, ganarás **{EmpireConfig.ECONOMY['REF_REWARD']} puntos**.\n\n🔗 Tu enlace único de adoctrinamiento:\n`{link}`",
            parse_mode="Markdown"
        )
        
    elif text == "🎮 MISIONES Y LOGROS":
        msg = "🎮 **SALÓN DE LA FAMA IMPERIAL**\n\n"
        for k, v in EmpireConfig.ACHIEVEMENTS.items():
            status = "✅ DESBLOQUEADO" if k in u_data["achievements"] else "🔒 BLOQUEADO"
            msg += f"• **{v['name']}**: {v['desc']} ({status})\n"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🎧 SOPORTE / TICKETS":
        await update.message.reply_text("📝 **Describe tu problema en un solo mensaje para abrir un ticket con el Alto Mando:**")
        context.user_data["state"] = "WAIT_TICKET"

    # --- ZONA OVERLORD (Solo Ishak) ---
    elif text == "👑 PANEL OVERLORD 👑" and user.id == EmpireConfig.ADMIN_ID:
        await update.message.reply_text("🛠 **CENTRO DE COMANDO SUPREMO ISHAK V80**", reply_markup=EmpireUI.overlord_panel())

    elif text == "🌐 TELEMETRÍA GLOBAL" and user.id == EmpireConfig.ADMIN_ID:
        s = db.data["stats"]
        up = str(datetime.datetime.now() - datetime.datetime.fromisoformat(s["boot_time"])).split('.')[0]
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        msg = (
            f"🌐 **TELEMETRÍA OMNIVERSAL**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Población Total: `{s['total_users']}`\n"
            f"📥 Extracciones Globales: `{s['total_downloads']}`\n"
            f"⚡ Comandos Ejecutados: `{s['commands_executed']}`\n"
            f"⏱️ Uptime del Motor: `{up}`\n"
            f"🧠 RAM del Servidor: `{mem.percent}%` ({mem.used//1024**2}MB usados)\n"
            f"💾 Almacenamiento: `{disk.percent}%` ({disk.free//1024**3}GB libres)\n"
            f"🚀 OS: `{platform.system()} {platform.release()}`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    # -------------------------------------------------------------
    # [B] MÁQUINA DE ESTADOS FINITOS (FSM)
    # -------------------------------------------------------------
    elif state == "WAIT_URL":
        if re.match(r'^https?://', text):
            context.user_data["active_url"] = text
            await update.message.reply_text("🛠 **Objetivo fijado.** Selecciona el formato de extracción:", reply_markup=EmpireUI.format_selector())
        else:
            await update.message.reply_text("❌ Formato de protocolo inválido. Se requiere HTTP/HTTPS.")
        context.user_data["state"] = None

    elif state == "WAIT_COUPON":
        code = text.upper().strip()
        if code in db.data["coupons"]:
            plan = db.data["coupons"].pop(code)
            u_data["plan"] = plan
            expiry = datetime.datetime.now() + datetime.timedelta(days=30)
            u_data["plan_expiry"] = str(expiry)
            await db.save()
            await update.message.reply_text(f"✅ **PROTOCOLOS SOBRESCRITOS.** Rango ascendido a **{plan}** durante 30 días.")
        else:
            await update.message.reply_text("❌ Cifrado inválido o cupón consumido.")
        context.user_data["state"] = None

    elif state == "WAIT_TICKET":
        ticket_id = f"TK-{random.randint(1000, 9999)}"
        db.data["tickets"][ticket_id] = {
            "uid": uid_str, "text": text, "status": "OPEN", "date": str(datetime.datetime.now())
        }
        await db.save()
        await update.message.reply_text(f"✅ Ticket `{ticket_id}` enviado al Alto Mando. Espera respuesta.")
        
        # Notificar a Ishak
        try:
            await context.bot.send_message(
                EmpireConfig.ADMIN_ID,
                f"🚨 **NUEVO TICKET ({ticket_id})**\nDe: {user.first_name} (`{uid_str}`)\n\nMensaje: {text}",
                reply_markup=EmpireUI.ticket_panel(ticket_id)
            )
        except: pass
        context.user_data["state"] = None

    # --- ESTADOS DEL PANEL OVERLORD ---
    elif state == "WAIT_BC" and user.id == EmpireConfig.ADMIN_ID:
        count, errors = 0, 0
        status_msg = await update.message.reply_text("📡 Iniciando transmisión global...")
        for sid in list(db.data["users"].keys()):
            try:
                await context.bot.send_message(sid, f"📢 **MENSAJE DEL SOBERANO ISHAK:**\n\n{text}", parse_mode="Markdown")
                count += 1
                await asyncio.sleep(0.05) # Rate limit protection
            except Exception:
                errors += 1
        await status_msg.edit_text(f"✅ Transmisión completada. Entregados: {count}. Fallos (Baneos/Bloqueos): {errors}.")
        context.user_data["state"] = None

    elif state == "WAIT_BAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = True
            await db.save()
            await update.message.reply_text(f"🚫 Esclavo `{text}` exiliado del sistema.")
        else: await update.message.reply_text("❌ UID no consta en los registros.")
        context.user_data["state"] = None

    elif state == "WAIT_UNBAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = False
            await db.save()
            await update.message.reply_text(f"🔓 Esclavo `{text}` rehabilitado.")
        else: await update.message.reply_text("❌ UID no consta.")
        context.user_data["state"] = None

    elif state == "WAIT_PTS_ID" and user.id == EmpireConfig.ADMIN_ID:
        context.user_data["target_id"] = text.strip()
        await update.message.reply_text(f"💰 Cuantifica la inyección de capital para `{text}`:")
        context.user_data["state"] = "WAIT_PTS_VAL"

    elif state == "WAIT_PTS_VAL" and user.id == EmpireConfig.ADMIN_ID:
        try:
            val = int(text)
            tid = context.user_data["target_id"]
            if tid in db.data["users"]:
                db.data["users"][tid]["points"] += val
                await db.log_transaction(tid, val, "Inyección Overlord")
                await update.message.reply_text(f"✅ Transferidos {val} pts a `{tid}`.")
                try: await context.bot.send_message(tid, f"🏦 El Soberano te ha transferido **{val} puntos**.")
                except: pass
            else: await update.message.reply_text("❌ UID inexistente.")
        except ValueError: await update.message.reply_text("❌ Formato numérico corrompido.")
        context.user_data["state"] = None

    elif state == "WAIT_CP_CODE" and user.id == EmpireConfig.ADMIN_ID:
        context.user_data["cp_code"] = text.upper().strip()
        await update.message.reply_text("🎫 ¿Nivel de acreditación? (FREE, PRO, ULTRA, GOD)")
        context.user_data["state"] = "WAIT_CP_PLAN"

    elif state == "WAIT_CP_PLAN" and user.id == EmpireConfig.ADMIN_ID:
        plan = text.upper().strip()
        if plan in EmpireConfig.PLANS:
            code = context.user_data["cp_code"]
            db.data["coupons"][code] = plan
            await db.save()
            await update.message.reply_text(f"🎫 Cupón forjado: `{code}` -> Nivel `{plan}`.")
        else: await update.message.reply_text("❌ Clase de rango no reconocida.")
        context.user_data["state"] = None

    elif state == "WAIT_PLAN_EDIT_ID" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            context.user_data["target_user_id"] = text
            await update.message.reply_text(f"🎭 Redefiniendo destino para `{text}`:", reply_markup=EmpireUI.plan_selector_admin())
        else: await update.message.reply_text("❌ Registro no hallado.")
        context.user_data["state"] = None

# =================================================================
# [8] SISTEMA NERVIOSO DE CALLBACKS (BOTONES INTERACTIVOS)
# =================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    uid_str = str(uid)
    data = q.data
    await q.answer()

    u_data = await db.get_user(q.from_user)

    # --- GESTIÓN DE TÓKENS Y MERCADO ---
    if data.startswith("buy_"):
        parts = data.split("_")
        plan = parts[1]
        days = int(parts[2])
        
        # Lógica de precio especial para 7 días
        multiplier = 6 if days == 7 else days
        price = EmpireConfig.ECONOMY[f"PRICE_{plan}_DAY"] * multiplier
        
        if u_data["points"] >= price:
            u_data["points"] -= price
            u_data["plan"] = plan
            current_expiry = u_data.get("plan_expiry")
            base_date = datetime.datetime.fromisoformat(current_expiry) if current_expiry else datetime.datetime.now()
            new_expiry = base_date + datetime.timedelta(days=days)
            u_data["plan_expiry"] = str(new_expiry)
            await db.log_transaction(uid_str, -price, f"Adquisición Rango {plan} x{days}d")
            await q.edit_message_text(f"✅ **TRANSACCIÓN VALIDADA.**\nBienvenido a la clase **{plan}**. Tus privilegios durarán hasta el `{new_expiry.date()}`.")
        else:
            await q.message.reply_text(f"❌ Capital insuficiente. Requiere {price} pts.")

    elif data == "market_crypto":
        # Simulación de trading rápido
        cost = 500
        if u_data["points"] >= cost:
            u_data["points"] -= cost
            win = random.choice([True, False])
            if win:
                profit = int(cost * random.uniform(1.2, 2.5))
                u_data["points"] += profit
                await q.message.reply_text(f"📈 **¡TRADING EXITOSO!** Invertiste 500 y retiraste {profit} pts.")
            else:
                await q.message.reply_text(f"📉 **CRASH DEL MERCADO.** Perdiste los 500 pts invertidos.")
            await db.save()
        else:
            await q.message.reply_text("❌ No tienes los 500 pts mínimos para invertir.")

    # --- RUTEO DE DESCARGAS MULTIMEDIA ---
    elif data.startswith("fmt_"):
        mode = data.split("_")[1]
        if mode == "back": return await q.edit_message_text("🎬 Selecciona formato:", reply_markup=EmpireUI.format_selector())
        context.user_data["active_fmt"] = mode
        if mode == "MP3": await finalize_download(update, context)
        else: await q.edit_message_text("🎥 Selecciona resolución óptica:", reply_markup=EmpireUI.quality_selector(u_data["plan"]))

    elif data.startswith("ql_"):
        context.user_data["active_qlty"] = data.split("_")[1]
        await finalize_download(update, context)

    # --- COMANDOS DEL ALTO MANDO OVERLORD ---
    elif data.startswith("adm_") and uid == EmpireConfig.ADMIN_ID:
        if data == "adm_list":
            users = db.data["users"]
            msg = "👥 **REGISTRO DE ESCLAVOS RECIENTES:**\n"
            for sid, d in list(users.items())[-15:]:
                status = "🚫" if d["is_banned"] else "✅"
                msg += f"• `{sid}` | {d['name']} | Lvl:{d['level']} | {d['plan']} | {status}\n"
            await q.message.reply_text(msg, parse_mode="Markdown")
        elif data == "adm_bc":
            await q.message.reply_text("📢 Dicta el mensaje para la propagación:"); context.user_data["state"] = "WAIT_BC"
        elif data == "adm_ban":
            await q.message.reply_text("🚫 ID a exiliar:"); context.user_data["state"] = "WAIT_BAN"
        elif data == "adm_unban":
            await q.message.reply_text("🔓 ID a perdonar:"); context.user_data["state"] = "WAIT_UNBAN"
        elif data == "adm_pts":
            await q.message.reply_text("💰 ID a fondear:"); context.user_data["state"] = "WAIT_PTS_ID"
        elif data == "adm_cp":
            await q.message.reply_text("🎫 Define la clave del cupón:"); context.user_data["state"] = "WAIT_CP_CODE"
        elif data == "adm_edit_plan":
            await q.message.reply_text("🎭 ID a reestructurar:"); context.user_data["state"] = "WAIT_PLAN_EDIT_ID"
        elif data == "adm_tickets":
            pending = [tid for tid, t in db.data["tickets"].items() if t["status"] == "OPEN"]
            await q.message.reply_text(f"🎫 Tienes {len(pending)} tickets pendientes de revisión.")
        elif data == "adm_backup":
            await db.save()
            await context.bot.send_document(uid, open(EmpireConfig.DATABASE_PATH, 'rb'), caption=f"💾 Master Vault Data Core - V80")
        elif data == "adm_clean":
            count = 0
            for f in os.listdir(EmpireConfig.BUFFER_DIR):
                try: os.remove(os.path.join(EmpireConfig.BUFFER_DIR, f)); count += 1
                except: pass
            await q.message.reply_text(f"🧹 Purgatorio vaciado: {count} espectros eliminados.")

    # --- CAMBIO DE PLAN ADMINISTRATIVO ---
    elif data.startswith("setplan_") and uid == EmpireConfig.ADMIN_ID:
        plan = data.split("_")[1]
        tid = context.user_data.get("target_user_id")
        if tid in db.data["users"]:
            db.data["users"][tid]["plan"] = plan
            u_data_target = db.data["users"][tid]
            expiry = datetime.datetime.now() + datetime.timedelta(days=365) if plan not in ["FREE", "GOD"] else None
            u_data_target["plan_expiry"] = str(expiry) if expiry else None
            await db.save()
            await q.edit_message_text(f"✅ Rango de `{tid}` reescrito a **{plan}**.")
            try: await context.bot.send_message(tid, f"👁️ El Soberano Ishak ha elevado tu existencia al rango **{plan}**.")
            except: pass
        context.user_data["target_user_id"] = None

    # --- CIERRE DE TICKETS ---
    elif data.startswith("tc_close_") and uid == EmpireConfig.ADMIN_ID:
        tid = data.replace("tc_close_", "")
        if tid in db.data["tickets"]:
            db.data["tickets"][tid]["status"] = "CLOSED"
            await db.save()
            user_ticket = db.data["tickets"][tid]["uid"]
            await q.edit_message_reply_markup(reply_markup=None)
            await q.message.reply_text(f"✅ Ticket {tid} clausurado.")
            try: await context.bot.send_message(user_ticket, f"✅ Tu ticket `{tid}` ha sido resuelto y cerrado por el Alto Mando.")
            except: pass

    elif data == "u_close":
        try: await q.message.delete()
        except: pass

# =================================================================
# [9] MOTOR DE DESCARGA ASÍNCRONA DE ALTO RENDIMIENTO
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
    limit = plan_info["limit_daily"]
    max_size = plan_info["max_file_mb"]

    if u_data["daily_downloads"][0] >= limit:
        return await q.edit_message_text(f"❌ Cuota de descargas excedida ({limit}). Mejora tu posición en el Mercado Negro.")

    msg = await q.edit_message_text(f"⚡ **SINCRONIZANDO TÚNEL QUANTUM...**\n`Formato: {fmt} | Óptica: {qlty}`\n*Prioridad de red: {plan_info['priority']}*")
    
    try:
        # Extracción y filtrado
        path, title, duration, f_size = await MediaEngine.run(url, fmt, qlty, uid_str, max_size)
        
        size_mb = f_size / (1024 * 1024)
        if size_mb > max_size:
            if os.path.exists(path): os.remove(path)
            return await msg.edit_text(f"❌ **SOBRECARGA:** El archivo ({size_mb:.1f}MB) excede tu límite de rango ({max_size}MB).")

        await msg.edit_text(f"📤 **CABLEANDO DATOS AL SATÉLITE IMPERIAL...**\n`Masa: {size_mb:.1f} MB`")
        
        # Envío asíncrono con lectura en trozos
        with open(path, 'rb') as f:
            lang_note = "\n🇪🇸 *Regla Override: Subtítulos/Audio en Español aplicados (Veo3).* " if "veo3" in url.lower() else ""
            cap = (
                f"✅ **{title[:60]}...**\n"
                f"⏱️ Tiempo: `{str(datetime.timedelta(seconds=duration))}`\n"
                f"💾 Masa: `{size_mb:.1f} MB`{lang_note}\n"
                f"⚡ Motor: `Ishak Omniversal V80`\n"
                f"👤 Operador: `{q.from_user.first_name}`"
            )
            
            # Timeout generoso para archivos grandes
            if fmt == "MP3": 
                await context.bot.send_audio(uid, f, caption=cap, parse_mode="Markdown", read_timeout=120, write_timeout=120)
            else: 
                await context.bot.send_video(uid, f, caption=cap, parse_mode="Markdown", read_timeout=300, write_timeout=300, supports_streaming=True)

        # Actualización de Estado Global
        u_data["daily_downloads"][0] += 1
        u_data["total_downloads"] += 1
        db.data["stats"]["total_downloads"] += 1
        db.data["stats"]["bytes_processed"] += f_size
        await db.save()
        
        # Revisión de Logros post-descarga
        asyncio.create_task(check_achievements(uid_str, update, context))
        
        # Limpieza de Purgatorio
        if os.path.exists(path): os.remove(path)
        await msg.delete()

    except Exception as e:
        logger.error(f"Falla crítica en flujo de extracción UID {uid}: {traceback.format_exc()}")
        err_msg = str(e)[:150]
        if "File is larger than max-filesize" in err_msg:
            err_msg = "Archivo excede tu límite de tamaño permitido."
        await msg.edit_text(f"❌ **ANOMALÍA EN EL TEJIDO DE DATOS:**\n`{err_msg}`")

# =================================================================
# [10] SERVIDOR DE COMUNICACIÓN EXTERNA E INTEGRACIONES (FLASK)
# =================================================================
web_app = Flask("IshakSaaS_API")

@web_app.route('/api/v1/status', methods=['GET'])
def api_status():
    s = db.data["stats"]
    return jsonify({
        "status": "SUPREME_CONTROL",
        "system_name": "ISHAK OMNIVERSAL SAAS",
        "version": EmpireConfig.VERSION,
        "metrics": {
            "citizens": s["total_users"],
            "extractions": s["total_downloads"],
            "terabytes_processed": round(s["bytes_processed"] / (1024**4), 4)
        },
        "creator": "Ishak Ezzahouani"
    })

def run_web():
    """Lanza el servidor local en un hilo separado."""
    # Ocultar banners de desarrollo de Flask
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    try: 
        port = int(os.getenv("PORT", 8080))
        web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e: 
        logger.error(f"Fallo iniciando API Externa: {e}")

# =================================================================
# [11] SECUENCIA DE IGNICIÓN PRINCIPAL
# =================================================================
async def setup_bot_commands(app: Application):
    """Establece los comandos en la UI de Telegram."""
    try:
        await app.bot.set_my_commands([
            ("start", "Iniciar conexión con el Imperio"),
            ("ayuda", "Manual de supervivencia"),
        ])
    except Exception: pass

async def post_init(app: Application):
    """Inyecta tareas en background una vez que el motor cuántico está en línea."""
    asyncio.create_task(db.backup_job())
    await setup_bot_commands(app)

def main():
    print("=" * 60)
    print(f"🚀 INICIANDO ISHAK EMPIRE V{EmpireConfig.VERSION}")
    print("⚙️ MODO DIOS ACTIVADO. PREPARANDO ALMAS...")
    print("=" * 60)
    
    # 1. Iniciar sub-hilos
    threading.Thread(target=run_web, daemon=True).start()
    
    # 2. Configurar motor de Telegram
    # Builder optimizado para soportar alta concurrencia
    application = (
        ApplicationBuilder()
        .token(EmpireConfig.TOKEN)
        .pool_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .connection_pool_size(1024)
        .post_init(post_init)
        .build()
    )
    
    # 3. Mapeo de Controladores
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # 4. Despliegue de red
    logger.info("🔥 OVERLORD EN LÍNEA. ESPERANDO DIRECTRICES...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Secuencia de apagado iniciada por el Soberano. Apagando motores...")
    except Exception as e:
        logger.critical(f"COLAPSO ESTRUCTURAL DEL SISTEMA: {traceback.format_exc()}")
        sys.exit(1)
