from pyrogram import Client, filters
from pyrogram.types import Message

from localization import LocalizationManager

def register_ping_handler(app: Client, locales: LocalizationManager, user_settings: dict):
    @app.on_message(filters.command("ping", prefixes=".") & filters.me)
    async def ping_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        response_text = locales.get_text(lang, "ping_response")
        await message.edit_text(response_text)