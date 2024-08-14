import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from config import settings,TEST_DATABASE_URL
from models import *
from schemas import *


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

# test content_type, permissions, roles
def test_content_type_permissions_roles(db):
    #test content_type creation 
    content_type = ContentType(content = "users")
    db.add(content_type)
    db.commit()
    assert content_type in db
    # test permission creation
    permission1 = Permission(name="Can View Users",codename="view_users",content_type=content_type)
    db.add(permission1)
    db.commit()
    assert permission1 in db
    #test role creation
    permission2 = Permission(name="Can Edit Users",codename="edit_users",content_type=content_type)
    role = Role(name="Admin",description="Admin Role")
    role.permissions.append(permission1)
    role.permissions.append(permission2)
    db.add(role)
    db.commit()
    assert role in db
    


"""Test Schemas"""

#test contenttype, permission, roles schemas
def test_contenttype_schema(db):
    #test create contenttype object
    content_type = ContentTypeCreate(**{"content": "users"})
    assert content_type.content == "users"
    
    #test update contenttype object
    content_type_update = ContentTypeUpdate(**{"content": "users1"})
    assert content_type_update.content == "users1"

    #test get contenttype object
    content_type_get = db.query(ContentType).first()
    content_type_schema = ContentTypeInDBBase.model_validate(content_type_get)
    assert content_type_schema.content == content_type_get.content

    #test create permission object
    content_type = db.query(ContentType).first()
    permission = PermissionCreate(**{"name": "Can View Users","codename": "view_users","content_type_id": content_type.id})
    assert permission.name == "Can View Users"
    assert permission.codename == "view_users"
    
    #test update permission object
    permission_update = PermissionUpdate(**{"name": "Can View Users1","codename": "view_users1","content_type_id": content_type.id})
    assert permission_update.name == "Can View Users1"
    assert permission_update.codename == "view_users1"

    #test get permission object
    permission_get = db.query(Permission).first()
    permission_schema = PermissionInDBBase.model_validate(permission_get)
    assert permission_schema.name == permission_get.name
    assert permission_schema.codename == permission_get.codename
    assert permission_schema.content_type.content == permission_get.content_type.content
    
    #test create role object
    role_create = RoleCreate(**{"name": "Admin","description": "Admin Role"})
    assert role_create.name == "Admin"
    assert role_create.description == "Admin Role"
    
    #test update role object
    permission1 = db.query(Permission).first()
    permission2 = db.query(Permission).all()[1]
    role_update = RoleUpdate(**{
        "name": "Admin1",
        "description": "Admin Role1",
        "permissions": [permission1.to_dict(),permission2.to_dict()]
        })
    assert role_update.name == "Admin1"
    assert role_update.description == "Admin Role1"

    #test get role object
    role_get = db.query(Role).first()
    role_schema = RoleInDBBase.model_validate(role_get)
    assert role_schema.name == role_get.name
    assert role_schema.description == role_get.description
    assert role_schema.permissions[0].name == role_get.permissions[0].name
    assert role_schema.permissions[1].name == role_get.permissions[1].name