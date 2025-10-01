from pyrogram import Client, filters
from pyrogram.types import Message

from localization import LocalizationManager

def register_lang_handler(app: Client, locales: LocalizationManager, user_settings: dict):
    @app.on_message(filters.command("lang", prefixes=".") & filters.me)
    async def lang_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")

        command = message.text.split()
        if len(command) > 1:
            new_lang = command[1].lower()
            if new_lang in locales.locales:
                user_settings["lang"] = new_lang
                response_text = locales.get_text(new_lang, "lang_changed")
                await message.edit_text(response_text)
            else:
                response_text = locales.get_text(lang, "lang_not_found", lang=new_lang)
                await message.edit_text(response_text)
        else:
            await message.edit_text(f"Current language: {lang}")