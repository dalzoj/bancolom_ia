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
    
config = ConfigLoader()