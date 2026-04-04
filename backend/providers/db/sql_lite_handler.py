from pathlib import Path
import sqlite3

from backend.interfaces.db_interface import DBInterface
from backend.core.config_loader import config


class SQLiteHandler(DBInterface):
    
    def __init__(self):
        self._db_name = Path(config.sql_lite_name)
        self._db_path = Path(config.sql_lite_path)
        self._db_table = config.sql_lite_table
        self._db_full_path = self._db_path / self._db_name
        self._conn = None
        self._locate_db()
        self._connect()
        
    def _create_table(self):
        self.execute_query(
            f"""
            CREATE TABLE IF NOT EXISTS {self._db_table} (
                url TEXT PRIMARY KEY,
                title TEXT,
                extracted_date TEXT,
                clean_text TEXT
            )
            """, ()
        )
        
    def _locate_db(self):
        self._db_path.mkdir(parents=True, exist_ok=True)
        if self._db_full_path.exists():
            print(f"INFO: Base de datos encontrada en {self._db_full_path}")
        else:
            print(f"INFO: Base de datos no encontrada, creando en {self._db_full_path}")
            
    def _connect(self):
        self._conn = sqlite3.connect(self._db_full_path)
        self._conn.row_factory = sqlite3.Row
        self._create_table()
        print(f"INFO: Conectado a SQLite en {self._db_full_path}")

    def execute_query(self, query, values):
        print(f"INFO: Ejecutando query")
        cursor = self._conn.cursor()
        cursor.execute(query, values)
        self._conn.commit()
        return [dict(row) for row in cursor.fetchall()]