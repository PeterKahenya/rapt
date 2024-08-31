from pydantic_settings import BaseSettings
import pytest
import sqlalchemy
from sqlalchemy import create_engine,text,select
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import crud
import models
import schemas
import uuid
from api import app,get_db


pytest_plugins = ('pytest_asyncio',)

class Settings(BaseSettings):
    mysql_driver: str = "mysql+pymysql"
    test_database_host: str
    test_database_port: int
    test_database_user: str
    test_database_password: str
    test_database_name: str

settings = Settings()
TEST_DATABASE_URL = f"{settings.mysql_driver}://{settings.test_database_user}:{settings.test_database_password}@{settings.test_database_host}:{settings.test_database_port}"

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


"""Test Models"""

# test content_type, permissions, roles
def test_content_type_permissions_roles_models(db):
    #test content_type creation 
    content_type = models.ContentType(content = "users")
    db.add(content_type)
    db.commit()
    assert content_type in db
    # test permission creation
    permission1 = models.Permission(name="Can View Users",codename="view_users",content_type=content_type)
    db.add(permission1)
    db.commit()
    assert permission1 in db
    #test role creation
    permission2 = models.Permission(name="Can Edit Users",codename="edit_users",content_type=content_type)
    role = models.Role(name="Admin",description="Admin Role")
    role.permissions.append(permission1)
    role.permissions.append(permission2)
    db.add(role)
    db.commit()
    assert role in db
    
#test create user, add contacts, roles
@pytest.mark.asyncio
async def test_add_user_contacts_roles_clientapp_models(db):
    user = models.User(name="Test User", phone="1234567890")
    db.add(user)
    db.commit()
    assert user in db
    user1 = models.User(name="Test User 1", phone="1234567891")
    user2 = models.User(name="Test User 2", phone="1234567892")
    user.contacts.append(user1)
    user.contacts.append(user2)
    db.add(user)
    db.commit()
    assert user1 in user.contacts
    assert user2 in user.contacts
    permission1 = db.execute(select(models.Permission).where(models.Permission.name == "Can View Users")).scalar_one()
    permission2 = db.execute(select(models.Permission).where(models.Permission.name == "Can Edit Users")).scalar_one()
    role = models.Role(name="Admin",description="Admin Role")
    role.permissions.append(permission1)
    role.permissions.append(permission2)
    db.add(role)
    db.commit()
    assert role in db
    
    #test clientapp creation
    clientapp = models.ClientApp(name="Test App",description="Test App Description",user_id=user.id)
    db.add(clientapp)
    db.commit()
    assert clientapp in db
    assert clientapp.user == user
    assert clientapp.client_id != None
    assert clientapp.client_secret != None
    
    #test user verification creation and validation
    user = await user.create_verification_code(db)
    assert user.phone_verification_code != None
    validation_status = await user.validate_verification_code(user.phone_verification_code)
    assert validation_status == True
    
    #test user jwt token creation and validation
    token = user.create_jwt_token()
    assert user.phone == models.User.verify_jwt_token(db,token)
    
    
    
    


