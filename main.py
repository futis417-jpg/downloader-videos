"""
SISTEMA: ISHAK HYPER-SAAS V25.0 - INFINITY EDITION
ESTADO: FULL OVERLORD MODE - NO LIMITS
PROPIETARIO: Ishak Ezzahouani (8398522835)
"""

import os, asyncio, json, uuid, shutil, sys
from datetime import datetime
from threading import Thread
from flask import Flask
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode

try:
    import yt_dlp
except ImportError:
    os.system('pip install yt-dlp python-telegram-bot flask')
    import yt_dlp

# =================================================================
# 1. NÚCLEO DE DATOS
# =================================================================
class Config:
    ADMIN_ID = 8398522835
    TOKEN = "8780125825:AAFZZonawTj_kNHrewjQtAdELod9vj3a6w4"
    DB_FILE = "infinity_vault.json"
    TEMP_DIR = "downloads"

class Database:
    def __init__(self):
        self.data = {
            "users": {}, "coupons": {}, "blacklist": [],
            "stats": {"total_dls": 0},
            "settings": {"maint": False}
        }
        self.load()

    def load(self):
        if os.path.exists(Config.DB_FILE):
            with open(Config.DB_FILE, 'r') as f: self.data = json.load(f)

    def save(self):
        with open(Config.DB_FILE, 'w') as f: json.dump(self.data, f, indent=4)

    def get_user(self, u):
        sid = str(u.id)
        if sid not in self.data["users"]:
            self.data["users"][sid] = {
                "id": u.id, "name": u.first_name, "username": u.username, "phone": "Sin verificar",
                "plan": "FREE", "dls": 0, "points": 0
            }
            self.save()
        return self.data["users"][sid]

db = Database()

# =================================================================
# 2. TECLADOS PERMANENTES (BOTONES AL LADO DEL TEXTO)
# =================================================================
def get_main_reply_markup(uid):
    btns = [
        [KeyboardButton("📥 Descargar"), KeyboardButton("👤 Perfil")],
        [KeyboardButton("💎 Planes VIP"), KeyboardButton("🎟️ Canjear Cupón")]
    ]
    if uid == Config.ADMIN_ID:
        btns.append([KeyboardButton("👑 PANEL ADMIN 👑")])
    return ReplyKeyboardMarkup(btns, resize_keyboard=True)

# =================================================================
# 3. FUNCIONES DE ADMINISTRACIÓN
# =================================================================
def admin_inline_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 LISTA USUARIOS COMPLETA", callback_data="a_list_all")],
        [InlineKeyboardButton("📊 Stats", callback_data="a_stats"), InlineKeyboardButton("📢 Broadcast", callback_data="a_bc")],
        [InlineKeyboardButton("🎟️ Crear Cupón", callback_data="a_cp"), InlineKeyboardButton("💎 Dar VIP", callback_data="a_vip")],
        [InlineKeyboardButton("🚫 Banear", callback_data="a_ban"), InlineKeyboardButton("🔓 Unban", callback_data="a_unban")],
        [InlineKeyboardButton("💾 Backup", callback_data="a_bkp"), InlineKeyboardButton("🧹 Limpiar", callback_data="a_clear")],
        [InlineKeyboardButton("🔄 Reiniciar Bot", callback_data="a_reboot")]
    ])

# =================================================================
# 4. MOTOR DE DESCARGA PRO
# =================================================================
async def download_pro(url, fmt):
    if not os.path.exists(Config.TEMP_DIR): os.makedirs(Config.TEMP_DIR)
    fid = str(uuid.uuid4())[:8]
    opts = {
        'format': 'bestvideo+bestaudio/best' if fmt != "MP3" else 'bestaudio/best',
        'outtmpl': f'{Config.TEMP_DIR}/{fid}.%(ext)s',
        'quiet': True, 'noplaylist': True,
    }
    if fmt == "MP3":
        opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]

    def run():
        with yt_dlp.YoutubeDL(opts) as ydl:
            res = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(res)
            if fmt == "MP3": path = os.path.splitext(path)[0] + ".mp3"
            return path, res.get('title', 'Ishak_Media')
    return await asyncio.to_thread(run)

