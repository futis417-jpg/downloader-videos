"""
SISTEMA: ISHAK HYPER-SAAS V40.0 - ABSOLUTE ZERO EDITION
ESTADO: TOTAL CONTROL OVERLORD - ULTIMATE HIERARCHY
PROPIETARIO: Ishak Ezzahouani (ID: 8398522835)
PAÍS: España (Control Central)
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
from typing import Dict, List, Any, Optional, Union

# =================================================================
# [0] AUTO-INSTALLER & DEPENDENCY CHECK (MILITARY GRADE)
# =================================================================
def _prepare_environment():
    """Asegura que todas las dependencias estén presentes."""
    required = ['python-telegram-bot', 'yt-dlp', 'flask', 'requests', 'pillow', 'psutil']
    for lib in required:
        try:
            __import__(lib.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

_prepare_environment()

# Importaciones Críticas
try:
    import psutil
except ImportError:
    psutil = None

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, constants,
    InputMediaPhoto, InputMediaVideo
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from flask import Flask, jsonify

# =================================================================
# [1] CONFIGURACIÓN MAESTRA (OVERLORD SETTINGS)
# =================================================================
class Config:
    ADMIN_ID = 8398522835
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    VERSION = "40.50.0-ZERO"
    
    # Rutas de Infraestructura
    ROOT_DIR = os.getcwd()
    DATA_DIR = os.path.join(ROOT_DIR, "vault_overlord")
    BUFFER_DIR = os.path.join(ROOT_DIR, "buffer_downloads")
    LOGS_DIR = os.path.join(ROOT_DIR, "system_logs")
    DB_FILE = os.path.join(DATA_DIR, "overlord_master.json")
    
    # Parámetros de Negocio
    PLANS = {
        "FREE": {
            "label": "🆓 CIVIL (FREE)", 
            "limit": 5, 
            "size_mb": 100, 
            "speed": "Standard",
            "resolutions": ["360p", "720p"]
        },
        "PRO": {
            "label": "💎 ELITE (PRO)", 
            "limit": 100, 
            "size_mb": 1000, 
            "speed": "High-Speed",
            "resolutions": ["360p", "720p", "1080p"]
        },
        "ZERO": {
            "label": "🔥 ABSOLUTE ZERO", 
            "limit": 99999, 
            "size_mb": 5000, 
            "speed": "Unlimited",
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K"]
        }
    }

    # Mensajería Central
    MSG_WELCOME = "🔥 **SISTEMA ISHAK V40 ACTIVO**\nBienvenido al centro de mando, {name}."
    MSG_MAINTENANCE = "⚠️ **SISTEMA EN MANTENIMIENTO**\nIshak está ajustando los engranajes. Vuelve pronto."

    @classmethod
    def setup(cls):
        """Crea la estructura de carpetas necesaria."""
        for d in [cls.DATA_DIR, cls.BUFFER_DIR, cls.LOGS_DIR]:
            os.makedirs(d, exist_ok=True)

Config.setup()

# =================================================================
# [2] LOGGING & AUDITORÍA
# =================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Config.LOGS_DIR, "master.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ISHAK_OVERLORD")

# =================================================================
# [3] BASE DE DATOS HYPER-SCALABLE (JSON ENGINE)
# =================================================================
class Database:
    def __init__(self):
        self._lock = threading.Lock()
        self.data = {
            "users": {},
            "coupons": {},
            "blacklist": [],
            "stats": {
                "total_downloads": 0,
                "total_users": 0,
                "total_points_distributed": 0,
                "server_start": str(datetime.datetime.now())
            },
            "system": {
                "maint_mode": False,
                "global_announcement": None,
                "daily_reward": 20
            }
        }
        self.load()

    def load(self):
        with self._lock:
            if os.path.exists(Config.DB_FILE):
                try:
                    with open(Config.DB_FILE, 'r', encoding='utf-8') as f:
                        self.data.update(json.load(f))
                except Exception as e:
                    logger.error(f"Error cargando base de datos: {e}")

    def save(self):
        with self._lock:
            try:
                with open(Config.DB_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error guardando base de datos: {e}")

    def get_user(self, user_obj):
        uid = str(user_obj.id)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "id": user_obj.id,
                "name": user_obj.first_name,
                "username": user_obj.username,
                "plan": "FREE",
                "points": 10,
                "total_downloads": 0,
                "daily_downloads": [0, str(datetime.date.today())],
                "last_daily_claim": None,
                "joined_at": str(datetime.date.today()),
                "is_banned": False,
                "referred_by": None,
                "referrals": 0,
                "language": "es"
            }
            self.data["stats"]["total_users"] += 1
            self.save()
        
        # Reset diario de límites
        u = self.data["users"][uid]
        today = str(datetime.date.today())
        if u["daily_downloads"][1] != today:
            u["daily_downloads"] = [0, today]
            self.save()
            
        return u

    def ban_user(self, uid):
        uid = str(uid)
        if uid in self.data["users"]:
            self.data["users"][uid]["is_banned"] = True
            if uid not in self.data["blacklist"]:
                self.data["blacklist"].append(uid)
            self.save()
            return True
        return False

    def add_points(self, uid, amount):
        uid = str(uid)
        if uid in self.data["users"]:
            self.data["users"][uid]["points"] += amount
            self.data["stats"]["total_points_distributed"] += amount
            self.save()
            return True
        return False

db = Database()

# =================================================================
# [4] MOTOR DE DESCARGA HYPER-SPEED (PRO-ENGINE)
# =================================================================
class DownloadEngine:
    """Motor especializado en extracción de medios con post-procesamiento."""
    
    @staticmethod
    async def get_metadata(url: str):
        """Extrae metadatos sin descargar."""
        ydl_opts = {'quiet': True, 'no_warnings': True, 'noplaylist': True}
        def _get():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        return await asyncio.to_thread(_get)

    @staticmethod
    async def run(url: str, mode: str, quality: str, uid: str):
        """Ejecuta la descarga física."""
        job_id = f"job_{uid}_{uuid.uuid4().hex[:8]}"
        out_tmpl = os.path.join(Config.BUFFER_DIR, f"{job_id}.%(ext)s")
        
        # Configuración de YT-DLP
        ydl_opts = {
            'outtmpl': out_tmpl,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'max_filesize': 2000 * 1024 * 1024, # 2GB
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
            # Mapeo de resolución
            h = quality.replace("p", "")
            ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        def _exec():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(res)
                if mode == "MP3":
                    path = os.path.splitext(path)[0] + ".mp3"
                return path, res.get('title', 'Media_Ishak')

        try:
            return await asyncio.to_thread(_exec)
        except Exception as e:
            logger.error(f"Error en motor descarga: {e}")
            raise e

# =================================================================
# [5] UI COMPONENT GENERATOR (DINÁMICO)
# =================================================================
class UI:
    """Generador de teclados y menús visuales."""
    
    @staticmethod
    def main_keyboard(uid):
        u = db.data["users"].get(str(uid), {})
        is_admin = uid == Config.ADMIN_ID
        
        kb = [
            [KeyboardButton("📥 DESCARGAR"), KeyboardButton("👤 MI PERFIL")],
            [KeyboardButton("💎 PLANES VIP"), KeyboardButton("🎁 RECOMPENSA")],
            [KeyboardButton("👥 REFERIDOS"), KeyboardButton("🎟️ CANJEAR")],
            [KeyboardButton("📊 ESTADÍSTICAS"), KeyboardButton("🤝 SOPORTE")]
        ]
        if is_admin:
            kb.append([KeyboardButton("👑 PANEL OVERLORD 👑")])
        return ReplyKeyboardMarkup(kb, resize_keyboard=True)

    @staticmethod
    def admin_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 LISTAR USUARIOS", callback_data="adm_list"), 
             InlineKeyboardButton("📢 BROADCAST", callback_data="adm_bc")],
            [InlineKeyboardButton("🚫 BANEAR USER", callback_data="adm_ban"), 
             InlineKeyboardButton("🔓 UNBAN USER", callback_data="adm_unban")],
            [InlineKeyboardButton("💰 DAR PUNTOS", callback_data="adm_pts"), 
             InlineKeyboardButton("🎫 GENERAR CUPÓN", callback_data="adm_cp")],
            [InlineKeyboardButton("📂 EXPLORADOR", callback_data="adm_files"), 
             InlineKeyboardButton("📜 LOGS", callback_data="adm_logs")],
            [InlineKeyboardButton("💾 BACKUP MASTER", callback_data="adm_backup"), 
             InlineKeyboardButton("🧹 LIMPIAR CACHÉ", callback_data="adm_clean")],
            [InlineKeyboardButton("⚙️ SISTEMA", callback_data="adm_sys"), 
             InlineKeyboardButton("🔄 REINICIAR", callback_data="adm_reboot")],
            [InlineKeyboardButton("❌ CERRAR PANEL", callback_data="u_close")]
        ])

    @staticmethod
    def format_selector():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 VIDEO (MP4)", callback_data="fmt_MP4"),
             InlineKeyboardButton("🎵 AUDIO (MP3)", callback_data="fmt_MP3")],
            [InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")]
        ])

    @staticmethod
    def quality_selector(plan_type):
        available = Config.PLANS.get(plan_type, Config.PLANS["FREE"])["resolutions"]
        btns = []
        for q in available:
            btns.append([InlineKeyboardButton(f"🎥 {q}", callback_data=f"ql_{q}")])
        btns.append([InlineKeyboardButton("⬅️ ATRÁS", callback_data="fmt_back")])
        return InlineKeyboardMarkup(btns)

# =================================================================
# [6] LÓGICA DE NEGOCIO (HANDLERS)
# =================================================================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u_data = db.get_user(user)
    
    # Manejo de Referidos Profundo
    if context.args and context.args[0].isdigit():
        ref_id = context.args[0]
        if ref_id != str(user.id) and not u_data.get("referred_by"):
            u_data["referred_by"] = ref_id
            if ref_id in db.data["users"]:
                db.data["users"][ref_id]["points"] += 100
                db.data["users"][ref_id]["referrals"] += 1
                try: await context.bot.send_message(ref_id, "🎊 **¡NUEVO REFERIDO!**\nHas ganado 100 puntos.")
                except: pass
            db.save()

    await update.message.reply_text(
        Config.MSG_WELCOME.format(name=user.first_name),
        reply_markup=UI.main_keyboard(user.id),
        parse_mode="Markdown"
    )

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    txt = update.message.text
    u_data = db.get_user(user)
    state = context.user_data.get("state")

    # Seguridad: Banned Check
    if u_data.get("is_banned"):
        return await update.message.reply_text("🚫 Acceso revocado por el Overlord Ishak.")

    # [1] NAVEGACIÓN PRINCIPAL
    if txt == "📥 DESCARGAR":
        await update.message.reply_text("🔗 **Pega el enlace ahora mismo:**")
        context.user_data["state"] = "AWAIT_URL"

    elif txt == "👤 MI PERFIL":
        plan = Config.PLANS[u_data["plan"]]
        msg = (
            f"👤 **EXPEDIENTE: {user.first_name}**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: `{user.id}`\n"
            f"🎭 Rango: **{plan['label']}**\n"
            f"💰 Puntos: `{u_data['points']}`\n"
            f"📥 Hoy: `{u_data['daily_downloads'][0]}/{plan['limit']}`\n"
            f"👥 Referidos: `{u_data['referrals']}`\n"
            f"📅 Miembro: `{u_data['joined_at']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif txt == "🎁 RECOMPENSA":
        today = str(datetime.date.today())
        if u_data.get("last_daily_claim") == today:
            await update.message.reply_text("❌ Ya has reclamado tu recompensa hoy. Vuelve mañana.")
        else:
            reward = db.data["system"]["daily_reward"]
            u_data["points"] += reward
            u_data["last_daily_claim"] = today
            db.save()
            await update.message.reply_text(f"✅ ¡Has recibido **{reward} puntos** de Ishak!")

    elif txt == "👥 REFERIDOS":
        bot_user = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_user}?start={user.id}"
        await update.message.reply_text(
            f"👥 **SISTEMA DE REFERENCIA**\n\n"
            f"Gana 100 puntos por cada persona que invites.\n\n"
            f"🔗 Tu link único:\n`{link}`",
            parse_mode="Markdown"
        )

    elif txt == "📊 ESTADÍSTICAS":
        s = db.data["stats"]
        uptime = str(datetime.datetime.now() - datetime.datetime.fromisoformat(s["server_start"])).split('.')[0]
        msg = (
            f"📊 **MÉTRICAS DEL IMPERIO**\n\n"
            f"👥 Usuarios: `{s['total_users']}`\n"
            f"📥 Descargas: `{s['total_downloads']}`\n"
            f"💰 Economía: `{s['total_points_distributed']} pts`\n"
            f"⏱ Uptime: `{uptime}`\n"
            f"🚀 Versión: `{Config.VERSION}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif txt == "👑 PANEL OVERLORD 👑" and user.id == Config.ADMIN_ID:
        await update.message.reply_text("🛠 **MODO ADMINISTRADOR ACTIVADO**", reply_markup=UI.admin_panel())

    # [2] MANEJO DE ESTADOS
    elif state == "AWAIT_URL":
        if "http" in txt:
            context.user_data["active_url"] = txt
            await update.message.reply_text("🛠 **Enlace capturado.** Elige el formato:", reply_markup=UI.format_selector())
        else:
            await update.message.reply_text("❌ Enlace basura. Envía algo real.")
        context.user_data["state"] = None

    elif state == "ADM_BC" and user.id == Config.ADMIN_ID:
        count = 0
        for sid in db.data["users"]:
            try:
                await context.bot.send_message(sid, f"📢 **MENSAJE DEL OVERLORD:**\n\n{txt}", parse_mode="Markdown")
                count += 1
                await asyncio.sleep(0.05)
            except: pass
        await update.message.reply_text(f"✅ Difusión finalizada: `{count}` usuarios.")
        context.user_data["state"] = None

    elif state == "ADM_PTS" and user.id == Config.ADMIN_ID:
        try:
            target_id, pts = txt.split(":")
            if db.add_points(target_id, int(pts)):
                await update.message.reply_text(f"✅ {pts} puntos añadidos a {target_id}.")
            else:
                await update.message.reply_text("❌ Usuario no encontrado.")
        except:
            await update.message.reply_text("❌ Formato: ID:PUNTOS")
        context.user_data["state"] = None

# =================================================================
# [7] MANEJO DE CALLBACKS (ACCIONES)
# =================================================================
async def callback_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    data = q.data
    await q.answer()

    u_data = db.get_user(q.from_user)

    # NAVEGACIÓN DE DESCARGA
    if data.startswith("fmt_"):
        mode = data.split("_")[1]
        if mode == "back":
            return await q.edit_message_text("🎬 Elige el formato:", reply_markup=UI.format_selector())
        
        context.user_data["active_mode"] = mode
        if mode == "MP3":
            await process_download_final(update, context)
        else:
            await q.edit_message_text("🎥 Selecciona la calidad deseada:", reply_markup=UI.quality_selector(u_data["plan"]))

    elif data.startswith("ql_"):
        context.user_data["active_quality"] = data.split("_")[1]
        await process_download_final(update, context)

    # ACCIONES ADMIN
    elif data.startswith("adm_") and uid == Config.ADMIN_ID:
        if data == "adm_list":
            users = db.data["users"]
            msg = "👥 **ÚLTIMOS 20 USUARIOS:**\n"
            for sid, d in list(users.items())[-20:]:
                msg += f"• `{sid}` | {d['name']} | {d['plan']} | {d['points']} pts\n"
            await q.message.reply_text(msg, parse_mode="Markdown")

        elif data == "adm_bc":
            await q.message.reply_text("✍️ Escribe el mensaje para el Broadcast:")
            context.user_data["state"] = "ADM_BC"

        elif data == "adm_pts":
            await q.message.reply_text("✍️ Formato `ID:PUNTOS` para añadir:")
            context.user_data["state"] = "ADM_PTS"

        elif data == "adm_backup":
            db.save()
            with open(Config.DB_FILE, 'rb') as f:
                await context.bot.send_document(uid, f, caption=f"💾 Master DB V40 - {datetime.datetime.now()}")

        elif data == "adm_clean":
            count = 0
            for f in os.listdir(Config.BUFFER_DIR):
                os.remove(os.path.join(Config.BUFFER_DIR, f))
                count += 1
            await q.message.reply_text(f"🧹 Se han purgado {count} archivos del buffer.")

        elif data == "adm_sys":
            # Engine de info de sistema
            if psutil:
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                msg = (
                    f"🖥 **ESTADO DEL SERVIDOR**\n\n"
                    f"🚀 CPU: `{psutil.cpu_percent()}%` (Cores: {psutil.cpu_count()})\n"
                    f"📟 RAM: `{mem.percent}%` ({mem.used // 1024**2} MB)\n"
                    f"💾 DISCO: `{disk.percent}%` ({disk.free // 1024**3} GB libres)\n"
                    f"🐍 Python: `{platform.python_version()}`"
                )
            else:
                msg = "⚠️ `psutil` no disponible. No hay telemetría."
            await q.message.reply_text(msg, parse_mode="Markdown")

        elif data == "adm_reboot":
            await q.message.reply_text("🔄 Reiniciando motor principal...")
            os.execl(sys.executable, sys.executable, *sys.argv)

    elif data == "u_close":
        await q.message.delete()

async def process_download_final(update, context):
    q = update.callback_query
    uid = q.from_user.id
    url = context.user_data.get("active_url")
    mode = context.user_data.get("active_mode")
    quality = context.user_data.get("active_quality", "720p")
    u_data = db.get_user(q.from_user)

    # Verificación de Límites
    limit = Config.PLANS[u_data["plan"]]["limit"]
    if u_data["daily_downloads"][0] >= limit:
        return await q.edit_message_text("❌ Has alcanzado tu límite diario. Sube de rango para continuar.")

    status_msg = await q.edit_message_text(f"⚡ **GENERANDO TÚNEL DE DATOS...**\n`[{mode} | {quality}]`")
    
    try:
        path, title = await DownloadEngine.run(url, mode, quality, str(uid))
        
        await status_msg.edit_text("📤 **SUBIENDO AL SATÉLITE...**")
        
        with open(path, 'rb') as f:
            caption = (
                f"✅ **{title}**\n\n"
                f"👤 Usuario: `{q.from_user.first_name}`\n"
                f"⚡ Engine: `Ishak Zero-V40`"
            )
            if mode == "MP3":
                await context.bot.send_audio(uid, f, caption=caption, parse_mode="Markdown")
            else:
                await context.bot.send_video(uid, f, caption=caption, parse_mode="Markdown")
        
        # Log & Stats
        u_data["daily_downloads"][0] += 1
        u_data["total_downloads"] += 1
        db.data["stats"]["total_downloads"] += 1
        db.save()
        
        # Cleanup
        if os.path.exists(path): os.remove(path)
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Error fatal descarga: {traceback.format_exc()}")
        await status_msg.edit_text(f"❌ **ERROR DE SISTEMA:**\n`{str(e)[:150]}`")

# =================================================================
# [8] WEB STATUS SERVER (FLASK)
# =================================================================
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return jsonify({
        "system": "ISHAK HYPER-SAAS",
        "status": "OPERATIONAL",
        "version": Config.VERSION,
        "active_users": len(db.data["users"]),
        "downloads": db.data["stats"]["total_downloads"]
    })

def run_flask():
    web_app.run(host='0.0.0.0', port=os.getenv("PORT", 5000))

# =================================================================
# [9] EJECUCIÓN MAESTRA
# =================================================================
def main():
    print(f"--- ISHAK HYPER-SAAS V{Config.VERSION} ---")
    
    # Iniciar Flask
    threading.Thread(target=run_web, daemon=True).start()
    
    # Configurar Telegram
    application = ApplicationBuilder().token(Config.TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))
    application.add_handler(CallbackQueryHandler(callback_dispatcher))

    # Lanzamiento
    print("🚀 SISTEMA ONLINE. ESPERANDO ÓRDENES.")
    application.run_polling()

def run_web():
    try:
        web_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
    except Exception as e:
        print(f"Error Flask: {e}")

if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
