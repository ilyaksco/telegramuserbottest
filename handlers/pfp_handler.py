import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from localization import LocalizationManager

def register_pfp_handler(app: Client, locales: LocalizationManager, user_settings: dict):
    @app.on_message(filters.command("pfp", prefixes=".") & filters.me)
    async def pfp_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")
        target_user = None
        
        # Logika untuk menentukan target pengguna (sama seperti .info)
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
        else:
            command = message.text.split(maxsplit=1)
            if len(command) > 1:
                try:
                    target_user = await client.get_users(command[1])
                except Exception:
                    await message.edit_text(locales.get_text(lang, "pfp_user_not_found"))
                    return
            else:
                target_user = message.from_user

        if not target_user:
            await message.edit_text(locales.get_text(lang, "pfp_user_not_found"))
            return

        await message.edit_text(locales.get_text(lang, "pfp_fetching"))
        
        photos_sent = 0
        # Mengambil foto profil pengguna
        async for photo in client.get_chat_photos(target_user.id):
            try:
                # Mengunduh foto
                downloaded_path = await client.download_media(photo.file_id)
                
                # Mengirim foto sebagai dokumen untuk kualitas maksimal
                await client.send_document(
                    chat_id=message.chat.id,
                    document=downloaded_path,
                    caption=locales.get_text(
                        lang,
                        "pfp_caption",
                        full_name=target_user.first_name,
                        file_name=os.path.basename(downloaded_path)
                    )
                )
                
                # Menghapus file yang sudah diunduh untuk membersihkan server
                os.remove(downloaded_path)
                photos_sent += 1
            except Exception as e:
                logging.error(f"Could not process a profile photo: {e}")

        # Hapus pesan "fetching..." setelah selesai
        await message.delete()

        if photos_sent == 0:
            # Kirim pesan baru jika tidak ada foto yang ditemukan
            await client.send_message(
                chat_id=message.chat.id,
                text=locales.get_text(lang, "pfp_no_photos")
            )