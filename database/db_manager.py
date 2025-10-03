import sqlite3
import logging

class DatabaseManager:
    def __init__(self, db_name="database/userbot.db"):
        self.db_name = db_name
        self.conn = None

    def setup_database(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            cursor = self.conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_blacklist (chat_id INTEGER PRIMARY KEY)
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_enabled_chats (chat_id INTEGER PRIMARY KEY)
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """)
            # -- Tabel baru untuk System Prompt --
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_system_prompts (
                chat_id INTEGER PRIMARY KEY,
                prompt TEXT NOT NULL
            )
            """)
            self.conn.commit()
            logging.info("Database setup successful. AI tables are ready.")
        except Exception as e:
            logging.error(f"Database setup failed: {e}")
        finally:
            if self.conn:
                self.conn.close()


    def add_to_blacklist(self, chat_id: int):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Coba masukkan, abaikan jika sudah ada
            cursor.execute("INSERT OR IGNORE INTO broadcast_blacklist (chat_id) VALUES (?)", (chat_id,))
            conn.commit()

    def remove_from_blacklist(self, chat_id: int):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM broadcast_blacklist WHERE chat_id = ?", (chat_id,))
            conn.commit()

    def get_blacklist(self) -> list:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM broadcast_blacklist")
            # Mengubah hasil dari list of tuples menjadi list of integers
            return [item[0] for item in cursor.fetchall()]
    
    def is_ai_enabled(self, chat_id: int) -> bool:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM ai_enabled_chats WHERE chat_id = ?", (chat_id,))
            return cursor.fetchone() is not None

    def enable_ai(self, chat_id: int):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO ai_enabled_chats (chat_id) VALUES (?)", (chat_id,))
            conn.commit()

    def disable_ai(self, chat_id: int):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ai_enabled_chats WHERE chat_id = ?", (chat_id,))
            conn.commit()

    def get_chat_history(self, chat_id: int) -> list:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, content FROM ai_conversation_history WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
            return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

    def add_to_chat_history(self, chat_id: int, role: str, content: str):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ai_conversation_history (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, role, content))
            conn.commit()

    def clear_chat_history(self, chat_id: int):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ai_conversation_history WHERE chat_id = ?", (chat_id,))
            conn.commit()
    
    def set_system_prompt(self, chat_id: int, prompt: str):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO ai_system_prompts (chat_id, prompt) VALUES (?, ?)", (chat_id, prompt))
            conn.commit()

    def get_system_prompt(self, chat_id: int) -> str or None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT prompt FROM ai_system_prompts WHERE chat_id = ?", (chat_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def clear_system_prompt(self, chat_id: int):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ai_system_prompts WHERE chat_id = ?", (chat_id,))
            conn.commit()
