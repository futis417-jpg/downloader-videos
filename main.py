"""
SISTEMA: ISHAK HYPER-SAAS V25.0 - INFINITY EDITION
ESTADO: ULTRA-OVERLORD / ENTERPRISE READY
PROPIETARIO: Ishak Ezzahouani (ID: 8398522835)
VALORACIÓN: €1,000,000.00
"""

import os, asyncio, json, uuid, shutil, sys, logging, time
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask, jsonify

# --- CAPA DE SEGURIDAD Y DEPENDECIAS ---
try:
    import yt_dlp
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup, 
        ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
    )
    from telegram.ext import (
        ApplicationBuilder, CommandHandler, MessageHandler, 
        CallbackQueryHandler, ContextTypes, filters, Defaults
    )
    from telegram.constants import ParseMode, ChatAction
except ImportError:
    os.system('pip install python-telegram-bot yt-dlp flask requests')
    import yt_dlp

# =================================================================
# 1. NÚCLEO DE CONFIGURACIÓN Y BASE DE DATOS (THE VAULT)
# =================================================================
class Core:
    ADMIN_ID = 8398522835
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    DB_FILE = "infinity_vault.json"
    TEMP_DIR = "buffer_ishak"
    LOG_FILE = "system.log"
    VERSION = "25.9.0-GOLD"

class DatabaseManager:
    def __init__(self):
        self.structure = {
            "users": {},
            "coupons": {},
            "blacklist": [],
            "stats": {"total_dls": 0, "total_users": 0, "revenue": 0},
            "system": {"maint": False, "msg": "🚀 Infinity SaaS Online"}
        }
        self.load_db()

    def load_db(self):
        if os.path.exists(Core.DB_FILE):
            try:
                with open(Core.DB_FILE, 'r') as f:
                    self.structure.update(json.load(f))
            except: pass

    def save_db(self):
        with open(Core.DB_FILE, 'w') as f:
            json.dump(self.structure, f, indent=4)

    def get_user(self, u):
        sid = str(u.id)
        if sid not in self.structure["users"]:
            self.structure["users"][sid] = {
                "id": u.id, "name": u.first_name, "user": u.username,
                "phone": "N/A", "plan": "FREE", "dls": 0, "joined": str(datetime.now())
            }
            self.structure["stats"]["total_users"] += 1
            self.save_db()
        return self.structure["users"][sid]

db = DatabaseManager()

# =================================================================
# 2. MOTOR DE DESCARGA MULTI-PLATAFORMA (SIN MARCAS)
# =================================================================
async def download_engine(url, mode, plan_limit=100):
    if not os.path.exists(Core.TEMP_DIR): os.makedirs(Core.TEMP_DIR)
    file_id = str(uuid.uuid4())[:10]
    
    # Configuración de formatos profesionales
    formats = {
        "MP4": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "MP3": "bestaudio/best",
        "WEBM": "bestvideo[ext=webm]+bestaudio[ext=webm]/best"
    }

    ydl_opts = {
        'format': formats.get(mode, "best"),
        'outtmpl': f'{Core.TEMP_DIR}/{file_id}.%(ext)s',
        'max_filesize': plan_limit * 1024 * 1024,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None
    }

    if mode == "MP3":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    def execute():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            if mode == "MP3": path = os.path.splitext(path)[0] + ".mp3"
            return path, info.get('title', 'Ishak_Media')

    return await asyncio.to_thread(execute)

# =================================================================
# 3. INTERFAZ DE USUARIO (UI/UX)
# =================================================================
def get_main_keyboard(uid):
    # Teclado físico persistente
    layout = [
        [KeyboardButton("📥 DESCARGAR"), KeyboardButton("👤 MI PERFIL")],
        [KeyboardButton("💎 PLANES VIP"), KeyboardButton("🎟️ CANJEAR CUPÓN")],
        [KeyboardButton("🤝 SOPORTE")]
    ]
    if uid == Core.ADMIN_ID:
        layout.append([KeyboardButton("👑 PANEL MAESTRO 👑")])
    return ReplyKeyboardMarkup(layout, resize_keyboard=True)

def get_admin_inline():
    # El corazón de las 20+ funciones de admin
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 LISTA DE USUARIOS (ID/TEL)", callback_data="adm_list")],
        [InlineKeyboardButton("📊 ESTADÍSTICAS", callback_data="adm_stats"), InlineKeyboardButton("📢 BROADCAST", callback_data="adm_bc")],
        [InlineKeyboardButton("🎟️ CREAR CUPÓN", callback_data="adm_cp"), InlineKeyboardButton("🚫 BANEAR", callback_data="adm_ban")],
        [InlineKeyboardButton("💎 GESTIONAR PLAN", callback_data="adm_plan"), InlineKeyboardButton("🔓 UNBAN", callback_data="adm_unban")],
        [InlineKeyboardButton("💾 BACKUP JSON", callback_data="adm_backup"), InlineKeyboardButton("🧹 LIMPIAR TEMP", callback_data="adm_clear")],
        [InlineKeyboardButton("🛠️ MANTENIMIENTO", callback_data="adm_maint"), InlineKeyboardButton("🔄 REINICIAR", callback_data="adm_reboot")],
        [InlineKeyboardButton("❌ CERRAR PANEL", callback_data="adm_close")]
    ])

