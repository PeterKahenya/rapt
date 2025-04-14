from fastapi import HTTPException
import pytest
from sqlalchemy import delete, select,exc
import crud
import models
import schemas
import uuid

pytest_plugins = ('pytest_asyncio',)

# test get_obj_or_404
@pytest.mark.asyncio
async def test_get_obj_or_404(db):
    content_type_db = db.execute(select(models.ContentType)).scalars().first()
    content_type_db = await crud.get_obj_or_404(db, models.ContentType, content_type_db.id)
    assert content_type_db is not None
    assert content_type_db in db
    with pytest.raises(HTTPException) as e:
        await crud.get_obj_or_404(db, models.ContentType, uuid.uuid4())

# test get_obj_or_None
@pytest.mark.asyncio
async def test_get_obj_or_None(db):
    content_type_db = db.execute(select(models.ContentType)).scalars().first()
    content_type_db = await crud.get_obj_or_None(db, models.ContentType, content_type_db.id)
    assert content_type_db is not None
    assert content_type_db in db
    content_type_db = await crud.get_obj_or_None(db, models.ContentType, uuid.uuid4())
    assert content_type_db is None
    
# test filter_objetcs using User model
@pytest.mark.asyncio
async def test_filter_objects(db):
    params = {
        "name__ilike": "%a%", 
        "phone__ilike": "%0%",
        "is_active": False,
        "created_at__gte": "2021-01-01",
    }
    users = await crud.filter_objects(db, models.User, params,sort_by="name,asc")
    assert users is not None
    assert all([user.name.lower().find("a") > -1 for user in users])
    users = await crud.filter_objects(db, models.User, {"name__contains":"ricardo shilly shally"})
    assert users is not None
    assert len(users) == 0
    with pytest.raises(AttributeError):
        await crud.filter_objects(db, models.User, {"country__eq":"Narnia"})

# test search_objects using User model
@pytest.mark.asyncio
async def test_search_objects(db):
    users = await crud.search_objects(db, models.User, "a")
    assert users is not None
    assert all([user.name.lower().find("a") > -1 for user in users])
    users = await crud.search_objects(db, models.User, "ricardo shilly shally")
    assert users is not None
    assert len(users) == 0

# test contenttype crud operations
@pytest.mark.asyncio
async def test_content_type_crud(db):
    # create contenttype
    content_type_params = schemas.ContentTypeCreate(**{"content": "ctyp1"})
    content_type_db = await crud.create_obj(db, models.ContentType, content_type_params)
    assert content_type_db in db
    # read single contenttype
    content_type_db1 = await crud.get_obj_or_None(db, models.ContentType, content_type_db.id)
    assert content_type_db1 == content_type_db
    with pytest.raises(HTTPException) as e:
        await crud.get_obj_or_404(db, models.ContentType, uuid.uuid4())
    # read all contenttypes
    content_types = await crud.filter_objects(db, models.ContentType, {})
    assert len(content_types) > 0
    # filter contenttypes
    content_types = await crud.filter_objects(db, models.ContentType, {"content__eq":"ctyp1"})
    assert len(content_types) > 0
    # update contenttype
    content_type_update = schemas.ContentTypeUpdate(**{"content": "ctyp2"})
    content_type_db = await crud.update_content_type(db, content_type_db.id, content_type_update)
    assert content_type_db.content == "ctyp2"
    # delete contenttype
    is_deleted = await crud.delete_obj(db, models.ContentType, content_type_db.id)
    assert is_deleted
    
# test permission crud operations
@pytest.mark.asyncio
async def test_permission_crud(db):
    # create permission
    content_type_db = db.execute(select(models.ContentType)).scalars().first()
    permission_params = schemas.PermissionCreate(**{
                                        "name": "Can Notify Users",
                                        "codename": "notify_users",
                                        "content_type_id": str(content_type_db.id)
                        })
    permission_db = await crud.create_obj(db, models.Permission, permission_params)
    assert permission_db in db
    # read single permission
    permission_db1 = await crud.get_obj_or_None(db, models.Permission, permission_db.id)
    assert permission_db1 == permission_db
    with pytest.raises(HTTPException) as e:
        await crud.get_obj_or_404(db, models.Permission, uuid.uuid4())
    # read all permissions
    permissions = await crud.filter_objects(db, models.Permission, {})
    assert len(permissions) > 0
    # filter permissions
    permissions = await crud.filter_objects(db, models.Permission, {"name__contains":"user"})
    assert len(permissions) > 0
    # update permission
    permission_update = schemas.PermissionUpdate(**{"name": "Can Notify Users1"})
    permission_db = await crud.update_permission(db, permission_db.id, permission_update)
    assert permission_db.name == "Can Notify Users1"
    # delete permission
    is_deleted = await crud.delete_obj(db, models.Permission, permission_db.id)
    assert is_deleted
    
