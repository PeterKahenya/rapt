

from pydantic_settings import BaseSettings
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import models
from .seed import seed_db

class Settings(BaseSettings):
    mysql_driver: str = "mysql+pymysql"
    test_database_host: str
    test_database_port: str
    test_database_user: str
    test_database_password: str
    test_database_name: str
    verification_code_length: int = 6
    verification_code_expiry_seconds: int = 300
    jwt_algorithm: str = "HS256"
    jwt_secret_key: str
    access_token_expiry_seconds: int = 3600

    model_config = {
        "env_file": "../.env",
        "extra": "allow"
    }

test_settings = Settings()
FULL_URL = f"{test_settings.mysql_driver}://{test_settings.test_database_user}:{test_settings.test_database_password}@{test_settings.test_database_host}:{test_settings.test_database_port}/{test_settings.test_database_name}"
engine = create_engine(FULL_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

@pytest.fixture(scope="session")
def db():
    models.Model.metadata.create_all(bind=engine)
    testing_db_session = SessionLocal()
    seed_db(testing_db_session)
    yield testing_db_session
    testing_db_session.rollback()
    testing_db_session.close()
    models.Model.metadata.drop_all(bind=engine)
    engine.dispose()
