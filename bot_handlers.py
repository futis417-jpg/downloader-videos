import os
import asyncio
import re
import time
import uuid
import datetime
import gc
import hashlib
import platform
import yt_dlp
import psutil

from telegram import Update, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import EmpireConfig, settings
from database_core import db
from security_core import sec_core, sanitizer
from ui_components import EmpireUI
from logger_core import logger, audit_logger, alert_system
from engines import MediaEngine, casino_engine, real_tools, progress_tracker

async def send_chunked_message(reply_func, text):
    lines = text.split('\n')
    chunk = ""
    for line in lines:
        if len(chunk) + len(line) > 4000:
            await reply_func(chunk, parse_mode="Markdown")
            chunk = line + "\n"
        else:
            chunk += line + "\n"
    if chunk:
        await reply_func(chunk, parse_mode="Markdown")

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload.startswith("stars_pack_"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Carga útil del paquete inválida.")

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid_str = str(update.message.from_user.id)
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    
    if payload.startswith("stars_pack_"):
        pack_key = payload.replace("stars_pack_", "")
        pack = EmpireConfig.STARS_PACKAGES.get(pack_key)
        
        if pack:
            u_data, _ = await db.get_user(update.message.from_user)
            u_data["stats"]["stars_spent"] += payment.total_amount
            u_data["total_spent_stars"] = u_data.get("total_spent_stars", 0) + payment.total_amount
            db.data["stats"]["stars_revenue"] += payment.total_amount
            
            asyncio.create_task(db.pay_affiliate_commission(uid_str, payment.total_amount))
            
            if pack["type"] == "points":
                u_data["points"] += pack["value"]
                await db.log_tx(uid_str, pack["value"], f"Compra Stars: {pack['name']}")
                msg = f"✅ Has adquirido `{pack['value']} Puntos Imperiales`."
            
            elif pack["type"] == "sub":
                u_data["plan"] = pack["value"]
                current_expiry = u_data.get("plan_expiry")
                base_date = datetime.datetime.fromisoformat(current_expiry) if current_expiry else datetime.datetime.now()
                new_expiry = base_date + datetime.timedelta(days=30)
                u_data["plan_expiry"] = str(new_expiry)
                await db.log_tx(uid_str, 0, f"Suscripción {pack['value']} x30 días (Stars)")
                msg = f"✅ **SUSCRIPCIÓN ACTIVADA**. Eres **{pack['value']}** hasta `{new_expiry.date()}`."

            elif pack["type"] == "vip":
                current_vip = u_data.get("vip_expiry")
                base_vip = datetime.datetime.fromisoformat(current_vip) if current_vip else datetime.datetime.now()
                new_vip = base_vip + datetime.timedelta(days=30)
                u_data["vip_expiry"] = str(new_vip)
                await db.log_tx(uid_str, 0, "VIP Sala x30 días (Stars)")
                msg = f"🥂 **ACCESO VIP ACTIVADO** hasta `{new_vip.date()}`."
                if "VIP_MEMBER" not in u_data.get("achievements", []):
                    u_data.setdefault("achievements", []).append("VIP_MEMBER")
                    u_data["points"] += EmpireConfig.ACHIEVEMENTS["VIP_MEMBER"]["reward"]
                    msg += "\n🏆 ¡LOGRO: VIP Exclusivo! +2000 pts"

            elif pack["type"] == "gift_card":
                code = await db.generate_gift_card(pack["value"])
                msg = f"🎁 **TARJETA REGALO GENERADA**\nCódigo: `{code}`\nValor: **{pack['value']} pts**\n\nRegálasela con el comando /gift `{code}`"

            if u_data.get("total_spent_stars", 0) >= 1000 and "WHALE" not in u_data.get("achievements", []):
                u_data.setdefault("achievements", []).append("WHALE")
                u_data["points"] += EmpireConfig.ACHIEVEMENTS["WHALE"]["reward"]
                msg += "\n🐋 ¡LOGRO BALLENA! +15000 pts"
            
            if "INVESTOR" not in u_data.get("achievements", []):
                u_data.setdefault("achievements", []).append("INVESTOR")
                u_data["points"] += 5000
                msg += "\n🏆 ¡LOGRO: Inversor Privado! +5000 pts"
            
            await db.save()
            audit_logger.log("STARS_PURCHASE", user_id=uid_str, details={"pack": pack_key, "amount": payment.total_amount})
            await update.message.reply_text(f"💎 **TRANSACCIÓN CONFIRMADA**\n{msg}", parse_mode="Markdown")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid_str = str(user.id)
    
    if db.data["system"]["maint_mode"] and user.id != EmpireConfig.ADMIN_ID:
        return await update.message.reply_text("🛠️ **SISTEMA EN MANTENIMIENTO CORPORATIVO.** Vuelve más tarde.")

    if sec_core.rate_limit(user.id, limit=3): 
        return

    referrer_id = context.args[0] if context.args else None
    u_data, referrer_rewarded = await db.get_user(user, referrer_id)

    if referrer_rewarded:
        try:
            await context.bot.send_message(referrer_id, f"🎉 **¡ALERTA VIRAL V400!**\nUn nuevo ciudadano ({user.first_name}) se ha unido con tu enlace. Has recibido **+1500 pts**.")
        except: pass

    if not u_data.get("captcha_solved") and user.id != EmpireConfig.ADMIN_ID:
        question = sec_core.generate_captcha(user.id)
        await update.message.reply_text(f"🛡️ **VERIFICACIÓN ANTI-DDOS (V400).**\nResuelve:\n`{question}`\nResponde solo con el número.")
        context.user_data["state"] = "WAIT_CAPTCHA"
        return

    lang = u_data.get("settings", {}).get("language", "es")
    welcome_msg = EmpireConfig.LANGUAGES.get(lang, EmpireConfig.LANGUAGES["es"])["welcome"]
    if user.id == EmpireConfig.ADMIN_ID:
        welcome_msg = "👁️ **SALVE, DIRECTOR ISHAK.**\nArquitectura V400 operativa. Redundancia asíncrona y Módulos de Comando en línea."

    await update.message.reply_text(welcome_msg, reply_markup=EmpireUI.main_keyboard(u_data), parse_mode="Markdown")

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user = update.effective_user
    text = update.message.text
    uid_str = str(user.id)

    if sec_core.rate_limit(user.id): return
    if sec_core.check_anomaly(user.id, text):
        return await update.message.reply_text("⚠️ **ANOMALÍA DETECTADA:** Has enviado el mismo comando múltiples veces en un segundo. Calma.")

    u_data, _ = await db.get_user(user)
    if u_data.get("is_banned"):
        return await update.message.reply_text("🚫 Cuenta suspendida por infracción corporativa.")

    db.data["stats"]["commands_executed"] += 1
    audit_logger.log("COMMAND_EXEC", user_id=uid_str, details={"command": text[:50]})

    MAIN_COMMANDS = [
        "📥 EXTRACCIÓN", "⭐️ TIENDA OFICIAL (STARS)", "💎 MERCADO NEGRO", 
        "⚙️ AJUSTES PRO", "🏢 ÁREA B2B", "🎰 CASINO IMPERIAL", "🛠️ CAJA DE HERRAMIENTAS", 
        "👤 PERFIL", "🎁 TRIBUTO", "🎮 MISIONES Y LOGROS", "🎧 SOPORTE", 
        "👑 PANEL OVERLORD 👑", "🌐 DATOS MATRIZ", "🛡️ FACCIONES", "🔔 NOTIFICACIONES",
        "🏆 RANKING GLOBAL", "🎫 CANJEAR CÓDIGO", "🥂 SALA VIP", "🏟️ TORNEO ADMIN",
    ]
    
    if text in MAIN_COMMANDS:
        context.user_data["state"] = None 
        
    state = context.user_data.get("state")
    
    if state == "WAIT_CAPTCHA":
        if sec_core.verify_captcha(user.id, text):
            db.data["users"][uid_str]["captcha_solved"] = True
            await db.save()
            context.user_data["state"] = None
            await update.message.reply_text("✅ Acceso autorizado a la matriz.", reply_markup=EmpireUI.main_keyboard(u_data))
        else:
            await update.message.reply_text("❌ Error en verificación de seguridad. Inténtalo de nuevo.")
        return

    if not state and re.match(r'^https?://', text):
        clean_url = sanitizer.sanitize_url(text)
        if not clean_url:
            return await update.message.reply_text("❌ URL inválida o bloqueada por seguridad.")
        context.user_data["active_url"] = clean_url
        await update.message.reply_text("🛠 **Enlace detectado automáticamente.** Selecciona formato:", reply_markup=EmpireUI.format_selector())
        return

    if text == "📥 EXTRACCIÓN":
        await update.message.reply_text("🔗 **PROTOCOLOS LISTOS. ENVÍA EL ENLACE O BUSCA:**\n*(Veo3, YT, IG, TikTok o escribe palabras clave...)*")
        context.user_data["state"] = "WAIT_URL"

    elif text == "⭐️ TIENDA OFICIAL (STARS)":
        await update.message.reply_text("⭐️ **MERCADO DIGITAL OFICIAL**\nSuscripciones y puntos mediante pagos seguros nativos (Telegram Stars):", reply_markup=EmpireUI.stars_shop())

    elif text == "💎 MERCADO NEGRO":
        cv = round(db.data["market_stats"]["crypto_value"], 2)
        trend_icon = "📈" if db.data["market_stats"].get("trend", "up") == "up" else "📉"
        c_bal = u_data.get("crypto_balance", 0.0)
        msg = (
            f"💎 **MERCADO CLANDESTINO V400**\n"
            f"Tu capital: `{u_data['points']} pts`.\n"
            f"Tus IshakCoins: `{c_bal:.4f}`\n\n"
            f"Valor IshakCoin actual: `{cv}` pts {trend_icon}\n"
            f"*(Fluctuaciones en tiempo real cada 10 mins)*\n\n"
            f"Usa tus puntos para operar o comprar ítems exclusivos:"
        )
        await update.message.reply_text(msg, reply_markup=EmpireUI.shop_panel(), parse_mode="Markdown")

    elif text == "⚙️ AJUSTES PRO":
        await update.message.reply_text("⚙️ **PANEL DE CONFIGURACIÓN AVANZADA:**", reply_markup=EmpireUI.settings_panel(u_data['settings']))

    elif text == "🏢 ÁREA B2B":
        if u_data['plan'] == 'GOD':
            await update.message.reply_text("🏢 **ENTORNO EMPRESARIAL B2B**\nGenera claves API reales encriptadas en SHA-256 para interactuar con nuestro endpoint remoto.", reply_markup=EmpireUI.b2b_panel(u_data.get('api_key')))
        else:
            await update.message.reply_text("🚫 Acceso restringido. Esta área es exclusiva para el rango GOD.")

    elif text == "🎰 CASINO IMPERIAL":
        await update.message.reply_text("🎰 **BIENVENIDO AL CASINO V400**\nJuegos actualizados. Selecciona tu mesa:", reply_markup=EmpireUI.casino_panel())

    elif text == "🛠️ CAJA DE HERRAMIENTAS":
        await update.message.reply_text("🛠️ **UTILERÍA CYBERPUNK V400 (HERRAMIENTAS REALES):**", reply_markup=EmpireUI.utils_panel())

    elif text == "👤 PERFIL":
        plan = EmpireConfig.PLANS[u_data["plan"]]
        fac = u_data.get("faction") or "Ninguna"
        crypto_bal = u_data.get("crypto_balance", 0.0)
        bot_info = await context.bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={uid_str}"
        
        user_txs = [tx for tx in db.data["transactions"] if tx["uid"] == uid_str]
        last_3_txs = user_txs[-3:]
        tx_str = ""
        if last_3_txs:
            for tx in reversed(last_3_txs):
                sign = "+" if tx['amount'] > 0 else ""
                tx_str += f"  • {tx['date'][:16]} | {sign}{tx['amount']} pts | {tx['desc']}\n"
        else:
            tx_str = "  • Sin transacciones recientes.\n"

        streak = u_data.get("streak", 0)
        affiliate_earnings = u_data.get("affiliate_earnings", 0)
        vip_exp = u_data.get("vip_expiry")
        is_vip = vip_exp and datetime.datetime.now() < datetime.datetime.fromisoformat(vip_exp)
        vip_str = f"\n🥂 VIP hasta: `{datetime.datetime.fromisoformat(vip_exp).strftime('%d/%m/%Y')}`" if is_vip else ""
        
        msg = (
            f"👤 **PERFIL CORPORATIVO V401**\n"
            f"🆔 `{user.id}` | Alias: `{u_data['name']}`\n"
            f"🎖️ Nivel: `{u_data['level']}` | Rango: **{plan['name']}**\n"
            f"🛡️ Facción: `{fac}`{vip_str}\n"
            f"💰 Capital: `{u_data['points']} pts` | ⭐️ Stars: `{u_data['stats'].get('stars_spent', 0)}`\n"
            f"📈 IshakCoins: `{crypto_bal:.4f}`\n"
            f"🔥 Racha diaria: `{streak} días`\n"
            f"💸 Ganancias afiliado: `{affiliate_earnings} pts`\n"
            f"📥 Extracciones Hoy: `{u_data['daily_downloads'][0]} / {plan['limit_daily']}`\n"
            f"📊 Total descargas: `{u_data.get('total_downloads', 0)}`\n\n"
            f"🔗 **Enlace de Reclutamiento Viral:**\n`{ref_link}`\n"
            f"*(Ganas 1500 pts T1 + 375 pts T2 por referido)*\n\n"
            f"📊 **Historial de Auditoría (SaaS):**\n{tx_str}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🎁 TRIBUTO":
        today = str(datetime.date.today())
        if u_data.get("last_daily") == today:
            streak = u_data.get("streak", 0)
            await update.message.reply_text(f"❌ Tributo ya reclamado hoy. Racha actual: 🔥 {streak} días.")
        else:
            total, streak, week_achieved = await db.process_daily_streak(uid_str)
            streak_icon = "🔥" if streak >= 3 else "✅"
            msg = f"{streak_icon} El Imperio te otorga **{total} pts**.\n🗓️ Racha: **{streak} días consecutivos**"
            if streak >= 3:
                msg += f"\n⚡ ¡Bonus de racha: +{min(streak * 100, 2000)} pts incluidos!"
            if week_achieved:
                msg += f"\n🏆 ¡LOGRO: Racha Semanal! +{EmpireConfig.ACHIEVEMENTS['STREAK_WEEK']['reward']} pts"
            await update.message.reply_text(msg, parse_mode="Markdown")

    elif text == "🏆 RANKING GLOBAL":
        await update.message.reply_text("🏆 **RANKING IMPERIAL V401**\nElige categoría:", reply_markup=EmpireUI.leaderboard_panel())

    elif text == "🎫 CANJEAR CÓDIGO":
        await update.message.reply_text("🎫 **CANJEAR CÓDIGO**\nEscribe tu código de cupón o tarjeta regalo:")
        context.user_data["state"] = "WAIT_REDEEM_CODE"

    elif text == "🥂 SALA VIP":
        vip_exp = u_data.get("vip_expiry")
        if vip_exp and datetime.datetime.now() < datetime.datetime.fromisoformat(vip_exp):
            exp_str = datetime.datetime.fromisoformat(vip_exp).strftime("%d/%m/%Y")
            msg = (
                f"🥂 **BIENVENIDO A LA SALA VIP**\n"
                f"Tu acceso expira: `{exp_str}`\n\n"
                f"Beneficios activos:\n"
                f"• ✅ Descargas sin límite diario\n"
                f"• ✅ Acceso a tarjetas regalo\n"
                f"• ✅ Soporte prioritario\n"
                f"• ✅ Sin colas de espera\n"
            )
            await update.message.reply_text(msg, reply_markup=EmpireUI.vip_lounge_panel(), parse_mode="Markdown")
        else:
            await update.message.reply_text("🚫 No tienes acceso VIP activo.\n\n💡 Adquiérelo en ⭐️ Tienda Oficial por solo **150 Stars/mes**.")

    elif text == "🏟️ TORNEO ADMIN" and user.id == EmpireConfig.ADMIN_ID:
        t = db.data["system"].get("tournament", {})
        if t.get("active"):
            end = datetime.datetime.fromisoformat(t["end_time"]).strftime("%d/%m %H:%M")
            participants = len(t.get("participants", {}))
            pool = t.get("prize_pool", 0)
            msg = f"🏟️ **TORNEO EN CURSO**\n⏰ Finaliza: `{end}`\n👥 Participantes: `{participants}`\n💰 Bote: `{pool} pts`"
        else:
            msg = "🏟️ **PANEL DE TORNEOS ADMIN**\nNo hay torneo activo."
        await update.message.reply_text(msg, reply_markup=EmpireUI.admin_tournament_panel(), parse_mode="Markdown")

    elif text == "🛡️ FACCIONES":
        await update.message.reply_text("🛡️ **SISTEMA DE FACCIONES (GREMIOS)**\nÚnete a un clan o forja tu propio destino.", reply_markup=EmpireUI.factions_panel(bool(u_data.get("faction"))))

    elif text == "🎮 MISIONES Y LOGROS":
        bounties = u_data.get("bounties", [])
        msg = "📜 **MISIONES DIARIAS:**\n"
        for b in bounties:
            status = "✅ Completado" if b["done"] else f"⏳ {b['progress']}/{b['target']}"
            msg += f"• {b['desc']} ({status}) -> +{b['reward']} pts\n"
            
        msg += "\n🎮 **SALÓN DE LA FAMA IMPERIAL:**\n"
        for k, v in EmpireConfig.ACHIEVEMENTS.items():
            status = "✅" if k in u_data["achievements"] else "🔒"
            msg += f"{status} **{v['name']}**: {v['desc']}\n"
        
        await send_chunked_message(update.message.reply_text, msg)

    elif text == "🎧 SOPORTE":
        await update.message.reply_text("📝 **Describe tu problema en 1 solo mensaje para el Alto Mando:**")
        context.user_data["state"] = "WAIT_TICKET"

    elif text == "🔔 NOTIFICACIONES":
        notifications = u_data.get("notification_queue", [])
        unread = [n for n in notifications if not n.get("read")]
        if unread:
            msg = "📬 **TUS NOTIFICACIONES:**\n"
            for n in unread:
                msg += f"🔹 [{n['timestamp'][:19]}] {n['message']}\n"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("📭 No tienes notificaciones pendientes.")

    elif text == "👑 PANEL OVERLORD 👑" and user.id == EmpireConfig.ADMIN_ID:
        await update.message.reply_text("🛠 **CENTRO DE COMANDO V400**", reply_markup=EmpireUI.overlord_panel())

    elif text == "🌐 DATOS MATRIZ" and user.id == EmpireConfig.ADMIN_ID:
        s = db.data["stats"]
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        msg = (
            f"🌐 **TELEMETRÍA EN TIEMPO REAL V400**\n"
            f"👥 Usuarios: `{s['total_users']}`\n"
            f"📥 Extracciones: `{s['total_downloads']}`\n"
            f"🎰 Giros Casino: `{s['casino_spins']}`\n"
            f"⭐️ Revenue Stars: `{s.get('stars_revenue', 0)}`\n"
            f"🛡️ Intentos Fraude Bloqueados: `{s.get('fraud_attempts_blocked', 0)}`\n"
            f"🛠️ Fixes Automáticos de DB: `{s.get('self_healing_fixes', 0)}`\n"
            f"🖥️ CPU: `{psutil.cpu_percent()}%` | RAM: `{mem.percent}%`\n"
            f"💾 Disco: `{disk.percent}%` libre\n"
            f"🚀 OS: `{platform.system()} {platform.release()}`\n"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif state == "WAIT_URL":
        if re.match(r'^https?://', text):
            clean_url = sanitizer.sanitize_url(text)
            if not clean_url:
                return await update.message.reply_text("❌ URL inválida o bloqueada.")
            context.user_data["active_url"] = clean_url
            await update.message.reply_text("⚡ **PROCESANDO RELÁMPAGO...**", reply_markup=EmpireUI.format_selector())
            asyncio.create_task(MediaEngine.get_metadata(clean_url))
            context.user_data["state"] = None
        else:
            m = await update.message.reply_text(f"🔍 **BUSCADOR INTELIGENTE V400:**\nRastreando '{text}' en la red global...")
            try:
                def _search():
                    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True, 'default_search': 'ytsearch3'}) as ydl:
                        return ydl.extract_info(text, download=False).get('entries', [])[:3]
                
                results = await asyncio.to_thread(_search)
                
                if results:
                    context.user_data["search_results"] = {str(i): r['url'] for i, r in enumerate(results)}
                    kb = []
                    for i, r in enumerate(results):
                        title = r.get('title', 'Contenido Desconocido')[:35]
                        dur = r.get('duration_string', 'N/A')
                        kb.append([InlineKeyboardButton(f"{i+1}. {title} [{dur}]", callback_data=f"src_{i}")])
                    kb.append([InlineKeyboardButton("❌ ABORTAR", callback_data="u_close")])
                    
                    await m.edit_text("🎯 **OBJETIVOS LOCALIZADOS:**\nSelecciona el archivo para extraer:", reply_markup=InlineKeyboardMarkup(kb))
                else:
                    await m.edit_text("❌ No se encontraron resultados tangibles en la matriz. Intenta otra palabra clave.")
            except Exception as e:
                logger.error(f"Search Engine Error: {e}")
                await m.edit_text("❌ Fallo crítico en el rastreo B2B.")
            context.user_data["state"] = None

    elif state == "WAIT_WATERMARK":
        u_data['settings']['watermark'] = sanitizer.sanitize_text(text, 30)
        await db.save()
        await update.message.reply_text(f"✅ Marca de agua configurada a: `{u_data['settings']['watermark']}`", parse_mode="Markdown")
        context.user_data["state"] = None
        
    elif state == "WAIT_UTIL_TTS":
        text_to_say = sanitizer.sanitize_text(text, 300)
        m = await update.message.reply_text("🗣️ Sintetizando audio real con IA (gTTS)...")
        try:
            lang = u_data.get("settings", {}).get("language", "es")
            audio_path = await real_tools.generate_tts(text_to_say, uid_str, lang)
            if audio_path and os.path.exists(audio_path):
                with open(audio_path, 'rb') as f:
                    await context.bot.send_voice(user.id, f, caption="🗣️ **Audio Real V400**", parse_mode="Markdown")
                os.remove(audio_path)
            else:
                await update.message.reply_text("❌ Fallo en el motor de voz.")
        except Exception as e: 
            await update.message.reply_text("❌ Excepción en generación de voz.")
        finally:
            await m.delete()
        context.user_data["state"] = None

    elif state == "WAIT_UTIL_QR":
        qr_data = sanitizer.sanitize_text(text, 500)
        m = await update.message.reply_text("🔳 Diseñando código QR Real...")
        try:
            img_path = await real_tools.generate_qr(qr_data, uid_str)
            if img_path and os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    await context.bot.send_photo(user.id, f, caption="🔳 **Código QR Generado Exitosamente.**", parse_mode="Markdown")
                os.remove(img_path)
            else:
                await update.message.reply_text("❌ Error al renderizar la imagen QR.")
        except Exception as e:
            await update.message.reply_text("❌ Excepción en generación QR.")
        finally:
            await m.delete()
        context.user_data["state"] = None

    elif state == "WAIT_UTIL_B64ENC":
        encoded = real_tools.encode_base64(text)
        await update.message.reply_text(f"📜 **Cifrado Base64 Completado:**\n`{encoded}`", parse_mode="Markdown")
        context.user_data["state"] = None
        
    elif state == "WAIT_UTIL_B64DEC":
        decoded = real_tools.decode_base64(text)
        await update.message.reply_text(f"🔓 **Descifrado Base64:**\n`{decoded}`", parse_mode="Markdown")
        context.user_data["state"] = None

    elif state == "WAIT_UTIL_URL_THUMB":
        url = text.strip()
        m = await update.message.reply_text("⏳ Extrayendo miniatura máxima resolución...")
        thumb = await MediaEngine.get_thumbnail(url, uid_str)
        if thumb: await context.bot.send_photo(uid_str, thumb, caption="🖼️ Aquí tienes la miniatura.")
        else: await update.message.reply_text("❌ No se pudo extraer miniatura de ese enlace.")
        await m.delete(); context.user_data["state"] = None
        
    elif state == "WAIT_UTIL_URL_META":
        url = text.strip()
        m = await update.message.reply_text("⏳ Analizando metadatos en profundidad...")
        meta = await MediaEngine.get_metadata(url)
        if meta:
            res = f"📊 **METADATOS EXTRAÍDOS**\n• Título: `{meta.get('title')}`\n• Autor: `{meta.get('uploader')}`\n• Duración: `{meta.get('duration')}s`\n• Vistas: `{meta.get('view_count')}`"
            await update.message.reply_text(res, parse_mode="Markdown")
        else: await update.message.reply_text("❌ Fallo en la extracción.")
        await m.delete(); context.user_data["state"] = None
    
    elif state == "WAIT_UTIL_SEARCH":
        m = await update.message.reply_text("🔍 Buscando en la base de datos con filtros avanzados...")
        try:
            text_lower = text.lower()
            filters = {}
            if "plataforma" in text_lower or "youtube" in text_lower: filters["platform"] = "youtube"
            if "corto" in text_lower or "<5" in text_lower: filters["max_duration"] = 300
            if "largo" in text_lower or ">30" in text_lower: filters["min_duration"] = 1800
            if "reciente" in text_lower: filters["sort"] = "date"
            if "visto" in text_lower: filters["sort"] = "views"
            await m.edit_text(f"🔎 **RESULTADOS DE BÚSQUEDA AVANZADA:**\nFiltros aplicados: {filters}\nFuncionalidad completa en desarrollo para V400.2 Enterprise.")
        except Exception as e:
            await m.edit_text("❌ Fallo en búsqueda avanzada.")
        context.user_data["state"] = None

    elif state == "WAIT_TICKET":
        tid = f"TK-{random.randint(1000, 9999)}"
        sanitized_text = sanitizer.sanitize_text(text, 1000)
        db.data["tickets"][tid] = {"uid": uid_str, "text": sanitized_text, "status": "OPEN", "created_at": datetime.datetime.now().isoformat()}
        await db.save()
        await update.message.reply_text(f"✅ Ticket `{tid}` enviado al Alto Mando.")
        try: await context.bot.send_message(EmpireConfig.ADMIN_ID, f"🚨 TICKET {tid} de {user.first_name}:\n{sanitized_text}", reply_markup=EmpireUI.ticket_panel(tid))
        except: pass
        context.user_data["state"] = None

    elif state == "WAIT_REDEEM_CODE":
        code = sanitizer.sanitize_text(text.strip().upper(), 30)
        success, msg = await db.redeem_gift_card(uid_str, code)
        if success:
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            if code in db.data["coupons"]:
                coupon_data = db.data["coupons"][code]
                if isinstance(coupon_data, dict) and coupon_data.get("type") == "gift_card":
                    await update.message.reply_text(msg, parse_mode="Markdown")
                elif isinstance(coupon_data, str):
                    plan = coupon_data
                    if plan in EmpireConfig.PLANS:
                        u_data["plan"] = plan
                        expiry = datetime.datetime.now() + datetime.timedelta(days=30)
                        u_data["plan_expiry"] = str(expiry) if plan not in ["FREE", "GOD"] else None
                        del db.data["coupons"][code]
                        await db.save()
                        await update.message.reply_text(f"✅ Cupón canjeado. Plan **{plan}** activado durante 30 días.")
                    else:
                        await update.message.reply_text("❌ Cupón inválido o expirado.")
                else:
                    await update.message.reply_text("❌ Código no reconocido.")
            else:
                await update.message.reply_text("❌ Código no encontrado. Verifica que esté bien escrito.")
        context.user_data["state"] = None

    elif state == "WAIT_FAC_CREATE":
        fac_name = sanitizer.sanitize_text(text.strip(), 20)
        if len(fac_name) < 3 or len(fac_name) > 20: return await update.message.reply_text("❌ Nombre debe tener entre 3 y 20 caracteres.")
        if fac_name in db.data["factions"]: return await update.message.reply_text("❌ Nombre en uso.")
        if u_data["inventory"]["CLAN_TICKET"] > 0:
            u_data["inventory"]["CLAN_TICKET"] -= 1
            db.data["factions"][fac_name] = {"owner": uid_str, "members": [uid_str], "vault": 0, "level": 1}
            u_data["faction"] = fac_name
            if "GUILD_MASTER" not in u_data["achievements"]:
                u_data["achievements"].append("GUILD_MASTER"); u_data["points"] += 3000
                await update.message.reply_text("🏆 ¡LOGRO: Maestro de Gremio! +3000 pts")
            await db.save()
            await update.message.reply_text(f"✅ Has fundado la facción **{fac_name}**.")
        else: await update.message.reply_text("❌ No tienes un Ticket de Fundación (Cómpralo en la tienda).")
        context.user_data["state"] = None

    elif state == "WAIT_FAC_JOIN":
        fac_name = sanitizer.sanitize_text(text.strip(), 20)
        if fac_name in db.data["factions"]:
            db.data["factions"][fac_name]["members"].append(uid_str)
            u_data["faction"] = fac_name
            await db.save()
            await update.message.reply_text(f"✅ Te has unido a **{fac_name}**.")
        else: await update.message.reply_text("❌ Facción no encontrada.")
        context.user_data["state"] = None

    elif state == "WAIT_FAC_DONATE":
        try:
            amt = int(text)
            if amt > 0 and await db.deduct_points(uid_str, amt):
                fac_name = u_data["faction"]
                db.data["factions"][fac_name]["vault"] += amt
                await db.save()
                await update.message.reply_text(f"✅ Donaste {amt} pts a {fac_name}.")
            else: await update.message.reply_text("❌ Saldo insuficiente o inválido.")
        except: await update.message.reply_text("❌ Ingresa un número válido.")
        context.user_data["state"] = None

    elif state == "WAIT_BC" and user.id == EmpireConfig.ADMIN_ID:
        count = 0
        m = await update.message.reply_text("📡 Propagando...")
        for sid in list(db.data["users"].keys()):
            try:
                await context.bot.send_message(sid, f"📢 **MENSAJE DEL DIRECTOR ISHAK:**\n\n{text}")
                count += 1; await asyncio.sleep(0.05)
            except: pass
        await m.edit_text(f"✅ Entregados a {count} súbditos.")
        context.user_data["state"] = None
        
    elif state == "WAIT_BAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = True
            await update.message.reply_text("🚫 Usuario exiliado de la matriz.")
            await db.save()
            audit_logger.log("USER_BANNED", user_id=int(text), severity="CRITICAL")
        context.user_data["state"] = None
        
    elif state == "WAIT_UNBAN" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            db.data["users"][text]["is_banned"] = False
            await update.message.reply_text("🔓 Usuario rehabilitado.")
            await db.save()
            audit_logger.log("USER_UNBANNED", user_id=int(text))
        context.user_data["state"] = None

    elif state == "WAIT_PTS_ID" and user.id == EmpireConfig.ADMIN_ID:
        context.user_data["target_id"] = text.strip()
        await update.message.reply_text("💰 Monto a inyectar:")
        context.user_data["state"] = "WAIT_PTS_VAL"
        
    elif state == "WAIT_PTS_VAL" and user.id == EmpireConfig.ADMIN_ID:
        try:
            val = int(text)
            tid = context.user_data["target_id"]
            if tid in db.data["users"]:
                await db.add_points(tid, val)
                await update.message.reply_text(f"✅ Puntos inyectados con éxito a {tid}.")
        except: pass
        context.user_data["state"] = None

    elif state == "WAIT_CP_CODE" and user.id == EmpireConfig.ADMIN_ID:
        context.user_data["cp_code"] = text.upper().strip()
        await update.message.reply_text("🎫 Rango (FREE, PRO, ULTRA, GOD):")
        context.user_data["state"] = "WAIT_CP_PLAN"

    elif state == "WAIT_CP_PLAN" and user.id == EmpireConfig.ADMIN_ID:
        plan = text.upper().strip()
        if plan in EmpireConfig.PLANS:
            db.data["coupons"][context.user_data["cp_code"]] = plan
            await db.save()
            await update.message.reply_text(f"✅ Cupón empresarial creado.")
        context.user_data["state"] = None

    elif state == "WAIT_PLAN_EDIT_ID" and user.id == EmpireConfig.ADMIN_ID:
        if text in db.data["users"]:
            context.user_data["target_user_id"] = text
            await update.message.reply_text(f"🎭 Redefiniendo a `{text}`:", reply_markup=EmpireUI.plan_selector_admin())
        else: await update.message.reply_text("❌ Usuario no encontrado.")
        context.user_data["state"] = None


async def simulate_crash_tick(bot, uid, message_id, bet, crash_point, context):
    """(BUG REPARADO) Función de simulación extraída correctamente para Crash"""
    current_mult = 1.00
    try:
        while current_mult < crash_point:
            await asyncio.sleep(1.2) 
            
            if context.user_data.get("crash_point") == -1: return
            
            if current_mult < 2.0: current_mult += 0.2
            elif current_mult < 5.0: current_mult += 0.5
            elif current_mult < 10.0: current_mult += 1.0
            else: current_mult += 2.5
            
            if current_mult >= crash_point: break
            
            msg = f"📈 **CRIPTO CRASH (Apuesta: {bet})**\nEl cohete está subiendo...\nMultiplicador actual: `{current_mult:.2f}x`"
            await bot.edit_message_text(msg, chat_id=uid, message_id=message_id, reply_markup=EmpireUI.crash_panel(bet, current_mult))
            
        if context.user_data.get("crash_point") != -1:
            context.user_data["crash_point"] = -1
            msg = f"💥 **¡CRASH!**\nEl cohete explotó en `{crash_point:.2f}x`.\n💀 Perdiste tu apuesta de {bet} pts."
            await bot.edit_message_text(msg, chat_id=uid, message_id=message_id, reply_markup=EmpireUI.casino_panel())
    except Exception as e:
        logger.error(f"Error en Crash tick: {e}")
        alert_system.track_error()

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    uid_str = str(uid)
    data = q.data
    await q.answer()

    u_data, _ = await db.get_user(q.from_user)

    if data.startswith("src_"): 
        idx = data.split("_")[1]
        results = context.user_data.get("search_results", {})
        if idx in results:
            target_url = results[idx]
            clean_url = sanitizer.sanitize_url(target_url)
            if not clean_url:
                return await q.edit_message_text("❌ URL inválida o bloqueada por seguridad.")
            context.user_data["active_url"] = clean_url
            context.user_data.pop("search_results", None) 
            await q.edit_message_text(f"🔗 **Objetivo Enlazado:**\n`{target_url}`\n\n🛠 Selecciona formato de salida:", reply_markup=EmpireUI.format_selector())
        else:
            await q.edit_message_text("❌ Búsqueda caducada en la sesión actual.")

    elif data.startswith("stars_"):
        pack_key = data.replace("stars_", "")
        pack = EmpireConfig.STARS_PACKAGES.get(pack_key)
        if pack:
            title = pack["name"]
            description = f"Pago oficial para: {pack['name']} en Ishak SaaS."
            payload = f"stars_pack_{pack_key}"
            currency = "XTR"
            price = pack["stars"]
            prices = [LabeledPrice(title, price)]
            await context.bot.send_invoice(chat_id=uid, title=title, description=description, payload=payload, provider_token="", currency=currency, prices=prices)

    elif data.startswith("buy_item_"):
        item_key = data.replace("buy_item_", "")
        item = EmpireConfig.SHOP_ITEMS[item_key]
        if await db.deduct_points(uid_str, item["price"]):
            if item_key == "XP_BOOST_X2":
                u_data["active_buffs"]["xp_multiplier"] = 2.0
                u_data["active_buffs"]["buff_expiry"] = str(datetime.datetime.now() + datetime.timedelta(days=1))
                await q.message.reply_text("🧪 Multiplicador de XP x2 activado por 24 horas.")
            else:
                u_data["inventory"][item_key] += 1
                await q.message.reply_text(f"📦 Añadido a tu inventario: {item['name']}")
            await db.save()
        else: await q.message.reply_text("❌ Puntos insuficientes en el balance.")

    elif data == "crypto_buy" or data == "crypto_sell":
        is_buy = data == "crypto_buy"
        amt = 500 if is_buy else 0
        success, msg = await db.trade_crypto(uid_str, amt, is_buy=is_buy)
        await db.save()
        await q.answer(msg, show_alert=True)
        
        cv = round(db.data["market_stats"]["crypto_value"], 2)
        trend_icon = "📈" if db.data["market_stats"].get("trend", "up") == "up" else "📉"
        u_data_updated = db.data["users"][uid_str]
        c_bal = u_data_updated.get("crypto_balance", 0.0)
        new_text = f"💎 **MERCADO CLANDESTINO V400**\nTu capital: `{u_data_updated['points']} pts`.\nTus IshakCoins: `{c_bal:.4f}`\n\nValor IshakCoin actual: `{cv}` pts {trend_icon}\n*(Fluctuaciones en tiempo real cada 10 mins)*\n\nUsa tus puntos para operar o comprar ítems exclusivos:"
        await q.edit_message_text(new_text, reply_markup=EmpireUI.shop_panel(), parse_mode="Markdown")

    elif data.startswith("set_"):
        action = data.split("_")[1]
        if action == "watermark":
            await q.message.reply_text("✍️ Escribe tu nueva Marca de Agua (Max 30 char):")
            context.user_data["state"] = "WAIT_WATERMARK"
        elif action == "transcribe":
            u_data['settings']['auto_transcribe'] = not u_data['settings'].get('auto_transcribe')
            await db.save(); await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))
        elif action == "ghost":
            if u_data['plan'] in ['ULTRA', 'GOD']:
                u_data['settings']['ghost_mode'] = not u_data['settings'].get('ghost_mode')
                await db.save(); await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))
            else: await q.message.reply_text("❌ El Modo Fantasma es exclusivo para rangos ULTRA o GOD.")
        elif action == "doc":
            u_data['settings']['send_as_doc'] = not u_data['settings'].get('send_as_doc')
            await db.save(); await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))
        elif action == "theme":
            themes = ["dark", "light", "midnight"]
            current = u_data['settings'].get('theme', 'dark')
            idx = (themes.index(current) + 1) % len(themes)
            u_data['settings']['theme'] = themes[idx]
            await db.save()
            await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))
            await q.answer(f"Tema cambiado a: {themes[idx].capitalize()}")
        elif action == "lang":
            langs = ["es", "en", "fr", "ar"]
            current = u_data['settings'].get('language', 'es')
            idx = (langs.index(current) + 1) % len(langs)
            u_data['settings']['language'] = langs[idx]
            await db.save()
            await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))
            await q.answer(f"Idioma cambiado a: {langs[idx].upper()}")
        elif action == "notif":
            u_data['settings']['notifications_enabled'] = not u_data['settings'].get('notifications_enabled', True)
            await db.save()
            await q.edit_message_reply_markup(reply_markup=EmpireUI.settings_panel(u_data['settings']))

    elif data == "b2b_gen_key":
        if u_data['plan'] != 'GOD':
            return await q.message.reply_text("❌ Acceso Denegado. Función de seguridad exclusiva para GOD.")
        
        for k, v in list(db.data['b2b_api_keys'].items()):
            if v == uid_str: del db.data['b2b_api_keys'][k]
            
        new_key = f"sk_live_{uuid.uuid4().hex}"
        hashed_key = hashlib.sha256(new_key.encode()).hexdigest()
        
        u_data['api_key'] = hashed_key 
        db.data['b2b_api_keys'][hashed_key] = uid_str
        
        if "HACKER" not in u_data["achievements"]:
            u_data["achievements"].append("HACKER")
            await db.add_points(uid_str, 1000)
        await db.save()
        audit_logger.log("API_KEY_GENERATED", user_id=uid)
        await q.edit_message_text(f"🔑 **NUEVA CLAVE API (GUARDA ESTO, NO SE VOLVERÁ A MOSTRAR):**\n`{new_key}`\n\n*Usa esta clave en la cabecera X-API-KEY para requests al servidor Web.*", reply_markup=EmpireUI.b2b_panel(hashed_key))
    
    elif data == "b2b_docs":
        await q.edit_message_text("📖 **Documentación API B2B:**\n\n🔗 Endpoint: `/api/v1/extract` (POST)\n📦 Body: `{\"url\": \"https://...\"}`\n🔐 Header: `X-API-KEY: tu_clave`\n\n📊 Métricas: `/api/v4/metrics` (GET)\n🩺 Health: `/health` (GET)\n📈 Prometheus: `/metrics` (GET)\n\nPara más detalles visita el panel web.")

    elif data.startswith("util_"):
        act = data.split("_")[1]
        if act == "tts_req":
            await q.message.reply_text("🗣️ Escribe el texto para generar voz (Max 300 letras):")
            context.user_data["state"] = "WAIT_UTIL_TTS"
        elif act == "qr_req":
            await q.message.reply_text("🔳 Envía el enlace o texto para generar un QR real:")
            context.user_data["state"] = "WAIT_UTIL_QR"
        elif act == "b64enc_req":
            await q.message.reply_text("📜 Envía el texto a codificar en Base64:")
            context.user_data["state"] = "WAIT_UTIL_B64ENC"
        elif act == "b64dec_req":
            await q.message.reply_text("🔓 Envía la cadena Base64 a decodificar:")
            context.user_data["state"] = "WAIT_UTIL_B64DEC"
        elif act == "ping":
            m = await q.message.reply_text("📡 Ejecutando test de latencia ICMP real...")
            latency = await real_tools.execute_ping()
            await m.edit_text(f"📡 **Ping Test Real V400:**\nLatencia Red Central: `{latency}`")
        elif act == "thumb":
            await q.message.reply_text("🖼️ Envía el enlace para extraer su miniatura:"); context.user_data["state"] = "WAIT_UTIL_URL_THUMB"
        elif act == "meta":
            await q.message.reply_text("📊 Envía el enlace para inspeccionar metadatos:"); context.user_data["state"] = "WAIT_UTIL_URL_META"
        elif act == "search":
            await q.message.reply_text("🔍 **BÚSQUEDA AVANZADA**\nEscribe tu búsqueda con filtros:\n• 'youtube' o 'tiktok' (plataforma)\n• 'corto' (<5min) o 'largo' (>30min)\n• 'reciente' o 'visto' (orden)"); context.user_data["state"] = "WAIT_UTIL_SEARCH"

    elif data.startswith("fac_"):
        action = data.split("_")[1]
        if action == "create":
            await q.message.reply_text("🛡️ Escribe el nombre de tu nueva Facción (3-20 letras):")
            context.user_data["state"] = "WAIT_FAC_CREATE"
        elif action == "join":
            await q.message.reply_text("🤝 Escribe el nombre exacto de la Facción:")
            context.user_data["state"] = "WAIT_FAC_JOIN"
        elif action == "info":
            f_name = u_data["faction"]
            fac = db.data["factions"][f_name]
            msg = f"🛡️ **FACCIÓN: {f_name}**\n👑 Dueño: `{fac['owner']}`\n👥 Miembros: `{len(fac['members'])}`\n💰 Bóveda: `{fac['vault']} pts`\n📈 Nivel: `{fac['level']}`"
            await q.message.reply_text(msg)
        elif action == "donate":
            await q.message.reply_text("💰 Escribe la cantidad de puntos a donar a la bóveda:")
            context.user_data["state"] = "WAIT_FAC_DONATE"
        elif action == "upgrade":
            f_name = u_data["faction"]
            fac = db.data["factions"][f_name]
            if fac['vault'] >= 10000:
                fac['vault'] -= 10000
                fac['level'] += 1
                await db.save()
                await q.message.reply_text(f"⭐ ¡La facción {f_name} ha subido al Nivel {fac['level']}!")
            else: await q.message.reply_text("❌ La bóveda no tiene 10,000 pts para ascender.")
        elif action == "leave":
            f_name = u_data["faction"]
            db.data["factions"][f_name]["members"].remove(uid_str)
            u_data["faction"] = None
            if uid_str == db.data["factions"][f_name]["owner"]:
                db.data["factions"][f_name]["owner"] = db.data["factions"][f_name]["members"][0] if db.data["factions"][f_name]["members"] else "Abandonada"
            await db.save()
            await q.edit_message_text("🚪 Has abandonado la facción.")

    elif data.startswith("casino_"):
        db.data["stats"]["casino_spins"] = db.data["stats"].get("casino_spins", 0) + 1
        game = data.split("_")[1]
        
        await db.update_bounty(uid_str, "casino_5", 1)
        
        if game == "slots":
            bet = 100
            if await db.deduct_points(uid_str, bet):
                w, msg = casino_engine.play_slots(bet)
                await db.add_points(uid_str, w)
                await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())
            else:
                return await q.message.reply_text("❌ Puntos insuficientes.")
            
        elif game == "roulette":
            bet = 250
            if await db.deduct_points(uid_str, bet):
                num = random.randint(0, 36)
                color = "🟢" if num == 0 else ("🔴" if num in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36] else "⚫")
                msg = f"🎡 **RULETA (Apuesta: 250)**\nLa bola gira...\n\n¡Cayó en **{num} {color}**!\n"
                if num == 0:
                    win = bet * 14; msg += f"🎉 ¡PLENO VERDE! Ganaste {win} pts."; await db.add_points(uid_str, win)
                elif color == "🔴":
                    win = bet * 2; msg += f"🔥 Rojo. Ganaste {win} pts."; await db.add_points(uid_str, win)
                else: msg += "💀 Negro. Pierdes la apuesta."
                await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())
            else:
                return await q.message.reply_text("❌ Puntos insuficientes.")

        elif game == "bj":
            bet = 500
            if await db.deduct_points(uid_str, bet):
                p_hand = [casino_engine.draw_card(), casino_engine.draw_card()]
                d_hand = [casino_engine.draw_card()]
                context.user_data["bj_hand"] = p_hand
                context.user_data["bj_dealer"] = d_hand
                msg = f"🃏 **BLACKJACK (Apuesta 500)**\n\nTu Mano: {p_hand} (Valor: {casino_engine.calculate_hand(p_hand)})\nCrupier: {d_hand} [?]\n\n¿Qué deseas hacer?"
                await q.edit_message_text(msg, reply_markup=EmpireUI.blackjack_panel(bet))
            else:
                return await q.message.reply_text("❌ Puntos insuficientes (500 req).")
            
        elif game == "crash":
            bet = 1000
            if await db.deduct_points(uid_str, bet):
                crash_point = casino_engine.calculate_crash_multiplier()
                context.user_data["crash_point"] = crash_point
                
                msg = f"📈 **CRIPTO CRASH (Apuesta: {bet})**\nEl cohete está despegando...\nMultiplicador actual: `1.00x`"
                await q.edit_message_text(msg, reply_markup=EmpireUI.crash_panel(bet, 1.00))
                asyncio.create_task(simulate_crash_tick(context.bot, uid, q.message.message_id, bet, crash_point, context))
            else:
                return await q.message.reply_text("❌ Puntos insuficientes (1000 req).")

    elif data.startswith("bj_"):
        parts = data.split("_")
        action = parts[1]
        bet = int(parts[2])
        p_hand = context.user_data.get("bj_hand", [])
        d_hand = context.user_data.get("bj_dealer", [])
        
        if action == "hit":
            p_hand.append(casino_engine.draw_card())
            val = casino_engine.calculate_hand(p_hand)
            if val > 21:
                msg = f"💥 **TE PASASTE!**\n\nTu Mano: {p_hand} (Valor: {val})\n💀 Pierdes {bet} pts."
                await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())
            else:
                msg = f"🃏 **BLACKJACK**\n\nTu Mano: {p_hand} (Valor: {val})\nCrupier: {d_hand} [?]\n\n¿Qué deseas hacer?"
                await q.edit_message_text(msg, reply_markup=EmpireUI.blackjack_panel(bet))
                
        elif action == "stand":
            p_val = casino_engine.calculate_hand(p_hand)
            while casino_engine.calculate_hand(d_hand) < 17: d_hand.append(casino_engine.draw_card())
            d_val = casino_engine.calculate_hand(d_hand)
            
            msg = f"🃏 **BLACKJACK - RESULTADO**\n\nTu Mano: {p_hand} (Valor: {p_val})\nCrupier: {d_hand} (Valor: {d_val})\n\n"
            if d_val > 21 or p_val > d_val:
                win = bet * 2; await db.add_points(uid_str, win); u_data["stats"]["blackjack_wins"] += 1
                msg += f"🎉 **¡GANASTE!** +{win} pts."
                if u_data["stats"]["blackjack_wins"] >= 10 and "CARD_SHARK" not in u_data["achievements"]:
                    u_data["achievements"].append("CARD_SHARK")
                    await db.add_points(uid_str, 3000)
                    await q.message.reply_text("🏆 ¡LOGRO: Tiburón de Cartas! +3000 pts")
            elif p_val == d_val:
                await db.add_points(uid_str, bet); msg += "🤝 **EMPATE.** Recuperas tu apuesta."
            else: msg += "💀 **EL CRUPIER GANA.**"
            
            await db.save()
            await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())

    elif data.startswith("crash_cashout_"):
        parts = data.split("_")
        bet = int(parts[2])
        mult = float(parts[3])
        
        crash_point = context.user_data.pop("crash_point", -1) 
        
        if crash_point != -1 and mult <= crash_point:
            win = int(bet * mult)
            await db.add_points(uid_str, win)
            msg = f"✅ **¡CASH OUT EXITOSO!**\nSaltaste a `{mult}x`.\n🚀 Ganancia: +{win} pts."
            await q.edit_message_text(msg, reply_markup=EmpireUI.casino_panel())
        else:
            await q.answer("El cohete ya explotó o ya habías saltado.", show_alert=True)

    elif data.startswith("adm_") and uid == EmpireConfig.ADMIN_ID:
        if data.startswith("adm_list_"):
            page = int(data.split("_")[2])
            users = list(db.data["users"].items())
            start = page * 10
            end = start + 10
            msg = f"👥 **ESCLAVOS (Pág {page+1}):**\n"
            for sid, d in users[start:end]:
                msg += f"• `{sid}` | {d['name'][:10]} | Lvl:{d['level']} | {d['plan']}\n"
            kb = [[InlineKeyboardButton("⬅️ Ant", callback_data=f"adm_list_{max(0, page-1)}"), InlineKeyboardButton("Sig ➡️", callback_data=f"adm_list_{page+1}")]]
            kb.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
            await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
            
        elif data == "adm_bc":
            await q.message.reply_text("📢 Dicta mensaje para propagación general:"); context.user_data["state"] = "WAIT_BC"
        elif data == "adm_ban":
            await q.message.reply_text("🚫 ID a banear del sistema:"); context.user_data["state"] = "WAIT_BAN"
        elif data == "adm_unban":
            await q.message.reply_text("🔓 ID a desbanear:"); context.user_data["state"] = "WAIT_UNBAN"
        elif data == "adm_pts":
            await q.message.reply_text("💰 ID al que fondear:"); context.user_data["state"] = "WAIT_PTS_ID"
        elif data == "adm_cp":
            await q.message.reply_text("🎫 Escribe la clave del nuevo cupón (Max 10 chars):"); context.user_data["state"] = "WAIT_CP_CODE"
        elif data == "adm_edit_plan":
            await q.message.reply_text("🎭 ID del usuario para cambiar rango:"); context.user_data["state"] = "WAIT_PLAN_EDIT_ID"
        elif data == "adm_maint":
            db.data["system"]["maint_mode"] = not db.data["system"]["maint_mode"]
            await db.save()
            estado = "ACTIVADO" if db.data["system"]["maint_mode"] else "DESACTIVADO"
            await q.edit_message_text(f"⚠️ Mantenimiento {estado}.", reply_markup=EmpireUI.overlord_panel(0))
            audit_logger.log("MAINTENANCE_TOGGLED", user_id=uid, details={"state": estado})
        elif data == "adm_backup":
            await db.save()
            def _send_backup():
                 return open(EmpireConfig.DATABASE_PATH, 'rb')
            f_backup = await asyncio.to_thread(_send_backup)
            await context.bot.send_document(uid, f_backup, caption="💾 Core Vault V401 (Respaldo Manual)")

        elif data == "adm_giftcard":
            values = EmpireConfig.ECONOMY["GIFT_CARD_VALUES"]
            kb = [[InlineKeyboardButton(f"🎁 {v} pts", callback_data=f"adm_giftval_{v}")] for v in values]
            kb.append([InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")])
            await q.edit_message_text("🎁 **GENERAR TARJETA REGALO**\nElige el valor:", reply_markup=InlineKeyboardMarkup(kb))

        elif data.startswith("adm_giftval_") and uid == EmpireConfig.ADMIN_ID:
            val = int(data.split("_")[2])
            code = await db.generate_gift_card(val)
            await q.edit_message_text(f"✅ **TARJETA REGALO CREADA**\nCódigo: `{code}`\nValor: `{val} pts`\n\nCompártela con quien quieras.", reply_markup=EmpireUI.overlord_panel(), parse_mode="Markdown")

        elif data == "adm_analytics" and uid == EmpireConfig.ADMIN_ID:
            s = db.data["stats"]
            users_list = list(db.data["users"].values())
            free_c = sum(1 for u in users_list if u.get("plan") == "FREE")
            pro_c = sum(1 for u in users_list if u.get("plan") == "PRO")
            ultra_c = sum(1 for u in users_list if u.get("plan") == "ULTRA")
            god_c = sum(1 for u in users_list if u.get("plan") == "GOD")
            banned_c = sum(1 for u in users_list if u.get("is_banned"))
            today = str(datetime.date.today())
            active_today = sum(1 for u in users_list if u.get("daily_downloads", [0, ""])[1] == today)
            avg_dl = s["total_downloads"] / max(s["total_users"], 1)
            msg = (
                f"📊 **ANALÍTICAS AVANZADAS V401**\n\n"
                f"**Distribución de Planes:**\n"
                f"• FREE: `{free_c}` | PRO: `{pro_c}` | ULTRA: `{ultra_c}` | GOD: `{god_c}`\n"
                f"• Baneados: `{banned_c}`\n\n"
                f"**Engagement:**\n"
                f"• Activos hoy: `{active_today}`\n"
                f"• Promedio descargas/usuario: `{avg_dl:.1f}`\n\n"
                f"**Ingresos:**\n"
                f"• Stars totales: `{s.get('stars_revenue', 0)} ⭐️`\n"
                f"• Comisiones afiliados pagadas: `{s.get('affiliate_payouts', 0)} pts`\n"
                f"• Gift cards vendidas: `{s.get('gift_cards_sold', 0)}`\n"
                f"• Premios torneos: `{s.get('tournament_prize_pool', 0)} pts`\n\n"
                f"**Casino:**\n"
                f"• Total giros: `{s.get('casino_spins', 0)}`\n"
            )
            await q.edit_message_text(msg, reply_markup=EmpireUI.overlord_panel(), parse_mode="Markdown")

        elif data == "adm_vip_push" and uid == EmpireConfig.ADMIN_ID:
            await q.message.reply_text("📣 Escribe el mensaje de push exclusivo para usuarios VIP:")
            context.user_data["state"] = "WAIT_VIP_PUSH"

        elif data == "adm_apikeys" and uid == EmpireConfig.ADMIN_ID:
            keys = db.data.get("b2b_api_keys", {})
            msg = f"🔑 **API KEYS ACTIVAS ({len(keys)})**\n\n"
            for key_hash, owner_uid in list(keys.items())[:15]:
                owner_name = db.data["users"].get(owner_uid, {}).get("name", owner_uid)[:12]
                msg += f"• `{key_hash[:20]}...` → {owner_name}\n"
            await q.edit_message_text(msg, reply_markup=EmpireUI.overlord_panel(), parse_mode="Markdown")

    elif data.startswith("setplan_") and uid == EmpireConfig.ADMIN_ID:
        plan = data.split("_")[1]
        tid = context.user_data.get("target_user_id")
        if tid in db.data["users"]:
            db.data["users"][tid]["plan"] = plan
            expiry = datetime.datetime.now() + datetime.timedelta(days=365) if plan not in ["FREE", "GOD"] else None
            db.data["users"][tid]["plan_expiry"] = str(expiry) if expiry else None
            await db.save()
            await q.edit_message_text(f"✅ Rango de `{tid}` reescrito de forma forzada a **{plan}**.")
            try: await context.bot.send_message(tid, f"👁️ El Director Ishak ha modificado tu existencia al rango **{plan}**.")
            except: pass
        context.user_data["target_user_id"] = None

    elif data.startswith("tc_close_") and uid == EmpireConfig.ADMIN_ID:
        tid = data.replace("tc_close_", "")
        if tid in db.data["tickets"]:
            db.data["tickets"][tid]["status"] = "CLOSED"
            await db.save()
            user_ticket = db.data["tickets"][tid]["uid"]
            await q.edit_message_reply_markup(reply_markup=None)
            await q.message.reply_text(f"✅ Ticket {tid} clausurado.")
            try: await context.bot.send_message(user_ticket, f"✅ Tu ticket `{tid}` ha sido resuelto por el Alto Mando.")
            except: pass

    elif data.startswith("fmt_"):
        mode = data.split("_")[1]
        if mode == "back": return await q.edit_message_text("🎬 Selecciona formato:", reply_markup=EmpireUI.format_selector())
        context.user_data["active_fmt"] = mode
        
        if mode in ["MP3", "MP3U", "GIF", "VOICE", "VNOA"]: 
            await finalize_download(update, context)
        else: 
            await q.edit_message_text("🎥 Selecciona resolución óptica:", reply_markup=EmpireUI.quality_selector(u_data["plan"]))

    elif data.startswith("ql_"):
        context.user_data["active_qlty"] = data.split("_")[1]
        await finalize_download(update, context)

    elif data.startswith("lb_"):
        cat = data.split("_")[1]
        cat_names = {"points": "Puntos", "downloads": "Descargas", "referrals": "Referidos", "affiliate": "Afiliados"}
        top = await db.get_leaderboard(cat, 10)
        medals = ["🥇", "🥈", "🥉"] + ["4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        msg = f"🏆 **TOP 10 - {cat_names.get(cat, cat).upper()}**\n\n"
        for i, (name, username, val) in enumerate(top):
            uname_str = f"@{username}" if username else name
            msg += f"{medals[i]} `{val:,}` — {uname_str[:20]}\n"
        await q.edit_message_text(msg, reply_markup=EmpireUI.leaderboard_panel(), parse_mode="Markdown")

    elif data.startswith("tour_"):
        action = data.split("_")[1]
        t = db.data["system"].get("tournament", {})
        
        if action == "rank":
            parts_t = t.get("participants", {})
            if not parts_t:
                await q.answer("No hay participantes aún.", show_alert=True)
            else:
                sorted_p = sorted(parts_t.items(), key=lambda x: x[1], reverse=True)[:10]
                msg = "🏟️ **CLASIFICACIÓN TORNEO**\n\n"
                medals = ["🥇","🥈","🥉"] + ["4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
                for i, (puid, score) in enumerate(sorted_p):
                    pname = db.data["users"].get(puid, {}).get("name", puid)[:15]
                    msg += f"{medals[i]} `{score}` pts — {pname}\n"
                await q.edit_message_text(msg, reply_markup=EmpireUI.tournament_panel(), parse_mode="Markdown")
        
        elif action == "prizes":
            pool = t.get("prize_pool", 0)
            msg = (f"🏆 **PREMIOS TORNEO**\n\n"
                   f"Bote total: `{pool} pts`\n\n"
                   f"🥇 1er lugar: `{int(pool*0.5)} pts`\n"
                   f"🥈 2do lugar: `{int(pool*0.3)} pts`\n"
                   f"🥉 3er lugar: `{int(pool*0.2)} pts`\n\n"
                   f"*Por cada descarga durante el torneo acumulas puntos en el ranking.*")
            await q.edit_message_text(msg, reply_markup=EmpireUI.tournament_panel(), parse_mode="Markdown")

        elif action == "start" and uid == EmpireConfig.ADMIN_ID:
            hours = int(data.split("_")[2])
            await db.start_tournament(duration_hours=hours, prize_pool_seed=5000)
            await q.edit_message_text(f"✅ ¡Torneo iniciado! Duración: {hours}h. Bote inicial: 5,000 pts.\n\nSe notificará a todos los usuarios.", reply_markup=EmpireUI.admin_tournament_panel())
            for sid in list(db.data["users"].keys()):
                try:
                    await context.bot.send_message(sid, f"🏟️ **¡TORNEO IMPERIAL INICIADO!**\n⏰ Duración: {hours} horas.\nCada descarga suma al ranking.\nPremios: hasta {5000 * int(hours // 24 + 1)} pts para el 1er lugar.\n¡Empieza a descargar ahora!")
                    await asyncio.sleep(0.04)
                except: pass

        elif action == "end" and uid == EmpireConfig.ADMIN_ID:
            winners = await db.finalize_tournament()
            if winners:
                msg = "🏁 **TORNEO FINALIZADO**\n\nGanadores:\n"
                for i, (wuid, score, prize) in enumerate(winners):
                    wname = db.data["users"].get(wuid, {}).get("name", wuid)[:15]
                    medals = ["🥇","🥈","🥉"]
                    msg += f"{medals[i]} {wname} — {score} pts → +{prize} pts\n"
                await q.edit_message_text(msg, reply_markup=EmpireUI.admin_tournament_panel())
                for wuid, score, prize in winners:
                    try:
                        await context.bot.send_message(wuid, f"🏆 ¡Felicidades! Has ganado el torneo. Premio: **+{prize} pts**.")
                    except: pass
            else:
                await q.edit_message_text("❌ Torneo finalizado sin participantes.", reply_markup=EmpireUI.admin_tournament_panel())

    elif data.startswith("vip_"):
        vip_action = data.split("_")[1]
        vip_exp = u_data.get("vip_expiry")
        is_vip = vip_exp and datetime.datetime.now() < datetime.datetime.fromisoformat(vip_exp)
        if not is_vip and vip_action != "join":
            await q.answer("❌ Acceso VIP requerido.", show_alert=True)
        elif vip_action == "stats":
            user_rank = sorted(db.data["users"].values(), key=lambda x: x.get("points", 0), reverse=True)
            rank_pos = next((i+1 for i, u in enumerate(user_rank) if str(u.get("id")) == uid_str), "?")
            msg = (f"📊 **TUS ESTADÍSTICAS VIP**\n\n"
                   f"Posición global: `#{rank_pos}`\n"
                   f"Total descargas: `{u_data.get('total_downloads', 0)}`\n"
                   f"Ganancias afiliados: `{u_data.get('affiliate_earnings', 0)} pts`\n"
                   f"Stars gastadas: `{u_data.get('total_spent_stars', 0)}`\n"
                   f"Racha máxima registrada: `{u_data.get('streak', 0)} días`")
            await q.answer()
            await q.message.reply_text(msg, parse_mode="Markdown")
        elif vip_action == "gift":
            values = EmpireConfig.ECONOMY["GIFT_CARD_VALUES"]
            kb = [[InlineKeyboardButton(f"🎁 {v} pts ({v//50} ⭐️)", callback_data=f"vip_giftbuy_{v}")] for v in values]
            kb.append([InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")])
            await q.edit_message_text("🎁 **COMPRAR TARJETA REGALO**\nElige el valor:", reply_markup=InlineKeyboardMarkup(kb))
        elif vip_action == "giftbuy":
            val = int(data.split("_")[2])
            cost_stars = val // 50
            code = await db.generate_gift_card(val)
            await q.edit_message_text(f"✅ Tarjeta regalo generada:\nCódigo: `{code}`\nValor: `{val} pts`\n\nComparte este código con quien quieras.", parse_mode="Markdown")
        elif vip_action == "unlimited":
            if u_data.get("plan") not in ["ULTRA", "GOD"]:
                u_data["daily_downloads"] = [0, str(datetime.date.today())]
                await db.save()
                await q.answer("✅ ¡Límite diario reseteado! Puedes descargar de nuevo.", show_alert=True)
            else:
                await q.answer("Ya tienes descargas ilimitadas con tu plan.", show_alert=True)

    elif data == "u_close":
        try: await q.message.delete()
        except: pass

async def gift_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid_str = str(user.id)
    u_data, _ = await db.get_user(user)
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "🎁 **SISTEMA DE TARJETAS REGALO**\n\n"
            "Uso:\n"
            "`/gift <código>` — canjea tu propia tarjeta\n"
            "`/gift <código> <ID_usuario>` — regala el código a otro usuario\n\n"
            "Compra tarjetas en ⭐️ Tienda Oficial.", parse_mode="Markdown"
        )
        return
    
    code = context.args[0].strip().upper()
    
    if len(context.args) >= 2:
        target_id = context.args[1].strip().replace("@", "")
        target_uid = None
        for uid_k, u in db.data["users"].items():
            if str(u.get("id")) == target_id or u.get("username", "").lower() == target_id.lower():
                target_uid = uid_k
                break
        
        if not target_uid:
            await update.message.reply_text("❌ Usuario no encontrado.")
            return
        
        success, msg = await db.redeem_gift_card(target_uid, code)
        if success:
            target_name = db.data["users"][target_uid].get("name", "Usuario")
            await update.message.reply_text(f"🎁 ¡Tarjeta enviada a **{target_name}**!\n{msg}", parse_mode="Markdown")
            try:
                await context.bot.send_message(target_uid, f"🎁 **¡Has recibido un regalo de {user.first_name}!**\n{msg}", parse_mode="Markdown")
            except: pass
        else:
            await update.message.reply_text(f"❌ {msg}")
    else:
        success, msg = await db.redeem_gift_card(uid_str, code)
        await update.message.reply_text(msg, parse_mode="Markdown")

async def coupon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid_str = str(user.id)
    u_data, _ = await db.get_user(user)
    
    if not context.args:
        await update.message.reply_text("Uso: `/coupon CÓDIGO`", parse_mode="Markdown")
        return
    
    code = context.args[0].strip().upper()
    if code in db.data["coupons"]:
        coupon_data = db.data["coupons"][code]
        if isinstance(coupon_data, dict) and coupon_data.get("type") == "gift_card":
            success, msg = await db.redeem_gift_card(uid_str, code)
            await update.message.reply_text(msg, parse_mode="Markdown")
        elif isinstance(coupon_data, str):
            plan = coupon_data
            if plan in EmpireConfig.PLANS:
                u_data["plan"] = plan
                expiry = datetime.datetime.now() + datetime.timedelta(days=30)
                u_data["plan_expiry"] = str(expiry) if plan not in ["FREE", "GOD"] else None
                del db.data["coupons"][code]
                await db.save()
                await update.message.reply_text(f"✅ ¡Cupón **{code}** canjeado! Plan **{plan}** activo 30 días.", parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Cupón con plan inválido.")
        else:
            await update.message.reply_text("❌ Tipo de cupón desconocido.")
    else:
        await update.message.reply_text("❌ Código incorrecto o ya usado.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid_str = str(user.id)
    u_data, _ = await db.get_user(user)
    
    all_users = sorted(db.data["users"].values(), key=lambda x: x.get("points", 0), reverse=True)
    rank = next((i+1 for i, u in enumerate(all_users) if str(u.get("id")) == uid_str), "?")
    
    tier2_count = len(u_data.get("referrals_tier2", []))
    
    msg = (
        f"📊 **ESTADÍSTICAS DETALLADAS V401**\n\n"
        f"**General:**\n"
        f"• Ranking global: `#{rank}`\n"
        f"• Nivel: `{u_data['level']}` (XP: `{u_data['xp']}`)\n"
        f"• Puntos totales: `{u_data['points']:,}`\n\n"
        f"**Descargas:**\n"
        f"• Hoy: `{u_data['daily_downloads'][0]}`\n"
        f"• Total histórico: `{u_data.get('total_downloads', 0):,}`\n\n"
        f"**Afiliados:**\n"
        f"• Referidos Tier-1: `{u_data.get('referrals', 0)}`\n"
        f"• Referidos Tier-2: `{tier2_count}`\n"
        f"• Ganancias afiliado: `{u_data.get('affiliate_earnings', 0):,} pts`\n\n"
        f"**Engagement:**\n"
        f"• Racha actual: `{u_data.get('streak', 0)} días 🔥`\n"
        f"• Casino jugadas: `{u_data['stats'].get('casino_played', 0)}`\n"
        f"• Stars gastadas: `{u_data.get('total_spent_stars', 0)}`\n"
        f"• Logros: `{len(u_data.get('achievements', []))} / {len(EmpireConfig.ACHIEVEMENTS)}`\n"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def finalize_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    uid_str = str(uid)
    url = context.user_data.get("active_url")
    fmt = context.user_data.get("active_fmt")
    qlty = context.user_data.get("active_qlty", "720p")
    u_data, _ = await db.get_user(q.from_user)

    plan_info = EmpireConfig.PLANS[u_data["plan"]]
    max_size = plan_info["max_file_mb"]

    msg = await q.edit_message_text(f"⚡ **MOTOR V400 INICIADO...**\n`[{fmt} | {qlty}]`")
    job_id = f"job_{uid_str}_{uuid.uuid4().hex[:6]}"
    progress_tracker.add_job(job_id, msg)
    
    try:
        success, path, title, duration, f_size, err_msg = await asyncio.wait_for(
            MediaEngine.run(url, fmt, qlty, uid_str, max_size, job_id, u_data['settings']),
            timeout=600.0
        )
        
        if job_id in progress_tracker.active_jobs:
            progress_tracker.active_jobs[job_id]['finished'] = True
            
        if not success:
            await msg.edit_text(f"❌ **ERROR DEL NÚCLEO EXTRACCIÓN:**\n{err_msg}")
            return
        
        size_mb = f_size / (1024 * 1024)
        if size_mb > max_size:
            if os.path.exists(path):
                await asyncio.to_thread(os.remove, path)
            await msg.edit_text(f"❌ Archivo excede límite de {max_size}MB de tu rango {u_data['plan']}.")
            return

        await msg.edit_text("📤 **SUBIENDO AL SATÉLITE CORPORATIVO...**", parse_mode="Markdown")
        
        def _get_file_reader():
            return open(path, 'rb')
            
        with await asyncio.to_thread(_get_file_reader) as f:
            wm_text = f"\n©️ Marca de Agua: `{u_data['settings']['watermark']}`" if u_data['settings'].get('watermark') else ""
            veo3_note = "\n🇪🇸 *Regla Directiva Absoluta: Español (Veo3).* " if "veo3" in url.lower() else ""
            cap = (
                f"✅ **{title[:50]}...**\n"
                f"⏱️ `{str(datetime.timedelta(seconds=duration))}` | 💾 `{size_mb:.1f} MB`{wm_text}{veo3_note}\n"
            )
            
            if u_data['settings'].get('send_as_doc'):
                await context.bot.send_document(uid, f, caption=cap, parse_mode="Markdown", read_timeout=300)
            elif fmt in ["MP3", "MP3U"]: 
                await context.bot.send_audio(uid, f, caption=cap, parse_mode="Markdown", read_timeout=120)
            elif fmt == "VOICE":
                await context.bot.send_voice(uid, f, caption=cap, parse_mode="Markdown", read_timeout=120)
            elif fmt == "GIF":
                await context.bot.send_animation(uid, f, caption=cap, parse_mode="Markdown", read_timeout=300)
            else: 
                await context.bot.send_video(uid, f, caption=cap, parse_mode="Markdown", read_timeout=300, supports_streaming=True)

        u_data["daily_downloads"][0] += 1
        u_data["total_downloads"] = u_data.get("total_downloads", 0) + 1
        db.data["stats"]["total_downloads"] += 1
        await db.save()
        await db.update_bounty(uid_str, "dl_3", 1)
        await db.add_xp(uid_str, EmpireConfig.ECONOMY["XP_PER_DOWNLOAD"])
        
        asyncio.create_task(db.add_tournament_score(uid_str, 1))
        
        total_dl = u_data.get("total_downloads", 0)
        if total_dl == 1 and "FIRST_BLOOD" not in u_data.get("achievements", []):
            u_data.setdefault("achievements", []).append("FIRST_BLOOD")
            u_data["points"] += EmpireConfig.ACHIEVEMENTS["FIRST_BLOOD"]["reward"]
            try: await context.bot.send_message(uid, "🏆 ¡LOGRO: Primera Sangre! +500 pts")
            except: pass
        if total_dl >= 100 and "CENTURION" not in u_data.get("achievements", []):
            u_data.setdefault("achievements", []).append("CENTURION")
            u_data["points"] += EmpireConfig.ACHIEVEMENTS["CENTURION"]["reward"]
            try: await context.bot.send_message(uid, "🏆 ¡LOGRO: Centurión! 100 descargas. +5000 pts")
            except: pass
        if total_dl >= 500 and "DOWNLOADER_500" not in u_data.get("achievements", []):
            u_data.setdefault("achievements", []).append("DOWNLOADER_500")
            u_data["points"] += EmpireConfig.ACHIEVEMENTS["DOWNLOADER_500"]["reward"]
            try: await context.bot.send_message(uid, "🏆 ¡LOGRO LEGENDARIO: Extractor 500! +25,000 pts")
            except: pass
        await db.save()
        
        if os.path.exists(path):
            await asyncio.to_thread(os.remove, path)
            
        try: await msg.delete()
        except: pass

    except asyncio.TimeoutError:
        if job_id in progress_tracker.active_jobs: progress_tracker.active_jobs[job_id]['finished'] = True
        logger.error(f"⌛ Timeout B2B superado para job {job_id} por UID: {uid}.")
        await msg.edit_text("❌ **ERROR DE SISTEMA:**\nServidor de Extracción Saturado. La operación superó el límite de tiempo.")
        alert_system.track_error()
        
    except Exception as e:
        if job_id in progress_tracker.active_jobs: progress_tracker.active_jobs[job_id]['finished'] = True
        logger.error(f"Fallo general asíncrono UID {uid}: {e}")
        await msg.edit_text(f"❌ **ERROR DE SISTEMA:**\nFallo crítico en la matriz B2B.")
        alert_system.track_error()
    
    finally:
        gc.collect()
        logger.info(f"🧹 [MEMORY PURGE] Garbage Collector V400 ha liberado memoria para el job {job_id}.")
