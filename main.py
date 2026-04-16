"""
SISTEMA: ISHAK HYPER-SAAS V45.0 - THE SINGULARITY EDITION
ESTADO: SUPREME CONTROL - ABSOLUTE HIERARCHY
PROPIETARIO: Ishak Ezzahouani (ID: 8398522835)
PAÍS: España (Sede Central)
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
import signal
from typing import Dict, List, Any, Optional, Union, Tuple

# =================================================================
# [0] PREPARACIÓN DE ENTORNO E INSTALACIÓN (MODO ULTRA)
# =================================================================
def _prepare_environment():
    """Garantiza que el entorno tenga todas las armas necesarias."""
    print("🛡️ Verificando arsenal de dependencias...")
    required = [
        'python-telegram-bot', 
        'yt-dlp', 
        'flask', 
        'requests', 
        'pillow', 
        'psutil', 
        'colorama'
    ]
    for lib in required:
        try:
            __import__(lib.replace('-', '_'))
        except ImportError:
            print(f"📦 Instalando componente faltante: {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

_prepare_environment()

# Importaciones tras verificación
try:
    import psutil
except ImportError:
    psutil = None

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, constants,
    InputMediaPhoto, InputMediaVideo, InputFile
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters, Application
)
from flask import Flask, jsonify

# =================================================================
# [1] CONFIGURACIÓN MAESTRA (OVERLORD CORE)
# =================================================================
class Config:
    ADMIN_ID = 8398522835
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    VERSION = "45.0.0-SINGULARITY"
    
    # Infraestructura de Archivos
    ROOT_DIR = os.getcwd()
    DATA_DIR = os.path.join(ROOT_DIR, "vault_ishak")
    BUFFER_DIR = os.path.join(ROOT_DIR, "buffer_overlord")
    LOGS_DIR = os.path.join(ROOT_DIR, "logs_system")
    DB_FILE = os.path.join(DATA_DIR, "master_database.json")
    
    # Definición de Rangos y Poderes
    PLANS = {
        "FREE": {
            "label": "🆓 CIUDADANO (FREE)", 
            "limit": 5, 
            "size_mb": 150, 
            "speed_limit": "2MB/s",
            "resolutions": ["360p", "720p"],
            "features": ["Descargas básicas", "Soporte comunitario"]
        },
        "PRO": {
            "label": "💎 ÉLITE (PRO)", 
            "limit": 150, 
            "size_mb": 1500, 
            "speed_limit": "20MB/s",
            "resolutions": ["360p", "720p", "1080p"],
            "features": ["Prioridad alta", "Sin anuncios", "Soporte prioritario"]
        },
        "ULTRA": {
            "label": "🔥 SUPREMO (ULTRA)", 
            "limit": 999999, 
            "size_mb": 10000, 
            "speed_limit": "MAX",
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K"],
            "features": ["Control total", "Acceso anticipado", "API Personalizada"]
        }
    }

    # Constantes de Recompensa
    REWARDS = {
        "DAILY": 50,
        "REFERRAL": 250,
        "STREAK_BONUS": 100
    }

    @classmethod
    def setup_system(cls):
        """Inicializa la estructura física del Imperio."""
        for path in [cls.DATA_DIR, cls.BUFFER_DIR, cls.LOGS_DIR]:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        # Limpieza de buffer al iniciar
        for f in os.listdir(cls.BUFFER_DIR):
            try: os.remove(os.path.join(cls.BUFFER_DIR, f))
            except: pass

Config.setup_system()

# =================================================================
# [2] SISTEMA DE LOGS Y AUDITORÍA PRO
# =================================================================
class Audit:
    @staticmethod
    def get_logger():
        l = logging.getLogger("ISHAK_CORE")
        l.setLevel(logging.INFO)
        if not l.handlers:
            fh = logging.FileHandler(os.path.join(Config.LOGS_DIR, "ishak_master.log"))
            sh = logging.StreamHandler(sys.stdout)
            fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            fh.setFormatter(fmt)
            sh.setFormatter(fmt)
            l.addHandler(fh)
            l.addHandler(sh)
        return l

log = Audit.get_logger()

# =================================================================
# [3] GESTIÓN DE BASE DE DATOS (NÚCLEO PERSISTENTE)
# =================================================================
class Database:
    def __init__(self):
        self._lock = threading.Lock()
        self.db_path = Config.DB_FILE
        self.cache = {
            "users": {},
            "coupons": {},
            "blacklist": [],
            "transactions": [],
            "stats": {
                "total_downloads": 0,
                "total_users": 0,
                "points_in_circulation": 0,
                "total_revenue_sim": 0,
                "start_date": str(datetime.datetime.now())
            },
            "config": {
                "maintenance": False,
                "welcome_msg": "👑 **BIENVENIDO AL IMPERIO ISHAK V45**\nSistema operacional y listo.",
                "global_multiplier": 1.0,
                "auto_backup": True
            }
        }
        self.load()

    def load(self):
        with self._lock:
            if os.path.exists(self.db_path):
                try:
                    with open(self.db_path, 'r', encoding='utf-8') as f:
                        self.cache.update(json.load(f))
                except Exception as e:
                    log.error(f"Error crítico cargando DB: {e}")

    def save(self):
        with self._lock:
            try:
                with open(self.db_path, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, indent=4, ensure_ascii=False)
            except Exception as e:
                log.error(f"Error crítico guardando DB: {e}")

    def get_user_template(self, user_obj):
        return {
            "id": user_obj.id,
            "name": user_obj.first_name,
            "username": user_obj.username,
            "plan": "FREE",
            "points": 100,
            "total_downloads": 0,
            "daily_stats": [0, str(datetime.date.today())],
            "last_login": str(datetime.datetime.now()),
            "joined": str(datetime.date.today()),
            "referrals": 0,
            "referred_by": None,
            "is_admin": user_obj.id == Config.ADMIN_ID,
            "banned": False,
            "settings": {"notif": True, "lang": "es"}
        }

    def ensure_user(self, user_obj):
        uid = str(user_obj.id)
        if uid not in self.cache["users"]:
            self.cache["users"][uid] = self.get_user_template(user_obj)
            self.cache["stats"]["total_users"] += 1
            self.save()
            log.info(f"Nuevo usuario registrado: {uid} ({user_obj.first_name})")
        
        # Reset de límites diarios
        u = self.cache["users"][uid]
        today = str(datetime.date.today())
        if u["daily_stats"][1] != today:
            u["daily_stats"] = [0, today]
            self.save()
            
        return u

    def add_points(self, uid, amount, reason="Gift"):
        uid = str(uid)
        if uid in self.cache["users"]:
            self.cache["users"][uid]["points"] += amount
            self.cache["stats"]["points_in_circulation"] += amount
            self.cache["transactions"].append({
                "uid": uid, "amount": amount, "reason": reason, "date": str(datetime.datetime.now())
            })
            self.save()
            return True
        return False

    def ban_user(self, uid):
        uid = str(uid)
        if uid in self.cache["users"]:
            self.cache["users"][uid]["banned"] = True
            if uid not in self.cache["blacklist"]:
                self.cache["blacklist"].append(uid)
            self.save()
            return True
        return False

    def unban_user(self, uid):
        uid = str(uid)
        if uid in self.cache["users"]:
            self.cache["users"][uid]["banned"] = False
            if uid in self.cache["blacklist"]:
                self.cache["blacklist"].remove(uid)
            self.save()
            return True
        return False

db = Database()

# =================================================================
# [4] MOTOR DE DESCARGAS "ISHAK-X" (ULTRA RÁPIDO)
# =================================================================
class IshakXEngine:
    """Motor de procesamiento de medios avanzado con soporte multiformato."""
    
    @staticmethod
    async def get_info(url: str):
        """Extrae metadatos de cualquier URL soportada."""
        opts = {'quiet': True, 'no_warnings': True, 'noplaylist': True}
        def _get():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        try:
            return await asyncio.to_thread(_get)
        except Exception as e:
            log.error(f"Error extrayendo info: {e}")
            return None

    @staticmethod
    async def download(url: str, mode: str, quality: str, uid: str):
        """Procesa la descarga física hacia el buffer."""
        job_token = f"{uid}_{uuid.uuid4().hex[:10]}"
        output_path = os.path.join(Config.BUFFER_DIR, f"{job_token}.%(ext)s")
        
        ydl_opts = {
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'max_filesize': 5000 * 1024 * 1024, # 5GB límite físico
            'cookiefile': None, # Opcional: añadir si hay problemas con YT
        }

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
            height = quality.replace("p", "")
            ydl_opts['format'] = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        def _exec():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                final_file = ydl.prepare_filename(info)
                if mode == "MP3":
                    final_file = os.path.splitext(final_file)[0] + ".mp3"
                return final_file, info.get('title', 'Ishak_Media'), info.get('duration', 0)

        return await asyncio.to_thread(_exec)

# =================================================================
# [5] UI & UX DESIGNER (MATERIAL OVERLORD)
# =================================================================
class UI:
    """Generador de interfaces de usuario para Telegram."""
    
    @staticmethod
    def main_menu(uid):
        u = db.cache["users"].get(str(uid), {})
        is_admin = uid == Config.ADMIN_ID
        
        buttons = [
            [KeyboardButton("📥 DESCARGAR"), KeyboardButton("👤 MI PERFIL")],
            [KeyboardButton("💎 PLANES VIP"), KeyboardButton("🎁 RECOMPENSA")],
            [KeyboardButton("👥 REFERIDOS"), KeyboardButton("🎟️ CANJEAR")],
            [KeyboardButton("📊 ESTADÍSTICAS"), KeyboardButton("🤝 SOPORTE")]
        ]
        if is_admin:
            buttons.append([KeyboardButton("👑 PANEL OVERLORD 👑")])
        return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    @staticmethod
    def admin_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("👥 LISTAR USERS", callback_data="adm_list"), 
             InlineKeyboardButton("📢 BROADCAST", callback_data="adm_bc")],
            [InlineKeyboardButton("🚫 BANEAR", callback_data="adm_ban"), 
             InlineKeyboardButton("🔓 UNBAN", callback_data="adm_unban")],
            [InlineKeyboardButton("💰 DAR PUNTOS", callback_data="adm_pts"), 
             InlineKeyboardButton("🎫 CREAR CÓDIGO", callback_data="adm_cp")],
            [InlineKeyboardButton("📂 EXPLORADOR", callback_data="adm_files"), 
             InlineKeyboardButton("📜 LOGS", callback_data="adm_logs")],
            [InlineKeyboardButton("💾 BACKUP DB", callback_data="adm_backup"), 
             InlineKeyboardButton("🧹 LIMPIAR CACHÉ", callback_data="adm_clean")],
            [InlineKeyboardButton("⚙️ SISTEMA", callback_data="adm_sys"), 
             InlineKeyboardButton("🔄 REINICIAR", callback_data="adm_reboot")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def format_selector():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 VIDEO (MP4)", callback_data="f_MP4"),
             InlineKeyboardButton("🎵 AUDIO (MP3)", callback_data="f_MP3")],
            [InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")]
        ])

    @staticmethod
    def quality_selector(user_plan):
        plan_data = Config.PLANS.get(user_plan, Config.PLANS["FREE"])
        res_list = plan_data["resolutions"]
        rows = []
        for res in res_list:
            rows.append([InlineKeyboardButton(f"🎥 {res}", callback_data=f"q_{res}")])
        rows.append([InlineKeyboardButton("⬅️ VOLVER", callback_data="f_back")])
        return InlineKeyboardMarkup(rows)

# =================================================================
# [6] HANDLERS: CORE LOGIC & COMMANDS
# =================================================================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u_data = db.ensure_user(user)
    
    # Sistema de referidos por link
    if context.args and context.args[0].isdigit():
        ref_id = context.args[0]
        if ref_id != str(user.id) and not u_data.get("referred_by"):
            u_data["referred_by"] = ref_id
            if ref_id in db.cache["users"]:
                db.add_points(ref_id, Config.REWARDS["REFERRAL"], f"Referido: {user.first_name}")
                db.cache["users"][ref_id]["referrals"] += 1
                try:
                    await context.bot.send_message(
                        ref_id, 
                        f"🎊 **¡NUEVO REFERIDO!**\n{user.first_name} se ha unido. +{Config.REWARDS['REFERRAL']} puntos."
                    )
                except: pass
            db.save()

    await update.message.reply_text(
        db.cache["config"]["welcome_msg"].format(name=user.first_name),
        reply_markup=UI.main_menu(user.id),
        parse_mode="Markdown"
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    u_data = db.ensure_user(user)
    state = context.user_data.get("state")

    # Filtro de baneo
    if u_data.get("banned"):
        return await update.message.reply_text("🚫 **ACCESO REVOCADO.** Tu cuenta ha sido suspendida.")

    # --- NAVEGACIÓN DE MENÚ ---
    if text == "📥 DESCARGAR":
        await update.message.reply_text("🔗 **ENVÍA EL LINK (YT, TikTok, IG, FB, Twitter):**")
        context.user_data["state"] = "WAIT_LINK"

    elif text == "👤 MI PERFIL":
        plan = Config.PLANS[u_data["plan"]]
        msg = (
            f"👤 **EXPEDIENTE DE USUARIO**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: `{user.id}`\n"
            f"🎭 Rango: **{plan['label']}**\n"
            f"💰 Puntos: `{u_data['points']}`\n"
            f"📥 Hoy: `{u_data['daily_stats'][0]}/{plan['limit']}`\n"
            f"👥 Referidos: `{u_data['referrals']}`\n"
            f"📅 Miembro desde: `{u_data['joined']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🎁 RECOMPENSA":
        today = str(datetime.date.today())
        if u_data.get("last_daily_claim") == today:
            await update.message.reply_text("❌ Ya has reclamado tu recompensa diaria. Vuelve mañana.")
        else:
            u_data["last_daily_claim"] = today
            db.add_points(user.id, Config.REWARDS["DAILY"], "Recompensa Diaria")
            await update.message.reply_text(f"✅ ¡Has recibido **{Config.REWARDS['DAILY']} puntos**!")

    elif text == "👥 REFERIDOS":
        me = await context.bot.get_me()
        link = f"https://t.me/{me.username}?start={user.id}"
        await update.message.reply_text(
            f"👥 **SISTEMA DE REFERENCIA**\n\n"
            f"Comparte tu link y gana **{Config.REWARDS['REFERRAL']} puntos** por cada usuario nuevo.\n\n"
            f"🔗 `{link}`",
            parse_mode="Markdown"
        )

    elif text == "📊 ESTADÍSTICAS":
        s = db.cache["stats"]
        uptime = str(datetime.datetime.now() - datetime.datetime.fromisoformat(s["start_date"])).split('.')[0]
        msg = (
            f"📊 **MÉTRICAS DEL IMPERIO**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Usuarios: `{s['total_users']}`\n"
            f"📥 Descargas: `{s['total_downloads']}`\n"
            f"💰 Circulación: `{s['points_in_circulation']} pts`\n"
            f"⏱ Uptime: `{uptime}`\n"
            f"🚀 Versión: `{Config.VERSION}`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "👑 PANEL OVERLORD 👑" and user.id == Config.ADMIN_ID:
        await update.message.reply_text("🛠 **CENTRAL DE COMANDO ACTIVADA**", reply_markup=UI.admin_panel())

    # --- MANEJO DE ESTADOS DE ENTRADA ---
    elif state == "WAIT_LINK":
        if "http" in text:
            context.user_data["active_url"] = text
            await update.message.reply_text("⚙️ **Analizando medio...** Selecciona el formato:", reply_markup=UI.format_selector())
        else:
            await update.message.reply_text("❌ Enlace no detectado. Envía una URL válida.")
        context.user_data["state"] = None

    elif state == "ADM_BC" and user.id == Config.ADMIN_ID:
        count = 0
        for sid in list(db.cache["users"].keys()):
            try:
                await context.bot.send_message(sid, f"📢 **MENSAJE DEL OVERLORD:**\n\n{text}", parse_mode="Markdown")
                count += 1
                await asyncio.sleep(0.05) # Anti-spam
            except: pass
        await update.message.reply_text(f"✅ Difusión completada: `{count}` usuarios alcanzados.")
        context.user_data["state"] = None

    elif state == "ADM_BAN" and user.id == Config.ADMIN_ID:
        if db.ban_user(text): await update.message.reply_text(f"🚫 Usuario `{text}` baneado.")
        else: await update.message.reply_text("❌ ID no encontrado.")
        context.user_data["state"] = None

    elif state == "ADM_UNBAN" and user.id == Config.ADMIN_ID:
        if db.unban_user(text): await update.message.reply_text(f"🔓 Usuario `{text}` desbloqueado.")
        else: await update.message.reply_text("❌ ID no encontrado en blacklist.")
        context.user_data["state"] = None

    elif state == "ADM_PTS" and user.id == Config.ADMIN_ID:
        try:
            target, pts = text.split(":")
            db.add_points(target, int(pts), "Admin Gift")
            await update.message.reply_text(f"💰 Se han enviado {pts} puntos a `{target}`.")
        except: await update.message.reply_text("❌ Formato inválido. Usa: `ID:PUNTOS`")
        context.user_data["state"] = None

    elif state == "ADM_CP" and user.id == Config.ADMIN_ID:
        try:
            code, plan = text.upper().split(":")
            db.cache["coupons"][code] = plan
            db.save()
            await update.message.reply_text(f"🎫 Cupón `{code}` creado para plan `{plan}`.")
        except: await update.message.reply_text("❌ Formato: `CODIGO:PLAN` (Ej: ISHAKVIP:PRO)")
        context.user_data["state"] = None

# =================================================================
# [7] CALLBACK DISPATCHER (LÓGICA DE BOTONES INLINE)
# =================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    data = q.data
    await q.answer()

    u_data = db.ensure_user(q.from_user)

    # --- LÓGICA DE DESCARGA ---
    if data.startswith("f_"):
        fmt = data.split("_")[1]
        if fmt == "back":
            return await q.edit_message_text("🎬 Selecciona el formato:", reply_markup=UI.format_selector())
        
        context.user_data["active_fmt"] = fmt
        if fmt == "MP3":
            await start_download_process(update, context)
        else:
            await q.edit_message_text("🎥 Selecciona la calidad del video:", reply_markup=UI.quality_selector(u_data["plan"]))

    elif data.startswith("q_"):
        context.user_data["active_quality"] = data.split("_")[1]
        await start_download_process(update, context)

    # --- LÓGICA DE ADMINISTRACIÓN (SOLO ISHAK) ---
    elif data.startswith("adm_") and uid == Config.ADMIN_ID:
        if data == "adm_list":
            users = db.cache["users"]
            msg = "👥 **ESTADO DE LA POBLACIÓN (Últimos 20):**\n"
            for sid, d in list(users.items())[-20:]:
                msg += f"• `{sid}` | {d['name']} | {d['plan']} | {d['points']} pts\n"
            await q.message.reply_text(msg, parse_mode="Markdown")

        elif data == "adm_bc":
            await q.message.reply_text("✍️ Escribe el mensaje para el Broadcast Global:")
            context.user_data["state"] = "ADM_BC"

        elif data == "adm_ban":
            await q.message.reply_text("🚫 Envía el ID del usuario a banear:")
            context.user_data["state"] = "ADM_BAN"

        elif data == "adm_unban":
            await q.message.reply_text("🔓 Envía el ID del usuario a desbloquear:")
            context.user_data["state"] = "ADM_UNBAN"

        elif data == "adm_pts":
            await q.message.reply_text("💰 Envía el comando `ID:PUNTOS`:")
            context.user_data["state"] = "ADM_PTS"

        elif data == "adm_cp":
            await q.message.reply_text("🎫 Envía el comando `CÓDIGO:PLAN`:")
            context.user_data["state"] = "ADM_CP"

        elif data == "adm_files":
            files = os.listdir(Config.DATA_DIR)
            msg = "📂 **ARCHIVOS EN VAULT:**\n" + "\n".join([f"• `{f}`" for f in files])
            await q.message.reply_text(msg, parse_mode="Markdown")

        elif data == "adm_logs":
            log_path = os.path.join(Config.LOGS_DIR, "ishak_master.log")
            if os.path.exists(log_path):
                await context.bot.send_document(uid, open(log_path, 'rb'), caption="📜 Logs del Sistema")
            else: await q.message.reply_text("❌ No hay logs disponibles.")

        elif data == "adm_backup":
            db.save()
            await context.bot.send_document(uid, open(Config.DB_FILE, 'rb'), caption=f"💾 Master DB Backup - {datetime.datetime.now()}")

        elif data == "adm_clean":
            count = 0
            for f in os.listdir(Config.BUFFER_DIR):
                try: 
                    os.remove(os.path.join(Config.BUFFER_DIR, f))
                    count += 1
                except: pass
            await q.message.reply_text(f"🧹 Se han purgado `{count}` archivos del buffer.")

        elif data == "adm_sys":
            if psutil:
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                msg = (
                    f"🖥 **TELEMETRÍA DE SERVIDOR**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🚀 CPU: `{psutil.cpu_percent()}%` (Cores: {psutil.cpu_count()})\n"
                    f"📟 RAM: `{mem.percent}%` ({mem.used // 1024**2} MB usados)\n"
                    f"💾 DISCO: `{disk.percent}%` ({disk.free // 1024**3} GB libres)\n"
                    f"🐍 Python: `{platform.python_version()}`\n"
                    f"🏗 OS: `{platform.system()} {platform.release()}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
            else: msg = "⚠️ `psutil` no disponible en este entorno."
            await q.message.reply_text(msg, parse_mode="Markdown")

        elif data == "adm_reboot":
            await q.message.reply_text("🔄 **REINICIANDO INFRAESTRUCTURA...**")
            db.save()
            os.execl(sys.executable, sys.executable, *sys.argv)

    elif data == "u_close":
        await q.message.delete()

# --- LÓGICA DE DESCARGA FINAL (ORQUESTADOR) ---
async def start_download_process(update, context):
    q = update.callback_query
    uid = q.from_user.id
    url = context.user_data.get("active_url")
    fmt = context.user_data.get("active_fmt")
    qlty = context.user_data.get("active_quality", "720p")
    u_data = db.ensure_user(q.from_user)

    # 1. Verificación de límites
    plan = Config.PLANS[u_data["plan"]]
    if u_data["daily_stats"][0] >= plan["limit"]:
        return await q.edit_message_text(
            f"❌ **LÍMITE ALCANZADO.** Tu plan permite {plan['limit']} descargas/día.\n"
            f"Adquiere un plan **PRO** o **ULTRA** para continuar."
        )

    # 2. Inicio de UI de progreso
    status = await q.edit_message_text(f"⚡ **GENERANDO TÚNEL DE DATOS...**\n`[{fmt} | {qlty}]`")
    
    try:
        # 3. Descarga vía Motor Ishak-X
        path, title, duration = await IshakXEngine.download(url, fmt, qlty, str(uid))
        
        # 4. Envío al usuario
        await status.edit_text("📤 **SUBIENDO AL SATÉLITE DE TELEGRAM...**")
        
        with open(path, 'rb') as f:
            cap = (
                f"✅ **{title}**\n\n"
                f"⏱ Duración: `{str(datetime.timedelta(seconds=duration))}`\n"
                f"⚡ Motor: `Ishak-Singularity V45`"
            )
            if fmt == "MP3":
                await context.bot.send_audio(uid, f, caption=cap, parse_mode="Markdown")
            else:
                await context.bot.send_video(uid, f, caption=cap, parse_mode="Markdown")

        # 5. Actualización de DB
        u_data["daily_stats"][0] += 1
        u_data["total_downloads"] += 1
        db.cache["stats"]["total_downloads"] += 1
        db.save()
        
        # 6. Cleanup
        if os.path.exists(path): os.remove(path)
        await status.delete()

    except Exception as e:
        log.error(f"Error en flujo de descarga: {traceback.format_exc()}")
        await status.edit_text(f"❌ **ERROR CRÍTICO DEL MOTOR:**\n`{str(e)[:200]}`")

# =================================================================
# [8] SERVIDOR WEB DE MANTENIMIENTO (FLASK)
# =================================================================
web_app = Flask(__name__)

@web_app.route('/')
def ping():
    return jsonify({
        "status": "OPERATIONAL",
        "empire": "ISHAK HYPER-SAAS",
        "version": Config.VERSION,
        "metrics": {
            "users": len(db.cache["users"]),
            "downloads": db.cache["stats"]["total_downloads"]
        }
    })

def run_flask():
    try:
        port = int(os.getenv("PORT", 5000))
        web_app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Flask Error: {e}")

# =================================================================
# [9] LANZAMIENTO SUPREMO
# =================================================================
def main():
    print(f"""
    ==================================================
    ISHAK HYPER-SAAS V{Config.VERSION}
    ESTADO: LISTO PARA LA DOMINACIÓN
    ==================================================
    """)
    
    # Iniciar Flask en hilo independiente para mantener el servicio
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Construir aplicación de Telegram
    app = ApplicationBuilder().token(Config.TOKEN).build()

    # Registro de Handlers de Comandos y Mensajes
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Ejecución
    print("🚀 NÚCLEO SINGULARITY ONLINE.")
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Apagado por el administrador.")
    except Exception:
        traceback.print_exc()
