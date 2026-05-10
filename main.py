"""
██╗███████╗██╗  ██╗ █████╗ ██╗  ██╗    ██╗   ██╗███████╗ ██████╗  ██████╗
██║██╔════╝██║  ██║██╔══██╗██║ ██╔╝    ██║   ██║██╔════╝██╔═████╗██╔═████╗
██║███████╗███████║███████║█████╔╝     ██║   ██║███████╗██║██╔██║██║██╔██║
██║╚════██║██╔══██║██╔══██║██╔═██╗     ╚██╗ ██╔╝╚════██║████╔╝██║████╔╝██║
██║███████║██║  ██║██║  ██║██║  ██╗     ╚████╔╝ ███████║╚██████╔╝╚██████╔╝
╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝     ╚═══╝  ╚══════╝ ╚═════╝  ╚═════╝
================================================================================
SISTEMA: ISHAK HYPER-SAAS V500.0 - THE LEVIATHAN ULTRA MAX EDITION
VERSIÓN: 500.0.0-LEVIATHAN-ULTRA-MAX
PROPIETARIO: Ishak Ezzahouani | Director General | España | Edad: 18
ARQUITECTURA: Full Async • Shadow DB • Self-Healing • Multi-Tier Economy
NUEVO V500: Poker, Mines, Plinko, Dados, Planes Empresariales, Seguridad 2FA,
            Cola Inteligente, Mercado P2P, Guerra de Clanes, Admin Web Completo,
            Batch Downloads, Historial, Favoritos, Eventos Automáticos
================================================================================
"""

# ============================================================
# [0] BOOTSTRAP Y DEPENDENCIAS
# ============================================================
import os, sys, json, uuid, time, shutil, asyncio, logging
import datetime, traceback, subprocess, threading, platform
import random, re, math, hashlib, base64, copy, gc, html, string, csv, io
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum

def bootstrap_packages():
    packages = [
        'python-telegram-bot', 'yt-dlp', 'flask', 'flask-cors', 'requests',
        'psutil', 'Pillow', 'aiohttp', 'cryptography', 'qrcode', 'python-dotenv',
        'gTTS', 'pydantic', 'pydantic-settings', 'sentry-sdk', 'cachetools',
        'Flask-Limiter', 'apscheduler', 'pyotp', 'python-jose'
    ]
    for p in packages:
        try:
            __import__(p.replace('-', '_').replace('python_', ''))
            if p == 'yt-dlp':
                subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp", "--quiet"])
        except ImportError:
            print(f"📦 [BOOTSTRAP V500] Instalando: {p}...")
            if subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", p, "--quiet"]) != 0:
                print(f"❌ CRÍTICO: No se pudo instalar {p}. Abortando.")
                sys.exit(1)

bootstrap_packages()

import yt_dlp, requests, psutil, aiohttp, qrcode, pyotp
from dotenv import load_dotenv
from flask_cors import CORS
from gtts import gTTS
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet
from flask import Flask, jsonify, request, render_template_string, abort, Response, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, LabeledPrice,
    InputMediaPhoto, InputFile
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, PreCheckoutQueryHandler,
    ContextTypes, filters, Application
)

load_dotenv()

# ============================================================
# [1] CONFIGURACIÓN CENTRAL V500
# ============================================================
class AppSettings(BaseSettings):
    admin_id: int = Field(default=8398522835)
    telegram_token: str = Field(...)
    deploy_env: str = Field(default="production")
    port: int = Field(default=8080)
    redis_url: str = Field(default="redis://localhost:6379/0")
    use_redis: bool = Field(default=False)
    encryption_key: str = Field(default=Fernet.generate_key().decode())
    webhook_enabled: bool = Field(default=False)
    webhook_url: Optional[str] = Field(default=None)
    default_language: str = Field(default="es")
    alert_chat_id: Optional[int] = Field(default=None)
    alert_threshold_errors: int = Field(default=5)
    two_fa_enabled: bool = Field(default=True)
    max_batch_urls: int = Field(default=10)
    class Config:
        env_prefix = "ISHAK_"
        env_file = ".env"

settings = AppSettings()
fernet = Fernet(settings.encryption_key.encode() if isinstance(settings.encryption_key, str) else settings.encryption_key)

def encrypt_data(data: str) -> str: return fernet.encrypt(data.encode()).decode()
def decrypt_data(token: str) -> str: return fernet.decrypt(token.encode()).decode()

# ============================================================
# [2] LOGGING ESTRUCTURADO
# ============================================================
class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": record.levelname, "message": record.getMessage(),
            "module": record.module, "function": record.funcName,
            **({"exception": self.formatException(record.exc_info)} if record.exc_info else {})
        }, ensure_ascii=False)

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger("ISHAK_V500")

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0,
        integrations=[FlaskIntegration()], environment=settings.deploy_env)

# ============================================================
# [3] EMPIRE CONFIG V500 - PLANES EXPANDIDOS
# ============================================================
class EmpireConfig:
    ADMIN_ID   = settings.admin_id
    TOKEN      = settings.telegram_token
    VERSION    = "500.0.0-LEVIATHAN-ULTRA-MAX"

    if not TOKEN:
        print("❌ ISHAK_TELEGRAM_TOKEN no definido."); sys.exit(1)

    ROOT       = os.getcwd()
    VAULT_DIR  = os.path.join(ROOT, "empire_vault")
    BUFFER_DIR = os.path.join(ROOT, "download_buffer")
    LOGS_DIR   = os.path.join(ROOT, "system_logs")
    BACKUP_DIR = os.path.join(VAULT_DIR, "backups")
    EXPORT_DIR = os.path.join(VAULT_DIR, "exports")
    DATABASE_PATH = os.path.join(VAULT_DIR, "empire_v500.json")
    SHADOW_DB_PATH = os.path.join(VAULT_DIR, "empire_shadow_v500.json")
    QR_DIR  = os.path.join(BUFFER_DIR, "qrcodes")
    TTS_DIR = os.path.join(BUFFER_DIR, "tts_audio")

    # ── PLANES V500 ──────────────────────────────────────────
    PLANS = {
        "FREE": {
            "name": "🆓 CIUDADANO", "limit_daily": 3, "max_file_mb": 100,
            "resolutions": ["360p", "720p"], "speed": "Básica",
            "priority": 0, "max_duration_min": 10, "batch_urls": 0,
            "price_weekly_stars": 0, "price_monthly_stars": 0, "price_annual_stars": 0,
            "color": "⬜", "casino_multiplier": 1.0
        },
        "STARTER": {
            "name": "🌱 INICIADO", "limit_daily": 15, "max_file_mb": 300,
            "resolutions": ["360p", "720p", "1080p"], "speed": "Estándar (5MB/s)",
            "priority": 1, "max_duration_min": 30, "batch_urls": 2,
            "price_weekly_stars": 25, "price_monthly_stars": 80, "price_annual_stars": 700,
            "color": "🟩", "casino_multiplier": 1.1
        },
        "BASIC": {
            "name": "💠 BÁSICO", "limit_daily": 30, "max_file_mb": 600,
            "resolutions": ["360p", "720p", "1080p"], "speed": "Media (10MB/s)",
            "priority": 2, "max_duration_min": 60, "batch_urls": 3,
            "price_weekly_stars": 50, "price_monthly_stars": 150, "price_annual_stars": 1300,
            "color": "🔷", "casino_multiplier": 1.2
        },
        "PRO": {
            "name": "💎 ÉLITE PRO", "limit_daily": 150, "max_file_mb": 1500,
            "resolutions": ["360p", "720p", "1080p", "1440p"], "speed": "Alta (25MB/s)",
            "priority": 3, "max_duration_min": 120, "batch_urls": 5,
            "price_weekly_stars": 100, "price_monthly_stars": 250, "price_annual_stars": 2200,
            "color": "💎", "casino_multiplier": 1.5
        },
        "ULTRA": {
            "name": "🔥 SOBERANO ULTRA", "limit_daily": 500, "max_file_mb": 10000,
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K"],
            "speed": "Instantánea (100MB/s)", "priority": 4,
            "max_duration_min": 600, "batch_urls": 8,
            "price_weekly_stars": 200, "price_monthly_stars": 500, "price_annual_stars": 4500,
            "color": "🔥", "casino_multiplier": 2.0
        },
        "ENTERPRISE": {
            "name": "🏢 CORPORATIVO ENTERPRISE", "limit_daily": 2000, "max_file_mb": 50000,
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K", "Original"],
            "speed": "CDN Dedicado", "priority": 5,
            "max_duration_min": 1200, "batch_urls": 10,
            "price_weekly_stars": 500, "price_monthly_stars": 1200, "price_annual_stars": 10000,
            "color": "🏢", "casino_multiplier": 2.5
        },
        "GOD": {
            "name": "👁️ OMNIPRESENTE GOD", "limit_daily": float('inf'), "max_file_mb": float('inf'),
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K", "Original"],
            "speed": "Quantum (Sin límite)", "priority": 6,
            "max_duration_min": float('inf'), "batch_urls": 999,
            "price_weekly_stars": 0, "price_monthly_stars": 0, "price_annual_stars": 0,
            "color": "👁️", "casino_multiplier": 3.0
        }
    }

    # ── ECONOMÍA V500 ─────────────────────────────────────────
    ECONOMY = {
        "DAILY_REWARD_MIN": 200, "DAILY_REWARD_MAX": 600,
        "REF_REWARD": 2000, "REF_TIER2": 500, "REF_TIER3": 100,
        "XP_PER_DOWNLOAD": 30, "XP_PER_MESSAGE": 3,
        "STREAK_BONUS_DAY": 150, "MAX_STREAK_BONUS": 3000,
        "AFFILIATE_T1_PCT": 0.12, "AFFILIATE_T2_PCT": 0.06, "AFFILIATE_T3_PCT": 0.02,
        "WEEKLY_TOURNAMENT_ENTRY": 500,
        "P2P_MARKET_FEE": 0.05,         # 5% comisión en ventas P2P
        "CLAN_WAR_REWARD_TOP": 25000,
        "GIFT_CARD_VALUES": [500, 1000, 2500, 5000, 10000],
        "DAILY_SHOP_DISCOUNT": 0.30,     # 30% descuento en tienda rotativa
    }

    # ── PAQUETES STARS V500 ───────────────────────────────────
    STARS_PACKAGES = {
        # Puntos
        "PTS_MICRO":  {"name": "🪙 2,000 Puntos",    "type": "points",  "stars": 20,   "value": 2000},
        "PTS_SMALL":  {"name": "💰 5,000 Puntos",    "type": "points",  "stars": 45,   "value": 5000},
        "PTS_MEDIUM": {"name": "💎 15,000 Puntos",   "type": "points",  "stars": 120,  "value": 15000},
        "PTS_LARGE":  {"name": "🏆 50,000 Puntos",   "type": "points",  "stars": 350,  "value": 50000},
        "PTS_WHALE":  {"name": "🐋 200,000 Puntos",  "type": "points",  "stars": 1200, "value": 200000},
        # Suscripciones semanales
        "SUB_STARTER_W": {"name": "🌱 STARTER Semanal",    "type": "sub_week", "stars": 25,   "value": "STARTER"},
        "SUB_BASIC_W":   {"name": "💠 BÁSICO Semanal",     "type": "sub_week", "stars": 50,   "value": "BASIC"},
        "SUB_PRO_W":     {"name": "💎 PRO Semanal",        "type": "sub_week", "stars": 100,  "value": "PRO"},
        "SUB_ULTRA_W":   {"name": "🔥 ULTRA Semanal",      "type": "sub_week", "stars": 200,  "value": "ULTRA"},
        # Suscripciones mensuales
        "SUB_STARTER_M": {"name": "🌱 STARTER 30 días",   "type": "sub_month","stars": 80,   "value": "STARTER"},
        "SUB_BASIC_M":   {"name": "💠 BÁSICO 30 días",    "type": "sub_month","stars": 150,  "value": "BASIC"},
        "SUB_PRO_M":     {"name": "💎 PRO 30 días",       "type": "sub_month","stars": 250,  "value": "PRO"},
        "SUB_ULTRA_M":   {"name": "🔥 ULTRA 30 días",     "type": "sub_month","stars": 500,  "value": "ULTRA"},
        "SUB_ENT_M":     {"name": "🏢 ENTERPRISE 30 días","type": "sub_month","stars": 1200, "value": "ENTERPRISE"},
        # Suscripciones anuales (ahorro 30%)
        "SUB_PRO_Y":     {"name": "💎 PRO ANUAL (Ahorra 30%)",  "type": "sub_year","stars": 2200, "value": "PRO"},
        "SUB_ULTRA_Y":   {"name": "🔥 ULTRA ANUAL (Ahorra 30%)","type": "sub_year","stars": 4500, "value": "ULTRA"},
        # Especiales
        "VIP_MONTH":     {"name": "🥂 Sala VIP 30 días",  "type": "vip",      "stars": 150,  "value": "VIP"},
        "GIFT_500":      {"name": "🎁 Tarjeta 500 pts",   "type": "gift_card","stars": 10,   "value": 500},
        "GIFT_2500":     {"name": "🎁 Tarjeta 2,500 pts", "type": "gift_card","stars": 40,   "value": 2500},
        "GIFT_10000":    {"name": "🎁 Tarjeta 10,000 pts","type": "gift_card","stars": 150,  "value": 10000},
        "BOOST_XP_W":    {"name": "🧪 XP Boost x3 Semanal","type":"boost",   "stars": 60,   "value": "xp3_week"},
        "CLAN_SLOT":     {"name": "🛡️ Slot Extra en Clan", "type":"clan_slot","stars": 80,   "value": 5},
    }

    # ── TIENDA DE ÍTEMS ───────────────────────────────────────
    SHOP_ITEMS = {
        "XP_BOOST_X2":   {"name": "🧪 XP x2 (24h)",        "price": 5000,  "desc": "Doble XP por 24 horas."},
        "XP_BOOST_X3":   {"name": "🔬 XP x3 (24h)",        "price": 12000, "desc": "Triple XP (solo ULTRA+)."},
        "BYPASS_QUEUE":  {"name": "🚀 Bypass Cola",         "price": 3000,  "desc": "Descarga prioritaria."},
        "CLAN_TICKET":   {"name": "🛡️ Fundar Facción",      "price": 10000, "desc": "Crea tu propio clan."},
        "RENAME_CARD":   {"name": "📝 Cambio Apodo",        "price": 2000,  "desc": "Cambia tu nombre."},
        "SHIELD":        {"name": "🛡️ Escudo Anti-Robo 24h","price": 4000,  "desc": "Nadie puede robarte puntos."},
        "LOOT_BOX":      {"name": "🎁 Caja Loot Aleatoria", "price": 1500,  "desc": "Premio aleatorio: 500-50,000 pts."},
        "CLAN_WAR_PASS": {"name": "⚔️ Pase de Guerra",      "price": 8000,  "desc": "Participa en Guerra de Clanes."},
        "EXTRA_DL":      {"name": "➕ +10 Descargas Hoy",   "price": 2500,  "desc": "10 extracciones adicionales hoy."},
        "PRESTIGE_TOKEN":{"name": "👑 Token Prestigio",     "price": 50000, "desc": "Símbolo de estatus máximo."},
        "LUCK_CHARM":    {"name": "🍀 Amuleto Suerte 24h",  "price": 6000,  "desc": "+15% ganancias casino 24h."},
        "DOUBLE_REF":    {"name": "🔗 Referido x2 48h",     "price": 7000,  "desc": "Doble recompensa por referidos 48h."},
    }

    # ── LOGROS V500 ───────────────────────────────────────────
    ACHIEVEMENTS = {
        "FIRST_BLOOD":    {"name": "Primera Sangre",     "desc": "Primera descarga.",            "reward": 500},
        "CENTURION":      {"name": "Centurión",          "desc": "100 descargas.",               "reward": 5000},
        "DOWNLOADER_500": {"name": "Extractor Leyenda",  "desc": "500 descargas.",               "reward": 25000},
        "BATCH_MASTER":   {"name": "Maestro Batch",      "desc": "10 descargas en lote.",        "reward": 3000},
        "INFLUENCER":     {"name": "Influencer",         "desc": "10 referidos.",                "reward": 10000},
        "MEGA_REF":       {"name": "Mega Referido",      "desc": "50 referidos.",                "reward": 50000},
        "GAMBLER":        {"name": "Ludópata Imperial",  "desc": "100 partidas casino.",         "reward": 2000},
        "GUILD_MASTER":   {"name": "Maestro de Gremio",  "desc": "Funda una Facción.",           "reward": 3000},
        "INVESTOR":       {"name": "Inversor Privado",   "desc": "Primera compra Stars.",        "reward": 5000},
        "WHALE":          {"name": "Ballena Cripto",     "desc": "100,000 pts en Stars.",        "reward": 15000},
        "CARD_SHARK":     {"name": "Tiburón de Cartas",  "desc": "10 victorias Blackjack.",      "reward": 3000},
        "MINES_MASTER":   {"name": "Maestro de Minas",   "desc": "20 victorias en Mines.",       "reward": 4000},
        "PLINKO_KING":    {"name": "Rey del Plinko",     "desc": "Jackpot en Plinko.",           "reward": 5000},
        "POKER_PRO":      {"name": "Profesional Poker",  "desc": "50 manos ganadas en Poker.",   "reward": 8000},
        "STREAK_WEEK":    {"name": "Racha Semanal",      "desc": "7 días seguidos.",             "reward": 5000},
        "STREAK_MONTH":   {"name": "Racha Mensual",      "desc": "30 días seguidos.",            "reward": 30000},
        "AFFILIATE_BOSS": {"name": "Jefe Afiliado",      "desc": "10,000 pts en comisiones.",    "reward": 8000},
        "TOURNAMENT_WIN": {"name": "Campeón Imperial",   "desc": "Gana un torneo.",              "reward": 20000},
        "VIP_MEMBER":     {"name": "VIP Exclusivo",      "desc": "Accede a la Sala VIP.",        "reward": 2000},
        "CLAN_WAR_WIN":   {"name": "Guerrero Victorioso","desc": "Gana una guerra de clanes.",   "reward": 10000},
        "MARKET_BARON":   {"name": "Barón del Mercado",  "desc": "10 ventas en mercado P2P.",    "reward": 5000},
        "HACKER":         {"name": "Cyber-Hacker",       "desc": "Genera API Key.",              "reward": 1000},
        "TWO_FA_GUARDIAN":{"name": "Guardián 2FA",       "desc": "Activa 2FA.",                  "reward": 1500},
        "PRESTIGE":       {"name": "Símbolo de Prestigio","desc": "Compra Token Prestigio.",     "reward": 100000},
    }

    # ── IDIOMAS ───────────────────────────────────────────────
    LANGUAGES = {
        "es": {"welcome": "👑 **BIENVENIDO AL IMPERIO V500**\nInfraestructura blindada. Sin límites."},
        "en": {"welcome": "👑 **WELCOME TO THE EMPIRE V500**\nFortified infrastructure. No limits."},
        "fr": {"welcome": "👑 **BIENVENUE À L'EMPIRE V500**\nInfrastructure blindée. Sans limites."},
        "ar": {"welcome": "👑 **مرحبًا في الإمبراطورية V500**\nبنية محصنة. بلا حدود."},
        "de": {"welcome": "👑 **WILLKOMMEN IM IMPERIUM V500**\nGesicherte Infrastruktur. Keine Grenzen."},
        "it": {"welcome": "👑 **BENVENUTO ALL'IMPERO V500**\nInfrastruttura blindata. Nessun limite."},
    }

    @classmethod
    def init_filesystem(cls):
        for d in [cls.VAULT_DIR, cls.BUFFER_DIR, cls.LOGS_DIR, cls.BACKUP_DIR,
                  cls.QR_DIR, cls.TTS_DIR, cls.EXPORT_DIR]:
            os.makedirs(d, exist_ok=True)

EmpireConfig.init_filesystem()

# Añadir handler de logs estructurados
json_handler = logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "structured_v500.jsonl"), encoding='utf-8')
json_handler.setFormatter(JsonFormatter())
logger.addHandler(json_handler)
file_handler = logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "audit_v500.log"), encoding='utf-8')
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

# ============================================================
# [4] AUDITORÍA Y ALERTAS
# ============================================================
class AuditLogger:
    def __init__(self):
        self.log_file = os.path.join(EmpireConfig.LOGS_DIR, "audit_v500.jsonl")

    def log(self, action: str, user_id=None, details: Dict = None, severity: str = "INFO"):
        entry = {"timestamp": datetime.datetime.utcnow().isoformat(), "action": action,
                 "user_id": user_id, "details": details or {}, "severity": severity, "pid": os.getpid()}
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    def export_csv(self, limit: int = 1000) -> str:
        """Exporta los últimos N logs a CSV."""
        path = os.path.join(EmpireConfig.EXPORT_DIR, f"audit_{datetime.date.today()}.csv")
        rows = []
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try: rows.append(json.loads(line))
                    except: pass
        rows = rows[-limit:]
        with open(path, 'w', newline='', encoding='utf-8') as f:
            if rows:
                w = csv.DictWriter(f, fieldnames=rows[0].keys())
                w.writeheader(); w.writerows(rows)
        return path

audit_logger = AuditLogger()

class AlertSystem:
    def __init__(self):
        self.error_count = 0
        self.last_reset  = time.time()
        self.bot_ref     = None  # se inyecta al arrancar

    def track_error(self, msg: str = ""):
        now = time.time()
        if now - self.last_reset > 60:
            self.error_count = 0; self.last_reset = now
        self.error_count += 1
        if self.error_count >= settings.alert_threshold_errors:
            logger.critical(f"🚨 ALERTA SISTEMA: {self.error_count} errores/min. {msg}")
            audit_logger.log("SYSTEM_ALERT", details={"count": self.error_count, "msg": msg}, severity="CRITICAL")

alert_system = AlertSystem()

