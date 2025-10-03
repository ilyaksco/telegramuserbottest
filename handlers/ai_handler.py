import logging
from groq import AsyncGroq
from pyrogram import Client, filters
from pyrogram.types import Message

from localization import LocalizationManager
from database.db_manager import DatabaseManager

AI_MODEL = "openai/gpt-oss-120b"

def register_ai_handler(app: Client, locales: LocalizationManager, user_settings: dict, db: DatabaseManager, groq_client: AsyncGroq):
    
    @app.on_message(filters.command("AiOn", prefixes=".") & filters.me)
    async def ai_on_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        db.enable_ai(message.chat.id)
        db.clear_chat_history(message.chat.id)
        await message.edit_text(locales.get_text(lang, "ai_on"))

    @app.on_message(filters.command("AiOff", prefixes=".") & filters.me)
    async def ai_off_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        db.disable_ai(message.chat.id)
        await message.edit_text(locales.get_text(lang, "ai_off"))

    @app.on_message(filters.command("newchat", prefixes=".") & filters.me)
    async def new_chat_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        db.clear_chat_history(message.chat.id)
        await message.edit_text(locales.get_text(lang, "ai_new_chat"))

    # -- Perintah Baru untuk System Prompt --
    @app.on_message(filters.command("prompt", prefixes=".") & filters.me)
    async def set_prompt_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        command = message.text.split(maxsplit=1)

        if len(command) > 1:
            prompt_text = command[1]
            db.set_system_prompt(message.chat.id, prompt_text)
            await message.edit_text(locales.get_text(lang, "ai_prompt_set"))
        else:
            db.clear_system_prompt(message.chat.id)
            await message.edit_text(locales.get_text(lang, "ai_prompt_cleared"))
        
    @app.on_message(group=1)
    async def ai_watcher(client: Client, message: Message):
        if (message.from_user and message.from_user.is_self) or not message.text:
            return

        if not db.is_ai_enabled(message.chat.id):
            return
        
        if not message.reply_to_message or not message.reply_to_message.from_user or not message.reply_to_message.from_user.is_self:
            return
        
        lang = user_settings.get("lang", "en")
        thinking_message = await message.reply_text(locales.get_text(lang, "ai_thinking"))

        try:
            # -- Logika Diperbarui untuk Menggunakan System Prompt --
            messages_for_api = []
            
            # 1. Ambil dan tambahkan system prompt jika ada
            system_prompt = db.get_system_prompt(message.chat.id)
            if system_prompt:
                messages_for_api.append({"role": "system", "content": system_prompt})

            # 2. Tambahkan riwayat percakapan
            history = db.get_chat_history(message.chat.id)
            messages_for_api.extend(history)

            # 3. Tambahkan pesan baru dari pengguna
            user_message = {"role": "user", "content": message.text}
            messages_for_api.append(user_message)
            db.add_to_chat_history(message.chat.id, "user", message.text)
            
            # Kirim semua pesan ke API
            chat_completion = await groq_client.chat.completions.create(
                messages=messages_for_api,
                model=AI_MODEL,
            )
            ai_response = chat_completion.choices[0].message.content
            
            db.add_to_chat_history(message.chat.id, "assistant", ai_response)
            await thinking_message.edit_text(ai_response)

        except Exception as e:
            logging.error(f"AI response failed: {e}", exc_info=True)
            await thinking_message.edit_text(f"An error occurred with the AI: {e}")