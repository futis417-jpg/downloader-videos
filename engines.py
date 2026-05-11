import os
import time
import re
import asyncio
import uuid
import datetime
import subprocess
import platform
import random
import base64
import gc
from typing import List, Tuple, Optional
import yt_dlp
from gtts import gTTS
import qrcode

from config import EmpireConfig
from logger_core import logger, alert_system

GLOBAL_METADATA_CACHE = {}

class DownloadProgressTracker:
    def __init__(self):
        self.active_jobs = {}
    
    def add_job(self, job_id, message_obj):
        self.active_jobs[job_id] = {
            'msg': message_obj, 'status': 'Iniciando', 'percent': 0,
            'speed': '0B/s', 'eta': 'Calculando...', 'last_update': time.time(),
            'finished': False
        }

    async def update_messages_loop(self):
        while True:
            await asyncio.sleep(3.5)
            now = time.time()
            for job_id, data in list(self.active_jobs.items()):
                if data['finished'] or (now - data['last_update'] > 900):
                    if (now - data['last_update'] > 900) and not data['finished']:
                        logger.warning(f"🧹 [MEMORY PURGE] Job atascado eliminado: {job_id}")
                    del self.active_jobs[job_id]
                    continue
                
                if now - data['last_update'] >= 3.5:
                    try:
                        bar_length = 15
                        filled = int(bar_length * data['percent'] / 100)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        text = (
                            f"⚡ **SINTETIZANDO DATOS (V400 LEVIATHAN)...**\n"
                            f"Progreso: `{bar}` {data['percent']:.1f}%\n"
                            f"Velocidad: `{data['speed']}` | ETA: `{data['eta']}`"
                        )
                        if data.get('last_text') != text:
                            await data['msg'].edit_text(text, parse_mode="Markdown")
                            data['last_text'] = text
                            data['last_update'] = now
                    except: pass

progress_tracker = DownloadProgressTracker()

class MediaEngine:
    @staticmethod
    async def get_thumbnail(url: str, uid: str) -> Optional[str]:
        try:
            def _get():
                with yt_dlp.YoutubeDL({'quiet': True, 'nocheckcertificate': True, 'no_warnings': True}) as ydl:
                    return ydl.extract_info(url, download=False).get('thumbnail')
            return await asyncio.to_thread(_get)
        except: return None

    @staticmethod
    async def get_metadata(url: str) -> dict:
        if url in GLOBAL_METADATA_CACHE:
            return GLOBAL_METADATA_CACHE[url]["info"]
            
        try:
            def _get():
                opts = {
                    'quiet': True, 'no_warnings': True, 'nocheckcertificate': True,
                    'socket_timeout': 5, 'extract_flat': 'in_playlist'
                }
                with yt_dlp.YoutubeDL(opts) as ydl:
                    i = ydl.extract_info(url, download=False)
                    if not i: return {}
                    res = {"title": i.get("title"), "duration": i.get("duration"), "uploader": i.get("uploader"), "view_count": i.get("view_count")}
                    GLOBAL_METADATA_CACHE[url] = {"info": res, "timestamp": time.time()}
                    return res
            return await asyncio.to_thread(_get)
        except: return {}

    @staticmethod
    async def run(url: str, mode: str, quality: str, uid: str, max_size_mb: int, job_id: str, settings: dict):
        output_template = os.path.join(EmpireConfig.BUFFER_DIR, f"{job_id}.%(ext)s")
        
        def yt_dlp_hook(d):
            if d['status'] == 'downloading':
                job = progress_tracker.active_jobs.get(job_id)
                if job:
                    try:
                        p_str = d.get('_percent_str', '0.0%').replace('%', '').strip()
                        job['percent'] = float(p_str)
                        job['speed'] = d.get('_speed_str', '0B/s')
                        job['eta'] = d.get('_eta_str', 'Desconocido')
                    except: pass

        ydl_opts = {
            'outtmpl': output_template, 
            'quiet': True, 
            'no_warnings': True,
            'noplaylist': True, 
            'max_filesize': max_size_mb * 1024 * 1024,
            'nocheckcertificate': True, 
            'progress_hooks': [yt_dlp_hook],
            'socket_timeout': 10,
            'extract_flat': 'in_playlist',
            'extractor_args': {'youtube': ['player_client=ios,android,web']}
        }

        if "veo3" in url.lower():
            match = re.search(r'veo3.*?/([a-zA-Z0-9_-]+)', url)
            vid_id = match.group(1) if match else "Desconocido"
            logger.info(f"🚨 [VEO3 DEFENSE] Veo3 detectado - Video ID: {vid_id} (UID: {uid}). Validando integridad corporativa.")
            
            if mode == "VNOA":
                logger.warning(f"🛡️ [VEO3 DEFENSE] Bypass bloqueado para VNOA (sin audio). Restaurando a MP4 con audio en Español.")
                mode = "MP4"

            ydl_opts['writesubtitles'] = True
            ydl_opts['subtitleslangs'] = ['es', 'spa']
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            ydl_opts['format_sort'] = ['lang:es', 'lang:spa', 'res:1080', 'ext:mp4:m4a']
        else:
            if mode == "MP3":
                ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]})
            elif mode == "MP3U":
                ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]})
            elif mode == "VOICE":
                ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'vorbis', 'preferredquality': '192'}]})
            elif mode == "VNOA":
                h = quality.replace("p", "") if quality != "Original" else "1080"
                ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]/bestvideo/best' 
            elif mode == "GIF":
                h = quality.replace("p", "") if quality != "Original" else "720"
                ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]/best'
            else: 
                h = quality.replace("p", "") if quality != "Original" else "2160"
                ydl_opts['format'] = f'bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        def _execute():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        return False, None, None, 0, 0, "No se pudo extraer información del archivo."
                        
                    file_path = ydl.prepare_filename(info)
                    
                    if mode in ["MP3", "MP3U"]: file_path = os.path.splitext(file_path)[0] + ".mp3"
                    elif mode == "VOICE": file_path = os.path.splitext(file_path)[0] + ".ogg"
                    
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    return True, file_path, info.get('title', 'Media_Enterprise_V400'), info.get('duration', 0), file_size, ""
            except yt_dlp.utils.DownloadError as e:
                gc.collect() 
                err_msg = str(e).lower()
                user_msg = f"Excepción en el satélite de extracción B2B.\nDetalles técnicos: `{str(e)}`"
                if "copyright" in err_msg:
                    user_msg = "Contenido bloqueado por derechos de autor (Copyright) en el país de origen."
                elif "too large" in err_msg or "filesize" in err_msg:
                    user_msg = f"El archivo original supera tu límite de {max_size_mb}MB permitido en tu plan."
                elif "sign in" in err_msg or "members only" in err_msg or "private" in err_msg:
                    user_msg = "El enlace es privado, requiere autenticación o suscripción nativa."
                elif "geo-restricted" in err_msg:
                    user_msg = "Contenido restringido geográficamente."
                return False, None, None, 0, 0, user_msg
            except Exception as e:
                gc.collect() 
                return False, None, None, 0, 0, f"Error general de sistema: {e}"

        return await asyncio.to_thread(_execute)