# test role crud operations
@pytest.mark.asyncio
async def test_role_crud(db):
    # create role
    role_create = schemas.RoleCreate(**{
        "name": "Admin",
        "description": "Admin Role",
    })
    role_db = await crud.create_obj(db, models.Role, role_create)
    assert role_db in db
    # read single role
    role_db1 = await crud.get_obj_or_None(db, models.Role, role_db.id)
    assert role_db1 == role_db
    with pytest.raises(HTTPException) as e:
        await crud.get_obj_or_404(db, models.Role, uuid.uuid4())
    # read all roles
    roles = await crud.filter_objects(db, models.Role, {})
    assert len(roles) > 0
    # filter roles
    roles = await crud.filter_objects(db, models.Role, {"name__contains":"admin"})
    assert len(roles) > 0
    # update role
    permissions = db.execute(select(models.Permission)).scalars().all()[0:2]
    role_update = schemas.RoleUpdate(**{
        "name": "Admin1",
        "description": "Admin Role1",
        "permissions": [p.to_dict() for p in permissions]
    })
    role_db = await crud.update_role(db, role_db.id, role_update)
    assert role_db.name == "Admin1"
    # delete role
    is_deleted = await crud.delete_obj(db, models.Role, role_db.id)
    assert is_deleted

# test user crud operations
@pytest.mark.asyncio
async def test_user_crud(db):
    pass
    # create user
    user_create = schemas.UserCreate(**{
        "phone": "9994567899",
        "name": "Test User1",
        "device_fcm_token": "Test FCM Token",
        "is_superuser": False
    })
    user_db = await crud.create_obj(db, models.User, user_create)
    assert user_db in db
    # read single user
    user_db1 = await crud.get_obj_or_None(db, models.User, user_db.id)
    assert user_db1 == user_db
    with pytest.raises(HTTPException) as e:
        await crud.get_obj_or_404(db, models.User, uuid.uuid4())
    # read all users
    users = await crud.filter_objects(db, models.User, {})
    assert len(users) > 0
    # filter users
    users = await crud.filter_objects(db, models.User, {"phone__contains":"0"})
    assert len(users) > 0
    # update user
    roles = db.execute(select(models.Role)).scalars().all()[0:2]
    user_update = schemas.UserUpdate(**{
        "phone": "9994567890",
        "name": "Test User1",
        "is_superuser": True,
        "is_active": False,
        "is_verified": False,
        "phone_verification_code": "1234",
        "phone_verification_code_expiry_at": "2021-01-01",
        "device_fcm_token": "Test FCM Token1",
        "last_seen": "2021-01-01",
        "roles": [r.to_dict() for r in roles]
    })
    user_db = await crud.update_user(db, user_db.id, user_update)
    assert user_db.phone == "9994567890"
    # delete user
    is_deleted = await crud.delete_obj(db, models.User, user_db.id)
    assert is_deleted

# test contact crud operations
@pytest.mark.asyncio
async def test_contact_crud(db):
    # create contact
    users = db.execute(select(models.User)).scalars().all()
    user = users[0]
    contact_create = schemas.ContactCreate(**{
        "phone": "0790003390",
        "name": "Test Contact",
        "user_id": str(user.id)
    })
    contact_db = await crud.create_contact(db, contact_create)
    assert contact_db in db
    # update contact
    contact_update = schemas.ContactUpdate(**{
        "name": "Test Contact1",
        "user_id": str(contact_db.user_id),
        "contact_id": str(contact_db.contact_id)
    })
    contact_db = await crud.update_contact(db, contact_update)
    assert contact_db.phone == contact_db.contact.phone
    assert contact_db.name == "Test Contact1"

