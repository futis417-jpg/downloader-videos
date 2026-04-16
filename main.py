"""
SISTEMA: ISHAK HYPER-SAAS V35.0 - ETERNAL OVERLORD
ESTADO: TOTAL CONTROL ENFORCED
PROPIETARIO: Ishak Ezzahouani (ID: 8398522835)
ESTADIO: PRODUCTION READY
"""

import os
import sys
import json
import uuid
import time
import shutil
import asyncio
import logging
import sqlite3
import hashlib
import requests
import traceback
import subprocess
import psutil
from datetime import datetime, timedelta
from threading import Thread
from typing import Dict, List, Any, Optional, Union

# --- AUTOPREPARACIÓN DEL ENTORNO ---
def install_dependencies():
    """Instala las dependencias necesarias de forma silenciosa."""
    critical_deps = ['python-telegram-bot', 'yt-dlp', 'flask', 'requests', 'psutil', 'Pillow']
    for dep in critical_deps:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

install_dependencies()

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, InputFile, LabeledPrice
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters, PreCheckoutQueryHandler
)
from telegram.constants import ParseMode
from flask import Flask, jsonify

# =================================================================
# 1. CONFIGURACIÓN E INFRAESTRUCTURA MAESTRA
# =================================================================
class Config:
    ADMIN_ID = 8398522835
    OWNER_NAME = "Ishak Ezzahouani"
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    VERSION = "35.15.2-OVERLORD"
    
    # Rutas de Archivos
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "vault_data")
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    STORAGE_DIR = os.path.join(BASE_DIR, "buffer_overlord")
    DB_PATH = os.path.join(DATA_DIR, "infinity_v35.json")
    
    # Límites por Plan
    PLANS = {
        "FREE": {
            "name": "🆓 FREE",
            "daily_limit": 5,
            "max_size_mb": 100,
            "resolutions": ["360p", "720p"],
            "support": "Básico",
            "price": 0
        },
        "PRO": {
            "name": "💎 PRO",
            "daily_limit": 50,
            "max_size_mb": 1000,
            "resolutions": ["360p", "720p", "1080p"],
            "support": "Prioritario",
            "price": 10
        },
        "INFINITY": {
            "name": "🚀 INFINITY",
            "daily_limit": 9999,
            "max_size_mb": 4000,
            "resolutions": ["360p", "720p", "1080p", "4K"],
            "support": "Directo Ishak",
            "price": 25
        }
    }

    @classmethod
    def initialize_filesystem(cls):
        """Crea la estructura de carpetas necesaria."""
        for path in [cls.DATA_DIR, cls.LOG_DIR, cls.STORAGE_DIR]:
            os.makedirs(path, exist_ok=True)

Config.initialize_filesystem()

# =================================================================
# 2. LOGGING Y AUDITORÍA
# =================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Config.LOG_DIR, "system.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ISHAK_CORE")

# =================================================================
# 3. GESTIÓN DE BASE DE DATOS (NO-SQL JSON ENGINE)
# =================================================================
class Database:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self.data = {
            "users": {},
            "coupons": {},
            "referrals": {},
            "blacklist": [],
            "stats": {
                "total_dls": 0,
                "total_users": 0,
                "revenue": 0,
                "start_time": time.time()
            },
            "system_settings": {
                "maintenance": False,
                "welcome_text": "🔥 Bienvenido al Ecosistema Ishak V35. Control total.",
                "bot_enabled": True
            }
        }
        self.load()

    def load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.data.update(json.load(f))
            except Exception as e:
                logger.error(f"Error cargando DB: {e}")

    def save(self):
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando DB: {e}")

    def get_user(self, user_obj) -> Dict:
        uid = str(user_obj.id)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "id": user_obj.id,
                "first_name": user_obj.first_name,
                "username": user_obj.username,
                "plan": "FREE",
                "points": 0,
                "downloads": 0,
                "last_active": str(datetime.now()),
                "joined": str(datetime.now().date()),
                "referred_by": None,
                "is_admin": user_obj.id == Config.ADMIN_ID
            }
            self.data["stats"]["total_users"] += 1
            self.save()
        return self.data["users"][uid]

    def update_user(self, uid: Union[str, int], key: str, value: Any):
        uid = str(uid)
        if uid in self.data["users"]:
            self.data["users"][uid][key] = value
            self.save()

db = Database()

