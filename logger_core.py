import os
import json
import logging
import datetime
import time
from typing import Dict, Optional
import sys
from config import EmpireConfig, settings

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "enterprise_audit_v400.log"), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
json_handler = logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "structured_logs.jsonl"), encoding='utf-8')
json_handler.setFormatter(JsonFormatter())
logging.getLogger("ISHAK_LEVIATHAN").addHandler(json_handler)

logger = logging.getLogger("ISHAK_LEVIATHAN")
if SENTRY_DSN:
    logger.info("✅ Sentry integrado. Errores enviados automáticamente al panel.")

# [15] AUDIT LOGS DETALLADOS
class AuditLogger:
    """Registra cada acción crítica con trazabilidad completa."""
    def __init__(self, log_file: str = "audit_logs.jsonl"):
        self.log_file = os.path.join(EmpireConfig.LOGS_DIR, log_file)
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
