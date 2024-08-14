import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from models import *
from config import settings,TEST_DATABASE_URL


pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def db():
    engine = create_engine(TEST_DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.test_database_name};"))
    engine = create_engine(f"{TEST_DATABASE_URL}/{settings.test_database_name}")
    Model.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal(bind=engine)
    yield session
    session.rollback()
    session.close()
    Model.metadata.drop_all(bind=engine)
    engine.dispose()


"""Test Models"""

#test content_type creation 
def test_content_type_creation(db):
    content_type = ContentType(content = "users")
    db.add(content_type)
    db.commit()
    assert content_type in db

# test permission creation
def test_permission_creation(db):
    content_type = ContentType(content = "users")
    permission = Permission(name="Can View Users",codename="view_users",content_type=content_type)
    db.add(permission)
    db.commit()
    assert permission in db


#test role creation
def test_role_creation(db):
    content_type = ContentType(content = "users")
    permission1 = Permission(name="Can View Users",codename="view_users",content_type=content_type)
    permission2 = Permission(name="Can Edit Users",codename="edit_users",content_type=content_type)
    role = Role(name="Admin",description="Admin Role")
    role.permissions.append(permission1)
    role.permissions.append(permission2)
    db.add(role)
    db.commit()
    assert role in db