# test clientapp crud operations
@pytest.mark.asyncio
async def test_clientapp_crud(db):
    # create clientapp
    user_db = db.execute(select(models.User)).scalars().first()
    clientapp_create = schemas.ClientAppCreate(**{
        "name": "Test App",
        "description": "Test App Description",
        "user_id": user_db.id
    })
    clientapp_db = await crud.create_obj(db, models.ClientApp, clientapp_create)
    assert clientapp_db in db
    # read single clientapp
    clientapp_db1 = await crud.get_obj_or_None(db, models.ClientApp, clientapp_db.id)
    assert clientapp_db1 == clientapp_db
    with pytest.raises(HTTPException) as e:
        await crud.get_obj_or_404(db, models.ClientApp, uuid.uuid4())
    # read all clientapps
    clientapps = await crud.filter_objects(db, models.ClientApp, {})
    assert len(clientapps) > 0
    # filter clientapps
    clientapps = await crud.filter_objects(db, models.ClientApp, {"name__contains":"app"})
    assert len(clientapps) > 0
    # update clientapp
    clientapp_update = schemas.ClientAppUpdate(**{
        "name": "Test App1",
        "description": "Test App Description1",
        "user_id": user_db.id
    })
    clientapp_db = await crud.update_clientapp(db, clientapp_db.id, clientapp_update)
    assert clientapp_db.name == "Test App1"
    # delete clientapp
    is_deleted = await crud.delete_obj(db, models.ClientApp, clientapp_db.id)
    assert is_deleted

# test chatroom crud operations
@pytest.mark.asyncio
async def test_chatroom_crud(db):
    # create chatroom
    members = db.execute(select(models.User)).scalars().all()[0:2]
    chatroom_create = schemas.ChatRoomCreate(**{
        "socket_room_id": "socket_room_id",
        "members": [m.to_dict() for m in members]
    })
    chatroom_db = await crud.create_chatroom(db, chatroom_create)
    assert chatroom_db in db
    # read single chatroom
    chatroom_db1 = await crud.get_obj_or_None(db, models.ChatRoom, chatroom_db.id)
    assert chatroom_db1 == chatroom_db
    with pytest.raises(HTTPException) as e:
        await crud.get_obj_or_404(db, models.ChatRoom, uuid.uuid4())
    # read all chatrooms
    chatrooms = await crud.filter_objects(db, models.ChatRoom, {})
    assert len(chatrooms) > 0
    # filter chatrooms
    chatrooms = await crud.filter_objects(db, models.ChatRoom, {"socket_room_id__contains":"et"})
    assert len(chatrooms) > 0
    # update chatroom
    chatroom_update = schemas.ChatRoomUpdate(**{
        "members": [m.to_dict() for m in members]
    })
    chatroom_db = await crud.update_chatroom(db, chatroom_db.id, chatroom_update)
    assert chatroom_db in db
    # delete chatroom
    is_deleted = await crud.delete_obj(db, models.ChatRoom, chatroom_db.id)
    assert is_deleted


# test chatgroup crud operations
@pytest.mark.asyncio
async def test_chatgroup_crud(db):
    # create chatgroup
    members = db.execute(select(models.User)).scalars().all()[0:2]
    chatroom = models.ChatRoom(socket_room_id="SOCKROOMID00099",members=members)
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    chatgroup_create = schemas.GroupCreate(**{
        "name": "Test Group",
        "description": "Test Group Description",
        "chatroom_id": chatroom.id
    })
    chatgroup_db = await crud.create_obj(db, models.Group, chatgroup_create)
    assert chatgroup_db in db
    # read single chatgroup
    chatgroup_db1 = await crud.get_obj_or_None(db, models.Group, chatgroup_db.id)
    assert chatgroup_db1 == chatgroup_db
    with pytest.raises(HTTPException) as e:
        await crud.get_obj_or_404(db, models.Group, uuid.uuid4())
    # read all chatgroups
    chatgroups = await crud.filter_objects(db, models.Group, {})
    assert len(chatgroups) > 0
    # filter chatgroups
    chatgroups = await crud.filter_objects(db, models.Group, {"name__contains":"group"})
    assert len(chatgroups) > 0
    # update chatgroup
    chatgroup_update = schemas.GroupUpdate(**{
        "name": "Test Group1",
        "description": "Test Group Description1",
        "chatroom_id": chatroom.id
    })
    chatgroup_db = await crud.update_group(db, chatgroup_db.id, chatgroup_update)
    assert chatgroup_db.name == "Test Group1"
    # delete chatgroup
    is_deleted = await crud.delete_obj(db, models.Group, chatgroup_db.id)
    assert is_deleted
    

