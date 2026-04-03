from backend.scraping.finder import Finder

def main():
    
    finder = Finder()
    
    raw_pages = finder.find()
    
if __name__ == "__main__":
    main()