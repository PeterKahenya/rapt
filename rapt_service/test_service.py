import pytest
import sqlalchemy
from sqlalchemy import create_engine,text,select
from sqlalchemy.orm import sessionmaker
from config import settings,TEST_DATABASE_URL
import models
from schemas import *
import crud
import uuid
from api import app,get_db
from fastapi.testclient import TestClient


pytest_plugins = ('pytest_asyncio',)


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
    


"""Test Schemas"""

#test contenttype, permission, roles schemas
def test_content_type_permissions_roles_schema(db):
    #test create contenttype object
    content_type = ContentTypeCreate(**{"content": "users"})
    assert content_type.content == "users"
    
    #test update contenttype object
    content_type_update = ContentTypeUpdate(**{"content": "users1"})
    assert content_type_update.content == "users1"

    #test get contenttype object
    content_type_get = db.query(models.ContentType).first()
    content_type_schema = ContentTypeInDBBase.model_validate(content_type_get)
    assert content_type_schema.content == content_type_get.content

    #test create permission object
    content_type = db.query(models.ContentType).first()
    permission = PermissionCreate(**{"name": "Can View Users","codename": "view_users","content_type_id": content_type.id})
    assert permission.name == "Can View Users"
    assert permission.codename == "view_users"
    
    #test update permission object
    permission_update = PermissionUpdate(**{"name": "Can View Users1","codename": "view_users1","content_type_id": content_type.id})
    assert permission_update.name == "Can View Users1"
    assert permission_update.codename == "view_users1"

    #test get permission object
    permission_get = db.query(models.Permission).first()
    permission_schema = PermissionInDBBase.model_validate(permission_get)
    assert permission_schema.name == permission_get.name
    assert permission_schema.codename == permission_get.codename
    assert permission_schema.content_type.content == permission_get.content_type.content
    
    #test create role object
    role_create = RoleCreate(**{"name": "Admin","description": "Admin Role"})
    assert role_create.name == "Admin"
    assert role_create.description == "Admin Role"
    
    #test update role object
    permission1 = db.query(models.Permission).first()
    permission2 = db.query(models.Permission).all()[1]
    role_update = RoleUpdate(**{
        "name": "Admin1",
        "description": "Admin Role1",
        "permissions": [permission1.to_dict(),permission2.to_dict()]
        })
    assert role_update.name == "Admin1"
    assert role_update.description == "Admin Role1"

    #test get role object
    role_get = db.query(models.Role).first()
    role_schema = RoleInDBBase.model_validate(role_get)
    assert role_schema.name == role_get.name
    assert role_schema.description == role_get.description
    assert role_schema.permissions[0].name == role_get.permissions[0].name
    assert role_schema.permissions[1].name == role_get.permissions[1].name
    


"""Test CRUD"""

