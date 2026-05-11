import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import EmpireConfig

class EmpireUI:
    @staticmethod
    def main_keyboard(u_data):
        if u_data.get("is_banned"): return ReplyKeyboardMarkup([[KeyboardButton("🎧 SOPORTE")]], resize_keyboard=True)
        
        is_admin = u_data['id'] == EmpireConfig.ADMIN_ID
        is_god = u_data['plan'] == 'GOD'
        is_vip = u_data.get('vip_expiry') and datetime.datetime.now() < datetime.datetime.fromisoformat(u_data['vip_expiry'])
        
        btns = [
            [KeyboardButton("📥 EXTRACCIÓN"), KeyboardButton("👤 PERFIL")],
            [KeyboardButton("⭐️ TIENDA OFICIAL (STARS)"), KeyboardButton("💎 MERCADO NEGRO")],
            [KeyboardButton("⚙️ AJUSTES PRO"), KeyboardButton("🎰 CASINO IMPERIAL")],
            [KeyboardButton("🛠️ CAJA DE HERRAMIENTAS"), KeyboardButton("🛡️ FACCIONES")],
            [KeyboardButton("🎁 TRIBUTO"), KeyboardButton("🎧 SOPORTE")],
            [KeyboardButton("🎮 MISIONES Y LOGROS"), KeyboardButton("🏆 RANKING GLOBAL")],
            [KeyboardButton("🎫 CANJEAR CÓDIGO")],
        ]
        
        if is_vip:
            btns.insert(2, [KeyboardButton("🥂 SALA VIP")])
        
        if is_god:
            btns.append([KeyboardButton("🏢 ÁREA B2B")])
            
        if is_admin:
            btns.append([KeyboardButton("👑 PANEL OVERLORD 👑"), KeyboardButton("🌐 DATOS MATRIZ")])
            btns.append([KeyboardButton("🏟️ TORNEO ADMIN")])
            
        return ReplyKeyboardMarkup(btns, resize_keyboard=True)

    @staticmethod
    def overlord_panel(page=0):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 LISTA ESCLAVOS", callback_data=f"adm_list_{page}"), 
             InlineKeyboardButton("📢 TRANSMISIÓN", callback_data="adm_bc")],
            [InlineKeyboardButton("🚫 BANEAR", callback_data="adm_ban"), 
             InlineKeyboardButton("🔓 DESBANEAR", callback_data="adm_unban")],
            [InlineKeyboardButton("💰 DAR FONDOS", callback_data="adm_pts"), 
             InlineKeyboardButton("🎫 CREAR CUPÓN", callback_data="adm_cp")],
            [InlineKeyboardButton("🎭 EDITAR RANGO", callback_data="adm_edit_plan"), 
             InlineKeyboardButton("📂 TICKETS", callback_data="adm_tickets")],
            [InlineKeyboardButton("⚠️ MANTENIMIENTO", callback_data="adm_maint"), 
             InlineKeyboardButton("💾 BACKUP DB", callback_data="adm_backup")],
            [InlineKeyboardButton("🎁 GENERAR GIFT CARD", callback_data="adm_giftcard"),
             InlineKeyboardButton("📊 ANALÍTICAS AVANZADAS", callback_data="adm_analytics")],
            [InlineKeyboardButton("📣 PUSH MASIVO VIP", callback_data="adm_vip_push"),
             InlineKeyboardButton("🔑 VER API KEYS", callback_data="adm_apikeys")],
            [InlineKeyboardButton("❌ CERRAR TERMINAL", callback_data="u_close")]
        ])

    @staticmethod
    def factions_panel(has_faction):
        if has_faction:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Info de Facción", callback_data="fac_info"),
                 InlineKeyboardButton("💰 Donar a la Bóveda", callback_data="fac_donate")],
                [InlineKeyboardButton("⭐ Subir Nivel Clan (10k pts)", callback_data="fac_upgrade")],
                [InlineKeyboardButton("🚪 Abandonar", callback_data="fac_leave")],
                [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
            ])
        else:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("🛡️ Crear Facción (Req. Ticket)", callback_data="fac_create")],
                [InlineKeyboardButton("🤝 Unirse a Facción", callback_data="fac_join")],
                [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
            ])

    @staticmethod
    def format_selector():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 VIDEO (MP4)", callback_data="fmt_MP4"),
             InlineKeyboardButton("🎵 AUDIO (MP3)", callback_data="fmt_MP3")],
            [InlineKeyboardButton("🔥 MP3 ULTRA (320kbps)", callback_data="fmt_MP3U"),
             InlineKeyboardButton("🎞️ VIDEO SIN AUDIO", callback_data="fmt_VNOA")],
            [InlineKeyboardButton("🎙️ NOTA DE VOZ (OGG)", callback_data="fmt_VOICE"),
             InlineKeyboardButton("🎞️ ANIMACIÓN (GIF)", callback_data="fmt_GIF")],
            [InlineKeyboardButton("❌ ABORTAR", callback_data="u_close")]
        ])

    @staticmethod
    def quality_selector(plan_id):
        qualities = EmpireConfig.PLANS.get(plan_id, EmpireConfig.PLANS["FREE"])["resolutions"]
        rows = []
        for i in range(0, len(qualities), 2):
            rows.append([InlineKeyboardButton(f"🎥 {q}", callback_data=f"ql_{q}") for q in qualities[i:i+2]])
        rows.append([InlineKeyboardButton("⬅️ ATRÁS", callback_data="fmt_back")])
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def stars_shop():
        rows = []
        for k, v in EmpireConfig.STARS_PACKAGES.items():
            rows.append([InlineKeyboardButton(f"{v['name']} - {v['stars']} ⭐️", callback_data=f"stars_{k}")])
        rows.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def shop_panel():
        rows = []
        for k, v in EmpireConfig.SHOP_ITEMS.items():
            rows.append([InlineKeyboardButton(f"🛒 {v['name']} ({v['price']} pts)", callback_data=f"buy_item_{k}")])
        rows.append([
            InlineKeyboardButton("📈 COMPRAR IshakCoin (500 pts)", callback_data="crypto_buy"),
            InlineKeyboardButton("📉 VENDER TODO", callback_data="crypto_sell")
        ])
        rows.append([InlineKeyboardButton("❌ CERRAR", callback_data="u_close")])
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def settings_panel(settings):
        wm_status = settings.get('watermark', None) or "Ninguna"
        transcribe = "✅" if settings.get('auto_transcribe') else "❌"
        ghost = "✅" if settings.get('ghost_mode') else "❌"
        doc_mode = "✅" if settings.get('send_as_doc') else "❌"
        theme = settings.get('theme', 'dark').capitalize()
        lang = settings.get('language', 'es').upper()
        notifications = "✅" if settings.get('notifications_enabled', True) else "❌"
        
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🖋️ Marca de Agua: {wm_status}", callback_data="set_watermark")],
            [InlineKeyboardButton(f"📝 Auto-Transcribir IA: {transcribe}", callback_data="set_transcribe")],
            [InlineKeyboardButton(f"👻 Modo Fantasma: {ghost}", callback_data="set_ghost")],
            [InlineKeyboardButton(f"📄 Enviar como Documento: {doc_mode}", callback_data="set_doc")],
            [InlineKeyboardButton(f"🎨 Tema: {theme}", callback_data="set_theme")],
            [InlineKeyboardButton(f"🌐 Idioma: {lang}", callback_data="set_lang")],
            [InlineKeyboardButton(f"🔔 Notificaciones Push: {notifications}", callback_data="set_notif")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def utils_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🗣️ Text to Speech Real", callback_data="util_tts_req"),
             InlineKeyboardButton("📡 Ping Test (Sist. Operativo)", callback_data="util_ping")],
            [InlineKeyboardButton("🔳 Generador QR Real", callback_data="util_qr_req"),
             InlineKeyboardButton("🖼️ Extraer Miniatura", callback_data="util_thumb")],
            [InlineKeyboardButton("📜 Codificar a Base64", callback_data="util_b64enc_req"),
             InlineKeyboardButton("🔓 Decodificar Base64", callback_data="util_b64dec_req")],
            [InlineKeyboardButton("📊 Info Metadatos", callback_data="util_meta")],
            [InlineKeyboardButton("🔍 Búsqueda Avanzada", callback_data="util_search")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def b2b_panel(api_key):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Generar/Regenerar API Key", callback_data="b2b_gen_key")],
            [InlineKeyboardButton(f"Clave Hasheada en DB", callback_data="dummy_btn") if api_key else InlineKeyboardButton("Sin clave activa", callback_data="dummy_btn")],
            [InlineKeyboardButton("📖 Ver Documentación API", callback_data="b2b_docs")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def casino_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 Slots (100 pts)", callback_data="casino_slots")],
            [InlineKeyboardButton("🎡 Ruleta (250 pts)", callback_data="casino_roulette")],
            [InlineKeyboardButton("🃏 Blackjack (500 pts)", callback_data="casino_bj_init")],
            [InlineKeyboardButton("📈 Cripto Crash (1000 pts)", callback_data="casino_crash_init")],
            [InlineKeyboardButton("❌ SALIR", callback_data="u_close")]
        ])
        
    @staticmethod
    def blackjack_panel(bet):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🃏 Pedir Carta", callback_data=f"bj_hit_{bet}"),
             InlineKeyboardButton("🛑 Plantarse", callback_data=f"bj_stand_{bet}")],
        ])

    @staticmethod
    def crash_panel(bet, mult=1.00):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🚀 SALTAR AHORA ({mult:.2f}x)", callback_data=f"crash_cashout_{bet}_{mult:.2f}")]
        ])

    @staticmethod
    def plan_selector_admin():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🆓 FREE", callback_data="setplan_FREE"),
             InlineKeyboardButton("💎 PRO", callback_data="setplan_PRO")],
            [InlineKeyboardButton("🔥 ULTRA", callback_data="setplan_ULTRA"),
             InlineKeyboardButton("👁️ GOD", callback_data="setplan_GOD")],
            [InlineKeyboardButton("❌ CANCELAR", callback_data="u_close")]
        ])

    @staticmethod
    def ticket_panel(ticket_id):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔒 CERRAR TICKET", callback_data=f"tc_close_{ticket_id}")]
        ])

    @staticmethod
    def leaderboard_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Top Puntos", callback_data="lb_points"),
             InlineKeyboardButton("📥 Top Descargas", callback_data="lb_downloads")],
            [InlineKeyboardButton("👥 Top Referidos", callback_data="lb_referrals"),
             InlineKeyboardButton("💸 Top Afiliados", callback_data="lb_affiliate")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def tournament_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🏟️ Ver Clasificación", callback_data="tour_rank")],
            [InlineKeyboardButton("🏆 Ver Premios", callback_data="tour_prizes")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def admin_tournament_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Iniciar Torneo 24h", callback_data="tour_start_24"),
             InlineKeyboardButton("🚀 Iniciar Torneo 48h", callback_data="tour_start_48")],
            [InlineKeyboardButton("🏁 Finalizar Torneo", callback_data="tour_end")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def vip_lounge_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Estadísticas VIP", callback_data="vip_stats"),
             InlineKeyboardButton("🎁 Generar Tarjeta Regalo", callback_data="vip_gift_gen")],
            [InlineKeyboardButton("👑 Descargas Ilimitadas Hoy", callback_data="vip_unlimited")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])

    @staticmethod
    def search_panel():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Por plataforma", callback_data="search_platform"),
             InlineKeyboardButton("⏱️ Por duración", callback_data="search_duration")],
            [InlineKeyboardButton("📅 Recientes", callback_data="search_recent"),
             InlineKeyboardButton("📈 Más vistos", callback_data="search_popular")],
            [InlineKeyboardButton("❌ CERRAR", callback_data="u_close")]
        ])
