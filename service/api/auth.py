from typing import Annotated, Any, Dict, List
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.orm import Session
import crud
import schemas
import models
from depends import get_db, get_or_create_user, get_app, phone_verify, authorize, get_query_params
from config import logger,settings
import utils
import jwt
from fastapi import Form
from honeybadger.contrib.fastapi import HoneybadgerRoute

router = APIRouter(dependencies=[Depends(get_db)],route_class=HoneybadgerRoute)

@router.post("/login",status_code=200,tags=["Authenticate"])
async def login(db: Session = Depends(get_db), user: models.User = Depends(get_or_create_user), app: models.ClientApp = Depends(get_app)) -> Dict:
    try:
        user = await user.create_verification_code(db=db,code_length=settings.verification_code_length,code_expiry_seconds=settings.verification_code_expiry_seconds)
        message = f"Your rapt verification code is {user.phone_verification_code} please enter it to verify your phone number"
        print(f"User {user.phone} code {user.phone_verification_code}")
        # await utils.smsleopard_send_sms(phone=user.phone, message=message)
        return {"message":"SMS verification code sent", "success":True, "phone":user.phone}
    except Exception as e:
        logger.error(f"Login Error: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":"Unexpected error occurred",
            "success":False,
            "phone":user.phone
        })
   
@router.post("/verify",status_code=200,tags=["Authenticate"])
async def verify(db: Session = Depends(get_db), user: models.User = Depends(phone_verify), app: models.ClientApp = Depends(get_app)) -> schemas.AccessToken:
    try:
        access_token = user.create_jwt_token(app, settings.jwt_secret_key,settings.jwt_algorithm,settings.access_token_expiry_seconds)
        chatter_role = db.execute(select(models.Role).where(models.Role.name=="Chatter")).scalars().first()
        if chatter_role not in user.roles and chatter_role:
            user.roles.append(chatter_role)  # by default a user is a chatter
        db.commit()
        db.refresh(user)
        return schemas.AccessToken(access_token=access_token,token_type="Bearer",expires_in=settings.access_token_expiry_seconds)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500,detail={"message":"An unexpected error occurred"})
        
@router.post("/refresh",status_code=200,tags=["Authenticate"])
async def refresh_token(access_token: Annotated[str,Form()], db: Session = Depends(get_db), app: models.ClientApp = Depends(get_app)) -> schemas.AccessToken:
    try:
        payload = jwt.decode(access_token,settings.jwt_secret_key,algorithms=[settings.jwt_algorithm],options={"verify_exp":False,"verify_signature":True,"required":["exp","sub"]})
        phone = payload.get("sub",None)
        if not phone:
            logger.error(f"No phone number found in the access token")
            raise HTTPException(status_code=401,detail={
                "message":"Invalid access token"
            })
        else:
            user = db.execute(select(models.User).where(models.User.phone==phone)).scalars().first()
            if not user:
                logger.error(f"User not found with phone number: {phone}")
                raise HTTPException(status_code=401,detail={
                    "message":"User not found"
                })
            if user.access_token != access_token:
                logger.error(f"Access token is invalid or expired")
                raise HTTPException(status_code=401,detail={
                    "message":"Access token is invalid or expired"
                })
            else:
                access_token = user.create_jwt_token(app, settings.jwt_secret_key,settings.jwt_algorithm,settings.access_token_expiry_seconds)
                db.commit()
                db.refresh(user)
                return schemas.AccessToken(access_token=access_token,token_type="Bearer",expires_in=settings.access_token_expiry_seconds)
    except HTTPException as e:
        logger.warning(f"Error: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":"An unexpected error occurred",
        })
       
@router.get("/me",status_code=200,tags=["Profile"])
async def me(user: models.User = Depends(authorize(perm="read_users"))) -> schemas.UserInDBBase:
    return user

@router.get("/permissions/", status_code=200, tags=["Authorize"])
async def get_permissions(
                            params: Dict[str, Any] = Depends(get_query_params),
                            user: models.User = Depends(authorize(perm="read_permissions")),
                            db: Session = Depends(get_db),
                        ) -> schemas.ListResponse:
    return await crud.paginate(
                                    db=db,
                                    model=models.Permission,
                                    schema=schemas.PermissionInDBBase,
                                    **params
                                )
    
@router.get("/permissions/{permission_id}", status_code=200, tags=["Authorize"])
async def get_permission(
                            permission_id: UUID4,
                            user: models.User = Depends(authorize(perm="read_permissions")),
                            db: Session = Depends(get_db)
                        ) -> schemas.PermissionInDBBase:
    return await crud.get_obj_or_404(db=db,model=models.Permission,id=permission_id)

