from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger("rapt-api")
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


class AppSettings(BaseSettings):
    mysql_driver: str = "mysql+pymysql"
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str

settings = AppSettings()
DATABASE_URL = f"{settings.mysql_driver}://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"