# ============================================================
# [5] SEGURIDAD V500 — Rate Limit, Captcha, 2FA, IP Blacklist
# ============================================================
class SecurityCoreV500:
    def __init__(self):
        self.spam_cache      = {}       # uid -> (timestamp, count)
        self.captcha_cache   = {}       # uid -> expected_answer
        self.anomaly_cache   = {}       # uid -> (last_text, time, count)
        self.ip_blacklist    = set()    # IPs bloqueadas
        self.session_log     = {}       # uid -> [session_entries]
        self.login_attempts  = {}       # uid -> (count, last_time)
        self.blocked_ips     = {}       # ip -> block_until
        self.totp_secrets    = {}       # uid -> totp_secret (in-memory cache)

    # ── Rate limiting ──────────────────────────────────────
    def rate_limit(self, uid: int, limit: int = 5, window: float = 3.0) -> bool:
        now = time.time()
        if uid in self.spam_cache:
            last, count = self.spam_cache[uid]
            if now - last < window:
                count += 1
                self.spam_cache[uid] = (now, count)
                if count > limit:
                    audit_logger.log("RATE_LIMIT", user_id=uid, severity="WARNING")
                    return True
            else:
                self.spam_cache[uid] = (now, 1)
        else:
            self.spam_cache[uid] = (now, 1)
        return False

    # ── Anomaly detection ──────────────────────────────────
    def check_anomaly(self, uid: int, text: str) -> bool:
        now = time.time()
        if uid in self.anomaly_cache:
            last_text, last_time, count = self.anomaly_cache[uid]
            if text == last_text and (now - last_time < 2):
                count += 1
                self.anomaly_cache[uid] = (text, now, count)
                return count > 5
            else:
                self.anomaly_cache[uid] = (text, now, 1)
        else:
            self.anomaly_cache[uid] = (text, now, 1)
        return False

    # ── Captcha matemático ────────────────────────────────
    def generate_captcha(self, uid: int) -> str:
        ops = ['+', '-', '*']
        a, b = random.randint(10, 99), random.randint(2, 19)
        op = random.choice(ops)
        ans = eval(f"{a}{op}{b}")
        self.captcha_cache[uid] = int(ans)
        return f"🔐 CAPTCHA: `{a} {op} {b} = ?`"

    def verify_captcha(self, uid: int, text: str) -> bool:
        try:
            if uid in self.captcha_cache and int(text.strip()) == self.captcha_cache[uid]:
                del self.captcha_cache[uid]; return True
        except: pass
        return False

    # ── 2FA con TOTP ──────────────────────────────────────
    def generate_2fa_secret(self, uid: str) -> Tuple[str, str]:
        """Genera un secreto TOTP y devuelve (secret, otpauth_uri)."""
        secret = pyotp.random_base32()
        totp   = pyotp.TOTP(secret)
        uri    = totp.provisioning_uri(name=f"User_{uid}", issuer_name="IshakEmpireV500")
        self.totp_secrets[uid] = secret
        return secret, uri

    def verify_2fa(self, uid: str, code: str, stored_secret: str) -> bool:
        totp = pyotp.TOTP(stored_secret)
        return totp.verify(code, valid_window=1)

    # ── Blacklist IPs ─────────────────────────────────────
    def block_ip(self, ip: str, duration_min: int = 60):
        self.blocked_ips[ip] = time.time() + duration_min * 60
        self.ip_blacklist.add(ip)
        audit_logger.log("IP_BLOCKED", details={"ip": ip, "duration_min": duration_min}, severity="WARNING")

    def is_ip_blocked(self, ip: str) -> bool:
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]: return True
            del self.blocked_ips[ip]; self.ip_blacklist.discard(ip)
        return False

    # ── Registro de sesiones ──────────────────────────────
    def log_session(self, uid: str, action: str, meta: dict = None):
        entry = {"action": action, "time": datetime.datetime.utcnow().isoformat(), "meta": meta or {}}
        if uid not in self.session_log: self.session_log[uid] = []
        self.session_log[uid].append(entry)
        if len(self.session_log[uid]) > 50: self.session_log[uid].pop(0)

    def get_session_log(self, uid: str) -> List[dict]:
        return self.session_log.get(uid, [])

    # ── Sanitización ──────────────────────────────────────
    @staticmethod
    def sanitize_text(text: str, max_len: int = 1000) -> str:
        if not text: return ""
        return html.escape(re.sub(r'\.\./|\.\.\\', '', text))[:max_len]

    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        if not url: return None
        url = url.strip()
        if not re.match(r'^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+$', url): return None
        if re.search(r'\.\./|\.\.\\', url): return None
        return url

    @staticmethod
    def validate_username(username: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9_]{3,32}$', username)) if username else False

sec = SecurityCoreV500()

# ============================================================
# [6] REDIS CACHE
# ============================================================
class RedisCache:
    def __init__(self):
        self._mem = {}
        self._redis = None
        if settings.use_redis:
            try:
                import redis
                self._redis = redis.from_url(settings.redis_url, decode_responses=True)
                self._redis.ping(); logger.info("✅ Redis conectado.")
            except Exception as e:
                logger.warning(f"Redis no disponible ({e}), usando memoria.")
                self._redis = None

    def get(self, key: str):
        if self._redis:
            v = self._redis.get(key); return json.loads(v) if v else None
        return self._mem.get(key)

    def set(self, key: str, value, ttl: int = 3600):
        if self._redis: self._redis.setex(key, ttl, json.dumps(value))
        else: self._mem[key] = value

    def delete(self, key: str):
        if self._redis: self._redis.delete(key)
        self._mem.pop(key, None)

    def exists(self, key: str) -> bool:
        if self._redis: return bool(self._redis.exists(key))
        return key in self._mem

cache = RedisCache()
METADATA_CACHE: Dict[str, dict] = {}

# ============================================================
# [7] BASE DE DATOS V500 — NOSQL + SHADOW + SELF-HEALING
# ============================================================
API_RATE_LIMITS: Dict = {}

class EmpireDatabase:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.data  = self._default_structure()
        self.sync_load()

    def _default_structure(self) -> dict:
        return {
            "users": {}, "coupons": {}, "blacklist": [],
            "factions": {}, "transactions": [], "tickets": {},
            "b2b_api_keys": {}, "p2p_market": [],
            "clan_wars": {}, "events": [],
            "market_stats": {
                "crypto_value": 150.0, "trend": "up",
                "history": [], "volume_24h": 0
            },
            "stats": {
                "total_downloads": 0, "total_users": 0, "bytes_processed": 0,
                "boot_time": str(datetime.datetime.now()), "commands_executed": 0,
                "stars_revenue": 0, "fraud_attempts_blocked": 0,
                "casino_spins": 0, "self_healing_fixes": 0,
                "affiliate_payouts": 0, "gift_cards_sold": 0,
                "tournament_prize_pool": 0, "p2p_volume": 0,
                "batch_downloads": 0, "clan_wars_total": 0,
            },
            "system": {
                "maint_mode": False,
                "global_welcome": EmpireConfig.LANGUAGES["es"]["welcome"],
                "tournament": {"active": False, "end_time": None, "prize_pool": 0,
                               "participants": {}, "winners": []},
                "clan_war": {"active": False, "end_time": None, "factions": [],
                             "scores": {}, "prize": 25000},
                "daily_shop": {"items": [], "date": None},
                "vip_group_id": None,
                "announcement_channel": None,
                "scheduled_events": [],
            },
            "leaderboard_cache": {"top_points": [], "top_downloads": [], "updated": None},
        }

    # ── DB I/O ─────────────────────────────────────────────
    def _auto_repair(self):
        if not os.path.exists(EmpireConfig.DATABASE_PATH): return
        try:
            with open(EmpireConfig.DATABASE_PATH, 'r', encoding='utf-8') as f:
                json.load(f)
        except:
            logger.critical("⚠️ DB PRINCIPAL CORRUPTA. Restaurando desde shadow...")
            if os.path.exists(EmpireConfig.SHADOW_DB_PATH):
                shutil.copy2(EmpireConfig.SHADOW_DB_PATH, EmpireConfig.DATABASE_PATH)
                audit_logger.log("DB_AUTO_REPAIR", severity="WARNING")
            else:
                logger.critical("❌ Shadow DB inexistente. Pérdida de datos posible.")

    def sync_load(self):
        self._auto_repair()
        for path in [EmpireConfig.DATABASE_PATH, EmpireConfig.SHADOW_DB_PATH]:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self._merge(self.data, json.load(f)); return
                except: pass

    def _merge(self, base: dict, saved: dict):
        for k, v in saved.items():
            if isinstance(v, dict) and k in base and isinstance(base[k], dict):
                self._merge(base[k], v)
            else:
                base[k] = v

    def _write(self, data_copy: dict):
        for path in [EmpireConfig.DATABASE_PATH, EmpireConfig.SHADOW_DB_PATH]:
            tmp = path + ".tmp"
            try:
                with open(tmp, 'w', encoding='utf-8') as f:
                    json.dump(data_copy, f, indent=2, ensure_ascii=False)
                if os.path.getsize(tmp) > 0:
                    os.replace(tmp, path)
            except Exception as e:
                logger.error(f"Error escribiendo DB {path}: {e}")

    async def save(self):
        async with self._lock:
            await self._save_nolock()

    async def _save_nolock(self):
        try:
            data_copy = copy.deepcopy(self.data)
            await asyncio.to_thread(self._write, data_copy)
        except Exception as e:
            logger.error(f"Error en save: {e}"); alert_system.track_error()

    # ── Gestión de puntos ─────────────────────────────────
    async def add_points(self, uid: str, amount: int):
        async with self._lock:
            if uid in self.data["users"]:
                self.data["users"][uid]["points"] += amount
                await self._save_nolock()

    async def deduct_points(self, uid: str, amount: int) -> bool:
        async with self._lock:
            u = self.data["users"].get(uid)
            if u and u["points"] >= amount:
                u["points"] -= amount
                await self._save_nolock(); return True
            return False

    # ── Registro de transacciones ─────────────────────────
    async def log_tx(self, uid: str, amount: int, desc: str):
        async with self._lock:
            self.data["transactions"].append({
                "uid": uid, "amount": amount, "desc": desc,
                "date": str(datetime.datetime.now())})
            if len(self.data["transactions"]) > 10000:
                self.data["transactions"] = self.data["transactions"][-8000:]
            await self._save_nolock()

    # ── GET / CREATE USER ─────────────────────────────────
    async def get_user(self, user_obj, referrer_id: str = None) -> Tuple[dict, bool]:
        uid = str(user_obj.id)
        ref_rewarded = False
        async with self._lock:
            is_new = uid not in self.data["users"]
            if is_new:
                self.data["users"][uid] = self._new_user(user_obj)
                self.data["stats"]["total_users"] += 1
                ref_rewarded = await self._process_referral(uid, referrer_id)

            u = self.data["users"][uid]
            today = str(datetime.date.today())
            changed = False

            # Reset diario
            if u["daily_downloads"][1] != today:
                u["daily_downloads"] = [0, today]
                u["bounties"] = self._gen_bounties()
                changed = True

            # Expiración de plan
            for field in ["plan_expiry", "vip_expiry"]:
                if u.get(field):
                    try:
                        if datetime.datetime.now() > datetime.datetime.fromisoformat(u[field]):
                            if field == "plan_expiry": u["plan"] = "FREE"; u["plan_expiry"] = None
                            else: u["vip_expiry"] = None
                            changed = True
                    except: u[field] = None; changed = True

            # Expiración de buffs
            if u["active_buffs"].get("buff_expiry"):
                try:
                    if datetime.datetime.now() > datetime.datetime.fromisoformat(u["active_buffs"]["buff_expiry"]):
                        u["active_buffs"] = {"xp_multiplier": 1.0, "buff_expiry": None, "luck_bonus": 0}
                        changed = True
                except: u["active_buffs"] = {"xp_multiplier": 1.0, "buff_expiry": None, "luck_bonus": 0}; changed = True

            if changed or is_new: await self._save_nolock()
        return u, ref_rewarded

    def _new_user(self, user_obj) -> dict:
        uid = str(user_obj.id)
        return {
            "id": user_obj.id,
            "name": sec.sanitize_text(user_obj.first_name or "Usuario", 50),
            "username": user_obj.username,
            "plan": "GOD" if user_obj.id == EmpireConfig.ADMIN_ID else "FREE",
            "plan_expiry": None,
            "points": 2000, "level": 1, "xp": 0,
            "crypto_balance": 0.0,
            "total_downloads": 0,
            "daily_downloads": [0, str(datetime.date.today())],
            "extra_downloads_today": 0,
            "download_history": [],      # [{url, title, date, format}]
            "favorites": [],             # [url]
            "batch_queue": [],           # [{url, fmt, quality, status}]
            "referrals": 0, "referred_by": None,
            "referrals_tier2": [], "referrals_tier3": [],
            "achievements": [], "inventory": {k: 0 for k in EmpireConfig.SHOP_ITEMS},
            "active_buffs": {"xp_multiplier": 1.0, "buff_expiry": None, "luck_bonus": 0},
            "settings": {
                "watermark": None, "auto_transcribe": False,
                "ghost_mode": False, "send_as_doc": False,
                "theme": "dark", "language": settings.default_language,
                "notifications_enabled": True, "auto_dl_best": False,
            },
            "security": {
                "two_fa_enabled": False, "two_fa_secret": None,
                "two_fa_verified": False, "login_history": [],
                "trusted_ips": [],
            },
            "faction": None, "joined": str(datetime.date.today()),
            "is_banned": False, "ban_reason": None,
            "captcha_solved": False, "fraud_warnings": 0,
            "stats": {
                "casino_played": 0, "bounties_done": 0, "stars_spent": 0,
                "blackjack_wins": 0, "mines_wins": 0, "poker_wins": 0,
                "plinko_jackpots": 0, "p2p_sales": 0, "p2p_purchases": 0,
            },
            "last_daily": None, "api_key": None,
            "bounties": self._gen_bounties(),
            "notification_queue": [],
            "streak": 0, "last_streak_date": None,
            "affiliate_earnings": 0,
            "vip_expiry": None,
            "gift_cards_owned": [],
            "tournament_score": 0,
            "total_spent_stars": 0,
            "prestige_level": 0,
            "poker_hand": None,          # estado mano activa de poker
            "mines_state": None,         # estado juego mines activo
            "rename_pending": False,
        }

    def _gen_bounties(self) -> list:
        pool = [
            {"id": "dl_3",     "desc": "Extrae 3 archivos",          "target": 3,  "progress": 0, "reward": 600,  "done": False},
            {"id": "dl_10",    "desc": "Extrae 10 archivos",         "target": 10, "progress": 0, "reward": 2500, "done": False},
            {"id": "casino_5", "desc": "Juega 5 veces al casino",    "target": 5,  "progress": 0, "reward": 900,  "done": False},
            {"id": "casino_20","desc": "Juega 20 veces al casino",   "target": 20, "progress": 0, "reward": 4000, "done": False},
            {"id": "share_1",  "desc": "Invita a 1 amigo",           "target": 1,  "progress": 0, "reward": 1500, "done": False},
            {"id": "batch_1",  "desc": "Usa modo lote 1 vez",        "target": 1,  "progress": 0, "reward": 800,  "done": False},
        ]
        return random.sample(pool, min(4, len(pool)))

    async def _process_referral(self, uid: str, referrer_id: str) -> bool:
        if not referrer_id or referrer_id == uid or referrer_id not in self.data["users"]:
            return False
        r1 = self.data["users"][referrer_id]
        bonus = EmpireConfig.ECONOMY["REF_REWARD"]
        if r1.get("inventory", {}).get("DOUBLE_REF", 0) > 0: bonus *= 2
        r1["points"] += bonus; r1["referrals"] = r1.get("referrals", 0) + 1
        self.data["users"][uid]["referred_by"] = referrer_id
        self.data["transactions"].append({"uid": referrer_id, "amount": bonus, "desc": f"Referido T1 ({uid})", "date": str(datetime.datetime.now())})
        # Tier 2
        t2 = r1.get("referred_by")
        if t2 and t2 in self.data["users"]:
            t2_bonus = EmpireConfig.ECONOMY["REF_TIER2"]
            self.data["users"][t2]["points"] += t2_bonus
            self.data["users"][t2].setdefault("referrals_tier2", []).append(uid)
            self.data["users"][t2]["affiliate_earnings"] = self.data["users"][t2].get("affiliate_earnings", 0) + t2_bonus
            self.data["transactions"].append({"uid": t2, "amount": t2_bonus, "desc": f"Referido T2 ({uid})", "date": str(datetime.datetime.now())})
            # Tier 3
            t3 = self.data["users"][t2].get("referred_by")
            if t3 and t3 in self.data["users"]:
                t3_bonus = EmpireConfig.ECONOMY["REF_TIER3"]
                self.data["users"][t3]["points"] += t3_bonus
                self.data["users"][t3].setdefault("referrals_tier3", []).append(uid)
                self.data["transactions"].append({"uid": t3, "amount": t3_bonus, "desc": f"Referido T3 ({uid})", "date": str(datetime.datetime.now())})
        return True

    # ── XP y niveles ──────────────────────────────────────
    async def add_xp(self, uid: str, amount: int) -> Tuple[bool, int]:
        async with self._lock:
            u = self.data["users"][uid]
            multi = u["active_buffs"]["xp_multiplier"]
            if u.get("faction") and u["faction"] in self.data["factions"]:
                multi += self.data["factions"][u["faction"]].get("level", 1) * 0.05
            u["xp"] += int(amount * multi)
            xp_needed = u["level"] * 120
            leveled = False
            while u["xp"] >= xp_needed:
                u["xp"] -= xp_needed; u["level"] += 1
                u["points"] += u["level"] * 150; xp_needed = u["level"] * 120; leveled = True
            await self._save_nolock()
            return leveled, u["level"]

    # ── Misiones ─────────────────────────────────────────
    async def update_bounty(self, uid: str, bounty_id: str, amount: int = 1):
        async with self._lock:
            u = self.data["users"].get(uid)
            if not u: return None
            for b in u.get("bounties", []):
                if b["id"] == bounty_id and not b["done"]:
                    b["progress"] += amount
                    if b["progress"] >= b["target"]:
                        b["done"] = True; u["points"] += b["reward"]
                        u["stats"]["bounties_done"] += 1
                        await self._save_nolock(); return b
            return None

    # ── Crypto ───────────────────────────────────────────
    async def trade_crypto(self, uid: str, amount_pts: int, buy: bool) -> Tuple[bool, str]:
        async with self._lock:
            u = self.data["users"].get(uid)
            if not u: return False, "Usuario no encontrado."
            price = self.data["market_stats"]["crypto_value"]
            if buy:
                if u["points"] < amount_pts: return False, "Fondos insuficientes."
                coins = amount_pts / price
                u["points"] -= amount_pts; u["crypto_balance"] += coins
                self.data["market_stats"]["volume_24h"] += amount_pts
                msg = f"✅ Comprados `{coins:.4f}` IshakCoins por `{amount_pts} pts`."
            else:
                coins = u.get("crypto_balance", 0)
                if coins <= 0: return False, "No tienes IshakCoins."
                gained = int(coins * price)
                u["crypto_balance"] = 0; u["points"] += gained
                self.data["market_stats"]["volume_24h"] += gained
                msg = f"✅ Vendidos `{coins:.4f}` coins. Recibes `{gained} pts`."
            self.data["transactions"].append({"uid": uid, "amount": amount_pts if buy else gained, "desc": "Crypto trade", "date": str(datetime.datetime.now())})
            await self._save_nolock(); return True, msg

    # ── Racha diaria ─────────────────────────────────────
    async def process_daily_streak(self, uid: str) -> Tuple[int, int, bool, bool]:
        async with self._lock:
            u = self.data["users"].get(uid)
            if not u: return 0, 0, False, False
            today = str(datetime.date.today())
            yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
            if u.get("last_daily") == today: return 0, u.get("streak", 0), False, False
            streak = u.get("streak", 0)
            streak = (streak + 1) if u.get("last_streak_date") == yesterday else 1
            u["streak"] = streak; u["last_streak_date"] = today
            base = random.randint(EmpireConfig.ECONOMY["DAILY_REWARD_MIN"],
                                  EmpireConfig.ECONOMY["DAILY_REWARD_MAX"])
            streak_bonus = min(streak * EmpireConfig.ECONOMY["STREAK_BONUS_DAY"],
                               EmpireConfig.ECONOMY["MAX_STREAK_BONUS"])
            plan = u["plan"]
            multi = {"FREE":1.0,"STARTER":1.3,"BASIC":1.6,"PRO":2.0,"ULTRA":3.0,"ENTERPRISE":4.0,"GOD":5.0}.get(plan, 1.0)
            total = int((base + streak_bonus) * multi)
            u["points"] += total; u["last_daily"] = today
            self.data["transactions"].append({"uid": uid, "amount": total, "desc": f"Tributo Diario (racha {streak})", "date": str(datetime.datetime.now())})
            week_ach  = streak == 7  and "STREAK_WEEK"  not in u.get("achievements",[])
            month_ach = streak == 30 and "STREAK_MONTH" not in u.get("achievements",[])
            for ach, key in [(week_ach,"STREAK_WEEK"),(month_ach,"STREAK_MONTH")]:
                if ach:
                    u.setdefault("achievements",[]).append(key)
                    u["points"] += EmpireConfig.ACHIEVEMENTS[key]["reward"]
            await self._save_nolock()
            return total, streak, week_ach, month_ach

    # ── Afiliados ─────────────────────────────────────────
    async def pay_affiliate_commission(self, buyer_uid: str, stars: int):
        async with self._lock:
            t1 = self.data["users"].get(buyer_uid, {}).get("referred_by")
            if t1 and t1 in self.data["users"]:
                c1 = int(stars * EmpireConfig.ECONOMY["AFFILIATE_T1_PCT"] * 10)
                self.data["users"][t1]["points"] += c1
                self.data["users"][t1]["affiliate_earnings"] = self.data["users"][t1].get("affiliate_earnings",0)+c1
                self.data["stats"]["affiliate_payouts"] += c1
                t2 = self.data["users"][t1].get("referred_by")
                if t2 and t2 in self.data["users"]:
                    c2 = int(stars * EmpireConfig.ECONOMY["AFFILIATE_T2_PCT"] * 10)
                    self.data["users"][t2]["points"] += c2
                    self.data["users"][t2]["affiliate_earnings"] = self.data["users"][t2].get("affiliate_earnings",0)+c2
                    t3 = self.data["users"][t2].get("referred_by")
                    if t3 and t3 in self.data["users"]:
                        c3 = int(stars * EmpireConfig.ECONOMY["AFFILIATE_T3_PCT"] * 10)
                        self.data["users"][t3]["points"] += c3
            await self._save_nolock()

    # ── Gift cards ────────────────────────────────────────
    async def generate_gift_card(self, value: int) -> str:
        async with self._lock:
            code = "GFT-" + uuid.uuid4().hex[:10].upper()
            self.data["coupons"][code] = {"type": "gift_card", "value": value,
                                          "used": False, "created": str(datetime.datetime.now())}
            self.data["stats"]["gift_cards_sold"] += 1
            await self._save_nolock(); return code

    async def redeem_gift_card(self, uid: str, code: str) -> Tuple[bool, str]:
        async with self._lock:
            code = code.strip().upper()
            if code not in self.data["coupons"]: return False, "Código inválido."
            card = self.data["coupons"][code]
            if card.get("used"): return False, "Tarjeta ya canjeada."
            if card.get("type") != "gift_card": return False, "No es tarjeta regalo."
            self.data["coupons"][code]["used"] = True
            self.data["coupons"][code]["used_by"] = uid
            self.data["users"][uid]["points"] += card["value"]
            self.data["transactions"].append({"uid":uid,"amount":card["value"],"desc":f"Gift Card ({code})","date":str(datetime.datetime.now())})
            await self._save_nolock(); return True, f"✅ Recibidos **{card['value']} pts**."

    # ── Leaderboard ───────────────────────────────────────
    async def get_leaderboard(self, cat: str = "points", n: int = 10) -> list:
        users = list(self.data["users"].values())
        key_map = {"points":"points","downloads":"total_downloads",
                   "referrals":"referrals","affiliate":"affiliate_earnings","level":"level"}
        key = key_map.get(cat, "points")
        s = sorted(users, key=lambda x: x.get(key, 0), reverse=True)
        return [(u.get("name","?"), u.get("username",""), u.get(key,0), u.get("plan","FREE")) for u in s[:n]]

    # ── Torneos ───────────────────────────────────────────
    async def start_tournament(self, hours: int = 24, seed: int = 5000):
        async with self._lock:
            end = datetime.datetime.now() + datetime.timedelta(hours=hours)
            self.data["system"]["tournament"] = {
                "active": True, "end_time": end.isoformat(),
                "prize_pool": seed, "participants": {}, "winners": []}
            await self._save_nolock()

    async def add_tournament_score(self, uid: str, score: int = 1):
        async with self._lock:
            t = self.data["system"]["tournament"]
            if not t.get("active"): return
            if t.get("end_time") and datetime.datetime.now() > datetime.datetime.fromisoformat(t["end_time"]):
                t["active"] = False; await self._save_nolock(); return
            t["participants"][uid] = t["participants"].get(uid, 0) + score
            t["prize_pool"] += 15
            await self._save_nolock()

    async def finalize_tournament(self) -> list:
        async with self._lock:
            t = self.data["system"]["tournament"]
            p = t.get("participants", {})
            if not p: t["active"] = False; await self._save_nolock(); return []
            sorted_p = sorted(p.items(), key=lambda x: x[1], reverse=True)
            pool = t["prize_pool"]
            dist = [0.50, 0.30, 0.20]
            winners = []
            for i, (uid, score) in enumerate(sorted_p[:3]):
                prize = int(pool * dist[i])
                if uid in self.data["users"]:
                    self.data["users"][uid]["points"] += prize
                    if i == 0 and "TOURNAMENT_WIN" not in self.data["users"][uid].get("achievements",[]):
                        self.data["users"][uid]["achievements"].append("TOURNAMENT_WIN")
                        self.data["users"][uid]["points"] += EmpireConfig.ACHIEVEMENTS["TOURNAMENT_WIN"]["reward"]
                    self.data["transactions"].append({"uid":uid,"amount":prize,"desc":f"Premio Torneo #{i+1}","date":str(datetime.datetime.now())})
                    winners.append((uid, score, prize))
            t["active"] = False; t["winners"] = [{"uid":w[0],"score":w[1],"prize":w[2]} for w in winners]
            t["participants"] = {}; self.data["stats"]["tournament_prize_pool"] += pool
            await self._save_nolock(); return winners

    # ── Guerra de Clanes ──────────────────────────────────
    async def start_clan_war(self, faction1: str, faction2: str, hours: int = 48):
        async with self._lock:
            if faction1 not in self.data["factions"] or faction2 not in self.data["factions"]:
                return False, "Una o ambas facciones no existen."
            end = datetime.datetime.now() + datetime.timedelta(hours=hours)
            war_id = f"war_{uuid.uuid4().hex[:8]}"
            self.data["clan_wars"][war_id] = {
                "factions": [faction1, faction2], "end_time": end.isoformat(),
                "scores": {faction1: 0, faction2: 0}, "active": True,
                "prize": EmpireConfig.ECONOMY["CLAN_WAR_REWARD_TOP"]
            }
            self.data["system"]["clan_war"] = {
                "active": True, "war_id": war_id, "factions": [faction1, faction2],
                "end_time": end.isoformat(), "scores": {faction1: 0, faction2: 0},
                "prize": EmpireConfig.ECONOMY["CLAN_WAR_REWARD_TOP"]
            }
            self.data["stats"]["clan_wars_total"] += 1
            await self._save_nolock()
            return True, war_id

    async def add_clan_war_score(self, uid: str, points: int = 1):
        async with self._lock:
            u = self.data["users"].get(uid, {})
            faction = u.get("faction")
            cw = self.data["system"].get("clan_war", {})
            if not cw.get("active") or not faction: return
            if faction in cw.get("factions", []):
                cw["scores"][faction] = cw["scores"].get(faction, 0) + points
            await self._save_nolock()

    async def finalize_clan_war(self) -> dict:
        async with self._lock:
            cw = self.data["system"].get("clan_war", {})
            if not cw.get("active"): return {}
            scores = cw.get("scores", {})
            if not scores: cw["active"] = False; await self._save_nolock(); return {}
            winner = max(scores, key=scores.get)
            loser  = [f for f in cw["factions"] if f != winner][0]
            prize  = cw["prize"]
            if winner in self.data["factions"]:
                for member_uid in self.data["factions"][winner].get("members", []):
                    if member_uid in self.data["users"]:
                        self.data["users"][member_uid]["points"] += prize // max(len(self.data["factions"][winner]["members"]),1)
                        self.data["users"][member_uid].setdefault("achievements",[])
                        if "CLAN_WAR_WIN" not in self.data["users"][member_uid]["achievements"]:
                            self.data["users"][member_uid]["achievements"].append("CLAN_WAR_WIN")
                            self.data["users"][member_uid]["points"] += EmpireConfig.ACHIEVEMENTS["CLAN_WAR_WIN"]["reward"]
            cw["active"] = False
            result = {"winner": winner, "loser": loser, "scores": scores, "prize": prize}
            await self._save_nolock(); return result

    # ── Mercado P2P ───────────────────────────────────────
    async def create_p2p_listing(self, seller_uid: str, item_type: str, amount: int, price: int) -> Tuple[bool, str]:
        async with self._lock:
            u = self.data["users"].get(seller_uid)
            if not u: return False, "Usuario no encontrado."
            if item_type == "points":
                if u["points"] < amount: return False, "Puntos insuficientes."
                u["points"] -= amount  # escrow
            listing_id = f"p2p_{uuid.uuid4().hex[:8]}"
            self.data["p2p_market"].append({
                "id": listing_id, "seller": seller_uid, "type": item_type,
                "amount": amount, "price": price, "active": True,
                "created": str(datetime.datetime.now())
            })
            await self._save_nolock()
            return True, listing_id

    async def buy_p2p_listing(self, buyer_uid: str, listing_id: str) -> Tuple[bool, str]:
        async with self._lock:
            listing = next((l for l in self.data["p2p_market"] if l["id"] == listing_id and l["active"]), None)
            if not listing: return False, "Anuncio no encontrado o ya cerrado."
            buyer = self.data["users"].get(buyer_uid)
            if not buyer: return False, "Comprador no encontrado."
            if buyer["points"] < listing["price"]: return False, "Puntos insuficientes."
            fee = int(listing["price"] * EmpireConfig.ECONOMY["P2P_MARKET_FEE"])
            seller_gets = listing["price"] - fee
            buyer["points"] -= listing["price"]
            seller = self.data["users"].get(listing["seller"])
            if seller:
                seller["points"] += seller_gets + listing["amount"]  # devolver escrow + pago
                seller["stats"]["p2p_sales"] = seller.get("stats",{}).get("p2p_sales",0)+1
            buyer["stats"]["p2p_purchases"] = buyer.get("stats",{}).get("p2p_purchases",0)+1
            self.data["stats"]["p2p_volume"] += listing["price"]
            listing["active"] = False
            await self._save_nolock()
            return True, f"✅ Compra P2P completada. +{listing['amount']} {listing['type']}."

    # ── Historial de descargas ────────────────────────────
    async def add_download_history(self, uid: str, url: str, title: str, fmt: str, size_mb: float):
        async with self._lock:
            u = self.data["users"].get(uid)
            if not u: return
            u.setdefault("download_history", []).append({
                "url": url, "title": title[:60], "format": fmt,
                "size_mb": round(size_mb, 2), "date": str(datetime.datetime.now())
            })
            if len(u["download_history"]) > 100:
                u["download_history"] = u["download_history"][-80:]
            await self._save_nolock()

    # ── Favoritos ────────────────────────────────────────
    async def toggle_favorite(self, uid: str, url: str) -> bool:
        async with self._lock:
            u = self.data["users"].get(uid)
            if not u: return False
            favs = u.setdefault("favorites", [])
            if url in favs: favs.remove(url); added = False
            else: favs.append(url); added = True
            await self._save_nolock(); return added

    # ── Tienda diaria rotativa ────────────────────────────
    async def refresh_daily_shop(self):
        async with self._lock:
            today = str(datetime.date.today())
            shop = self.data["system"]["daily_shop"]
            if shop.get("date") == today: return
            all_items = list(EmpireConfig.SHOP_ITEMS.items())
            selected = random.sample(all_items, min(4, len(all_items)))
            discount = EmpireConfig.ECONOMY["DAILY_SHOP_DISCOUNT"]
            self.data["system"]["daily_shop"] = {
                "items": [{"key": k, "name": v["name"], "desc": v["desc"],
                           "original_price": v["price"],
                           "price": int(v["price"] * (1 - discount))}
                          for k, v in selected],
                "date": today
            }
            await self._save_nolock()

    # ── Notificaciones push ───────────────────────────────
    async def push_notification(self, uid: str, msg: str, cat: str = "general"):
        async with self._lock:
            u = self.data["users"].get(uid)
            if not u: return
            if u.get("settings",{}).get("notifications_enabled", True):
                u.setdefault("notification_queue",[]).append({
                    "message": msg, "category": cat,
                    "timestamp": datetime.datetime.now().isoformat(), "read": False
                })
                if len(u["notification_queue"]) > 25:
                    u["notification_queue"] = u["notification_queue"][-20:]
                await self._save_nolock()

    # ── Backup automático ─────────────────────────────────
    async def backup_job(self):
        while True:
            await asyncio.sleep(7200)
            try:
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                dst = os.path.join(EmpireConfig.BACKUP_DIR, f"db_{ts}.json")
                await asyncio.to_thread(shutil.copy2, EmpireConfig.DATABASE_PATH, dst)
                # Mantener solo los últimos 30 backups
                backups = sorted(os.listdir(EmpireConfig.BACKUP_DIR))
                for old in backups[:-30]:
                    os.remove(os.path.join(EmpireConfig.BACKUP_DIR, old))
                logger.info(f"💾 Backup creado: {dst}")
            except Exception as e:
                logger.error(f"Error backup: {e}"); alert_system.track_error()

    # ── Exportar usuarios a CSV ───────────────────────────
    def export_users_csv(self) -> str:
        path = os.path.join(EmpireConfig.EXPORT_DIR, f"users_{datetime.date.today()}.csv")
        users = list(self.data["users"].values())
        with open(path, 'w', newline='', encoding='utf-8') as f:
            fields = ["id","name","username","plan","points","level","total_downloads",
                      "referrals","affiliate_earnings","streak","joined","is_banned"]
            w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            w.writeheader(); w.writerows(users)
        return path

    # ── Self-healing loop ─────────────────────────────────
    async def self_healing_loop(self):
        while True:
            await asyncio.sleep(1800)
            async with self._lock:
                fixed = 0
                for uid, u in self.data["users"].items():
                    if not isinstance(u.get("points"), (int,float)) or u["points"] < 0:
                        u["points"] = 0; fixed += 1
                    if not isinstance(u.get("crypto_balance"), (int,float)) or u["crypto_balance"] < 0:
                        u["crypto_balance"] = 0.0; fixed += 1
                    if not isinstance(u.get("level"), int) or u.get("level",0) < 1:
                        u["level"] = 1; fixed += 1
                    if "settings" not in u:
                        u["settings"] = {"watermark":None,"auto_transcribe":False,
                                         "ghost_mode":False,"send_as_doc":False,
                                         "theme":"dark","language":settings.default_language,
                                         "notifications_enabled":True,"auto_dl_best":False}; fixed += 1
                    if "security" not in u:
                        u["security"] = {"two_fa_enabled":False,"two_fa_secret":None,
                                         "two_fa_verified":False,"login_history":[],"trusted_ips":[]}; fixed += 1
                    if "download_history" not in u: u["download_history"] = []; fixed += 1
                    if "favorites" not in u: u["favorites"] = []; fixed += 1
                    if "batch_queue" not in u: u["batch_queue"] = []; fixed += 1
                    # Asegura inventario completo
                    for item_key in EmpireConfig.SHOP_ITEMS:
                        if item_key not in u.get("inventory", {}):
                            u.setdefault("inventory",{})[item_key] = 0; fixed += 1
                if fixed > 0:
                    self.data["stats"]["self_healing_fixes"] += fixed
                    logger.warning(f"🛠️ Self-Healing: {fixed} reparaciones.")
                await self._save_nolock()

