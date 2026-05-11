import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet
from typing import Callable

load_dotenv()

class AppSettings(BaseSettings):
    """Configuración centralizada y validada con Pydantic."""
    admin_id: int = Field(default=8398522835, description="ID del administrador principal")
    telegram_token: str = Field(..., description="Token del bot de Telegram")
    deploy_env: str = Field(default="production", description="Entorno de despliegue")
    port: int = Field(default=8080, description="Puerto del servidor web")
    
    # [2] REDIS CONFIGURACIÓN
    redis_url: str = Field(default="redis://localhost:6379/0", description="URL de Redis")
    use_redis: bool = Field(default=False, description="Activar Redis para caché y colas")
    
    # [6] SECRET MANAGEMENT
    vault_url: str | None = Field(default=None, description="URL de HashiCorp Vault")
    aws_region: str | None = Field(default=None, description="Región AWS para Secrets Manager")
    
    # [5] CDN CONFIG
    cdn_enabled: bool = Field(default=False, description="Activar CDN para entrega de archivos")
    cdn_base_url: str | None = Field(default=None, description="URL base del CDN")
    
    # [10] ENCRIPTACIÓN
    encryption_key: str = Field(default=Fernet.generate_key().decode(), description="Clave Fernet para cifrar datos sensibles")
    
    # [12] WEBHOOKS
    webhook_enabled: bool = Field(default=False, description="Activar Webhooks en lugar de Polling")
    webhook_url: str | None = Field(default=None, description="URL del Webhook")
    webhook_secret: str | None = Field(default=None, description="Secret para validar Webhook")
    
    # [21] MULTI-IDIOMA
    default_language: str = Field(default="es", description="Idioma por defecto (es/en/fr/ar)")
    
    # [14] ALERTAS
    alert_chat_id: int | None = Field(default=None, description="Chat ID para alertas críticas")
    alert_threshold_errors: int = Field(default=5, description="Umbral de errores por minuto para alertar")
    
    class Config:
        env_prefix = "ISHAK_"
        env_file = ".env"

settings = AppSettings()

# [10] CRYPTOGRAPHY - Encriptación de datos sensibles
encryption_key_bytes = settings.encryption_key.encode() if isinstance(settings.encryption_key, str) else settings.encryption_key
fernet = Fernet(encryption_key_bytes)

def encrypt_sensitive(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_sensitive(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

# [18] DEPENDENCY INJECTION
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

class EmpireConfig:
    ADMIN_ID = settings.admin_id
    TOKEN = settings.telegram_token
    VERSION = "401.0.0-LEVIATHAN-ULTRA-MONETIZED"
    
    if not TOKEN:
        print("❌ [ALERTA] TELEGRAM_TOKEN no definido en variables de entorno. Fallo crítico de seguridad.")
        import sys
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
        "STREAK_BONUS_DAY": 100,
        "AFFILIATE_TIER1_PCT": 0.10,
        "AFFILIATE_TIER2_PCT": 0.05,
        "WEEKLY_TOURNAMENT_ENTRY": 500,
        "VIP_LOUNGE_MONTHLY": 1500,
        "GIFT_CARD_VALUES": [500, 1000, 2500, 5000],
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
        "PACK_LARGE": {"name": "🏆 50,000 Puntos (Whale)", "type": "points", "stars": 350, "value": 50000},
        "SUB_PRO_30D": {"name": "👑 SUSCRIPCIÓN PRO (30 DÍAS)", "type": "sub", "stars": 250, "value": "PRO"},
        "SUB_ULTRA_30D": {"name": "🔥 SUSCRIPCIÓN ULTRA (30 DÍAS)", "type": "sub", "stars": 500, "value": "ULTRA"},
        "GIFT_500": {"name": "🎁 Tarjeta Regalo 500 pts", "type": "gift_card", "stars": 10, "value": 500},
        "GIFT_2500": {"name": "🎁 Tarjeta Regalo 2,500 pts", "type": "gift_card", "stars": 40, "value": 2500},
        "VIP_MONTH": {"name": "🥂 Sala VIP (30 días)", "type": "vip", "stars": 150, "value": "VIP"},
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
        "STREAK_WEEK": {"name": "Racha Semanal", "desc": "7 días seguidos de tributo.", "reward": 5000},
        "WHALE": {"name": "Ballena Cripto", "desc": "Compra 100,000 pts en Stars.", "reward": 15000},
        "AFFILIATE_BOSS": {"name": "Jefe Afiliado", "desc": "Gana 10,000 pts por comisiones.", "reward": 8000},
        "TOURNAMENT_WINNER": {"name": "Campeón Imperial", "desc": "Gana un torneo semanal.", "reward": 20000},
        "VIP_MEMBER": {"name": "VIP Exclusivo", "desc": "Accede a la Sala VIP.", "reward": 2000},
        "DOWNLOADER_500": {"name": "Extractor Legendario", "desc": "Llega a 500 descargas.", "reward": 25000},
    }
    
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
