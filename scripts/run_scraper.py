from backend.scraping.finder import Finder
from backend.scraping.cleaner import Cleander
from backend.core.models import PrincipalData

def main():
    
    principal_data = []
    
    finder = Finder()
    raw_pages = finder.find()
    print(f'INFO: Se han guardado {len(raw_pages)} elementos.')
    
    cleaner = Cleander()
    for page in raw_pages:
        clean_text = cleaner.clean_page(page["url"], page["html"])
        
        principal_data.append(
            PrincipalData(
                url = page["url"],
                title = page["title"],
                extracted_date = page["extracted_date"],
                clean_text = clean_text
            )
        )
        
    print(principal_data)

    
if __name__ == "__main__":
    main()