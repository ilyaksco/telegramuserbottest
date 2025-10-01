import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from localization import LocalizationManager

# Variabel untuk menyimpan status AFK di memori
afk_status = {
    "is_afk": False,
    "reason": "",
    "start_time": 0,
    "notified_chats": set()
}

def format_duration(seconds):
    if seconds < 60:
        return f"{int(seconds)} seconds"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {int(seconds)}s"
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m"

def register_afk_handler(app: Client, locales: LocalizationManager, user_settings: dict):
    
    @app.on_message(filters.command("afk", prefixes=".") & filters.me)
    async def go_afk(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        reason = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "N/A"
        
        afk_status["is_afk"] = True
        afk_status["reason"] = reason
        afk_status["start_time"] = time.time()
        afk_status["notified_chats"].clear()
        
        await message.edit_text(locales.get_text(lang, "afk_on", reason=reason))

    # Handler untuk mematikan AFK
    @app.on_message(filters.me & ~filters.command("afk", prefixes=".") & filters.group, group=10)
    async def come_back_group(client: Client, message: Message):
        if afk_status["is_afk"]:
            afk_status["is_afk"] = False
            start_time = afk_status["start_time"]
            duration = format_duration(time.time() - start_time)
            lang = user_settings.get("lang", "en")
            
            await client.send_message(
                message.chat.id,
                locales.get_text(lang, "afk_back", duration=duration)
            )
    
    # Handler untuk membalas mention/PM
    @app.on_message(
        (filters.mentioned | filters.private) & 
        ~filters.me & 
        ~filters.bot & 
        filters.incoming
    )
    async def afk_watcher(client: Client, message: Message):
        if afk_status["is_afk"] and message.chat.id not in afk_status["notified_chats"]:
            start_time = afk_status["start_time"]
            time_ago = format_duration(time.time() - start_time)
            reason = afk_status["reason"]
            lang = user_settings.get("lang", "en")
            
            await message.reply_text(
                locales.get_text(lang, "afk_reply", time_ago=time_ago, reason=reason)
            )
            afk_status["notified_chats"].add(message.chat.id)