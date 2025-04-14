from faker import Faker
import pytest
import models
import pytest
from sqlalchemy import select
from unittest.mock import patch
import uuid
import json
from .conftest import test_settings
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

pytest_plugins = ('pytest_asyncio',)
faker = Faker()

    
"""Test API"""

# test authentication api calls
async def authenticate(client: TestClient, db: Session):
    app = db.execute(select(models.ClientApp)).scalars().first()
    user = db.execute(select(models.User).where(models.User.phone == test_settings.superuser_phone)).scalars().first()
    if not user or not app:
        user = models.User(
            phone=test_settings.superuser_phone,
            name=faker.name(),
            is_superuser=True,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        client_app = models.ClientApp(name=faker.word(),description=faker.word(),user_id=user.id)
        db.add(client_app)
        db.commit()


    #test login by sending phone, client_id, client_secret as form data
    response = client.post("/auth/login",data={"phone": user.phone,"client_id": app.client_id,"client_secret": app.client_secret})
    assert response.status_code == 200
    assert response.json()["message"] == "SMS verification code sent"
    code = db.execute(select(models.User).where(models.User.phone == user.phone)).scalar_one().phone_verification_code
    #test verify by sending phone, code, client_id, client_secret as form data
    response = client.post("/auth/verify",data={"phone": user.phone,"phone_verification_code": code,"client_id": app.client_id,"client_secret": app.client_secret})
    assert response.status_code == 200
    assert response.json()["access_token"] != None
    #test refresh by sending access_token as form data
    access_token = response.json()["access_token"]
    response = client.post("/auth/refresh",data={"access_token": access_token,"client_id": app.client_id,"client_secret": app.client_secret})
    assert response.status_code == 200
    assert response.json()["access_token"] != None
    access_token = response.json()["access_token"]
    # test get user by access token
    response = client.get("/auth/me",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["phone"] == user.phone
    return access_token

@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_permissions_api(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    # test get permissions
    response = client.get("/auth/permissions/",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    # test get single permission
    permission_id = db.execute(select(models.Permission)).scalars().first().id
    response = client.get(f"/auth/permissions/{permission_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["name"] != None

# test roles api calls
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_roles_api(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    # create role
    role_data = {
        "name": "EndUser",
        "description": "End User"
    }
    response = client.post("/auth/roles/",json=role_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 201
    assert response.json()["name"] == "EndUser"
    # get roles
    response = client.get("/auth/roles/",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    # get single role
    role_db = db.execute(select(models.Role)).scalars().first()
    role_id = role_db.id
    response = client.get(f"/auth/roles/{role_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["name"] == role_db.name
    # update role
    permissions = db.execute(select(models.Permission)).scalars().all()[:3]    
    role_data = {
        "name": "EndUser1",
        "permissions": [p.to_dict() for p in permissions]
    }
    response = client.put(f"/auth/roles/{role_id}",json=role_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "EndUser1"
    assert len(response.json()["permissions"]) == 3
    assert response.json()["permissions"][0]["name"] == permissions[0].name
    # delete role
    response = client.delete(f"/auth/roles/{role_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204
    role = db.execute(select(models.Role).where(models.Role.id == role_id)).scalar_one_or_none()
    assert role is None

# test users api calls
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_users_api(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    # create user
    user_data = {
        "phone": faker.unique.phone_number()[0:11],
        "name": faker.name()
    }
    response = client.post("/auth/users/",json=user_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 201
    assert response.json()["phone"] == user_data["phone"]
    # get users
    response = client.get("/auth/users/",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    # get single user
    user_db = db.execute(select(models.User)).scalars().first()
    user_id = user_db.id
    response = client.get(f"/auth/users/{user_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["phone"] == user_db.phone
    # update user
    users: list[models.User] = db.execute(select(models.User)).scalars().all()
    user_id = users[1].id  if users[0].phone == test_settings.superuser_phone else users[0].id
    contacts = [users[1].to_dict(),users[2].to_dict(),users[3].to_dict(),{"name": "Contact 33","phone": faker.unique.phone_number()[0:11]}]
    roles: list[models.Role] = db.execute(select(models.Role)).scalars().all()[:2]
    update_data = {
        "name": "Test User 22",
        "is_superuser": False,
        "is_active": False,
        "is_verified": True,
        "phone": faker.unique.phone_number()[0:11],
        "contacts": contacts,
        "roles": [r.to_dict() for r in roles]
    }
    response = client.put(f"/auth/users/{user_id}",json=update_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["phone"] == update_data["phone"]
    # TODO: test contacts, roles
    # delete user
    response = client.delete(f"/auth/users/{user_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204
    user = db.execute(select(models.User).where(models.User.id == user_id)).scalar_one_or_none()
    assert user is None
    
# test contacts api calls
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_contacts_api(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    # profile
    response = client.get("/auth/me",headers={"Authorization": f"Bearer {access_token}"})
    user_id = response.json()["id"]
    # upload contacts
    contacts_data = [
        {"phone": faker.unique.phone_number()[0:11],"name": faker.name()},
        {"phone": faker.unique.phone_number()[0:11],"name": faker.name()},
        {"phone": faker.unique.phone_number()[0:11],"name": faker.name()},
    ]
    response = client.post(f"/auth/users/{user_id}/contacts",json=contacts_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 201
    assert len(response.json()) >= 3
    assert response.json()[0]["phone"] == contacts_data[0]["phone"]
    print(response.json())
    # update contact
    new_contact_data = {
        "name": "Test Contact",
        "user_id": user_id,
        "contact_id": response.json()[0]["contact_id"]       
    }
    response = client.put(f"/auth/users/{user_id}/contacts",json=new_contact_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["name"] == new_contact_data["name"]
    # read contacts
    response = client.get(f"/auth/users/{user_id}/contacts",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 1
    
# test clientapps api calls
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_clientapps_api(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    # create clientapp
    user_db = db.execute(select(models.User)).scalars().first()
    clientapp_data = {
        "name": "Test App",
        "description": "Test App Description",
        "user_id": str(user_db.id)
    }
    response = client.post("/auth/apps/",json=clientapp_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test App"
    # get clientapps
    response = client.get("/auth/apps/",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    # get single clientapp
    clientapp_db = db.execute(select(models.ClientApp)).scalars().first()
    clientapp_id = clientapp_db.id
    response = client.get(f"/auth/apps/{str(clientapp_id)}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["name"] == clientapp_db.name
    # update clientapp
    update_data = {
        "name": "Test App 1",
        "description": "Test App Description 1",
        "user_id": str(user_db.id)
    }
    response = client.put(f"/auth/apps/{str(clientapp_id)}",json=update_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test App 1"
    # delete clientapp
    response = client.delete(f"/auth/apps/{str(clientapp_id)}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204
    clientapp = db.execute(select(models.ClientApp).where(models.ClientApp.id == clientapp_id)).scalar_one_or_none()
    assert client
    
# test pagination
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_pagination(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    response = client.get("/api/auth/permissions/?page=1&size=1",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["total"] >= 1
    assert response.json()["page"] == 1
    assert response.json()["size"] == 1
    response = client.get("/api/auth/permissions/?page=2&size=1",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["total"] >= 1
    assert response.json()["page"] == 2
    assert response.json()["size"] == 1
    response = client.get("/api/auth/permissions/?page=2&size=2",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["total"] >= 1
    assert response.json()["page"] == 2
    assert response.json()["size"] == 2
    
# test search
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_search(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    response = client.get("/api/auth/permissions/?q=Delete",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    assert "Delete" in response.json()["data"][0]["name"]
    response = client.get("/api/auth/permissions/?q=Create",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    assert "Create" in response.json()["data"][0]["name"]
    response = client.get("/api/auth/permissions/?q=Update",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    assert "Update" in response.json()["data"][0]["name"]
    
# test filter using users api
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_filter(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    response = client.get("/api/auth/users/?name__ilike=admin&phone__ilike=254",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    assert "Admin".lower() in response.json()["data"][0]["name"].lower()
    response = client.get("/api/auth/users/?phone__ilike=254",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
    assert "254" in response.json()["data"][0]["phone"]
    
# test chatrooms api calls
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_chatrooms_api(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    # create chatroom
    members: list[models.User] = db.execute(select(models.User)).scalars().all()[:2]
    chatroom_data = {
        "members": [m.to_dict() for m in members],
    }
    create_response = client.post("/api/chat/rooms/",json=chatroom_data,headers={"Authorization": f"Bearer {access_token}"})
    assert create_response.status_code == 201
    assert create_response.json()["members"][0]["phone"] == members[0].phone
    
    # get chatrooms
    response = client.get("/api/chat/rooms/",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 1
    # get single chatroom
    chatroom_id = create_response.json()["id"]
    chatroom_db = db.execute(select(models.ChatRoom).where(models.ChatRoom.id == uuid.UUID(chatroom_id))).scalar_one_or_none()
    response = client.get(f"/api/chat/rooms/{chatroom_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    # update chatroom
    members: list[models.User] = db.execute(select(models.User)).scalars().all()[:3]
    chatroom_data = {
        "members": [m.to_dict() for m in members],
    }
    response = client.put(f"/api/chat/rooms/{chatroom_id}",json=chatroom_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["members"][0]["phone"] == members[0].phone
    # delete chatroom
    response = client.delete(f"/api/chat/rooms/{chatroom_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204
    chatroom = db.execute(select(models.ChatRoom).where(models.ChatRoom.id == uuid.UUID(chatroom_id))).scalar_one_or_none()
    assert chatroom is None

# test groups api calls
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_groups_api(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    # get chatroom where user is a member
        # create chatroom
    members: list[models.User] = db.execute(select(models.User)).scalars().all()[:2]
    chatroom_data = {
        "members": [m.to_dict() for m in members],
    }
    create_response = client.post("/api/chat/rooms/",json=chatroom_data,headers={"Authorization": f"Bearer {access_token}"})
    assert create_response.status_code == 201
    assert create_response.json()["members"][0]["phone"] == members[0].phone
    chatroom_id = create_response.json()["id"]
    create_group_data = {
        "name": "Test Group",
        "description": "Test Group Description",
        "chatroom_id": chatroom_id
    }
    create_group_response = client.post("/api/chat/groups/",json=create_group_data,headers={"Authorization": f"Bearer {access_token}"})
    assert create_group_response.status_code == 201
    assert create_group_response.json()["name"] == create_group_data["name"]
    assert create_group_response.json()["description"] == create_group_data["description"]
    assert create_group_response.json()["chatroom_id"] == create_group_data["chatroom_id"]
    # get groups
    response = client.get("/api/chat/groups/",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 1
    # get single group
    group_id = response.json()[0]["id"]
    group_db = db.execute(select(models.Group).where(models.Group.id == uuid.UUID(group_id))).scalar_one_or_none()
    response = client.get(f"/api/chat/groups/{group_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["name"] == group_db.name
    assert response.json()["description"] == group_db.description
    # update group
    group_data = {
        "name": "Test Group 1",
        "description": "Test Group Description 1",
        "chatroom_id": str(group_db.chatroom_id)
    }
    response = client.put(f"/api/chat/groups/{group_id}",json=group_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["name"] == group_data["name"]
    assert response.json()["description"] == group_data["description"]
    assert response.json()["chatroom_id"] == group_data["chatroom_id"]
    # delete group
    response = client.delete(f"/api/chat/groups/{group_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204
    group = db.execute(select(models.Group).where(models.Group.id == uuid.UUID(group_id))).scalar_one_or_none()
    assert group is None
    
# test get chat api calls
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_chats_api(mock_send_sms,client,db):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    # get chatroom where user is a member and that has chats
    rooms = db.execute(select(models.ChatRoom).where(models.ChatRoom.members.any(models.User.phone == test_settings.superuser_phone))).scalars().all()
    for r in rooms:
        if len(r.room_chats) != 0:
            room = r
            break
    else:
        room = r
        
    room_id = str(room.id)
    # get chats
    response = client.get(f"/api/chat/rooms/{room_id}/chats/",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) == len(room.room_chats)
    # get single chat
    chat_id = str(db.execute(select(models.Chat)).scalars().first().id)
    response = client.get(f"/api/chat/rooms/{room_id}/chats/{chat_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == chat_id
    # delete chat
    response = client.delete(f"/api/chat/rooms/{room_id}/chats/{chat_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204
    chat = db.execute(select(models.Chat).where(models.Chat.id == uuid.UUID(chat_id))).scalar_one_or_none()
    assert chat is None