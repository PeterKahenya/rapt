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
@app.get("/permissions/",response_model=crud.Pagination)
async def get_permissions(
                        db: Session = Depends(get_db), 
                        q: Optional[str] = None,
                        params: Optional[Dict] = None,
                        page: int = Query(1, ge=1),
                        size: int = Query(10, ge=1, le=100)
                        ) -> crud.Pagination:
    return await crud.paginate(
        db=db,
        model=models.Permission,
        schema=schemas.PermissionInDBBase,
        q=q,
        params=params,
        page=page,
        size=size
    )

@app.get("/permissions/{permission_id}",response_model=schemas.PermissionInDBBase)
async def get_permission(permission_id: UUID4, db: Session = Depends(get_db)) -> schemas.PermissionInDBBase:
    return await crud.get_obj(db=db,model=models.Permission,id=permission_id)
    
@app.post("/roles/",status_code=201,response_model=schemas.RoleInDBBase)
async def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)) -> schemas.RoleInDBBase:
    return await crud.create_obj(db=db,model=models.Role,schema_model=role)

@app.get("/roles/",response_model=crud.Pagination)
async def get_roles(
                        db: Session = Depends(get_db), 
                        q: Optional[str] = None,
                        params: Optional[Dict] = None,
                        page: int = Query(1, ge=1),
                        size: int = Query(10, ge=1, le=100)) -> crud.Pagination:
    return await crud.paginate(
        db=db,
        model=models.Role,
        schema=schemas.RoleInDBBase,
        q=q,
        params=params,
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

#get users list
@app.get("/users/",response_model=crud.Pagination)
async def get_users(
                        db: Session = Depends(get_db), 
                        q: Optional[str] = None,
                        params: Optional[Dict] = None,
                        page: int = Query(1, ge=1),
                        size: int = Query(10, ge=1, le=100)
                    ) -> crud.Pagination:
    return await crud.paginate(
        db=db,
        model=models.User,
        schema=schemas.UserInDBBase,
        q=q,
        params=params,
        page=page,
        size=size
    )

#get user by id
@app.get("/users/{user_id}",response_model=schemas.UserInDBBase)
async def get_user(user_id: UUID4, db: Session = Depends(get_db)) -> schemas.UserInDBBase:
    return await crud.get_obj(db=db,model=models.User,id=user_id)

#update user
@app.put("/users/{user_id}",response_model=schemas.UserInDBBase)
async def update_user(user_id: UUID4, user: schemas.UserUpdate, db: Session = Depends(get_db)) -> schemas.UserInDBBase:
    return await crud.update_user(db=db,user_id=user_id,user_update_data=user)

#delete user
@app.delete("/users/{user_id}",status_code=204)
async def delete_user(user_id: UUID4, db: Session = Depends(get_db)) -> None:
    is_deleted = await crud.delete_obj(db=db,model=models.User,id=user_id)
    if is_deleted:
        return None
    else:
        return {"message":"Something went wrong"},500

#onboarding new user
@app.post("/users/onboard/",status_code=200,response_model=Dict)
async def onboard_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Get name and phone number 
        - create user if not exists
        - initialize user verification code
        - send verification code to phone number
        - return message that verification code has been sent
    """
    # check if user exists, otherwise create user
    user_exists = await crud.filter_objects(db=db,model=models.User,params={"phone":user.phone})
    if not user_exists:
        user = await crud.create_obj(db=db,model=models.User,schema_model=user)
    else:
        user:models.User = user_exists[0]
    # initialize user verification code
    user = await user.create_verification_code(db=db)
    # send verification code to phone number
    #TODO send verification code to phone number
    # return message that verification code has been sent
    return {"message":"Verification Code Sent"}
    
#verify user
@app.post("/users/verify/",status_code=200,response_model=Dict)
async def verify_user(user: schemas.UserVerify, db: Session = Depends(get_db)):
    """
    Get phone number and verification code
        - check if user exists
        - check if verification code is valid
        - return message that user has been verified
    """
    print(f"Verifying user with phone number: {user.phone}")
    # check if user exists
    user_exists = await crud.filter_objects(db=db,model=models.User,params={"phone":user.phone})
    if not user_exists:
        return {"message":"User does not exist"},404
    user:models.User = user_exists[0]
    # TODO verify user, create token and return token and user details
    # check if verification code is valid
    if user.phone_verification_code != user.phone_verification_code:
        return {"message":"Invalid Verification Code"},400
    # return message that user has been verified
    response = schemas.UserInDBBase.model_validate(user).model_dump()
    response["message"] = "User Verified"
    print(user)
    return response

# client apps
@app.post("/clientapps/",status_code=201,response_model=schemas.ClientAppInDBBase)
async def create_client_app(client_app: schemas.ClientAppCreate, db: Session = Depends(get_db)) -> schemas.ClientAppInDBBase:
    return await crud.create_obj(db=db,model=models.ClientApp,schema_model=client_app)

@app.get("/clientapps/",response_model=crud.Pagination)
async def get_client_apps(
                        db: Session = Depends(get_db), 
                        q: Optional[str] = None,
                        params: Optional[Dict] = None,
                        page: int = Query(1, ge=1),
                        size: int = Query(10, ge=1, le=100)) -> crud.Pagination:
    return await crud.paginate(
        db=db,
        model=models.ClientApp,
        schema=schemas.ClientAppInDBBase,
        q=q,
        params=params,
        page=page,
        size=size
    )

@app.get("/clientapps/{client_app_id}",response_model=schemas.ClientAppInDBBase)
async def get_client_app(client_app_id: UUID4, db: Session = Depends(get_db)) -> schemas.ClientAppInDBBase:
    return await crud.get_obj(db=db,model=models.ClientApp,id=client_app_id)

@app.put("/clientapps/{client_app_id}",response_model=schemas.ClientAppInDBBase)
async def update_client_app(client_app_id: UUID4, client_app: schemas.ClientAppUpdate, db: Session = Depends(get_db)) -> schemas.ClientAppInDBBase:
    return await crud.update_obj(db=db,model=models.ClientApp,id=client_app_id,schema_model=client_app)

@app.delete("/clientapps/{client_app_id}",status_code=204)
async def delete_client_app(client_app_id: UUID4, db: Session = Depends(get_db)) -> None:
    is_deleted = await crud.delete_obj(db=db,model=models.ClientApp,id=client_app_id)
    if is_deleted:
        return None
    else:
        return {"message":"Something went wrong"},500

if __name__ == "__main__":
    SERVICE_PORT = os.environ.get("SERVICE_PORT")
    uvicorn.run(app="api:app",host="0.0.0.0",port=int(SERVICE_PORT),reload=True)