db = EmpireDatabase()

# ============================================================
# [8] MOTORES: CASINO V500 (SLOTS, RULETA, BJ, CRASH, MINES, PLINKO, POKER, DADOS)
# ============================================================
class CasinoV500:
    CARD_VALUES = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10,'A':11}
    SUITS = ["♠","♥","♦","♣"]
    RANKS = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']

    # ── Slots ─────────────────────────────────────────────
    @staticmethod
    def play_slots(bet: int, luck_bonus: float = 0) -> Tuple[int, str]:
        syms = ["🍒","🍋","🍊","🔔","💎","👑","🎰","⚡"]
        weights = [30,25,20,12,7,4,1,1]
        res = random.choices(syms, weights=weights, k=3)
        msg = f"🎰 **SLOTS IMPERIAL**\n[ {res[0]} | {res[1]} | {res[2]} ]\n"
        if res[0] == res[1] == res[2]:
            mults = {"🎰":100,"👑":50,"💎":25,"⚡":20,"🔔":10,"🍊":7,"🍋":5,"🍒":3}
            m = mults.get(res[0], 3)
            w = int(bet * m * (1 + luck_bonus))
            msg += f"🎉 **{'MEGA ' if m >= 20 else ''}JACKPOT! x{m}**\nGanaste **{w} pts**!"
            return w, msg
        elif len(set(res)) == 2:
            w = int(bet * 1.5 * (1 + luck_bonus))
            msg += f"👍 Par. Recuperas **{w} pts**."
            return w, msg
        msg += "💀 Perdiste la apuesta."
        return 0, msg

    # ── Ruleta ────────────────────────────────────────────
    @staticmethod
    def play_roulette(bet: int, choice: str, luck_bonus: float = 0) -> Tuple[int, str]:
        num = random.randint(0, 36)
        reds = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
        color = "🟢" if num==0 else ("🔴" if num in reds else "⚫")
        msg = f"🎡 **RULETA**\nBola cayó en **{num} {color}**\n"
        win = 0
        c = choice.lower()
        if c == "verde" and num == 0:
            win = int(bet * 35 * (1+luck_bonus)); msg += f"🎉 ¡VERDE! x35 → +{win} pts"
        elif c == "rojo" and color == "🔴":
            win = int(bet * 2 * (1+luck_bonus)); msg += f"✅ Rojo → +{win} pts"
        elif c == "negro" and color == "⚫":
            win = int(bet * 2 * (1+luck_bonus)); msg += f"✅ Negro → +{win} pts"
        elif c == "par" and num > 0 and num % 2 == 0:
            win = int(bet * 2 * (1+luck_bonus)); msg += f"✅ Par → +{win} pts"
        elif c == "impar" and num > 0 and num % 2 == 1:
            win = int(bet * 2 * (1+luck_bonus)); msg += f"✅ Impar → +{win} pts"
        elif c.isdigit() and int(c) == num:
            win = int(bet * 35 * (1+luck_bonus)); msg += f"🎯 Número exacto! x35 → +{win} pts"
        else:
            msg += "💀 Perdiste."
        return win, msg

    # ── Blackjack ─────────────────────────────────────────
    @staticmethod
    def draw_card() -> str:
        return random.choice(CasinoV500.RANKS)

    @staticmethod
    def hand_value(hand: List[str]) -> int:
        v = 0; aces = 0
        for c in hand:
            if c == 'A': aces += 1; v += 11
            else: v += CasinoV500.CARD_VALUES.get(c, 0)
        while v > 21 and aces: v -= 10; aces -= 1
        return v

    # ── Crash ──────────────────────────────────────────────
    @staticmethod
    def calc_crash() -> float:
        r = random.random()
        if r < 0.04: return 1.00
        return min(100.0, 1.0 / (1.0 - r))

    # ── Mines ──────────────────────────────────────────────
    @staticmethod
    def init_mines(mines_count: int = 5, grid_size: int = 25) -> dict:
        positions = list(range(grid_size))
        mines = set(random.sample(positions, mines_count))
        return {
            "grid_size": grid_size, "mines": list(mines),
            "revealed": [], "mines_count": mines_count,
            "safe_clicked": 0, "game_over": False, "won": False
        }

    @staticmethod
    def mines_click(state: dict, pos: int) -> Tuple[bool, bool, float]:
        """Devuelve (es_mina, juego_terminado, multiplicador_actual)."""
        if pos in state["mines"]:
            state["game_over"] = True; return True, True, 0.0
        if pos not in state["revealed"]:
            state["revealed"].append(pos)
            state["safe_clicked"] += 1
        safe = state["safe_clicked"]
        m = state["mines_count"]
        g = state["grid_size"]
        mult = max(1.0, (g / (g - m)) ** safe * 0.97)  # house edge 3%
        if len(state["revealed"]) >= (g - m):
            state["won"] = True; state["game_over"] = True
        return False, state["game_over"], round(mult, 2)

    # ── Plinko ─────────────────────────────────────────────
    @staticmethod
    def play_plinko(bet: int, rows: int = 8, luck_bonus: float = 0) -> Tuple[int, str, float]:
        pos = 0
        for _ in range(rows):
            pos += random.choice([-1, 1])
        # Distribución normal → posición determina multiplicador
        buckets = {0: 0.2, 1: 0.5, 2: 1.0, 3: 2.0, 4: 3.0, 5: 5.0, 6: 10.0, 7: 25.0, 8: 100.0}
        abs_pos = min(abs(pos), rows)
        mult = buckets.get(abs_pos, 0.2) * (1 + luck_bonus)
        win = int(bet * mult)
        emoji = "🎯" if mult >= 10 else ("✅" if mult >= 1 else "💀")
        msg = f"🎱 **PLINKO**\nLa bola cayó en slot `{pos:+d}`\nMultiplicador: `x{mult:.1f}` {emoji}\n"
        if win > bet: msg += f"Ganaste **+{win} pts**!"
        elif win == 0: msg += "💀 Perdiste la apuesta."
        else: msg += f"Recuperas **{win} pts**."
        return win, msg, mult

    # ── Dados ──────────────────────────────────────────────
    @staticmethod
    def play_dice(bet: int, prediction: str, luck_bonus: float = 0) -> Tuple[int, str]:
        d1, d2 = random.randint(1,6), random.randint(1,6)
        total = d1 + d2
        dice_str = f"🎲`{d1}` + 🎲`{d2}` = **{total}**"
        msg = f"🎲 **DADOS IMPERIALES**\n{dice_str}\n"
        win = 0; pred = prediction.lower()
        if pred == "alto" and total > 7:
            win = int(bet * 1.8 * (1+luck_bonus)); msg += f"✅ Alto → +{win} pts"
        elif pred == "bajo" and total < 7:
            win = int(bet * 1.8 * (1+luck_bonus)); msg += f"✅ Bajo → +{win} pts"
        elif pred == "exacto_7" and total == 7:
            win = int(bet * 4.0 * (1+luck_bonus)); msg += f"🎯 Exacto 7! → +{win} pts"
        elif pred == "doble" and d1 == d2:
            win = int(bet * 5.0 * (1+luck_bonus)); msg += f"🎰 ¡Doble! → +{win} pts"
        else:
            msg += "💀 Perdiste."
        return win, msg

    # ── Poker (5 cartas) ──────────────────────────────────
    @staticmethod
    def deal_poker_hand() -> List[str]:
        deck = [f"{r}{s}" for r in CasinoV500.RANKS for s in CasinoV500.SUITS]
        return random.sample(deck, 5)

    @staticmethod
    def eval_poker_hand(hand: List[str]) -> Tuple[str, float]:
        ranks = sorted([c[:-1] for c in hand])
        rank_vals = sorted([CasinoV500.CARD_VALUES.get(r,0) for r in ranks])
        suits = [c[-1] for c in hand]
        is_flush   = len(set(suits)) == 1
        rank_v2    = [CasinoV500.CARD_VALUES.get(r,0) for r in ranks]
        sorted_rv  = sorted(rank_v2)
        is_straight = (sorted_rv == list(range(sorted_rv[0], sorted_rv[0]+5)))
        from collections import Counter
        cnt = Counter(ranks)
        counts = sorted(cnt.values(), reverse=True)
        if is_straight and is_flush and sorted_rv[-1] == 14: return "🃏 Royal Flush",    800.0
        if is_straight and is_flush:                          return "🎴 Straight Flush", 50.0
        if counts == [4,1]:                                   return "4️⃣ Póker",           25.0
        if counts == [3,2]:                                   return "🏠 Full House",      10.0
        if is_flush:                                          return "♠ Color",             6.0
        if is_straight:                                       return "📈 Escalera",          4.0
        if counts == [3,1,1]:                                 return "3️⃣ Trío",              3.0
        if counts == [2,2,1]:                                 return "2️⃣ Dos Pares",         2.0
        if counts == [2,1,1,1]:                               return "1️⃣ Un Par",            1.0
        return "❌ Nada",                                                                    0.0

casino = CasinoV500()

# ============================================================
# [9] MOTOR DE MEDIOS V500
# ============================================================
class ProgressTracker:
    def __init__(self):
        self.jobs: Dict[str, dict] = {}

    def add(self, job_id: str, msg_obj):
        self.jobs[job_id] = {"msg": msg_obj, "percent": 0, "speed": "0B/s",
                             "eta": "...", "finished": False, "last_upd": time.time()}

    async def loop(self):
        while True:
            await asyncio.sleep(3)
            now = time.time()
            for jid, d in list(self.jobs.items()):
                if d["finished"] or (now - d["last_upd"] > 900):
                    self.jobs.pop(jid, None); continue
                try:
                    filled = int(15 * d["percent"] / 100)
                    bar = '█'*filled + '░'*(15-filled)
                    txt = (f"⚡ **SINTETIZANDO...**\n`{bar}` {d['percent']:.1f}%\n"
                           f"Vel: `{d['speed']}` | ETA: `{d['eta']}`")
                    if d.get("last_txt") != txt:
                        await d["msg"].edit_text(txt, parse_mode="Markdown")
                        d["last_txt"] = txt; d["last_upd"] = now
                except: pass

progress = ProgressTracker()

