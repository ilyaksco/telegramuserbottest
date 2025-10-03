import os
import json
import asyncio
import logging
from uuid import uuid4
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

load_dotenv()

# --- Memuat semua teks dari file locales ---
locales = {}
try:
    for lang in ["en", "id"]:
        with open(f"locales/{lang}.json", "r", encoding="utf-8") as f:
            locales[lang] = json.load(f)
except FileNotFoundError:
    print("FATAL: locales/en.json or locales/id.json not found. Please create them.")
    exit()

# Variabel untuk menyimpan pilihan bahasa pengguna
user_lang = {}

# --- Teks Detail Lengkap (Inggris & Indonesia) ---
HELP_DETAILS = {
    "en": {
        "ping": "<b>⚡️ Ping</b>\n\nChecks if the userbot is responsive. A simple command to see if the bot is alive.\n\n<b>Usage:</b> <code>.ping</code>",
        "info": "<b>👤 User Info</b>\n\nGets detailed information about a user. Use it by replying to a user's message or by providing their username/ID.\n\n<b>Usage:</b>\n• <code>.info</code> (reply to a message)\n• <code>.info &lt;username_or_id&gt;</code>",
        "lang_userbot": "<b>🌐 Language</b>\n\nChanges the userbot's display language for all command responses.\n\n<b>Usage:</b> <code>.lang &lt;id/en&gt;</code>",
        "stats": "<b>📊 Stats</b>\n\nShows the system statistics (CPU, RAM, Disk) of the server where the userbot is running.\n\n<b>Usage:</b> <code>.stats</code>",
        "joinvc": "<b>▶️ Join VC</b>\n\nCommands the userbot to join the active voice chat in the current group.\n\n<b>Usage:</b> <code>.joinvc</code>",
        "leavevc": "<b>⏹️ Leave VC</b>\n\nCommands the userbot to leave the voice chat it is currently in.\n\n<b>Usage:</b> <code>.leavevc</code>",
        "purge": "<b>🧹 Purge</b>\n\nDeletes a range of messages. Reply to the starting message and type <code>.purge</code>. All messages between the replied message and your command will be deleted.\n\n<b>Usage:</b> <code>.purge</code> (as a reply)",
        "afk": "<b>💤 AFK</b>\n\nSets an Away From Keyboard status. The bot will automatically reply to anyone who mentions you or sends you a PM. Your AFK status is cleared automatically when you send a message anywhere.\n\n<b>Usage:</b> <code>.afk &lt;reason&gt;</code>",
        "bc": "<b>📢 Broadcast</b>\n\nBroadcasts a replied message to multiple groups. You can target all groups, specific groups, or exclude certain groups.\n\n<b>Usage:</b>\n• <code>.bc</code> or <code>.bc all</code>\n• <code>.bc only &lt;group_id&gt;</code>\n• <code>.bc except &lt;group_id&gt;</code>\n\nAdditionally, you can manage a permanent blacklist:\n• <code>.excludebc</code> (in a group to blacklist it)\n• <code>.includebc</code> (in a group to un-blacklist it)",
        "pfp": "<b>🖼️ PFP</b>\n\nDownloads the full-resolution profile picture(s) of a user and sends them as documents.\n\n<b>Usage:</b>\n• <code>.pfp</code> (reply to a user)\n• <code>.pfp &lt;username_or_id&gt;</code>\n• <code>.pfp</code> (alone, for your own pfp)",
        "steal": "<b>🔐 Steal Sticker</b>\n\n'Steals' a sticker by replying to it and adds it to your designated sticker pack via the @Stickers bot.\n\n<b>Usage:</b> <code>.steal</code> (reply to a static sticker)",
        "ai": "<b>🤖 AI Chat</b>\n\nEnables a conversational AI (Groq) in a chat. The AI will only respond when someone replies to your messages.\n\n<b>Usage:</b>\n• <code>.AiOn</code>: Enables AI in the chat.\n• <code>.AiOff</code>: Disables AI.\n• <code>.newchat</code>: Resets the AI's memory.\n• <code>.prompt &lt;text&gt;</code>: Sets a custom personality for the AI in that chat.",
        "crypto": "<b>🪙 Crypto</b>\n\nFetches detailed price information for one or more cryptocurrencies from CoinGecko, including the price in IDR.\n\n<b>Usage:</b> <code>.crypto &lt;symbol1&gt; &lt;symbol2&gt; ...</code>\n<b>Example:</b> <code>.crypto btc eth ton</code>",
    },
    "id": {
        "ping": "<b>⚡️ Ping</b>\n\nCek kalo userbot-nya masih idup apa ngga. Perintah simpel buat liat botnya online.\n\n<b>Cara pake:</b> <code>.ping</code>",
        "info": "<b>👤 Info User</b>\n\nNgasih info detail soal seorang user. Bisa dipake dengan bales pesan orangnya, atau pake username/ID-nya.\n\n<b>Cara pake:</b>\n• <code>.info</code> (sambil bales pesan)\n• <code>.info &lt;username_atau_id&gt;</code>",
        "lang_userbot": "<b>🌐 Bahasa</b>\n\nGanti bahasa yang dipake userbot buat semua balasan perintah.\n\n<b>Cara pake:</b> <code>.lang &lt;id/en&gt;</code>",
        "stats": "<b>📊 Statistik</b>\n\nNampilin statistik sistem (CPU, RAM, Disk) dari server tempat userbot jalan.\n\n<b>Cara pake:</b> <code>.stats</code>",
        "joinvc": "<b>▶️ Gabung VC</b>\n\nNyuruh userbot buat join obrolan suara (VC) yang lagi aktif di grup.\n\n<b>Cara pake:</b> <code>.joinvc</code>",
        "leavevc": "<b>⏹️ Keluar VC</b>\n\nNyuruh userbot buat cabut dari obrolan suara yang lagi diikutin.\n\n<b>Cara pake:</b> <code>.leavevc</code>",
        "purge": "<b>🧹 Bersihin</b>\n\nNgehapus banyak pesan sekaligus. Bales pesan pertama yang mau dihapus, terus ketik <code>.purge</code>. Semua pesan di antaranya bakal ilang.\n\n<b>Cara pake:</b> <code>.purge</code> (sambil bales pesan)",
        "afk": "<b>💤 AFK</b>\n\nNgaktifin mode AFK (Lagi Pergi). Bot bakal bales otomatis kalo ada yang nge-mention atau nge-DM kamu. Status AFK otomatis mati pas kamu ngirim pesan lagi.\n\n<b>Cara pake:</b> <code>.afk &lt;alesan kamu&gt;</code>",
        "bc": "<b>📢 Broadcast</b>\n\nNgirim pesan siaran ke banyak grup. Kamu bisa targetin semua grup, grup tertentu aja, atau ngecualian beberapa grup.\n\n<b>Cara pake:</b>\n• <code>.bc</code> atau <code>.bc all</code>\n• <code>.bc only &lt;id_grup&gt;</code>\n• <code>.bc except &lt;id_grup&gt;</code>\n\nKamu juga bisa ngatur daftar hitam permanen:\n• <code>.excludebc</code> (di grup buat nge-blacklist)\n• <code>.includebc</code> (di grup buat nge-unblacklist)",
        "pfp": "<b>🖼️ PFP</b>\n\nNgunduh semua foto profil orang dalam kualitas full dan dikirim sebagai file.\n\n<b>Cara pake:</b>\n• <code>.pfp</code> (sambil bales pesan)\n• <code>.pfp &lt;username_atau_id&gt;</code>\n• <code>.pfp</code> (buat ngambil fotomu sendiri)",
        "steal": "<b>🔐 Comot Stiker</b>\n\n'Nyomot' stiker dengan bales pesannya, terus otomatis nambahin ke sticker pack kamu lewat @Stickers.\n\n<b>Cara pake:</b> <code>.steal</code> (bales ke stiker gambar)",
        "ai": "<b>🤖 Obrolan AI</b>\n\nMengelola AI percakapan (Groq) di sebuah chat. AI cuma bakal bales kalo ada yang nge-reply pesan kamu.\n\n<b>Cara pake:</b>\n• <code>.AiOn</code>: Ngaktifin AI di chat.\n• <code>.AiOff</code>: Matiin AI.\n• <code>.newchat</code>: Ngereset ingatan AI.\n• <code>.prompt &lt;teks&gt;</code>: Ngasih 'kepribadian' khusus buat AI di chat itu.",
        "crypto": "<b>🪙 Kripto</b>\n\nNgecek info harga detail buat satu atau beberapa koin kripto dari CoinGecko, termasuk harga dalam Rupiah.\n\n<b>Cara pake:</b> <code>.crypto &lt;simbol1&gt; &lt;simbol2&gt; ...</code>\n<b>Contoh:</b> <code>.crypto btc eth ton</code>",
    }
}