"""Test Schemas"""
#test contenttype, permission, roles schemas
def test_user_contacts_roles_clientapp_schema(db):
    #test create contenttype object
    content_type = schemas.ContentTypeCreate(**{"content": "users"})
    assert content_type.content == "users"

    #test get contenttype object
    content_type_get = db.query(models.ContentType).first()
    content_type_schema = schemas.ContentTypeInDBBase.model_validate(content_type_get)
    assert content_type_schema.content == content_type_get.content

    #test create permission object
    content_type = db.query(models.ContentType).first()
    permission = schemas.PermissionCreate(**{"name": "Can View Users","codename": "view_users","content_type_id": content_type.id})
    assert permission.name == "Can View Users"
    assert permission.codename == "view_users"

    #test get permission object
    permission_get = db.query(models.Permission).first()
    permission_schema = schemas.PermissionInDBBase.model_validate(permission_get)
    assert permission_schema.name == permission_get.name
    assert permission_schema.codename == permission_get.codename
    assert permission_schema.content_type.content == permission_get.content_type.content
    
    #test create role object
    role_create = schemas.RoleCreate(**{"name": "Admin","description": "Admin Role"})
    assert role_create.name == "Admin"
    assert role_create.description == "Admin Role"
    
    #test update role object
    permission1 = db.query(models.Permission).first()
    permission2 = db.query(models.Permission).all()[1]
    role_update = schemas.RoleUpdate(**{
        "name": "Admin1",
        "description": "Admin Role1",
        "permissions": [permission1.to_dict(),permission2.to_dict()]
        })
    assert role_update.name == "Admin1"
    assert role_update.description == "Admin Role1"

    #test get role object
    role_get = db.query(models.Role).first()
    role_schema = schemas.RoleInDBBase.model_validate(role_get)
    assert role_schema.name == role_get.name
    assert role_schema.description == role_get.description
    assert role_schema.permissions[0].name == role_get.permissions[0].name
    assert role_schema.permissions[1].name == role_get.permissions[1].name
    
    #test create user object
    user = schemas.UserCreate(**{
        "phone": "1234567890",
        "name": "Test User"
    })
    assert user.phone == "1234567890" and user.name == "Test User"
    #test update user object
    user_update = schemas.UserUpdate(**{
        "phone": "1234567891",
        "name": "Test User 1",
        "is_superuser": True,
        "roles": [role_schema.model_dump()]        
    })
    assert user_update.phone == "1234567891"
    #test get user object
    user_get = db.query(models.User).first()
    user_schema = schemas.UserInDBBase.model_validate(user_get)
    assert user_schema.phone == user_get.phone
    
    #test create clientapp object
    clientapp = schemas.ClientAppCreate(**{
        "name": "Test App",
        "description": "Test App Description",
        "user_id": user_get.id
    })
    assert clientapp.name == "Test App" and clientapp.description == "Test App Description"
    #test get clientapp object
    clientapp_get = db.execute(select(models.ClientApp)).scalar_one()
    clientapp_schema = schemas.ClientAppInDBBase.model_validate(clientapp_get)
    assert clientapp_schema.name == clientapp_get.name
    #test clientapp update object
    clientapp_update = schemas.ClientAppUpdate(**{
        "name": "Test App 1",
        "description": "Test App Description 1",
        "user_id": user_get.id
    })
    assert clientapp_update.name == "Test App 1" and clientapp_update.description == "Test App Description 1"
      
    


"""Test CRUD"""

#test contenttype crud operations
@pytest.mark.asyncio
async def test_content_type_permissions_roles_crud(db):  
    content_types =  await crud.get_objects_list(db,models.ContentType)
    content_type_db = content_types[0]
    #create role
    permission_params = schemas.PermissionCreate(**{"name": "Can View Users4","codename": "view_users4","content_type_id": content_type_db.id})
    permission_db =  await crud.create_obj(db,models.Permission,permission_params)
    role_params = schemas.RoleCreate(**{"name": "Admin","description": "Admin Role"})
    role_db =  await crud.create_obj(db,models.Role,role_params)
    assert role_db in db
    #read role
    role_get =  await crud.get_obj(db=db, model=models.Role,  id=role_db.id)
    assert role_get == role_db
    with pytest.raises(sqlalchemy.exc.NoResultFound) as e:
        await crud.get_obj(db=db, model=models.Role,  id=uuid.uuid4())
    roles = await crud.get_objects_list(db=db,model=models.Role)
    assert role_db in roles
    #update role
    permissions = await crud.get_objects_list(db=db,model=models.Permission)
    role_update = schemas.RoleUpdate(**{
        "name": "Admin1",
        "description": "Admin Role1",
        "permissions": [p.to_dict() for p in permissions]
        })
    role_db = await crud.update_role(db=db,role_id=role_db.id,role_update_data=role_update)
    assert role_db.name == "Admin1"
    #delete role
    is_deleted = await crud.delete_obj(db=db,model=models.Role, id=role_db.id)
    assert role_db not in db
    
    #create user
    user_params = schemas.UserCreate(**{
        "phone": "1234567896",
        "name": "Test User"
    })
    user_db = await crud.create_obj(db,models.User,user_params)
    assert user_db in db
    #read user
    user_get = await crud.get_obj(db=db,model=models.User,id=user_db.id)
    assert user_get == user_db
    with pytest.raises(sqlalchemy.exc.NoResultFound) as e:
        await crud.get_obj(db=db, model=models.User,  id=uuid.uuid4())
    users = await crud.get_objects_list(db=db,model=models.User)
    assert user_db in users
    
    #create clientapp
    clientapp_params = schemas.ClientAppCreate(**{
        "name": "Test App",
        "description": "Test App Description",
        "user_id": user_db.id
    })
    clientapp_db = await crud.create_obj(db,models.ClientApp,clientapp_params)
    assert clientapp_db in db
    
    
"""Test API"""

@pytest.fixture(scope="session")
def client(db):
    def get_test_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    
@pytest.mark.asyncio
async def test_initialize_api(client,db):
    response = client.get("/initialize/")
    assert response.status_code == 200
    assert response.json()["message"] == "System Initialized"