class MediaEngineV500:
    @staticmethod
    async def get_metadata(url: str) -> dict:
        if url in METADATA_CACHE and time.time() - METADATA_CACHE[url].get("ts",0) < 3600:
            return METADATA_CACHE[url]["data"]
        try:
            def _get():
                with yt_dlp.YoutubeDL({"quiet":True,"no_warnings":True,"nocheckcertificate":True}) as ydl:
                    i = ydl.extract_info(url, download=False)
                    if not i: return {}
                    return {"title":i.get("title"),"duration":i.get("duration"),
                            "uploader":i.get("uploader"),"view_count":i.get("view_count"),
                            "thumbnail":i.get("thumbnail"),"description":i.get("description","")[:200]}
            data = await asyncio.to_thread(_get)
            METADATA_CACHE[url] = {"data": data, "ts": time.time()}
            return data
        except: return {}

    @staticmethod
    async def run(url: str, mode: str, quality: str, uid: str,
                  max_mb: float, job_id: str, user_settings: dict) -> tuple:
        out = os.path.join(EmpireConfig.BUFFER_DIR, f"{job_id}.%(ext)s")

        def hook(d):
            job = progress.jobs.get(job_id)
            if job and d["status"] == "downloading":
                try:
                    p = float(d.get("_percent_str","0%").replace("%","").strip())
                    job["percent"] = p; job["speed"] = d.get("_speed_str","0B/s")
                    job["eta"] = d.get("_eta_str","...")
                except: pass

        opts = {
            "outtmpl": out, "quiet": True, "no_warnings": True,
            "noplaylist": True, "nocheckcertificate": True,
            "progress_hooks": [hook], "socket_timeout": 15,
            "max_filesize": max_mb * 1024 * 1024,
            "extractor_args": {"youtube": ["player_client=ios,android,web"]},
        }

        if mode == "MP3":
            opts.update({"format":"bestaudio/best","postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"192"}]})
        elif mode == "MP3U":
            opts.update({"format":"bestaudio/best","postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"320"}]})
        elif mode == "VOICE":
            opts.update({"format":"bestaudio/best","postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"vorbis","preferredquality":"128"}]})
        elif mode == "VNOA":
            h = quality.replace("p","") if quality != "Original" else "1080"
            opts["format"] = f"bestvideo[height<={h}][ext=mp4]/bestvideo"
        elif mode == "GIF":
            opts["format"] = "bestvideo[height<=480][ext=mp4]/best"
        elif mode == "WEBM":
            h = quality.replace("p","") if quality != "Original" else "1080"
            opts["format"] = f"bestvideo[height<={h}][ext=webm]+bestaudio/best"
        elif mode == "FLAC":
            opts.update({"format":"bestaudio/best","postprocessors":[{"key":"FFmpegExtractAudio","preferredcodec":"flac"}]})
        else:  # MP4
            h = quality.replace("p","") if quality != "Original" else "2160"
            opts["format"] = f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

        def _run():
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not info: return False,None,None,0,0,"Sin información."
                    path = ydl.prepare_filename(info)
                    ext_map = {"MP3":"mp3","MP3U":"mp3","VOICE":"ogg","FLAC":"flac"}
                    if mode in ext_map: path = os.path.splitext(path)[0]+"."+ext_map[mode]
                    size = os.path.getsize(path) if os.path.exists(path) else 0
                    return True, path, info.get("title","Media"), info.get("duration",0), size, ""
            except yt_dlp.utils.DownloadError as e:
                err = str(e).lower()
                msg = str(e)
                if "copyright" in err: msg = "Bloqueado por derechos de autor."
                elif "too large" in err: msg = f"Archivo supera el límite de {max_mb:.0f}MB."
                elif "private" in err or "sign in" in err: msg = "Contenido privado o con login requerido."
                elif "geo" in err: msg = "Restricción geográfica."
                gc.collect(); return False,None,None,0,0,msg
            except Exception as e:
                gc.collect(); return False,None,None,0,0,f"Error: {e}"

        return await asyncio.to_thread(_run)

    @staticmethod
    async def batch_download(urls: List[str], mode: str, quality: str,
                             uid: str, max_mb: float) -> List[Tuple[bool, str, str]]:
        """Descarga múltiples URLs secuencialmente."""
        results = []
        for url in urls[:settings.max_batch_urls]:
            jid = f"batch_{uid}_{uuid.uuid4().hex[:6]}"
            ok, path, title, dur, size, err = await MediaEngineV500.run(
                url, mode, quality, uid, max_mb, jid, {})
            results.append((ok, path or "", title or url, err))
        return results

media = MediaEngineV500()

# ============================================================
# [10] HERRAMIENTAS REALES (TTS, QR, PING, B64, HASH)
# ============================================================
class RealTools:
    @staticmethod
    async def tts(text: str, uid: str, lang: str = "es") -> Optional[str]:
        try:
            def _gen():
                tts = gTTS(text=text[:500], lang=lang)
                p = os.path.join(EmpireConfig.TTS_DIR, f"tts_{uid}_{uuid.uuid4().hex[:6]}.ogg")
                tts.save(p); return p
            return await asyncio.to_thread(_gen)
        except Exception as e:
            logger.error(f"TTS error: {e}"); return None

    @staticmethod
    async def qr(data: str, uid: str) -> Optional[str]:
        try:
            def _gen():
                q = qrcode.QRCode(version=1, box_size=10, border=5)
                q.add_data(data); q.make(fit=True)
                img = q.make_image(fill_color="black", back_color="white")
                p = os.path.join(EmpireConfig.QR_DIR, f"qr_{uid}_{uuid.uuid4().hex[:6]}.png")
                img.save(p); return p
            return await asyncio.to_thread(_gen)
        except Exception as e:
            logger.error(f"QR error: {e}"); return None

    @staticmethod
    async def ping(host: str = "8.8.8.8") -> str:
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            out = await asyncio.to_thread(
                lambda: subprocess.check_output(["ping", param, "4", host],
                                                stderr=subprocess.STDOUT, universal_newlines=True))
            m = re.search(r"avg[/ =]+([\d.]+)", out)
            return f"{m.group(1)}ms" if m else "OK (latencia no parseada)"
        except: return "Host inalcanzable."

    @staticmethod
    def b64enc(text: str) -> str: return base64.b64encode(text.encode()).decode()
    @staticmethod
    def b64dec(text: str) -> str:
        try: return base64.b64decode(text.encode()).decode()
        except: return "Error: Base64 inválido."
    @staticmethod
    def sha256(text: str) -> str: return hashlib.sha256(text.encode()).hexdigest()
    @staticmethod
    def md5(text: str) -> str: return hashlib.md5(text.encode()).hexdigest()
    @staticmethod
    def rot13(text: str) -> str:
        return text.translate(str.maketrans(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
            'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))

tools = RealTools()

# ============================================================
# [11] INTERFAZ DE USUARIO V500
# ============================================================
class UI:
    # ── Teclados principales ──────────────────────────────
    @staticmethod
    def main_kb(u: dict) -> ReplyKeyboardMarkup:
        if u.get("is_banned"):
            return ReplyKeyboardMarkup([[KeyboardButton("🎧 SOPORTE")]], resize_keyboard=True)
        is_admin = u["id"] == EmpireConfig.ADMIN_ID
        is_vip   = u.get("vip_expiry") and datetime.datetime.now() < datetime.datetime.fromisoformat(u["vip_expiry"])
        is_god   = u["plan"] == "GOD"
        rows = [
            [KeyboardButton("📥 EXTRACCIÓN"),     KeyboardButton("📦 LOTE DE URLs")],
            [KeyboardButton("👤 PERFIL"),          KeyboardButton("📊 MIS ESTADÍSTICAS")],
            [KeyboardButton("⭐️ TIENDA STARS"),   KeyboardButton("🏪 MERCADO NEGRO")],
            [KeyboardButton("🎰 CASINO IMPERIAL"), KeyboardButton("⚙️ AJUSTES PRO")],
            [KeyboardButton("🛠️ HERRAMIENTAS"),   KeyboardButton("🛡️ FACCIONES")],
            [KeyboardButton("🎁 TRIBUTO DIARIO"), KeyboardButton("🎮 MISIONES Y LOGROS")],
            [KeyboardButton("🏆 RANKING GLOBAL"), KeyboardButton("🔔 NOTIFICACIONES")],
            [KeyboardButton("📜 MI HISTORIAL"),   KeyboardButton("⭐ MIS FAVORITOS")],
            [KeyboardButton("🛒 TIENDA DIARIA"),  KeyboardButton("🎫 CANJEAR CÓDIGO")],
            [KeyboardButton("🤝 MERCADO P2P"),    KeyboardButton("🎧 SOPORTE")],
        ]
        if is_vip:  rows.insert(2, [KeyboardButton("🥂 SALA VIP")])
        if is_god:  rows.append([KeyboardButton("🏢 ÁREA B2B")])
        if is_admin:
            rows.append([KeyboardButton("👑 PANEL OVERLORD"), KeyboardButton("🌐 TELEMETRÍA")])
            rows.append([KeyboardButton("🏟️ TORNEOS ADMIN"),  KeyboardButton("⚔️ GUERRA DE CLANES")])
        return ReplyKeyboardMarkup(rows, resize_keyboard=True)

    # ── Panel Overlord ────────────────────────────────────
    @staticmethod
    def overlord_panel(page: int = 0) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Listar Usuarios",    callback_data=f"adm_list_{page}"),
             InlineKeyboardButton("📢 Broadcast",          callback_data="adm_bc")],
            [InlineKeyboardButton("🚫 Banear",             callback_data="adm_ban"),
             InlineKeyboardButton("🔓 Desbanear",          callback_data="adm_unban")],
            [InlineKeyboardButton("💰 Dar Puntos",         callback_data="adm_pts"),
             InlineKeyboardButton("🎫 Crear Cupón",        callback_data="adm_cp")],
            [InlineKeyboardButton("🎭 Cambiar Plan",       callback_data="adm_edit_plan"),
             InlineKeyboardButton("📂 Ver Tickets",        callback_data="adm_tickets")],
            [InlineKeyboardButton("⚠️ Mantenimiento",      callback_data="adm_maint"),
             InlineKeyboardButton("💾 Backup DB",          callback_data="adm_backup")],
            [InlineKeyboardButton("🎁 Generar Gift Card",  callback_data="adm_giftcard"),
             InlineKeyboardButton("📊 Analíticas Full",    callback_data="adm_analytics")],
            [InlineKeyboardButton("📣 Push VIP Masivo",    callback_data="adm_vip_push"),
             InlineKeyboardButton("🔑 API Keys",           callback_data="adm_apikeys")],
            [InlineKeyboardButton("📥 Exportar CSV",       callback_data="adm_export_csv"),
             InlineKeyboardButton("🔍 Buscar Usuario",     callback_data="adm_search_user")],
            [InlineKeyboardButton("🗑️ Limpiar Buffer",     callback_data="adm_clean_buffer"),
             InlineKeyboardButton("💸 Ver Transacciones",  callback_data="adm_txns")],
            [InlineKeyboardButton("🏟️ Gestionar Torneo",   callback_data="adm_tournament"),
             InlineKeyboardButton("⚔️ Gestionar Guerra",   callback_data="adm_clan_war")],
            [InlineKeyboardButton("🔒 Ver Blacklist IPs",  callback_data="adm_blacklist"),
             InlineKeyboardButton("📅 Programar Evento",   callback_data="adm_schedule")],
            [InlineKeyboardButton("❌ CERRAR",              callback_data="u_close")],
        ])

    # ── Selectores de formato/calidad ─────────────────────
    @staticmethod
    def format_selector() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 MP4",        callback_data="fmt_MP4"),
             InlineKeyboardButton("🎵 MP3 (192k)", callback_data="fmt_MP3")],
            [InlineKeyboardButton("🔥 MP3 ULTRA",  callback_data="fmt_MP3U"),
             InlineKeyboardButton("🎵 FLAC",        callback_data="fmt_FLAC")],
            [InlineKeyboardButton("🎞️ Sin Audio",  callback_data="fmt_VNOA"),
             InlineKeyboardButton("🎙️ Nota Voz",   callback_data="fmt_VOICE")],
            [InlineKeyboardButton("🎞️ GIF",        callback_data="fmt_GIF"),
             InlineKeyboardButton("📹 WEBM",        callback_data="fmt_WEBM")],
            [InlineKeyboardButton("❌ ABORTAR",     callback_data="u_close")],
        ])

    @staticmethod
    def quality_selector(plan_id: str) -> InlineKeyboardMarkup:
        qs = EmpireConfig.PLANS.get(plan_id, EmpireConfig.PLANS["FREE"])["resolutions"]
        rows = [[InlineKeyboardButton(f"🎥 {q}", callback_data=f"ql_{q}") for q in qs[i:i+2]]
                for i in range(0, len(qs), 2)]
        rows.append([InlineKeyboardButton("⬅️ Atrás", callback_data="fmt_back")])
        return InlineKeyboardMarkup(rows)

    # ── Tienda Stars ─────────────────────────────────────
    @staticmethod
    def stars_shop_main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Comprar Puntos",           callback_data="shop_cat_points")],
            [InlineKeyboardButton("📅 Suscripciones Semanales",  callback_data="shop_cat_week")],
            [InlineKeyboardButton("🗓️ Suscripciones Mensuales",  callback_data="shop_cat_month")],
            [InlineKeyboardButton("📆 Suscripciones Anuales",    callback_data="shop_cat_year")],
            [InlineKeyboardButton("🎁 Gift Cards & Especiales",  callback_data="shop_cat_special")],
            [InlineKeyboardButton("❌ CERRAR",                    callback_data="u_close")],
        ])

    @staticmethod
    def stars_shop_category(cat: str) -> InlineKeyboardMarkup:
        cat_map = {
            "points":  ["PTS_MICRO","PTS_SMALL","PTS_MEDIUM","PTS_LARGE","PTS_WHALE"],
            "week":    ["SUB_STARTER_W","SUB_BASIC_W","SUB_PRO_W","SUB_ULTRA_W"],
            "month":   ["SUB_STARTER_M","SUB_BASIC_M","SUB_PRO_M","SUB_ULTRA_M","SUB_ENT_M"],
            "year":    ["SUB_PRO_Y","SUB_ULTRA_Y"],
            "special": ["VIP_MONTH","GIFT_500","GIFT_2500","GIFT_10000","BOOST_XP_W","CLAN_SLOT"],
        }
        keys = cat_map.get(cat, [])
        rows = [[InlineKeyboardButton(
            f"{EmpireConfig.STARS_PACKAGES[k]['name']} — {EmpireConfig.STARS_PACKAGES[k]['stars']} ⭐️",
            callback_data=f"stars_{k}")] for k in keys if k in EmpireConfig.STARS_PACKAGES]
        rows.append([InlineKeyboardButton("⬅️ Volver", callback_data="shop_main"),
                     InlineKeyboardButton("❌ Cerrar", callback_data="u_close")])
        return InlineKeyboardMarkup(rows)

    # ── Casino ────────────────────────────────────────────
    @staticmethod
    def casino_main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 Slots (100 pts)",          callback_data="cas_slots"),
             InlineKeyboardButton("🎡 Ruleta (250 pts)",          callback_data="cas_roulette_menu")],
            [InlineKeyboardButton("🃏 Blackjack (500 pts)",       callback_data="cas_bj"),
             InlineKeyboardButton("📈 Crash (1000 pts)",          callback_data="cas_crash")],
            [InlineKeyboardButton("💣 Mines (500 pts)",           callback_data="cas_mines_menu"),
             InlineKeyboardButton("🎱 Plinko (300 pts)",          callback_data="cas_plinko")],
            [InlineKeyboardButton("🎲 Dados (200 pts)",           callback_data="cas_dice_menu"),
             InlineKeyboardButton("🃏 Poker (1000 pts)",          callback_data="cas_poker")],
            [InlineKeyboardButton("❌ SALIR",                     callback_data="u_close")],
        ])

    @staticmethod
    def roulette_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 Rojo",    callback_data="cas_rul_rojo"),
             InlineKeyboardButton("⚫ Negro",   callback_data="cas_rul_negro")],
            [InlineKeyboardButton("🟢 Verde",   callback_data="cas_rul_verde"),
             InlineKeyboardButton("2️⃣ Par",     callback_data="cas_rul_par")],
            [InlineKeyboardButton("1️⃣ Impar",  callback_data="cas_rul_impar")],
            [InlineKeyboardButton("⬅️ Volver",  callback_data="cas_back")],
        ])

    @staticmethod
    def mines_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💣 3 minas (fácil)",    callback_data="cas_mines_3"),
             InlineKeyboardButton("💣 5 minas (medio)",    callback_data="cas_mines_5")],
            [InlineKeyboardButton("💣 10 minas (difícil)", callback_data="cas_mines_10"),
             InlineKeyboardButton("💣 15 minas (hardcore)",callback_data="cas_mines_15")],
            [InlineKeyboardButton("⬅️ Volver",              callback_data="cas_back")],
        ])

    @staticmethod
    def mines_grid(state: dict, bet: int) -> InlineKeyboardMarkup:
        rows, cols = 5, 5
        revealed = set(state["revealed"])
        mines    = set(state["mines"])
        kb = []
        for r in range(rows):
            row = []
            for c in range(cols):
                pos = r*cols+c
                if pos in revealed:
                    row.append(InlineKeyboardButton("💎", callback_data="mines_noop"))
                else:
                    row.append(InlineKeyboardButton("⬛", callback_data=f"mines_click_{pos}_{bet}"))
            kb.append(row)
        safe = state["safe_clicked"]; m = state["mines_count"]; g = state["grid_size"]
        current_mult = max(1.0, (g/(g-m))**safe*0.97) if safe > 0 else 1.0
        kb.append([InlineKeyboardButton(f"💰 Cash Out (x{current_mult:.2f})", callback_data=f"mines_cashout_{bet}")])
        kb.append([InlineKeyboardButton("❌ Rendirse (perder)", callback_data="mines_quit")])
        return InlineKeyboardMarkup(kb)

    @staticmethod
    def dice_menu() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬆️ Alto (>7)",    callback_data="cas_dice_alto"),
             InlineKeyboardButton("⬇️ Bajo (<7)",    callback_data="cas_dice_bajo")],
            [InlineKeyboardButton("7️⃣ Exacto 7",    callback_data="cas_dice_exacto_7"),
             InlineKeyboardButton("🎰 Doble",        callback_data="cas_dice_doble")],
            [InlineKeyboardButton("⬅️ Volver",       callback_data="cas_back")],
        ])

    @staticmethod
    def bj_panel(bet: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("🃏 Pedir", callback_data=f"bj_hit_{bet}"),
            InlineKeyboardButton("🛑 Plantarse", callback_data=f"bj_stand_{bet}"),
            InlineKeyboardButton("2x Doblar", callback_data=f"bj_double_{bet}"),
        ]])

    @staticmethod
    def crash_panel(bet: int, mult: float = 1.0) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(f"🚀 Cash Out ({mult:.2f}x)", callback_data=f"crash_co_{bet}_{mult:.2f}")
        ]])

    @staticmethod
    def poker_panel() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🃏 Ver Mano", callback_data="poker_view"),
             InlineKeyboardButton("🔄 Nueva Mano", callback_data="poker_new")],
            [InlineKeyboardButton("❌ Salir",    callback_data="cas_back")],
        ])

    # ── Facciones ─────────────────────────────────────────
    @staticmethod
    def factions_panel(has_faction: bool) -> InlineKeyboardMarkup:
        if has_faction:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Info Facción",   callback_data="fac_info"),
                 InlineKeyboardButton("💰 Donar Bóveda",   callback_data="fac_donate")],
                [InlineKeyboardButton("⭐ Subir Nivel",    callback_data="fac_upgrade"),
                 InlineKeyboardButton("👥 Ver Miembros",   callback_data="fac_members")],
                [InlineKeyboardButton("⚔️ Declarar Guerra",callback_data="fac_war"),
                 InlineKeyboardButton("🚪 Abandonar",       callback_data="fac_leave")],
                [InlineKeyboardButton("❌ CERRAR",          callback_data="u_close")],
            ])
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡️ Crear Facción",    callback_data="fac_create")],
            [InlineKeyboardButton("🤝 Unirse a Facción", callback_data="fac_join")],
            [InlineKeyboardButton("❌ CERRAR",            callback_data="u_close")],
        ])

    # ── Ajustes ───────────────────────────────────────────
    @staticmethod
    def settings_panel(s: dict) -> InlineKeyboardMarkup:
        b = lambda x: "✅" if x else "❌"
        theme   = s.get("theme","dark").capitalize()
        lang    = s.get("language","es").upper()
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🖋️ Marca Agua: {s.get('watermark') or 'No'}", callback_data="set_watermark")],
            [InlineKeyboardButton(f"📝 Auto-Transcribir: {b(s.get('auto_transcribe'))}", callback_data="set_transcribe")],
            [InlineKeyboardButton(f"👻 Modo Fantasma: {b(s.get('ghost_mode'))}", callback_data="set_ghost")],
            [InlineKeyboardButton(f"📄 Como Documento: {b(s.get('send_as_doc'))}", callback_data="set_doc")],
            [InlineKeyboardButton(f"⚡ Mejor Calidad Auto: {b(s.get('auto_dl_best'))}", callback_data="set_autobest")],
            [InlineKeyboardButton(f"🎨 Tema: {theme}", callback_data="set_theme"),
             InlineKeyboardButton(f"🌐 Idioma: {lang}", callback_data="set_lang")],
            [InlineKeyboardButton(f"🔔 Notificaciones: {b(s.get('notifications_enabled',True))}", callback_data="set_notif")],
            [InlineKeyboardButton("🔐 Configurar 2FA",  callback_data="set_2fa"),
             InlineKeyboardButton("🗝️ Historial Login",  callback_data="set_login_hist")],
            [InlineKeyboardButton("🔑 Cambiar Apodo",   callback_data="set_rename"),
             InlineKeyboardButton("❌ CERRAR",           callback_data="u_close")],
        ])

    # ── Herramientas ──────────────────────────────────────
    @staticmethod
    def tools_panel() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🗣️ TTS",           callback_data="util_tts"),
             InlineKeyboardButton("🔳 QR Code",        callback_data="util_qr")],
            [InlineKeyboardButton("📡 Ping",           callback_data="util_ping"),
             InlineKeyboardButton("🖼️ Miniatura",      callback_data="util_thumb")],
            [InlineKeyboardButton("📜 B64 Enc",        callback_data="util_b64e"),
             InlineKeyboardButton("🔓 B64 Dec",        callback_data="util_b64d")],
            [InlineKeyboardButton("🔐 SHA-256",        callback_data="util_sha"),
             InlineKeyboardButton("🔏 MD5",            callback_data="util_md5")],
            [InlineKeyboardButton("🔄 ROT-13",         callback_data="util_rot"),
             InlineKeyboardButton("📊 Metadatos URL",  callback_data="util_meta")],
            [InlineKeyboardButton("⭐ Añadir Favorito",callback_data="util_fav"),
             InlineKeyboardButton("❌ CERRAR",          callback_data="u_close")],
        ])

    # ── B2B ───────────────────────────────────────────────
    @staticmethod
    def b2b_panel(has_key: bool) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Generar/Regenerar API Key", callback_data="b2b_gen")],
            [InlineKeyboardButton("📖 Documentación",             callback_data="b2b_docs")],
            [InlineKeyboardButton("📊 Uso de API",                callback_data="b2b_usage")],
            [InlineKeyboardButton("❌ CERRAR",                     callback_data="u_close")],
        ])

    # ── Leaderboard ───────────────────────────────────────
    @staticmethod
    def lb_panel() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Puntos",     callback_data="lb_points"),
             InlineKeyboardButton("📥 Descargas",   callback_data="lb_downloads")],
            [InlineKeyboardButton("👥 Referidos",  callback_data="lb_referrals"),
             InlineKeyboardButton("💸 Afiliados",   callback_data="lb_affiliate")],
            [InlineKeyboardButton("🎮 Nivel",      callback_data="lb_level"),
             InlineKeyboardButton("❌ CERRAR",      callback_data="u_close")],
        ])

    # ── P2P Mercado ───────────────────────────────────────
    @staticmethod
    def p2p_panel() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Ver Anuncios",          callback_data="p2p_list")],
            [InlineKeyboardButton("➕ Vender Puntos",          callback_data="p2p_sell")],
            [InlineKeyboardButton("❌ CERRAR",                 callback_data="u_close")],
        ])

    # ── Plan selector admin ───────────────────────────────
    @staticmethod
    def plan_selector() -> InlineKeyboardMarkup:
        rows = [[InlineKeyboardButton(
            f"{EmpireConfig.PLANS[p]['color']} {p}",
            callback_data=f"setplan_{p}") for p in list(EmpireConfig.PLANS.keys())[i:i+2]]
            for i in range(0, len(EmpireConfig.PLANS), 2)]
        rows.append([InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")])
        return InlineKeyboardMarkup(rows)

    # ── Torneos admin ─────────────────────────────────────
    @staticmethod
    def tour_admin() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 24h",   callback_data="tour_start_24"),
             InlineKeyboardButton("🚀 48h",   callback_data="tour_start_48"),
             InlineKeyboardButton("🚀 72h",   callback_data="tour_start_72")],
            [InlineKeyboardButton("🏁 Finalizar", callback_data="tour_end"),
             InlineKeyboardButton("📊 Ver ranking", callback_data="tour_rank")],
            [InlineKeyboardButton("❌ CERRAR",   callback_data="u_close")],
        ])

    @staticmethod
    def clan_war_admin() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⚔️ Iniciar Guerra", callback_data="cw_start")],
            [InlineKeyboardButton("🏁 Finalizar Guerra",callback_data="cw_end")],
            [InlineKeyboardButton("📊 Ver Marcador",    callback_data="cw_scores")],
            [InlineKeyboardButton("❌ CERRAR",           callback_data="u_close")],
        ])

