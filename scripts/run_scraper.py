from backend.scraping.finder import Finder
from backend.scraping.cleaner import Cleander
from backend.core.models import PrincipalData
from backend.core.factories.db_factory import DBFactory
from backend.core.config_loader import config


def main():
    
    principal_data = []
    db = DBFactory.create()
    
    finder = Finder()
    raw_pages = finder.find()
    print(f'INFO: Se han guardado {len(raw_pages)} elementos.')
    
    cleaner = Cleander()
    for page in raw_pages:
        clean_text = cleaner.clean_page(page["url"], page["html"])
        
        principal_data = PrincipalData(
            url = page["url"],
            title = page["title"],
            extracted_date = page["extracted_date"],
            clean_text = clean_text
        )
        
        db.execute_query(
            f"""
            INSERT OR REPLACE INTO {config.sql_lite_table}
                (url, title, extracted_date, clean_text)
            VALUES
                (:url, :title, :extracted_date, :clean_text)
            """, {
                "url": principal_data.url,
                "title": principal_data.title,
                "extracted_date": principal_data.extracted_date,
                "clean_text": principal_data.clean_text
                }
        )
        
    sample = db.execute_query(f"SELECT * FROM {config.sql_lite_table} LIMIT 5", ())
    for row in sample:
        print(row)

if __name__ == "__main__":
    main()