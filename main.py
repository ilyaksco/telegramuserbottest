import os
import logging
from dotenv import load_dotenv

from pyrogram import Client
from pytgcalls import GroupCallFactory
from groq import AsyncGroq # <-- DIUBAH: Impor dari groq


from handlers import register_all_handlers
from localization import LocalizationManager
from database.db_manager import DatabaseManager 

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='{"level":"%(levelname)s","ts":"%(asctime)s","caller":"%(filename)s:%(lineno)d","msg":"%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S.%fZ'
)

db_manager = DatabaseManager()
db_manager.setup_database()

groq_client = AsyncGroq()


API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "my_userbot")

user_settings = {"lang": "en"}

locales = LocalizationManager("locales")

app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    sleep_threshold=60  # Otomatis tunggu jika floodwait di bawah 60 detik
)

group_call_factory = GroupCallFactory(app)
group_call = group_call_factory.get_group_call()

register_all_handlers(app, group_call, locales, user_settings, db_manager, groq_client)

if __name__ == "__main__":
    logging.info("starting userbot...")
    app.run()
    logging.info("userbot stopped.")