ui = UI()

# ============================================================
# [12] TAREAS BACKGROUND
# ============================================================
async def crypto_task():
    while True:
        await asyncio.sleep(600)
        async with db._lock:
            v = db.data["market_stats"]["crypto_value"]
            f = random.uniform(-0.10, 0.15)
            v = max(5.0, v * (1+f))
            db.data["market_stats"]["crypto_value"] = round(v, 4)
            db.data["market_stats"]["trend"] = "up" if f>0 else "down"
            db.data["market_stats"]["history"].append(round(v,2))
            if len(db.data["market_stats"]["history"])>60:
                db.data["market_stats"]["history"].pop(0)
            await db._save_nolock()

async def cleanup_task():
    while True:
        await asyncio.sleep(3600)
        try:
            now = time.time()
            disk = psutil.disk_usage('/').percent
            count = 0
            for d in [EmpireConfig.BUFFER_DIR, EmpireConfig.QR_DIR, EmpireConfig.TTS_DIR]:
                for f in os.listdir(d):
                    fp = os.path.join(d, f)
                    if os.path.isfile(fp) and (now - os.path.getmtime(fp) > 3600 or disk > 88):
                        try: os.remove(fp); count += 1
                        except: pass
            if count: logger.info(f"🧹 Limpieza: {count} archivos eliminados.")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

async def daily_shop_task():
    while True:
        await asyncio.sleep(3600)
        await db.refresh_daily_shop()

async def tournament_auto_check():
    while True:
        await asyncio.sleep(300)
        t = db.data["system"]["tournament"]
        if t.get("active") and t.get("end_time"):
            try:
                if datetime.datetime.now() > datetime.datetime.fromisoformat(t["end_time"]):
                    winners = await db.finalize_tournament()
                    logger.info(f"🏆 Torneo auto-finalizado. Ganadores: {len(winners)}")
            except: pass

async def clan_war_auto_check():
    while True:
        await asyncio.sleep(300)
        cw = db.data["system"].get("clan_war", {})
        if cw.get("active") and cw.get("end_time"):
            try:
                if datetime.datetime.now() > datetime.datetime.fromisoformat(cw["end_time"]):
                    result = await db.finalize_clan_war()
                    if result: logger.info(f"⚔️ Guerra de clanes finalizada. Ganador: {result.get('winner')}")
            except: pass

# ============================================================
# [13] HANDLERS TELEGRAM — COMANDOS Y MENSAJES
# ============================================================

async def send_long(reply_fn, text: str):
    """Envía textos largos en chunks."""
    for i in range(0, len(text), 4000):
        await reply_fn(text[i:i+4000], parse_mode="Markdown")

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid  = str(user.id)
    if db.data["system"]["maint_mode"] and user.id != EmpireConfig.ADMIN_ID:
        return await update.message.reply_text("🛠️ **MANTENIMIENTO.** Vuelve pronto.")
    if sec.rate_limit(user.id, 3): return
    ref = ctx.args[0] if ctx.args else None
    u, ref_rewarded = await db.get_user(user, ref)
    if ref_rewarded:
        try:
            await ctx.bot.send_message(ref, f"🎉 **REFERIDO REGISTRADO!**\n+{EmpireConfig.ECONOMY['REF_REWARD']} pts por invitar a {user.first_name}.")
        except: pass
    if not u.get("captcha_solved") and user.id != EmpireConfig.ADMIN_ID:
        q = sec.generate_captcha(user.id)
        await update.message.reply_text(f"🛡️ **VERIFICACIÓN ANTI-BOT**\n{q}\n\nResponde solo con el número:")
        ctx.user_data["state"] = "WAIT_CAPTCHA"; return
    lang = u.get("settings",{}).get("language","es")
    welcome = EmpireConfig.LANGUAGES.get(lang, EmpireConfig.LANGUAGES["es"])["welcome"]
    if user.id == EmpireConfig.ADMIN_ID:
        welcome = f"👁️ **SALVE DIRECTOR ISHAK.**\nArquitectura V500 operativa.\nUsuarios: `{db.data['stats']['total_users']}` | Revenue: `{db.data['stats']['stars_revenue']} ⭐️`"
    await update.message.reply_text(welcome, reply_markup=UI.main_kb(u), parse_mode="Markdown")
    sec.log_session(uid, "LOGIN")

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📖 **AYUDA ISHAK EMPIRE V500**\n\n"
        "**Comandos:**\n"
        "`/start` — Arrancar el sistema\n"
        "`/stats` — Tus estadísticas detalladas\n"
        "`/gift <código> [usuario]` — Canjear/regalar tarjeta\n"
        "`/coupon <código>` — Canjear cupón de plan\n"
        "`/ref` — Tu enlace de referidos\n"
        "`/history` — Historial de descargas\n"
        "`/favorites` — Tus URLs favoritas\n"
        "`/2fa` — Gestionar autenticación 2FA\n"
        "`/security` — Ver sesiones y seguridad\n"
        "`/leaderboard [cat]` — Ver ranking\n\n"
        "**Funciones principales:**\n"
        "• 📥 Extracción de vídeo/audio en múltiples formatos\n"
        "• 📦 Descarga en lote (hasta 10 URLs a la vez)\n"
        "• 🎰 Casino con 8 juegos únicos\n"
        "• 💹 Mercado de IshakCoin en tiempo real\n"
        "• 🛡️ Facciones con guerras de clanes\n"
        "• 🤝 Mercado P2P entre usuarios\n"
        "• ⭐ Sistema de referidos de 3 niveles\n"
        "• 🔐 Autenticación 2FA con TOTP\n"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_ref(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u, _ = await db.get_user(user)
    bot_info = await ctx.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={user.id}"
    msg = (
        f"🔗 **TU ENLACE DE REFERIDOS**\n\n`{link}`\n\n"
        f"**Ganancias por referido:**\n"
        f"• Tier 1: +{EmpireConfig.ECONOMY['REF_REWARD']} pts\n"
        f"• Tier 2: +{EmpireConfig.ECONOMY['REF_TIER2']} pts\n"
        f"• Tier 3: +{EmpireConfig.ECONOMY['REF_TIER3']} pts\n\n"
        f"**Comisiones en compras Stars:**\n"
        f"• Tier 1: {EmpireConfig.ECONOMY['AFFILIATE_T1_PCT']*100:.0f}%\n"
        f"• Tier 2: {EmpireConfig.ECONOMY['AFFILIATE_T2_PCT']*100:.0f}%\n"
        f"• Tier 3: {EmpireConfig.ECONOMY['AFFILIATE_T3_PCT']*100:.0f}%\n\n"
        f"👥 Tus referidos: `{u.get('referrals',0)}`\n"
        f"💸 Ganancias afiliado: `{u.get('affiliate_earnings',0):,} pts`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid  = str(user.id)
    u, _ = await db.get_user(user)
    all_u = sorted(db.data["users"].values(), key=lambda x: x.get("points",0), reverse=True)
    rank  = next((i+1 for i,v in enumerate(all_u) if str(v.get("id"))==uid), "?")
    plan_info = EmpireConfig.PLANS[u["plan"]]
    achv_pct  = len(u.get("achievements",[])) / len(EmpireConfig.ACHIEVEMENTS) * 100
    msg = (
        f"📊 **ESTADÍSTICAS DETALLADAS V500**\n\n"
        f"**Identidad:**\n"
        f"• Rango Global: `#{rank}`\n"
        f"• Plan: **{plan_info['name']}**\n"
        f"• Nivel: `{u['level']}` | XP: `{u['xp']}/{u['level']*120}`\n"
        f"• Prestigio: `{u.get('prestige_level',0)}` ⭐\n\n"
        f"**Capital:**\n"
        f"• Puntos: `{u['points']:,}`\n"
        f"• IshakCoins: `{u.get('crypto_balance',0):.4f}`\n"
        f"• Stars gastadas: `{u.get('total_spent_stars',0)}`\n\n"
        f"**Actividad:**\n"
        f"• Descargas hoy: `{u['daily_downloads'][0]}/{plan_info['limit_daily']}`\n"
        f"• Total descargas: `{u.get('total_downloads',0):,}`\n"
        f"• Racha: `{u.get('streak',0)} días 🔥`\n\n"
        f"**Afiliados:**\n"
        f"• Referidos T1/T2/T3: `{u.get('referrals',0)}/{len(u.get('referrals_tier2',[]))}/{len(u.get('referrals_tier3',[]))}`\n"
        f"• Ganancias afiliado: `{u.get('affiliate_earnings',0):,} pts`\n\n"
        f"**Casino:**\n"
        f"• Partidas: `{u['stats'].get('casino_played',0)}`\n"
        f"• BJ wins: `{u['stats'].get('blackjack_wins',0)}` | Mines: `{u['stats'].get('mines_wins',0)}`\n"
        f"• Poker wins: `{u['stats'].get('poker_wins',0)}`\n\n"
        f"**Logros:** `{len(u.get('achievements',[]))}/{len(EmpireConfig.ACHIEVEMENTS)}` ({achv_pct:.0f}%)\n"
        f"**P2P:** Ventas `{u['stats'].get('p2p_sales',0)}` | Compras `{u['stats'].get('p2p_purchases',0)}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u, _ = await db.get_user(user)
    hist = u.get("download_history", [])
    if not hist:
        return await update.message.reply_text("📜 No tienes descargas en el historial aún.")
    lines = ["📜 **HISTORIAL DE DESCARGAS** (últimas 20):\n"]
    for h in reversed(hist[-20:]):
        lines.append(f"• `{h['date'][:16]}` | `{h['format']}` | {h['title'][:30]}... ({h.get('size_mb',0):.1f}MB)")
    await send_long(update.message.reply_text, "\n".join(lines))

async def cmd_favorites(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u, _ = await db.get_user(user)
    favs = u.get("favorites", [])
    if not favs:
        return await update.message.reply_text("⭐ No tienes URLs favoritas guardadas.")
    msg = "⭐ **TUS FAVORITOS:**\n\n"
    for i, url in enumerate(favs[-15:], 1):
        msg += f"`{i}.` {url[:60]}...\n"
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"▶️ Descargar #{i+1}", callback_data=f"fav_dl_{i}")
        for i in range(min(3, len(favs)))]])
    await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")

async def cmd_security(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid  = str(user.id)
    u, _ = await db.get_user(user)
    sec_data = u.get("security", {})
    sessions = sec.get_session_log(uid)[-5:]
    tfa = "✅ Activo" if sec_data.get("two_fa_enabled") else "❌ Inactivo"
    msg = (
        f"🔐 **CENTRO DE SEGURIDAD V500**\n\n"
        f"• 2FA: {tfa}\n"
        f"• Sesiones registradas: `{len(sec.get_session_log(uid))}`\n"
        f"• IPs de confianza: `{len(sec_data.get('trusted_ips',[]))}`\n\n"
        f"**Últimas 5 sesiones:**\n"
    )
    for s in reversed(sessions):
        msg += f"  • `{s['time'][:19]}` — {s['action']}\n"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Gestionar 2FA", callback_data="set_2fa")],
        [InlineKeyboardButton("❌ CERRAR",        callback_data="u_close")],
    ])
    await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")

async def cmd_2fa(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid  = str(user.id)
    u, _ = await db.get_user(user)
    sec_data = u.get("security",{})
    if sec_data.get("two_fa_enabled"):
        await update.message.reply_text(
            "🔐 **2FA ya está activo.**\n\nUsa el botón de Ajustes para desactivarlo o verificar.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Ajustes", callback_data="open_settings")]]))
    else:
        secret, uri = sec.generate_2fa_secret(uid)
        # Guardar en DB
        u["security"]["two_fa_secret"] = encrypt_data(secret)
        await db.save()
        qr_path = await tools.qr(uri, uid)
        msg = (f"🔐 **CONFIGURAR 2FA**\n\nEscanea el QR con Google Authenticator / Authy.\n\n"
               f"O ingresa este código manualmente:\n`{secret}`\n\n"
               f"Luego envía el código de 6 dígitos para confirmar.")
        if qr_path and os.path.exists(qr_path):
            with open(qr_path,'rb') as f:
                await ctx.bot.send_photo(user.id, f, caption=msg, parse_mode="Markdown")
            os.remove(qr_path)
        else:
            await update.message.reply_text(msg, parse_mode="Markdown")
        ctx.user_data["state"] = "WAIT_2FA_VERIFY"

