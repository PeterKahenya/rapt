import pytest
from sqlalchemy import select
from exceptions import JWTVerificationError
import models
from .conftest import test_settings as settings
from fastapi import HTTPException

# test to_dict method of models using contenttype
def test_to_dict_method(db):
    content_type = models.ContentType(content = "clientapps")
    db.add(content_type)
    db.commit()
    db.refresh(content_type)
    dict_content_type = content_type.to_dict()
    assert dict_content_type["id"] == str(content_type.id)
    assert dict_content_type["content"] == "clientapps"
    assert dict_content_type["created_at"] == content_type.created_at.isoformat()
    assert dict_content_type["updated_at"] == None

# test content_type model
def test_content_type_model(db):
    content_type = models.ContentType(content = "users1")
    db.add(content_type)
    db.commit()
    assert content_type in db

# test permission model
def test_permission_model(db):
    user_content_type = db.execute(select(models.ContentType).where(models.ContentType.content == "users1")).scalars().first()
    permission = models.Permission(name="Can View Users1",codename="read_users1",content_type=user_content_type)
    db.add(permission)
    db.commit()
    assert permission in db

# test role model
def test_role_model(db):
    user_content_type = db.execute(select(models.ContentType).where(models.ContentType.content == "users1")).scalars().first()
    permission1 = models.Permission(name="Can Edit Users",codename="edit_users1",content_type=user_content_type)
    permission2 = models.Permission(name="Can Delete Users",codename="delete_users1",content_type=user_content_type)
    role = models.Role(name="Admin",description="Admin Role")
    role.permissions.append(permission1)
    role.permissions.append(permission2)
    db.add(role)
    db.commit()
    assert role in db
    