# =================================================================
# 4. MOTOR DE DESCARGA PROFESIONAL (YT-DLP)
# =================================================================
class DownloadManager:
    """Clase encargada de la lógica de procesamiento de video y audio."""
    
    @staticmethod
    async def get_info(url: str):
        """Obtiene información de un video antes de descargar."""
        ydl_opts = {'quiet': True, 'no_warnings': True}
        try:
            return await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False))
        except Exception as e:
            logger.error(f"Error obteniendo info: {e}")
            return None

    @staticmethod
    async def download(url: str, format_type: str, quality: str, uid: str):
        """Ejecuta la descarga con parámetros específicos."""
        job_id = f"{uid}_{int(time.time())}"
        output_template = os.path.join(Config.STORAGE_DIR, f"{job_id}.%(ext)s")
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'max_filesize': 2000 * 1024 * 1024, # 2GB
        }

        if format_type == "MP3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            })
        elif format_type == "MP4":
            # Selección de calidad inteligente
            q_map = {"4K": "2160", "1080p": "1080", "720p": "720", "360p": "360"}
            height = q_map.get(quality, "720")
            ydl_opts['format'] = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        def run_dl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)
                if format_type == "MP3":
                    path = os.path.splitext(path)[0] + ".mp3"
                return path, info.get('title', 'Media_Ishak')

        return await asyncio.to_thread(run_dl)

# =================================================================
# 5. GENERADOR DE INTERFACES (UI/UX)
# =================================================================
class Interface:
    """Generador de teclados y mensajes visuales."""
    
    @staticmethod
    def main_keyboard(uid: int):
        user = db.data["users"].get(str(uid), {})
        is_admin = user.get("is_admin", False)
        
        btns = [
            [KeyboardButton("📥 DESCARGAR"), KeyboardButton("👤 MI PERFIL")],
            [KeyboardButton("💎 PLANES VIP"), KeyboardButton("🎁 REFERIDOS")],
            [KeyboardButton("🎟️ CANJEAR CÓDIGO"), KeyboardButton("📊 ESTADÍSTICAS")]
        ]
        if is_admin:
            btns.append([KeyboardButton("👑 PANEL OVERLORD 👑")])
        return ReplyKeyboardMarkup(btns, resize_keyboard=True)

    @staticmethod
    def admin_inline():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("👥 Lista Usuarios", callback_data="adm_list"), 
             InlineKeyboardButton("📢 Global Broadcast", callback_data="adm_bc")],
            [InlineKeyboardButton("🎫 Crear Cupón", callback_data="adm_coupon"), 
             InlineKeyboardButton("🚫 Banear User", callback_data="adm_ban")],
            [InlineKeyboardButton("💰 Modificar Puntos", callback_data="adm_pts"), 
             InlineKeyboardButton("🔄 Reiniciar Bot", callback_data="adm_reboot")],
            [InlineKeyboardButton("🛠 Salud Sistema", callback_data="adm_health"), 
             InlineKeyboardButton("🧹 Limpiar Buffer", callback_data="adm_clean")],
            [InlineKeyboardButton("❌ Cerrar Panel", callback_data="u_close")]
        ])

    @staticmethod
    def format_selector():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Video MP4", callback_data="f_MP4"),
             InlineKeyboardButton("🎵 Audio MP3", callback_data="f_MP3")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="u_close")]
        ])

    @staticmethod
    def quality_selector(plan: str):
        available = Config.PLANS.get(plan, Config.PLANS["FREE"])["resolutions"]
        rows = []
        for res in available:
            rows.append([InlineKeyboardButton(f"🎥 {res}", callback_data=f"q_{res}")])
        rows.append([InlineKeyboardButton("⬅️ Volver", callback_data="f_back")])
        return InlineKeyboardMarkup(rows)

