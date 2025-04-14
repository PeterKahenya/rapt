from pydantic_settings import BaseSettings
import logging
from honeybadger.contrib.logger import HoneybadgerHandler

class AppSettings(BaseSettings):
    mysql_driver: str = "mysql+pymysql"
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str
    verification_code_length: int = 6
    verification_code_expiry_seconds: int = 300
    jwt_algorithm: str = "HS256"
    access_token_expiry_seconds: int = 3600
    jwt_secret_key: str
    smsleopard_base_url: str 
    smsleopard_api_key: str
    smsleopard_api_secret: str
    mailtrap_api_token: str 
    superuser_phone: str
    honeybadger_api_key: str

    model_config = {
        "env_file": "../.env",
        "extra": "allow"
    }
    
settings = AppSettings()

hb_handler = HoneybadgerHandler(api_key=settings.honeybadger_api_key)
hb_handler.setLevel(logging.DEBUG)
hb_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger = logging.getLogger('honeybadger')
logger.addHandler(hb_handler)


def get_database_url():
    return f"{settings.mysql_driver}://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"

DEFAULT_PERMISSIONS_CLASSES = ["create","read","update","delete"]
