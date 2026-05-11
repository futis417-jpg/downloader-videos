import threading
import asyncio
import os

# Ejecutar el bootstrap primero para asegurar paquetes instalados antes de los imports
import bootstrap
bootstrap.bootstrap_packages()

from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, PreCheckoutQueryHandler, filters
)

from config import EmpireConfig
from logger_core import logger
from database_core import db
from web_server import run_api
from engines import progress_tracker
from background_tasks import self_healing_core_task, buffer_cleanup_task, crypto_fluctuation_task
from bot_handlers import (
    start_handler, message_dispatcher, callback_handler, 
    precheckout_callback, successful_payment_callback,
    gift_command, coupon_command, stats_command
)

def main():
    """
    Función principal de arranque del Leviathan V400.
    Inicia los hilos web, carga la base de datos asíncrona, agenda tareas de fondo y pone en marcha el Telegram Bot.
    """
    
    # 1. Arrancar la API Web B2B en segundo plano
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    logger.info("🌐 Web API SaaS B2B iniciada en segundo plano.")

    # 2. Construir la aplicación de Telegram
    application = ApplicationBuilder().token(EmpireConfig.TOKEN).build()

    # 3. Registrar los controladores (Handlers) y comandos solucionados
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("gift", gift_command))
    application.add_handler(CommandHandler("coupon", coupon_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # 4. Iniciar las tareas asíncronas ANTES de arrancar el polling
    async def setup_tasks(app):
        # Creamos las tareas dentro del contexto de la aplicación
        asyncio.create_task(db.backup_job())
        asyncio.create_task(self_healing_core_task())
        asyncio.create_task(buffer_cleanup_task())
        asyncio.create_task(crypto_fluctuation_task())
        asyncio.create_task(progress_tracker.update_messages_loop())
        logger.info("⚙️ Tareas asíncronas de mantenimiento programadas.")

    # 5. Ejecutar el Polling para escuchar mensajes
    logger.info("🚀 SISTEMA LEVIATHAN V400 EN LÍNEA. Iniciando polling...")
    
    application.post_init = setup_tasks
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
