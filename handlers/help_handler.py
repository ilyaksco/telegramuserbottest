import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

def register_help_handler(app: Client, locales, user_settings):
    @app.on_message(filters.command("help", prefixes=".") & filters.me)
    async def help_command(client: Client, message: Message):
        
        HELPER_BOT_USERNAME = os.getenv("HELPER_BOT_USERNAME")
        await message.delete()

        if not HELPER_BOT_USERNAME:
            await client.send_message(message.chat.id, "`HELPER_BOT_USERNAME` not set in .env")
            return

        try:
            # Panggil helper bot secara inline
            results = await client.get_inline_bot_results(HELPER_BOT_USERNAME)
            
            # Kirim hasilnya
            await client.send_inline_bot_result(
                chat_id=message.chat.id,
                query_id=results.query_id,
                result_id=results.results[0].id
            )
        except Exception as e:
            logging.error(f"An unknown error occurred in .help: {e}", exc_info=True)
            await client.send_message(message.chat.id, f"Could not fetch help menu. Error: {e}")