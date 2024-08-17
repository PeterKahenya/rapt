from fastapi import FastAPI,Depends
from config import DATABASE_URL,logger,TEST_DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
import models
import schemas
import crud
from typing import List
from pydantic import UUID4

app = FastAPI()

def get_db():
    try:
        engine = create_engine(DATABASE_URL)
        models.Model.metadata.create_all(bind=engine)
        session_local = sessionmaker(autocommit=False,autoflush=False,bind=engine)
        db = session_local()
        logger.info("Database connection established")
        yield db
    finally:
        db.close()

@app.get("/initialize/")
async def initialize(db: Session = Depends(get_db)):
    for content in models.Model.metadata.tables.values():
        if not await crud.filter_objects(db=db,model=models.ContentType,params={"content":content.name}):
            await crud.create_obj(db=db,model=models.ContentType,schema_model=schemas.ContentTypeCreate(content=content.name))
    return {"message":"System Initialized"}

@app.get("/api/contenttypes/",response_model=List[schemas.ContentTypeInDBBase])
async def get_content_types(db: Session = Depends(get_db)) -> List[schemas.ContentTypeInDBBase]:
    return await crud.get_objects_list(db=db,model=models.ContentType)

@app.post("/api/permissions/",status_code=201,response_model=schemas.PermissionInDBBase)
async def create_permission(permission: schemas.PermissionCreate, db: Session = Depends(get_db)) -> schemas.PermissionInDBBase:
    return await crud.create_obj(db=db,model=models.Permission,schema_model=permission)

#TODO add supoport for filtering/searching for permissions
@app.get("/api/permissions/",response_model=List[schemas.PermissionInDBBase])
async def get_permissions(db: Session = Depends(get_db)) -> List[schemas.PermissionInDBBase]:
    return await crud.get_objects_list(db=db,model=models.Permission)

@app.get("/api/permissions/{permission_id}",response_model=schemas.PermissionInDBBase)
async def get_permission(permission_id: UUID4, db: Session = Depends(get_db)) -> schemas.PermissionInDBBase:
    return await crud.get_obj(db=db,model=models.Permission,id=permission_id)

@app.put("/api/permissions/{permission_id}",response_model=schemas.PermissionInDBBase)
async def update_permission(permission_id: UUID4, permission: schemas.PermissionUpdate, db: Session = Depends(get_db)) -> schemas.PermissionInDBBase:
    return await crud.update_obj(db=db,model=models.Permission,id=permission_id,schema_model=permission)

@app.delete("/api/permissions/{permission_id}",status_code=204)
async def delete_permission(permission_id: UUID4, db: Session = Depends(get_db)) -> None:
    is_deleted = await crud.delete_obj(db=db,model=models.Permission,id=permission_id)
    if is_deleted:
        return None
    else:
        return {"message":"Something went wrong"},500
    
@app.post("/api/roles/",status_code=201,response_model=schemas.RoleInDBBase)
async def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)) -> schemas.RoleInDBBase:
    return await crud.create_obj(db=db,model=models.Role,schema_model=role)

@app.get("/api/roles/",response_model=List[schemas.RoleInDBBase])
async def get_roles(db: Session = Depends(get_db)) -> List[schemas.RoleInDBBase]:
    return await crud.get_objects_list(db=db,model=models.Role)

@app.get("/api/roles/{role_id}",response_model=schemas.RoleInDBBase)
async def get_role(role_id: UUID4, db: Session = Depends(get_db)) -> schemas.RoleInDBBase:
    return await crud.get_obj(db=db,model=models.Role,id=role_id)

@app.put("/api/roles/{role_id}",response_model=schemas.RoleInDBBase)
async def update_role(role_id: UUID4, role: schemas.RoleUpdate, db: Session = Depends(get_db)) -> schemas.RoleInDBBase:
    return await crud.update_role(db=db,role_id=role_id,role_update_data=role)

@app.delete("/api/roles/{role_id}",status_code=204)
async def delete_role(role_id: UUID4, db: Session = Depends(get_db)) -> None:
    is_deleted = await crud.delete_obj(db=db,model=models.Role,id=role_id)
    if is_deleted:
        return None
    else:
        return {"message":"Something went wrong"},500