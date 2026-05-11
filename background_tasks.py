import asyncio
import time
import psutil
import os
import random
from config import EmpireConfig, settings
from database_core import db
from logger_core import logger, alert_system

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
