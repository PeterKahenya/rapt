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
    verification_code_length: int = 6
    verification_code_expiry_seconds: int = 300
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expiry_minutes: int = 60
    smsleopard_base_url: str
    smsleopard_api_key: str
    smsleopard_api_secret: str
    

settings = AppSettings()
DATABASE_URL = f"{settings.mysql_driver}://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"

DEFAULT_PERMISSIONS_CLASSES = ["create","read","update","delete"]