#test CRUD api calls for permissions, roles
@pytest.mark.asyncio
async def test_permissions_roles_users_clientapps_api(client,db):
    #get permissions
    response = client.get("/permissions/")
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    permission_id = uuid.UUID(response.json()["data"][0]["id"])
    response = client.get("/permissions?q=Delete")
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    assert "Delete" in response.json()["data"][0]["name"]
    #get single permission
    response = client.get(f"/permissions/{permission_id}")
    assert response.status_code == 200
    assert response.json()["name"] != None
    
    #create role
    permissions = db.execute(select(models.Permission)).scalars().all()
    role_data = {
        "name": "Admin",
        "description": "Admin Role",
        "permissions": [p.to_dict() for p in permissions]
    }
    response = client.post("/roles/",json=role_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Admin"
    #get roles
    response = client.get("/roles/")
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    #get single role
    role_id = uuid.UUID(response.json()["data"][0]["id"])
    response = client.get(f"/roles/{role_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Admin"
    
    #update role
    permissions = db.execute(select(models.Permission)).scalars().all()
    role_data = {
        "name": "Admin1",
        "permissions": [p.to_dict() for p in permissions]
    }
    response = client.put(f"/roles/{role_id}",json=role_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Admin1"
    
    #delete role
    response = client.delete(f"/roles/{role_id}")
    assert response.status_code == 204
    role = db.execute(select(models.Role).where(models.Role.id == role_id)).scalar_one_or_none()
    assert role is None
    
    # test pagination
    response = client.get("/permissions/?page=1&size=1")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["total"] >= 1
    assert response.json()["page"] == 1
    assert response.json()["size"] == 1
    response = client.get("/permissions/?page=2&size=1")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["total"] >= 1
    assert response.json()["page"] == 2
    assert response.json()["size"] == 1
    response = client.get("/permissions/?page=1&size=2")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["total"] >= 1
    assert response.json()["page"] == 1
    assert response.json()["size"] == 2
    # test search
    response = client.get("/permissions/?q=Delete")
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    assert "Delete" in response.json()["data"][0]["name"]
    
    #test list/filter/search users
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    response = client.get("/users/?q=Test")
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    response = client.get("/users/",params={"name__ilike": "User"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    user_id = db.execute(select(models.User)).scalars().first().id
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] != None
    response = client.put(f"/users/{user_id}",json={"name": "Test User 1"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test User 1"
    
    #test user onboard/verification/login
    response = client.post("/users/onboard/",json={"phone": "1234567890","name": "Test User"})
    assert response.status_code == 200
    assert response.json()["message"] == "Verification Code Sent"
    #verify user by sending verification code
    code = db.execute(select(models.User).where(models.User.phone == "1234567890")).scalar_one().phone_verification_code
    response = client.post("/users/verify/",json={"phone": "1234567890","phone_verification_code": code})
    assert response.status_code == 200
    assert response.json()["phone"] == "1234567890"
    
    #test add contacts
    contacts = [
        {"name": "Test Contact 1","phone": "1234567991"},
        {"name": "Test Contact 2","phone": "1234567992"}
    ]
    response = client.put(f"/users/{user_id}",json={"contacts": contacts})
    
    print(f"Contact add response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["contacts"] != None
    assert response.json()["contacts"][0]["name"] == "Test Contact 1" \
            or response.json()["contacts"][0]["name"] == "Test Contact 2"
    
    #test add roles
    role_db = db.execute(select(models.Role)).scalars().first()
    # print(role_db)
    response = client.put(f"/users/{user_id}",json={"roles": [role_db.to_dict()]})
    assert response.status_code == 200
    assert role_db in db.execute(select(models.User).where(models.User.id == user_id)).scalar_one().roles

    #test create clientapp
    response = client.post("/clientapps/",json={"name": "Test App","description": "Test App Description","user_id": str(user_id)})
    print(f"Clientapp create response: {response.json()}")  
    assert response.status_code == 201
    assert response.json()["name"] == "Test App"
    #test get clientapps
    response = client.get("/clientapps/")
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    #test get single clientapp
    clientapp_id = uuid.UUID(response.json()["data"][0]["id"])
    response = client.get(f"/clientapps/{str(clientapp_id)}")
    assert response.status_code == 200
    assert response.json()["name"] != None
    #test update clientapp
    response = client.put(f"/clientapps/{clientapp_id}",json={"name": "Test App 1","description": "Test App Description 1","user_id": str(user_id)})
    assert response.status_code == 200
    assert response.json()["name"] == "Test App 1"
    #test delete clientapp
    response = client.delete(f"/clientapps/{clientapp_id}")
    assert response.status_code == 204
    clientapp = db.execute(select(models.ClientApp).where(models.ClientApp.id == clientapp_id)).scalar_one_or_none()
    assert clientapp is None