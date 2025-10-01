from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from localization import LocalizationManager

async def get_user_info(target_user):
    return {
        "user_id": target_user.id,
        "first_name": target_user.first_name or "N/A",
        "last_name": target_user.last_name or "N/A",
        "username": target_user.username or "N/A",
        "is_bot": target_user.is_bot,
        "is_scam": target_user.is_scam,
        "is_fake": target_user.is_fake,
        "lang_code": target_user.language_code or "N/A",
        "user_link": target_user.mention(style="md")
    }

def register_info_handler(app: Client, locales: LocalizationManager, user_settings: dict):
    @app.on_message(filters.command("info", prefixes=".") & filters.me)
    async def info_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        target_user = None

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
        else:
            command = message.text.split(maxsplit=1)
            if len(command) > 1:
                try:
                    target_user = await client.get_users(command[1])
                except Exception:
                    await message.edit_text("User not found.")
                    return
            else:
                target_user = message.from_user

        if target_user:
            user_details = await get_user_info(target_user)
            response_text = locales.get_text(lang, "user_info", **user_details)
            await message.edit_text(response_text, parse_mode=ParseMode.HTML)