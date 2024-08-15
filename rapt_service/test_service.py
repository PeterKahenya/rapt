import pytest
import sqlalchemy
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from config import settings,TEST_DATABASE_URL
import models
from schemas import *
import crud
import uuid

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
    content_type_params = ContentTypeCreate(**{"content": "users"})
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
    content_type_update = ContentTypeUpdate(**{"content": "users1"})
    content_type_db = await crud.update_obj(db=db,model=models.ContentType,id=content_type_db.id,schema_model=content_type_update)
    assert content_type_db.content == "users1"
    #delete contenttype
    content_type_db = await crud.delete_obj(db=db,model=models.ContentType, id=content_type_db.id)
    assert content_type_db not in db
    
    #create permission
    content_type_params1 = ContentTypeCreate(**{"content": "users"})
    content_type_db1 =  await crud.create_obj(db,models.ContentType,content_type_params1)
    permission_params = PermissionCreate(**{"name": "Can View Users","codename": "view_users","content_type_id": content_type_db1.id})
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
    permission_update = PermissionUpdate(**{"name": "Can View Users1","codename": "view_users1","content_type_id": content_type_db1.id})
    permission_db = await crud.update_obj(db=db,model=models.Permission,id=permission_db.id,schema_model=permission_update)
    assert permission_db.name == "Can View Users1"
    #delete permission
    permission_db = await crud.delete_obj(db=db,model=models.Permission, id=permission_db.id)
    assert permission_db not in db
    
    #create role
    permission_params = PermissionCreate(**{"name": "Can View Users","codename": "view_users","content_type_id": content_type_db1.id})
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
    role_db = await crud.delete_obj(db=db,model=models.Role, id=role_db.id)
    assert role_db not in db
    
    
    

    
    
    
    