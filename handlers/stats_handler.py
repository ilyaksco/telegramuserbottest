import psutil
import platform
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from localization import LocalizationManager

def register_stats_handler(app: Client, locales: LocalizationManager, user_settings: dict):
    @app.on_message(filters.command("stats", prefixes=".") & filters.me)
    async def stats_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")

        # Mengambil data sistem
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Mengambil info OS
        os_name = f"{platform.system()} {platform.release()}"
        kernel = platform.version()

        # Format teks
        response_text = locales.get_text(
            lang,
            "stats_text",
            os_name=os_name,
            kernel=kernel,
            cpu_percent=cpu_percent,
            ram_percent=ram.percent,
            disk_percent=disk.percent
        )
        
        await message.edit_text(
            response_text,
            parse_mode=ParseMode.HTML
        )