async def cmd_gift(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid  = str(user.id)
    u, _ = await db.get_user(user)
    if not ctx.args:
        await update.message.reply_text("🎁 Uso: `/gift <código>` o `/gift <código> <ID_usuario>`", parse_mode="Markdown"); return
    code = ctx.args[0].strip().upper()
    if len(ctx.args) >= 2:
        target = ctx.args[1].strip()
        target_uid = next((k for k,v in db.data["users"].items()
                           if str(v.get("id"))==target or (v.get("username") or "").lower()==target.lower()), None)
        if not target_uid: return await update.message.reply_text("❌ Usuario no encontrado.")
        ok, msg = await db.redeem_gift_card(target_uid, code)
        if ok:
            await update.message.reply_text(f"🎁 ¡Enviado a **{db.data['users'][target_uid].get('name','?')}**!\n{msg}", parse_mode="Markdown")
            try: await ctx.bot.send_message(target_uid, f"🎁 **Regalo de {user.first_name}!**\n{msg}", parse_mode="Markdown")
            except: pass
        else: await update.message.reply_text(f"❌ {msg}")
    else:
        ok, msg = await db.redeem_gift_card(uid, code)
        await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_coupon(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user; uid = str(user.id)
    u, _ = await db.get_user(user)
    if not ctx.args: return await update.message.reply_text("Uso: `/coupon CÓDIGO`", parse_mode="Markdown")
    code = ctx.args[0].strip().upper()
    if code not in db.data["coupons"]: return await update.message.reply_text("❌ Código inválido o ya usado.")
    coupon = db.data["coupons"][code]
    if isinstance(coupon, dict) and coupon.get("type") == "gift_card":
        ok, msg = await db.redeem_gift_card(uid, code)
        await update.message.reply_text(msg, parse_mode="Markdown")
    elif isinstance(coupon, str) and coupon in EmpireConfig.PLANS:
        u["plan"] = coupon
        days = 30
        u["plan_expiry"] = str(datetime.datetime.now() + datetime.timedelta(days=days)) if coupon not in ["FREE","GOD"] else None
        del db.data["coupons"][code]; await db.save()
        await update.message.reply_text(f"✅ ¡Plan **{coupon}** activado por {days} días!", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Tipo de cupón desconocido.")

async def cmd_leaderboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cat = ctx.args[0] if ctx.args else "points"
    top = await db.get_leaderboard(cat, 10)
    medals = ["🥇","🥈","🥉"]+["4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    cat_names = {"points":"Puntos","downloads":"Descargas","referrals":"Referidos","affiliate":"Afiliados","level":"Nivel"}
    msg = f"🏆 **TOP 10 — {cat_names.get(cat,cat).upper()}**\n\n"
    for i,(name,username,val,plan) in enumerate(top):
        ustr = f"@{username}" if username else name
        color = EmpireConfig.PLANS.get(plan,{}).get("color","⬜")
        msg += f"{medals[i]} {color} `{val:,}` — {ustr[:20]}\n"
    await update.message.reply_text(msg, reply_markup=UI.lb_panel(), parse_mode="Markdown")

# ── Pagos Telegram Stars ───────────────────────────────────
async def precheckout_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.pre_checkout_query
    if q.invoice_payload.startswith("stars_"):
        await q.answer(ok=True)
    else:
        await q.answer(ok=False, error_message="Pago inválido.")

async def payment_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user    = update.message.from_user
    uid     = str(user.id)
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    u, _    = await db.get_user(user)

    if not payload.startswith("stars_"): return
    pack_key = payload.replace("stars_","")
    pack = EmpireConfig.STARS_PACKAGES.get(pack_key)
    if not pack: return

    stars = payment.total_amount
    u["stats"]["stars_spent"] += stars
    u["total_spent_stars"]     = u.get("total_spent_stars",0) + stars
    db.data["stats"]["stars_revenue"] += stars
    asyncio.create_task(db.pay_affiliate_commission(uid, stars))

    msg = ""
    ptype = pack["type"]

    if ptype == "points":
        u["points"] += pack["value"]
        await db.log_tx(uid, pack["value"], f"Stars: {pack['name']}")
        msg = f"✅ Recibidos **{pack['value']:,} pts**."

    elif ptype in ("sub_week","sub_month","sub_year"):
        plan_id = pack["value"]
        days    = {"sub_week":7,"sub_month":30,"sub_year":365}[ptype]
        u["plan"] = plan_id
        base = datetime.datetime.fromisoformat(u["plan_expiry"]) if u.get("plan_expiry") else datetime.datetime.now()
        new_exp = base + datetime.timedelta(days=days)
        u["plan_expiry"] = str(new_exp)
        await db.log_tx(uid, 0, f"Sub {plan_id} ({days}d)")
        msg = f"✅ **{EmpireConfig.PLANS[plan_id]['name']}** activo hasta `{new_exp.date()}`."

    elif ptype == "vip":
        base = datetime.datetime.fromisoformat(u["vip_expiry"]) if u.get("vip_expiry") else datetime.datetime.now()
        new_exp = base + datetime.timedelta(days=30)
        u["vip_expiry"] = str(new_exp)
        if "VIP_MEMBER" not in u.get("achievements",[]): u.setdefault("achievements",[]).append("VIP_MEMBER"); u["points"]+=2000
        msg = f"🥂 **VIP activo** hasta `{new_exp.date()}`."

    elif ptype == "gift_card":
        code = await db.generate_gift_card(pack["value"])
        msg  = f"🎁 Código: `{code}` | Valor: **{pack['value']} pts**."

    elif ptype == "boost":
        val = pack["value"]
        if "xp3" in val:
            u["active_buffs"]["xp_multiplier"] = 3.0
            u["active_buffs"]["buff_expiry"]    = str(datetime.datetime.now()+datetime.timedelta(days=7))
            msg = "🔬 **XP x3 activo por 7 días**."

    elif ptype == "clan_slot":
        fac = u.get("faction")
        if fac and fac in db.data["factions"]:
            db.data["factions"][fac]["max_members"] = db.data["factions"][fac].get("max_members",20) + pack["value"]
            msg = f"🛡️ Clan expandido en **+{pack['value']} slots**."

    # Logros
    if "INVESTOR" not in u.get("achievements",[]):
        u.setdefault("achievements",[]).append("INVESTOR"); u["points"]+=5000; msg+="\n🏆 LOGRO: Inversor! +5000pts"
    if u.get("total_spent_stars",0) >= 1000 and "WHALE" not in u.get("achievements",[]):
        u.setdefault("achievements",[]).append("WHALE"); u["points"]+=15000; msg+="\n🐋 LOGRO: Ballena! +15000pts"

    await db.save()
    audit_logger.log("STARS_PURCHASE", user_id=uid, details={"pack":pack_key,"stars":stars})
    await update.message.reply_text(f"💎 **TRANSACCIÓN CONFIRMADA**\n{msg}", parse_mode="Markdown")

# ============================================================
# [14] DISPATCHER DE MENSAJES PRINCIPAL
# ============================================================
MAIN_COMMANDS = {
    "📥 EXTRACCIÓN", "📦 LOTE DE URLs", "👤 PERFIL", "📊 MIS ESTADÍSTICAS",
    "⭐️ TIENDA STARS", "🏪 MERCADO NEGRO", "🎰 CASINO IMPERIAL",
    "⚙️ AJUSTES PRO", "🛠️ HERRAMIENTAS", "🛡️ FACCIONES",
    "🎁 TRIBUTO DIARIO", "🎮 MISIONES Y LOGROS", "🏆 RANKING GLOBAL",
    "🔔 NOTIFICACIONES", "📜 MI HISTORIAL", "⭐ MIS FAVORITOS",
    "🛒 TIENDA DIARIA", "🎫 CANJEAR CÓDIGO", "🤝 MERCADO P2P", "🎧 SOPORTE",
    "🏢 ÁREA B2B", "👑 PANEL OVERLORD", "🌐 TELEMETRÍA",
    "🏟️ TORNEOS ADMIN", "⚔️ GUERRA DE CLANES", "🥂 SALA VIP",
}

async def msg_dispatcher(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user = update.effective_user
    text = update.message.text.strip()
    uid  = str(user.id)

    if sec.rate_limit(user.id): return
    if sec.check_anomaly(user.id, text):
        return await update.message.reply_text("⚠️ Anomalía detectada. Cálmate.")

    u, _ = await db.get_user(user)
    if u.get("is_banned"):
        return await update.message.reply_text("🚫 Cuenta suspendida.")

    db.data["stats"]["commands_executed"] += 1
    sec.log_session(uid, f"MSG:{text[:30]}")

    # Resetear estado si es comando principal
    if text in MAIN_COMMANDS: ctx.user_data["state"] = None

    state = ctx.user_data.get("state")

    # ── CAPTCHA ───────────────────────────────────────────
    if state == "WAIT_CAPTCHA":
        if sec.verify_captcha(user.id, text):
            u["captcha_solved"] = True; await db.save()
            ctx.user_data["state"] = None
            await update.message.reply_text("✅ Verificado. ¡Bienvenido!", reply_markup=UI.main_kb(u))
        else:
            await update.message.reply_text("❌ Respuesta incorrecta. Inténtalo de nuevo.")
        return

    # ── 2FA VERIFY ────────────────────────────────────────
    if state == "WAIT_2FA_VERIFY":
        sec_data = u.get("security",{})
        stored   = sec_data.get("two_fa_secret")
        if stored:
            try: secret = decrypt_data(stored)
            except: secret = stored
            if sec.verify_2fa(uid, text.strip(), secret):
                u["security"]["two_fa_enabled"]  = True
                u["security"]["two_fa_verified"] = True
                if "TWO_FA_GUARDIAN" not in u.get("achievements",[]): u.setdefault("achievements",[]).append("TWO_FA_GUARDIAN"); u["points"]+=1500
                await db.save(); ctx.user_data["state"] = None
                await update.message.reply_text("✅ **2FA Activado correctamente!** +1500 pts de seguridad.", parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Código 2FA inválido. Inténtalo de nuevo.")
        return

    # ── URL DIRECTA ───────────────────────────────────────
    if not state and re.match(r'^https?://', text):
        url = sec.sanitize_url(text)
        if not url: return await update.message.reply_text("❌ URL bloqueada por seguridad.")
        ctx.user_data["active_url"] = url
        if u.get("settings",{}).get("auto_dl_best"):
            ctx.user_data["active_fmt"]  = "MP4"
            ctx.user_data["active_qlty"] = EmpireConfig.PLANS[u["plan"]]["resolutions"][-1]
            await process_download(update, ctx)
        else:
            asyncio.create_task(media.get_metadata(url))
            await update.message.reply_text("🛠️ Enlace detectado. **Selecciona formato:**",
                                            reply_markup=UI.format_selector(), parse_mode="Markdown")
        return

    # ── COMANDOS PRINCIPALES ──────────────────────────────
    if text == "📥 EXTRACCIÓN":
        await update.message.reply_text("🔗 **ENVÍA EL ENLACE** o palabras clave para buscar:")
        ctx.user_data["state"] = "WAIT_URL"

    elif text == "📦 LOTE DE URLs":
        plan_info = EmpireConfig.PLANS[u["plan"]]
        max_batch = plan_info["batch_urls"]
        if max_batch == 0:
            await update.message.reply_text("❌ Tu plan FREE no soporta descargas en lote.\n💡 Actualiza a STARTER o superior.")
        else:
            await update.message.reply_text(
                f"📦 **MODO LOTE**\nTu plan permite hasta **{max_batch} URLs** por lote.\n\n"
                f"Envía las URLs separadas por saltos de línea:")
            ctx.user_data["state"] = "WAIT_BATCH_URLS"

    elif text == "👤 PERFIL":
        plan_info = EmpireConfig.PLANS[u["plan"]]
        bot_info  = await ctx.bot.get_me()
        ref_link  = f"https://t.me/{bot_info.username}?start={uid}"
        vip_exp   = u.get("vip_expiry")
        is_vip    = vip_exp and datetime.datetime.now() < datetime.datetime.fromisoformat(vip_exp)
        exp_str   = ""
        if u.get("plan_expiry"):
            try: exp_str = f"\n📅 Expira: `{datetime.datetime.fromisoformat(u['plan_expiry']).strftime('%d/%m/%Y')}`"
            except: pass
        msg = (
            f"👤 **PERFIL IMPERIAL V500**\n"
            f"🆔 `{user.id}` | **{u['name']}**\n"
            f"{plan_info['color']} Plan: **{plan_info['name']}**{exp_str}\n"
            f"{'🥂 VIP ' if is_vip else ''}"
            f"🎮 Nivel `{u['level']}` | XP `{u['xp']}/{u['level']*120}`\n"
            f"🛡️ Facción: `{u.get('faction') or 'Sin facción'}`\n"
            f"💰 Puntos: `{u['points']:,}` | 📈 Coins: `{u.get('crypto_balance',0):.4f}`\n"
            f"🔥 Racha: `{u.get('streak',0)} días`\n"
            f"📥 Hoy: `{u['daily_downloads'][0]}/{plan_info['limit_daily']}`\n"
            f"🏆 Logros: `{len(u.get('achievements',[]))}/{len(EmpireConfig.ACHIEVEMENTS)}`\n"
            f"👥 Referidos: `{u.get('referrals',0)}` | 💸 Afiliado: `{u.get('affiliate_earnings',0):,} pts`\n\n"
            f"🔗 **Enlace referido:**\n`{ref_link}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "📊 MIS ESTADÍSTICAS":
        await cmd_stats(update, ctx)

    elif text == "⭐️ TIENDA STARS":
        await update.message.reply_text("⭐️ **TIENDA OFICIAL**\nElige categoría:", reply_markup=UI.stars_shop_main())

    elif text == "🏪 MERCADO NEGRO":
        cv    = round(db.data["market_stats"]["crypto_value"], 2)
        trend = "📈" if db.data["market_stats"]["trend"] == "up" else "📉"
        vol   = db.data["market_stats"].get("volume_24h", 0)
        hist  = db.data["market_stats"].get("history", [])
        if len(hist) >= 2:
            change = (hist[-1]-hist[-2])/max(hist[-2],1)*100
            ch_str = f"({change:+.1f}%)"
        else: ch_str = ""
        msg = (
            f"🏪 **MERCADO CLANDESTINO V500**\n"
            f"💰 Capital: `{u['points']:,} pts`\n"
            f"📈 IshakCoins: `{u.get('crypto_balance',0):.4f}`\n\n"
            f"💹 Precio: `{cv} pts` {trend} {ch_str}\n"
            f"📊 Volumen 24h: `{vol:,} pts`\n\n"
            f"Elige una operación:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📈 Comprar 500pts",   callback_data="crypto_buy_500"),
             InlineKeyboardButton("📈 Comprar 2000pts",  callback_data="crypto_buy_2000")],
            [InlineKeyboardButton("📉 Vender Todo",      callback_data="crypto_sell"),
             InlineKeyboardButton("📊 Ver Gráfico",      callback_data="crypto_chart")],
            [InlineKeyboardButton("🛒 Tienda Ítems",     callback_data="open_shop"),
             InlineKeyboardButton("❌ Cerrar",            callback_data="u_close")],
        ])
        await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")

    elif text == "🎰 CASINO IMPERIAL":
        luck = u.get("active_buffs",{}).get("luck_bonus",0)
        plan_mult = EmpireConfig.PLANS[u["plan"]]["casino_multiplier"]
        msg = (f"🎰 **CASINO IMPERIAL V500**\n"
               f"Multiplicador plan: `x{plan_mult}` | Suerte: `+{luck*100:.0f}%`\n\n"
               f"Elige tu juego:")
        await update.message.reply_text(msg, reply_markup=UI.casino_main(), parse_mode="Markdown")

    elif text == "⚙️ AJUSTES PRO":
        await update.message.reply_text("⚙️ **CONFIGURACIÓN AVANZADA:**", reply_markup=UI.settings_panel(u["settings"]))

    elif text == "🛠️ HERRAMIENTAS":
        await update.message.reply_text("🛠️ **HERRAMIENTAS REALES V500:**", reply_markup=UI.tools_panel())

    elif text == "🛡️ FACCIONES":
        await update.message.reply_text("🛡️ **SISTEMA DE FACCIONES:**", reply_markup=UI.factions_panel(bool(u.get("faction"))))

    elif text == "🎁 TRIBUTO DIARIO":
        total, streak, week_ach, month_ach = await db.process_daily_streak(uid)
        if total == 0:
            return await update.message.reply_text(f"❌ Tributo ya reclamado hoy.\n🔥 Racha: `{streak} días`", parse_mode="Markdown")
        msg = f"{'🔥' if streak>=3 else '✅'} **+{total:,} pts** recibidos.\n🗓️ Racha: **{streak} días**"
        if streak >= 3: msg += f"\n⚡ Bonus racha incluido!"
        if week_ach:  msg += f"\n🏆 ¡RACHA SEMANAL! +{EmpireConfig.ACHIEVEMENTS['STREAK_WEEK']['reward']:,} pts"
        if month_ach: msg += f"\n👑 ¡RACHA MENSUAL! +{EmpireConfig.ACHIEVEMENTS['STREAK_MONTH']['reward']:,} pts"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🎮 MISIONES Y LOGROS":
        bounties = u.get("bounties", [])
        lines = ["📋 **MISIONES DIARIAS:**\n"]
        for b in bounties:
            status = "✅" if b["done"] else f"⏳ {b['progress']}/{b['target']}"
            lines.append(f"• {b['desc']} — {status} → +{b['reward']} pts")
        lines.append("\n🏆 **LOGROS:**\n")
        for k, v in EmpireConfig.ACHIEVEMENTS.items():
            done = k in u.get("achievements",[])
            lines.append(f"{'✅' if done else '🔒'} **{v['name']}**: {v['desc']} → +{v['reward']:,} pts")
        await send_long(update.message.reply_text, "\n".join(lines))

    elif text == "🏆 RANKING GLOBAL":
        await cmd_leaderboard(update, ctx)

    elif text == "🔔 NOTIFICACIONES":
        notifs = [n for n in u.get("notification_queue",[]) if not n.get("read")]
        if not notifs: return await update.message.reply_text("📭 Sin notificaciones pendientes.")
        msg = "📬 **NOTIFICACIONES:**\n\n"
        for n in notifs[-10:]: msg += f"🔹 `{n['timestamp'][:16]}` {n['message']}\n"
        async with db._lock:
            for n in u["notification_queue"]: n["read"] = True
            await db._save_nolock()
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "📜 MI HISTORIAL":
        await cmd_history(update, ctx)

    elif text == "⭐ MIS FAVORITOS":
        await cmd_favorites(update, ctx)

    elif text == "🛒 TIENDA DIARIA":
        await db.refresh_daily_shop()
        shop = db.data["system"]["daily_shop"]
        msg  = f"🛒 **TIENDA DIARIA** (30% descuento)\nRenueva en 24h.\n\n"
        rows = []
        for it in shop.get("items",[]):
            msg += f"• **{it['name']}** ~~{it['original_price']}~~ **{it['price']} pts**\n  {it['desc']}\n"
            rows.append([InlineKeyboardButton(f"🛒 {it['name']} ({it['price']} pts)", callback_data=f"daily_buy_{it['key']}")])
        rows.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")

    elif text == "🎫 CANJEAR CÓDIGO":
        await update.message.reply_text("🎫 Escribe tu código de cupón o tarjeta regalo:")
        ctx.user_data["state"] = "WAIT_REDEEM"

    elif text == "🤝 MERCADO P2P":
        listings = [l for l in db.data.get("p2p_market",[]) if l.get("active")]
        fee_pct  = int(EmpireConfig.ECONOMY["P2P_MARKET_FEE"]*100)
        msg = (f"🤝 **MERCADO P2P**\n"
               f"Comisión del mercado: `{fee_pct}%`\n"
               f"Anuncios activos: `{len(listings)}`\n\n")
        await update.message.reply_text(msg, reply_markup=UI.p2p_panel(), parse_mode="Markdown")

    elif text == "🎧 SOPORTE":
        await update.message.reply_text("📝 Describe tu problema (1 mensaje) para el Alto Mando:")
        ctx.user_data["state"] = "WAIT_TICKET"

    elif text == "🏢 ÁREA B2B" and u["plan"] == "GOD":
        await update.message.reply_text("🏢 **ENTORNO B2B**\nAPI Key encriptada SHA-256:", reply_markup=UI.b2b_panel(bool(u.get("api_key"))))

    elif text == "👑 PANEL OVERLORD" and user.id == EmpireConfig.ADMIN_ID:
        await update.message.reply_text("🛠️ **CENTRO DE COMANDO V500**", reply_markup=UI.overlord_panel())

    elif text == "🌐 TELEMETRÍA" and user.id == EmpireConfig.ADMIN_ID:
        s   = db.data["stats"]
        mem = psutil.virtual_memory()
        disk= psutil.disk_usage('/')
        msg = (
            f"🌐 **TELEMETRÍA V500**\n"
            f"👥 Usuarios: `{s['total_users']}`\n"
            f"📥 Extracciones: `{s['total_downloads']:,}`\n"
            f"📦 Batch DLs: `{s['batch_downloads']:,}`\n"
            f"🎰 Casino spins: `{s['casino_spins']:,}`\n"
            f"⭐ Stars revenue: `{s['stars_revenue']:,}`\n"
            f"🛡️ Fraude bloqueado: `{s['fraud_attempts_blocked']}`\n"
            f"🛠️ Self-healing fixes: `{s['self_healing_fixes']}`\n"
            f"🤝 Volumen P2P: `{s['p2p_volume']:,} pts`\n"
            f"⚔️ Guerras de clanes: `{s['clan_wars_total']}`\n"
            f"💸 Afiliados pagados: `{s['affiliate_payouts']:,} pts`\n\n"
            f"🖥️ CPU: `{psutil.cpu_percent()}%` | RAM: `{mem.percent}%`\n"
            f"💾 Disco: `{disk.percent}%` usado\n"
            f"🚀 {platform.system()} {platform.release()}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🏟️ TORNEOS ADMIN" and user.id == EmpireConfig.ADMIN_ID:
        t = db.data["system"]["tournament"]
        if t.get("active"):
            end_str = datetime.datetime.fromisoformat(t["end_time"]).strftime("%d/%m %H:%M") if t.get("end_time") else "?"
            msg = f"🏟️ **TORNEO ACTIVO**\nFin: `{end_str}` | Participantes: `{len(t.get('participants',{}))}` | Bote: `{t.get('prize_pool',0):,}`"
        else:
            msg = "🏟️ **TORNEOS ADMIN**\nNo hay torneo activo."
        await update.message.reply_text(msg, reply_markup=UI.tour_admin(), parse_mode="Markdown")

    elif text == "⚔️ GUERRA DE CLANES" and user.id == EmpireConfig.ADMIN_ID:
        cw = db.data["system"].get("clan_war",{})
        if cw.get("active"):
            scores = cw.get("scores",{}); facs = cw.get("factions",[])
            msg = f"⚔️ **GUERRA ACTIVA**\n{facs[0] if facs else '?'}: `{scores.get(facs[0],0)}` pts\n{facs[1] if len(facs)>1 else '?'}: `{scores.get(facs[1] if len(facs)>1 else '',0)}` pts"
        else:
            msg = "⚔️ **GUERRA DE CLANES ADMIN**\nNo hay guerra activa."
        await update.message.reply_text(msg, reply_markup=UI.clan_war_admin(), parse_mode="Markdown")

    elif text == "🥂 SALA VIP":
        vip_exp = u.get("vip_expiry")
        is_vip  = vip_exp and datetime.datetime.now() < datetime.datetime.fromisoformat(vip_exp)
        if is_vip:
            exp_str = datetime.datetime.fromisoformat(vip_exp).strftime("%d/%m/%Y")
            msg = (f"🥂 **SALA VIP EXCLUSIVA**\nExpira: `{exp_str}`\n\nBeneficios activos:\n"
                   f"• ✅ Soporte prioritario\n• ✅ Tarjetas regalo especiales\n"
                   f"• ✅ Acceso a eventos VIP\n• ✅ Reset de límite diario")
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Reset Límite Diario", callback_data="vip_reset_limit")],
                [InlineKeyboardButton("📊 Mis Stats VIP",       callback_data="vip_stats")],
                [InlineKeyboardButton("❌ CERRAR",               callback_data="u_close")],
            ])
            await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")
        else:
            await update.message.reply_text("🚫 No tienes VIP activo.\n💡 Compra en ⭐️ Tienda Stars → Gift Cards & Especiales.")

    # ── ESTADOS DE ESPERA ─────────────────────────────────
    elif state == "WAIT_URL":
        if re.match(r'^https?://', text):
            url = sec.sanitize_url(text)
            if not url: return await update.message.reply_text("❌ URL bloqueada.")
            ctx.user_data["active_url"] = url
            asyncio.create_task(media.get_metadata(url))
            await update.message.reply_text("📡 Enlace capturado. **Selecciona formato:**",
                                            reply_markup=UI.format_selector(), parse_mode="Markdown")
            ctx.user_data["state"] = None
        else:
            m = await update.message.reply_text(f"🔍 Buscando: `{text}`...", parse_mode="Markdown")
            try:
                def _search():
                    with yt_dlp.YoutubeDL({"quiet":True,"extract_flat":True,"default_search":"ytsearch5"}) as ydl:
                        return ydl.extract_info(text, download=False).get("entries",[])[:5]
                results = await asyncio.to_thread(_search)
                if results:
                    ctx.user_data["search_results"] = {str(i): r["url"] for i,r in enumerate(results)}
                    kb = [[InlineKeyboardButton(f"{i+1}. {r.get('title','?')[:35]} [{r.get('duration_string','?')}]",
                           callback_data=f"src_{i}")] for i,r in enumerate(results)]
                    kb.append([InlineKeyboardButton("❌ ABORTAR", callback_data="u_close")])
                    await m.edit_text("🎯 **RESULTADOS:**", reply_markup=InlineKeyboardMarkup(kb))
                else:
                    await m.edit_text("❌ Sin resultados.")
            except: await m.edit_text("❌ Error en búsqueda.")
            ctx.user_data["state"] = None

    elif state == "WAIT_BATCH_URLS":
        urls_raw = [l.strip() for l in text.split('\n') if l.strip()]
        valid    = [sec.sanitize_url(u_) for u_ in urls_raw if re.match(r'^https?://', u_)]
        valid    = [u_ for u_ in valid if u_]
        plan_info = EmpireConfig.PLANS[u["plan"]]
        max_b = plan_info["batch_urls"]
        if not valid: return await update.message.reply_text("❌ No se encontraron URLs válidas.")
        valid = valid[:max_b]
        ctx.user_data["batch_urls"] = valid
        await update.message.reply_text(
            f"📦 **{len(valid)} URL(s) detectadas.** Selecciona formato para todas:",
            reply_markup=UI.format_selector())
        ctx.user_data["state"] = "WAIT_BATCH_FMT"

    elif state == "WAIT_TICKET":
        tid  = f"TK-{random.randint(10000,99999)}"
        safe = sec.sanitize_text(text, 1000)
        db.data["tickets"][tid] = {"uid": uid, "text": safe, "status": "OPEN",
                                   "created_at": datetime.datetime.now().isoformat()}
        await db.save()
        await update.message.reply_text(f"✅ Ticket `{tid}` enviado.")
        try:
            tkb = InlineKeyboardMarkup([[InlineKeyboardButton("🔒 Cerrar Ticket", callback_data=f"tc_close_{tid}")]])
            await ctx.bot.send_message(EmpireConfig.ADMIN_ID,
                f"🚨 **TICKET {tid}** de {user.first_name} (`{uid}`):\n{safe}", reply_markup=tkb)
        except: pass
        ctx.user_data["state"] = None

    elif state == "WAIT_REDEEM":
        code = sec.sanitize_text(text.strip().upper(), 30)
        ok, msg = await db.redeem_gift_card(uid, code)
        if ok: await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            if code in db.data["coupons"]:
                coupon = db.data["coupons"][code]
                if isinstance(coupon, str) and coupon in EmpireConfig.PLANS:
                    u["plan"] = coupon
                    u["plan_expiry"] = str(datetime.datetime.now()+datetime.timedelta(days=30)) if coupon not in ["FREE","GOD"] else None
                    del db.data["coupons"][code]; await db.save()
                    await update.message.reply_text(f"✅ Plan **{coupon}** activado 30 días!", parse_mode="Markdown")
                else: await update.message.reply_text(f"❌ {msg}")
            else: await update.message.reply_text(f"❌ {msg}")
        ctx.user_data["state"] = None

    elif state == "WAIT_WATERMARK":
        u["settings"]["watermark"] = sec.sanitize_text(text, 30); await db.save()
        await update.message.reply_text(f"✅ Marca: `{u['settings']['watermark']}`", parse_mode="Markdown")
        ctx.user_data["state"] = None

    elif state == "WAIT_RENAME":
        new_name = sec.sanitize_text(text.strip(), 30)
        if len(new_name) < 2: return await update.message.reply_text("❌ Nombre demasiado corto.")
        if u["inventory"].get("RENAME_CARD",0) > 0:
            u["inventory"]["RENAME_CARD"] -= 1; u["name"] = new_name; await db.save()
            await update.message.reply_text(f"✅ Apodo cambiado a `{new_name}`.", parse_mode="Markdown")
        else: await update.message.reply_text("❌ Necesitas una Tarjeta de Renombre.")
        ctx.user_data["state"] = None

    elif state == "WAIT_TTS":
        m = await update.message.reply_text("🗣️ Generando audio...")
        lang = u.get("settings",{}).get("language","es")
        path = await tools.tts(text, uid, lang)
        if path and os.path.exists(path):
            with open(path,'rb') as f: await ctx.bot.send_voice(user.id, f, caption="🗣️ TTS V500")
            os.remove(path)
        else: await update.message.reply_text("❌ Error en TTS.")
        await m.delete(); ctx.user_data["state"] = None

    elif state == "WAIT_QR":
        m = await update.message.reply_text("🔳 Generando QR...")
        path = await tools.qr(sec.sanitize_text(text, 500), uid)
        if path and os.path.exists(path):
            with open(path,'rb') as f: await ctx.bot.send_photo(user.id, f, caption="🔳 QR generado.")
            os.remove(path)
        else: await update.message.reply_text("❌ Error en QR.")
        await m.delete(); ctx.user_data["state"] = None

    elif state == "WAIT_B64E":
        await update.message.reply_text(f"📜 `{tools.b64enc(text)}`", parse_mode="Markdown")
        ctx.user_data["state"] = None

    elif state == "WAIT_B64D":
        await update.message.reply_text(f"🔓 `{tools.b64dec(text)}`", parse_mode="Markdown")
        ctx.user_data["state"] = None

    elif state == "WAIT_SHA":
        await update.message.reply_text(f"🔐 SHA-256:\n`{tools.sha256(text)}`", parse_mode="Markdown")
        ctx.user_data["state"] = None

    elif state == "WAIT_MD5":
        await update.message.reply_text(f"🔏 MD5:\n`{tools.md5(text)}`", parse_mode="Markdown")
        ctx.user_data["state"] = None

    elif state == "WAIT_ROT":
        await update.message.reply_text(f"🔄 ROT-13:\n`{tools.rot13(text)}`", parse_mode="Markdown")
        ctx.user_data["state"] = None

    elif state == "WAIT_THUMB":
        m = await update.message.reply_text("⏳ Extrayendo miniatura...")
        meta = await media.get_metadata(text.strip())
        thumb = meta.get("thumbnail")
        if thumb: await ctx.bot.send_photo(uid, thumb, caption="🖼️ Miniatura extraída.")
        else: await update.message.reply_text("❌ No se pudo extraer miniatura.")
        await m.delete(); ctx.user_data["state"] = None

    elif state == "WAIT_META":
        m = await update.message.reply_text("⏳ Analizando metadatos...")
        meta = await media.get_metadata(text.strip())
        if meta:
            msg = (f"📊 **METADATOS:**\n• Título: `{meta.get('title','?')}`\n"
                   f"• Autor: `{meta.get('uploader','?')}`\n"
                   f"• Duración: `{meta.get('duration','?')}s`\n"
                   f"• Vistas: `{meta.get('view_count','?')}`\n"
                   f"• Descripción: {meta.get('description','N/A')}")
            await update.message.reply_text(msg, parse_mode="Markdown")
        else: await update.message.reply_text("❌ Sin metadatos.")
        await m.delete(); ctx.user_data["state"] = None

    elif state == "WAIT_FAV_URL":
        url = sec.sanitize_url(text.strip())
        if url:
            added = await db.toggle_favorite(uid, url)
            await update.message.reply_text(f"{'⭐ Añadido a favoritos.' if added else '❌ Eliminado de favoritos.'}")
        else: await update.message.reply_text("❌ URL inválida.")
        ctx.user_data["state"] = None

    elif state == "WAIT_FAC_CREATE":
        name = sec.sanitize_text(text.strip(), 20)
        if len(name) < 3 or name in db.data["factions"]:
            return await update.message.reply_text("❌ Nombre inválido o ya en uso.")
        if u["inventory"].get("CLAN_TICKET",0) > 0:
            u["inventory"]["CLAN_TICKET"] -= 1
            db.data["factions"][name] = {"owner":uid,"members":[uid],"vault":0,"level":1,"max_members":20,"war_wins":0}
            u["faction"] = name
            if "GUILD_MASTER" not in u.get("achievements",[]): u.setdefault("achievements",[]).append("GUILD_MASTER"); u["points"]+=3000
            await db.save()
            await update.message.reply_text(f"✅ Facción **{name}** fundada.", parse_mode="Markdown")
        else: await update.message.reply_text("❌ Necesitas un Ticket de Fundación.")
        ctx.user_data["state"] = None

    elif state == "WAIT_FAC_JOIN":
        name = sec.sanitize_text(text.strip(), 20)
        if name in db.data["factions"]:
            fac = db.data["factions"][name]
            if len(fac["members"]) >= fac.get("max_members",20):
                await update.message.reply_text("❌ Facción llena.")
            else:
                fac["members"].append(uid); u["faction"] = name; await db.save()
                await update.message.reply_text(f"✅ Unido a **{name}**.", parse_mode="Markdown")
        else: await update.message.reply_text("❌ Facción no encontrada.")
        ctx.user_data["state"] = None

    elif state == "WAIT_FAC_DONATE":
        try:
            amt = int(text)
            if amt > 0 and await db.deduct_points(uid, amt):
                fac = u["faction"]
                db.data["factions"][fac]["vault"] += amt; await db.save()
                await update.message.reply_text(f"✅ Donados `{amt} pts` a {fac}.", parse_mode="Markdown")
            else: await update.message.reply_text("❌ Saldo insuficiente.")
        except: await update.message.reply_text("❌ Número inválido.")
        ctx.user_data["state"] = None

    elif state == "WAIT_FAC_WAR":
        target = sec.sanitize_text(text.strip(), 20)
        my_fac = u.get("faction")
        if not my_fac: return await update.message.reply_text("❌ No tienes facción."); ctx.user_data["state"]=None; return
        ok, result = await db.start_clan_war(my_fac, target, hours=48)
        if ok: await update.message.reply_text(f"⚔️ ¡Guerra declarada contra **{target}**!\nID: `{result}`\nDuración: 48h.", parse_mode="Markdown")
        else:  await update.message.reply_text(f"❌ {result}")
        ctx.user_data["state"] = None

    elif state == "WAIT_P2P_SELL":
        try:
            parts = text.strip().split()
            if len(parts) < 2: raise ValueError
            amount = int(parts[0]); price = int(parts[1])
            if amount <= 0 or price <= 0: raise ValueError
            ok, result = await db.create_p2p_listing(uid, "points", amount, price)
            if ok: await update.message.reply_text(f"✅ Anuncio creado. ID: `{result}`\n`{amount} pts` por `{price} pts`.", parse_mode="Markdown")
            else:  await update.message.reply_text(f"❌ {result}")
        except: await update.message.reply_text("❌ Formato: `<cantidad> <precio>`", parse_mode="Markdown")
        ctx.user_data["state"] = None

    # ── ESTADOS ADMIN ─────────────────────────────────────
    elif state == "WAIT_BC" and user.id == EmpireConfig.ADMIN_ID:
        count = 0; m = await update.message.reply_text("📡 Transmitiendo...")
        for sid in list(db.data["users"].keys()):
            try: await ctx.bot.send_message(sid, f"📢 **ISHAK EMPIRE:**\n\n{text}"); count+=1; await asyncio.sleep(0.05)
            except: pass
        await m.edit_text(f"✅ Entregado a {count} súbditos."); ctx.user_data["state"] = None

    elif state == "WAIT_BAN" and user.id == EmpireConfig.ADMIN_ID:
        reason = ctx.user_data.get("ban_reason","Infracción.")
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = True
            db.data["users"][text]["ban_reason"] = reason
            await db.save(); audit_logger.log("USER_BANNED",user_id=int(text),details={"reason":reason},severity="CRITICAL")
            await update.message.reply_text("🚫 Usuario baneado.")
        ctx.user_data["state"] = None

    elif state == "WAIT_UNBAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = False
            db.data["users"][text]["ban_reason"] = None
            await db.save(); audit_logger.log("USER_UNBANNED",user_id=int(text))
            await update.message.reply_text("🔓 Usuario desbaneado.")
        ctx.user_data["state"] = None

    elif state == "WAIT_PTS_ID" and user.id == EmpireConfig.ADMIN_ID:
        ctx.user_data["target_id"] = text.strip()
        await update.message.reply_text("💰 Cantidad a inyectar:")
        ctx.user_data["state"] = "WAIT_PTS_VAL"

    elif state == "WAIT_PTS_VAL" and user.id == EmpireConfig.ADMIN_ID:
        try:
            val = int(text); tid = ctx.user_data["target_id"]
            if tid in db.data["users"]:
                await db.add_points(tid, val); await update.message.reply_text(f"✅ +{val:,} pts a {tid}.")
        except: pass
        ctx.user_data["state"] = None

    elif state == "WAIT_CP_CODE" and user.id == EmpireConfig.ADMIN_ID:
        ctx.user_data["cp_code"] = text.upper().strip()
        await update.message.reply_text("🎫 Plan del cupón (FREE/STARTER/BASIC/PRO/ULTRA/ENTERPRISE/GOD):")
        ctx.user_data["state"] = "WAIT_CP_PLAN"

    elif state == "WAIT_CP_PLAN" and user.id == EmpireConfig.ADMIN_ID:
        plan = text.upper().strip()
        if plan in EmpireConfig.PLANS:
            db.data["coupons"][ctx.user_data["cp_code"]] = plan; await db.save()
            await update.message.reply_text(f"✅ Cupón `{ctx.user_data['cp_code']}` → {plan} creado.")
        else: await update.message.reply_text("❌ Plan inválido.")
        ctx.user_data["state"] = None

    elif state == "WAIT_PLAN_EDIT_ID" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            ctx.user_data["target_user_id"] = text
            await update.message.reply_text(f"🎭 Nuevo plan para `{text}`:", reply_markup=UI.plan_selector())
        else: await update.message.reply_text("❌ Usuario no encontrado.")
        ctx.user_data["state"] = None

    elif state == "WAIT_SEARCH_USER" and user.id == EmpireConfig.ADMIN_ID:
        query = text.strip().lower()
        matches = [(k,v) for k,v in db.data["users"].items()
                   if query in v.get("name","").lower() or query == str(v.get("id",""))
                   or query == (v.get("username","") or "").lower()][:5]
        if not matches: await update.message.reply_text("❌ Sin resultados.")
        else:
            msg = "🔍 **RESULTADOS:**\n"
            for kid,kv in matches:
                msg += f"• `{kv['id']}` | {kv['name']} | {kv['plan']} | {'🚫' if kv.get('is_banned') else '✅'}\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
        ctx.user_data["state"] = None

    elif state == "WAIT_VIP_PUSH" and user.id == EmpireConfig.ADMIN_ID:
        count = 0
        for sid, sv in db.data["users"].items():
            vip_exp = sv.get("vip_expiry")
            if vip_exp and datetime.datetime.now() < datetime.datetime.fromisoformat(vip_exp):
                try: await ctx.bot.send_message(sid, f"🥂 **VIP EXCLUSIVO:**\n{text}"); count+=1; await asyncio.sleep(0.04)
                except: pass
        await update.message.reply_text(f"✅ Push enviado a {count} VIPs.")
        ctx.user_data["state"] = None

    elif state == "WAIT_CW_FAC1" and user.id == EmpireConfig.ADMIN_ID:
        ctx.user_data["cw_fac1"] = text.strip()
        await update.message.reply_text("⚔️ Nombre de la segunda facción:")
        ctx.user_data["state"] = "WAIT_CW_FAC2"

    elif state == "WAIT_CW_FAC2" and user.id == EmpireConfig.ADMIN_ID:
        fac1 = ctx.user_data.get("cw_fac1","")
        fac2 = text.strip()
        ok, result = await db.start_clan_war(fac1, fac2, hours=48)
        if ok: await update.message.reply_text(f"⚔️ ¡Guerra iniciada! `{fac1}` vs `{fac2}`. ID: `{result}`.", parse_mode="Markdown")
        else:  await update.message.reply_text(f"❌ {result}")
        ctx.user_data["state"] = None

    elif state == "WAIT_BATCH_FMT":
        # No llega texto aquí normalmente (es inline), pero por si acaso
        ctx.user_data["state"] = None

# ============================================================
# [15] HANDLER DE CALLBACKS (INLINE BUTTONS)
# ============================================================
async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    uid  = q.from_user.id
    uid_s= str(uid)
    data = q.data
    await q.answer()

    u, _ = await db.get_user(q.from_user)
    luck = u.get("active_buffs",{}).get("luck_bonus",0.0)

    # ── CIERRE ────────────────────────────────────────────
    if data == "u_close":
        try: await q.message.delete()
        except: pass; return

    # ── BÚSQUEDA ──────────────────────────────────────────
    if data.startswith("src_"):
        idx = data.split("_")[1]
        results = ctx.user_data.get("search_results",{})
        if idx in results:
            url = sec.sanitize_url(results[idx])
            if url:
                ctx.user_data["active_url"] = url
                await q.edit_message_text("🛠️ **Selecciona formato:**", reply_markup=UI.format_selector())
            else: await q.edit_message_text("❌ URL inválida.")
        return

    # ── FORMATO / CALIDAD / DESCARGA ─────────────────────
    if data.startswith("fmt_"):
        mode = data.split("_")[1]
        if mode == "back": await q.edit_message_text("🎬 Selecciona formato:", reply_markup=UI.format_selector()); return
        ctx.user_data["active_fmt"] = mode
        if mode in ["MP3","MP3U","GIF","VOICE","VNOA","FLAC","WEBM"]:
            await process_download(update, ctx)
        else:
            await q.edit_message_text("🎥 Selecciona resolución:", reply_markup=UI.quality_selector(u["plan"]))
        return

    if data.startswith("ql_"):
        ctx.user_data["active_qlty"] = data.split("_")[1]
        await process_download(update, ctx)
        return

    # ── BATCH FORMAT ──────────────────────────────────────
    if data.startswith("fmt_") and ctx.user_data.get("state") == "WAIT_BATCH_FMT":
        mode = data.split("_")[1]
        ctx.user_data["active_fmt"]  = mode
        ctx.user_data["active_qlty"] = "720p"
        ctx.user_data["state"] = None
        await process_batch_download(update, ctx)
        return

    # ── FAVORITOS ─────────────────────────────────────────
    if data.startswith("fav_dl_"):
        idx = int(data.split("_")[2])
        favs = u.get("favorites",[])
        if idx < len(favs):
            ctx.user_data["active_url"]  = favs[idx]
            ctx.user_data["active_fmt"]  = "MP4"
            ctx.user_data["active_qlty"] = "720p"
            await process_download(update, ctx)
        return

    # ── TIENDA STARS ──────────────────────────────────────
    if data == "shop_main":
        await q.edit_message_text("⭐️ **TIENDA OFICIAL:**", reply_markup=UI.stars_shop_main()); return

    if data.startswith("shop_cat_"):
        cat = data.replace("shop_cat_","")
        await q.edit_message_text(f"⭐️ **Categoría: {cat.upper()}**", reply_markup=UI.stars_shop_category(cat)); return

    if data.startswith("stars_"):
        pack_key = data.replace("stars_","")
        pack = EmpireConfig.STARS_PACKAGES.get(pack_key)
        if pack:
            await ctx.bot.send_invoice(
                chat_id=uid, title=pack["name"],
                description=f"Pago oficial en Ishak Empire V500: {pack['name']}",
                payload=f"stars_{pack_key}", provider_token="",
                currency="XTR",
                prices=[LabeledPrice(pack["name"], pack["stars"])])
        return

    # ── MERCADO NEGRO / CRYPTO ────────────────────────────
    if data.startswith("crypto_buy_"):
        amt = int(data.split("_")[2])
        ok, msg = await db.trade_crypto(uid_s, amt, buy=True)
        await q.answer(msg, show_alert=True); return

    if data == "crypto_sell":
        ok, msg = await db.trade_crypto(uid_s, 0, buy=False)
        await q.answer(msg, show_alert=True); return

    if data == "crypto_chart":
        hist = db.data["market_stats"].get("history",[])
        if len(hist) >= 2:
            mn = min(hist); mx = max(hist)
            bars = ""
            for v in hist[-15:]:
                normalized = int((v-mn)/(mx-mn+1)*8)
                bars += "▁▂▃▄▅▆▇█"[normalized]
            trend = "📈" if hist[-1] > hist[-2] else "📉"
            msg = (f"📊 **GRÁFICO ISHAKCOIN (últimos puntos)**\n\n"
                   f"`{bars}`\n\n"
                   f"Min: `{mn:.0f}` | Max: `{mx:.0f}` | Actual: `{hist[-1]:.2f}` {trend}")
            await q.edit_message_text(msg, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌", callback_data="u_close")]]))
        return

    if data == "open_shop":
        cv = round(db.data["market_stats"]["crypto_value"],2)
        rows = [[InlineKeyboardButton(f"🛒 {v['name']} ({v['price']} pts)", callback_data=f"buy_item_{k}")]
                for k,v in EmpireConfig.SHOP_ITEMS.items()]
        rows.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
        await q.edit_message_text(f"🛒 **TIENDA DE ÍTEMS**\n💹 IshakCoin: `{cv} pts`",
                                  reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
        return

    if data.startswith("buy_item_"):
        key  = data.replace("buy_item_","")
        item = EmpireConfig.SHOP_ITEMS.get(key)
        if not item: return
        # Plan restriction
        if key == "XP_BOOST_X3" and u["plan"] not in ["ULTRA","ENTERPRISE","GOD"]:
            await q.answer("❌ Requiere plan ULTRA o superior.", show_alert=True); return
        if await db.deduct_points(uid_s, item["price"]):
            if key == "XP_BOOST_X2":
                u["active_buffs"]["xp_multiplier"] = 2.0
                u["active_buffs"]["buff_expiry"]    = str(datetime.datetime.now()+datetime.timedelta(days=1))
            elif key == "XP_BOOST_X3":
                u["active_buffs"]["xp_multiplier"] = 3.0
                u["active_buffs"]["buff_expiry"]    = str(datetime.datetime.now()+datetime.timedelta(days=1))
            elif key == "LUCK_CHARM":
                u["active_buffs"]["luck_bonus"] = 0.15
                u["active_buffs"]["buff_expiry"] = str(datetime.datetime.now()+datetime.timedelta(days=1))
            elif key == "LOOT_BOX":
                prize = random.choice([500,1000,2000,5000,10000,25000,50000])
                u["points"] += prize
                await q.message.reply_text(f"🎁 ¡Caja Loot! Ganaste **{prize:,} pts**!", parse_mode="Markdown")
            elif key == "PRESTIGE_TOKEN":
                u["prestige_level"] = u.get("prestige_level",0)+1
                if "PRESTIGE" not in u.get("achievements",[]): u.setdefault("achievements",[]).append("PRESTIGE"); u["points"]+=100000
            else:
                u["inventory"][key] = u["inventory"].get(key,0)+1
            await db.save()
            await q.answer(f"✅ {item['name']} adquirido.", show_alert=True)
        else:
            await q.answer("❌ Puntos insuficientes.", show_alert=True)
        return

    if data.startswith("daily_buy_"):
        key  = data.replace("daily_buy_","")
        shop = db.data["system"]["daily_shop"]
        it   = next((i for i in shop.get("items",[]) if i["key"]==key), None)
        if not it: return
        if await db.deduct_points(uid_s, it["price"]):
            u["inventory"][key] = u["inventory"].get(key,0)+1; await db.save()
            await q.answer(f"✅ {it['name']} comprado con 30% off!", show_alert=True)
        else:
            await q.answer("❌ Puntos insuficientes.", show_alert=True)
        return

    # ── CASINO ────────────────────────────────────────────
    if data == "cas_back":
        await q.edit_message_text("🎰 **CASINO V500:**", reply_markup=UI.casino_main()); return

    if data == "cas_slots":
        bet = 100
        if not await db.deduct_points(uid_s, bet):
            await q.answer("❌ Puntos insuficientes.", show_alert=True); return
        db.data["stats"]["casino_spins"] += 1
        u["stats"]["casino_played"] = u["stats"].get("casino_played",0)+1
        w, msg = casino.play_slots(bet, luck)
        await db.add_points(uid_s, w); await db.save()
        await db.update_bounty(uid_s, "casino_5", 1)
        await db.update_bounty(uid_s, "casino_20", 1)
        await q.edit_message_text(msg, reply_markup=UI.casino_main(), parse_mode="Markdown")
        return

    if data == "cas_roulette_menu":
        await q.edit_message_text("🎡 **RULETA** (250 pts)\nElige tu apuesta:", reply_markup=UI.roulette_menu())
        return

    if data.startswith("cas_rul_"):
        choice = data.replace("cas_rul_","")
        bet = 250
        if not await db.deduct_points(uid_s, bet):
            await q.answer("❌ Puntos insuficientes.", show_alert=True); return
        db.data["stats"]["casino_spins"] += 1
        u["stats"]["casino_played"] = u["stats"].get("casino_played",0)+1
        w, msg = casino.play_roulette(bet, choice, luck)
        await db.add_points(uid_s, w); await db.save()
        await db.update_bounty(uid_s, "casino_5", 1)
        await q.edit_message_text(msg, reply_markup=UI.casino_main(), parse_mode="Markdown")
        return

    if data == "cas_bj":
        bet = 500
        if not await db.deduct_points(uid_s, bet):
            await q.answer("❌ Puntos insuficientes.", show_alert=True); return
        db.data["stats"]["casino_spins"] += 1
        u["stats"]["casino_played"] = u["stats"].get("casino_played",0)+1
        p = [casino.draw_card(), casino.draw_card()]
        d = [casino.draw_card()]
        ctx.user_data["bj_p"] = p; ctx.user_data["bj_d"] = d
        pv = casino.hand_value(p)
        msg = (f"🃏 **BLACKJACK** (Apuesta: {bet})\n\n"
               f"Tu mano: {p} = `{pv}`\nCrupier: {d} + [?]")
        await q.edit_message_text(msg, reply_markup=UI.bj_panel(bet), parse_mode="Markdown")
        return

    if data.startswith("bj_"):
        parts  = data.split("_"); action = parts[1]; bet = int(parts[2])
        p_hand = ctx.user_data.get("bj_p", []); d_hand = ctx.user_data.get("bj_d", [])
        if action == "hit":
            p_hand.append(casino.draw_card()); pv = casino.hand_value(p_hand)
            if pv > 21:
                await q.edit_message_text(f"💥 **BUST!** {p_hand} = `{pv}`\nPierdes {bet} pts.", reply_markup=UI.casino_main())
                await db.save()
            else:
                await q.edit_message_text(f"🃏 Tu mano: {p_hand} = `{pv}`\nCrupier: {d_hand} + [?]",
                                          reply_markup=UI.bj_panel(bet), parse_mode="Markdown")
        elif action in ("stand","double"):
            if action == "double":
                extra_bet = bet
                if not await db.deduct_points(uid_s, extra_bet):
                    await q.answer("❌ Sin fondos para doblar.", show_alert=True); return
                bet *= 2
                p_hand.append(casino.draw_card())
            while casino.hand_value(d_hand) < 17: d_hand.append(casino.draw_card())
            pv = casino.hand_value(p_hand); dv = casino.hand_value(d_hand)
            if pv > 21: result_msg = "💥 BUST! Perdiste."
            elif dv > 21 or pv > dv:
                win = bet*2; await db.add_points(uid_s, win)
                u["stats"]["blackjack_wins"] = u["stats"].get("blackjack_wins",0)+1
                result_msg = f"🎉 ¡GANASTE! +{win} pts."
                if u["stats"]["blackjack_wins"] >= 10 and "CARD_SHARK" not in u.get("achievements",[]):
                    u.setdefault("achievements",[]).append("CARD_SHARK"); u["points"]+=3000
                    result_msg += "\n🏆 LOGRO: Tiburón! +3000pts"
            elif pv == dv:
                await db.add_points(uid_s, bet); result_msg = "🤝 Empate. Recuperas tu apuesta."
            else: result_msg = "💀 Crupier gana."
            await db.save()
            await q.edit_message_text(
                f"🃏 **RESULTADO BJ**\nTú: {p_hand}=`{pv}` | Crupier: {d_hand}=`{dv}`\n{result_msg}",
                reply_markup=UI.casino_main(), parse_mode="Markdown")
        return

    if data == "cas_crash":
        bet = 1000
        if not await db.deduct_points(uid_s, bet):
            await q.answer("❌ Puntos insuficientes.", show_alert=True); return
        db.data["stats"]["casino_spins"] += 1
        u["stats"]["casino_played"] = u["stats"].get("casino_played",0)+1
        cp = casino.calc_crash()
        ctx.user_data["crash_point"] = cp
        await q.edit_message_text(f"📈 **CRASH** (Apuesta: {bet})\n🚀 Multiplicador: `1.00x`",
                                  reply_markup=UI.crash_panel(bet, 1.0))
        asyncio.create_task(_crash_ticker(ctx.bot, uid, q.message.message_id, bet, cp, ctx))
        return

    if data.startswith("crash_co_"):
        parts = data.split("_"); bet = int(parts[2]); mult = float(parts[3])
        cp    = ctx.user_data.pop("crash_point", -1)
        if cp == -1: await q.answer("Ya explotó o ya saltaste.", show_alert=True); return
        if mult <= cp:
            win = int(bet * mult); await db.add_points(uid_s, win); await db.save()
            await q.edit_message_text(f"✅ **CASH OUT** a `{mult}x`!\n+{win} pts.",
                                      reply_markup=UI.casino_main(), parse_mode="Markdown")
        else:
            await q.answer("El cohete ya explotó.", show_alert=True)
        return

    if data == "cas_mines_menu":
        await q.edit_message_text("💣 **MINES** — Elige dificultad (apuesta: 500 pts):", reply_markup=UI.mines_menu())
        return

    if data.startswith("cas_mines_"):
        mines_n = int(data.replace("cas_mines_",""))
        bet = 500
        if not await db.deduct_points(uid_s, bet):
            await q.answer("❌ Puntos insuficientes.", show_alert=True); return
        db.data["stats"]["casino_spins"] += 1
        u["stats"]["casino_played"] = u["stats"].get("casino_played",0)+1
        state_mines = casino.init_mines(mines_n)
        ctx.user_data["mines_state"] = state_mines
        ctx.user_data["mines_bet"]   = bet
        await db.save()
        msg = f"💣 **MINES** ({mines_n} minas) — Apuesta: {bet} pts\n💎 Clica casillas para ganar. Evita las minas!"
        await q.edit_message_text(msg, reply_markup=UI.mines_grid(state_mines, bet), parse_mode="Markdown")
        return

    if data.startswith("mines_click_"):
        parts = data.split("_"); pos = int(parts[2]); bet = int(parts[3])
        state_mines = ctx.user_data.get("mines_state")
        if not state_mines or state_mines.get("game_over"):
            await q.answer("Juego ya terminado.", show_alert=True); return
        is_mine, game_over, mult = casino.mines_click(state_mines, pos)
        if is_mine:
            await q.edit_message_text(f"💥 **¡MINA!** Perdiste {bet} pts.\nMultiplicador alcanzado antes: `x{mult:.2f}`",
                                      reply_markup=UI.casino_main(), parse_mode="Markdown")
            ctx.user_data.pop("mines_state", None)
        elif game_over:
            win = int(bet * mult); await db.add_points(uid_s, win); await db.save()
            u["stats"]["mines_wins"] = u["stats"].get("mines_wins",0)+1
            await q.edit_message_text(f"🎉 ¡CAMPO LIMPIO! x`{mult:.2f}` → +{win} pts.",
                                      reply_markup=UI.casino_main(), parse_mode="Markdown")
            ctx.user_data.pop("mines_state", None)
        else:
            await q.edit_message_text(f"💎 Casilla segura! Mult actual: `x{mult:.2f}`\nContinúa o haz Cash Out:",
                                      reply_markup=UI.mines_grid(state_mines, bet), parse_mode="Markdown")
        return

    if data.startswith("mines_cashout_"):
        bet = int(data.split("_")[2])
        state_mines = ctx.user_data.pop("mines_state", None)
        if not state_mines: await q.answer("Sin juego activo.", show_alert=True); return
        safe = state_mines["safe_clicked"]; m_ = state_mines["mines_count"]; g = state_mines["grid_size"]
        mult = max(1.0, (g/(g-m_))**safe*0.97) if safe > 0 else 1.0
        win  = int(bet * mult); await db.add_points(uid_s, win); await db.save()
        await q.edit_message_text(f"💰 **CASH OUT** x`{mult:.2f}`\n+{win} pts.", reply_markup=UI.casino_main(), parse_mode="Markdown")
        return

    if data == "mines_quit":
        ctx.user_data.pop("mines_state", None)
        await q.edit_message_text("🏳️ Te rendiste. Perdiste la apuesta.", reply_markup=UI.casino_main())
        return
    if data == "mines_noop": return

    if data == "cas_plinko":
        bet = 300
        if not await db.deduct_points(uid_s, bet):
            await q.answer("❌ Puntos insuficientes.", show_alert=True); return
        db.data["stats"]["casino_spins"] += 1
        u["stats"]["casino_played"] = u["stats"].get("casino_played",0)+1
        win, msg, mult = casino.play_plinko(bet, luck_bonus=luck)
        await db.add_points(uid_s, win); await db.save()
        if mult >= 25 and "PLINKO_KING" not in u.get("achievements",[]):
            u.setdefault("achievements",[]).append("PLINKO_KING"); u["points"]+=5000; msg+="\n🏆 LOGRO: Rey Plinko! +5000pts"; await db.save()
        await q.edit_message_text(msg, reply_markup=UI.casino_main(), parse_mode="Markdown")
        return

    if data == "cas_dice_menu":
        await q.edit_message_text("🎲 **DADOS** (200 pts)\nElige tu predicción:", reply_markup=UI.dice_menu())
        return

    if data.startswith("cas_dice_"):
        pred = data.replace("cas_dice_","")
        bet  = 200
        if not await db.deduct_points(uid_s, bet):
            await q.answer("❌ Puntos insuficientes.", show_alert=True); return
        db.data["stats"]["casino_spins"] += 1
        u["stats"]["casino_played"] = u["stats"].get("casino_played",0)+1
        win, msg = casino.play_dice(bet, pred, luck)
        await db.add_points(uid_s, win); await db.save()
        await q.edit_message_text(msg, reply_markup=UI.casino_main(), parse_mode="Markdown")
        return

    if data == "cas_poker":
        bet = 1000
        if not await db.deduct_points(uid_s, bet):
            await q.answer("❌ Puntos insuficientes.", show_alert=True); return
        db.data["stats"]["casino_spins"] += 1
        u["stats"]["casino_played"] = u["stats"].get("casino_played",0)+1
        hand = casino.deal_poker_hand()
        hand_name, mult = casino.eval_poker_hand(hand)
        win = int(bet * mult) if mult > 0 else 0
        await db.add_points(uid_s, win)
        if mult > 0: u["stats"]["poker_wins"] = u["stats"].get("poker_wins",0)+1
        if u["stats"].get("poker_wins",0) >= 50 and "POKER_PRO" not in u.get("achievements",[]):
            u.setdefault("achievements",[]).append("POKER_PRO"); u["points"]+=8000
            await q.message.reply_text("🏆 LOGRO: Profesional Poker! +8000pts")
        await db.save()
        hand_str = " | ".join(hand)
        msg = (f"🃏 **POKER 5 CARTAS** (Apuesta: {bet})\n\n"
               f"Tu mano: `{hand_str}`\n\n"
               f"Resultado: **{hand_name}**\n"
               f"Multiplicador: `x{mult}`\n"
               f"{'💰 Ganaste **'+str(win)+' pts**!' if win>0 else '💀 Sin combinación. Pierdes.'}")
        await q.edit_message_text(msg, reply_markup=UI.casino_main(), parse_mode="Markdown")
        return

    # ── AJUSTES ───────────────────────────────────────────
    if data.startswith("set_"):
        action = data.replace("set_","")
        if action == "watermark":
            await q.message.reply_text("✍️ Escribe tu marca de agua (max 30 chars):")
            ctx.user_data["state"] = "WAIT_WATERMARK"
        elif action == "transcribe":
            u["settings"]["auto_transcribe"] = not u["settings"].get("auto_transcribe"); await db.save()
            await q.edit_message_reply_markup(reply_markup=UI.settings_panel(u["settings"]))
        elif action == "ghost":
            if u["plan"] in ["ULTRA","ENTERPRISE","GOD"]:
                u["settings"]["ghost_mode"] = not u["settings"].get("ghost_mode"); await db.save()
                await q.edit_message_reply_markup(reply_markup=UI.settings_panel(u["settings"]))
            else: await q.answer("❌ Requiere ULTRA+.", show_alert=True)
        elif action == "doc":
            u["settings"]["send_as_doc"] = not u["settings"].get("send_as_doc"); await db.save()
            await q.edit_message_reply_markup(reply_markup=UI.settings_panel(u["settings"]))
        elif action == "autobest":
            u["settings"]["auto_dl_best"] = not u["settings"].get("auto_dl_best"); await db.save()
            await q.edit_message_reply_markup(reply_markup=UI.settings_panel(u["settings"]))
        elif action == "theme":
            themes = ["dark","light","midnight","neon","minimal"]
            cur = u["settings"].get("theme","dark")
            u["settings"]["theme"] = themes[(themes.index(cur)+1)%len(themes)]; await db.save()
            await q.edit_message_reply_markup(reply_markup=UI.settings_panel(u["settings"]))
            await q.answer(f"Tema: {u['settings']['theme'].capitalize()}")
        elif action == "lang":
            langs = list(EmpireConfig.LANGUAGES.keys())
            cur = u["settings"].get("language","es")
            u["settings"]["language"] = langs[(langs.index(cur)+1)%len(langs)]; await db.save()
            await q.edit_message_reply_markup(reply_markup=UI.settings_panel(u["settings"]))
            await q.answer(f"Idioma: {u['settings']['language'].upper()}")
        elif action == "notif":
            u["settings"]["notifications_enabled"] = not u["settings"].get("notifications_enabled",True); await db.save()
            await q.edit_message_reply_markup(reply_markup=UI.settings_panel(u["settings"]))
        elif action == "2fa":
            await q.message.reply_text("🔐 Usa el comando `/2fa` para configurar la autenticación de dos factores.", parse_mode="Markdown")
        elif action == "login_hist":
            sessions = sec.get_session_log(uid_s)[-10:]
            msg = "🗝️ **HISTORIAL DE SESIONES:**\n"
            for s in reversed(sessions): msg += f"• `{s['time'][:19]}` — {s['action']}\n"
            await q.message.reply_text(msg or "Sin historial.", parse_mode="Markdown")
        elif action == "rename":
            if u["inventory"].get("RENAME_CARD",0)>0:
                await q.message.reply_text("📝 Escribe tu nuevo apodo:"); ctx.user_data["state"]="WAIT_RENAME"
            else: await q.answer("❌ Necesitas una Tarjeta de Renombre (Tienda).", show_alert=True)
        elif action == "open_settings":
            await q.edit_message_text("⚙️ **CONFIGURACIÓN:**", reply_markup=UI.settings_panel(u["settings"]))
        return

    # ── HERRAMIENTAS ──────────────────────────────────────
    if data.startswith("util_"):
        act = data.replace("util_","")
        if act == "tts":   await q.message.reply_text("🗣️ Escribe el texto para TTS (max 500 chars):"); ctx.user_data["state"]="WAIT_TTS"
        elif act == "qr":  await q.message.reply_text("🔳 Envía texto o URL para el QR:"); ctx.user_data["state"]="WAIT_QR"
        elif act == "b64e":await q.message.reply_text("📜 Texto a codificar en Base64:"); ctx.user_data["state"]="WAIT_B64E"
        elif act == "b64d":await q.message.reply_text("🔓 Base64 a decodificar:"); ctx.user_data["state"]="WAIT_B64D"
        elif act == "sha": await q.message.reply_text("🔐 Texto para SHA-256:"); ctx.user_data["state"]="WAIT_SHA"
        elif act == "md5": await q.message.reply_text("🔏 Texto para MD5:"); ctx.user_data["state"]="WAIT_MD5"
        elif act == "rot": await q.message.reply_text("🔄 Texto para ROT-13:"); ctx.user_data["state"]="WAIT_ROT"
        elif act == "thumb":await q.message.reply_text("🖼️ URL para extraer miniatura:"); ctx.user_data["state"]="WAIT_THUMB"
        elif act == "meta":await q.message.reply_text("📊 URL para metadatos:"); ctx.user_data["state"]="WAIT_META"
        elif act == "fav": await q.message.reply_text("⭐ URL para añadir/quitar favoritos:"); ctx.user_data["state"]="WAIT_FAV_URL"
        elif act == "ping":
            m = await q.message.reply_text("📡 Ejecutando ping...")
            lat = await tools.ping()
            await m.edit_text(f"📡 Latencia: `{lat}`", parse_mode="Markdown")
        return

    # ── FACCIONES ─────────────────────────────────────────
    if data.startswith("fac_"):
        action = data.replace("fac_","")
        if action == "create":
            await q.message.reply_text("🛡️ Nombre de tu nueva facción (3-20 chars):"); ctx.user_data["state"]="WAIT_FAC_CREATE"
        elif action == "join":
            await q.message.reply_text("🤝 Nombre exacto de la facción:"); ctx.user_data["state"]="WAIT_FAC_JOIN"
        elif action == "info":
            fname = u.get("faction")
            if fname and fname in db.data["factions"]:
                fac = db.data["factions"][fname]
                msg = (f"🛡️ **{fname}**\n👑 Dueño: `{fac['owner']}`\n"
                       f"👥 Miembros: `{len(fac['members'])}/{fac.get('max_members',20)}`\n"
                       f"💰 Bóveda: `{fac['vault']:,} pts`\n"
                       f"📈 Nivel: `{fac['level']}` | ⚔️ Guerras ganadas: `{fac.get('war_wins',0)}`")
                await q.message.reply_text(msg, parse_mode="Markdown")
        elif action == "members":
            fname = u.get("faction")
            if fname and fname in db.data["factions"]:
                members = db.data["factions"][fname]["members"]
                msg = f"👥 **Miembros de {fname}:**\n"
                for m_uid in members[:20]:
                    m_user = db.data["users"].get(m_uid,{})
                    msg += f"• {m_user.get('name','?')} | Lvl {m_user.get('level',1)}\n"
                await q.message.reply_text(msg, parse_mode="Markdown")
        elif action == "donate":
            await q.message.reply_text("💰 Cantidad de puntos a donar:"); ctx.user_data["state"]="WAIT_FAC_DONATE"
        elif action == "upgrade":
            fname = u.get("faction")
            if fname in db.data["factions"]:
                fac = db.data["factions"][fname]
                cost = 10000 * fac.get("level",1)
                if fac["vault"] >= cost:
                    fac["vault"] -= cost; fac["level"] += 1; await db.save()
                    await q.message.reply_text(f"⭐ ¡Facción {fname} subió al nivel {fac['level']}! (coste: {cost:,} pts)")
                else: await q.answer(f"❌ Bóveda necesita {cost:,} pts.", show_alert=True)
        elif action == "war":
            await q.message.reply_text("⚔️ Nombre de la facción enemiga:"); ctx.user_data["state"]="WAIT_FAC_WAR"
        elif action == "leave":
            fname = u.get("faction")
            if fname and fname in db.data["factions"]:
                fac = db.data["factions"][fname]
                if uid_s in fac["members"]: fac["members"].remove(uid_s)
                if uid_s == fac["owner"] and fac["members"]:
                    fac["owner"] = fac["members"][0]
                u["faction"] = None; await db.save()
                await q.edit_message_text("🚪 Has abandonado la facción.")
        return

    # ── B2B ───────────────────────────────────────────────
    if data == "b2b_gen":
        if u["plan"] != "GOD": await q.answer("❌ Solo para GOD.", show_alert=True); return
        for k,v in list(db.data["b2b_api_keys"].items()):
            if v == uid_s: del db.data["b2b_api_keys"][k]
        new_key = f"sk_live_{uuid.uuid4().hex}"
        hashed  = hashlib.sha256(new_key.encode()).hexdigest()
        u["api_key"] = hashed; db.data["b2b_api_keys"][hashed] = uid_s
        if "HACKER" not in u.get("achievements",[]): u.setdefault("achievements",[]).append("HACKER"); u["points"]+=1000
        await db.save(); audit_logger.log("API_KEY_GEN",user_id=uid)
        await q.edit_message_text(
            f"🔑 **API KEY GENERADA (¡Guárdala!)**\n`{new_key}`\n\n*Header: `X-API-KEY: tu_clave`*",
            reply_markup=UI.b2b_panel(True), parse_mode="Markdown")
        return

    if data == "b2b_docs":
        await q.edit_message_text(
            "📖 **API B2B V500**\n\n"
            "**POST** `/api/v1/extract`\nHeader: `X-API-KEY`\nBody: `{\"url\":\"...\"}`\n\n"
            "**GET** `/api/v4/metrics` — Métricas JSON\n"
            "**GET** `/health` — Health check\n"
            "**GET** `/metrics` — Prometheus\n"
            "**GET** `/api/docs` — Swagger UI\n"
            "**GET** `/api/v1/users/export` — Exportar CSV (admin)\n"
            "**GET** `/api/v1/leaderboard` — Top usuarios",
            reply_markup=UI.b2b_panel(True))
        return

    if data == "b2b_usage":
        keys = len(db.data.get("b2b_api_keys",{}))
        await q.edit_message_text(f"📊 **Uso API B2B**\n• Claves activas: `{keys}`\n• Endpoint: `/api/v1/extract`",
                                  reply_markup=UI.b2b_panel(True), parse_mode="Markdown")
        return

    # ── LEADERBOARD ───────────────────────────────────────
    if data.startswith("lb_"):
        cat = data.replace("lb_","")
        top = await db.get_leaderboard(cat, 10)
        medals = ["🥇","🥈","🥉"]+["4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        cat_names = {"points":"Puntos","downloads":"Descargas","referrals":"Referidos","affiliate":"Afiliados","level":"Nivel"}
        msg = f"🏆 **TOP 10 — {cat_names.get(cat,cat).upper()}**\n\n"
        for i,(name,username,val,plan) in enumerate(top):
            ustr  = f"@{username}" if username else name
            color = EmpireConfig.PLANS.get(plan,{}).get("color","⬜")
            msg  += f"{medals[i]} {color} `{val:,}` — {ustr[:20]}\n"
        await q.edit_message_text(msg, reply_markup=UI.lb_panel(), parse_mode="Markdown")
        return

    # ── P2P ───────────────────────────────────────────────
    if data == "p2p_list":
        listings = [l for l in db.data.get("p2p_market",[]) if l.get("active")][:10]
        if not listings: await q.edit_message_text("📭 No hay anuncios activos.", reply_markup=UI.p2p_panel()); return
        rows = []
        for l in listings:
            seller = db.data["users"].get(l["seller"],{}).get("name","?")[:10]
            rows.append([InlineKeyboardButton(
                f"{l['amount']:,} {l['type']} por {l['price']:,} pts — {seller}",
                callback_data=f"p2p_buy_{l['id']}")])
        rows.append([InlineKeyboardButton("⬅️ Volver", callback_data="p2p_back"),
                     InlineKeyboardButton("❌ Cerrar",  callback_data="u_close")])
        await q.edit_message_text("📜 **ANUNCIOS ACTIVOS:**", reply_markup=InlineKeyboardMarkup(rows), parse_mode="Markdown")
        return

    if data.startswith("p2p_buy_"):
        lid = data.replace("p2p_buy_","")
        ok, msg = await db.buy_p2p_listing(uid_s, lid)
        if ok:
            if "MARKET_BARON" not in u.get("achievements",[]) and u["stats"].get("p2p_purchases",0) >= 10:
                u.setdefault("achievements",[]).append("MARKET_BARON"); u["points"]+=5000; await db.save()
        await q.answer(msg, show_alert=True)
        return

    if data == "p2p_sell":
        await q.message.reply_text("💰 Escribe `<cantidad_pts> <precio_pts>` para poner en venta:\nEjemplo: `5000 4500`")
        ctx.user_data["state"] = "WAIT_P2P_SELL"
        return

    if data == "p2p_back":
        await q.edit_message_text("🤝 **MERCADO P2P:**", reply_markup=UI.p2p_panel())
        return

    # ── ADMIN CALLBACKS ───────────────────────────────────
    if data.startswith("adm_") and uid == EmpireConfig.ADMIN_ID:
        if data.startswith("adm_list_"):
            page  = int(data.split("_")[2])
            users = list(db.data["users"].items())
            start = page*10; end = start+10
            msg   = f"👥 **USUARIOS (pág {page+1}/{math.ceil(len(users)/10)}):**\n"
            for sid,d in users[start:end]:
                ban = "🚫" if d.get("is_banned") else "✅"
                msg += f"{ban} `{sid}` | {d.get('name','?')[:10]} | Lv{d.get('level',1)} | {d.get('plan','?')} | {d.get('points',0):,}pts\n"
            kb = [[InlineKeyboardButton("⬅️",callback_data=f"adm_list_{max(0,page-1)}"),
                   InlineKeyboardButton(f"{page+1}",callback_data="dummy"),
                   InlineKeyboardButton("➡️",callback_data=f"adm_list_{page+1}")]]
            kb.append([InlineKeyboardButton("❌ CERRAR",callback_data="u_close")])
            await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

        elif data == "adm_bc":   await q.message.reply_text("📢 Mensaje para todos:"); ctx.user_data["state"]="WAIT_BC"
        elif data == "adm_ban":  await q.message.reply_text("🚫 ID a banear:"); ctx.user_data["state"]="WAIT_BAN"
        elif data == "adm_unban":await q.message.reply_text("🔓 ID a desbanear:"); ctx.user_data["state"]="WAIT_UNBAN"
        elif data == "adm_pts":  await q.message.reply_text("💰 ID del usuario:"); ctx.user_data["state"]="WAIT_PTS_ID"
        elif data == "adm_cp":   await q.message.reply_text("🎫 Código del cupón:"); ctx.user_data["state"]="WAIT_CP_CODE"
        elif data == "adm_edit_plan": await q.message.reply_text("🎭 ID del usuario:"); ctx.user_data["state"]="WAIT_PLAN_EDIT_ID"
        elif data == "adm_maint":
            db.data["system"]["maint_mode"] = not db.data["system"]["maint_mode"]; await db.save()
            est = "ACTIVADO" if db.data["system"]["maint_mode"] else "DESACTIVADO"
            await q.edit_message_text(f"⚠️ Mantenimiento {est}.", reply_markup=UI.overlord_panel())
        elif data == "adm_backup":
            await db.save()
            with open(EmpireConfig.DATABASE_PATH,'rb') as f:
                await ctx.bot.send_document(uid, f, caption="💾 DB Backup V500")
        elif data == "adm_tickets":
            open_tickets = {k:v for k,v in db.data["tickets"].items() if v["status"]=="OPEN"}
            msg = f"📂 **TICKETS ABIERTOS ({len(open_tickets)}):**\n\n"
            for tid,t in list(open_tickets.items())[:10]:
                user_t = db.data["users"].get(t["uid"],{}).get("name","?")
                msg += f"• `{tid}` — {user_t}: {t['text'][:50]}...\n"
            kb = [[InlineKeyboardButton(f"🔒 Cerrar {tid}", callback_data=f"tc_close_{tid}")] for tid in list(open_tickets.keys())[:5]]
            kb.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
            await q.edit_message_text(msg or "Sin tickets abiertos.", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        elif data == "adm_giftcard":
            values = EmpireConfig.ECONOMY["GIFT_CARD_VALUES"]
            kb = [[InlineKeyboardButton(f"🎁 {v:,} pts", callback_data=f"adm_giftval_{v}")] for v in values]
            kb.append([InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")])
            await q.edit_message_text("🎁 **GENERAR GIFT CARD** — Elige valor:", reply_markup=InlineKeyboardMarkup(kb))
        elif data == "adm_analytics":
            users_list = list(db.data["users"].values())
            plan_counts= {p: sum(1 for v in users_list if v.get("plan")==p) for p in EmpireConfig.PLANS}
            today_str  = str(datetime.date.today())
            active_today = sum(1 for v in users_list if v.get("daily_downloads",[0,""])[1]==today_str)
            avg_dl     = db.data["stats"]["total_downloads"] / max(db.data["stats"]["total_users"],1)
            banned_cnt = sum(1 for v in users_list if v.get("is_banned"))
            vip_cnt    = sum(1 for v in users_list if v.get("vip_expiry") and datetime.datetime.now() < datetime.datetime.fromisoformat(v["vip_expiry"]))
            total_pts  = sum(v.get("points",0) for v in users_list)
            msg = (
                f"📊 **ANALÍTICAS COMPLETAS V500**\n\n"
                f"**Distribución de Planes:**\n"
                + "\n".join(f"  {EmpireConfig.PLANS[p]['color']} {p}: `{plan_counts[p]}`" for p in EmpireConfig.PLANS)
                + f"\n  🥂 VIP activos: `{vip_cnt}`\n  🚫 Baneados: `{banned_cnt}`\n\n"
                f"**Engagement:**\n"
                f"  • Activos hoy: `{active_today}`\n"
                f"  • Avg descargas/usuario: `{avg_dl:.1f}`\n"
                f"  • Total puntos en circulación: `{total_pts:,}`\n\n"
                f"**Ingresos:**\n"
                f"  • Stars totales: `{db.data['stats'].get('stars_revenue',0):,} ⭐️`\n"
                f"  • Comisiones afiliado: `{db.data['stats'].get('affiliate_payouts',0):,} pts`\n"
                f"  • Gift cards generadas: `{db.data['stats'].get('gift_cards_sold',0)}`\n"
                f"  • Vol. P2P: `{db.data['stats'].get('p2p_volume',0):,} pts`\n\n"
                f"**Casino:**\n"
                f"  • Total spins: `{db.data['stats'].get('casino_spins',0):,}`\n\n"
                f"**Seguridad:**\n"
                f"  • Fraude bloqueado: `{db.data['stats'].get('fraud_attempts_blocked',0)}`\n"
                f"  • IPs en blacklist: `{len(sec.blocked_ips)}`"
            )
            await q.edit_message_text(msg, reply_markup=UI.overlord_panel(), parse_
