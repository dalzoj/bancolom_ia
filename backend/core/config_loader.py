import configparser
from dotenv import load_dotenv

class ConfigLoader:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
 
    def __init__(self):
        if self._initialized:
            return
        
        # Cargar .env
        load_dotenv(".env")
 
        # Cargar config.cfg
        self._config = configparser.ConfigParser()
        self._config.read("config/config.cfg")
 
        self._initialized = True
    
    
    ## HELPERS
    def get(self, section, key):
        return self._config.get(section, key)
    def get_int(self, section, key):
        return self._config.getint(section, key)
    def get_float(self, section, key):
        return self._config.getfloat(section, key)
    def get_bool(self, section, key):
        return self._config.getboolean(section, key)

    
    ## SCRAPPING
    @property
    def scraping_base_url(self):
        return self.get("scraping", "base_url")
    @property
    def scraping_max_pages(self):
        return self.get_int("scraping", "max_pages")
    @property
    def scraping_max_depth(self):
        return self.get_int("scraping", "max_depth")
    @property
    def scraping_respect_robots(self):
        return self.get_bool("scraping", "respect_robots")
    @property
    def scraping_delay(self):
        return self.get_float("scraping", "delay")
    @property
    def scraping_output_path(self):
        return self.get("scraping", "output_path")
    
    
    ## DB
    @property
    def db_provider(self):
        return self.get("db", "provider")
    
    
    ## SQL Lite
    @property
    def sql_lite_name(self):
        return self.get("sql_lite", "sql_lite_name")
    @property
    def sql_lite_path(self):
        return self.get("sql_lite", "sql_lite_path")
    @property
    def sql_lite_table(self):
        return self.get("sql_lite", "sql_lite_table")


config = ConfigLoader()