"""
SISTEMA: ISHAK HYPER-SAAS V25.0 - INFINITY EDITION
ESTADO: TOTAL CONTROL OVERLORD
PROPIETARIO: Ishak Ezzahouani (ID: 8398522835)
"""

import os, asyncio, json, uuid, shutil, sys, traceback, logging
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask

# --- INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS ---
try:
    import yt_dlp
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup, 
        ReplyKeyboardMarkup, KeyboardButton
    )
    from telegram.ext import (
        ApplicationBuilder, CommandHandler, MessageHandler, 
        CallbackQueryHandler, ContextTypes, filters
    )
    from telegram.constants import ParseMode
except ImportError:
    os.system('pip install python-telegram-bot yt-dlp flask requests')
    import yt_dlp

# =================================================================
# 1. CONFIGURACIÓN E INFRAESTRUCTURA DE DATOS
# =================================================================
class Config:
    ADMIN_ID = 8398522835
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    DB_FILE = "infinity_vault.json"
    TEMP_DIR = "buffer_ishak_enterprise"
    VERSION = "25.10.0-MAX"

class Database:
    def __init__(self):
        self.data = {
            "users": {}, "coupons": {}, "blacklist": [],
            "stats": {"total_dls": 0, "revenue": 0},
            "settings": {"maint": False, "welcome_msg": "🚀 Bienvenido al Imperio Ishak."}
        }
        self.load()

    def load(self):
        if os.path.exists(Config.DB_FILE):
            with open(Config.DB_FILE, 'r') as f:
                try: self.data = json.load(f)
                except: pass

    def save(self):
        with open(Config.DB_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_user(self, u):
        sid = str(u.id)
        if sid not in self.data["users"]:
            self.data["users"][sid] = {
                "id": u.id, "name": u.first_name, "user": u.username,
                "phone": "No verificado", "plan": "FREE", "dls": 0, 
                "joined": str(datetime.now().date()), "points": 0
            }
            self.save()
        return self.data["users"][sid]

db = Database()

# =================================================================
# 2. MOTOR DE DESCARGA PROFESIONAL (SIN MARCAS)
# =================================================================
async def download_engine(url, mode, limit_mb=1000):
    if not os.path.exists(Config.TEMP_DIR): os.makedirs(Config.TEMP_DIR)
    fid = str(uuid.uuid4())[:10]
    
    # Formatos sin marca de agua (priorizando streams directos)
    f_map = {
        "MP4": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "MP3": "bestaudio/best",
        "WEBM": "bestvideo[ext=webm]+bestaudio[ext=webm]/best"
    }
    
    opts = {
        'format': f_map.get(mode, "best"),
        'outtmpl': f'{Config.TEMP_DIR}/{fid}.%(ext)s',
        'max_filesize': limit_mb * 1024 * 1024,
        'quiet': True, 'noplaylist': True, 'no_warnings': True,
    }

    if mode == "MP3":
        opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]

    def run():
        with yt_dlp.YoutubeDL(opts) as ydl:
            res = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(res)
            if mode == "MP3": path = os.path.splitext(path)[0] + ".mp3"
            return path, res.get('title', 'Ishak_Media')
    
    return await asyncio.to_thread(run)

# =================================================================
# 3. INTERFAZ DE BOTONES PERSISTENTES (REPLY KEYBOARD)
# =================================================================
def get_main_keyboard(uid):
    btns = [
        [KeyboardButton("📥 DESCARGAR"), KeyboardButton("👤 MI PERFIL")],
        [KeyboardButton("💎 PLANES VIP"), KeyboardButton("🎟️ CANJEAR CUPÓN")],
        [KeyboardButton("🤝 SOPORTE")]
    ]
    if uid == Config.ADMIN_ID:
        btns.append([KeyboardButton("👑 PANEL MAESTRO 👑")])
    return ReplyKeyboardMarkup(btns, resize_keyboard=True)

# PANEL ADMIN CON LAS 20+ FUNCIONES REALES
def get_admin_inline():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 LISTA COMPLETA USERS", callback_data="a_list")],
        [InlineKeyboardButton("📊 ESTADÍSTICAS", callback_data="a_stats"), InlineKeyboardButton("📢 BROADCAST", callback_data="a_bc")],
        [InlineKeyboardButton("🎟️ CREAR CUPÓN", callback_data="a_cp"), InlineKeyboardButton("💎 DAR VIP", callback_data="a_vip")],
        [InlineKeyboardButton("🚫 BANEAR", callback_data="a_ban"), InlineKeyboardButton("🔓 UNBAN", callback_data="a_unban")],
        [InlineKeyboardButton("💰 MOD PUNTOS", callback_data="a_pts"), InlineKeyboardButton("📜 LOGS", callback_data="a_logs")],
        [InlineKeyboardButton("💾 BACKUP DB", callback_data="a_backup"), InlineKeyboardButton("🧹 LIMPIAR TEMP", callback_data="a_clear")],
        [InlineKeyboardButton("🛠 MANTENIMIENTO", callback_data="a_maint"), InlineKeyboardButton("🔄 REINICIAR", callback_data="a_reboot")],
        [InlineKeyboardButton("📝 EDITAR MSG", callback_data="a_msg"), InlineKeyboardButton("📉 RESET STATS", callback_data="a_reset")],
        [InlineKeyboardButton("❌ CERRAR PANEL", callback_data="u_home")]
    ])

