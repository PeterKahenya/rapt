import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
import models
from pydantic_settings import BaseSettings
from pydantic_settings import BaseSettings
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
import models


class Settings(BaseSettings):
    mysql_driver: str = "mysql+pymysql"
    test_database_host: str
    test_database_port: int
    test_database_user: str
    test_database_password: str
    test_database_name: str
    verification_code_length: int = 6
    verification_code_expiry_seconds: int = 300
    jwt_secret_key: str = "iufidfufidsfudfisudfsudfiudfidufd8f9df89f8d98fdf98"
    jwt_algorithm: str = "HS256"
    access_token_expiry_minutes: int = 60

settings = Settings()
TEST_DATABASE_URL = f"{settings.mysql_driver}://{settings.test_database_user}:{settings.test_database_password}@{settings.test_database_host}:{settings.test_database_port}"



SessionLocal = None
engine = None

@pytest.fixture(scope="session")
def db():
    engine = create_engine(TEST_DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.test_database_name};"))
    engine = create_engine(f"{TEST_DATABASE_URL}/{settings.test_database_name}")
    models.Model.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal(bind=engine)
    yield session
    session.rollback()
    session.close()
    models.Model.metadata.drop_all(bind=engine)
    engine.dispose()