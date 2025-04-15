from enum import Enum
from pydantic import BaseModel,UUID4
from typing import Any, List,Optional
from datetime import datetime, timezone

# common schemas
class ListResponse(BaseModel):
    total: int
    page: int
    size: int
    data: List[Any]

# base schemas
class ModelBase(BaseModel):
    id: UUID4
    model_config = {
        "from_attributes": True
    }
    
class ModelInDBBase(ModelBase):
    created_at: datetime
    updated_at: datetime | None

# content type schema
class ContentTypeCreate(BaseModel):
    content: str

class ContentTypeUpdate(BaseModel):
    content: str

class ContentTypeInDBBase(ModelInDBBase):
    content: str
    
# permission schema
class PermissionCreate(BaseModel):
    name: str
    codename: str
    content_type_id: UUID4

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    codename: Optional[str] = None
    content_type_id: Optional[UUID4] = None

class PermissionInDBBase(ModelInDBBase):
    name: str
    codename: str
    content_type: ContentTypeInDBBase

# role schema
class RoleCreate(BaseModel):
    name: str
    description: str

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: List[ModelBase] | None = []

class RoleInDBBase(ModelInDBBase):
    name: str
    description: str
    permissions: List[PermissionInDBBase] | None = []

# user schema
class UserCreate(BaseModel):
    phone: str
    name: str
    is_superuser: Optional[bool] = False
    device_fcm_token: Optional[str] = None


class UserUpdate(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    device_fcm_token: Optional[str] = None
    is_superuser: Optional[bool] = False
    is_active: Optional[bool] = False
    is_verified: Optional[bool] = False
    phone_verification_code: Optional[str] = None
    phone_verification_code_expiry_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    roles: Optional[List[ModelBase]] = []
    
class UserInDBBase(ModelInDBBase):
    phone: str
    name: str
    is_superuser: bool
    is_active: bool
    is_verified: bool
    phone_verification_code: str | None
    phone_verification_code_expiry_at: datetime | None
    last_seen: datetime | None
    roles: List[RoleInDBBase] = []
    client_apps: List[ModelBase] = []

class UserVerify(BaseModel):
    phone: str
    phone_verification_code: str
    
class ContactCreate(BaseModel):
    phone: str
    name: str
    user_id: Optional[UUID4] = None
    
class ContactUpdate(BaseModel):
    name: Optional[str] = None
    user_id: Optional[UUID4] = None
    contact_id: Optional[UUID4] = None

class ContactInDBBase(BaseModel):
    phone: str
    name: str
    is_active: bool
    user_id: UUID4
    contact_id: UUID4
    
    model_config = {
        "from_attributes": True
    }
    
class AccessToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    
class RefreshToken(BaseModel):
    access_token: str

# client app schema
class ClientAppCreate(BaseModel):
    name: str
    description: str
    user_id: Optional[UUID4] = None
    
class ClientAppUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[UUID4] = None
    
class ClientAppInDBBase(ModelInDBBase):
    name: str
    description: str
    client_id: str
    client_secret: str
    user: ModelInDBBase

# chatroom schema
class ChatRoomCreate(BaseModel):
    socket_room_id: Optional[str] = None
    members: List[ModelBase]

class ChatRoomUpdate(BaseModel):
    members: List[ModelBase] | None = []
    
class ChatRoomInDBBase(ModelInDBBase):
    members: List[UserInDBBase] | None
    room_chats: List["ChatInDBBase"] | None
    
# group schema
class GroupCreate(BaseModel):
    name: str
    description: str
    chatroom_id: UUID4

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chatroom_id: Optional[UUID4] = None

class GroupInDBBase(ModelInDBBase):
    name: str
    description: str
    chatroom_id: UUID4
    chatroom: ChatRoomInDBBase

class MediaObject(BaseModel):
    link: str
    file_type: str

# chat schema
class ChatCreate(BaseModel):
    message: str
    sender_id: Optional[UUID4] = None
    room_id: Optional[UUID4] = None
    media: Optional[List[MediaObject]] = None

class ChatUpdate(BaseModel):
    message: Optional[str] = None
    media: Optional[List[ModelBase]] | None = None
    is_read: Optional[bool] = False

class ChatInDBBase(ModelInDBBase):
    message: str
    is_read: bool
    sender: UserInDBBase
    room: ModelBase
    media: List["MediaInDBBase"] | None

# media schema
class MediaCreate(BaseModel):
    link: str
    file_type: str
    chat_id: UUID4

class MediaUpdate(BaseModel):
    link: Optional[str] = None
    file_type: Optional[str] = None
    chat_id: Optional[UUID4] = None

class MediaInDBBase(ModelInDBBase):
    link: str
    file_type: str
    chat_id: UUID4
    # WARNING: chat object would lead to recursive error

class MessageType(str, Enum):
    ONLINE = "online" # user is online
    OFFLINE = "offline" # user is offline
    CHAT = "chat" # new chat
    READ = "read" # the user has read the message
    READING = "reading" # the user is 'reading' i.e they are not typing but are looking through your chats
    AWAY = "away" # user is away from your chat but is online
    TYPING = "typing" # user has the phone keyboard up or cursor is on chatbox
    THINKING = "thinking" # user has the keyboad up or cursor on chatbox but they have not typed in a while (TODO: What's the approx. time)
    
class SocketMessage(BaseModel): # for websocket messages both incoming and outgoing
    type: MessageType
    user: dict # user object
    obj: Optional[dict] = None # for chat messages
    timestamp: datetime = datetime.now(tz=timezone.utc)

