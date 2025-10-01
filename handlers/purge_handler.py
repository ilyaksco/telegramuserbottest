import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from localization import LocalizationManager

def register_purge_handler(app: Client, locales: LocalizationManager, user_settings: dict):
    @app.on_message(filters.command("purge", prefixes=".") & filters.me)
    async def purge_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")

        # Cek apakah perintah ini adalah balasan ke pesan lain
        if not message.reply_to_message:
            await message.edit_text(locales.get_text(lang, "purge_no_reply"))
            return

        await message.edit_text(locales.get_text(lang, "purge_start"))

        # Dapatkan ID pesan awal dan akhir
        start_message_id = message.reply_to_message.id
        end_message_id = message.id
        
        # Buat daftar ID semua pesan yang akan dihapus
        message_ids = list(range(start_message_id, end_message_id + 1))
        
        try:
            # Hapus semua pesan dalam satu panggilan API
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=message_ids
            )
            
        except Exception as e:
            logging.error(f"Could not purge messages: {e}")
            await message.edit_text(f"Error: {e}")