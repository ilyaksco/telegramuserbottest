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
            # Buat tabel jika belum ada
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS broadcast_blacklist (
                chat_id INTEGER PRIMARY KEY
            )
            """)
            self.conn.commit()
            logging.info("Database setup successful. Blacklist table is ready.")
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