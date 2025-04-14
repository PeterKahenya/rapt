import datetime
from typing import List, Optional, Tuple
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, Table, UniqueConstraint, Uuid
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
import jwt
import utils
from config import logger
from fastapi import HTTPException

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
    Column('user_id', Uuid, ForeignKey('users.id',ondelete="CASCADE"), primary_key=True),
    Column('role_id', Uuid, ForeignKey('roles.id',ondelete="CASCADE"), primary_key=True)
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


chatroom_members_association = Table(
    'chatroom_members',
    Model.metadata,
    Column('user_id', Uuid, ForeignKey('users.id',ondelete="CASCADE"), primary_key=True),
    Column('chatroom_id', Uuid, ForeignKey('chatrooms.id',ondelete="CASCADE"),primary_key=True)
)

class Contact(Model):
    __tablename__ = 'contacts'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))    
    contact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    user: Mapped["User"] = relationship('User', foreign_keys=[user_id], back_populates='contacts')
    contact: Mapped["User"] = relationship('User', foreign_keys=[contact_id], back_populates='contact_of')
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    
    @hybrid_property
    def is_active(self):
        return self.contact.is_active
    
    @hybrid_property
    def phone(self):
        return self.contact.phone
    
    __table_args__= (
        UniqueConstraint('user_id','contact_id',name='unique_contact'),
    )


class User(Model):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(15),unique=True)
    phone_verification_code: Mapped[Optional[str]] = mapped_column(String(6))
    phone_verification_code_expiry_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime())
    device_fcm_token: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    access_token: Mapped[Optional[str]] = mapped_column(String(500))
    last_seen: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime())
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    contacts: Mapped[List[Contact]]  = relationship('Contact', foreign_keys='Contact.user_id', back_populates='user')
    contact_of = relationship('Contact', foreign_keys='Contact.contact_id', back_populates='contact')
    roles: Mapped[List[Role]] = relationship(
        'Role',
        secondary=user_roles_association,
        back_populates='users'
    )
    client_apps: Mapped[List["ClientApp"]] = relationship("ClientApp",back_populates="user")
    chatrooms:Mapped[List["ChatRoom"]] = relationship(
        'ChatRoom',
        secondary=chatroom_members_association,
        back_populates='members'
    )
    chats: Mapped[List["Chat"]] = relationship('Chat',back_populates='sender')

    async def create_verification_code(self,db:Session,code_length:int,code_expiry_seconds:int) -> "User":
        """
            Create the verification code for the user and set it's expiry date and time
        """
        code = utils.generate_random_string(length=code_length)
        expiry_at = datetime.datetime.now() + datetime.timedelta(seconds=code_expiry_seconds)
        self.phone_verification_code = code
        self.phone_verification_code_expiry_at = expiry_at
        db.add(self)
        db.commit()
        db.refresh(self)
        logger.info(f"User {self.phone} verification code {code} created, expires at {expiry_at}")
        return self

    async def validate_verification_code(self,code:str) -> bool:
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
    
    async def has_perm(self,permission:str) -> bool:
        """
            Check if the user has the permission
        """
        for role in self.roles:
            for perm in role.permissions:
                if perm.codename == permission:
                    return True
        return False
    
    def __str__(self):
        return f"{self.name} - {self.phone}"

    def create_jwt_token(self,clientapp: "ClientApp", secret:str,algorithm:str,expiry_seconds:int) -> str:
        """
        Create a JWT token for the user, encoding the phone number and expiry time and return it
        """
        logger.info(f"Creating JWT token for user {self.phone}")
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expiry_seconds)
        payload = {
            "sub": self.phone,
            "exp": expire, 
            "client_id": clientapp.client_id,
            "client_secret": clientapp.client_secret
        }
        access_token = jwt.encode(payload=payload,key=secret,algorithm=algorithm)
        self.access_token = access_token
        return access_token
    
    @staticmethod
    def verify_jwt_token(db:Session,token:str,secret:str,algorithm) -> Tuple[str,str,str] | None:
        """
            Verify the JWT token and return the phone number
        """
        logger.info(f"Verifying JWT token {token}")
        try:
            payload = jwt.decode(jwt=token,key=secret,algorithms=[algorithm],options={"verify_exp":True,"verify_signature":True,"required":["exp","sub"]})
            return payload.get("sub",None),payload.get("client_id",None),payload.get("client_secret",None)
        except jwt.InvalidAlgorithmError:
            logger.error(f"JWT token invalid algorithm: {algorithm} on token: {token}")
            raise HTTPException(status_code=401,detail={"message":"Invalid access token"})
        except jwt.ExpiredSignatureError:
            logger.error(f"JWT expired signature on token: {token}")
            raise HTTPException(status_code=401,detail={"message":"Access Token expired"})
        except jwt.InvalidTokenError as e:
            logger.error(f"JWT invalid token: {token} error: {e}")
            raise HTTPException(status_code=401,detail={"message":"Invalid access token"})


