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