# test user model, roles and contacts, verification code generation and validation and jwt token generation and validation
@pytest.mark.asyncio
async def test_user_model(db):
    user = models.User(name="Test User", phone="1234567890")
    db.add(user)
    db.commit()
    assert user in db
    user1 = models.User(name="Test User 1", phone="1234567891")
    user2 = models.User(name="Test User 2", phone="1234567892")
    db.add(user1)
    db.add(user2)
    db.commit()
    contact1 = models.Contact(name="Test Contact 1", user_id=user.id, contact_id=user1.id)
    contact2 = models.Contact(name="Test Contact 2", user_id=user.id, contact_id=user2.id)
    db.add(contact1)
    db.add(contact2)
    db.commit()
    db.add(user)
    db.commit()
    db.refresh(user)
    assert contact1 in user.contacts
    assert contact2 in user.contacts
    
    role = db.execute(select(models.Role)).scalars().first()
    role2 = models.Role(name="User",description="User Role")
    db.add(role2)
    db.commit()
    db.refresh(role2)
    user.roles.append(role)
    user.roles.append(role2)
    db.commit()
    db.refresh(user)
    assert role in user.roles
    assert role2 in user.roles
    
    # test verification code generation and validation
    user = await user.create_verification_code(db,settings.verification_code_length,settings.verification_code_expiry_seconds)
    assert user.phone_verification_code != None
    assert user.phone_verification_code_expiry_at != None
    validation_status = await user.validate_verification_code(user.phone_verification_code)
    assert validation_status == True
    validation_status = await user.validate_verification_code("123456")
    assert validation_status == False
    
    # test jwt token generation and validation
    clientapp = db.execute(select(models.ClientApp)).scalars().first()
    token = user.create_jwt_token(clientapp=clientapp,secret=settings.jwt_secret_key,algorithm=settings.jwt_algorithm,expiry_seconds=settings.access_token_expiry_seconds)
    phone,_,_ = models.User.verify_jwt_token(db,token,secret=settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
    assert user.phone == phone
    with pytest.raises(HTTPException):
        models.User.verify_jwt_token(db,token,secret=settings.jwt_secret_key,algorithm=settings.jwt_algorithm+"1")
    with pytest.raises(HTTPException):
        expired_token = user.create_jwt_token(clientapp=clientapp,secret=settings.jwt_secret_key,algorithm=settings.jwt_algorithm,expiry_seconds=-10)
        models.User.verify_jwt_token(db,expired_token,secret=settings.jwt_secret_key,algorithm=settings.jwt_algorithm)
    with pytest.raises(HTTPException):
        models.User.verify_jwt_token(db,token,secret="lsdslkdsldk",algorithm=settings.jwt_algorithm)

# test clientapp model and user relationship
def test_clientapp_model(db):
    user = db.execute(select(models.User).where(models.User.name == "Test User")).scalar_one()
    clientapp = models.ClientApp(name="Test App",description="Test App Description",user_id=user.id)
    db.add(clientapp)
    db.commit()
    db.refresh(clientapp)
    db.refresh(user)
    assert clientapp in db
    assert clientapp.user == user
    assert clientapp.client_id != None
    assert clientapp.client_secret != None
    assert clientapp in user.client_apps
    
    # test client_id and client_secret generation
    clientapp2 = models.ClientApp(name="Test App 2",description="Test App Description",user_id=user.id)
    db.add(clientapp2)
    db.commit()
    db.refresh(clientapp2)
    assert clientapp2.client_id != None
    assert clientapp2.client_secret != None
    assert clientapp2.client_id != clientapp.client_id
    assert clientapp2.client_secret != clientapp.client_secret
    
    # test clientapp must have a user, name and description
    with pytest.raises(ValueError):
        models.ClientApp(name=None,description="Test App Description",user_id=user.id)
    with pytest.raises(ValueError):
        models.ClientApp(name="Test App",description="Test App Description",user_id=None)
    with pytest.raises(ValueError):
        models.ClientApp(name="Test App",description=None,user_id=user.id)

# test chatroom model and user relationship
def test_chatroom_model(db):
    member1 = db.execute(select(models.User).where(models.User.name == "Test User")).scalar_one()
    member2 = db.execute(select(models.User).where(models.User.name == "Test User 1")).scalar_one()
    chatroom = models.ChatRoom(socket_room_id="SOCKROOMID0001",members=[member1,member2])
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    db.refresh(member1)
    db.refresh(member2)
    assert chatroom in db
    assert member1 in chatroom.members
    assert member2 in chatroom.members
    assert chatroom in member1.chatrooms
    assert chatroom in member2.chatrooms
    
    # chatroom must have at least 2 members
    with pytest.raises(ValueError):
        models.ChatRoom(socket_room_id="SOCKROOMID0002",members=[member1])
    # chatroom must have unique members
    with pytest.raises(ValueError):
        models.ChatRoom(socket_room_id="SOCKROOMID0003",members=[member1,member2,member1])
    # chatroom must have socket_room_id
    with pytest.raises(ValueError):
        models.ChatRoom(socket_room_id=None,members=[member1,member2])
    
# test group model and chatroom relationship
def test_group_model(db):
    chatroom = db.execute(select(models.ChatRoom)).scalars().first()
    if chatroom.group != None:
        assert True
    else:
        group = models.Group(name="Test Group",description="Test Group Description",chatroom_id=chatroom.id)
        db.add(group)
        db.commit()
        db.refresh(group)
        db.refresh(chatroom)
        assert group in db
        assert group.chatroom == chatroom
        assert chatroom.group == group
    
# test chat model and chatroom relationship and sender relationship
def test_chat_model(db):
    chatroom = db.execute(select(models.ChatRoom)).scalars().first()
    sender = chatroom.members[0]
    chat = models.Chat(message="Test Chat",room=chatroom,sender=sender)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    db.refresh(chatroom)
    db.refresh(sender)
    assert chat in db
    assert chat.room == chatroom
    assert chat.sender == sender
    assert chat.message == "Test Chat"
    assert chat in chatroom.room_chats
    assert chat in sender.chats
    
    with pytest.raises(ValueError):
        models.Chat(message=None,room=chatroom,sender=sender)
    with pytest.raises(ValueError):
        models.Chat(message="Test Chat",room=chatroom,sender=None)
    with pytest.raises(ValueError):
        models.Chat(message="Test Chat",room=None,sender=sender)
    with pytest.raises(ValueError):
        models.Chat(message="Test Chat",room=None,sender=None)

    # test sender must be a member of the chatroom
    sender2 = db.execute(select(models.User).where(models.User.name == "Test User 2")).scalar_one()
    with pytest.raises(ValueError):
        models.Chat(message="Test Chat",room=chatroom,sender=sender2)

# test media model and chat relationship
def test_media_model(db):
    chat = db.execute(select(models.Chat).where(models.Chat.message == "Test Chat")).scalar_one()
    media = models.Media(link="http://test.com/test.jpg",file_type="jpg",chat_id=chat.id)
    db.add(media)
    db.commit()
    db.refresh(media)
    db.refresh(chat)
    assert media in db
    assert media.chat == chat
    assert media in chat.media