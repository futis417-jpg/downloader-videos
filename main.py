"""
SISTEMA: ISHAK HYPER-SAAS V75.0 - THE SINGULARITY EDITION
ESTADO: SUPREME CONTROL - GOD MODE ENFORCED
PROPIETARIO: Ishak Ezzahouani (ID: 8398522835)
PAÍS: España (Control Central de Datos)
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
# [0] INICIALIZACIÓN DE DEPENDENCIAS Y BLINDAJE DE ENTORNOS
# =================================================================
def bootstrap_packages():
    """Garantiza que el arsenal de librerías esté listo para el despliegue."""
    packages = ['python-telegram-bot', 'yt-dlp', 'flask', 'requests', 'psutil', 'Pillow']
    for p in packages:
        try:
            __import__(p.replace('-', '_'))
        except ImportError:
            print(f"📦 Instalando componente: {p}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])
    
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
# [1] ARQUITECTURA DE CONFIGURACIÓN (CENTRO DE DATOS)
# =================================================================
class EmpireConfig:
    ADMIN_ID = 8398522835
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    VERSION = "75.10.2-SINGULARITY"
    
    # Rutas de Infraestructura
    ROOT = os.getcwd()
    VAULT_DIR = os.path.join(ROOT, "empire_vault")
    BUFFER_DIR = os.path.join(ROOT, "download_buffer")
    LOGS_DIR = os.path.join(ROOT, "system_logs")
    DATABASE_PATH = os.path.join(VAULT_DIR, "empire_master_v75.json")
    
    # Estructura de Planes y Limitaciones
    PLANS = {
        "FREE": {
            "name": "🆓 CIUDADANO (FREE)",
            "limit_daily": 5,
            "max_file_mb": 150,
            "resolutions": ["360p", "720p"],
            "speed": "Standard (2MB/s)"
        },
        "PRO": {
            "name": "💎 ELITE (PRO)",
            "limit_daily": 150,
            "max_file_mb": 1500,
            "resolutions": ["360p", "720p", "1080p"],
            "speed": "High-Speed (25MB/s)"
        },
        "ULTRA": {
            "name": "🔥 SOBERANO (ULTRA)",
            "limit_daily": 999999,
            "max_file_mb": 10000,
            "resolutions": ["360p", "720p", "1080p", "1440p", "4K", "8K"],
            "speed": "Instántanea (Sin límites)"
        }
    }

    # Economía Imperial
    ECONOMY = {
        "DAILY_REWARD": 150,
        "REF_REWARD": 750,
        "PRICE_PRO_DAY": 1000,   # 1000 pts = 1 día PRO
        "PRICE_ULTRA_DAY": 2500, # 2500 pts = 1 día ULTRA
    }

    @classmethod
    def init_filesystem(cls):
        """Prepara el entorno de almacenamiento."""
        for d in [cls.VAULT_DIR, cls.BUFFER_DIR, cls.LOGS_DIR]:
            os.makedirs(d, exist_ok=True)
        # Limpieza inicial de archivos temporales
        for f in os.listdir(cls.BUFFER_DIR):
            try: os.remove(os.path.join(cls.BUFFER_DIR, f))
            except: pass

EmpireConfig.init_filesystem()

# =================================================================
# [2] SISTEMA DE LOGS Y AUDITORÍA
# =================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(EmpireConfig.LOGS_DIR, "empire_audit.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ISHAK_OVERLORD")

# =================================================================
# [3] BASE DE DATOS DE ALTA DISPONIBILIDAD (PERSISTENCIA TOTAL)
# =================================================================
class EmpireDatabase:
    """Motor de base de datos JSON con protección de hilos y caché."""
    def __init__(self):
        self._lock = threading.Lock()
        self.data = {
            "users": {},
            "coupons": {},
            "blacklist": [],
            "transactions": [],
            "stats": {
                "total_downloads": 0,
                "total_users": 0,
                "revenue_sim": 0,
                "boot_time": str(datetime.datetime.now())
            },
            "system": {
                "maint_mode": False,
                "announcement": None,
                "global_welcome": "👑 **BIENVENIDO AL IMPERIO ISHAK V75**\nDominio absoluto sobre los medios digitales."
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
                    logger.error(f"Error cargando base de datos: {e}")

    def save(self):
        with self._lock:
            try:
                with open(EmpireConfig.DATABASE_PATH, 'w', encoding='utf-8') as f:
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
                "plan_expiry": None, # Para suscripciones temporales
                "points": 500,
                "total_downloads": 0,
                "daily_downloads": [0, str(datetime.date.today())],
                "referrals": 0,
                "referred_by": None,
                "joined": str(datetime.date.today()),
                "is_banned": False,
                "last_daily": None,
                "history": []
            }
            self.data["stats"]["total_users"] += 1
            self.save()
        
        # Sincronización de límites diarios
        u = self.data["users"][uid]
        today = str(datetime.date.today())
        if u["daily_downloads"][1] != today:
            u["daily_downloads"] = [0, today]
            self.save()
            
        # Verificar expiración de plan
        if u["plan_expiry"]:
            expiry = datetime.datetime.fromisoformat(u["plan_expiry"])
            if datetime.datetime.now() > expiry:
                u["plan"] = "FREE"
                u["plan_expiry"] = None
                self.save()
                
        return u

    def log_transaction(self, uid, amount, description):
        self.data["transactions"].append({
            "uid": uid,
            "amount": amount,
            "desc": description,
            "date": str(datetime.datetime.now())
        })
        self.save()

db = EmpireDatabase()

# =================================================================
# [4] MOTOR DE DESCARGA "ISHAK-EMPIRE-X" (ULTRA SPEED)
# =================================================================
class MediaEngine:
    """Núcleo de procesamiento de video, audio y metadatos."""
    
    @staticmethod
    async def get_info(url: str):
        opts = {'quiet': True, 'no_warnings': True, 'noplaylist': True}
        def _get():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        try:
            return await asyncio.to_thread(_get)
        except Exception as e:
            logger.error(f"Error extrayendo info: {e}")
            return None

    @staticmethod
    async def run(url: str, mode: str, quality: str, uid: str):
        """Descarga el medio y lo guarda en el buffer imperial."""
        job_id = f"ishak_{uid}_{uuid.uuid4().hex[:10]}"
        output_template = os.path.join(EmpireConfig.BUFFER_DIR, f"{job_id}.%(ext)s")
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'max_filesize': 5000 * 1024 * 1024, # 5GB máximo
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

        def _execute():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if mode == "MP3":
                    file_path = os.path.splitext(file_path)[0] + ".mp3"
                return file_path, info.get('title', 'Media_Ishak'), info.get('duration', 0)

        return await asyncio.to_thread(_execute)

# =================================================================
# [5] DISEÑADOR DE INTERFACES (MATERIAL EMPIRE)
# =================================================================
class EmpireUI:
    """Generador de teclados y menús dinámicos."""
    
    @staticmethod
    def main_keyboard(uid):
        user = db.data["users"].get(str(uid), {})
        is_admin = uid == EmpireConfig.ADMIN_ID
        
        btns = [
            [KeyboardButton("📥 DESCARGAR"), KeyboardButton("👤 MI PERFIL")],
            [KeyboardButton("💎 MERCADO VIP"), KeyboardButton("🎁 RECOMPENSA")],
            [KeyboardButton("👥 REFERIDOS"), KeyboardButton("🎟️ CANJEAR CÓDIGO")],
            [KeyboardButton("📊 ESTADÍSTICAS"), KeyboardButton("🤝 SOPORTE")]
        ]
        if is_admin:
            btns.append([KeyboardButton("👑 PANEL OVERLORD 👑")])
        return ReplyKeyboardMarkup(btns, resize_keyboard=True)

    @staticmethod
    def overlord_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 LISTA CIUDADANOS", callback_data="adm_list"), 
             InlineKeyboardButton("📢 BROADCAST GLOBAL", callback_data="adm_bc")],
            [InlineKeyboardButton("🚫 BANEAR USER", callback_data="adm_ban"), 
             InlineKeyboardButton("🔓 DESBANEAR USER", callback_data="adm_unban")],
            [InlineKeyboardButton("💰 SUMAR PUNTOS", callback_data="adm_pts"), 
             InlineKeyboardButton("🎫 CREAR CUPÓN", callback_data="adm_cp")],
            [InlineKeyboardButton("🎭 EDITAR PLAN", callback_data="adm_edit_plan"), 
             InlineKeyboardButton("📂 ARCHIVOS", callback_data="adm_files")],
            [InlineKeyboardButton("💾 BACKUP DB", callback_data="adm_backup"), 
             InlineKeyboardButton("🧹 LIMPIAR CACHÉ", callback_data="adm_clean")],
            [InlineKeyboardButton("⚙️ TELEMETRÍA", callback_data="adm_sys"), 
             InlineKeyboardButton("🔄 REINICIAR", callback_data="adm_reboot")],
            [InlineKeyboardButton("❌ CERRAR PANEL", callback_data="u_close")]
        ])

    @staticmethod
    def market_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💎 1 DÍA PRO ({EmpireConfig.ECONOMY['PRICE_PRO_DAY']} pts)", callback_data="buy_PRO_1")],
            [InlineKeyboardButton(f"🔥 1 DÍA ULTRA ({EmpireConfig.ECONOMY['PRICE_ULTRA_DAY']} pts)", callback_data="buy_ULTRA_1")],
            [InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")]
        ])

    @staticmethod
    def format_selector():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 VIDEO (MP4)", callback_data="fmt_MP4"),
             InlineKeyboardButton("🎵 AUDIO (MP3)", callback_data="fmt_MP3")],
            [InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")]
        ])

    @staticmethod
    def quality_selector(plan_id):
        qualities = EmpireConfig.PLANS.get(plan_id, EmpireConfig.PLANS["FREE"])["resolutions"]
        rows = []
        for q in qualities:
            rows.append([InlineKeyboardButton(f"🎥 {q}", callback_data=f"ql_{q}")])
        rows.append([InlineKeyboardButton("⬅️ VOLVER AL FORMATO", callback_data="fmt_back")])
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def plan_selector_admin():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🆓 FREE", callback_data="setplan_FREE"),
             InlineKeyboardButton("💎 PRO", callback_data="setplan_PRO")],
            [InlineKeyboardButton("🔥 ULTRA", callback_data="setplan_ULTRA")],
            [InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")]
        ])

# =================================================================
# [6] CONTROLADORES DE COMANDOS Y LÓGICA DE USUARIO
# =================================================================
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    u_data = db.get_user(user)
    
    # Manejo de Referidos
    if context.args and context.args[0].isdigit():
        ref_id = context.args[0]
        if ref_id != str(user.id) and not u_data.get("referred_by"):
            u_data["referred_by"] = ref_id
            if ref_id in db.data["users"]:
                db.data["users"][ref_id]["points"] += EmpireConfig.ECONOMY["REF_REWARD"]
                db.data["users"][ref_id]["referrals"] += 1
                db.log_transaction(ref_id, EmpireConfig.ECONOMY["REF_REWARD"], f"Referido: {user.first_name}")
                try:
                    await context.bot.send_message(
                        ref_id, 
                        f"🎊 **¡NUEVO CIUDADANO!**\n{user.first_name} se ha unido bajo tu link. +{EmpireConfig.ECONOMY['REF_REWARD']} puntos."
                    )
                except: pass
            db.save()

    await update.message.reply_text(
        db.data["system"]["global_welcome"].format(name=user.first_name),
        reply_markup=EmpireUI.main_keyboard(user.id),
        parse_mode="Markdown"
    )

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    u_data = db.get_user(user)
    state = context.user_data.get("state")

    if u_data.get("is_banned"):
        return await update.message.reply_text("🚫 Tu acceso al Imperio ha sido revocado. Contacta con soporte.")

    # [1] RUTAS DEL MENÚ PRINCIPAL
    if text == "📥 DESCARGAR":
        await update.message.reply_text("🔗 **ENVÍA EL ENLACE DEL CONTENIDO:**")
        context.user_data["state"] = "WAIT_URL"

    elif text == "👤 MI PERFIL":
        plan = EmpireConfig.PLANS[u_data["plan"]]
        expiry = f"\n⏳ Expira: `{u_data['plan_expiry']}`" if u_data['plan_expiry'] else ""
        msg = (
            f"👤 **EXPEDIENTE IMPERIAL**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 ID: `{user.id}`\n"
            f"🎭 Rango: **{plan['name']}**{expiry}\n"
            f"💰 Puntos: `{u_data['points']}`\n"
            f"📥 Hoy: `{u_data['daily_downloads'][0]}/{plan['limit_daily']}`\n"
            f"👥 Referidos: `{u_data['referrals']}`\n"
            f"📅 Unido: `{u_data['joined']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🎁 RECOMPENSA":
        today = str(datetime.date.today())
        if u_data.get("last_daily") == today:
            await update.message.reply_text("❌ Ya has reclamado tu recompensa hoy. El sistema se reinicia a medianoche.")
        else:
            u_data["last_daily"] = today
            u_data["points"] += EmpireConfig.ECONOMY["DAILY_REWARD"]
            db.log_transaction(user.id, EmpireConfig.ECONOMY["DAILY_REWARD"], "Recompensa diaria")
            await update.message.reply_text(f"✅ ¡Has reclamado **{EmpireConfig.ECONOMY['DAILY_REWARD']} puntos**!")

    elif text == "💎 MERCADO VIP":
        await update.message.reply_text(
            "💎 **BIENVENIDO AL MERCADO DE PUNTOS**\n\nAquí puedes canjear tus puntos por días de suscripción PRO o ULTRA.",
            reply_markup=EmpireUI.market_panel()
        )

    elif text == "🎟️ CANJEAR CÓDIGO":
        await update.message.reply_text("🎟️ **Escribe el código del cupón:**")
        context.user_data["state"] = "WAIT_COUPON"

    elif text == "👥 REFERIDOS":
        me = await context.bot.get_me()
        link = f"https://t.me/{me.username}?start={user.id}"
        await update.message.reply_text(
            f"👥 **PROGRAMA DE AFILIADOS**\n\nGana {EmpireConfig.ECONOMY['REF_REWARD']} puntos por cada nuevo miembro.\n\n🔗 Tu link Imperial:\n`{link}`",
            parse_mode="Markdown"
        )

    elif text == "📊 ESTADÍSTICAS":
        s = db.data["stats"]
        up = str(datetime.datetime.now() - datetime.datetime.fromisoformat(s["boot_time"])).split('.')[0]
        msg = (
            f"📊 **ESTADO DEL IMPERIO**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Ciudadanos: `{s['total_users']}`\n"
            f"📥 Descargas: `{s['total_downloads']}`\n"
            f"⏱ Uptime: `{up}`\n"
            f"🚀 Versión: `{EmpireConfig.VERSION}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "👑 PANEL OVERLORD 👑" and user.id == EmpireConfig.ADMIN_ID:
        await update.message.reply_text("🛠 **CENTRO DE COMANDO OVERLORD**", reply_markup=EmpireUI.overlord_panel())

    # [2] MANEJO DE ESTADOS (FSM)
    elif state == "WAIT_URL":
        if "http" in text:
            context.user_data["active_url"] = text
            await update.message.reply_text("🛠 **Medio detectado.** Elige el formato:", reply_markup=EmpireUI.format_selector())
        else:
            await update.message.reply_text("❌ URL no detectada. Envía un enlace válido.")
        context.user_data["state"] = None

    elif state == "WAIT_COUPON":
        code = text.upper()
        if code in db.data["coupons"]:
            plan = db.data["coupons"].pop(code)
            u_data["plan"] = plan
            # Dar 30 días si es por cupón
            expiry = datetime.datetime.now() + datetime.timedelta(days=30)
            u_data["plan_expiry"] = str(expiry)
            db.save()
            await update.message.reply_text(f"✅ **¡CUPÓN ACTIVADO!** Tu plan ahora es **{plan}** por 30 días.")
        else:
            await update.message.reply_text("❌ Cupón inválido, expirado o ya reclamado.")
        context.user_data["state"] = None

    # [3] ESTADOS DE ADMINISTRADOR
    elif state == "WAIT_BC" and user.id == EmpireConfig.ADMIN_ID:
        count = 0
        for sid in db.data["users"]:
            try:
                await context.bot.send_message(sid, f"📢 **COMUNICADO IMPERIAL:**\n\n{text}", parse_mode="Markdown")
                count += 1
                await asyncio.sleep(0.05)
            except: pass
        await update.message.reply_text(f"✅ Mensaje enviado a {count} ciudadanos.")
        context.user_data["state"] = None

    elif state == "WAIT_BAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = True
            db.save()
            await update.message.reply_text(f"🚫 Ciudadano `{text}` bloqueado.")
        else: await update.message.reply_text("❌ ID no encontrado.")
        context.user_data["state"] = None

    elif state == "WAIT_UNBAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = False
            db.save()
            await update.message.reply_text(f"🔓 Ciudadano `{text}` rehabilitado.")
        else: await update.message.reply_text("❌ ID no encontrado.")
        context.user_data["state"] = None

    elif state == "WAIT_PTS_ID" and user.id == EmpireConfig.ADMIN_ID:
        context.user_data["target_id"] = text
        await update.message.reply_text(f"💰 ¿Cuántos puntos añadir a `{text}`?")
        context.user_data["state"] = "WAIT_PTS_VAL"

    elif state == "WAIT_PTS_VAL" and user.id == EmpireConfig.ADMIN_ID:
        try:
            val = int(text)
            tid = context.user_data["target_id"]
            if tid in db.data["users"]:
                db.data["users"][tid]["points"] += val
                db.log_transaction(tid, val, "Admin Gift")
                await update.message.reply_text(f"✅ Se han añadido {val} puntos a `{tid}`.")
            else: await update.message.reply_text("❌ El ID ya no existe.")
        except: await update.message.reply_text("❌ Valor inválido.")
        context.user_data["state"] = None

    elif state == "WAIT_CP_CODE" and user.id == EmpireConfig.ADMIN_ID:
        context.user_data["cp_code"] = text.upper()
        await update.message.reply_text("🎫 ¿Para qué plan? (FREE, PRO, ULTRA)")
        context.user_data["state"] = "WAIT_CP_PLAN"

    elif state == "WAIT_CP_PLAN" and user.id == EmpireConfig.ADMIN_ID:
        plan = text.upper()
        if plan in EmpireConfig.PLANS:
            code = context.user_data["cp_code"]
            db.data["coupons"][code] = plan
            db.save()
            await update.message.reply_text(f"🎫 Cupón `{code}` creado para plan `{plan}`.")
        else: await update.message.reply_text("❌ Plan no válido.")
        context.user_data["state"] = None

    elif state == "WAIT_PLAN_EDIT_ID" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            context.user_data["target_user_id"] = text
            await update.message.reply_text(f"🎭 Selecciona el nuevo rango para `{text}`:", reply_markup=EmpireUI.plan_selector_admin())
        else: await update.message.reply_text("❌ Usuario no encontrado.")
        context.user_data["state"] = None

# =================================================================
# [7] MANEJO DE CALLBACKS (LÓGICA DE BOTONES INTERACTIVOS)
# =================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    data = q.data
    await q.answer()

    u_data = db.get_user(q.from_user)

    # --- LÓGICA DE MERCADO (CANJEAR PUNTOS) ---
    if data.startswith("buy_"):
        _, plan, days = data.split("_")
        price = EmpireConfig.ECONOMY[f"PRICE_{plan}_DAY"]
        if u_data["points"] >= price:
            u_data["points"] -= price
            u_data["plan"] = plan
            current_expiry = u_data["plan_expiry"]
            base_date = datetime.datetime.fromisoformat(current_expiry) if current_expiry else datetime.datetime.now()
            new_expiry = base_date + datetime.timedelta(days=int(days))
            u_data["plan_expiry"] = str(new_expiry)
            db.log_transaction(uid, -price, f"Compra {plan} x{days}d")
            await q.edit_message_text(f"✅ **¡COMPRA EXITOSA!** Tu plan **{plan}** ha sido activado hasta `{new_expiry.date()}`.")
        else:
            await q.message.reply_text(f"❌ Puntos insuficientes. Necesitas {price} pts.")

    # --- LÓGICA DE DESCARGA ---
    elif data.startswith("fmt_"):
        mode = data.split("_")[1]
        if mode == "back": return await q.edit_message_text("🎬 Elige formato:", reply_markup=EmpireUI.format_selector())
        context.user_data["active_fmt"] = mode
        if mode == "MP3": await finalize_download(update, context)
        else: await q.edit_message_text("🎥 Selecciona calidad de video:", reply_markup=EmpireUI.quality_selector(u_data["plan"]))

    elif data.startswith("ql_"):
        context.user_data["active_qlty"] = data.split("_")[1]
        await finalize_download(update, context)

    # --- LÓGICA OVERLORD (ADMIN) ---
    elif data.startswith("adm_") and uid == EmpireConfig.ADMIN_ID:
        if data == "adm_list":
            users = db.data["users"]
            msg = "👥 **POBLACIÓN DEL IMPERIO:**\n"
            for sid, d in list(users.items())[-20:]:
                status = "🚫" if d["is_banned"] else "✅"
                msg += f"• `{sid}` | {d['name']} | {d['plan']} | {status}\n"
            await q.message.reply_text(msg, parse_mode="Markdown")

        elif data == "adm_bc":
            await q.message.reply_text("📢 Escribe el mensaje para el Broadcast:"); context.user_data["state"] = "WAIT_BC"

        elif data == "adm_ban":
            await q.message.reply_text("🚫 Envía el ID a bloquear:"); context.user_data["state"] = "WAIT_BAN"

        elif data == "adm_unban":
            await q.message.reply_text("🔓 Envía el ID a rehabilitar:"); context.user_data["state"] = "WAIT_UNBAN"

        elif data == "adm_pts":
            await q.message.reply_text("💰 Envía el ID a beneficiar:"); context.user_data["state"] = "WAIT_PTS_ID"

        elif data == "adm_cp":
            await q.message.reply_text("🎫 Escribe el CÓDIGO deseado:"); context.user_data["state"] = "WAIT_CP_CODE"

        elif data == "adm_edit_plan":
            await q.message.reply_text("🎭 Envía el ID del usuario a modificar:"); context.user_data["state"] = "WAIT_PLAN_EDIT_ID"

        elif data == "adm_backup":
            db.save()
            await context.bot.send_document(uid, open(EmpireConfig.DATABASE_PATH, 'rb'), caption=f"💾 Master Vault Backup - {datetime.datetime.now()}")

        elif data == "adm_logs":
            lp = os.path.join(EmpireConfig.LOGS_DIR, "empire_audit.log")
            if os.path.exists(lp): await context.bot.send_document(uid, open(lp, 'rb'), caption="📜 Auditoría de Sistema")

        elif data == "adm_clean":
            count = 0
            for f in os.listdir(EmpireConfig.BUFFER_DIR):
                try: os.remove(os.path.join(EmpireConfig.BUFFER_DIR, f)); count += 1
                except: pass
            await q.message.reply_text(f"🧹 Purgados {count} archivos del buffer.")

        elif data == "adm_sys":
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            msg = (
                f"🖥 **TELEMETRÍA IMPERIAL**\n"
                f"🚀 CPU: `{psutil.cpu_percent()}%` (Cores: {psutil.cpu_count()})\n"
                f"📟 RAM: `{mem.percent}%` ({mem.used//1024**2}MB)\n"
                f"💾 DISCO: `{disk.percent}%` ({disk.free//1024**3}GB libres)\n"
                f"🏗 OS: `{platform.system()} {platform.release()}`"
            )
            await q.message.reply_text(msg, parse_mode="Markdown")

        elif data == "adm_reboot":
            await q.message.reply_text("🔄 Reiniciando motor central..."); db.save()
            os.execl(sys.executable, sys.executable, *sys.argv)

    # --- SET PLAN CALLBACK ---
    elif data.startswith("setplan_") and uid == EmpireConfig.ADMIN_ID:
        plan = data.split("_")[1]
        tid = context.user_data.get("target_user_id")
        if tid in db.data["users"]:
            db.data["users"][tid]["plan"] = plan
            # Si el admin lo cambia, le damos 30 días o indefinido si es ULTRA
            u_data_target = db.data["users"][tid]
            expiry = datetime.datetime.now() + datetime.timedelta(days=365) if plan != "FREE" else None
            u_data_target["plan_expiry"] = str(expiry) if expiry else None
            db.save()
            await q.edit_message_text(f"✅ Rango de `{tid}` actualizado a **{plan}**.")
            try: await context.bot.send_message(tid, f"🎭 Tu plan ha sido actualizado a **{plan}** por un administrador.")
            except: pass
        context.user_data["target_user_id"] = None

    elif data == "u_close":
        await q.message.delete()

# --- PROCESO FINAL DE DESCARGA (ISHAK-FLOW) ---
async def finalize_download(update, context):
    q = update.callback_query
    uid = q.from_user.id
    url = context.user_data.get("active_url")
    fmt = context.user_data.get("active_fmt")
    qlty = context.user_data.get("active_qlty", "720p")
    u_data = db.get_user(q.from_user)

    # Verificación de Límites
    limit = EmpireConfig.PLANS[u_data["plan"]]["limit_daily"]
    if u_data["daily_downloads"][0] >= limit:
        return await q.edit_message_text(f"❌ Límite diario alcanzado ({limit}). Sube de rango en el Mercado.")

    msg = await q.edit_message_text(f"⚡ **GENERANDO TÚNEL DE DATOS...**\n`[{fmt} | {qlty}]`")
    
    try:
        path, title, duration = await MediaEngine.run(url, fmt, qlty, str(uid))
        
        await msg.edit_text("📤 **SUBIENDO AL SATÉLITE IMPERIAL...**")
        
        with open(path, 'rb') as f:
            cap = f"✅ **{title}**\n\n⏱ Duración: `{str(datetime.timedelta(seconds=duration))}`\n⚡ Motor: `Ishak Singularity V75`"
            if fmt == "MP3": await context.bot.send_audio(uid, f, caption=cap, parse_mode="Markdown")
            else: await context.bot.send_video(uid, f, caption=cap, parse_mode="Markdown")

        u_data["daily_downloads"][0] += 1
        u_data["total_downloads"] += 1
        db.data["stats"]["total_downloads"] += 1
        db.save()
        
        if os.path.exists(path): os.remove(path)
        await msg.delete()

    except Exception as e:
        logger.error(f"Error descarga: {traceback.format_exc()}")
        await msg.edit_text(f"❌ **ERROR DE SISTEMA:**\n`{str(e)[:150]}`")

# =================================================================
# [8] SERVIDOR WEB DE ESTADO (FLASK)
# =================================================================
web_app = Flask(__name__)

@web_app.route('/')
def status():
    return jsonify({
        "status": "OPERATIONAL",
        "empire": "ISHAK HYPER-SAAS",
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
# [9] LANZAMIENTO DEL IMPERIO
# =================================================================
def main():
    print(f"🚀 INICIANDO ISHAK EMPIRE V{EmpireConfig.VERSION}")
    threading.Thread(target=run_web, daemon=True).start()
    
    application = ApplicationBuilder().token(EmpireConfig.TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    print("🔥 Overlord operacional. Esperando comandos.")
    application.run_polling()

if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
