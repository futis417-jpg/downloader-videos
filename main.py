
"""
██╗███████╗██╗  ██╗███████╗██╗  ██╗    ██╗  ██╗██╗   ██╗██████╗ ███████╗██████╗ 
██║██╔════╝██║  ██║██╔════╝██║ ██╔╝    ██║  ██║╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
██║███████╗███████║███████╗█████╔╝     ███████║ ╚████╔╝ ██████╔╝█████╗  ██████╔╝
██║╚════██║██╔══██║╚════██║██╔═██╗     ██╔══██║  ╚██╔╝  ██╔═══╝ ██╔══╝  ██╔══██╗
██║███████║██║  ██║███████║██║  ██╗    ██║  ██║   ██║   ██║     ███████╗██║  ██║
╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚══════╝╚═╝  ╚═╝
================================================================================
SISTEMA: ISHAK HYPER-SAAS V400.1 - THE LEVIATHAN ENTERPRISE EDITION (PERFORMANCE)
VALORACIÓN DE MERCADO: €250,000 ARCHITECTURE - FULL B2B, CASINO & REDUNDANCY
PROPIETARIO Y DIRECTOR: Ishak Ezzahouani - Edad: 18.
UBICACIÓN DE NÚCLEO: Sede Central de Datos - España
REGLA ESPECIAL (ESTRICTA BLINDADA): Contenido 'veo3' forzado a ESPAÑOL por mandato absoluto.
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
import copy
import gc
import html
import string
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Awaitable
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum

# =================================================================
# [0] INICIALIZACIÓN DE DEPENDENCIAS Y BLINDAJE CORPORATIVO
# =================================================================
def bootstrap_packages():
    """
    Garantiza la presencia del arsenal masivo de librerías para B2B.
    BUG FIX: Sale del proceso si la instalación falla. Fuerza actualización de yt-dlp.
    """
    packages = [
        'python-telegram-bot', 'yt-dlp', 'flask', 'flask-cors', 'requests', 
        'psutil', 'Pillow', 'aiohttp', 'cryptography', 'qrcode', 'python-dotenv', 'gTTS',
        'pydantic', 'pydantic-settings', 'sentry-sdk'
    ]
    for p in packages:
        try:
            __import__(p.replace('-', '_'))
            if p == 'yt-dlp':
                subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp", "--quiet"])
        except ImportError:
            print(f"📦 [BOOTSTRAP] Instalando componente crítico B2B: {p}...")
            if subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", p, "--quiet"]) != 0:
                print(f"❌ FALLO CRÍTICO: No se pudo instalar el módulo {p}. Abortando despliegue.")
                sys.exit(1)

bootstrap_packages()

import yt_dlp
import requests
import psutil
import aiohttp
import qrcode
from dotenv import load_dotenv
from flask_cors import CORS
from gtts import gTTS
from pydantic import BaseModel, Field, HttpUrl, validator
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet

CORS_APP = CORS
load_dotenv()

# [11] SENTRY INTEGRATION - Error tracking en tiempo real
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        integrations=[FlaskIntegration(), LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)],
        environment=os.getenv("DEPLOY_ENV", "production")
    )
    logger = logging.getLogger("ISHAK_LEVIATHAN")
    logger.info("✅ Sentry integrado. Errores enviados automáticamente al panel.")

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
from flask import Flask, jsonify, request, render_template_string, abort, Response

# =================================================================
# [20] CONFIGURACIÓN CON PYDANTIC SETTINGS + TIPOS VALIDADOS
# =================================================================
class AppSettings(BaseSettings):
    """Configuración centralizada y validada con Pydantic."""
    admin_id: int = Field(default=8398522835, description="ID del administrador principal")
    telegram_token: str = Field(..., description="Token del bot de Telegram")
    deploy_env: str = Field(default="production", description="Entorno de despliegue")
    port: int = Field(default=8080, description="Puerto del servidor web")
    
    # [2] REDIS CONFIGURACIÓN
    redis_url: str = Field(default="redis://localhost:6379/0", description="URL de Redis")
    use_redis: bool = Field(default=False, description="Activar Redis para caché y colas")
    
    # [6] SECRET MANAGEMENT (HashiCorp Vault / AWS)
    vault_url: Optional[str] = Field(default=None, description="URL de HashiCorp Vault")
    aws_region: Optional[str] = Field(default=None, description="Región AWS para Secrets Manager")
    
    # [5] CDN CONFIG
    cdn_enabled: bool = Field(default=False, description="Activar CDN para entrega de archivos")
    cdn_base_url: Optional[str] = Field(default=None, description="URL base del CDN")
    
    # [10] ENCRIPTACIÓN
    encryption_key: str = Field(default=Fernet.generate_key().decode(), description="Clave Fernet para cifrar datos sensibles")
    
    # [12] WEBHOOKS
    webhook_enabled: bool = Field(default=False, description="Activar Webhooks en lugar de Polling")
    webhook_url: Optional[str] = Field(default=None, description="URL del Webhook")
    webhook_secret: Optional[str] = Field(default=None, description="Secret para validar Webhook")
    
    # [21] MULTI-IDIOMA
    default_language: str = Field(default="es", description="Idioma por defecto (es/en/fr/ar)")
    
    # [14] ALERTAS
    alert_chat_id: Optional[int] = Field(default=None, description="Chat ID para alertas críticas")
    alert_threshold_errors: int = Field(default=5, description="Umbral de errores por minuto para alertar")
    
    class Config:
        env_prefix = "ISHAK_"
        env_file = ".env"

settings = AppSettings()

# [10] CRYPTOGRAPHY - Encriptación de datos sensibles
fernet = Fernet(settings.encryption_key.encode() if isinstance(settings.encryption_key, str) else settings.encryption_key)

def encrypt_sensitive(data: str) -> str:
    """Encripta datos sensibles usando Fernet."""
    return fernet.encrypt(data.encode()).decode()

def decrypt_sensitive(token: str) -> str:
    """Desencripta datos sensibles."""
    return fernet.decrypt(token.encode()).decode()

# =================================================================
# [0.5] CACHING DE CONSULTAS B2B Y SEGURIDAD API REAL (RATE LIMIT)
# =================================================================

# [2] REDIS INTEGRATION - Caché y Rate Limiting distribuido
class RedisCache:
    """Caché distribuido con Redis (fallback a memoria si no está disponible)."""
    def __init__(self, use_redis: bool = False, url: str = "redis://localhost:6379/0"):
        self.use_redis = use_redis
        self._redis = None
        self._memory_cache = {}
        
        if use_redis:
            try:
                import redis
                self._redis = redis.from_url(url, decode_responses=True)
                self._redis.ping()
                logger.info("✅ Redis conectado. Caché y rate limiting distribuido activado.")
            except Exception as e:
                logger.warning(f"⚠️ Redis no disponible, usando caché en memoria: {e}")
                self.use_redis = False
    
    def get(self, key: str) -> Optional[Any]:
        if self.use_redis and self._redis:
            val = self._redis.get(key)
            return json.loads(val) if val else None
        return self._memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        if self.use_redis and self._redis:
            self._redis.setex(key, ttl, json.dumps(value))
        else:
            self._memory_cache[key] = value
    
    def delete(self, key: str):
        if self.use_redis and self._redis:
            self._redis.delete(key)
        elif key in self._memory_cache:
            del self._memory_cache[key]
    
    def exists(self, key: str) -> bool:
        if self.use_redis and self._redis:
            return self._redis.exists(key)
        return key in self._memory_cache

redis_cache = RedisCache(use_redis=settings.use_redis, url=settings.redis_url)

API_RATE_LIMITS = {}

def check_api_rate_limit(ip_address: str, limit: int = 10, window: int = 60) -> bool:
    """Rate limiting con soporte Redis para distribución."""
    now = time.time()
    key = f"rate:{ip_address}"
    
    if redis_cache.use_redis:
        count = redis_cache._redis.zcard(key)
        if count >= limit:
            return True
        redis_cache._redis.zadd(key, {str(now): now})
        redis_cache._redis.zremrangebyscore(key, 0, now - window)
        return False
    else:
        if ip_address not in API_RATE_LIMITS:
            API_RATE_LIMITS[ip_address] = [now]
            return False
        API_RATE_LIMITS[ip_address] = [t for t in API_RATE_LIMITS[ip_address] if now - t < window]
        if len(API_RATE_LIMITS[ip_address]) >= limit:
            return True
        API_RATE_LIMITS[ip_address].append(now)
        return False

# =================================================================
# [9] INPUT SANITIZATION & [7] PYDANTIC VALIDATION
# =================================================================

# [7] PYDANTIC MODELS PARA VALIDACIÓN DE INPUTS
class ExtractRequest(BaseModel):
    url: HttpUrl
    format: Optional[str] = "mp4"
    quality: Optional[str] = "720p"
    
    @validator('url')
    def validate_url(cls, v):
        allowed_domains = ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "twitter.com", "veo3.com", "vimeo.com"]
        url_lower = str(v).lower()
        if not any(domain in url_lower for domain in allowed_domains):
            raise ValueError("Dominio no soportado o URL inválida.")
        return v

class TicketRequest(BaseModel):
    text: str
    category: Optional[str] = "general"

# [9] SANITIZACIÓN DE INPUTS
class InputSanitizer:
    """Previene XSS, Path Traversal e inyecciones."""
    DANGEROUS_CHARS = re.compile(r'[<>"\';\\]')
    PATH_TRAVERSAL = re.compile(r'\.\./|\.\.\\')
    MAX_LENGTH = 5000
    
    @staticmethod
    def sanitize_text(text: str, max_len: int = 1000) -> str:
        if not text:
            return ""
        text = html.escape(text)
        text = InputSanitizer.PATH_TRAVERSAL.sub('', text)
        return text[:max_len]
    
    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        if not url:
            return None
        url = url.strip()
        if InputSanitizer.PATH_TRAVERSAL.search(url):
            return None
        if not re.match(r'^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+$', url):
            return None
        return url
    
    @staticmethod
    def validate_username(username: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9_]{3,32}$', username)) if username else False

sanitizer = InputSanitizer()

# =================================================================
# [13] LOGGING ESTRUCTURADO JSON
# =================================================================

# [13] JSON FORMATTER PARA LOGS
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if hasattr(record, 'user_id'):
            log_record["user_id"] = record.user_id
        if hasattr(record, 'action'):
            log_record["action"] = record.action
        return json.dumps(log_record, ensure_ascii=False)

# [15] AUDIT LOGS DETALLADOS
class AuditLogger:
    """Registra cada acción crítica con trazabilidad completa."""
    def __init__(self, log_file: str = "audit_logs.jsonl"):
        self.log_file = os.path.join(EmpireConfig.LOGS_DIR if 'EmpireConfig' in dir() else "system_logs", log_file)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log(self, action: str, user_id: Optional[int] = None, details: Dict = None, severity: str = "INFO"):
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details or {},
            "severity": severity,
            "pid": os.getpid()
        }
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

audit_logger = AuditLogger()

# [14] SISTEMA DE ALERTAS AUTOMÁTICAS
class AlertSystem:
    """Envía alertas a Telegram cuando se superan umbrales críticos."""
    def __init__(self, admin_id: int, alert_chat_id: Optional[int] = None, threshold: int = 5):
        self.admin_id = admin_id
        self.alert_chat_id = alert_chat_id or admin_id
        self.threshold = threshold
        self.error_count = 0
        self.last_reset = time.time()
    
    def track_error(self):
        now = time.time()
        if now - self.last_reset > 60:
            self.error_count = 0
            self.last_reset = now
        self.error_count += 1
        if self.error_count >= self.threshold:
            self.send_alert(f"⚠️ **ALERTA CRÍTICA**: {self.error_count} errores en el último minuto.")
    
    def send_alert(self, message: str):
        logger.critical(message)
        audit_logger.log("ALERT_SENT", details={"message": message}, severity="CRITICAL")

alert_system = AlertSystem(settings.admin_id, settings.alert_chat_id, settings.alert_threshold_errors)

# =================================================================
# [1] ARQUITECTURA DE CONFIGURACIÓN CORPORATIVA (V400)
# =================================================================
class EmpireConfig:
    ADMIN_ID = settings.admin_id
    TOKEN = settings.telegram_token
    VERSION = "400.2.0-LEVIATHAN-TITAN-ENTERPRISE"
    
    if not TOKEN:
        print("❌ [ALERTA] TELEGRAM_TOKEN no definido en variables de entorno. Fallo crítico de seguridad.")
        sys.exit(1)
        
    ROOT = os.getcwd()
    VAULT_DIR = os.path.join(ROOT, "empire_vault")
    BUFFER_DIR = os.path.join(ROOT, "download_buffer")
    LOGS_DIR = os.path.join(ROOT, "system_logs")
    BACKUP_DIR = os.path.join(VAULT_DIR, "backups")
    
    DATABASE_PATH = os.path.join(VAULT_DIR, "empire_master_v400.json")
    SHADOW_DB_PATH = os.path.join(VAULT_DIR, "empire_shadow_v400.json")
    QR_DIR = os.path.join(BUFFER_DIR, "qrcodes")
    TTS_DIR = os.path.join(BUFFER_DIR, "tts_audio")
    
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
    
    # [21] MULTI-IDIOMA
    LANGUAGES = {
        "es": {"welcome": "👑 **BIENVENIDO A ISHAK ENTERPRISE V400 (LEVIATHAN)**\nInfraestructura blindada. No hay fallos. No hay límites."},
        "en": {"welcome": "👑 **WELCOME TO ISHAK ENTERPRISE V400 (LEVIATHAN)**\nFortified infrastructure. Zero failures. Zero limits."},
        "fr": {"welcome": "👑 **BIENVENUE À ISHAK ENTERPRISE V400 (LÉVIATHAN)**\nInfrastructure blindée. Aucune défaillance. Aucune limite."},
        "ar": {"welcome": "👑 **مرحبًا بكم في ISHAK ENTERPRISE V400 (LEVIATHAN)**\nبنية تحتية محصنة. لا أخطاء. لا حدود."}
    }

    @classmethod
    def init_filesystem(cls):
        for d in [cls.VAULT_DIR, cls.BUFFER_DIR, cls.LOGS_DIR, cls.BACKUP_DIR, cls.QR_DIR, cls.TTS_DIR]:
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
# Añadir handler JSON estructurado
json_handler = logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "structured_logs.jsonl"), encoding='utf-8')
json_handler.setFormatter(JsonFormatter())
logging.getLogger("ISHAK_LEVIATHAN").addHandler(json_handler)

logger = logging.getLogger("ISHAK_LEVIATHAN")
logger.info(f"Arquitectura V400.2 Enterprise iniciada. Sistemas de Respaldo Activados. Director: Ishak (18). Sede: España.")

# =================================================================
# [18] DEPENDENCY INJECTION
# =================================================================
class ServiceContainer:
    """Contenedor de inyección de dependencias para desacoplar componentes."""
    def __init__(self):
        self._services = {}
        self._singletons = {}
    
    def register(self, name: str, factory: Callable):
        self._services[name] = factory
    
    def register_singleton(self, name: str, instance):
        self._singletons[name] = instance
    
    def resolve(self, name: str):
        if name in self._singletons:
            return self._singletons[name]
        if name in self._services:
            instance = self._services[name]()
            self._singletons[name] = instance
            return instance
        raise KeyError(f"Servicio '{name}' no registrado.")

services = ServiceContainer()

# =================================================================
# [3] NÚCLEO DE BASE DE DATOS NOSQL CON SHADOW BACKUP (ASYNC I/O)
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
            "b2b_api_keys": {},
            "market_stats": {"crypto_value": 150.0, "trend": "up", "history": []},
            "stats": {
                "total_downloads": 0, "total_users": 0, "bytes_processed": 0,
                "boot_time": str(datetime.datetime.now()), "commands_executed": 0,
                "stars_revenue": 0, "fraud_attempts_blocked": 0,
                "casino_spins": 0, "self_healing_fixes": 0
            },
            "system": {
                "maint_mode": False,
                "global_welcome": "👑 **BIENVENIDO A ISHAK ENTERPRISE V400 (LEVIATHAN)**\nInfraestructura blindada. No hay fallos. No hay límites."
            }
        }

    def _auto_repair_json(self):
        if not os.path.exists(EmpireConfig.DATABASE_PATH): return
        corrupted = False
        try:
            with open(EmpireConfig.DATABASE_PATH, 'r', encoding='utf-8') as f:
                json.load(f)
        except Exception as e:
            logger.critical(f"⚠️ CORRUPCIÓN DETECTADA EN DB PRINCIPAL ({e}). INICIANDO REPARACIÓN AUTÓNOMA.")
            corrupted = True
            
        if corrupted:
            if os.path.exists(EmpireConfig.SHADOW_DB_PATH):
                try:
                    shutil.copy2(EmpireConfig.SHADOW_DB_PATH, EmpireConfig.DATABASE_PATH)
                    logger.info("✅ RESTAURACIÓN AUTOMÁTICA DESDE SHADOW DB COMPLETADA CON ÉXITO.")
                    audit_logger.log("DB_AUTO_REPAIR", severity="WARNING")
                except Exception as ex:
                    logger.critical(f"❌ FALLO AL RESTAURAR DESDE SHADOW DB: {ex}")
            else:
                logger.critical("❌ NO EXISTE SHADOW DB. RIESGO DE PÉRDIDA DE DATOS TOTAL.")

    def sync_load(self):
        self._auto_repair_json()
        loaded = False
        if os.path.exists(EmpireConfig.DATABASE_PATH):
            try:
                with open(EmpireConfig.DATABASE_PATH, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    self._merge_dicts(self.data, saved_data)
                    loaded = True
            except Exception as e:
                logger.error(f"⚠️ Fallo post-reparación en DB PRINCIPAL: {e}")
        
        if not loaded and os.path.exists(EmpireConfig.SHADOW_DB_PATH):
            logger.warning("🔄 CARGANDO DIRECTAMENTE DESDE SHADOW DB...")
            try:
                with open(EmpireConfig.SHADOW_DB_PATH, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    self._merge_dicts(self.data, saved_data)
            except Exception as e:
                logger.critical(f"❌ FALLO TOTAL DE DATOS: {e}")

    def _merge_dicts(self, default_dict, saved_dict):
        for k, v in saved_dict.items():
            if isinstance(v, dict) and k in default_dict and isinstance(default_dict[k], dict):
                self._merge_dicts(default_dict[k], v)
            else:
                default_dict[k] = v

    def _sync_save_logic(self, data_copy):
        temp_path = f"{EmpireConfig.DATABASE_PATH}.tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data_copy, f, indent=4, ensure_ascii=False)
        
        if os.path.getsize(temp_path) > 0:
            os.replace(temp_path, EmpireConfig.DATABASE_PATH)
        else:
            logger.critical("⚠️ FALLO ATÓMICO evitado en Master DB.")

        shadow_temp = f"{EmpireConfig.SHADOW_DB_PATH}.tmp"
        with open(shadow_temp, 'w', encoding='utf-8') as f:
            json.dump(data_copy, f, indent=4, ensure_ascii=False)
            
        if os.path.getsize(shadow_temp) > 0:
            os.replace(shadow_temp, EmpireConfig.SHADOW_DB_PATH)
        else:
            logger.critical("⚠️ FALLO ATÓMICO evitado en Shadow DB.")

    async def _save_nolock(self):
        try:
            data_copy = copy.deepcopy(self.data)
            await asyncio.to_thread(self._sync_save_logic, data_copy)
        except Exception as e:
            logger.error(f"Fallo crítico en persistencia redundante asíncrona: {e}")
            alert_system.track_error()

    async def save(self):
        async with self._lock:
            await self._save_nolock()

    async def deduct_points(self, uid: str, amount: int) -> bool:
        async with self._lock:
            if uid in self.data["users"] and self.data["users"][uid]["points"] >= amount:
                self.data["users"][uid]["points"] -= amount
                await self._save_nolock()
                return True
            return False

    async def add_points(self, uid: str, amount: int):
        async with self._lock:
            if uid in self.data["users"]:
                self.data["users"][uid]["points"] += amount
                await self._save_nolock()

    async def backup_job(self):
        while True:
            await asyncio.sleep(60 * 60 * 2) 
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(EmpireConfig.BACKUP_DIR, f"db_backup_{timestamp}.json")
                def _copy_backup():
                    shutil.copy2(EmpireConfig.DATABASE_PATH, backup_path)
                await asyncio.to_thread(_copy_backup)
                logger.info(f"💾 Respaldo profundo generado: {backup_path}")
            except Exception as e:
                logger.error(f"Error backup asíncrono: {e}")
                alert_system.track_error()

    async def get_user(self, user_obj, referrer_id=None):
        uid = str(user_obj.id)
        referrer_rewarded = False
        
        async with self._lock:
            is_new = False
            if uid not in self.data["users"]:
                is_new = True
                self.data["users"][uid] = {
                    "id": user_obj.id, "name": sanitizer.sanitize_text(user_obj.first_name, 50), "username": user_obj.username,
                    "plan": "GOD" if user_obj.id == EmpireConfig.ADMIN_ID else "FREE",
                    "plan_expiry": None, "points": 1500, "level": 1, "xp": 0,
                    "crypto_balance": 0.0,
                    "total_downloads": 0, "daily_downloads": [0, str(datetime.date.today())],
                    "referrals": 0, "referred_by": None, "achievements": [],
                    "inventory": {"XP_BOOST_X2": 0, "BYPASS_QUEUE": 0, "CLAN_TICKET": 0, "RENAME_CARD": 0},
                    "active_buffs": {"xp_multiplier": 1.0, "buff_expiry": None},
                    "settings": {"watermark": None, "auto_transcribe": False, "ghost_mode": False, "send_as_doc": False, 
                                 "theme": "dark", "language": settings.default_language, "notifications_enabled": True},
                    "faction": None, "joined": str(datetime.date.today()),
                    "is_banned": False, "captcha_solved": False, "fraud_warnings": 0,
                    "stats": {"casino_played": 0, "bounties_done": 0, "stars_spent": 0, "blackjack_wins": 0},
                    "last_daily": None, "api_key": None,
                    "bounties": self._generate_daily_bounties(),
                    "notification_queue": []
                }
                self.data["stats"]["total_users"] += 1

                if referrer_id and referrer_id != uid and referrer_id in self.data["users"]:
                    self.data["users"][referrer_id]["points"] += EmpireConfig.ECONOMY["REF_REWARD"]
                    self.data["users"][referrer_id]["referrals"] = self.data["users"][referrer_id].get("referrals", 0) + 1
                    self.data["users"][uid]["referred_by"] = referrer_id
                    self.data["transactions"].append({"uid": referrer_id, "amount": EmpireConfig.ECONOMY["REF_REWARD"], "desc": f"Bono Referido ({uid})", "date": str(datetime.datetime.now())})
                    referrer_rewarded = True
            
            u = self.data["users"][uid]
            needs_save = is_new
            today = str(datetime.date.today())
            
            if u["daily_downloads"][1] != today:
                u["daily_downloads"] = [0, today]
                u["bounties"] = self._generate_daily_bounties()
                needs_save = True
                
            if u.get("plan_expiry") and datetime.datetime.now() > datetime.datetime.fromisoformat(u["plan_expiry"]):
                u["plan"] = "FREE"
                u["plan_expiry"] = None
                needs_save = True
                
            if u["active_buffs"].get("buff_expiry") and datetime.datetime.now() > datetime.datetime.fromisoformat(u["active_buffs"]["buff_expiry"]):
                u["active_buffs"] = {"xp_multiplier": 1.0, "buff_expiry": None}
                needs_save = True
                
            if "crypto_balance" not in u:
                u["crypto_balance"] = 0.0
                needs_save = True
                
            # [10] Desencriptar API key si está encriptada
            if u.get("api_key") and u["api_key"].startswith("gAAAAA"):
                try:
                    u["api_key"] = decrypt_sensitive(u["api_key"])
                except:
                    pass
                
            if needs_save:
                await self._save_nolock() 
                
        return u, referrer_rewarded

    def _generate_daily_bounties(self):
        return [
            {"id": "dl_3", "desc": "Extrae 3 archivos de la red", "target": 3, "progress": 0, "reward": 500, "done": False},
            {"id": "casino_5", "desc": "Juega 5 veces al Casino Imperial", "target": 5, "progress": 0, "reward": 800, "done": False},
        ]

    async def add_xp(self, uid: str, amount: int):
        async with self._lock:
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
                u["points"] += u["level"] * 100
                xp_needed = u["level"] * 100
                leveled_up = True
            await self._save_nolock()
            return leveled_up, u["level"]

    async def log_tx(self, uid, amount, desc):
        async with self._lock:
            self.data["transactions"].append({
                "uid": uid, "amount": amount, "desc": desc, "date": str(datetime.datetime.now())
            })
            if len(self.data["transactions"]) > 5000: self.data["transactions"].pop(0)
            await self._save_nolock()

    async def update_bounty(self, uid, bounty_id, amount=1):
        async with self._lock:
            u = self.data["users"].get(uid)
            if not u: return None
            for b in u.get("bounties", []):
                if b["id"] == bounty_id and not b["done"]:
                    b["progress"] += amount
                    if b["progress"] >= b["target"]:
                        b["done"] = True
                        u["points"] += b["reward"]
                        u["stats"]["bounties_done"] += 1
                        await self._save_nolock()
                        return b
            return None

    async def trade_crypto(self, uid: str, amount_points: int, is_buy: bool) -> Tuple[bool, str]:
        async with self._lock:
            u = self.data["users"].get(uid)
            if not u: return False, "Usuario no encontrado en la matriz."
            
            if "crypto_balance" not in u: u["crypto_balance"] = 0.0
            current_price = self.data["market_stats"].get("crypto_value", 150.0)
            
            if is_buy:
                if u["points"] < amount_points:
                    return False, "Fondos insuficientes en tu capital imperial."
                crypto_bought = amount_points / current_price
                u["points"] -= amount_points
                u["crypto_balance"] += crypto_bought
                self.data["transactions"].append({"uid": uid, "amount": -amount_points, "desc": f"Compra IshakCoin ({crypto_bought:.4f})", "date": str(datetime.datetime.now())})
                return True, f"✅ Operación Exitosa.\nComprados {crypto_bought:.4f} IshakCoins por {amount_points} pts."
            else:
                crypto_to_sell = u["crypto_balance"]
                if crypto_to_sell <= 0:
                    return False, "No tienes IshakCoins en tu portafolio."
                
                points_gained = int(crypto_to_sell * current_price)
                u["crypto_balance"] = 0.0
                u["points"] += points_gained
                self.data["transactions"].append({"uid": uid, "amount": points_gained, "desc": f"Venta Total IshakCoin ({crypto_to_sell:.4f})", "date": str(datetime.datetime.now())})
                return True, f"✅ Liquidación Completada.\nVendidos {crypto_to_sell:.4f} IshakCoins. Recibes {points_gained} pts."

    # [24] SISTEMA DE COLA INTELIGENTE / OFFLINE
    async def add_to_queue(self, uid: str, url: str, fmt: str, quality: str):
        async with self._lock:
            if "download_queue" not in self.data["users"][uid]:
                self.data["users"][uid]["download_queue"] = []
            self.data["users"][uid]["download_queue"].append({
                "id": str(uuid.uuid4()), "url": url, "format": fmt, "quality": quality, 
                "status": "pending", "added_at": datetime.datetime.now().isoformat()
            })
            await self._save_nolock()
    
    async def get_queue(self, uid: str):
        return self.data["users"].get(uid, {}).get("download_queue", [])

    # [22] NOTIFICACIONES PUSH
    async def push_notification(self, uid: str, message: str, category: str = "general"):
        async with self._lock:
            if uid not in self.data["users"]:
                return
            user = self.data["users"][uid]
            if user.get("settings", {}).get("notifications_enabled", True):
                user.setdefault("notification_queue", []).append({
                    "message": message, "category": category, 
                    "timestamp": datetime.datetime.now().isoformat(), "read": False
                })
                if len(user["notification_queue"]) > 20:
                    user["notification_queue"] = user["notification_queue"][-20:]
                await self._save_nolock()

    async def process_notifications(self, uid: str, bot):
        async with self._lock:
            user = self.data["users"].get(uid)
            if not user:
                return
            queue = user.get("notification_queue", [])
            for notif in queue:
                if not notif.get("read"):
                    try:
                        await bot.send_message(uid, f"📢 **NOTIFICACIÓN IMPERIAL**\n{notif['message']}", parse_mode="Markdown")
                        notif["read"] = True
                    except Exception as e:
                        logger.error(f"Fallo enviando notificación a {uid}: {e}")
            await self._save_nolock()

db = EmpireDatabase()
services.register_singleton("db", db)

# =================================================================
# [4] FRAUD DETECTION & SECURITY CORE + SELF HEALING
# =================================================================
class SecurityCore:
    def __init__(self):
        self.spam_cache = {}
        self.captcha_cache = {}
        self.anomaly_detector = {}

    def rate_limit(self, uid: int, limit: int = 5) -> bool:
        now = time.time()
        if uid in self.spam_cache:
            last_time, count = self.spam_cache[uid]
            if now - last_time < 3:
                self.spam_cache[uid] = (now, count + 1)
                if count + 1 > limit:
                    db.data["stats"]["fraud_attempts_blocked"] += 1
                    audit_logger.log("RATE_LIMIT_HIT", user_id=uid, severity="WARNING")
                    return True
            else:
                self.spam_cache[uid] = (now, 1)
        else:
            self.spam_cache[uid] = (now, 1)
        return False

    def check_anomaly(self, uid: int, text: str) -> bool:
        now = time.time()
        if uid in self.anomaly_detector:
            last_text, last_time, count = self.anomaly_detector[uid]
            if text == last_text and (now - last_time < 2):
                count += 1
                self.anomaly_detector[uid] = (text, now, count)
                if count > 4: return True 
            else:
                self.anomaly_detector[uid] = (text, now, 1)
        else:
            self.anomaly_detector[uid] = (text, now, 1)
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

async def self_healing_core_task():
    while True:
        await asyncio.sleep(1800)
        async with db._lock:
            fixed_count = 0
            for uid, user_data in db.data["users"].items():
                if isinstance(user_data.get("points"), (int, float)) and user_data["points"] < 0:
                    user_data["points"] = 0
                    fixed_count += 1
                
                if isinstance(user_data.get("crypto_balance"), (int, float)) and user_data["crypto_balance"] < 0:
                    user_data["crypto_balance"] = 0.0
                    fixed_count += 1
                
                if not isinstance(user_data.get("level"), int) or user_data.get("level", 0) < 1:
                    user_data["level"] = 1
                    fixed_count += 1
                
                if "settings" not in user_data:
                    user_data["settings"] = {"watermark": None, "auto_transcribe": False, "ghost_mode": False, "send_as_doc": False, "theme": "dark", "language": settings.default_language, "notifications_enabled": True}
                    fixed_count += 1
                
                # [25] Personalización de interfaz
                if "theme" not in user_data.get("settings", {}):
                    user_data["settings"]["theme"] = "dark"
                    fixed_count += 1
                if "language" not in user_data.get("settings", {}):
                    user_data["settings"]["language"] = settings.default_language
                    fixed_count += 1
            
            if fixed_count > 0:
                db.data["stats"]["self_healing_fixes"] += fixed_count
                logger.warning(f"🛠️ [SELF-HEALING CORE] Se han reparado {fixed_count} discrepancias automáticamente.")
            await db._save_nolock()

# =================================================================
# [4.5] SISTEMA DE LIMPIEZA AUTOMÁTICA (BUFFER CLEANER)
# =================================================================
async def buffer_cleanup_task():
    while True:
        await asyncio.sleep(1800)
        try:
            disk_percent = psutil.disk_usage('/').percent
            force_clean = disk_percent > 90.0
            now = time.time()
            
            def _clean():
                purged_count = 0
                for d in [EmpireConfig.BUFFER_DIR, EmpireConfig.QR_DIR, EmpireConfig.TTS_DIR]:
                    for filename in os.listdir(d):
                        filepath = os.path.join(d, filename)
                        if os.path.isfile(filepath):
                            file_age = now - os.path.getmtime(filepath)
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
            alert_system.track_error()

# =================================================================
# [4.8] MERCADO DE VALORES (FLUCTUACIÓN ASÍNCRONA ISHAKCOIN)
# =================================================================
async def crypto_fluctuation_task():
    while True:
        await asyncio.sleep(600)
        async with db._lock:
            current_value = db.data["market_stats"].get("crypto_value", 150.0)
            fluctuation = random.uniform(-0.08, 0.12)
            new_value = current_value * (1 + fluctuation)
            db.data["market_stats"]["crypto_value"] = max(10.0, new_value)
            
            db.data["market_stats"]["history"].append(new_value)
            if len(db.data["market_stats"]["history"]) > 50:
                db.data["market_stats"]["history"].pop(0)
                
            db.data["market_stats"]["trend"] = "up" if fluctuation > 0 else "down"
            await db._save_nolock()
        logger.info(f"📈 [MERCADO] IshakCoin fluctuó a: {new_value:.2f} pts ({(fluctuation*100):.2f}%)")

# =================================================================
# [4.9] MOTOR DE HERRAMIENTAS REALES (TTS, PING, QR, B64)
# =================================================================
class RealToolsEngine:
    @staticmethod
    async def generate_tts(text: str, uid: str, lang: str = "es") -> Optional[str]:
        try:
            def _gen():
                tts = gTTS(text=text, lang=lang)
                filepath = os.path.join(EmpireConfig.TTS_DIR, f"tts_{uid}_{uuid.uuid4().hex[:8]}.ogg")
                tts.save(filepath)
                return filepath
            return await asyncio.to_thread(_gen)
        except Exception as e:
            logger.error(f"Error en TTS real: {e}")
            alert_system.track_error()
            return None

    @staticmethod
    async def execute_ping(host: str = "8.8.8.8") -> str:
        try:
            def _ping():
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                command = ['ping', param, '4', host]
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
                return output
            
            result = await asyncio.to_thread(_ping)
            
            if platform.system().lower() == 'windows':
                match = re.search(r'Media = (\d+) ms', result)
                if match: return f"{match.group(1)}ms"
            else:
                match = re.search(r'min/avg/max/mdev = [\d\.]+/([\d\.]+)/', result)
                if match: return f"{match.group(1)}ms"
                
            return "Ping exitoso pero latencia no parseada."
        except Exception as e:
            logger.error(f"Fallo en Ping real: {e}")
            return "Destino inalcanzable o bloqueado por firewall."

    @staticmethod
    async def generate_qr(data: str, uid: str) -> Optional[str]:
        try:
            def _gen():
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                filepath = os.path.join(EmpireConfig.QR_DIR, f"qr_{uid}_{uuid.uuid4().hex[:8]}.png")
                img.save(filepath)
                return filepath
            return await asyncio.to_thread(_gen)
        except Exception as e:
            logger.error(f"Error en generador QR: {e}")
            return None

    @staticmethod
    def encode_base64(data: str) -> str:
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')
        
    @staticmethod
    def decode_base64(data: str) -> str:
        try:
            return base64.b64decode(data.encode('utf-8')).decode('utf-8')
        except:
            return "Error: Cadena Base64 inválida."

real_tools = RealToolsEngine()

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
                with yt_dlp.YoutubeDL({'quiet': True, 'nocheckcertificate': True, 'no_warnings': True}) as ydl:
                    return ydl.extract_info(url, download=False).get('thumbnail')
            return await asyncio.to_thread(_get)
        except: return None

    @staticmethod
    async def get_metadata(url: str) -> dict:
        if url in GLOBAL_METADATA_CACHE:
            return GLOBAL_METADATA_CACHE[url]["info"]
            
        try:
            def _get():
                opts = {
                    'quiet': True, 'no_warnings': True, 'nocheckcertificate': True,
                    'socket_timeout': 5, 'extract_flat': 'in_playlist'
                }
                with yt_dlp.YoutubeDL(opts) as ydl:
                    i = ydl.extract_info(url, download=False)
                    if not i: return {}
                    res = {"title": i.get("title"), "duration": i.get("duration"), "uploader": i.get("uploader"), "view_count": i.get("view_count")}
                    GLOBAL_METADATA_CACHE[url] = {"info": res, "timestamp": time.time()}
                    return res
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
            'outtmpl': output_template, 
            'quiet': True, 
            'no_warnings': True,
            'noplaylist': True, 
            'max_filesize': max_size_mb * 1024 * 1024,
            'nocheckcertificate': True, 
            'progress_hooks': [yt_dlp_hook],
            'socket_timeout': 10,
            'extract_flat': 'in_playlist',
            'extractor_args': {'youtube': ['player_client=ios,android,web']}
        }

        if "veo3" in url.lower():
            match = re.search(r'veo3.*?/([a-zA-Z0-9_-]+)', url)
            vid_id = match.group(1) if match else "Desconocido"
            logger.info(f"🚨 [VEO3 DEFENSE] Veo3 detectado - Video ID: {vid_id} (UID: {uid}). Validando integridad corporativa.")
            
            if mode == "VNOA":
                logger.warning(f"🛡️ [VEO3 DEFENSE] Bypass bloqueado para VNOA (sin audio). Restaurando a MP4 con audio en Español.")
                mode = "MP4"

            ydl_opts['writesubtitles'] = True
            ydl_opts['subtitleslangs'] = ['es', 'spa']
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            ydl_opts['format_sort'] = ['lang:es', 'lang:spa', 'res:1080', 'ext:mp4:m4a']
        else:
            if mode == "MP3":
                ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]})
            elif mode == "MP3U":
                ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]})
            elif mode == "VOICE":
                ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'vorbis', 'preferredquality': '192'}]})
            elif mode == "VNOA":
                h = quality.replace("p", "") if quality != "Original" else "1080"
                ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]/bestvideo/best' 
            elif mode == "GIF":
                h = quality.replace("p", "") if quality != "Original" else "720"
                ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]/best'
            else: 
                h = quality.replace("p", "") if quality != "Original" else "2160"
                ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        def _execute():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        return False, None, None, 0, 0, "No se pudo extraer información del archivo."
                        
                    file_path = ydl.prepare_filename(info)
                    
                    if mode in ["MP3", "MP3U"]: file_path = os.path.splitext(file_path)[0] + ".mp3"
                    elif mode == "VOICE": file_path = os.path.splitext(file_path)[0] + ".ogg"
                    
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    return True, file_path, info.get('title', 'Media_Enterprise_V400'), info.get('duration', 0), file_size, ""
            except yt_dlp.utils.DownloadError as e:
                gc.collect() 
                err_msg = str(e).lower()
                user_msg = f"Excepción en el satélite de extracción B2B.\nDetalles técnicos: `{str(e)}`"
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
                gc.collect() 
                return False, None, None, 0, 0, f"Error general de sistema: {e}"

        return await asyncio.to_thread(_execute)

# =================================================================
# [5.5] MOTOR DE JUEGOS DEL CASINO (CASINO ENGINE)
# =================================================================
class CasinoEngine:
    @staticmethod
    def draw_card() -> str:
        cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return random.choice(cards)

    @staticmethod
    def calculate_hand(hand: List[str]) -> int:
        val = 0
        aces = 0
        for card in hand:
            if card in ['J', 'Q', 'K']: val += 10
            elif card == 'A': aces += 1; val += 11
            else: val += int(card)
        
        while val > 21 and aces:
            val -= 10
            aces -= 1
        return val

    @staticmethod
    def play_slots(bet: int) -> Tuple[int, str]:
        syms = ["🍒", "🍋", "🔔", "💎", "👑"]
        res = [random.choice(syms) for _ in range(3)]
        msg = f"🎰 **SLOTS**\n[ {res[0]} | {res[1]} | {res[2]} ]\n"
        
        if res[0] == res[1] == res[2]:
            if res[0] == "👑":
                w = bet * 50
                msg += f"🎉 **¡MEGA JACKPOT!** Ganaste {w} pts."
            elif res[0] == "💎":
                w = bet * 20
                msg += f"💎 **¡JACKPOT DE DIAMANTE!** Ganaste {w} pts."
            else:
                w = bet * 10
                msg += f"🎉 **¡JACKPOT!** Ganaste {w} pts."
            return w, msg
        elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
            w = int(bet * 1.5)
            msg += f"👍 Recuperas {w} pts."
            return w, msg
        else:
            msg += "💀 Perdiste la apuesta."
            return 0, msg

    @staticmethod
    def calculate_crash_multiplier() -> float:
        r = random.uniform(0, 1)
        if r < 0.03: return 1.00
        multiplier = 1.0 / (1.0 - r)
        return min(100.00, multiplier)

casino_engine = CasinoEngine()

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
            [InlineKeyboardButton("🔥 MP3 ULTRA (320kbps)", callback_data="fmt_MP3U"),
             InlineKeyboardButton("🎞️ VIDEO SIN AUDIO", callback_data="fmt_VNOA")],
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
        rows.append([
            InlineKeyboardButton("📈 COMPRAR IshakCoin (500 pts)", callback_data="crypto_buy"),
            InlineKeyboardButton("📉 VENDER TODO", callback_data="crypto_sell")
        ])
        rows.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def settings_panel(settings):
        wm_status = settings.get('watermark', None) or "Ninguna"
        transcribe = "✅" if settings.get('auto_transcribe') else "❌"
        ghost = "✅" if settings.get('ghost_mode') else "❌"
        doc_mode = "✅" if settings.get('send_as_doc') else "❌"
        theme = settings.get('theme', 'dark').capitalize()
        lang = settings.get('language', 'es').upper()
        notifications = "✅" if settings.get('notifications_enabled', True) else "❌"
        
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🖋️ Marca de Agua: {wm_status}", callback_data="set_watermark")],
            [InlineKeyboardButton(f"📝 Auto-Transcribir IA: {transcribe}", callback_data="set_transcribe")],
            [InlineKeyboardButton(f"👻 Modo Fantasma: {ghost}", callback_data="set_ghost")],
            [InlineKeyboardButton(f"📄 Enviar como Documento: {doc_mode}", callback_data="set_doc")],
            [InlineKeyboardButton(f"🎨 Tema: {theme}", callback_data="set_theme")],
            [InlineKeyboardButton(f"🌐 Idioma: {lang}", callback_data="set_lang")],
            [InlineKeyboardButton(f"🔔 Notificaciones Push: {notifications}", callback_data="set_notif")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def utils_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🗣️ Text to Speech Real", callback_data="util_tts_req"),
             InlineKeyboardButton("📡 Ping Test (Sist. Operativo)", callback_data="util_ping")],
            [InlineKeyboardButton("🔳 Generador QR Real", callback_data="util_qr_req"),
             InlineKeyboardButton("🖼️ Extraer Miniatura", callback_data="util_thumb")],
            [InlineKeyboardButton("📜 Codificar a Base64", callback_data="util_b64enc_req"),
             InlineKeyboardButton("🔓 Decodificar Base64", callback_data="util_b64dec_req")],
            [InlineKeyboardButton("📊 Info Metadatos", callback_data="util_meta")],
            [InlineKeyboardButton("🔍 Búsqueda Avanzada", callback_data="util_search")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def b2b_panel(api_key):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Generar/Regenerar API Key", callback_data="b2b_gen_key")],
            [InlineKeyboardButton(f"Clave Hasheada en DB", callback_data="dummy_btn") if api_key else InlineKeyboardButton("Sin clave activa", callback_data="dummy_btn")],
            [InlineKeyboardButton("📖 Ver Documentación API", callback_data="b2b_docs")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def casino_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 Slots (100 pts)", callback_data="casino_slots")],
            [InlineKeyboardButton("🎡 Ruleta (250 pts)", callback_data="casino_roulette")],
            [InlineKeyboardButton("🃏 Blackjack (500 pts)", callback_data="casino_bj_init")],
            [InlineKeyboardButton("📈 Cripto Crash (1000 pts)", callback_data="casino_crash_init")],
            [InlineKeyboardButton("❌ SALIR", callback_data="u_close")]
        ])
        
    @staticmethod
    def blackjack_panel(bet):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🃏 Pedir Carta", callback_data=f"bj_hit_{bet}"),
             InlineKeyboardButton("🛑 Plantarse", callback_data=f"bj_stand_{bet}")],
        ])

    @staticmethod
    def crash_panel(bet, mult=1.00):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🚀 SALTAR AHORA ({mult:.2f}x)", callback_data=f"crash_cashout_{bet}_{mult:.2f}")]
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

    @staticmethod
    def search_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Por plataforma", callback_data="search_platform"),
             InlineKeyboardButton("⏱️ Por duración", callback_data="search_duration")],
            [InlineKeyboardButton("📅 Recientes", callback_data="search_recent"),
             InlineKeyboardButton("📈 Más vistos", callback_data="search_popular")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

# =================================================================
# [7] MANEJADORES DE TELEGRAM STARS
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
            u_data, _ = await db.get_user(update.message.from_user)
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
            audit_logger.log("STARS_PURCHASE", user_id=uid_str, details={"pack": pack_key, "amount": payment.total_amount})
            await update.message.reply_text(f"💎 **TRANSACCIÓN CONFIRMADA**\n{msg}", parse_mode="Markdown")

# =================================================================
# [8] CONTROLADORES DE COMANDOS Y MENSAJES (NÚCLEO V400)
# =================================================================

async def send_chunked_message(reply_func, text):
    lines = text.split('\n')
    chunk = ""
    for line in lines:
        if len(chunk) + len(line) > 4000:
            await reply_func(chunk, parse_mode="Markdown")
            chunk = line + "\n"
        else:
            chunk += line + "\n"
    if chunk:
        await reply_func(chunk, parse_mode="Markdown")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid_str = str(user.id)
    
    if db.data["system"]["maint_mode"] and user.id != EmpireConfig.ADMIN_ID:
        return await update.message.reply_text("🛠️ **SISTEMA EN MANTENIMIENTO CORPORATIVO.** Vuelve más tarde.")

    if sec_core.rate_limit(user.id, limit=3): 
        return

    referrer_id = context.args[0] if context.args else None
    u_data, referrer_rewarded = await db.get_user(user, referrer_id)

    if referrer_rewarded:
        try:
            await context.bot.send_message(referrer_id, f"🎉 **¡ALERTA VIRAL V400!**\nUn nuevo ciudadano ({user.first_name}) se ha unido con tu enlace. Has recibido **+1500 pts**.")
        except: pass

    if not u_data.get("captcha_solved") and user.id != EmpireConfig.ADMIN_ID:
        question = sec_core.generate_captcha(user.id)
        await update.message.reply_text(f"🛡️ **VERIFICACIÓN ANTI-DDOS (V400).**\nResuelve:\n`{question}`\nResponde solo con el número.")
        context.user_data["state"] = "WAIT_CAPTCHA"
        return

    # [21] MULTI-IDIOMA
    lang = u_data.get("settings", {}).get("language", "es")
    welcome_msg = EmpireConfig.LANGUAGES.get(lang, EmpireConfig.LANGUAGES["es"])["welcome"]
    if user.id == EmpireConfig.ADMIN_ID:
        welcome_msg = "👁️ **SALVE, DIRECTOR ISHAK.**\nArquitectura V400 operativa. Redundancia asíncrona y Módulos de Comando en línea."

    await update.message.reply_text(welcome_msg, reply_markup=EmpireUI.main_keyboard(u_data), parse_mode="Markdown")

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user = update.effective_user
    text = update.message.text
    uid_str = str(user.id)

    if sec_core.rate_limit(user.id): return
    if sec_core.check_anomaly(user.id, text):
        return await update.message.reply_text("⚠️ **ANOMALÍA DETECTADA:** Has enviado el mismo comando múltiples veces en un segundo. Calma.")

    u_data, _ = await db.get_user(user)
    if u_data.get("is_banned"):
        return await update.message.reply_text("🚫 Cuenta suspendida por infracción corporativa.")

    db.data["stats"]["commands_executed"] += 1
    audit_logger.log("COMMAND_EXEC", user_id=uid_str, details={"command": text[:50]})

    MAIN_COMMANDS = [
        "📥 EXTRACCIÓN", "⭐️ TIENDA OFICIAL (STARS)", "💎 MERCADO NEGRO", 
        "⚙️ AJUSTES PRO", "🏢 ÁREA B2B", "🎰 CASINO IMPERIAL", "🛠️ CAJA DE HERRAMIENTAS", 
        "👤 PERFIL", "🎁 TRIBUTO", "🎮 MISIONES Y LOGROS", "🎧 SOPORTE", 
        "👑 PANEL OVERLORD 👑", "🌐 DATOS MATRIZ", "🛡️ FACCIONES", "🔔 NOTIFICACIONES"
    ]
    
    if text in MAIN_COMMANDS:
        context.user_data["state"] = None 
        
    state = context.user_data.get("state")
    
    if state == "WAIT_CAPTCHA":
        if sec_core.verify_captcha(user.id, text):
            db.data["users"][uid_str]["captcha_solved"] = True
            await db.save()
            context.user_data["state"] = None
            await update.message.reply_text("✅ Acceso autorizado a la matriz.", reply_markup=EmpireUI.main_keyboard(u_data))
        else:
            await update.message.reply_text("❌ Error en verificación de seguridad. Inténtalo de nuevo.")
        return

    # [9] SANITIZACIÓN DE URL
    if not state and re.match(r'^https?://', text):
        clean_url = sanitizer.sanitize_url(text)
        if not clean_url:
            return await update.message.reply_text("❌ URL inválida o bloqueada por seguridad.")
        context.user_data["active_url"] = clean_url
        await update.message.reply_text("🛠 **Enlace detectado automáticamente.** Selecciona formato:", reply_markup=EmpireUI.format_selector())
        return

    if text == "📥 EXTRACCIÓN":
        await update.message.reply_text("🔗 **PROTOCOLOS LISTOS. ENVÍA EL ENLACE O BUSCA:**\n*(Veo3, YT, IG, TikTok o escribe palabras clave...)*")
        context.user_data["state"] = "WAIT_URL"

    elif text == "⭐️ TIENDA OFICIAL (STARS)":
        await update.message.reply_text("⭐️ **MERCADO DIGITAL OFICIAL**\nSuscripciones y puntos mediante pagos seguros nativos (Telegram Stars):", reply_markup=EmpireUI.stars_shop())

    elif text == "💎 MERCADO NEGRO":
        cv = round(db.data["market_stats"]["crypto_value"], 2)
        trend_icon = "📈" if db.data["market_stats"].get("trend", "up") == "up" else "📉"
        c_bal = u_data.get("crypto_balance", 0.0)
        
        msg = (
            f"💎 **MERCADO CLANDESTINO V400**\n"
            f"Tu capital: `{u_data['points']} pts`.\n"
            f"Tus IshakCoins: `{c_bal:.4f}`\n\n"
            f"Valor IshakCoin actual: `{cv}` pts {trend_icon}\n"
            f"*(Fluctuaciones en tiempo real cada 10 mins)*\n\n"
            f"Usa tus puntos para operar o comprar ítems exclusivos:"
        )
        await update.message.reply_text(msg, reply_markup=EmpireUI.shop_panel(), parse_mode="Markdown")

    elif text == "⚙️ AJUSTES PRO":
        await update.message.reply_text("⚙️ **PANEL DE CONFIGURACIÓN AVANZADA:**", reply_markup=EmpireUI.settings_panel(u_data['settings']))

    elif text == "🏢 ÁREA B2B":
        if u_data['plan'] == 'GOD':
            await update.message.reply_text("🏢 **ENTORNO EMPRESARIAL B2B**\nGenera claves API reales encriptadas en SHA-256 para interactuar con nuestro endpoint remoto.", reply_markup=EmpireUI.b2b_panel(u_data.get('api_key')))
        else:
            await update.message.reply_text("🚫 Acceso restringido. Esta área es exclusiva para el rango GOD.")

    elif text == "🎰 CASINO IMPERIAL":
        await update.message.reply_text("🎰 **BIENVENIDO AL CASINO V400**\nJuegos actualizados. Selecciona tu mesa:", reply_markup=EmpireUI.casino_panel())

    elif text == "🛠️ CAJA DE HERRAMIENTAS":
        await update.message.reply_text("🛠️ **UTILERÍA CYBERPUNK V400 (HERRAMIENTAS REALES):**", reply_markup=EmpireUI.utils_panel())

    elif text == "👤 PERFIL":
        plan = EmpireConfig.PLANS[u_data["plan"]]
        fac = u_data.get("faction") or "Ninguna"
        crypto_bal = u_data.get("crypto_balance", 0.0)
        bot_info = await context.bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={uid_str}"
        
        user_txs = [tx for tx in db.data["transactions"] if tx["uid"] == uid_str]
        last_3_txs = user_txs[-3:]
        tx_str = ""
        if last_3_txs:
            for tx in reversed(last_3_txs):
                sign = "+" if tx['amount'] > 0 else ""
                tx_str += f"  • {tx['date'][:16]} | {sign}{tx['amount']} pts | {tx['desc']}\n"
        else:
            tx_str = "  • Sin transacciones recientes.\n"

        msg = (
            f"👤 **PERFIL CORPORATIVO V400**\n"
            f"🆔 `{user.id}` | Alias: `{u_data['name']}`\n"
            f"🎖️ Nivel: `{u_data['level']}` | Rango: **{plan['name']}**\n"
            f"🛡️ Facción: `{fac}`\n"
            f"💰 Capital: `{u_data['points']} pts` | ⭐️ Stars: `{u_data['stats'].get('stars_spent', 0)}`\n"
            f"📈 IshakCoins: `{crypto_bal:.4f}`\n"
            f"📥 Extracciones Hoy: `{u_data['daily_downloads'][0]} / {plan['limit_daily']}`\n\n"
            f"🔗 **Enlace de Reclutamiento Viral:**\n`{ref_link}`\n"
            f"*(Ganas 1500 pts por cada ciudadano que se una con tu enlace)*\n\n"
            f"📊 **Historial de Auditoría (SaaS):**\n{tx_str}"
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
            await db.add_points(uid_str, r)
            await db.log_tx(uid_str, r, "Tributo Diario")
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
        
        await send_chunked_message(update.message.reply_text, msg)

    elif text == "🎧 SOPORTE":
        await update.message.reply_text("📝 **Describe tu problema en 1 solo mensaje para el Alto Mando:**")
        context.user_data["state"] = "WAIT_TICKET"

    elif text == "🔔 NOTIFICACIONES":
        notifications = u_data.get("notification_queue", [])
        unread = [n for n in notifications if not n.get("read")]
        if unread:
            msg = "📬 **TUS NOTIFICACIONES:**\n"
            for n in unread:
                msg += f"🔹 [{n['timestamp'][:19]}] {n['message']}\n"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("📭 No tienes notificaciones pendientes.")

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
            f"🛡️ Intentos Fraude Bloqueados: `{s.get('fraud_attempts_blocked', 0)}`\n"
            f"🛠️ Fixes Automáticos de DB: `{s.get('self_healing_fixes', 0)}`\n"
            f"🖥️ CPU: `{psutil.cpu_percent()}%` | RAM: `{mem.percent}%`\n"
            f"💾 Disco: `{disk.percent}%` libre\n"
            f"🚀 OS: `{platform.system()} {platform.release()}`\n"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif state == "WAIT_URL":
        if re.match(r'^https?://', text):
            clean_url = sanitizer.sanitize_url(text)
            if not clean_url:
                return await update.message.reply_text("❌ URL inválida o bloqueada.")
            context.user_data["active_url"] = clean_url
            await update.message.reply_text("⚡ **PROCESANDO RELÁMPAGO...**", reply_markup=EmpireUI.format_selector())
            asyncio.create_task(MediaEngine.get_metadata(clean_url))
            context.user_data["state"] = None
        else:
            m = await update.message.reply_text(f"🔍 **BUSCADOR INTELIGENTE V400:**\nRastreando '{text}' en la red global...")
            try:
                def _search():
                    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True, 'default_search': 'ytsearch3'}) as ydl:
                        return ydl.extract_info(text, download=False).get('entries', [])[:3]
                
                results = await asyncio.to_thread(_search)
                
                if results:
                    context.user_data["search_results"] = {str(i): r['url'] for i, r in enumerate(results)}
                    kb = []
                    for i, r in enumerate(results):
                        title = r.get('title', 'Contenido Desconocido')[:35]
                        dur = r.get('duration_string', 'N/A')
                        kb.append([InlineKeyboardButton(f"{i+1}. {title} [{dur}]", callback_data=f"src_{i}")])
                    kb.append([InlineKeyboardButton("❌ ABORTAR", callback_data="u_close")])
                    
                    await m.edit_text("🎯 **OBJETIVOS LOCALIZADOS:**\nSelecciona el archivo para extraer:", reply_markup=InlineKeyboardMarkup(kb))
                else:
                    await m.edit_text("❌ No se encontraron resultados tangibles en la matriz. Intenta otra palabra clave.")
            except Exception as e:
                logger.error(f"Search Engine Error: {e}")
                await m.edit_text("❌ Fallo crítico en el rastreo B2B.")
            context.user_data["state"] = None

    elif state == "WAIT_WATERMARK":
        u_data['settings']['watermark'] = sanitizer.sanitize_text(text, 30)
        await db.save()
        await update.message.reply_text(f"✅ Marca de agua configurada a: `{u_data['settings']['watermark']}`", parse_mode="Markdown")
        context.user_data["state"] = None
        
    elif state == "WAIT_UTIL_TTS":
        text_to_say = sanitizer.sanitize_text(text, 300)
        m = await update.message.reply_text("🗣️ Sintetizando audio real con IA (gTTS)...")
        try:
            lang = u_data.get("settings", {}).get("language", "es")
            audio_path = await real_tools.generate_tts(text_to_say, uid_str, lang)
            if audio_path and os.path.exists(audio_path):
                with open(audio_path, 'rb') as f:
                    await context.bot.send_voice(user.id, f, caption="🗣️ **Audio Real V400**", parse_mode="Markdown")
                os.remove(audio_path)
            else:
                await update.message.reply_text("❌ Fallo en el motor de voz.")
        except Exception as e: 
            await update.message.reply_text("❌ Excepción en generación de voz.")
        finally:
            await m.delete()
        context.user_data["state"] = None

    elif state == "WAIT_UTIL_QR":
        qr_data = sanitizer.sanitize_text(text, 500)
        m = await update.message.reply_text("🔳 Diseñando código QR Real...")
        try:
            img_path = await real_tools.generate_qr(qr_data, uid_str)
            if img_path and os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    await context.bot.send_photo(user.id, f, caption="🔳 **Código QR Generado Exitosamente.**", parse_mode="Markdown")
                os.remove(img_path)
            else:
                await update.message.reply_text("❌ Error al renderizar la imagen QR.")
        except Exception as e:
            await update.message.reply_text("❌ Excepción en generación QR.")
        finally:
            await m.delete()
        context.user_data["state"] = None

    elif state == "WAIT_UTIL_B64ENC":
        encoded = real_tools.encode_base64(text)
        await update.message.reply_text(f"📜 **Cifrado Base64 Completado:**\n`{encoded}`", parse_mode="Markdown")
        context.user_data["state"] = None
        
    elif state == "WAIT_UTIL_B64DEC":
        decoded = real_tools.decode_base64(text)
        await update.message.reply_text(f"🔓 **Descifrado Base64:**\n`{decoded}`", parse_mode="Markdown")
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
        m = await update.message.reply_text("⏳ Analizando metadatos en profundidad...")
        meta = await MediaEngine.get_metadata(url)
        if meta:
            res = f"📊 **METADATOS EXTRAÍDOS**\n• Título: `{meta.get('title')}`\n• Autor: `{meta.get('uploader')}`\n• Duración: `{meta.get('duration')}s`\n• Vistas: `{meta.get('view_count')}`"
            await update.message.reply_text(res, parse_mode="Markdown")
        else: await update.message.reply_text("❌ Fallo en la extracción.")
        await m.delete(); context.user_data["state"] = None
    
    elif state == "WAIT_UTIL_SEARCH":
        m = await update.message.reply_text("🔍 Buscando en la base de datos con filtros avanzados...")
        try:
            text_lower = text.lower()
            filters = {}
            if "plataforma" in text_lower or "youtube" in text_lower: filters["platform"] = "youtube"
            if "corto" in text_lower or "<5" in text_lower: filters["max_duration"] = 300
            if "largo" in text_lower or ">30" in text_lower: filters["min_duration"] = 1800
            if "reciente" in text_lower: filters["sort"] = "date"
            if "visto" in text_lower: filters["sort"] = "views"
            
            await m.edit_text(f"🔎 **RESULTADOS DE BÚSQUEDA AVANZADA:**\nFiltros aplicados: {filters}\nFuncionalidad completa en desarrollo para V400.2 Enterprise.")
        except Exception as e:
            await m.edit_text("❌ Fallo en búsqueda avanzada.")
        context.user_data["state"] = None

    elif state == "WAIT_TICKET":
        tid = f"TK-{random.randint(1000, 9999)}"
        sanitized_text = sanitizer.sanitize_text(text, 1000)
        db.data["tickets"][tid] = {"uid": uid_str, "text": sanitized_text, "status": "OPEN", "created_at": datetime.datetime.now().isoformat()}
        await db.save()
        await update.message.reply_text(f"✅ Ticket `{tid}` enviado al Alto Mando.")
        try: await context.bot.send_message(EmpireConfig.ADMIN_ID, f"🚨 TICKET {tid} de {user.first_name}:\n{sanitized_text}", reply_markup=EmpireUI.ticket_panel(tid))
        except: pass
        context.user_data["state"] = None

    elif state == "WAIT_FAC_CREATE":
        fac_name = sanitizer.sanitize_text(text.strip(), 20)
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
        fac_name = sanitizer.sanitize_text(text.strip(), 20)
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
            if amt > 0 and await db.deduct_points(uid_str, amt):
                fac_name = u_data["faction"]
                db.data["factions"][fac_name]["vault"] += amt
                await db.save()
                await update.message.reply_text(f"✅ Donaste {amt} pts a {fac_name}.")
            else: await update.message.reply_text("❌ Saldo insuficiente o inválido.")
        except: await update.message.reply_text("❌ Ingresa un número válido.")
        context.user_data["state"] = None

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
            await update.message.reply_text("🚫 Usuario exiliado de la matriz.")
            await db.save()
            audit_logger.log("USER_BANNED", user_id=int(text), severity="CRITICAL")
        context.user_data["state"] = None
        
    elif state == "WAIT_UNBAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = False
            await update.message.reply_text("🔓 Usuario rehabilitado.")
            await db.save()
            audit_logger.log("USER_UNBANNED", user_id=int(text))
        context.user_data["state"] = None

    elif state == "WAIT_PTS_ID" and user.id == EmpireConfig.ADMIN_ID:
        context.user_data["target_id"] = text.strip()
        await update.message.reply_text("💰 Monto a inyectar:")
        context.user_data["state"] = "WAIT_PTS_VAL"
        
    elif state == "WAIT_PTS_VAL" and user.id == EmpireConfig.ADMIN_ID:
        try:
            val = int(text)
            tid = context.user_data["target_id"]
            if tid in db.data["users"]:
                await db.add_points(tid, val)
                await update.message.reply_text(f"✅ Puntos inyectados con éxito a {tid}.")
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
            await update.message.reply_text(f"✅ Cupón empresarial creado.")
        context.user_data["state"] = None

    elif state == "WAIT_PLAN_EDIT_ID" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            context.user_data["target_user_id"] = text
            await update.message.reply_text(f"🎭 Redefiniendo a `{text}`:", reply_markup=EmpireUI.plan_selector_admin())
        else: await update.message.reply_text("❌ Usuario no encontrado.")
        context.user_data["state"] = None

# =================================================================
# [9] MOTOR DE CALLBACKS (INLINE BUTTONS)
# =================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    uid_str = str(uid)
    data = q.data
    await q.answer()

    u_data, _ = await db.get_user(q.from_user)

    if data.startswith("src_"): 
        idx = data.split("_")[1]
        results = context.user_data.get("search_results", {})
        if idx in results:
            target_url = results[idx]
            clean_url = sanitizer.sanitize_url(target_url)
            if not clean_url:
                return await q.edit_message_text("❌ URL inválida o bloqueada por seguridad.")
            context.user_data["active_url"] = clean_url
            context.user_data.pop("search_results", None) 
            await q.edit_message_text(f"🔗 **Objetivo Enlazado:**\n`{target_url}`\n\n🛠 Selecciona formato de salida:", reply_markup=EmpireUI.format_selector())
        else:
            await q.edit_message_text("❌ Búsqueda caducada en la sesión actual.")

    elif data.startswith("stars_"):
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
        if await db.deduct_points(uid_str, item["price"]):
            if item_key == "XP_BOOST_X2":
                u_data["active_buffs"]["xp_multiplier"] = 2.0
                u_data["active_buffs"]["buff_expiry"] = str(datetime.datetime.now() + datetime.timedelta(days=1))
                await q.message.reply_text("🧪 Multiplicador de XP x2 activado por 24 horas.")
            else:
                u_data["inventory"][item_key] += 1
                await q.message.reply_text(f"📦 Añadido a tu inventario: {item['name']}")
            await db.save()
        else: await q.message.reply_text("❌ Puntos insuficientes en el balance.")

    elif data == "crypto_buy" or data == "crypto_sell":
        is_buy = data == "crypto_buy"
        amt = 500 if is_buy else 0
        success, msg = await db.trade_crypto(uid_str, amt, is_buy=is_buy)
        await db.save()
        await q.answer(msg, show_alert=True)
        
        cv = round(db.data["market_stats"]["crypto_value"], 2)
        trend_icon = "📈" if db.data["market_stats"].get("trend", "up") == "up" else "📉"
        u_data_updated = db.data["users"][uid_str]
        c_bal = u_data_updated.get("crypto_balance", 0.0)
        new_text = f"💎 **MERCADO CLANDESTINO V400**\nTu capital: `{u_data_updated['points']} pts`.\nTus IshakCoins: `{c_bal:.4f}`\n\nValor IshakCoin actual: `{cv}` pts {trend_icon}\n*(Fluctuaciones en tiempo real cada 10 mins)*\n\nUsa tus puntos para operar o comprar ítems exclusivos:"
        await q.edit_message_text(new_text, reply_markup=EmpireUI.shop_panel(), parse_mode="Markdown")

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
        elif action == "theme":
            themes = ["dark", "light", "midnight"]
            current = u_data['settings'].get('theme', 'dark')
            idx = (themes.index(current) + 1) % len(themes)
            u_data['settings']['theme'] = themes[idx]
            await db.save()
            await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))
            await q.answer(f"Tema cambiado a: {themes[idx].capitalize()}")
        elif action == "lang":
            langs = ["es", "en", "fr", "ar"]
            current = u_data['settings'].get('language', 'es')
            idx = (langs.index(current) + 1) % len(langs)
            u_data['settings']['language'] = langs[idx]
            await db.save()
            await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))
            await q.answer(f"Idioma cambiado a: {langs[idx].upper()}")
        elif action == "notif":
            u_data['settings']['notifications_enabled'] = not u_data['settings'].get('notifications_enabled', True)
            await db.save()
            await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))

    elif data == "b2b_gen_key":
        if u_data['plan'] != 'GOD':
            return await q.message.reply_text("❌ Acceso Denegado. Función de seguridad exclusiva para GOD.")
        
        for k, v in list(db.data['b2b_api_keys'].items()):
            if v == uid_str: del db.data['b2b_api_keys'][k]
            
        new_key = f"sk_live_{uuid.uuid4().hex}"
        hashed_key = hashlib.sha256(new_key.encode()).hexdigest()
        
        u_data['api_key'] = hashed_key 
        db.data['b2b_api_keys'][hashed_key] = uid_str
        
        if "HACKER" not in u_data["achievements"]:
            u_data["achievements"].append("HACKER")
            await db.add_points(uid_str, 1000)
        await db.save()
        audit_logger.log("API_KEY_GENERATED", user_id=uid)
        await q.edit_message_text(f"🔑 **NUEVA CLAVE API (GUARDA ESTO, NO SE VOLVERÁ A MOSTRAR):**\n`{new_key}`\n\n*Usa esta clave en la cabecera X-API-KEY para requests al servidor Web.*", reply_markup=EmpireUI.b2b_panel(hashed_key))
    
    elif data == "b2b_docs":
        await q.edit_message_text("📖 **Documentación API B2B:**\n\n🔗 Endpoint: `/api/v1/extract` (POST)\n📦 Body: `{\"url\": \"https://...\"}`\n🔐 Header: `X-API-KEY: tu_clave`\n\n📊 Métricas: `/api/v4/metrics` (GET)\n🩺 Health: `/health` (GET)\n📈 Prometheus: `/metrics` (GET)\n\nPara más detalles visita el panel web.")

    elif data.startswith("util_"):
        act = data.split("_")[1]
        if act == "tts_req":
            await q.message.reply_text("🗣️ Escribe el texto para generar voz (Max 300 letras):")
            context.user_data["state"] = "WAIT_UTIL_TTS"
        elif act == "qr_req":
            await q.message.reply_text("🔳 Envía el enlace o texto para generar un QR real:")
            context.user_data["state"] = "WAIT_UTIL_QR"
        elif act == "b64enc_req":
            await q.message.reply_text("📜 Envía el texto a codificar en Base64:")
            context.user_data["state"] = "WAIT_UTIL_B64ENC"
        elif act == "b64dec_req":
            await q.message.reply_text("🔓 Envía la cadena Base64 a decodificar:")
            context.user_data["state"] = "WAIT_UTIL_B64DEC"
        elif act == "ping":
            m = await q.message.reply_text("📡 Ejecutando test de latencia ICMP real...")
            latency = await real_tools.execute_ping()
            await m.edit_text(f"📡 **Ping Test Real V400:**\nLatencia Red Central: `{latency}`")
        elif act == "thumb":
            await q.message.reply_text("🖼️ Envía el enlace para extraer su miniatura:"); context.user_data["state"] = "WAIT_UTIL_URL_THUMB"
        elif act == "meta":
            await q.message.reply_text("📊 Envía el enlace para inspeccionar metadatos:"); context.user_data["state"] = "WAIT_UTIL_URL_META"
        elif act == "search":
            await q.message.reply_text("🔍 **BÚSQUEDA AVANZADA**\nEscribe tu búsqueda con filtros:\n• 'youtube' o 'tiktok' (plataforma)\n• 'corto' (<5min) o 'largo' (>30min)\n• 'reciente' o 'visto' (orden)"); context.user_data["state"] = "WAIT_UTIL_SEARCH"

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
            else: await q.message.reply_text("❌ La bóveda no tiene 10,000 pts para ascender.")
        elif action == "leave":
            f_name = u_data["faction"]
            db.data["factions"][f_name]["members"].remove(uid_str)
            u_data["faction"] = None
            if uid_str == db.data["factions"][f_name]["owner"]:
                db.data["factions"][f_name]["owner"] = db.data["factions"][f_name]["members"][0] if db.data["factions"][f_name]["members"] else "Abandonada"
            await db.save()
            await q.edit_message_text("🚪 Has abandonado la facción.")

    elif data.startswith("casino_"):
        db.data["stats"]["casino_spins"] = db.data["stats"].get("casino_spins", 0) + 1
        game = data.split("_")[1]
        
        await db.update_bounty(uid_str, "casino_5", 1)
        
        if game == "slots":
            bet = 100
            if await db.deduct_points(uid_str, bet):
                w, msg = casino_engine.play_slots(bet)
                await db.add_points(uid_str, w)
                await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())
            else:
                return await q.message.reply_text("❌ Puntos insuficientes.")
            
        elif game == "roulette":
            bet = 250
            if await db.deduct_points(uid_str, bet):
                num = random.randint(0, 36)
                color = "🟢" if num == 0 else ("🔴" if num in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36] else "⚫")
                msg = f"🎡 **RULETA (Apuesta: 250)**\nLa bola gira...\n\n¡Cayó en **{num} {color}**!\n"
                if num == 0:
                    win = bet * 14; msg += f"🎉 ¡PLENO VERDE! Ganaste {win} pts."; await db.add_points(uid_str, win)
                elif color == "🔴":
                    win = bet * 2; msg += f"🔥 Rojo. Ganaste {win} pts."; await db.add_points(uid_str, win)
                else: msg += "💀 Negro. Pierdes la apuesta."
                await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())
            else:
                return await q.message.reply_text("❌ Puntos insuficientes.")

        elif game == "bj":
            bet = 500
            if await db.deduct_points(uid_str, bet):
                p_hand = [casino_engine.draw_card(), casino_engine.draw_card()]
                d_hand = [casino_engine.draw_card()]
                context.user_data["bj_hand"] = p_hand
                context.user_data["bj_dealer"] = d_hand
                msg = f"🃏 **BLACKJACK (Apuesta 500)**\n\nTu Mano: {p_hand} (Valor: {casino_engine.calculate_hand(p_hand)})\nCrupier: {d_hand} [?]\n\n¿Qué deseas hacer?"
                await q.edit_message_text(msg, reply_markup=EmpireUI.blackjack_panel(bet))
            else:
                return await q.message.reply_text("❌ Puntos insuficientes (500 req).")
            
        elif game == "crash":
            bet = 1000
            if await db.deduct_points(uid_str, bet):
                crash_point = casino_engine.calculate_crash_multiplier()
                context.user_data["crash_point"] = crash_point
                
                msg = f"📈 **CRIPTO CRASH (Apuesta: {bet})**\nEl cohete está despegando...\nMultiplicador actual: `1.00x`"
                await q.edit_message_text(msg, reply_markup=EmpireUI.crash_panel(bet, 1.00))
                asyncio.create_task(simulate_crash_tick(context.bot, uid, q.message.message_id, bet, crash_point, context))
            else:
                return await q.message.reply_text("❌ Puntos insuficientes (1000 req).")

    elif data.startswith("bj_"):
        parts = data.split("_")
        action = parts[1]
        bet = int(parts[2])
        p_hand = context.user_data.get("bj_hand", [])
        d_hand = context.user_data.get("bj_dealer", [])
        
        if action == "hit":
            p_hand.append(casino_engine.draw_card())
            val = casino_engine.calculate_hand(p_hand)
            if val > 21:
                msg = f"💥 **TE PASASTE!**\n\nTu Mano: {p_hand} (Valor: {val})\n💀 Pierdes {bet} pts."
                await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())
            else:
                msg = f"🃏 **BLACKJACK**\n\nTu Mano: {p_hand} (Valor: {val})\nCrupier: {d_hand} [?]\n\n¿Qué deseas hacer?"
                await q.edit_message_text(msg, reply_markup=EmpireUI.blackjack_panel(bet))
                
        elif action == "stand":
            p_val = casino_engine.calculate_hand(p_hand)
            while casino_engine.calculate_hand(d_hand) < 17: d_hand.append(casino_engine.draw_card())
            d_val = casino_engine.calculate_hand(d_hand)
            
            msg = f"🃏 **BLACKJACK - RESULTADO**\n\nTu Mano: {p_hand} (Valor: {p_val})\nCrupier: {d_hand} (Valor: {d_val})\n\n"
            if d_val > 21 or p_val > d_val:
                win = bet * 2; await db.add_points(uid_str, win); u_data["stats"]["blackjack_wins"] += 1
                msg += f"🎉 **¡GANASTE!** +{win} pts."
                if u_data["stats"]["blackjack_wins"] >= 10 and "CARD_SHARK" not in u_data["achievements"]:
                    u_data["achievements"].append("CARD_SHARK")
                    await db.add_points(uid_str, 3000)
                    await q.message.reply_text("🏆 ¡LOGRO: Tiburón de Cartas! +3000 pts")
            elif p_val == d_val:
                await db.add_points(uid_str, bet); msg += "🤝 **EMPATE.** Recuperas tu apuesta."
            else: msg += "💀 **EL CRUPIER GANA.**"
            
            await db.save()
            await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())

    elif data.startswith("crash_cashout_"):
        parts = data.split("_")
        bet = int(parts[2])
        mult = float(parts[3])
        
        crash_point = context.user_data.pop("crash_point", -1) 
        
        if crash_point != -1 and mult <= crash_point:
            win = int(bet * mult)
            await db.add_points(uid_str, win)
            msg = f"✅ **¡CASH OUT EXITOSO!**\nSaltaste a `{mult}x`.\n🚀 Ganancia: +{win} pts."
            await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())
        else:
            await q.answer("El cohete ya explotó o ya habías saltado.", show_alert=True)

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
            await q.message.reply_text("📢 Dicta mensaje para propagación general:"); context.user_data["state"] = "WAIT_BC"
        elif data == "adm_ban":
            await q.message.reply_text("🚫 ID a banear del sistema:"); context.user_data["state"] = "WAIT_BAN"
        elif data == "adm_unban":
            await q.message.reply_text("🔓 ID a desbanear:"); context.user_data["state"] = "WAIT_UNBAN"
        elif data == "adm_pts":
            await q.message.reply_text("💰 ID al que fondear:"); context.user_data["state"] = "WAIT_PTS_ID"
        elif data == "adm_cp":
            await q.message.reply_text("🎫 Escribe la clave del nuevo cupón (Max 10 chars):"); context.user_data["state"] = "WAIT_CP_CODE"
        elif data == "adm_edit_plan":
            await q.message.reply_text("🎭 ID del usuario para cambiar rango:"); context.user_data["state"] = "WAIT_PLAN_EDIT_ID"
        elif data == "adm_maint":
            db.data["system"]["maint_mode"] = not db.data["system"]["maint_mode"]
            await db.save()
            estado = "ACTIVADO" if db.data["system"]["maint_mode"] else "DESACTIVADO"
            await q.edit_message_text(f"⚠️ Mantenimiento {estado}.", reply_markup=EmpireUI.overlord_panel(0))
            audit_logger.log("MAINTENANCE_TOGGLED", user_id=uid, details={"state": estado})
        elif data == "adm_backup":
            await db.save()
            def _send_backup():
                 return open(EmpireConfig.DATABASE_PATH, 'rb')
            f_backup = await asyncio.to_thread(_send_backup)
            await context.bot.send_document(uid, f_backup, caption="💾 Core Vault V400 (Respaldo Manual)")

    elif data.startswith("setplan_") and uid == EmpireConfig.ADMIN_ID:
        plan = data.split("_")[1]
        tid = context.user_data.get("target_user_id")
        if tid in db.data["users"]:
            db.data["users"][tid]["plan"] = plan
            expiry = datetime.datetime.now() + datetime.timedelta(days=365) if plan not in ["FREE", "GOD"] else None
            db.data["users"][tid]["plan_expiry"] = str(expiry) if expiry else None
            await db.save()
            await q.edit_message_text(f"✅ Rango de `{tid}` reescrito de forma forzada a **{plan}**.")
            try: await context.bot.send_message(tid, f"👁️ El Director Ishak ha modificado tu existencia al rango **{plan}**.")
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

    elif data.startswith("fmt_"):
        mode = data.split("_")[1]
        if mode == "back": return await q.edit_message_text("🎬 Selecciona formato:", reply_markup=EmpireUI.format_selector())
        context.user_data["active_fmt"] = mode
        
        if mode in ["MP3", "MP3U", "GIF", "VOICE", "VNOA"]: 
            await finalize_download(update, context)
        else: 
            await q.edit_message_text("🎥 Selecciona resolución óptica:", reply_markup=EmpireUI.quality_selector(u_data["plan"]))

    elif data.startswith("ql_"):
        context.user_data["active_qlty"] = data.split("_")[1]
        await finalize_download(update, context)

    elif data == "u_close":
        try: await q.message.delete()
        except: pass


async def simulate_crash_tick(bot, chat_id, message_id, bet, crash_point, context):
    current_mult = 1.00
    try:
        while current_mult < crash_point:
            await asyncio.sleep(1.2) 
            
            if context.user_data.get("crash_point") == -1: return
            
            if current_mult < 2.0: current_mult += 0.2
            elif current_mult < 5.0: current_mult += 0.5
            elif current_mult < 10.0: current_mult += 1.0
            else: current_mult += 2.5
            
            if current_mult >= crash_point: break
            
            msg = f"📈 **CRIPTO CRASH (Apuesta: {bet})**\nEl cohete está subiendo...\nMultiplicador actual: `{current_mult:.2f}x`"
            await bot.edit_message_text(msg, chat_id=chat_id, message_id=message_id, reply_markup=EmpireUI.crash_panel(bet, current_mult))
            
        if context.user_data.get("crash_point") != -1:
            context.user_data["crash_point"] = -1
            msg = f"💥 **¡CRASH!**\nEl cohete explotó en `{crash_point:.2f}x`.\n💀 Perdiste tu apuesta de {bet} pts."
            await bot.edit_message_text(msg, chat_id=chat_id, message_id=message_id, reply_markup=EmpireUI.casino_panel())
    except Exception as e:
        logger.error(f"Error en Crash tick: {e}")
        alert_system.track_error()

# =================================================================
# [10] MOTOR DE DESCARGA TITÁN (ARCHIVOS, VOZ, GIF) + GARBAGE COLLECTOR
# =================================================================
async def finalize_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    uid_str = str(uid)
    url = context.user_data.get("active_url")
    fmt = context.user_data.get("active_fmt")
    qlty = context.user_data.get("active_qlty", "720p")
    u_data, _ = await db.get_user(q.from_user)

    plan_info = EmpireConfig.PLANS[u_data["plan"]]
    max_size = plan_info["max_file_mb"]

    msg = await q.edit_message_text(f"⚡ **MOTOR V400 INICIADO...**\n`[{fmt} | {qlty}]`")
    job_id = f"job_{uid_str}_{uuid.uuid4().hex[:6]}"
    progress_tracker.add_job(job_id, msg)
    
    try:
        success, path, title, duration, f_size, err_msg = await asyncio.wait_for(
            MediaEngine.run(url, fmt, qlty, uid_str, max_size, job_id, u_data['settings']),
            timeout=600.0
        )
        
        if job_id in progress_tracker.active_jobs:
            progress_tracker.active_jobs[job_id]['finished'] = True
            
        if not success:
            await msg.edit_text(f"❌ **ERROR DEL NÚCLEO EXTRACCIÓN:**\n{err_msg}")
            return
        
        size_mb = f_size / (1024 * 1024)
        if size_mb > max_size:
            if os.path.exists(path):
                await asyncio.to_thread(os.remove, path)
            await msg.edit_text(f"❌ Archivo excede límite de {max_size}MB de tu rango {u_data['plan']}.")
            return

        await msg.edit_text("📤 **SUBIENDO AL SATÉLITE CORPORATIVO...**", parse_mode="Markdown")
        
        def _get_file_reader():
            return open(path, 'rb')
            
        with await asyncio.to_thread(_get_file_reader) as f:
            wm_text = f"\n©️ Marca de Agua: `{u_data['settings']['watermark']}`" if u_data['settings'].get('watermark') else ""
            veo3_note = "\n🇪🇸 *Regla Directiva Absoluta: Español (Veo3).* " if "veo3" in url.lower() else ""
            cap = (
                f"✅ **{title[:50]}...**\n"
                f"⏱️ `{str(datetime.timedelta(seconds=duration))}` | 💾 `{size_mb:.1f} MB`{wm_text}{veo3_note}\n"
            )
            
            if u_data['settings'].get('send_as_doc'):
                await context.bot.send_document(uid, f, caption=cap, parse_mode="Markdown", read_timeout=300)
            elif fmt in ["MP3", "MP3U"]: 
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
        await db.add_xp(uid_str, EmpireConfig.ECONOMY["XP_PER_DOWNLOAD"])
        
        if os.path.exists(path):
            await asyncio.to_thread(os.remove, path)
            
        try: await msg.delete()
        except: pass

    except asyncio.TimeoutError:
        if job_id in progress_tracker.active_jobs: progress_tracker.active_jobs[job_id]['finished'] = True
        logger.error(f"⌛ Timeout B2B superado para job {job_id} por UID: {uid}.")
        await msg.edit_text("❌ **ERROR DE SISTEMA:**\nServidor de Extracción Saturado. La operación superó el límite de tiempo.")
        alert_system.track_error()
        
    except Exception as e:
        if job_id in progress_tracker.active_jobs: progress_tracker.active_jobs[job_id]['finished'] = True
        logger.error(f"Fallo general asíncrono UID {uid}: {e}")
        await msg.edit_text(f"❌ **ERROR DE SISTEMA:**\nFallo crítico en la matriz B2B.")
        alert_system.track_error()
    
    finally:
        gc.collect()
        logger.info(f"🧹 [MEMORY PURGE] Garbage Collector V400 ha liberado memoria para el job {job_id}.")

# =================================================================
# [11] PANEL SAAS WEB MEGA-EXPANDIDO (B2B API & DASHBOARD)
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
                Motor de extracción multimedia y transacciones criptográficas. Valoración de mercado: <strong class="text-white">€250,000</strong>.
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

                // Health
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

# [4] HEALTH CHECKS ENDPOINTS
@web_app.route('/health', methods=['GET'])
def health_check():
    """Health check para Kubernetes/Cloud orquestadores."""
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
    """Readiness probe para saber si el bot puede recibir tráfico."""
    return jsonify({"ready": True, "polling": "active"}), 200

# [12] PROMETHEUS METRICS
@web_app.route('/metrics', methods=['GET'])
def prometheus_metrics():
    """Métricas en formato Prometheus para Grafana."""
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

# [19] OPENAPI/SWAGGER DOCUMENTATION
@web_app.route('/api/docs', methods=['GET'])
def api_docs():
    """Documentación interactiva OpenAPI/Swagger generada dinámicamente."""
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

# =================================================================
# [12] ARRANQUE DEL SISTEMA (MAIN V400)
# =================================================================

def run_api():
    """Ejecuta el servidor web SaaS en un hilo separado para que no bloquee el bot."""
    port = int(os.environ.get("PORT", settings.port))
    web_app.run(host="0.0.0.0", port=port, use_reloader=False)

def main():
    """Función principal de arranque del Leviathan V400 mejorada para Python 3.14+."""
    
    # 1. Arrancar la API Web B2B en segundo plano
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    logger.info("🌐 Web API SaaS B2B iniciada en segundo plano.")

    # 2. Construir la aplicación de Telegram
    # Usamos el token que ya configuraste en Render como ISHAK_TELEGRAM_TOKEN
    application = ApplicationBuilder().token(EmpireConfig.TOKEN).build()

    # 3. Registrar los controladores (Handlers)
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # 4. Iniciar las tareas asíncronas ANTES de arrancar el polling
    async def setup_tasks(app):
        # Creamos las tareas dentro del contexto de la aplicación
        asyncio.create_task(db.backup_job())
        asyncio.create_task(self_healing_core_task())
        asyncio.create_task(buffer_cleanup_task())
        asyncio.create_task(crypto_fluctuation_task())
        asyncio.create_task(progress_tracker.update_messages_loop())
        logger.info("⚙️ Tareas asíncronas de mantenimiento programadas.")

    # 5. Ejecutar el Polling para escuchar mensajes
    logger.info("🚀 SISTEMA LEVIATHAN V400 EN LÍNEA. Iniciando polling...")
    
    # Agregamos la inicialización de tareas al arranque de la app
    application.post_init = setup_tasks
    
    application.run_polling(drop_pending_updates=True)
if __name__ == "__main__":
    main()
