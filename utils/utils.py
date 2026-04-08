import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = ".storage/db/principal_db"
OUTPUT_PATH = Path(".storage/view_tables")
TABLES = ["principal_data", "conversation_data", "conversation_summary"]
EXCEL_FILE = True

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(DB_PATH)

dataframes = {}
for table in TABLES:
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.replace(r"\s+", " ", regex=True).str.strip()
    df.to_csv(OUTPUT_PATH / f"{table}.csv", index=False, sep="|")
    dataframes[table] = df
    print(f"INFO: Exportado CSV {table} con {len(df)} registros")

if EXCEL_FILE:
    with pd.ExcelWriter(OUTPUT_PATH / "tables_export.xlsx") as writer:
        for table, df in dataframes.items():
            df.to_excel(writer, sheet_name=table, index=False)
    print(f"INFO: Exportado CSV {table} con {len(df)} registros")

conn.close()
print(f"INFO: Exportación completa en: {OUTPUT_PATH.resolve()}")
