import os
import json
import uuid
import asyncio
import shutil
import datetime
import copy
import random
from typing import Tuple

from config import EmpireConfig, services, decrypt_sensitive
from logger_core import logger, audit_logger, alert_system
from security_core import sanitizer

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
                "casino_spins": 0, "self_healing_fixes": 0,
                "affiliate_payouts": 0, "gift_cards_sold": 0,
                "tournament_prize_pool": 0,
            },
            "system": {
                "maint_mode": False,
                "global_welcome": "👑 **BIENVENIDO A ISHAK ENTERPRISE V401 (LEVIATHAN ULTRA)**\nInfraestructura blindada. No hay fallos. No hay límites.",
                "tournament": {
                    "active": False, "end_time": None, "prize_pool": 0,
                    "participants": {}, "winners": []
                },
                "vip_group_id": None, 
                "announcement_channel": None, 
            },
            "leaderboard_cache": {"top_downloads": [], "top_points": [], "updated": None},
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
                                 "theme": "dark", "language": "es", "notifications_enabled": True},
                    "faction": None, "joined": str(datetime.date.today()),
                    "is_banned": False, "captcha_solved": False, "fraud_warnings": 0,
                    "stats": {"casino_played": 0, "bounties_done": 0, "stars_spent": 0, "blackjack_wins": 0},
                    "last_daily": None, "api_key": None,
                    "bounties": self._generate_daily_bounties(),
                    "notification_queue": [],
                    "streak": 0,                    
                    "last_streak_date": None,
                    "affiliate_earnings": 0,        
                    "referrals_tier2": [],          
                    "vip_expiry": None,             
                    "gift_cards_owned": [],         
                    "tournament_score": 0,          
                    "total_spent_stars": 0,         
                    "coupon_used": None,            
                }
                self.data["stats"]["total_users"] += 1

                if referrer_id and referrer_id != uid and referrer_id in self.data["users"]:
                    self.data["users"][referrer_id]["points"] += EmpireConfig.ECONOMY["REF_REWARD"]
                    self.data["users"][referrer_id]["referrals"] = self.data["users"][referrer_id].get("referrals", 0) + 1
                    self.data["users"][uid]["referred_by"] = referrer_id
                    self.data["transactions"].append({"uid": referrer_id, "amount": EmpireConfig.ECONOMY["REF_REWARD"], "desc": f"Bono Referido ({uid})", "date": str(datetime.datetime.now())})
                    referrer_rewarded = True
                    tier1_ref = self.data["users"][referrer_id].get("referred_by")
                    if tier1_ref and tier1_ref in self.data["users"]:
                        tier2_bonus = int(EmpireConfig.ECONOMY["REF_REWARD"] * 0.25)
                        self.data["users"][tier1_ref]["points"] += tier2_bonus
                        self.data["users"][tier1_ref].setdefault("referrals_tier2", []).append(uid)
                        self.data["users"][tier1_ref]["affiliate_earnings"] = self.data["users"][tier1_ref].get("affiliate_earnings", 0) + tier2_bonus
                        self.data["transactions"].append({"uid": tier1_ref, "amount": tier2_bonus, "desc": f"Comisión Tier-2 ({uid})", "date": str(datetime.datetime.now())})
            
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
                
            if u.get("vip_expiry") and datetime.datetime.now() > datetime.datetime.fromisoformat(u["vip_expiry"]):
                u["vip_expiry"] = None
                needs_save = True
                
            if u["active_buffs"].get("buff_expiry") and datetime.datetime.now() > datetime.datetime.fromisoformat(u["active_buffs"]["buff_expiry"]):
                u["active_buffs"] = {"xp_multiplier": 1.0, "buff_expiry": None}
                needs_save = True
                
            if "crypto_balance" not in u:
                u["crypto_balance"] = 0.0
                needs_save = True
                
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

    async def process_daily_streak(self, uid: str) -> Tuple[int, int, bool]:
        async with self._lock:
            u = self.data["users"].get(uid)
            if not u:
                return 0, 0, False
            today = str(datetime.date.today())
            yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
            last = u.get("last_streak_date")
            if last == today:
                return 0, u.get("streak", 0), False
            
            streak = u.get("streak", 0)
            if last == yesterday:
                streak += 1
            else:
                streak = 1
            
            u["streak"] = streak
            u["last_streak_date"] = today
            
            base = random.randint(EmpireConfig.ECONOMY["DAILY_REWARD_MIN"], EmpireConfig.ECONOMY["DAILY_REWARD_MAX"])
            streak_bonus = min(streak * EmpireConfig.ECONOMY["STREAK_BONUS_DAY"], 2000)
            if u["plan"] == "PRO": base = int(base * 1.5)
            elif u["plan"] in ["ULTRA", "GOD"]: base = int(base * 3)
            total = base + streak_bonus
            
            u["points"] += total
            u["last_daily"] = today
            self.data["transactions"].append({"uid": uid, "amount": total, "desc": f"Tributo Diario (Racha {streak})", "date": str(datetime.datetime.now())})
            
            week_achieved = streak == 7 and "STREAK_WEEK" not in u.get("achievements", [])
            if week_achieved:
                u.setdefault("achievements", []).append("STREAK_WEEK")
                u["points"] += EmpireConfig.ACHIEVEMENTS["STREAK_WEEK"]["reward"]
            
            await self._save_nolock()
            return total, streak, week_achieved

    async def pay_affiliate_commission(self, buyer_uid: str, stars_amount: int):
        async with self._lock:
            tier1_uid = self.data["users"].get(buyer_uid, {}).get("referred_by")
            if tier1_uid and tier1_uid in self.data["users"]:
                commission = int(stars_amount * EmpireConfig.ECONOMY["AFFILIATE_TIER1_PCT"] * 10)
                self.data["users"][tier1_uid]["points"] += commission
                self.data["users"][tier1_uid]["affiliate_earnings"] = self.data["users"][tier1_uid].get("affiliate_earnings", 0) + commission
                self.data["transactions"].append({"uid": tier1_uid, "amount": commission, "desc": f"Comisión Stars T1 de {buyer_uid}", "date": str(datetime.datetime.now())})
                self.data["stats"]["affiliate_payouts"] += commission
                
                tier2_uid = self.data["users"].get(tier1_uid, {}).get("referred_by")
                if tier2_uid and tier2_uid in self.data["users"]:
                    commission2 = int(stars_amount * EmpireConfig.ECONOMY["AFFILIATE_TIER2_PCT"] * 10)
                    self.data["users"][tier2_uid]["points"] += commission2
                    self.data["users"][tier2_uid]["affiliate_earnings"] = self.data["users"][tier2_uid].get("affiliate_earnings", 0) + commission2
                    self.data["transactions"].append({"uid": tier2_uid, "amount": commission2, "desc": f"Comisión Stars T2 de {buyer_uid}", "date": str(datetime.datetime.now())})
            await self._save_nolock()

    async def generate_gift_card(self, value: int) -> str:
        async with self._lock:
            code = "GFT-" + uuid.uuid4().hex[:10].upper()
            self.data["coupons"][code] = {"type": "gift_card", "value": value, "used": False, "created": str(datetime.datetime.now())}
            self.data["stats"]["gift_cards_sold"] += 1
            await self._save_nolock()
            return code

    async def redeem_gift_card(self, uid: str, code: str) -> Tuple[bool, str]:
        async with self._lock:
            code = code.strip().upper()
            if code not in self.data["coupons"]:
                return False, "Código de tarjeta inválido."
            card = self.data["coupons"][code]
            if card.get("used"):
                return False, "Esta tarjeta ya fue canjeada."
            if card.get("type") != "gift_card":
                return False, "Código no es una tarjeta regalo."
            
            self.data["coupons"][code]["used"] = True
            self.data["coupons"][code]["used_by"] = uid
            self.data["users"][uid]["points"] += card["value"]
            self.data["transactions"].append({"uid": uid, "amount": card["value"], "desc": f"Tarjeta Regalo Canjeada ({code})", "date": str(datetime.datetime.now())})
            await self._save_nolock()
            return True, f"✅ Tarjeta canjeada. Has recibido **{card['value']} pts**."

    async def get_leaderboard(self, category: str = "points", top_n: int = 10) -> list:
        users = list(self.data["users"].values())
        if category == "points":
            sorted_users = sorted(users, key=lambda x: x.get("points", 0), reverse=True)
        elif category == "downloads":
            sorted_users = sorted(users, key=lambda x: x.get("total_downloads", 0), reverse=True)
        elif category == "referrals":
            sorted_users = sorted(users, key=lambda x: x.get("referrals", 0), reverse=True)
        elif category == "affiliate":
            sorted_users = sorted(users, key=lambda x: x.get("affiliate_earnings", 0), reverse=True)
        else:
            sorted_users = sorted(users, key=lambda x: x.get("level", 0), reverse=True)
        
        return [(u.get("name", "?"), u.get("username", ""), u.get(category, 0)) for u in sorted_users[:top_n]]

    async def start_tournament(self, duration_hours: int = 24, prize_pool_seed: int = 5000):
        async with self._lock:
            end = datetime.datetime.now() + datetime.timedelta(hours=duration_hours)
            self.data["system"]["tournament"] = {
                "active": True, "end_time": end.isoformat(),
                "prize_pool": prize_pool_seed, "participants": {}, "winners": []
            }
            await self._save_nolock()

    async def add_tournament_score(self, uid: str, score: int = 1):
        async with self._lock:
            t = self.data["system"].get("tournament", {})
            if not t.get("active"):
                return
            if t.get("end_time") and datetime.datetime.now() > datetime.datetime.fromisoformat(t["end_time"]):
                t["active"] = False
                await self._save_nolock()
                return
            t["participants"][uid] = t["participants"].get(uid, 0) + score
            self.data["users"][uid]["tournament_score"] = t["participants"][uid]
            t["prize_pool"] += 10
            await self._save_nolock()

    async def finalize_tournament(self) -> list:
        async with self._lock:
            t = self.data["system"].get("tournament", {})
            if not t.get("participants"):
                t["active"] = False
                await self._save_nolock()
                return []
            
            sorted_p = sorted(t["participants"].items(), key=lambda x: x[1], reverse=True)
            pool = t["prize_pool"]
            winners = []
            prizes = [int(pool * 0.5), int(pool * 0.30), int(pool * 0.20)]
            
            for i, (uid, score) in enumerate(sorted_p[:3]):
                prize = prizes[i] if i < len(prizes) else 0
                if prize and uid in self.data["users"]:
                    self.data["users"][uid]["points"] += prize
                    if "TOURNAMENT_WINNER" not in self.data["users"][uid].get("achievements", []) and i == 0:
                        self.data["users"][uid]["achievements"].append("TOURNAMENT_WINNER")
                        self.data["users"][uid]["points"] += EmpireConfig.ACHIEVEMENTS["TOURNAMENT_WINNER"]["reward"]
                    self.data["transactions"].append({"uid": uid, "amount": prize, "desc": f"Premio Torneo #{i+1}", "date": str(datetime.datetime.now())})
                    winners.append((uid, score, prize))
            
            t["active"] = False
            t["winners"] = [{"uid": w[0], "score": w[1], "prize": w[2]} for w in winners]
            t["participants"] = {}
            self.data["stats"]["tournament_prize_pool"] += pool
            await self._save_nolock()
            return winners

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
