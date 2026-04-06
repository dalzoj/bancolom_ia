from backend.indexing.indexer import Indexer
from backend.factories.db_factory import DBFactory
from backend.core.config_loader import config
from backend.core.models import PrincipalData


def main():
    
    # Conectar con Base de Datos
    db = DBFactory.create()
    data = db.execute_query(
        f"""
        SELECT * FROM {config.sql_lite_data_table};
        """
    )
    data = [
        PrincipalData(
            url=row["url"],
            title=row["title"],
            extracted_date=row["extracted_date"],
            clean_text=row["clean_text"],
            category=row["category"],
        )
        for row in data
    ]
    print(f"INFO: Se han recuperado {len(data)} elementos a indexar.")
    
    # Ejcutar proceso de indexar
    indexer = Indexer()
    indexer.index_data(data)
    

if __name__ == "__main__":
    main()