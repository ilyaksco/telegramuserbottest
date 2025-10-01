from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from localization import LocalizationManager

def register_help_handler(app: Client, locales: LocalizationManager, user_settings: dict):
    @app.on_message(filters.command("help", prefixes=".") & filters.me)
    async def help_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        
        # Ambil teks bantuan yang sudah diformat
        response_text = locales.get_text(lang, "help_text")
        
        await message.edit_text(
            response_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )