import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

from localization import LocalizationManager
from database.db_manager import DatabaseManager

def register_broadcast_handler(app: Client, locales: LocalizationManager, user_settings: dict, db: DatabaseManager):
    
    @app.on_message(filters.command(["bc", "broadcast"], prefixes=".") & filters.me)
    async def broadcast_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")

        if not message.reply_to_message:
            await message.edit_text(locales.get_text(lang, "bc_no_reply"))
            return

        # Mendapatkan semua grup
        all_groups = []
        async for dialog in client.get_dialogs():
            if dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                all_groups.append(dialog.chat.id)

        # Mendapatkan daftar hitam dari DB
        blacklist = db.get_blacklist()

        # Logika filter
        command = message.text.split()
        target_groups = []
        
        mode = command[1] if len(command) > 1 else "all"

        if mode == "all":
            target_groups = [gid for gid in all_groups if gid not in blacklist]
        elif mode == "except" and len(command) > 2:
            exceptions = [int(gid) for gid in command[2:]]
            target_groups = [gid for gid in all_groups if gid not in exceptions and gid not in blacklist]
        elif mode == "only" and len(command) > 2:
            target_groups = [int(gid) for gid in command[2:]]
        
        await message.edit_text(locales.get_text(lang, "bc_started", target_count=len(target_groups)))

        sent_count = 0
        failed_count = 0
        for group_id in target_groups:
            try:
                await message.reply_to_message.forward(group_id)
                sent_count += 1
                await asyncio.sleep(2) # Jeda 2 detik antar pesan
            except FloodWait as e:
                logging.warning(f"FloodWait for {e.value} seconds. Sleeping...")
                await asyncio.sleep(e.value)
                await message.reply_to_message.forward(group_id) # Coba lagi
                sent_count += 1
            except Exception as e:
                logging.error(f"Failed to send broadcast to {group_id}: {e}")
                failed_count += 1
        
        await message.edit_text(locales.get_text(lang, "bc_finished", sent_count=sent_count, failed_count=failed_count))

    @app.on_message(filters.command("excludebc", prefixes=".") & filters.me)
    async def exclude_bc_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await message.edit_text(locales.get_text(lang, "bc_not_a_group"))
            return
        
        db.add_to_blacklist(message.chat.id)
        await message.edit_text(locales.get_text(lang, "bc_exclude_added"))

    @app.on_message(filters.command("includebc", prefixes=".") & filters.me)
    async def include_bc_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await message.edit_text(locales.get_text(lang, "bc_not_a_group"))
            return
        
        db.remove_from_blacklist(message.chat.id)
        await message.edit_text(locales.get_text(lang, "bc_exclude_removed"))