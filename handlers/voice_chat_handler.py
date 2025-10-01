import logging
from asyncio import TimeoutError
from pyrogram import Client, filters, errors
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pytgcalls.exceptions import GroupCallNotFoundError

from localization import LocalizationManager

def register_vc_handler(app: Client, group_call, locales: LocalizationManager, user_settings: dict):
    @app.on_message(filters.command("joinvc", prefixes=".") & filters.me)
    async def join_vc_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        chat_id = message.chat.id

        await message.edit_text(locales.get_text(lang, "joining_vc"))

        try:
            await group_call.join(chat_id)
            await message.edit_text(locales.get_text(lang, "join_vc_success"))
        except errors.FloodWait as e:
            await message.edit_text(
                locales.get_text(lang, "join_vc_failed_floodwait", seconds=e.value),
                parse_mode=ParseMode.HTML
            )
        except GroupCallNotFoundError:
            await message.edit_text(locales.get_text(lang, "join_vc_failed_no_vc"))
        except TimeoutError:
            await message.edit_text(
                locales.get_text(lang, "join_vc_failed_timeout"),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logging.error(f"Could not join VC: {e}")
            await message.edit_text(
                locales.get_text(lang, "join_vc_failed_unknown", error=str(e))
            )

    @app.on_message(filters.command("leavevc", prefixes=".") & filters.me)
    async def leave_vc_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        # chat_id tidak diperlukan untuk leave
        
        await message.edit_text(locales.get_text(lang, "leaving_vc"))
        
        try:
            # Hapus argumen dari sini
            await group_call.leave()
            await message.edit_text(locales.get_text(lang, "leave_vc_success"))
        except Exception as e:
            logging.error(f"Could not leave VC: {e}")
            await message.edit_text(
                locales.get_text(lang, "join_vc_failed_unknown", error=str(e))
            )