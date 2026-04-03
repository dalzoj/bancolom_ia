from backend.core.config_loader import config


class DBFactory:

    @staticmethod
    def create():

        provider = config.db_provider
        
        if provider == "sql_lite":
            from backend.core.providers.db.sql_lite_handler import SQLLiteHanlder
            return SQLLiteHanlder()