

from logging import config
from pydantic_settings import BaseSettings
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import models
from .seed import seed_db
import config

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
    superuser_phone: str = "0200100210"

    model_config = {
        "env_file": "../.env",
        "extra": "allow"
    }

test_settings = Settings()
def get_test_db_uri():
    FULL_URL = f"{test_settings.mysql_driver}://{test_settings.test_database_user}:{test_settings.test_database_password}@{test_settings.test_database_host}:{test_settings.test_database_port}/{test_settings.test_database_name}"
    return FULL_URL
config.get_database_url = get_test_db_uri
engine = create_engine(get_test_db_uri())
models.Model.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

from main import app
from depends import get_db
from init import initialize_db

@pytest.fixture(scope="session")
def db():
    testing_db_session = SessionLocal()
    seed_db(testing_db_session)
    initialize_db(testing_db_session, test_settings, is_test=True)
    yield testing_db_session
    testing_db_session.rollback()
    testing_db_session.close()
    models.Model.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="session")
def client(db):
    def get_test_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
