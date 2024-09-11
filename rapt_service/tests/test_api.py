import pytest
import models
import pytest
from sqlalchemy import select
from unittest.mock import patch

pytest_plugins = ('pytest_asyncio',)
    
"""Test API"""

# test authentication api calls
async def authenticate(client,db):
    app = db.execute(select(models.ClientApp)).scalars().first()
    user = db.execute(select(models.User).where(models.User.phone == "254102227267")).scalars().first()
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
        "phone": "254711111111",
        "name": "Test User11"
    }
    response = client.post("/auth/users/",json=user_data,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 201
    assert response.json()["phone"] == "254711111111"
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
    user_id = users[0].id
    contacts = [users[1].to_dict(),users[2].to_dict(),users[3].to_dict(),{"name": "Contact 33","phone": "254733333333"}]
    roles: list[models.Role] = db.execute(select(models.Role)).scalars().all()[:2]
    update_data = {
        "name": "Test User 22",
        "is_superuser": False,
        "is_active": False,
        "is_verified": True,
        "phone": "254722222222",
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
    