# create role
@router.post("/roles/", status_code=201, tags=["Authorize"])
async def create_role(
                        role_create: schemas.RoleCreate,
                        user: models.User = Depends(authorize(perm="create_roles")),
                        db: Session = Depends(get_db)
                    ) -> schemas.RoleInDBBase:
    try:
        role_db: models.Role = await crud.create_obj(db=db,model=models.Role,schema_model=role_create)
        return role_db
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":"An unexpected error occurred"
        })
        
# get roles
@router.get("/roles/", status_code=200, tags=["Authorize"])
async def get_roles(
                        params: Dict[str, Any] = Depends(get_query_params),
                        user: models.User = Depends(authorize(perm="read_roles")),
                        db: Session = Depends(get_db)
                    ) -> schemas.ListResponse:
    return await crud.paginate(
                                db=db,
                                model=models.Role,
                                schema=schemas.RoleInDBBase,
                                **params
                            )

# get role by id
@router.get("/roles/{role_id}", status_code=200, tags=["Authorize"])
async def get_role(
                        role_id: UUID4,
                        user: models.User = Depends(authorize(perm="read_roles")),
                        db: Session = Depends(get_db)
                    ) -> schemas.RoleInDBBase:
    return await crud.get_obj_or_404(db=db,model=models.Role,id=role_id)

# update role
@router.put("/roles/{role_id}", status_code=200, tags=["Authorize"])
async def update_role(
                        role_id: UUID4,
                        role_update: schemas.RoleUpdate,
                        user: models.User = Depends(authorize(perm="update_roles")),
                        db: Session = Depends(get_db)
                    ) -> schemas.RoleInDBBase:
    try:
        role_db: models.Role = await crud.update_role(db=db,role_id=role_id,role_update_data=role_update)
        return role_db
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":f"An unexpected error: {e} occurred"
        })
        
# delete role
@router.delete("/roles/{role_id}", status_code=204, tags=["Authorize"])
async def delete_role(
                        role_id: UUID4,
                        user: models.User = Depends(authorize(perm="delete_roles")),
                        db: Session = Depends(get_db)
                    ) -> None:
    try:
        is_deleted = await crud.delete_obj(db=db,model=models.Role,id=role_id)
        if is_deleted:
            return None
        else:
            return {"message":"Something went wrong"},500
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":f"An unexpected error {e} occurred"
        })
        
# create user
@router.post("/users/", status_code=201, tags=["Users"])
async def create_user(
                        user_create: schemas.UserCreate,
                        user: models.User = Depends(authorize(perm="create_users")),
                        db: Session = Depends(get_db)
                    ) -> schemas.UserInDBBase:
    try:
        user_db: models.User = await crud.create_obj(db=db,model=models.User,schema_model=user_create)
        return user_db
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":"An unexpected error occurred"
        })

# get users
@router.get("/users/", status_code=200, tags=["Users"])
async def get_users(
                        params: Dict[str, Any] = Depends(get_query_params),
                        user: models.User = Depends(authorize(perm="read_users")),
                        db: Session = Depends(get_db)
                    ) -> schemas.ListResponse:
    return await crud.paginate(
                                db=db,
                                model=models.User,
                                schema=schemas.UserInDBBase,
                                **params
                            )

# get user by id
@router.get("/users/{user_id}", status_code=200, tags=["Users"])
async def get_user(
                        user_id: UUID4,
                        user: models.User = Depends(authorize(perm="read_users")),
                        db: Session = Depends(get_db)
                    ) -> schemas.UserInDBBase:
    return await crud.get_obj_or_404(db=db,model=models.User,id=user_id)

# update user
@router.put("/users/{user_id}", status_code=200, tags=["Users"])
async def update_user(
                        user_id: UUID4,
                        user_update: schemas.UserUpdate,
                        user: models.User = Depends(authorize(perm="update_users")),
                        db: Session = Depends(get_db)
                    ) -> schemas.UserInDBBase:
    try:
        user_db: models.User = await crud.update_user(db=db,user_id=user_id,user_update_data=user_update)
        return user_db
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":f"An unexpected error occurred: {e}"
        })

# delete user
@router.delete("/users/{user_id}", status_code=204, tags=["Users"])
async def delete_user(
                        user_id: UUID4,
                        user: models.User = Depends(authorize(perm="delete_users")),
                        db: Session = Depends(get_db)
                    ) -> None:
    is_deleted = await crud.delete_obj(db=db,model=models.User,id=user_id)
    if is_deleted:
        return None
    else:
        logger.error(f"Unable to delete user")
        raise HTTPException(status_code=500,detail={
            "message":"Something went wrong"
        })
        
