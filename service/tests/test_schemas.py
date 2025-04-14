from pydantic import ValidationError
import pytest
from sqlalchemy import select
import uuid
import schemas
import models

# test common schemas
def test_common_schema(db):
    # test list response schema
    content_types = db.execute(select(models.ContentType)).scalars().all()
    list_response = schemas.ListResponse(**{
        "total": len(content_types),
        "page": 1,
        "size": len(content_types),
        "data": [schemas.ContentTypeInDBBase.model_validate(content_type).model_dump() for content_type in content_types]
    })
    list_response_json = list_response.model_dump()
    assert list_response_json["total"] == len(content_types)
    assert list_response_json["page"] == 1
    assert list_response_json["size"] == len(content_types)

# test contenttype schemas
def test_contenttype_schema(db):
    content_type = schemas.ContentTypeCreate(**{"content": "users"})
    assert content_type.content == "users"
    content_type_update = schemas.ContentTypeUpdate(**{"content": "users1"})
    assert content_type_update.content == "users1"
    content_type_db = db.execute(select(models.ContentType)).scalars().first()
    content_type_schema = schemas.ContentTypeInDBBase.model_validate(content_type_db)
    assert content_type_schema.content == content_type_db.content
    
# test permission schemas
def test_permission_schema(db):
    content_type = db.execute(select(models.ContentType)).scalars().first()
    permission = schemas.PermissionCreate(**{"name": "Can View Users","codename": "read_users","content_type_id": str(content_type.id)})
    assert permission.name == "Can View Users"
    assert permission.codename == "read_users"
    assert permission.content_type_id == content_type.id
    permission_update = schemas.PermissionUpdate(**{"name": "Can View Users1"})
    assert permission_update.name == "Can View Users1"
    permission_db = db.execute(select(models.Permission)).scalars().first()
    permission_schema = schemas.PermissionInDBBase.model_validate(permission_db)
    assert permission_schema.name == permission_db.name
    assert permission_schema.codename == permission_db.codename
    assert permission_schema.content_type.content == permission_db.content_type.content

# test role schemas
def test_role_schema(db):
    role_create = schemas.RoleCreate(**{"name": "Admin","description": "Admin Role"})
    assert role_create.name == "Admin"
    assert role_create.description == "Admin Role"
    permission1 = db.execute(select(models.Permission)).scalars().all()[0]
    permission2 = db.execute(select(models.Permission)).scalars().all()[1]
    role_update = schemas.RoleUpdate(**{
        "name": "Admin1",
        "description": "Admin Role1",
        "permissions": [schemas.ModelBase.model_validate(perm).model_dump() for perm in [permission1, permission2]]
    })
    assert role_update.name == "Admin1"
    assert role_update.description == "Admin Role1"
    assert role_update.permissions[0].id == permission1.id
    role_db = db.execute(select(models.Role)).scalars().first()
    role_schema = schemas.RoleInDBBase.model_validate(role_db)
    assert role_schema.name == role_db.name
    assert role_schema.description == role_db.description
    assert len(role_schema.permissions) == len(role_db.permissions)
    
# test user schemas
def test_user_schema(db):
    user_create = schemas.UserCreate(**{
        "phone": "1234567890",
        "name": "Test User",
        "device_fcm_token": "test_fcm_token"
    })
    assert user_create.phone == "1234567890" and user_create.name == "Test User"
    roles = db.execute(select(models.Role)).scalars().all()
    contacts = db.execute(select(models.User)).scalars().all()    
    user_update = schemas.UserUpdate(**{
        "phone": "1234567891",
        "device_fcm_token": "test_fcm_token1",
        "name": "Test User 1",
        "is_superuser": True,
        "roles": [schemas.ModelBase.model_validate(role).model_dump() for role in roles],       
        # "contacts": [schemas.Contact.model_validate(contact).model_dump() for contact in contacts]
    })
    assert user_update.phone == "1234567891"
    assert user_update.name == "Test User 1"
    assert user_update.is_superuser == True
    assert user_update.roles[0].id == roles[0].id
    # assert user_update.contacts[0].id == contacts[0].id
    user_db = db.execute(select(models.User)).scalars().first()
    user_schema = schemas.UserInDBBase.model_validate(user_db)
    assert user_schema.phone == user_db.phone
    assert user_schema.name == user_db.name
    assert user_schema.is_superuser == user_db.is_superuser
    assert len(user_schema.roles) == len(user_db.roles)
    # assert len(user_schema.contacts) == len(user_db.contacts)
    user_verify = schemas.UserVerify(**{
        "phone": "0700000000",
        "phone_verification_code": "123456"
    })
    assert user_verify.phone == "0700000000"
    assert user_verify.phone_verification_code == "123456"

def test_contact_schema(db):
    contact_create = schemas.ContactCreate(**{
        "phone": "0700000000",
        "name": "Test Contact"
    })
    assert contact_create.phone == "0700000000"
    assert contact_create.name == "Test Contact"
    contact_update = schemas.ContactUpdate(**{
        "name": "Test Contact 1",
        "user_id": str(uuid.uuid4()),
        "contact_id": str(uuid.uuid4())
    })
    assert contact_update.name == "Test Contact 1"
    contact_db = db.execute(select(models.Contact)).scalars().first()
    contact_schema = schemas.ContactInDBBase.model_validate(contact_db)
    assert contact_schema.phone == contact_db.phone
    assert contact_schema.name == contact_db.name
    assert contact_schema.is_active == contact_db.is_active
    assert contact_schema.user_id == contact_db.user_id
    assert contact_schema.contact_id == contact_db.contact_id
    
