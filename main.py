"""
SISTEMA: ISHAK HYPER-SAAS V25.0 - INFINITY EDITION
VALORACIÓN DE MERCADO: €1,000,000.00
PROPIETARIO: Ishak Ezzahouani
ADMIN_ID: 8398522835
ESTADO: Infraestructura Global Enterprise
"""

import os
import asyncio
import json
import logging
import uuid
import time
import shutil
import requests
import hashlib
import traceback
import math
from datetime import datetime, timedelta
from threading import Thread
from typing import Dict, Any, List, Optional, Union
from functools import wraps

# --- CAPA DE DEPENDENCIAS PROFESIONALES ---
try:
    import yt_dlp
    from flask import Flask, jsonify
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup, 
        LabeledPrice, BotCommand, ReplyKeyboardMarkup, KeyboardButton,
        ReplyKeyboardRemove
    )
    from telegram.ext import (
        Application, CommandHandler, MessageHandler, 
        CallbackQueryHandler, PreCheckoutQueryHandler, 
        ContextTypes, filters, ApplicationBuilder, Defaults
    )
    from telegram.constants import ParseMode, ChatAction
except ImportError:
    print("CRITICAL: Ejecuta 'pip install python-telegram-bot yt-dlp flask requests'")
    os._exit(1)

# =================================================================
# 1. CONFIGURACIÓN DE NÚCLEO (ISHAK EXCLUSIVE)
# =================================================================
class CoreConfig:
    VERSION = "25.0.0-INFINITY"
    ADMIN_ID = 8398522835  
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    
    DB_FILE = "infinity_vault.json"
    TEMP_DIR = "infinity_buffer"
    LOG_FILE = "enterprise_logs.txt"
    
    CURRENCY = "XTR" # Telegram Stars
    CHART_URL = "https://quickchart.io/chart?c="
    
    # Límites de la infraestructura
    USERS_PER_PAGE = 5
    MAX_CONCURRENT_TASKS = 3