# =================================================================
# 6. HANDLERS: LÓGICA DE COMANDOS
# =================================================================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u_data = db.get_user(user)
    
    # Manejo de Referidos
    if context.args and context.args[0].isdigit():
        referrer_id = context.args[0]
        if referrer_id != str(user.id) and not u_data.get("referred_by"):
            u_data["referred_by"] = referrer_id
            db.update_user(user.id, "referred_by", referrer_id)
            # Dar puntos al referido
            ref_data = db.data["users"].get(referrer_id)
            if ref_data:
                ref_data["points"] += 10
                db.save()
                try: await context.bot.send_message(referrer_id, f"🎊 ¡Alguien se unió con tu link! +10 puntos.")
                except: pass

    await update.message.reply_text(
        f"👑 **{db.data['system_settings']['welcome_text']}**\n\n"
        f"Bienvenido `{user.first_name}`, el sistema está a tus órdenes.\n"
        f"Versión: `{Config.VERSION}`",
        reply_markup=Interface.main_keyboard(user.id),
        parse_mode=ParseMode.MARKDOWN
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    txt = update.message.text
    u_data = db.get_user(user)
    state = context.user_data.get("state")

    # Seguridad: Blacklist
    if str(user.id) in db.data["blacklist"]:
        return await update.message.reply_text("🚫 Acceso denegado. Tu ID está en la lista negra.")

    # --- NAVEGACIÓN PRINCIPAL ---
    if txt == "📥 DESCARGAR":
        await update.message.reply_text("🔗 **Envía el enlace de YouTube, TikTok o Instagram:**")
        context.user_data["state"] = "WAITING_LINK"

    elif txt == "👤 MI PERFIL":
        plan_info = Config.PLANS.get(u_data["plan"], Config.PLANS["FREE"])
        profile = (
            f"👤 **EXPEDIENTE DE USUARIO**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: `{user.id}`\n"
            f"🎭 Rango: **{plan_info['name']}**\n"
            f"💰 Puntos: `{u_data['points']}`\n"
            f"📥 Descargas: `{u_data['downloads']}`\n"
            f"📅 Miembro: `{u_data['joined']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(profile, parse_mode=ParseMode.MARKDOWN)

    elif txt == "🎁 REFERIDOS":
        bot_user = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_user}?start={user.id}"
        msg = (
            f"🎁 **SISTEMA DE REFERIDOS**\n\n"
            f"Invita a tus amigos y gana **10 puntos** por cada uno.\n"
            f"Los puntos se pueden canjear por días VIP PRO.\n\n"
            f"🔗 Tu link: `{link}`"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    elif txt == "💎 PLANES VIP":
        msg = "💎 **SISTEMA DE MEMBRESÍAS**\n\n"
        for p_id, p in Config.PLANS.items():
            msg += f"🔹 **{p['name']}** - {p['price']}€\n   • Límite: {p['daily_limit']} dls/día\n   • Tamaño: {p['max_size_mb']}MB\n\n"
        msg += "👉 Contacta a @Ishak para comprar o usa /canjear."
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    elif txt == "👑 PANEL OVERLORD 👑" and user.id == Config.ADMIN_ID:
        await update.message.reply_text("🛠 **CENTRAL DE COMANDO ISHAK**", reply_markup=Interface.admin_inline())

    # --- MANEJO DE ESTADOS ---
    elif state == "WAITING_LINK":
        if "http" in txt:
            context.user_data["current_url"] = txt
            await update.message.reply_text("⚙️ **Analizando...** Selecciona el tipo de archivo:", reply_markup=Interface.format_selector())
            context.user_data["state"] = None
        else:
            await update.message.reply_text("❌ No parece un enlace válido.")

    elif state == "ADM_BC":
        count = 0
        for uid in db.data["users"]:
            try:
                await context.bot.send_message(uid, f"📢 **COMUNICADO OFICIAL:**\n\n{txt}", parse_mode=ParseMode.MARKDOWN)
                count += 1
                await asyncio.sleep(0.05)
            except: pass
        await update.message.reply_text(f"✅ Difusión completada: {count} recibidos.")
        context.user_data["state"] = None

    elif state == "REDEEM_CODE":
        code = txt.upper()
        if code in db.data["coupons"]:
            plan = db.data["coupons"].pop(code)
            u_data["plan"] = plan
            db.save()
            await update.message.reply_text(f"✅ ¡Cupón válido! Se ha activado el plan **{plan}**.")
        else:
            await update.message.reply_text("❌ Código expirado o inexistente.")
        context.user_data["state"] = None

# =================================================================
# 7. MANEJO DE CALLBACKS (ACCIONES INLINE)
# =================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    data = q.data
    await q.answer()

    # Lógica de Descarga
    if data == "f_MP4":
        u_plan = db.data["users"].get(str(uid))["plan"]
        await q.edit_message_text("🎬 Elige la calidad del video:", reply_markup=Interface.quality_selector(u_plan))
        context.user_data["current_format"] = "MP4"

    elif data == "f_MP3":
        context.user_data["current_format"] = "MP3"
        await execute_download(update, context)

    elif data.startswith("q_"):
        quality = data.split("_")[1]
        context.user_data["current_quality"] = quality
        await execute_download(update, context)

    # Lógica Admin
    elif data.startswith("adm_") and uid == Config.ADMIN_ID:
        if data == "adm_list":
            users = db.data["users"]
            report = "👥 **ESTADO DE USUARIOS**\n\n"
            for sid, d in list(users.items())[-20:]: # Últimos 20
                report += f"• `{sid}` | {d['first_name']} | {d['plan']}\n"
            await q.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)
        
        elif data == "adm_health":
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            msg = (
                f"🖥 **ESTADO DEL SERVIDOR**\n\n"
                f"🚀 CPU: `{psutil.cpu_percent()}%`\n"
                f"📟 RAM: `{mem.percent}%` ({mem.used // 1024**2}MB)\n"
                f"💾 DISCO: `{disk.percent}%` libre\n"
                f"⏱ Uptime Bot: `{str(timedelta(seconds=int(time.time() - db.data['stats']['start_time'])))}`"
            )
            await q.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

        elif data == "adm_bc":
            await q.message.reply_text("✍️ Envía el texto para el Broadcast:")
            context.user_data["state"] = "ADM_BC"

        elif data == "adm_clean":
            shutil.rmtree(Config.STORAGE_DIR)
            os.makedirs(Config.STORAGE_DIR)
            await q.message.reply_text("🧹 Almacenamiento temporal vaciado correctamente.")

    elif data == "u_close":
        await q.message.delete()

# --- ACCIÓN DE DESCARGA FINAL ---
async def execute_download(update, context):
    q = update.callback_query
    uid = q.from_user.id
    url = context.user_data.get("current_url")
    fmt = context.user_data.get("current_format")
    qlty = context.user_data.get("current_quality", "720p")
    
    msg = await q.edit_message_text(f"⚡ **Iniciando Transmisión Overlord...**\n`[{fmt} - {qlty}]`")
    
    try:
        path, title = await DownloadManager.download(url, fmt, qlty, str(uid))
        
        await msg.edit_text("📤 **Subiendo a servidores de Telegram...**")
        
        with open(path, 'rb') as f:
            caption = f"✅ **{title}**\n\n🔥 Descargado por Ishak Hyper-SaaS"
            if fmt == "MP3":
                await context.bot.send_audio(uid, f, caption=caption, parse_mode=ParseMode.MARKDOWN)
            else:
                await context.bot.send_video(uid, f, caption=caption, parse_mode=ParseMode.MARKDOWN)
        
        # Limpieza y Stats
        db.data["stats"]["total_dls"] += 1
        db.data["users"][str(uid)]["downloads"] += 1
        db.save()
        if os.path.exists(path): os.remove(path)
        await msg.delete()

    except Exception as e:
        logger.error(f"Error en descarga: {traceback.format_exc()}")
        await msg.edit_text(f"❌ **Error en el sistema:**\n`{str(e)[:150]}`")

# =================================================================
# 8. SISTEMA WEB (MONITOR DE ESTADO)
# =================================================================
web_app = Flask(__name__)

@web_app.route('/health')
def health():
    return jsonify({
        "status": "OPERATIONAL",
        "owner": Config.OWNER_NAME,
        "version": Config.VERSION,
        "users": len(db.data["users"]),
        "downloads": db.data["stats"]["total_dls"]
    })

def run_flask():
    web_app.run(host='0.0.0.0', port=5000)

# =================================================================
# 9. EJECUCIÓN MAESTRA
# =================================================================
def main():
    print(f"""
    ===========================================
    ISHAK HYPER-SAAS V35 - OVERLORD EDITION
    PROPIETARIO: {Config.OWNER_NAME}
    ===========================================
    Iniciando infraestructura...
    """)
    
    # Iniciar Flask en hilo separado
    Thread(target=run_flask, daemon=True).start()

    # Construir Aplicación de Telegram
    app = ApplicationBuilder().token(Config.TOKEN).build()

    # Registro de Handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Loop Infinito
    print("✅ Bot online. Esperando comandos.")
    app.run_polling()

if __name__ == '__main__':
    try:
        main()
    except Exception:
        print("CRITICAL ERROR DURING STARTUP:")
        traceback.print_exc()
