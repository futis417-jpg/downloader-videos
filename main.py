"""
SISTEMA: ISHAK HYPER-SAAS V60.0 - ETERNAL EMPIRE EDITION
ESTADO: TOTAL SUPREMACY - OVERLORD CONTROL
PROPIETARIO: Ishak Ezzahouani (ID: 8398522835)
PAÍS: España (Control Centralizado)
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
from typing import Dict, List, Any, Optional, Union, Tuple

# =================================================================
# [0] INICIALIZACIÓN DE DEPENDENCIAS CRÍTICAS
# =================================================================
def bootstrap_packages():
    """Garantiza que el entorno tenga todas las herramientas necesarias."""
    essential = ['python-telegram-bot', 'yt_dlp', 'flask', 'requests', 'psutil', 'Pillow']
    for package in essential:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"📦 Instalando {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    # Inyección en espacio global para evitar errores de 'not defined'
    global yt_dlp, requests, psutil
    import yt_dlp, requests, psutil

bootstrap_packages()

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
# [1] CONFIGURACIÓN DE NIVEL EMPRESARIAL
# =================================================================
class EmpireConfig:
    ADMIN_ID = 8398522835
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    VERSION = "60.25.0-EMPIRE"
    
    # Directorios de Operaciones
    ROOT = os.getcwd()
    VAULT_DIR = os.path.join(ROOT, "empire_vault")
    BUFFER_DIR = os.path.join(ROOT, "download_buffer")
    LOGS_DIR = os.path.join(ROOT, "system_logs")
    DATABASE_PATH = os.path.join(VAULT_DIR, "empire_db.json")
    
    # Configuración de Planes de Suscripción
    PLANS = {
        "FREE": {
            "name": "🆓 CIUDADANO (FREE)",
            "limit_daily": 5,
            "max_file_mb": 100,
            "resolutions": ["360p", "720p"],
            "speed": "Básica"
        },
        "PRO": {
            "name": "💎 ÉLITE (PRO)",
            "limit_daily": 100,
            "max_file_mb": 1500,
            "resolutions": ["360p", "720p", "1080p"],
            "speed": "Alta Velocidad"
        },
        "ULTRA": {
            "name": "🔥 SOBERANO (ULTRA)",
            "limit_daily": 99999,
            "max_file_mb": 5000,
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K"],
            "speed": "Instántanea"
        }
    }

    # Economía del Sistema
    REWARDS = {
        "DAILY": 100,
        "REFERRAL": 500
    }

    @classmethod
    def init_filesystem(cls):
        """Prepara el servidor para la ejecución."""
        for d in [cls.VAULT_DIR, cls.BUFFER_DIR, cls.LOGS_DIR]:
            os.makedirs(d, exist_ok=True)

EmpireConfig.init_filesystem()

# =================================================================
# [2] SISTEMA DE AUDITORÍA Y REGISTRO
# =================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "empire_core.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("EMPIRE_ISHAK")

# =================================================================
# [3] BASE DE DATOS DE ALTA DISPONIBILIDAD
# =================================================================
class EmpireDatabase:
    def __init__(self):
        self._lock = threading.Lock()
        self.data = {
            "users": {},
            "coupons": {},
            "blacklist": [],
            "stats": {
                "total_downloads": 0,
                "total_users": 0,
                "revenue_sim": 0,
                "boot_time": str(datetime.datetime.now())
            },
            "system": {
                "maint_mode": False,
                "welcome_text": "👑 **BIENVENIDO AL IMPERIO ISHAK V60**\nTu portal de acceso a la red global.",
                "global_announcement": None
            }
        }
        self.load()

    def load(self):
        with self._lock:
            if os.path.exists(EmpireConfig.DATABASE_PATH):
                try:
                    with open(EmpireConfig.DATABASE_PATH, 'r', encoding='utf-8') as f:
                        self.data.update(json.load(f))
                except Exception as e:
                    logger.error(f"Error cargando DB: {e}")

    def save(self):
        with self._lock:
            try:
                with open(EmpireConfig.DATABASE_PATH, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error guardando DB: {e}")

    def sync_user(self, user_obj):
        uid = str(user_obj.id)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "id": user_obj.id,
                "name": user_obj.first_name,
                "username": user_obj.username,
                "plan": "FREE",
                "points": 250,
                "total_dls": 0,
                "daily_dls": [0, str(datetime.date.today())],
                "referrals": 0,
                "referred_by": None,
                "joined": str(datetime.date.today()),
                "is_banned": False,
                "last_daily": None
            }
            self.data["stats"]["total_users"] += 1
            self.save()
        
        # Reset de contador diario
        u = self.data["users"][uid]
        today = str(datetime.date.today())
        if u["daily_dls"][1] != today:
            u["daily_dls"] = [0, today]
            self.save()
            
        return u

db = EmpireDatabase()

# =================================================================
# [4] MOTOR DE DESCARGA "ISHAK-EMPIRE-X"
# =================================================================
class DownloadProcessor:
    """Motor de procesamiento de medios optimizado para velocidad y bypass."""
    
    @staticmethod
    async def get_metadata(url: str):
        opts = {'quiet': True, 'no_warnings': True, 'noplaylist': True}
        def _get():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        try:
            return await asyncio.to_thread(_get)
        except Exception as e:
            logger.error(f"Metadata fail: {e}")
            return None

    @staticmethod
    async def start(url: str, mode: str, quality: str, uid: str):
        """Ejecuta la descarga en el buffer del imperio."""
        file_id = f"ishak_{uid}_{uuid.uuid4().hex[:12]}"
        output_template = os.path.join(EmpireConfig.BUFFER_DIR, f"{file_id}.%(ext)s")
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'max_filesize': 2000 * 1024 * 1024, # 2GB
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
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
            h = quality.replace("p", "")
            ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        def _do_work():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                path = ydl.prepare_filename(info)
                if mode == "MP3":
                    path = os.path.splitext(path)[0] + ".mp3"
                return path, info.get('title', 'Media_Empire'), info.get('duration', 0)

        return await asyncio.to_thread(_do_work)

# =================================================================
# [5] DISEÑADOR DE INTERFACES (EMPIRE UI)
# =================================================================
class EmpireUI:
    """Generador de componentes visuales para el Imperio."""
    
    @staticmethod
    def main_keyboard(uid):
        user = db.data["users"].get(str(uid), {})
        is_admin = uid == EmpireConfig.ADMIN_ID
        
        rows = [
            [KeyboardButton("📥 DESCARGAR"), KeyboardButton("👤 MI PERFIL")],
            [KeyboardButton("💎 TIENDA VIP"), KeyboardButton("🎁 RECOMPENSA")],
            [KeyboardButton("👥 REFERIDOS"), KeyboardButton("🎟️ CANJEAR")],
            [KeyboardButton("📊 ESTADÍSTICAS"), KeyboardButton("🤝 SOPORTE")]
        ]
        if is_admin:
            rows.append([KeyboardButton("👑 PANEL OVERLORD 👑")])
        return ReplyKeyboardMarkup(rows, resize_keyboard=True)

    @staticmethod
    def overlord_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 LISTA USERS", callback_data="adm_list"), 
             InlineKeyboardButton("📢 BROADCAST", callback_data="adm_bc")],
            [InlineKeyboardButton("🚫 BANEAR", callback_data="adm_ban"), 
             InlineKeyboardButton("🔓 DESBANEAR", callback_data="adm_unban")],
            [InlineKeyboardButton("💰 SUMAR PUNTOS", callback_data="adm_pts"), 
             InlineKeyboardButton("🎫 CREAR CUPÓN", callback_data="adm_cp")],
            [InlineKeyboardButton("📂 ARCHIVOS", callback_data="adm_files"), 
             InlineKeyboardButton("📜 LOGS", callback_data="adm_logs")],
            [InlineKeyboardButton("💾 BACKUP DB", callback_data="adm_backup"), 
             InlineKeyboardButton("🧹 LIMPIAR CACHÉ", callback_data="adm_clean")],
            [InlineKeyboardButton("⚙️ SISTEMA", callback_data="adm_sys"), 
             InlineKeyboardButton("🔄 REINICIAR", callback_data="adm_reboot")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def format_picker():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 VIDEO (MP4)", callback_data="f_MP4"),
             InlineKeyboardButton("🎵 AUDIO (MP3)", callback_data="f_MP3")],
            [InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")]
        ])

    @staticmethod
    def quality_picker(plan_id):
        qualities = EmpireConfig.PLANS.get(plan_id, EmpireConfig.PLANS["FREE"])["resolutions"]
        btns = []
        for q in qualities:
            btns.append([InlineKeyboardButton(f"🎥 {q}", callback_data=f"q_{q}")])
        btns.append([InlineKeyboardButton("⬅️ ATRÁS", callback_data="f_back")])
        return InlineKeyboardMarkup(btns)

# =================================================================
# [6] CONTROLADORES DE COMANDOS Y LÓGICA DE USUARIO
# =================================================================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u_data = db.sync_user(user)
    
    # Manejo de Referidos
    if context.args and context.args[0].isdigit():
        ref_id = context.args[0]
        if ref_id != str(user.id) and not u_data.get("referred_by"):
            u_data["referred_by"] = ref_id
            if ref_id in db.data["users"]:
                db.data["users"][ref_id]["points"] += EmpireConfig.REWARDS["REFERRAL"]
                db.data["users"][ref_id]["referrals"] += 1
                try:
                    await context.bot.send_message(
                        ref_id, 
                        f"🎊 **¡NUEVO REFERIDO!**\n{user.first_name} se ha unido. +{EmpireConfig.REWARDS['REFERRAL']} puntos."
                    )
                except: pass
            db.save()

    await update.message.reply_text(
        db.data["system"]["welcome_text"].format(name=user.first_name),
        reply_markup=EmpireUI.main_keyboard(user.id),
        parse_mode="Markdown"
    )

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    u_data = db.sync_user(user)
    state = context.user_data.get("state")

    if u_data.get("is_banned"):
        return await update.message.reply_text("🚫 Tu acceso al Imperio ha sido revocado.")

    # --- BOTONES DEL MENÚ ---
    if text == "📥 DESCARGAR":
        await update.message.reply_text("🔗 **ENVÍA EL ENLACE DEL CONTENIDO:**")
        context.user_data["state"] = "AWAIT_URL"

    elif text == "👤 MI PERFIL":
        plan = EmpireConfig.PLANS[u_data["plan"]]
        msg = (
            f"👤 **EXPEDIENTE IMPERIAL**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: `{user.id}`\n"
            f"🎭 Rango: **{plan['name']}**\n"
            f"💰 Puntos: `{u_data['points']}`\n"
            f"📥 Hoy: `{u_data['daily_dls'][0]}/{plan['limit_daily']}`\n"
            f"👥 Referidos: `{u_data['referrals']}`\n"
            f"📅 Unido: `{u_data['joined']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🎁 RECOMPENSA":
        today = str(datetime.date.today())
        if u_data.get("last_daily") == today:
            await update.message.reply_text("❌ Ya reclamaste tu recompensa. Vuelve en 24 horas.")
        else:
            u_data["last_daily"] = today
            u_data["points"] += EmpireConfig.REWARDS["DAILY"]
            db.save()
            await update.message.reply_text(f"✅ ¡Se han acreditado **{EmpireConfig.REWARDS['DAILY']} puntos**!")

    elif text == "💎 TIENDA VIP":
        msg = "💎 **SISTEMA DE PLANES DEL IMPERIO**\n\n"
        for pid, p in EmpireConfig.PLANS.items():
            msg += f"🔹 **{p['name']}**\n   • Límite: {p['limit_daily']} dls/día\n   • Calidades: {', '.join(p['resolutions'])}\n   • Velocidad: {p['speed']}\n\n"
        msg += "👉 Contacta con @Ishak para subir de rango."
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "👥 REFERIDOS":
        me = await context.bot.get_me()
        link = f"https://t.me/{me.username}?start={user.id}"
        await update.message.reply_text(
            f"👥 **SISTEMA DE AFILIACIÓN**\n\nGana {EmpireConfig.REWARDS['REFERRAL']} puntos por cada persona.\n\n🔗 Tu link:\n`{link}`",
            parse_mode="Markdown"
        )

    elif text == "📊 ESTADÍSTICAS":
        s = db.data["stats"]
        up = str(datetime.datetime.now() - datetime.datetime.fromisoformat(s["boot_time"])).split('.')[0]
        msg = (
            f"📊 **ESTADO DEL IMPERIO**\n\n"
            f"👥 Usuarios: `{s['total_users']}`\n"
            f"📥 Descargas: `{s['total_downloads']}`\n"
            f"⏱ Uptime: `{up}`\n"
            f"🚀 Versión: `{EmpireConfig.VERSION}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "👑 PANEL OVERLORD 👑" and user.id == EmpireConfig.ADMIN_ID:
        await update.message.reply_text("🛠 **CENTRO DE MANDO OVERLORD**", reply_markup=EmpireUI.overlord_panel())

    # --- LÓGICA DE ESTADOS DE ENTRADA ---
    elif state == "AWAIT_URL":
        if "http" in text:
            context.user_data["active_url"] = text
            await update.message.reply_text("⚙️ **Analizando...** Elige formato:", reply_markup=EmpireUI.format_picker())
        else: await update.message.reply_text("❌ Enlace no detectado.")
        context.user_data["state"] = None

    elif state == "ADM_BC" and user.id == EmpireConfig.ADMIN_ID:
        count = 0
        for sid in db.data["users"]:
            try:
                await context.bot.send_message(sid, f"📢 **COMUNICADO DEL IMPERIO:**\n\n{text}", parse_mode="Markdown")
                count += 1
                await asyncio.sleep(0.05)
            except: pass
        await update.message.reply_text(f"✅ Difusión finalizada: {count} usuarios.")
        context.user_data["state"] = None

    elif state == "ADM_BAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = True
            db.save()
            await update.message.reply_text(f"🚫 Usuario {text} bloqueado del sistema.")
        else: await update.message.reply_text("❌ ID no encontrado.")
        context.user_data["state"] = None

    elif state == "ADM_UNBAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = False
            db.save()
            await update.message.reply_text(f"🔓 Usuario {text} desbloqueado.")
        else: await update.message.reply_text("❌ ID no encontrado.")
        context.user_data["state"] = None

    elif state == "ADM_PTS" and user.id == EmpireConfig.ADMIN_ID:
        try:
            tid, pts = text.split(":")
            if tid in db.data["users"]:
                db.data["users"][tid]["points"] += int(pts)
                db.save()
                await update.message.reply_text(f"💰 Se añadieron {pts} puntos a {tid}.")
            else: await update.message.reply_text("❌ ID inexistente.")
        except: await update.message.reply_text("❌ Formato: `ID:PUNTOS`")
        context.user_data["state"] = None

    elif state == "ADM_CP" and user.id == EmpireConfig.ADMIN_ID:
        try:
            code, plan = text.upper().split(":")
            db.data["coupons"][code] = plan
            db.save()
            await update.message.reply_text(f"🎫 Cupón `{code}` creado para plan `{plan}`.")
        except: await update.message.reply_text("❌ Formato: `CODIGO:PLAN` (Ej: VIP:ULTRA)")
        context.user_data["state"] = None

    elif state == "AWAIT_COUPON":
        code = text.upper()
        if code in db.data["coupons"]:
            plan = db.data["coupons"].pop(code)
            u_data["plan"] = plan
            db.save()
            await update.message.reply_text(f"✅ **CUPÓN ACTIVADO.** Tu nuevo plan es: **{plan}**")
        else: await update.message.reply_text("❌ Cupón inválido o expirado.")
        context.user_data["state"] = None

# =================================================================
# [7] MANEJO DE CALLBACKS (ACCIONES DE BOTONES)
# =================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    data = q.data
    await q.answer()

    u_data = db.sync_user(q.from_user)

    # ACCIONES DE DESCARGA
    if data.startswith("f_"):
        fmt = data.split("_")[1]
        if fmt == "back": return await q.edit_message_text("🎬 Selecciona formato:", reply_markup=EmpireUI.format_picker())
        
        context.user_data["active_fmt"] = fmt
        if fmt == "MP3":
            await finalize_download_flow(update, context)
        else:
            await q.edit_message_text("🎥 Selecciona calidad:", reply_markup=EmpireUI.quality_picker(u_data["plan"]))

    elif data.startswith("q_"):
        context.user_data["active_quality"] = data.split("_")[1]
        await finalize_download_flow(update, context)

    # ACCIONES DE ADMINISTRACIÓN
    elif data.startswith("adm_") and uid == EmpireConfig.ADMIN_ID:
        if data == "adm_list":
            users = db.data["users"]
            msg = "👥 **LISTA DE CIUDADANOS:**\n"
            for sid, d in list(users.items())[-20:]:
                status = "🚫" if d["is_banned"] else "✅"
                msg += f"• `{sid}` | {d['name']} | {d['plan']} | {status}\n"
            await q.message.reply_text(msg, parse_mode="Markdown")

        elif data == "adm_bc":
            await q.message.reply_text("📢 Escribe el mensaje para el Broadcast:"); context.user_data["state"] = "ADM_BC"

        elif data == "adm_ban":
            await q.message.reply_text("🚫 Envía el ID del usuario a bloquear:"); context.user_data["state"] = "ADM_BAN"

        elif data == "adm_unban":
            await q.message.reply_text("🔓 Envía el ID del usuario a desbloquear:"); context.user_data["state"] = "ADM_UNBAN"

        elif data == "adm_pts":
            await q.message.reply_text("💰 Envía `ID:PUNTOS` para sumar:"); context.user_data["state"] = "ADM_PTS"

        elif data == "adm_cp":
            await q.message.reply_text("🎫 Envía `CÓDIGO:PLAN`:"); context.user_data["state"] = "ADM_CP"

        elif data == "adm_backup":
            db.save()
            await context.bot.send_document(uid, open(EmpireConfig.DATABASE_PATH, 'rb'), caption="💾 Backup DB V60")

        elif data == "adm_logs":
            log_p = os.path.join(EmpireConfig.LOGS_DIR, "empire_core.log")
            if os.path.exists(log_p): await context.bot.send_document(uid, open(log_p, 'rb'), caption="📜 Logs Sistema")

        elif data == "adm_clean":
            count = 0
            for f in os.listdir(EmpireConfig.BUFFER_DIR):
                try: os.remove(os.path.join(EmpireConfig.BUFFER_DIR, f)); count += 1
                except: pass
            await q.message.reply_text(f"🧹 Se han purgado {count} archivos del buffer.")

        elif data == "adm_sys":
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            msg = (
                f"🖥 **TELEMETRÍA**\n"
                f"🚀 CPU: `{psutil.cpu_percent()}%`\n"
                f"📟 RAM: `{mem.percent}%` ({mem.used//1024**2}MB)\n"
                f"💾 DISCO: `{disk.percent}%` ({disk.free//1024**3}GB libres)\n"
                f"🐍 Python: `{platform.python_version()}`"
            )
            await q.message.reply_text(msg, parse_mode="Markdown")

        elif data == "adm_reboot":
            await q.message.reply_text("🔄 Reiniciando motor principal...")
            os.execl(sys.executable, sys.executable, *sys.argv)

    elif data == "u_close":
        await q.message.delete()

# --- PROCESO FINAL DE DESCARGA ---
async def finalize_download_flow(update, context):
    q = update.callback_query
    uid = q.from_user.id
    url = context.user_data.get("active_url")
    fmt = context.user_data.get("active_fmt")
    qlty = context.user_data.get("active_quality", "720p")
    u_data = db.sync_user(q.from_user)

    # Verificación de Límites del Plan
    limit = EmpireConfig.PLANS[u_data["plan"]]["limit_daily"]
    if u_data["daily_dls"][0] >= limit:
        return await q.edit_message_text(f"❌ Has alcanzado el límite de tu plan ({limit}). Sube a PRO o ULTRA.")

    m = await q.edit_message_text(f"⚡ **GENERANDO TÚNEL DE DATOS...**\n`[{fmt} | {qlty}]`")
    
    try:
        path, title, duration = await DownloadProcessor.start(url, fmt, qlty, str(uid))
        
        await m.edit_text("📤 **SUBIENDO AL SATÉLITE...**")
        
        with open(path, 'rb') as f:
            cap = f"✅ **{title}**\n\n⏱ Duración: `{str(datetime.timedelta(seconds=duration))}`\n⚡ Motor: `Ishak Empire-V60`"
            if fmt == "MP3": await context.bot.send_audio(uid, f, caption=cap, parse_mode="Markdown")
            else: await context.bot.send_video(uid, f, caption=cap, parse_mode="Markdown")

        u_data["daily_dls"][0] += 1
        u_data["total_dls"] += 1
        db.data["stats"]["total_downloads"] += 1
        db.save()
        
        if os.path.exists(path): os.remove(path)
        await m.delete()

    except Exception as e:
        logger.error(f"Download error: {traceback.format_exc()}")
        await m.edit_text(f"❌ **ERROR DE SISTEMA:**\n`{str(e)[:150]}`")

# =================================================================
# [8] SERVIDOR WEB DE ESTADO (FLASK)
# =================================================================
web_app = Flask(__name__)

@web_app.route('/')
def index():
    return jsonify({
        "empire": "ISHAK HYPER-SAAS",
        "status": "OPERATIONAL",
        "version": EmpireConfig.VERSION,
        "metrics": {
            "users": len(db.data["users"]),
            "dls": db.data["stats"]["total_downloads"]
        }
    })

def run_web():
    try: web_app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
    except: pass

# =================================================================
# [9] LANZAMIENTO MAESTRO
# =================================================================
def main():
    print(f"🚀 INICIANDO ISHAK EMPIRE V{EmpireConfig.VERSION}")
    threading.Thread(target=run_web, daemon=True).start()
    
    app = ApplicationBuilder().token(EmpireConfig.TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print("🔥 Overlord activo. Esperando órdenes.")
    app.run_polling()

if __name__ == '__main__':
    main()
