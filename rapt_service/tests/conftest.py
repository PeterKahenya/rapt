import pytest
from sqlalchemy import create_engine, select,text
from sqlalchemy.orm import sessionmaker
import models
from pydantic_settings import BaseSettings
from faker import Faker
from api import app
from depends import get_db
from fastapi.testclient import TestClient
from init import initialize_db



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
faker = Faker()


# seed database with faker data for all models
def seed_db(db):
    # faker add content types
    for i in range(10):
        content_type = models.ContentType(content=faker.unique.word())
        db.add(content_type)
    db.commit()
    # faker add permissions
    for i in range(10):
        content_type = db.execute(select(models.ContentType)).scalars().first()
        permission = models.Permission(name=faker.word(),codename=faker.unique.word(),content_type=content_type)
        db.add(permission)
    db.commit()
    # faker add roles
    for i in range(10):
        permissions = db.execute(select(models.Permission)).scalars().all()[0:5]
        role = models.Role(name=faker.word(),description=faker.word(),permissions=permissions)
        db.add(role)
    db.commit()
    # faker add users
    for i in range(10):
        user = models.User(phone=faker.unique.phone_number()[0:11],name=faker.name(),roles=db.execute(select(models.Role)).scalars().all()[0:5])
        db.add(user)
    db.commit()
    # faker add contacts
    user = db.execute(select(models.User)).scalars().first()
    for i in range(20):
        contact = models.User(phone=faker.unique.phone_number()[0:11],name=faker.name())
        user.contacts.append(contact)
        db.add(user)
    db.commit()
    # faker client apps
    for i in range(10):
        user = db.execute(select(models.User)).scalars().first()
        client_app = models.ClientApp(name=faker.word(),description=faker.word(),user_id=user.id)
        db.add(client_app)
    db.commit()
    # faker add chatrooms
    members = db.execute(select(models.User)).scalars().all()[0:15]
    for i in range(11):
        chatroom = models.ChatRoom(fcm_room_id=faker.uuid4(),socket_room_id=faker.uuid4(),members=[members[0],members[i+1]])
        db.add(chatroom)
    db.commit()
    # faker add chat groups
    chatrooms = db.execute(select(models.ChatRoom)).scalars().all()[0:7]
    for i in range(4):
        chat_group = models.Group(name=faker.word(),description=faker.text(),chatroom=chatrooms[i])
        db.add(chat_group)
    db.commit()
    # faker add chat messages
    for i in range(6):
        chatroom = chatrooms[i]
        message = models.Chat(message=faker.text(),room=chatroom,sender=chatroom.members[0 if i%2==0 else 1])
        db.add(message)
    db.commit()
    # faker add media
    chats = db.execute(select(models.Chat)).scalars().all()[0:6]
    for i in range(5):
        media = models.Media(link=faker.url(),file_type=faker.file_extension(),chat=chats[i])
        db.add(media)
    db.commit()



@pytest.fixture(scope="session")
def db():
    engine = create_engine(TEST_DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.test_database_name};"))
    engine = create_engine(f"{TEST_DATABASE_URL}/{settings.test_database_name}")
    models.Model.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal(bind=engine)
    seed_db(session)
    yield session
    session.rollback()
    session.close()
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
    initialize_db(db)
    yield TestClient(app)