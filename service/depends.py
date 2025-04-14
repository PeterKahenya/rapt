from typing import Annotated, Any, Dict, Optional
import pymysql
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, Form, HTTPException, Query, Request, WebSocket, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
import config
from config import logger
import crud
import models
import schemas

class RaptOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request=None, websocket: WebSocket=None) -> Optional[HTTPAuthorizationCredentials]:
        request = request or websocket
        if not request:
            if self.auto_error:
                raise HTTPException(status_code= status.HTTP_403_FORBIDDEN,detail="Not authenticated")
            return None
        return await super().__call__(request)

oauth2_scheme = RaptOAuth2PasswordBearer(tokenUrl="/api/auth/login")

DATABASE_URL = config.get_database_url()
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable pre-ping to check connection health
    pool_size=10,        # Adjust pool size as needed
    max_overflow=20,     # Adjust overflow size as needed
    pool_recycle=3600    # Recycle connections after 1 hour
)
models.Model.metadata.create_all(bind=engine)
session_local = sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db():
    db = None
    try:
        db = session_local()
        logger.info("Database connection established")
        yield db
    except pymysql.MySQLError as e:
        logger.error(f"Database connection error: {e}")
        if db:
            db.close()
        raise
    finally:
        if db:
            logger.error("Closing database connection")
            db.close()
        
        
async def get_app(client_id: Annotated[str, Form()], client_secret: Annotated[str, Form()], db: Session = Depends(get_db)) -> models.ClientApp:
    clientapp = db.execute(select(models.ClientApp)
                           .where(models.ClientApp.client_id==client_id, models.ClientApp.client_secret==client_secret)
                        ).scalars().first()
    if not clientapp:
        raise HTTPException(status_code=401,detail={"message":"Client credentials are invalid"})
    return clientapp

async def get_or_create_user(phone: Annotated[str, Form()], db: Session = Depends(get_db)) -> models.User:
    user = db.execute(select(models.User).where(models.User.phone==phone)).scalars().first()
    if not user:
        user_create = schemas.UserCreate(phone=phone,name="Anonymous")
        user = await crud.create_obj(db=db,model=models.User,schema_model=user_create)
    return user

async def get_user_by_phone(phone: Annotated[str, Form()], db: Session = Depends(get_db)) -> models.User:
    user = db.execute(select(models.User).where(models.User.phone==phone)).scalars().first()
    if not user:
        raise HTTPException(status_code=404,detail={"message":"User not found"})
    return user

async def phone_verify(phone_verification_code: Annotated[str, Form()], user: models.User = Depends(get_user_by_phone), db: Session = Depends(get_db)) -> models.User:
    if(await user.validate_verification_code(code=phone_verification_code)):
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(status_code=401,detail={
            "message":"Invalid verification code"
        })
        
async def authenticate(access_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    phone,client_id,client_secret = models.User.verify_jwt_token(db,access_token,config.settings.jwt_secret_key,config.settings.jwt_algorithm)
    if not phone:
        logger.error("No phone sub in token")
        raise HTTPException(status_code=401, detail={"message":"Invalid access token"})
    if not client_id or not client_secret:
        logger.error("No client_id or client_secret in token")
        raise HTTPException(status_code=401, detail={"message":"Invalid access token"})
    app = db.execute(select(models.ClientApp).where(models.ClientApp.client_id==client_id,models.ClientApp.client_secret==client_secret)).scalars().first()
    if not app:
        logger.error("Client not found")
        raise HTTPException(status_code=401, detail={"message":"Invalid access token"})
    user = db.execute(select(models.User).where(models.User.phone==phone)).scalars().first()
    if not user:
        logger.error(f"User with phone: {phone} not found")
        raise HTTPException(status_code=401, detail={"message":"Invalid access token"})
    if not user.is_active:
        logger.error(f"User with phone: {phone} is not active")
        raise HTTPException(status_code=401, detail={"message":"User is not active"})
    if not user.is_verified:
        logger.error(f"User with phone: {phone} is not verified")
        raise HTTPException(status_code=401, detail={"message":"User is not verified"})
    return user
            
async def check_permission(perm: str, user: models.User) -> models.User:
    if user.is_superuser:
        return user
    elif await user.has_perm(perm):
        return user
    else:
        raise HTTPException(status_code=403,detail={"message":"User not authorized to view perform this action"})
    
def authorize(perm: str):
    async def _authorize(user: models.User = Depends(authenticate), db: Session = Depends(get_db)) -> models.User:
        return await check_permission(perm, user)
    return _authorize

async def get_query_params(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    q: Optional[str] = None,
) -> Dict[str, Any]:
    query_params = dict(request.query_params)
    query_params.pop('page', None)
    query_params.pop('size', None)
    query_params.pop('q', None)
    params = {
        "page": page,
        "size": size,
        "q": q,
        **query_params
    }
    return params