import uuid
import datetime
from sqlalchemy import Column,Uuid,String,ForeignKey,Table,DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,relationship,backref,Session
from typing import Optional,List
import utils
from config import settings,logger
import jwt

class Model(DeclarativeBase):
    def to_dict(self):
        object_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for key, value in object_dict.items():
            if isinstance(value, datetime.datetime):
                object_dict[key] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                object_dict[key] = str(value)
        return object_dict

role_permissions_association = Table(
    'role_permissions',
    Model.metadata,
    Column('role_id', Uuid, ForeignKey('roles.id',ondelete="CASCADE"), primary_key=True),
    Column('permission_id', Uuid, ForeignKey('permissions.id',ondelete="CASCADE"), primary_key=True)
)

class ContentType(Model):
    __tablename__ = "content_types"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)    
    content: Mapped[str] = mapped_column(String(100),unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    permissions: Mapped[List["Permission"]] = relationship(back_populates="content_type")


class Permission(Model):
    __tablename__ = "permissions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    codename: Mapped[str] = mapped_column(String(100),unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    content_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_types.id"))
    content_type: Mapped[ContentType] = relationship(back_populates="permissions")
    roles: Mapped[List["Role"]] = relationship(secondary=role_permissions_association,back_populates='permissions')


user_roles_association = Table(
    'user_roles',
    Model.metadata,
    Column('user_id', Uuid, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Uuid, ForeignKey('roles.id'), primary_key=True)
)


class Role(Model):
    __tablename__ = "roles"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)   
    permissions: Mapped[List["Permission"]] = relationship(secondary=role_permissions_association,back_populates='roles')
    
    users: Mapped[List["User"]] = relationship(
        'User',
        secondary=user_roles_association,
        back_populates='roles'
    )


contacts_association = Table(
    'contacts',
    Model.metadata,
    Column('user_id', Uuid, ForeignKey('users.id'), primary_key=True),
    Column('contact_id', Uuid, ForeignKey('users.id'), primary_key=True)
)


class User(Model):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(12),unique=True)
    phone_verification_code: Mapped[Optional[str]] = mapped_column(String(6))
    phone_verification_code_expiry_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime())
    is_active: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    last_seen: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime())
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    contacts: Mapped[List["User"]] = relationship(
        'User',
        secondary=contacts_association,
        primaryjoin=id == contacts_association.c.user_id,
        secondaryjoin=id == contacts_association.c.contact_id,
        backref=backref('contact_of', lazy='dynamic')
    )
    roles = relationship(
        'Role',
        secondary=user_roles_association,
        back_populates='users'
    )
    client_apps: Mapped[List["ClientApp"]] = relationship("ClientApp",back_populates="user")
    
    async def create_verification_code(self,db:Session):
        """
            Create the verification code for the user and set it's expiry date and time
        """
        code = utils.generate_random_string(length=settings.verification_code_length)
        expiry_at = datetime.datetime.now() + datetime.timedelta(milliseconds=settings.verification_code_expiry_milliseconds)
        self.phone_verification_code = code
        self.phone_verification_code_expiry_at = expiry_at
        db.add(self)
        db.commit()
        db.refresh(self)
        logger.info(f"User {self.phone} verification code {code} created, expires at {expiry_at}")
        return self
    

    async def validate_verification_code(self,code:str):
        """
            Validate the verification code and activate the user
        """
        logger.info(f"User {self.phone} verification code {code} vs {self.phone_verification_code} verification requested at {datetime.datetime.now()} vs {self.phone_verification_code_expiry_at}")
        if self.phone_verification_code == code and self.phone_verification_code_expiry_at > datetime.datetime.now():
            self.is_verified = True
            self.is_active = True
            self.phone_verification_code = None
            self.phone_verification_code_expiry_at = None
            logger.info(f"User {self.phone} verified successfully")
            return True
        else:
            logger.info(f"User {self.phone} verification failed")
            return False

    def create_jwt_token(self):
        """
        Create a JWT token for the user, encoding the phone number and expiry time and return it
        """
        logger.info(f"Creating JWT token for user {self.phone}")
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.access_token_expiry_minutes)
        return jwt.encode({"sub":self.phone,"exp":expire},settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
    
    @staticmethod
    def verify_jwt_token(db:Session,token:str) -> Optional[str]:
        """
            Verify the JWT token and return the phone number
        """
        logger.info(f"Verifying JWT token {token}")
        try:
            payload = jwt.decode(token,settings.jwt_secret_key,algorithms=[settings.jwt_algorithm])
            return payload.get("sub",None)
        except jwt.ExpiredSignatureError:
            logger.error(f"JWT token {token} expired")
            return None
        except jwt.InvalidTokenError:
            logger.error(f"JWT token {token} invalid")
            return None


class ClientApp(Model):
    __tablename__ = "client_apps"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    client_id: Mapped[str] = mapped_column(String(100),unique=True,default=utils.generate_client_id)
    client_secret: Mapped[str] = mapped_column(String(100),unique=True,default=utils.generate_client_secret)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship("User",back_populates="client_apps")


    #set the client id and secret at creation
    def __init__(self,name:str,description:str,user_id:uuid.UUID):
        if not name:
            raise ValueError("App name cannot be empty")
        if not user_id:
            raise ValueError("User ID cannot be empty")
        if not description:
            raise ValueError("Description cannot be empty")

        self.name = name
        self.user_id = user_id
        self.description = description
        self.client_id = utils.generate_client_id()
        self.client_secret = utils.generate_client_secret()


