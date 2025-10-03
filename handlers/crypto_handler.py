import logging
import aiohttp
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from localization import LocalizationManager

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

COIN_MAP = {
    "btc": "bitcoin", "eth": "ethereum", "doge": "dogecoin", "xrp": "ripple",
    "ltc": "litecoin", "bch": "bitcoin-cash", "ada": "cardano", "dot": "polkadot",
    "bnb": "binancecoin", "sol": "solana",
    "shib": "shiba-inu",
    "ton": "the-open-network", # <-- Tambahkan baris ini
}

# --- Sistem Cooldown ---
last_crypto_request_time = 0
COOLDOWN_SECONDS = 10  # Jeda 10 detik antar permintaan API
# -------------------------

def register_crypto_handler(app: Client, locales: LocalizationManager, user_settings: dict):
    @app.on_message(filters.command("crypto", prefixes=".") & filters.me)
    async def crypto_command(client: Client, message: Message):
        global last_crypto_request_time
        lang = user_settings.get("lang", "en")
        
        # Cek Cooldown
        current_time = time.time()
        time_since_last = current_time - last_crypto_request_time
        if time_since_last < COOLDOWN_SECONDS:
            remaining = COOLDOWN_SECONDS - time_since_last
            await message.edit_text(locales.get_text(lang, "crypto_cooldown", seconds=f"{remaining:.1f}"))
            return

        command = message.text.split()
        if len(command) == 1:
            await message.edit_text("Usage: `.crypto <symbol1> <symbol2>` ...")
            return

        await message.edit_text(locales.get_text(lang, "crypto_fetching_detailed"))
        
        symbols_input = [s.lower() for s in command[1:]]
        coin_ids = [COIN_MAP.get(s, s) for s in symbols_input]
        
        params_usd = {"vs_currency": "usd", "ids": ",".join(coin_ids)}
        params_idr = {"ids": ",".join(coin_ids), "vs_currencies": "idr"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, params=params_usd) as response_usd:
                    if response_usd.status != 200:
                        await message.edit_text(f"API Error (USD): {response_usd.status}")
                        return
                    data_usd = await response_usd.json()
                
                simple_price_url = "https://api.coingecko.com/api/v3/simple/price"
                async with session.get(simple_price_url, params=params_idr) as response_idr:
                    data_idr = await response_idr.json() if response_idr.status == 200 else {}

            # Perbarui timestamp HANYA jika permintaan API berhasil
            last_crypto_request_time = time.time()

            if not data_usd:
                await message.edit_text(locales.get_text(lang, "crypto_not_found_detailed", symbols=", ".join(symbols_input)))
                return
            
            await message.delete()
            
            found_symbols = []
            for coin_data in data_usd:
                coin_id = coin_data.get('id')
                symbol = coin_data.get('symbol', '').lower()
                found_symbols.append(symbol)
                price_idr = data_idr.get(coin_id, {}).get('idr', 0)

                def format_large_number(num):
                    if num is None: return "N/A"
                    num = float(num)
                    if num > 1_000_000_000_000: return f"{num / 1_000_000_000_000:.2f}T"
                    if num > 1_000_000_000: return f"{num / 1_000_000_000:.2f}B"
                    if num > 1_000_000: return f"{num / 1_000_000:.2f}M"
                    return f"{num:,}"

                card_text = locales.get_text(
                    lang, "crypto_detail_template",
                    name=coin_data.get('name', 'N/A'),
                    symbol=coin_data.get('symbol', 'N/A').upper(),
                    price_usd=f"{coin_data.get('current_price', 0):,}",
                    price_idr=f"{price_idr:,}",
                    change_24h=f"{coin_data.get('price_change_percentage_24h', 0):.2f}",
                    high_24h=f"{coin_data.get('high_24h', 0):,}",
                    low_24h=f"{coin_data.get('low_24h', 0):,}",
                    volume_24h=format_large_number(coin_data.get('total_volume')),
                    market_cap=format_large_number(coin_data.get('market_cap'))
                )
                
                await client.send_message(message.chat.id, card_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            
            not_found = [s for s in symbols_input if s not in found_symbols]
            if not_found:
                await client.send_message(message.chat.id, locales.get_text(lang, "crypto_not_found_detailed", symbols=", ".join(not_found)))

        except Exception as e:
            logging.error(f"Crypto command failed: {e}", exc_info=True)
            await message.edit_text(f"An error occurred: {e}")