#test contenttype crud operations
@pytest.mark.asyncio
async def test_content_type_permissions_roles_crud(db):
    #create contenttype
    content_type_params = ContentTypeCreate(**{"content": "users1"})
    content_type_db =  await crud.create_obj(db,models.ContentType,content_type_params)
    assert content_type_db in db
    #read contenttype
    content_type_get =  await crud.get_obj(db=db, model=models.ContentType,  id=content_type_db.id)
    assert content_type_get == content_type_db
    with pytest.raises(sqlalchemy.exc.NoResultFound) as e:
        await crud.get_obj(db=db, model=models.ContentType,  id=uuid.uuid4())
    content_types = await crud.get_objects_list(db=db,model=models.ContentType)
    assert content_type_db in content_types
    #update contenttype
    content_type_update = ContentTypeUpdate(**{"content": "users2"})
    content_type_db = await crud.update_obj(db=db,model=models.ContentType,id=content_type_db.id,schema_model=content_type_update)
    assert content_type_db.content == "users2"
    #delete contenttype
    is_deleted = await crud.delete_obj(db=db,model=models.ContentType, id=content_type_db.id)
    assert content_type_db not in db
    
    #create permission
    content_type_params1 = ContentTypeCreate(**{"content": "users2"})
    content_type_db1 =  await crud.create_obj(db,models.ContentType,content_type_params1)
    permission_params = PermissionCreate(**{"name": "Can View Users2","codename": "view_users2","content_type_id": content_type_db1.id})
    permission_db =  await crud.create_obj(db,models.Permission,permission_params)
    assert permission_db in db
    #read permission
    permission_get =  await crud.get_obj(db=db, model=models.Permission,  id=permission_db.id)
    assert permission_get == permission_db
    with pytest.raises(sqlalchemy.exc.NoResultFound) as e:
        await crud.get_obj(db=db, model=models.Permission,  id=uuid.uuid4())
    permissions = await crud.get_objects_list(db=db,model=models.Permission)
    assert permission_db in permissions
    #update permission
    permission_update = PermissionUpdate(**{"name": "Can View Users3","codename": "view_users3","content_type_id": content_type_db1.id})
    permission_db = await crud.update_obj(db=db,model=models.Permission,id=permission_db.id,schema_model=permission_update)
    assert permission_db.name == "Can View Users3"
    #delete permission
    is_deleted = await crud.delete_obj(db=db,model=models.Permission, id=permission_db.id)
    assert permission_db not in db
    
    #create role
    permission_params = PermissionCreate(**{"name": "Can View Users4","codename": "view_users4","content_type_id": content_type_db1.id})
    permission_db =  await crud.create_obj(db,models.Permission,permission_params)
    role_params = RoleCreate(**{"name": "Admin","description": "Admin Role"})
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
    role_update = RoleUpdate(**{
        "name": "Admin1",
        "description": "Admin Role1",
        "permissions": [p.to_dict() for p in permissions]
        })
    role_db = await crud.update_role(db=db,role_id=role_db.id,role_update_data=role_update)
    assert role_db.name == "Admin1"
    #delete role
    is_deleted = await crud.delete_obj(db=db,model=models.Role, id=role_db.id)
    assert role_db not in db
    
    
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
async def test_permissions_roles_api(client,db):
    #get content type
    response = client.get("/api/contenttypes/")
    assert response.status_code == 200
    assert len(response.json()) > 0
    content_type_id = response.json()[0]["id"]
    #create permission
    permission_data = {
        "name": "Can View Roles",
        "codename": "view_roles",
        "content_type_id": str(content_type_id)
    }
    response = client.post("/api/permissions/",json=permission_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Can View Roles"
    permission_id = uuid.UUID(response.json()["id"]) 
    permission = db.execute(select(models.Permission).where(models.Permission.id == permission_id)).scalar_one()
    assert permission in db
    #get permissions
    response = client.get("/api/permissions/")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    #get single permission
    response = client.get(f"/api/permissions/{permission_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Can View Roles"
    #update permission
    permission_data = {
        "name": "Can View Roles1",
        "codename": "view_roles1",
        "content_type_id": str(content_type_id)
    }
    response = client.put(f"/api/permissions/{permission_id}",json=permission_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Can View Roles1"
    #delete permission
    response = client.delete(f"/api/permissions/{permission_id}")
    assert response.status_code == 204
    permission = db.execute(select(models.Permission).where(models.Permission.id == permission_id)).scalar_one_or_none()
    assert permission is None
    
    #create role
    permissions = db.execute(select(models.Permission)).scalars().all()
    role_data = {
        "name": "Admin",
        "description": "Admin Role",
        "permissions": [p.to_dict() for p in permissions]
    }
    response = client.post("/api/roles/",json=role_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Admin"
    #get roles
    response = client.get("/api/roles/")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    #get single role
    role_id = uuid.UUID(response.json()[0]["id"])
    response = client.get(f"/api/roles/{role_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Admin"
    
    #update role
    permissions = db.execute(select(models.Permission)).scalars().all()
    role_data = {
        "name": "Admin1",
        "permissions": [p.to_dict() for p in permissions]
    }
    response = client.put(f"/api/roles/{role_id}",json=role_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Admin1"
    
    #delete role
    response = client.delete(f"/api/roles/{role_id}")
    assert response.status_code == 204
    role = db.execute(select(models.Role).where(models.Role.id == role_id)).scalar_one_or_none()
    assert role is None
    
    
    
    