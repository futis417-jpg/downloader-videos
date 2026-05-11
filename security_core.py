import re
import html
import time
import random
from typing import Optional
from pydantic import BaseModel, HttpUrl, validator
from logger_core import audit_logger

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

# [4] FRAUD DETECTION & SECURITY CORE + SELF HEALING
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
                    from database_core import db  # Import local para evitar dependencia circular
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
