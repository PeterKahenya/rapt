from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger("rapt-api")
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


class AppSettings(BaseSettings):
    mysql_driver: str
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str
    test_database_host: str
    test_database_port: int
    test_database_user: str
    test_database_password: str
    test_database_name: str
    smsleopard_api_key: str
    smsleopard_api_secret: str
    smsleopard_base_url: str

settings = AppSettings()
TEST_DATABASE_URL = f"{settings.mysql_driver}://{settings.test_database_user}:{settings.test_database_password}@{settings.test_database_host}:{settings.test_database_port}"
DATABASE_URL = f"{settings.mysql_driver}://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"

