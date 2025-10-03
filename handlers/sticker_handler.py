import logging
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image

from localization import LocalizationManager

# HAPUS BARIS INI DARI SINI
# STICKER_PACK_NAME = os.getenv("STICKER_PACK_NAME") 

def resize_image(image_path):
    img = Image.open(image_path)
    if img.width > img.height:
        new_width = 512
        new_height = int(512 * img.height / img.width)
    else:
        new_height = 512
        new_width = int(512 * img.width / img.height)
    
    img = img.resize((new_width, new_height))
    
    new_img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    new_img.paste(img, (int((512 - new_width) / 2), int((512 - new_height) / 2)))
    
    output_path = "downloads/stolen_sticker.png"
    new_img.save(output_path, "PNG")
    return output_path

def register_sticker_handler(app: Client, locales: LocalizationManager, user_settings: dict):
    @app.on_message(filters.command("steal", prefixes=".") & filters.me)
    async def steal_command(client: Client, message: Message):
        lang = user_settings.get("lang", "en")

        # PINDAHKAN KE SINI, DI DALAM FUNGSI
        STICKER_PACK_NAME = os.getenv("STICKER_PACK_NAME")

        if not STICKER_PACK_NAME:
            await message.edit_text("`STICKER_PACK_NAME` is not set in your .env file.")
            return

        if not message.reply_to_message or not message.reply_to_message.sticker:
            await message.edit_text(locales.get_text(lang, "steal_no_reply"))
            return
        
        sticker = message.reply_to_message.sticker
        
        if sticker.is_animated or sticker.is_video:
            await message.edit_text("Sorry, I can only steal static image stickers for now.")
            return

        await message.edit_text(locales.get_text(lang, "steal_in_progress"))
        
        downloaded_path = None
        resized_path = None

        try:
            os.makedirs("downloads", exist_ok=True)
            
            downloaded_path = await client.download_media(sticker.file_id, file_name="downloads/temp_sticker")
            resized_path = resize_image(downloaded_path)

            await client.send_message("@Stickers", "/cancel")
            await asyncio.sleep(2)
            await client.send_message("@Stickers", "/addsticker")
            await asyncio.sleep(2)
            await client.send_message("@Stickers", STICKER_PACK_NAME)
            await asyncio.sleep(2)
            await client.send_document("@Stickers", resized_path)
            await asyncio.sleep(2)
            await client.send_message("@Stickers", sticker.emoji or "😊")
            await asyncio.sleep(2)
            await client.send_message("@Stickers", "/done")

            await message.edit_text(locales.get_text(lang, "steal_success"))

        except Exception as e:
            logging.error(f"Sticker steal failed: {e}", exc_info=True)
            await message.edit_text(locales.get_text(lang, "steal_failed") + f"\n`{e}`")
        finally:
            if downloaded_path and os.path.exists(downloaded_path):
                os.remove(downloaded_path)
            if resized_path and os.path.exists(resized_path):
                os.remove(resized_path)