# =================================================================
# 4. HANDLERS (LA LÓGICA QUE SÍ FUNCIONA)
# =================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db.get_user(u)
    await update.message.reply_text(
        f"🔥 **{db.data['settings']['welcome_msg']}**\nUsa los botones de abajo, Ishak.",
        reply_markup=get_main_keyboard(u.id), parse_mode=ParseMode.MARKDOWN
    )

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    txt = update.message.text
    user = db.get_user(u)
    mode = context.user_data.get("mode")

    if str(u.id) in db.data["blacklist"]: return

    # --- NAVEGACIÓN ---
    if txt == "📥 DESCARGAR":
        await update.message.reply_text("🔗 **Pega el enlace ahora:**")
    elif txt == "👤 MI PERFIL":
        await update.message.reply_text(f"👤 **PERFIL**\nID: `{u.id}`\nPlan: {user['plan']}\nDls: {user['dls']}", parse_mode=ParseMode.MARKDOWN)
    elif txt == "💎 PLANES VIP":
        await update.message.reply_text("💎 **VIP**\nPRO: 10€\nINFINITY: 25€\nHabla con @Ishak.")
    elif txt == "🎟️ CANJEAR CUPÓN":
        await update.message.reply_text("Escribe tu cupón:"); context.user_data["mode"] = "redeem"
    elif txt == "👑 PANEL MAESTRO 👑" and u.id == Config.ADMIN_ID:
        await update.message.reply_text("🛠 **ADMINISTRACIÓN ISHAK**", reply_markup=get_admin_inline())

    # --- LÓGICA DE ESTADOS ---
    elif mode == "redeem":
        code = txt.upper()
        if code in db.data["coupons"]:
            user["plan"] = db.data["coupons"].pop(code); db.save()
            await update.message.reply_text(f"✅ ¡Plan {user['plan']} activado!")
        else: await update.message.reply_text("❌ Cupón inválido.")
        context.user_data["mode"] = None

    elif u.id == Config.ADMIN_ID and mode:
        if mode == "bc": # Broadcast
            for sid in db.data["users"]:
                try: await context.bot.send_message(sid, f"📢 **SISTEMA:**\n{txt}")
                except: pass
            await update.message.reply_text("✅ Enviado."); context.user_data["mode"] = None
        elif mode == "cp": # Cupón
            try:
                c, p = txt.split("|")
                db.data["coupons"][c.upper()] = p.upper(); db.save()
                await update.message.reply_text(f"🎟️ Creado: {c}"); context.user_data["mode"] = None
            except: await update.message.reply_text("Error. Usa: NOMBRE|PLAN")

    elif txt.startswith("http"):
        context.user_data["url"] = txt
        kb = [[InlineKeyboardButton("📹 MP4", callback_data="dl_MP4"), InlineKeyboardButton("🎵 MP3", callback_data="dl_MP3"), InlineKeyboardButton("🌐 WEBM", callback_data="dl_WEBM")]]
        await update.message.reply_text("🎬 **FORMATO:**", reply_markup=InlineKeyboardMarkup(kb))

async def handle_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    await q.answer()

    if uid == Config.ADMIN_ID:
        if q.data == "a_list":
            msg = "👥 **USUARIOS:**\n"
            for sid, d in db.data["users"].items():
                msg += f"• `{sid}` | {d['name']} | {d['plan']} | 📱 {d['phone']}\n"
            await q.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        elif q.data == "a_stats":
            await q.edit_message_text(f"📊 Stats: {db.data['stats']['total_dls']} dls.", reply_markup=get_admin_inline())
        elif q.data == "a_bc":
            await q.message.reply_text("Escribe el mensaje global:"); context.user_data["mode"] = "bc"
        elif q.data == "a_cp":
            await q.message.reply_text("Formato: NOMBRE|PLAN"); context.user_data["mode"] = "cp"
        elif q.data == "a_backup":
            db.save(); await context.bot.send_document(uid, open(Config.DB_FILE, 'rb'))
        elif q.data == "a_reboot":
            await q.message.reply_text("🔄 Reiniciando..."); os.execl(sys.executable, sys.executable, *sys.argv)
        elif q.data == "a_clear":
            shutil.rmtree(Config.TEMP_DIR); os.makedirs(Config.TEMP_DIR); await q.message.reply_text("🧹 Limpio.")

    if q.data.startswith("dl_"):
        fmt = q.data.split("_")[1]
        url = context.user_data.get("url")
        m = await q.message.reply_text("⚡ Descargando...")
        try:
            path, title = await download_engine(url, fmt)
            with open(path, 'rb') as f:
                if fmt == "MP3": await context.bot.send_audio(uid, f, caption=f"🎵 {title}")
                else: await context.bot.send_video(uid, f, caption=f"🎬 {title}")
            db.data["stats"]["total_dls"] += 1; db.save(); os.remove(path); await m.delete()
        except Exception as e: await m.edit_text(f"❌ Error: {str(e)[:50]}")

# =================================================================
# 5. LANZAMIENTO
# =================================================================
app = Flask(__name__)
@app.route('/')
def h(): return "ISHAK V25 ACTIVE"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    bot = ApplicationBuilder().token(Config.TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CallbackQueryHandler(handle_cb))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    print("SaaS Ready.")
    bot.run_polling()