def get_main_menu_keyboard(lang: str):
    l = locales.get(lang, locales["en"])
    buttons = [
        [types.InlineKeyboardButton(text=l["lang_button"], callback_data="lang_switch")],
        [types.InlineKeyboardButton(text=l["ping_button"], callback_data="help_ping"), types.InlineKeyboardButton(text=l["info_button"], callback_data="help_info")],
        [types.InlineKeyboardButton(text=l["lang_userbot_button"], callback_data="help_lang_userbot"), types.InlineKeyboardButton(text=l["stats_button"], callback_data="help_stats")],
        [types.InlineKeyboardButton(text=l["joinvc_button"], callback_data="help_joinvc"), types.InlineKeyboardButton(text=l["leavevc_button"], callback_data="help_leavevc")],
        [types.InlineKeyboardButton(text=l["purge_button"], callback_data="help_purge"), types.InlineKeyboardButton(text=l["afk_button"], callback_data="help_afk")],
        [types.InlineKeyboardButton(text=l["bc_button"], callback_data="help_bc"), types.InlineKeyboardButton(text=l["pfp_button"], callback_data="help_pfp")],
        [types.InlineKeyboardButton(text=l["steal_button"], callback_data="help_steal"), types.InlineKeyboardButton(text=l["ai_button"], callback_data="help_ai")],
        [types.InlineKeyboardButton(text=l["crypto_button"], callback_data="help_crypto")],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.inline_query()
async def inline_query_handler(query: types.InlineQuery):
    user_id = query.from_user.id
    lang = user_lang.get(user_id, "en")
    l = locales.get(lang, locales["en"])
    
    results = [
        types.InlineQueryResultArticle(
            id=str(uuid4()),
            title=l["help_main_title"],
            description=l["help_main_desc"],
            input_message_content=types.InputTextMessageContent(
                message_text=l["help_main_text"],
                parse_mode=ParseMode.HTML
            ),
            reply_markup=get_main_menu_keyboard(lang),
        )
    ]
    await query.answer(results, cache_time=1, is_personal=True)

@dp.callback_query(F.data.startswith(("help_", "lang_")))
async def button_callback_handler(query: types.CallbackQuery):
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    current_lang = user_lang.get(user_id, "en")
    
    if data == "lang_switch":
        new_lang = "id" if current_lang == "en" else "en"
        user_lang[user_id] = new_lang
        l_new = locales.get(new_lang, locales["en"])
        
        target_message = query.message or query.inline_message_id
        if target_message:
            await bot.edit_message_text(
                chat_id=query.message.chat.id if query.message else None,
                message_id=query.message.message_id if query.message else None,
                inline_message_id=query.inline_message_id,
                text=l_new["help_main_text"],
                reply_markup=get_main_menu_keyboard(new_lang),
                parse_mode=ParseMode.HTML
            )
        return

    l = locales.get(current_lang, locales["en"])
    back_button = types.InlineKeyboardButton(text=l["back_button"], callback_data="help_main")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    if data == "help_main":
        target_message = query.message or query.inline_message_id
        if target_message:
            await bot.edit_message_text(
                chat_id=query.message.chat.id if query.message else None,
                message_id=query.message.message_id if query.message else None,
                inline_message_id=query.inline_message_id,
                text=l["help_main_text"],
                reply_markup=get_main_menu_keyboard(current_lang),
                parse_mode=ParseMode.HTML
            )
    else:
        feature_key = data.split("_", 1)[1]
        
        # --- LOGIKA YANG DIPERBAIKI ---
        # 1. Coba ambil detail dari bahasa yang sedang aktif.
        detail_text = HELP_DETAILS.get(current_lang, {}).get(feature_key)
        
        # 2. Jika tidak ada, baru ambil dari Bahasa Inggris.
        if not detail_text:
            detail_text = HELP_DETAILS["en"].get(feature_key, "Detail not found.")
        # -----------------------------
        
        target_message = query.message or query.inline_message_id
        if target_message:
            await bot.edit_message_text(
                chat_id=query.message.chat.id if query.message else None,
                message_id=query.message.message_id if query.message else None,
                inline_message_id=query.inline_message_id,
                text=detail_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )

async def main() -> None:
    print("Helper bot (i18n) is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())