class CasinoEngine:
    @staticmethod
    def draw_card() -> str:
        cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return random.choice(cards)

    @staticmethod
    def calculate_hand(hand: List[str]) -> int:
        val = 0
        aces = 0
        for card in hand:
            if card in ['J', 'Q', 'K']: val += 10
            elif card == 'A': aces += 1; val += 11
            else: val += int(card)
        
        while val > 21 and aces:
            val -= 10
            aces -= 1
        return val

    @staticmethod
    def play_slots(bet: int) -> Tuple[int, str]:
        syms = ["🍒", "🍋", "🔔", "💎", "👑"]
        res = [random.choice(syms) for _ in range(3)]
        msg = f"🎰 **SLOTS**\n[ {res[0]} | {res[1]} | {res[2]} ]\n"
        
        if res[0] == res[1] == res[2]:
            if res[0] == "👑":
                w = bet * 50
                msg += f"🎉 **¡MEGA JACKPOT!** Ganaste {w} pts."
            elif res[0] == "💎":
                w = bet * 20
                msg += f"💎 **¡JACKPOT DE DIAMANTE!** Ganaste {w} pts."
            else:
                w = bet * 10
                msg += f"🎉 **¡JACKPOT!** Ganaste {w} pts."
            return w, msg
        elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
            w = int(bet * 1.5)
            msg += f"👍 Recuperas {w} pts."
            return w, msg
        else:
            msg += "💀 Perdiste la apuesta."
            return 0, msg

    @staticmethod
    def calculate_crash_multiplier() -> float:
        r = random.uniform(0, 1)
        if r < 0.03: return 1.00
        multiplier = 1.0 / (1.0 - r)
        return min(100.00, multiplier)

casino_engine = CasinoEngine()


class RealToolsEngine:
    @staticmethod
    async def generate_tts(text: str, uid: str, lang: str = "es") -> Optional[str]:
        try:
            def _gen():
                tts = gTTS(text=text, lang=lang)
                filepath = os.path.join(EmpireConfig.TTS_DIR, f"tts_{uid}_{uuid.uuid4().hex[:8]}.ogg")
                tts.save(filepath)
                return filepath
            return await asyncio.to_thread(_gen)
        except Exception as e:
            logger.error(f"Error en TTS real: {e}")
            alert_system.track_error()
            return None

    @staticmethod
    async def execute_ping(host: str = "8.8.8.8") -> str:
        try:
            def _ping():
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                command = ['ping', param, '4', host]
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
                return output
            
            result = await asyncio.to_thread(_ping)
            
            if platform.system().lower() == 'windows':
                match = re.search(r'Media = (\d+) ms', result)
                if match: return f"{match.group(1)}ms"
            else:
                match = re.search(r'min/avg/max/mdev = [\d\.]+/([\d\.]+)/', result)
                if match: return f"{match.group(1)}ms"
                
            return "Ping exitoso pero latencia no parseada."
        except Exception as e:
            logger.error(f"Fallo en Ping real: {e}")
            return "Destino inalcanzable o bloqueado por firewall."

    @staticmethod
    async def generate_qr(data: str, uid: str) -> Optional[str]:
        try:
            def _gen():
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                filepath = os.path.join(EmpireConfig.QR_DIR, f"qr_{uid}_{uuid.uuid4().hex[:8]}.png")
                img.save(filepath)
                return filepath
            return await asyncio.to_thread(_gen)
        except Exception as e:
            logger.error(f"Error en generador QR: {e}")
            return None

    @staticmethod
    def encode_base64(data: str) -> str:
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')
        
    @staticmethod
    def decode_base64(data: str) -> str:
        try:
            return base64.b64decode(data.encode('utf-8')).decode('utf-8')
        except:
            return "Error: Cadena Base64 inválida."

real_tools = RealToolsEngine()