# get user contacts
@router.get("/users/{user_id}/contacts", status_code=200, tags=["Contacts"])
async def get_user_contacts(
                                user_id: UUID4,
                                user: models.User = Depends(authorize(perm="read_contacts")),
                                db: Session = Depends(get_db)
                            ) -> List[schemas.ContactInDBBase]:
    return user.contacts
        
# upload contacts
@router.post("/users/{user_id}/contacts", status_code=201, tags=["Contacts"])
async def upload_contacts(
                            user_id: UUID4,
                            contacts: List[schemas.ContactCreate],
                            user: models.User = Depends(authorize(perm="create_contacts")),
                            db: Session = Depends(get_db)
                        ) -> List[schemas.ContactInDBBase]:
    try:
        await crud.get_obj_or_404(db=db,model=models.User,id=user_id)
        contacts_list = []
        for contact_data in contacts:
            contact_data.user_id = user_id
            contact_db: models.Contact = await crud.create_contact(db=db,contact_create_data=contact_data)
            contacts_list.append(contact_db)
        return contacts_list
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":f"An unexpected error occurred {e}"
        })
        
# update contact
@router.put("/users/{user_id}/contacts", status_code=200, tags=["Contacts"])
async def update_contact(
                            user_id: UUID4,
                            contact_update: schemas.ContactUpdate,
                            user: models.User = Depends(authorize(perm="update_contacts")),
                            db: Session = Depends(get_db)
                        ) -> schemas.ContactInDBBase:
    try:
        contact_db: models.Contact = await crud.update_contact(db=db,contact_update_data=contact_update)
        return contact_db
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":f"An unexpected error occurred: {e}"
        })

# create client app
@router.post("/apps/", status_code=201, tags=["Apps"])
async def create_client_app(
                                app_create: schemas.ClientAppCreate,
                                user: models.User = Depends(authorize(perm="create_client_apps")),
                                db: Session = Depends(get_db)
                            ) -> schemas.ClientAppInDBBase:
    try:
        app_create.user_id = app_create.user_id if app_create.user_id else  user.id
        app_db: models.ClientApp = await crud.create_obj(db=db,model=models.ClientApp,schema_model=app_create)
        db.commit()
        db.refresh(app_db)
        return app_db
    except Exception as e:
        logger.error(f"Error in create_client_app: {str(e)}")
        raise HTTPException(status_code=500,detail={"message":f"An unexpected error: {e} occurred"})

# get client apps
@router.get("/apps/", status_code=200, tags=["Apps"])
async def get_client_apps(
                            params: Dict[str, Any] = Depends(get_query_params),
                            user: models.User = Depends(authorize(perm="read_client_apps")),
                            db: Session = Depends(get_db)
                        ) -> schemas.ListResponse:
    return await crud.paginate(
                                db=db,
                                model=models.ClientApp,
                                schema=schemas.ClientAppInDBBase,
                                **params
                            )

# get client app by id
@router.get("/apps/{app_id}", status_code=200, tags=["Apps"])
async def get_client_app(
                            app_id: UUID4,
                            user: models.User = Depends(authorize(perm="read_client_apps")),
                            db: Session = Depends(get_db)
                        ) -> schemas.ClientAppInDBBase:
    return await crud.get_obj_or_404(db=db,model=models.ClientApp,id=app_id)

# update client app
@router.put("/apps/{app_id}", status_code=200, tags=["Apps"])
async def update_client_app(
                                app_id: UUID4,
                                app_update: schemas.ClientAppUpdate,
                                user: models.User = Depends(authorize(perm="update_client_apps")),
                                db: Session = Depends(get_db)
                            ) -> schemas.ClientAppInDBBase:
    try:
        app_update.user_id = app_update.user_id if app_update.user_id else user.id
        app_db: models.ClientApp = await crud.update_clientapp(
                                                                db=db,
                                                                client_app_id=app_id,
                                                                client_app_update_data=app_update
                                                            )
        return app_db
    except Exception as e:
        logger.error(f"Error in update_client_app: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":f"An unexpected error: {e} occurred"
        })

# delete client app
@router.delete("/apps/{app_id}", status_code=204, tags=["Apps"])
async def delete_client_app(
                                app_id: UUID4,
                                user: models.User = Depends(authorize(perm="delete_client_apps")),
                                db: Session = Depends(get_db)
                            ) -> None:
    try:
        is_deleted = await crud.delete_obj(db=db,model=models.ClientApp,id=app_id)
        if is_deleted:
            return None
        else:
            return {"message":"Something went wrong"},500
    except Exception as e:
        logger.error(f"Error in delete_client_app: {str(e)}")
        raise HTTPException(status_code=500,detail={
            "message":"An unexpected error occurred"
        })