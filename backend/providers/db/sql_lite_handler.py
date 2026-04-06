import sqlite3
import threading
from pathlib import Path

from backend.interfaces.db_interface import DBInterface
from backend.core.config_loader import config


class SQLiteHandler(DBInterface):

    def __init__(self):
        self._db_path = Path(config.sql_lite_path)
        self._db_full_path = self._db_path / config.sql_lite_name
        self._local = threading.local()

        self._db_path.mkdir(parents=True, exist_ok=True)

        if self._db_full_path.exists():
            print(f'INFO: Base de datos encontrada en {self._db_full_path}')
        else:
            print(f'INFO: Base de datos encontrada, creando en {self._db_full_path}')

        self._create_tables()

    def _connect(self):
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(str(self._db_full_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return self._local.conn

    def _create_tables(self):
        self.execute_query(
            f"""
            CREATE TABLE IF NOT EXISTS {config.sql_lite_data_table} (
                url TEXT PRIMARY KEY,
                title TEXT,
                extracted_date TEXT,
                clean_text TEXT
            );
            """
        )
        self.execute_query(
            f"""
            CREATE TABLE IF NOT EXISTS {config.sql_lite_conversation_table} (
                conversation_id TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                message_timestamp TEXT NOT NULL,
                human_message TEXT NOT NULL,
                llm_response TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                model_name TEXT,
                prompt_version TEXT,
                interaction_time REAL,
                PRIMARY KEY (conversation_id, message_id)
            );
            """
        )

    def execute_query(self, query, values = ()):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        return [dict(row) for row in cursor.fetchall()]