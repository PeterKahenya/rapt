from pydantic import BaseModel,UUID4
from typing import List,Optional
from datetime import datetime


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

class ContentTypeInDBBase(ModelInDBBase):
    content: str

# permission schema
class PermissionCreate(BaseModel):
    name: str
    codename: str
    content_type_id: UUID4

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
    permissions: List[ModelBase] | None

class RoleInDBBase(ModelInDBBase):
    name: str
    description: str
    permissions: List[PermissionInDBBase] | None

# user schema
class UserCreate(BaseModel):
    phone: str
    name: str
    is_superuser: Optional[bool] = False
    
class Contact(ModelBase):
    phone: str
    name: str
    id: Optional[UUID4] = None

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    is_superuser: Optional[bool] = False
    is_active: Optional[bool] = False
    is_verified: Optional[bool] = False
    phone_verification_code: Optional[str] = None
    phone_verification_code_expiry_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    contacts: Optional[List[Contact]] = []
    roles: Optional[List[ModelBase]] = []
    client_apps: Optional[List[ModelBase]] = []
    
class UserInDBBase(ModelInDBBase):
    phone: str
    name: str
    is_superuser: bool
    is_active: bool
    is_verified: bool
    phone_verification_code: str | None
    phone_verification_code_expiry_at: datetime | None
    last_seen: datetime | None
    contacts: List[Contact] = []
    roles: List[RoleInDBBase] = []
    client_apps: List[ModelBase] = []

# user verify
class UserVerify(BaseModel):
    phone: str
    phone_verification_code: str

# client app schema
class ClientAppCreate(BaseModel):
    name: str
    description: str
    user_id: UUID4
    
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
    