# =================================================================
# 5. HANDLERS
# =================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    db.get_user(u)
    await update.message.reply_text(
        f"🔥 **BIENVENIDO AL IMPERIO INFINITY**\nIshak, usa los botones de abajo para navegar sin comandos.",
        reply_markup=get_main_reply_markup(u.id), parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    text = update.message.text
    user = db.get_user(u)
    mode = context.user_data.get("mode")

    # Lógica de estados de Admin
    if u.id == Config.ADMIN_ID and mode:
        if mode == "bc": # Broadcast
            for sid in db.data["users"]:
                try: await context.bot.send_message(sid, f"📢 **MENSAJE GLOBAL:**\n{text}")
                except: pass
            await update.message.reply_text("✅ Mensaje enviado a todos.")
        elif mode == "cp": # Cupón: CODIGO|PLAN
            c, p = text.split("|")
            db.data["coupons"][c.upper()] = p.upper()
            db.save(); await update.message.reply_text(f"🎟️ Cupón {c} creado.")
        context.user_data["mode"] = None
        return

    # Navegación por botones Reply
    if text == "📥 Descargar":
        await update.message.reply_text("🔗 Pega el link del video aquí:")
    elif text == "👤 Perfil":
        await update.message.reply_text(f"👤 **PERFIL**\nID: `{u.id}`\nPlan: {user['plan']}\nDescargas: {user['dls']}", parse_mode=ParseMode.MARKDOWN)
    elif text == "💎 Planes VIP":
        await update.message.reply_text("💎 **PLANES DISPONIBLES**\n- PRO: 10€\n- INFINITY: 25€\nContacta con @Ishak para comprar.")
    elif text == "🎟️ Canjear Cupón":
        await update.message.reply_text("Escribe tu código de cupón:")
        context.user_data["mode"] = "redeem"
    elif text == "👑 PANEL ADMIN 👑" and u.id == Config.ADMIN_ID:
        await update.message.reply_text("🛠 **MODO DIOS ACTIVADO**", reply_markup=admin_inline_kb())
    
    # Procesar Links o Cupones
    elif text.startswith("http"):
        context.user_data["url"] = text
        kb = [[InlineKeyboardButton("📹 MP4", callback_data="dl_MP4"), InlineKeyboardButton("🎵 MP3", callback_data="dl_MP3")]]
        await update.message.reply_text("🎬 **FORMATO:**", reply_markup=InlineKeyboardMarkup(kb))
    elif context.user_data.get("mode") == "redeem":
        code = text.upper()
        if code in db.data["coupons"]:
            user["plan"] = db.data["coupons"].pop(code)
            db.save(); await update.message.reply_text(f"✅ ¡Plan {user['plan']} activado!")
        else: await update.message.reply_text("❌ Cupón inválido.")
        context.user_data["mode"] = None

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    await q.answer()

    if q.data == "a_list_all" and uid == Config.ADMIN_ID:
        msg = "👥 **LISTA COMPLETA DE USUARIOS**\n\n"
        for sid, d in db.data["users"].items():
            msg += f"👤 {d['name']} | ID: `{sid}` | 📱 {d['phone']} | 💎 {d['plan']}\n"
        # Si el mensaje es muy largo, Telegram lo corta, así que lo enviamos por partes o en un bloque
        await q.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    elif q.data == "a_bkp" and uid == Config.ADMIN_ID:
        db.save()
        await context.bot.send_document(uid, open(Config.DB_FILE, "rb"), caption="Respado de Base de Datos")

    elif q.data == "a_reboot" and uid == Config.ADMIN_ID:
        await q.message.reply_text("🔄 Reiniciando...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif q.data.startswith("dl_"):
        fmt = q.data.split("_")[1]
        url = context.user_data.get("url")
        m = await q.message.reply_text("⚡ Procesando...")
        try:
            path, title = await download_pro(url, fmt)
            with open(path, 'rb') as f:
                if fmt == "MP3": await context.bot.send_audio(uid, f, caption=f"🎵 {title}")
                else: await context.bot.send_video(uid, f, caption=f"🎬 {title}")
            db.data["stats"]["total_dls"] += 1; db.save(); os.remove(path); await m.delete()
        except Exception as e: await m.edit_text(f"❌ Error: {str(e)[:50]}")

# =================================================================
# 6. LANZAMIENTO
# =================================================================
app = Flask(__name__)
@app.route('/')
def h(): return "ISHAK_V25_READY"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    bot = ApplicationBuilder().token(Config.TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CallbackQueryHandler(handle_callback))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("SaaS Corriendo...")
    bot.run_polling()
