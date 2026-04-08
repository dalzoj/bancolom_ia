from backend.core.config_loader import config


class DBFactory:

    @staticmethod
    def create():

        provider = config.db_provider

        if provider == "sql_lite":
            from backend.providers.db.sql_lite_handler import SQLiteHandler
            return SQLiteHandler()

        raise ValueError(f"Provedor de BD '{provider}' no está soportado.")
