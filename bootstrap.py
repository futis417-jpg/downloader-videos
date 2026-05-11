import os
import sys
import subprocess

def bootstrap_packages():
    """
    Garantiza la presencia del arsenal masivo de librerías para B2B.
    BUG FIX: Sale del proceso si la instalación falla. Fuerza actualización de yt-dlp.
    """
    packages = [
        'python-telegram-bot', 'yt-dlp', 'flask', 'flask-cors', 'requests', 
        'psutil', 'Pillow', 'aiohttp', 'cryptography', 'qrcode', 'python-dotenv', 'gTTS',
        'pydantic', 'pydantic-settings', 'sentry-sdk', 'cachetools'
    ]
    for p in packages:
        try:
            __import__(p.replace('-', '_'))
            if p == 'yt-dlp':
                subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp", "--quiet"])
        except ImportError:
            print(f"📦 [BOOTSTRAP] Instalando componente crítico B2B: {p}...")
            if subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", p, "--quiet"]) != 0:
                print(f"❌ FALLO CRÍTICO: No se pudo instalar el módulo {p}. Abortando despliegue.")
                sys.exit(1)
