import os
import threading
import configparser

from dotenv import load_dotenv


class ConfigLoader:
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
 
    def __init__(self):
            with self._lock:
                if self._initialized:
                    return
                
                # Cargar .env
                load_dotenv(".env")
        
                # Cargar config.cfg
                self._config = configparser.ConfigParser()
                self._config.read("config/config.cfg")
        
                self._initialized = True
            
    
    # -- Helpers
    def get(self, section, key):
        return self._config.get(section, key)
    
    def get_int(self, section, key):
        return self._config.getint(section, key)
    
    def get_float(self, section, key):
        return self._config.getfloat(section, key)
    
    def get_bool(self, section, key):
        return self._config.getboolean(section, key)
    
    def env(self, key):
        return os.getenv(key)

    
    # -- Scraping
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
    
    
    # -- DB
    @property
    def db_provider(self):
        return self.get("db", "provider")
    
    
    # -- SQLite
    @property
    def sql_lite_name(self):
        return self.get("sql_lite", "sql_lite_name")
    
    @property
    def sql_lite_path(self):
        return self.get("sql_lite", "sql_lite_path")
    
    @property
    def sql_lite_data_table(self):
        return self.get("sql_lite", "sql_lite_data_table")
    
    @property
    def sql_lite_conversation_table(self):
        return self.get("sql_lite", "sql_lite_conversation_table")
    

    # -- Base de Datos Vectorial
    @property
    def vector_db_provider(self):
        return self.get("vector_db", "provider")
    
    @property
    def vector_db_index(self):
        return self.get("vector_db", "index")
    
    @property
    def vector_db_dimension(self):
        return self.get_int("vector_db", "dimension")
    
    @property
    def vector_db_metric(self):
        return self.get("vector_db", "metric")
    
    @property
    def vector_db_top_k(self):
        return self.get_int("vector_db", "top_k")
    
    
    # -- Embedding
    @property
    def embedding_provider(self):
        return self.get("embedding", "provider")
    
    @property
    def embedding_model(self):
        return self.get("embedding", "model")
    
    @property
    def embedding_dimension(self):
        return self.get_int("embedding", "dimension")
    
    
    # -- LLM
    @property
    def llm_provider(self):
        return self.get("llm", "provider")
    
    @property
    def llm_model(self):
        return self.get("llm", "model")
    
    @property
    def llm_max_tokens(self):
        return self.get_int("llm", "max_tokens")
    
    @property
    def llm_temperature(self):
        return self.get_float("llm", "temperature")
    
    
    # -- Prompt
    @property
    def prompt_name(self):
        return self.get("prompt", "name")
    
    
    # -- Conversation
    @property
    def conversation_history_limit(self):
        return self.get("conversation", "history_limit")
    

config = ConfigLoader()