class ClientApp(Model):
    __tablename__ = "client_apps"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    client_id: Mapped[str] = mapped_column(String(100),unique=True,default=utils.generate_client_id)
    client_secret: Mapped[str] = mapped_column(String(100),default=utils.generate_client_secret)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
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
    

class ChatRoom(Model):
    __tablename__ = "chatrooms"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    socket_room_id: Mapped[str] = mapped_column(String(500),unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    members: Mapped[List["User"]] = relationship(
        'User',
        secondary=chatroom_members_association,
        back_populates='chatrooms'
    )
    group: Mapped["Group"] = relationship("Group", uselist=False, back_populates="chatroom")
    room_chats: Mapped[List["Chat"]] = relationship('Chat',back_populates='room')

    #ensure that the chatroom has at least two members and members must be unique
    def __init__(self,socket_room_id:str,members:List[User]):
        if not socket_room_id:
            raise ValueError("Socket Room ID cannot be empty")
        # chatroom has at least two members
        if len(members) < 2:
            raise ValueError("Chatroom must have at least two members")
        # members must be unique
        if len(members) != len(set(members)):
            raise ValueError("Members must be unique")
        self.socket_room_id = socket_room_id
        self.members = members
    
    # check if a user is a member of the chatroom
    def is_member(self,user:User) -> bool:
        return user in self.members


class Group(Model):
    __tablename__ = "groups"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    chatroom_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chatrooms.id"),unique=True,nullable=False)
    chatroom: Mapped[ChatRoom] = relationship("ChatRoom",back_populates="group")


class Chat(Model):
    __tablename__ = "chats"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    message: Mapped[str] = mapped_column(String(500),nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    sender: Mapped[User] = relationship('User',back_populates='chats')
    room_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chatrooms.id"),nullable=False)
    room: Mapped[ChatRoom] = relationship('ChatRoom',back_populates='room_chats')
    media: Mapped[List["Media"]] = relationship("Media",back_populates="chat")

    #ensure that a user is a member of the chatroom before sending a message
    def __init__(self,message:str,sender:User=None,room:ChatRoom=None,**kwargs):
        if not message:
            raise ValueError("Message cannot be empty")
        if not sender and not kwargs.get("sender_id",None):
            raise ValueError("Sender cannot be empty")
        if not room and not kwargs.get("room_id",None):
            raise ValueError("Room cannot be empty")
        if sender not in room.members:
            raise ValueError("Sender must be a member of the room")   
        
        self.message = message
        self.sender_id = sender.id
        self.room_id = room.id


class Media(Model):
    __tablename__ = "media"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    link: Mapped[str] = mapped_column(String(1024),nullable=False)
    file_type: Mapped[str] = mapped_column(String(100),nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    chat_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chats.id",ondelete="CASCADE"),nullable=False)
    chat: Mapped[Chat] = relationship('Chat',back_populates='media')