# =================================================================
# 4. LÓGICA DE PROCESAMIENTO
# =================================================================
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db.get_user(u)
    await update.message.reply_text(
        f"🔥 **BIENVENIDO A ISHAK INFINITY V{Core.VERSION}**\n\n"
        "Sistema operativo. Usa los botones de abajo para navegar sin límites.",
        reply_markup=get_main_keyboard(u.id), parse_mode=ParseMode.MARKDOWN
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    text = update.message.text
    user_data = db.get_user(u)
    state = context.user_data.get("state")

    # --- SEGURIDAD ---
    if str(u.id) in db.structure["blacklist"]: return

    # --- NAVEGACIÓN POR BOTONES ---
    if text == "📥 DESCARGAR":
        await update.message.reply_text("🔗 **ENVÍA EL ENLACE AHORA:**\n(YouTube, TikTok, Instagram, Facebook...)")
    
    elif text == "👤 MI PERFIL":
        msg = (f"👤 **TU CUENTA**\n\n🆔 ID: `{u.id}`\n💎 Plan: `{user_data['plan']}`\n"
               f"📥 Descargas: `{user_data['dls']}`\n📅 Miembro desde: `{user_data['joined'][:10]}`")
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    elif text == "💎 PLANES VIP":
        await update.message.reply_text("💎 **MEJORA TU EXPERIENCIA**\n\n• PRO: 10€/mes\n• INFINITY: 25€ (De por vida)\n\nContacta a @Ishak para pagar.")

    elif text == "🎟️ CANJEAR CUPÓN":
        await update.message.reply_text("Escribe tu código promocional:")
        context.user_data["state"] = "redeem"

    elif text == "👑 PANEL MAESTRO 👑" and u.id == Core.ADMIN_ID:
        await update.message.reply_text("🛠 **MODO DIOS: ISHAK EZZAHOUANI**", reply_markup=get_admin_inline())

    # --- PROCESAMIENTO DE ESTADOS ---
    elif state == "redeem":
        code = text.upper()
        if code in db.structure["coupons"]:
            plan = db.structure["coupons"].pop(code)
            user_data["plan"] = plan
            db.save_db()
            await update.message.reply_text(f"✅ **¡ÉXITO!** Ahora eres usuario {plan}.")
        else:
            await update.message.reply_text("❌ Cupón inválido o usado.")
        context.user_data["state"] = None

    elif state == "bc" and u.id == Core.ADMIN_ID:
        for sid in db.structure["users"]:
            try: await context.bot.send_message(sid, f"📢 **MENSAJE DE ISHAK:**\n\n{text}")
            except: pass
        await update.message.reply_text("✅ Broadcast completado.")
        context.user_data["state"] = None

    elif text.startswith("http"):
        context.user_data["url"] = text
        kb = [[InlineKeyboardButton("📹 MP4", callback_data="dl_MP4"), 
               InlineKeyboardButton("🎵 MP3", callback_data="dl_MP3"),
               InlineKeyboardButton("🌐 WEBM", callback_data="dl_WEBM")]]
        await update.message.reply_text("🎬 **MEDIA DETECTADA**\nElige el formato de salida:", reply_markup=InlineKeyboardMarkup(kb))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    await q.answer()

    # --- FUNCIONES DE ADMIN ---
    if uid == Core.ADMIN_ID:
        if q.data == "adm_list":
            report = "👥 **LISTADO MAESTRO DE USUARIOS**\n\n"
            for sid, d in db.structure["users"].items():
                report += f"• `{sid}` | {d['name']} | Plan: {d['plan']} | 📱 {d['phone']}\n"
            await q.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)
        
        elif q.data == "adm_stats":
            msg = f"📊 **SISTEMA**\n\nUsers: {db.structure['stats']['total_users']}\nDls: {db.structure['stats']['total_dls']}"
            await q.edit_message_text(msg, reply_markup=get_admin_inline())

        elif q.data == "adm_bc":
            await q.message.reply_text("Escribe el mensaje global:")
            context.user_data["state"] = "bc"

        elif q.data == "adm_backup":
            db.save_db()
            await context.bot.send_document(uid, open(Core.DB_FILE, 'rb'), caption="Backup DB")

        elif q.data == "adm_reboot":
            await q.message.reply_text("🔄 Reiniciando motor...")
            os.execl(sys.executable, sys.executable, *sys.argv)

    # --- DESCARGAS ---
    if q.data.startswith("dl_"):
        mode = q.data.split("_")[1]
        url = context.user_data.get("url")
        m = await q.message.reply_text(f"🚀 **Descargando {mode}...**")
        try:
            path, title = await download_engine(url, mode)
            with open(path, 'rb') as f:
                if mode == "MP3": await context.bot.send_audio(uid, f, caption=f"🎵 {title} | Ishak Infinity")
                else: await context.bot.send_video(uid, f, caption=f"🎬 {title} | No Watermark")
            db.structure["stats"]["total_dls"] += 1
            db.structure["users"][str(uid)]["dls"] += 1
            db.save_db()
            os.remove(path)
            await m.delete()
        except Exception as e:
            await m.edit_text(f"❌ Error crítico: {str(e)[:100]}")

# =================================================================
# 5. SERVER Y BOOTSTRAP
# =================================================================
server = Flask(__name__)
@server.route('/')
def home(): return jsonify({"status": "ONLINE", "owner": "Ishak"})

def run_flask(): server.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    bot = ApplicationBuilder().token(Core.TOKEN).build()
    
    bot.add_handler(CommandHandler("start", start_cmd))
    bot.add_handler(CallbackQueryHandler(callback_handler))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print(f"ISHAK INFINITY V{Core.VERSION} OPERATIVO")
    bot.run_polling()