# test chatmessage crud operations
@pytest.mark.asyncio
async def test_chatmessage_crud(db):
    # create chatmessage
    chatroom = db.execute(select(models.ChatRoom)).scalars().first()
    sender = db.execute(select(models.User).where(models.User.id == chatroom.members[0].id)).scalars().first()
    chatmessage_create = schemas.ChatCreate(**{
        "message": "Hello World",
        "sender_id": sender.id,
        "room_id": chatroom.id,
        "media": [{"link":"https://www.google.com","file_type":"image/png"}]
    })
    chat_db = await crud.create_chat(db, chatmessage_create)
    assert chat_db in db
    # read single chatmessage
    chat_db1 = await crud.get_obj_or_None(db, models.Chat, chat_db.id)
    assert chat_db1 == chat_db
    with pytest.raises(HTTPException) as e:
        await crud.get_obj_or_404(db, models.Chat, uuid.uuid4())
    # read all chatmessages
    chatmessages = await crud.filter_objects(db, models.Chat, {})
    assert len(chatmessages) > 0
    # filter chatmessages
    chatmessages = await crud.filter_objects(db, models.Chat, {"message__contains":"Hello"})
    assert len(chatmessages) > 0
    # update chatmessage
    chatmessage_update = schemas.ChatUpdate(**{
        "message": "Hello World1",
        "is_read": True
    })
    chat_db = await crud.update_chat(db, chat_db.id, chatmessage_update)
    assert chat_db.message == "Hello World1"
    # delete chatmessage
    is_deleted = await crud.delete_obj(db, models.Chat, chat_db.id)
    assert is_deleted
    
# test media crud operations
@pytest.mark.asyncio
async def test_media_crud(db):
    # create media
    chat = db.execute(select(models.Chat)).scalars().first()
    media_create = schemas.MediaCreate(**{
        "link": "https://www.google.com",
        "file_type": "image/png",
        "chat_id": chat.id
    })
    media_db = await crud.create_obj(db, models.Media, media_create)
    assert media_db in db
    # read single media
    media_db1 = await crud.get_obj_or_None(db, models.Media, media_db.id)
    assert media_db1 == media_db
    with pytest.raises(HTTPException) as e:
        await crud.get_obj_or_404(db, models.Media, uuid.uuid4())
    # read all media
    medias = await crud.filter_objects(db, models.Media, {})
    assert len(medias) > 0
    # filter media
    medias = await crud.filter_objects(db, models.Media, {"link__contains":"google"})
    assert len(medias) > 0
    # update media
    media_update = schemas.MediaUpdate(**{
        "link": "https://www.google.com",
        "file_type": "image/png"
    })
    media_db = await crud.update_media(db, media_db.id, media_update)
    assert media_db.link == "https://www.google.com"
    # delete media
    is_deleted = await crud.delete_obj(db, models.Media, media_db.id)
    assert is_deleted

# test pagination
@pytest.mark.asyncio
async def test_pagination(db):
    # create 100 users
    for i in range(100):
        user_create = schemas.UserCreate(**{
            "phone": f"999456789{i}",
            "name": f"Test Paginate User{i}",
            "is_superuser": False
        })
        user_db = await crud.create_obj(db, models.User, user_create)
    # test pagination
    users = await crud.paginate(db, models.User, schemas.UserInDBBase, page=1, size=30,params={},q="paginate")
    assert len(users.data) == 30
    users = await crud.paginate(db, models.User, schemas.UserInDBBase, page=2, size=20,params={},q="paginate")
    assert len(users.data) == 20