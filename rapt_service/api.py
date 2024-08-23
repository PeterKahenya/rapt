from fastapi import FastAPI,Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from typing import List
from pydantic import UUID4
import uvicorn
import os
import config
import crud
import models
import schemas

fastapi_config = {
    "title":"RaptChat Service",
    "debug":True,
    "root_path": "/api"
}

app = FastAPI(**fastapi_config)

def get_db():
    try:
        engine = create_engine(config.DATABASE_URL)
        models.Model.metadata.create_all(bind=engine)
        session_local = sessionmaker(autocommit=False,autoflush=False,bind=engine)
        db = session_local()
        config.logger.info("Database connection established")
        yield db
    finally:
        db.close()

@app.get("/initialize/")
async def initialize(db: Session = Depends(get_db)):
    for content in models.Model.metadata.tables.values():
        content_types = await crud.filter_objects(db=db,model=models.ContentType,params={"content":content.name})
        if not content_types:
            content_type = await crud.create_obj(db=db,model=models.ContentType,schema_model=schemas.ContentTypeCreate(content=content.name))
        else:
            content_type = content_types[0]
        for permission in config.DEFAULT_PERMISSIONS_CLASSES:
            if not await crud.filter_objects(db=db,model=models.Permission,params={"codename":permission+"_"+content_type.content}):
                perm_object = {
                    "name":permission.title()+" "+content_type.content.title(),
                    "codename":permission+"_"+content_type.content,
                    "content_type_id":content_type.id
                }
                await crud.create_obj(db=db,model=models.Permission,schema_model=schemas.PermissionCreate(**perm_object))    
    return {"message":"System Initialized"}

#TODO add supoport for filtering/searching for permissions
@app.get("/permissions/",response_model=List[schemas.PermissionInDBBase])
async def get_permissions(db: Session = Depends(get_db)) -> List[schemas.PermissionInDBBase]:
    return await crud.get_objects_list(db=db,model=models.Permission)

@app.get("/permissions/{permission_id}",response_model=schemas.PermissionInDBBase)
async def get_permission(permission_id: UUID4, db: Session = Depends(get_db)) -> schemas.PermissionInDBBase:
    return await crud.get_obj(db=db,model=models.Permission,id=permission_id)
    
@app.post("/roles/",status_code=201,response_model=schemas.RoleInDBBase)
async def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)) -> schemas.RoleInDBBase:
    return await crud.create_obj(db=db,model=models.Role,schema_model=role)

@app.get("/roles/",response_model=List[schemas.RoleInDBBase])
async def get_roles(db: Session = Depends(get_db)) -> List[schemas.RoleInDBBase]:
    return await crud.get_objects_list(db=db,model=models.Role)

@app.get("/roles/{role_id}",response_model=schemas.RoleInDBBase)
async def get_role(role_id: UUID4, db: Session = Depends(get_db)) -> schemas.RoleInDBBase:
    return await crud.get_obj(db=db,model=models.Role,id=role_id)

@app.put("/roles/{role_id}",response_model=schemas.RoleInDBBase)
async def update_role(role_id: UUID4, role: schemas.RoleUpdate, db: Session = Depends(get_db)) -> schemas.RoleInDBBase:
    return await crud.update_role(db=db,role_id=role_id,role_update_data=role)

@app.delete("/roles/{role_id}",status_code=204)
async def delete_role(role_id: UUID4, db: Session = Depends(get_db)) -> None:
    is_deleted = await crud.delete_obj(db=db,model=models.Role,id=role_id)
    if is_deleted:
        return None
    else:
        return {"message":"Something went wrong"},500
    


if __name__ == "__main__":
    SERVICE_PORT = os.environ.get("SERVICE_PORT")
    uvicorn.run(app="api:app",host="0.0.0.0",port=int(SERVICE_PORT),reload=True)