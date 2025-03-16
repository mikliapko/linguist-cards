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

    def init_table(self):
        self.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} 
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                word TEXT NOT NULL
            )
            """
        )

    def insert(self, word: str):
        self.execute(f"INSERT INTO {self.table_name} (word) VALUES (?)", (word,))
