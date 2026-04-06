from pathlib import Path

import pandas as pd

from backend.scraping.finder import Finder
from backend.scraping.cleaner import Cleaner
from backend.core.models import PrincipalData
from backend.factories.db_factory import DBFactory
from backend.core.config_loader import config


def main():
    
    # Conectar con Base de Datos
    db = DBFactory.create()
    
    # Ejecutar el finder
    finder = Finder()
    finder.find()
    
    # Cargar información raw
    raw_path = Path(config.scraping_output_path) / "raw_data.parquet"
    df = pd.read_parquet(raw_path)
    raw_pages = df.to_dict(orient="records")
    print(f"INFO: Se cargaron {len(raw_pages)} elementos.")
    
    # Ejecutar el cleaner
    cleaner = Cleaner()
    principal_data = []
    for page in raw_pages:
        clean_text = cleaner.clean_page(page["url"], page["html"])
        principal_data.append(PrincipalData(
            url=page["url"],
            title=page["title"],
            extracted_date=page["extracted_date"],
            clean_text=clean_text
        ))
        
    # Insertar información en DB
    for data in principal_data:
        db.execute_query(
            f"""
            INSERT OR REPLACE INTO {config.sql_lite_data_table}
                (url, title, extracted_date, clean_text)
            VALUES
                (:url, :title, :extracted_date, :clean_text)
            """, {
                "url": data.url,
                "title": data.title,
                "extracted_date": data.extracted_date,
                "clean_text": data.clean_text
            }
        )

if __name__ == "__main__":
    main()