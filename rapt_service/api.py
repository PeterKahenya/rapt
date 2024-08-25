from fastapi import FastAPI,Depends,Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from typing import List,Dict,Optional
from pydantic import UUID4
import uvicorn
import os
import config
import crud
import models
import schemas
import utils


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
@app.get("/permissions/",response_model=utils.Pagination)
async def get_permissions(
                        db: Session = Depends(get_db), 
                        q: Optional[str] = None,
                        params: Optional[Dict] = None,
                        page: int = Query(1, ge=1),
                        size: int = Query(10, ge=1, le=100)
                        ) -> utils.Pagination:
    if q:
        permissions = await crud.search_objects(db=db,model=models.Permission,q=q)
    elif params:
        permissions = await crud.filter_objects(db=db,model=models.Permission,params=params)
    else:
        permissions = await crud.get_objects_list(db=db,model=models.Permission)
    return utils.paginate(
        items=[schemas.PermissionInDBBase.model_validate(p).model_dump() for p in permissions],
        page=page,
        size=size
    )

@app.get("/permissions/{permission_id}",response_model=schemas.PermissionInDBBase)
async def get_permission(permission_id: UUID4, db: Session = Depends(get_db)) -> schemas.PermissionInDBBase:
    return await crud.get_obj(db=db,model=models.Permission,id=permission_id)
    
@app.post("/roles/",status_code=201,response_model=schemas.RoleInDBBase)
async def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)) -> schemas.RoleInDBBase:
    return await crud.create_obj(db=db,model=models.Role,schema_model=role)

@app.get("/roles/",response_model=utils.Pagination)
async def get_roles(
                        db: Session = Depends(get_db), 
                        q: Optional[str] = None,
                        params: Optional[Dict] = None,
                        page: int = Query(1, ge=1),
                        size: int = Query(10, ge=1, le=100)) -> utils.Pagination:
    if q:
        roles = await crud.search_objects(db=db,model=models.Role,q=q)
    elif params:
        roles = await crud.filter_objects(db=db,model=models.Role,params=params)
    else:
        roles = await crud.get_objects_list(db=db,model=models.Role)
    return utils.paginate(
        items=[schemas.RoleInDBBase.model_validate(r).model_dump() for r in roles],
        page=page,
        size=size
    )

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