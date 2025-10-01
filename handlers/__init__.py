from pyrogram import Client
from localization import LocalizationManager
from database.db_manager import DatabaseManager 

from .ping_handler import register_ping_handler
from .lang_handler import register_lang_handler
from .info_handler import register_info_handler
from .voice_chat_handler import register_vc_handler
from .help_handler import register_help_handler 
from .purge_handler import register_purge_handler 
from .broadcast_handler import register_broadcast_handler 
from .stats_handler import register_stats_handler 
from .afk_handler import register_afk_handler 
from .pfp_handler import register_pfp_handler


def register_all_handlers(app: Client, group_call, locales: LocalizationManager, user_settings: dict, db_manager: DatabaseManager):
    register_ping_handler(app, locales, user_settings)
    register_lang_handler(app, locales, user_settings)
    register_info_handler(app, locales, user_settings)
    register_vc_handler(app, group_call, locales, user_settings)
    register_help_handler(app, locales, user_settings) 
    register_purge_handler(app, locales, user_settings) 
    register_broadcast_handler(app, locales, user_settings, db_manager) 
    register_stats_handler(app, locales, user_settings) 
    register_afk_handler(app, locales, user_settings) 
    register_pfp_handler(app, locales, user_settings)

    
