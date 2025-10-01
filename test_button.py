import asyncio
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- GANTI DENGAN KREDENSIAL ANDA ---
API_ID = 29327050
API_HASH = "4451190c6c5d59f1e60c7b8bab670d45"
SESSION_NAME = "test_button_session"
# ------------------------------------

async def main():
    print("Connecting client...")
    async with Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH) as app:
        print("Client connected. Sending test message to 'Saved Messages'...")
        
        try:
            await app.send_message(
                "me",  # "me" berarti ke Pesan Tersimpan (Saved Messages)
                "Ini adalah pesan tes dengan tombol.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Ini Tombol Tes",
                                callback_data="test_ok"
                            )
                        ]
                    ]
                )
            )
            print("Message sent successfully! Please check your Saved Messages.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Jika Anda diminta login, masukkan nomor telepon, kode, dan password 2FA Anda
    # seperti saat pertama kali menjalankan userbot.
    asyncio.run(main())