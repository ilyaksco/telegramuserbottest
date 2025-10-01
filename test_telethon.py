import asyncio
from telethon import TelegramClient, Button

# --- GANTI DENGAN KREDENSIAL ANDA ---
API_ID = 29327050  # Ganti dengan API_ID Anda
API_HASH = "4451190c6c5d59f1e60c7b8bab670d45"
SESSION_NAME = "telethon_test_session"
# ------------------------------------

async def main():
    print("Connecting with Telethon...")
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    await client.start()
    print("Client connected. Sending test message...")
    
    try:
        await client.send_message(
            "me",  # Mengirim ke Pesan Tersimpan
            "Ini adalah pesan tes dari Telethon.",
            buttons=[
                Button.inline("Tombol Tes Telethon", b"test")
            ]
        )
        print("Message sent successfully via Telethon! Please check your Saved Messages.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.disconnect()
        print("Client disconnected.")

if __name__ == "__main__":
    # Telethon akan menjalankan loop-nya sendiri
    # Jika diminta, masukkan nomor telepon, kode, dan password 2FA Anda
    asyncio.run(main())