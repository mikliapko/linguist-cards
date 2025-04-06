import logging
import sqlite3

logger = logging.getLogger(__name__)


class SQLiteConnector:
    def __init__(self, db_path):
        self.db_path = db_path
        self._conn = None
        self._cursor = None

    @property
    def conn(self):
        if not self._conn:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = self.conn.cursor()
        return self._cursor

    def execute(self, *args):
        try:
            self.cursor.execute(*args)
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error during database command execution - {e}")

    def db_teardown(self):
        self.cursor.close()
        self.conn.close()


class TranslationDbHandler(SQLiteConnector):
    def __init__(self, db_path, table_name):
        super().__init__(db_path)
        self.table_name = table_name

    @property
    def last_row_id(self) -> int:
        return self.cursor.lastrowid

    def init_table(self):
        self.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} 
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT DEFAULT CURRENT_TIMESTAMP,
                    word TEXT NOT NULL,
                    is_added INTEGER DEFAULT 0,
                    user_id INTEGER NOT NULL
                )
            """
        )

    def insert_translation(self, word: str, user_id: int) -> None:
        self.execute(f"INSERT INTO {self.table_name} (word, user_id) VALUES (?, ?)", (word, user_id))

    def update_is_added_status(self,is_added: bool) -> None:
        self.execute(
            f"UPDATE {self.table_name} SET is_added = ? WHERE id = ?",
            (1 if is_added else 0, self.last_row_id)
        )

    def select_by_word(self, word: str) -> list:
        self.execute(f"SELECT * FROM {self.table_name} WHERE word = ?", (word,))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]  # Convert Row objects to dictionaries