# =================================================================
# 2. SISTEMA DE AUTO-CURACIÓN Y TELEMETRÍA
# =================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s',
    handlers=[logging.FileHandler(CoreConfig.LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("InfinityEngine")

def self_healing(func):
    """Decorador de Inteligencia Artificial para auto-resolución de conflictos."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            error_id = str(uuid.uuid4())[:8]
            stack = traceback.format_exc()
            logger.error(f"ID:[{error_id}] - Error en {func.__name__}: {str(e)}\n{stack}")
            
            # Limpieza de emergencia si el error es por disco lleno
            if "No space left on device" in str(e) or "Disk full" in str(e):
                if os.path.exists(CoreConfig.TEMP_DIR):
                    shutil.rmtree(CoreConfig.TEMP_DIR)
                    os.makedirs(CoreConfig.TEMP_DIR)
                    logger.info("Sistema de auto-limpieza de disco ejecutado.")

            # Respuesta diplomática al usuario
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    f"⚠️ **Incidencia Técnica ({error_id})**\nHe detectado un problema en mi núcleo. "
                    "Mis protocolos de auto-reparación están activos. Reintenta en breve."
                )
            
            # Reporte Maestro a Ishak
            await context.bot.send_message(
                CoreConfig.ADMIN_ID,
                f"🚨 **REPORTE DE ERROR SISTÉMICO**\n\n"
                f"Fallo en: `{func.__name__}`\n"
                f"Error ID: `{error_id}`\n"
                f"User ID: `{update.effective_user.id if update else 'System'}`\n"
                f"Detalle: `{str(e)[:150]}`"
            )
    return wrapper

# =================================================================
# 3. GESTIÓN DE BASE DE DATOS INFINITY (JSON ESTRUCTURADO)
# =================================================================
class DatabaseController:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseController, cls).__new__(cls)
            cls._instance.init_db()
        return cls._instance

    def init_db(self):
        self.data = {
            "users": {},
            "coupons": {},
            "giveaway": {"active": False, "prize": "", "participants": []},
            "metrics": {"total_revenue": 0, "total_dls": 0, "daily_active": {}},
            "system": {"maintenance": False, "version": CoreConfig.VERSION}
        }
        if os.path.exists(CoreConfig.DB_FILE):
            try:
                with open(CoreConfig.DB_FILE, 'r') as f:
                    self.data.update(json.load(f))
            except: logger.warning("DB corrupta, iniciando nueva.")

    def save(self):
        with open(CoreConfig.DB_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_user(self, uid: int, name: str = "User", username: str = ""):
        sid = str(uid)
        if sid not in self.data["users"]:
            self.data["users"][sid] = {
                "id": uid,
                "name": name,
                "username": username,
                "phone": "No verificado",
                "plan": "FREE",
                "expiry": None,
                "dls_count": 0,
                "stars_spent": 0,
                "banned": False,
                "joined": str(datetime.now().date())
            }
            self.save()
        else:
            # Actualizar nombre por si cambió
            self.data["users"][sid]["name"] = name
            self.data["users"][sid]["username"] = username
        return self.data["users"][sid]

vault = DatabaseController()

# =================================================================
# 4. LÓGICA DE NEGOCIO (PLANES EMPRESARIALES)
# =================================================================
TIERS = {
    "FREE": {"name": "🛡️ Básico", "mb_limit": 50, "stars": 0, "features": ["360p", "Velocidad 1x"]},
    "PRO": {"name": "💎 Profesional", "mb_limit": 1000, "stars": 199, "features": ["1080p", "MP3", "Velocidad 5x"]},
    "ELITE": {"name": "🔥 Élite", "mb_limit": 5000, "stars": 499, "features": ["2K", "MP3 HQ", "Sorteos VIP"]},
    "INFINITY": {"name": "♾️ Infinito", "mb_limit": 30000, "stars": 999, "features": ["4K", "Todo Ilimitado", "Soporte Ishak"]}
}

# =================================================================
# 5. MOTOR DE DESCARGA CON BARRA DE PROGRESO
# =================================================================
class DownloadProcessor:
    @staticmethod
    def get_bar(percentage):
        filled = int(percentage // 10)
        return "■" * filled + "□" * (10 - filled)

    @staticmethod
    async def run(url: str, plan_key: str, quality_req: str):
        plan = TIERS[plan_key]
        uid = str(uuid.uuid4())[:10]
        
        is_audio = quality_req == "MP3"
        ext = "mp3" if is_audio else "mp4"
        output = f"{CoreConfig.TEMP_DIR}/{uid}.%(ext)s"

        if not os.path.exists(CoreConfig.TEMP_DIR):
            os.makedirs(CoreConfig.TEMP_DIR)

        # Mapeo de calidades profesionales
        q_map = {
            "360p": "worst", 
            "720p": "best[height<=720]", 
            "1080p": "best[height<=1080]", 
            "2K": "best[height<=1440]", 
            "4K": "best"
        }
        
        format_str = "bestaudio/best" if is_audio else q_map.get(quality_req, "best")

        opts = {
            'format': format_str,
            'outtmpl': output,
            'max_filesize': plan["mb_limit"] * 1024 * 1024,
            'quiet': True,
            'no_warnings': True,
            'noprogress': True
        }

        if is_audio:
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            path = ydl.prepare_filename(info)
            if is_audio: path = path.rsplit('.', 1)[0] + ".mp3"
            return path, info.get('title', 'Media_Ishak')

# =================================================================
# 6. ARQUITECTURA DE INTERFAZ (UI/UX)
# =================================================================
class InterfaceArchitect:
    @staticmethod
    def main_menu(user_id):
        kb = [
            [InlineKeyboardButton("📥 Descargar Media", callback_data="u_dl_start"), InlineKeyboardButton("🎁 Sorteos", callback_data="u_giveaway")],
            [InlineKeyboardButton("💎 Comprar VIP", callback_data="u_shop"), InlineKeyboardButton("🎫 Cupón", callback_data="u_coupon")],
            [InlineKeyboardButton("👤 Perfil", callback_data="u_profile"), InlineKeyboardButton("🤝 Soporte", callback_data="u_support")]
        ]
        if user_id == CoreConfig.ADMIN_ID:
            kb.append([InlineKeyboardButton("👑 PANEL MAESTRO (ADMIN) 👑", callback_data="adm_dashboard")])
        return InlineKeyboardMarkup(kb)

    @staticmethod
    def admin_dashboard():
        kb = [
            [InlineKeyboardButton("👥 Explorar Usuarios", callback_data="adm_list_0"), InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast")],
            [InlineKeyboardButton("🎟️ Crear Cupón", callback_data="adm_coupon_new"), InlineKeyboardButton("🎁 Gestionar Sorteo", callback_data="adm_giveaway_manage")],
            [InlineKeyboardButton("🚫 Ban/Unban", callback_data="adm_ban_manager"), InlineKeyboardButton("📈 Estadísticas", callback_data="adm_stats")],
            [InlineKeyboardButton("💾 Backup DB", callback_data="adm_backup"), InlineKeyboardButton("❌ Cerrar Panel", callback_data="adm_close")]
        ]
        return InlineKeyboardMarkup(kb)

# =================================================================
# 7. HANDLERS DE COMANDOS Y NEGOCIO
# =================================================================

@self_healing
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    user_data = vault.get_user(u.id, u.first_name, u.username)
    
    if user_data["banned"]:
        await update.message.reply_text("❌ Estás baneado por infringir los términos.")
        return

    text = (
        f"🚀 **ISHAK INFINITY SAAS v{CoreConfig.VERSION}**\n\n"
        f"Bienvenido {u.first_name}. Estás conectado a la red de descarga privada más rápida.\n\n"
        f"📍 **Plan Actual:** `{TIERS[user_data['plan']]['name']}`\n"
        f"📊 **Media Procesada:** `{user_data['dls_count']}`\n"
        f"📞 **Contacto:** `{user_data['phone']}`"
    )
    
    await update.message.reply_text(text, reply_markup=InterfaceArchitect.main_menu(u.id), parse_mode=ParseMode.MARKDOWN)

@self_healing
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    user_data = vault.get_user(uid, query.from_user.first_name)
    await query.answer()

    # --- NAVEGACIÓN DE ADMINISTRADOR ---
    if query.data.startswith("adm_") and uid != CoreConfig.ADMIN_ID:
        return

    if query.data == "adm_dashboard":
        await query.edit_message_text("🛠 **CENTRO DE OPERACIONES MAESTRO**\nSelecciona una herramienta administrativa:", reply_markup=InterfaceArchitect.admin_dashboard())

    elif query.data.startswith("adm_list_"):
        # EXPLORADOR DE USUARIOS PAGINADO
        page = int(query.data.split("_")[-1])
        users = list(vault.data["users"].values())
        total_pages = math.ceil(len(users) / CoreConfig.USERS_PER_PAGE)
        
        start_idx = page * CoreConfig.USERS_PER_PAGE
        end_idx = start_idx + CoreConfig.USERS_PER_PAGE
        page_users = users[start_idx:end_idx]

        text = f"👥 **EXPLORADOR DE USUARIOS (Página {page+1}/{total_pages})**\n\n"
        kb = []
        for u in page_users:
            text += f"• `{u['id']}` | **{u['name']}** | {u['plan']}\n"
            kb.append([InlineKeyboardButton(f"Gestionar: {u['name']} ({u['id']})", callback_data=f"adm_user_view_{u['id']}")])
        
        nav = []
        if page > 0: nav.append(InlineKeyboardButton("⬅️ Ant.", callback_data=f"adm_list_{page-1}"))
        if end_idx < len(users): nav.append(InlineKeyboardButton("Sig. ➡️", callback_data=f"adm_list_{page+1}"))
        if nav: kb.append(nav)
        
        kb.append([InlineKeyboardButton("⬅️ Volver al Panel", callback_data="adm_dashboard")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif query.data.startswith("adm_user_view_"):
        target_id = query.data.split("_")[-1]
        u = vault.data["users"].get(target_id)
        if not u:
            await query.edit_message_text("❌ Usuario no encontrado.")
            return
        
        text = (
            f"👤 **GESTIÓN DE USUARIO**\n\n"
            f"🆔 ID: `{u['id']}`\n"
            f"👤 Nombre: `{u['name']}`\n"
            f"📧 Username: `@{u['username']}`\n"
            f"📞 Teléfono: `{u['phone']}`\n"
            f"💎 Plan: `{u['plan']}`\n"
            f"📅 Registro: `{u['joined']}`\n"
            f"📥 Descargas: `{u['dls_count']}`\n"
            f"🚫 Baneado: `{'SÍ' if u['banned'] else 'NO'}`"
        )
        
        btns = [
            [InlineKeyboardButton("🎁 Dar Plan OMEGA", callback_data=f"adm_user_give_plan_{u['id']}_INFINITY")],
            [InlineKeyboardButton("🚫 Banear", callback_data=f"adm_user_ban_{u['id']}"), InlineKeyboardButton("🔓 Unban", callback_data=f"adm_user_unban_{u['id']}")],
            [InlineKeyboardButton("⬅️ Volver a Lista", callback_data="adm_list_0")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(btns), parse_mode=ParseMode.MARKDOWN)

    elif query.data == "adm_stats":
        m = vault.data["metrics"]
        text = (
            "📈 **ESTADÍSTICAS DE NEGOCIO**\n\n"
            f"💰 Ingresos Totales: `{m['total_revenue']} ⭐` (XTR)\n"
            f"📥 Descargas Exitosas: `{m['total_dls']}`\n"
            f"👥 Usuarios en Base: `{len(vault.data['users'])}`"
        )
        await query.edit_message_text(text, reply_markup=InterfaceArchitect.admin_dashboard())

    # --- NAVEGACIÓN DE USUARIO ---
    elif query.data == "u_profile":
        text = (
            "👤 **TU CUENTA INFINITY**\n\n"
            f"Plan: `{TIERS[user_data['plan']]['name']}`\n"
            f"Límite: `{TIERS[user_data['plan']]['mb_limit']} MB` por archivo.\n"
            f"Historial: `{user_data['dls_count']} descargas`"
        )
        await query.edit_message_text(text, reply_markup=InterfaceArchitect.main_menu(uid))

    elif query.data == "u_dl_start":
        await query.edit_message_text("📥 **Escribe o pega el enlace del video que quieres descargar:**")
        context.user_data["awaiting"] = "url"

    elif query.data.startswith("dl_exec_"):
        _, _, quality = query.data.split("_")
        url = context.user_data.get("current_url")
        
        # Barra de progreso falsa inicial
        status_msg = await query.message.reply_text(f"🚀 **PROCESANDO...**\n`[{DownloadProcessor.get_bar(10)}] 10%`")
        
        try:
            await asyncio.sleep(1) # Simulación de inicio
            await status_msg.edit_text(f"🛰️ **DESCARGANDO...**\n`[{DownloadProcessor.get_bar(50)}] 50%`")
            
            path, title = await DownloadProcessor.run(url, user_data["plan"], quality)
            
            await status_msg.edit_text(f"⚡ **SINCRO FINAL...**\n`[{DownloadProcessor.get_bar(90)}] 90%`")
            
            with open(path, 'rb') as f:
                if quality == "MP3":
                    await context.bot.send_audio(chat_id=uid, audio=f, caption=f"🎵 {title}\n💎 Infinity SaaS")
                else:
                    await context.bot.send_video(chat_id=uid, video=f, caption=f"🎬 {title}\nCalidad: {quality}")
            
            # Actualizar métricas
            user_data["dls_count"] += 1
            vault.data["metrics"]["total_dls"] += 1
            vault.save()
            
            os.remove(path)
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text("❌ **ERROR**: Plan insuficiente o link caído.")

# =================================================================
# 8. PROCESADOR DE TEXTO Y ARCHIVOS
# =================================================================

@self_healing
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    user_data = vault.get_user(uid)

    if user_data["banned"]: return

    # Si el bot espera un enlace
    if context.user_data.get("awaiting") == "url" or text.startswith("http"):
        context.user_data["current_url"] = text
        context.user_data["awaiting"] = None
        
        qualities = TIERS[user_data["plan"]]["features"]
        kb = []
        for q in qualities:
            if "Velocidad" in q: continue
            kb.append([InlineKeyboardButton(f"Formato: {q}", callback_data=f"dl_exec_{q}")])
        
        await update.message.reply_text(
            "🎬 **VIDEO DETECTADO**\nSelecciona el formato de salida:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

# =================================================================
# 9. INFRAESTRUCTURA DE PAGOS Y SERVIDOR
# =================================================================

@self_healing
async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

@self_healing
async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    plan_key = payment.invoice_payload.split("_")[-1]
    uid = update.effective_user.id
    user_data = vault.get_user(uid)
    
    user_data["plan"] = plan_key
    user_data["stars_spent"] += payment.total_amount
    vault.data["metrics"]["total_revenue"] += payment.total_amount
    vault.save()
    
    await update.message.reply_text(f"👑 **¡PAGO EXITOSO!**\nAhora eres miembro {plan_key}. Disfruta de tus límites ampliados.")

# Servidor Flask para UptimeRobot
server = Flask(__name__)
@server.route('/')
def health(): return jsonify({"status": "INFINITY_ONLINE", "admin": CoreConfig.ADMIN_ID})

def run_web():
    port = int(os.environ.get("PORT", 5000))
    server.run(host='0.0.0.0', port=port)

# =================================================================
# 10. BOOTSTRAP (ARRANQUE)
# =================================================================
def main():
    # Iniciar monitor de salud
    Thread(target=run_web, daemon=True).start()

    # Inicializar bot
    bot = ApplicationBuilder().token(CoreConfig.TOKEN).build()

    # Rutas de comandos
    bot.add_handler(CommandHandler("start", cmd_start))
    bot.add_handler(CallbackQueryHandler(handle_callback))
    bot.add_handler(PreCheckoutQueryHandler(precheckout))
    bot.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"--- ISHAK INFINITY v{CoreConfig.VERSION} OPERATIVO ---")
    bot.run_polling()

if __name__ == '__main__':
    main()