# test client app schemas
def test_clientapp_schema(db):
    user_db = db.execute(select(models.User)).scalars().first()
    clientapp_create = schemas.ClientAppCreate(**{
        "name": "Test App",
        "description": "Test App Description",
        "user_id": str(user_db.id)
    })
    assert clientapp_create.name == "Test App"
    assert clientapp_create.description == "Test App Description"
    assert clientapp_create.user_id == user_db.id
    clientapp_update = schemas.ClientAppUpdate(**{
        "name": "Test App 1",
        "user_id": str(user_db.id)
    })
    assert clientapp_update.name == "Test App 1"
    assert clientapp_update.user_id == user_db.id        
    clientapp_db = db.execute(select(models.ClientApp)).scalars().first()
    clientapp_schema = schemas.ClientAppInDBBase.model_validate(clientapp_db)
    assert clientapp_schema.name == clientapp_db.name
    assert clientapp_schema.description == clientapp_db.description
    assert clientapp_schema.client_id == clientapp_db.client_id
    assert clientapp_schema.user.id == clientapp_db.user.id
    assert clientapp_schema.client_secret != None
    
# test chatroom schemas
def test_chatroom_schema(db):
    #test create chatroom object
    members = db.execute(select(models.User)).scalars().all()[:3]
    chatroom_create = schemas.ChatRoomCreate(**{
        "members": [schemas.ModelBase.model_validate(user).model_dump() for user in members]})
    assert chatroom_create.members[0].id == members[0].id
    new_members = db.execute(select(models.User)).scalars().all()[2:5]
    chatroom_update = schemas.ChatRoomUpdate(**{
         "members": [schemas.ModelBase.model_validate(user).model_dump() for user in new_members]
    })
    assert chatroom_update.members[0].id == new_members[0].id
    chatroom_db = db.execute(select(models.ChatRoom)).scalars().first()
    chatroom_schema = schemas.ChatRoomInDBBase.model_validate(chatroom_db)
    assert chatroom_schema.members[0].id == chatroom_db.members[0].id
    assert len(chatroom_schema.members) == len(chatroom_db.members)
    assert len(chatroom_schema.room_chats) == len(chatroom_db.room_chats)
    with pytest.raises(ValidationError):
        schemas.ChatRoomCreate(**{})

# test group schemas
def test_group_schema(db):
    chatroom = db.execute(select(models.ChatRoom)).scalars().first()
    group_create = schemas.GroupCreate(**{
        "name": "Test Group",
        "description": "Test Group Description",
        "chatroom_id": str(chatroom.id)
    })
    assert group_create.name == "Test Group"
    assert group_create.description == "Test Group Description"
    assert group_create.chatroom_id == chatroom.id
    group_update = schemas.GroupUpdate(**{
        "name": "Test Group1",
        "chatroom_id": str(chatroom.id)
    })
    assert group_update.name == "Test Group1"
    assert group_update.description == None
    assert group_update.chatroom_id == chatroom.id
    group_db = db.execute(select(models.Group)).scalars().first()
    group_schema = schemas.GroupInDBBase.model_validate(group_db)
    assert group_schema.name == group_db.name
    assert group_schema.description == group_db.description
    assert group_schema.chatroom.id == group_db.chatroom.id

# test chat schemas
def test_chat_schema(db):
    user = db.execute(select(models.User)).scalars().first()
    chatroom = db.execute(select(models.ChatRoom)).scalars().first()
    chat_create = schemas.ChatCreate(**{
        "message": "Test Message",
        "sender_id": str(user.id),
        "room_id": str(chatroom.id)
    })
    assert chat_create.message == "Test Message"
    assert chat_create.sender_id == user.id
    assert chat_create.room_id == chatroom.id
    chat_update = schemas.ChatUpdate(**{
        "message": "Test Message1",
        "is_read": True
    })
    assert chat_update.message == "Test Message1"
    assert chat_update.is_read == True
    chat_db = db.execute(select(models.Chat)).scalars().first()
    chat_schema = schemas.ChatInDBBase.model_validate(chat_db)
    assert chat_schema.message == chat_db.message
    assert chat_schema.is_read == chat_db.is_read
    assert chat_schema.sender.id == chat_db.sender.id
    assert chat_schema.room.id == chat_db.room.id
    assert len(chat_schema.media) == len(chat_db.media)

# test media schemas
def test_media_schema(db):
    chat = db.execute(select(models.Chat)).scalars().first()
    media_create = schemas.MediaCreate(**{
        "link": "https://test_link",
        "file_type": "mp4",
        "chat_id": str(chat.id)
    })
    assert media_create.link == "https://test_link"
    assert media_create.file_type == "mp4"
    assert media_create.chat_id == chat.id    
    media_update = schemas.MediaUpdate(**{"link": "test_link1","file_type": "test_type1"})
    assert media_update.link == "test_link1"
    assert media_update.file_type == "test_type1"
    media_db = db.execute(select(models.Media)).scalars().first()
    media_schema = schemas.MediaInDBBase.model_validate(media_db)
    assert media_schema.link == media_db.link
    assert media_schema.file_type == media_db.file_type
    assert media_schema.chat_id == media_db.chat.id