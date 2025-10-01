import json
import logging
import os

class LocalizationManager:
    def __init__(self, locales_dir):
        self.locales = {}
        if not os.path.isdir(locales_dir):
            logging.error(f"Locales directory '{locales_dir}' not found.")
            return

        for lang_code in ["en", "id"]:
            file_path = os.path.join(locales_dir, f"{lang_code}.json")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.locales[lang_code] = json.load(f)
            except FileNotFoundError:
                logging.error(f"Locale file for '{lang_code}.json' not found at '{file_path}'.")
                self.locales[lang_code] = {}
            except json.JSONDecodeError:
                logging.error(f"Error decoding JSON from '{lang_code}.json'.")
                self.locales[lang_code] = {}

    def get_text(self, lang, key, **kwargs):
        lang_data = self.locales.get(lang)

        if not lang_data:
            lang_data = self.locales.get("en", {})

        text_template = lang_data.get(key, f"ERROR: Translation key '{key}' not found.")
        
        try:
            return text_template.format(**kwargs)
        except KeyError as e:
            logging.error(f"Missing formatting key {e} in translation for '{key}'")
            return text_template