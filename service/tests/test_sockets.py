from unittest.mock import patch
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import select
from .test_api import authenticate
import models
from .conftest import test_settings


# test chat websockets
@pytest.mark.asyncio
@patch("utils.smsleopard_send_sms")
async def test_websockets(mock_send_sms,client,db: Session):
    mock_send_sms.return_value = True
    access_token: str = await authenticate(client,db)
    # get chatroom where user is a member
    room = db.execute(select(models.ChatRoom).where(models.ChatRoom.members.any(models.User.phone == test_settings.superuser_phone))).scalar_one_or_none()
    if room is None:
        user =  db.execute(select(models.User).where(models.User.phone == test_settings.superuser_phone)).scalar_one_or_none()
        user2 =  db.execute(select(models.User).where(models.User.phone != test_settings.superuser_phone)).scalars().first()
        room = models.ChatRoom(socket_room_id="test_sock_id",members=[user,user2])
        db.add(room)
        db.commit()
        db.refresh(room)
    room_id = str(room.id)

    with client.websocket_connect(f"/chatsocket/{room_id}",headers={"Authorization":f"Bearer {access_token}"}) as socket:
        # test connection and 'online' message
        data_json = socket.receive_json()
        assert data_json["type"] == "online" and data_json["user"]["phone"] == test_settings.superuser_phone
        # test chat message and response
        chat_socket_data = {
            "type": "chat",
            "user": {
                "phone": test_settings.superuser_phone
            },
            "obj": {
                "message": "Hello",
            }
        }
        socket.send_json(chat_socket_data)
        chat_alert_json = socket.receive_json()
        assert chat_alert_json["type"] == "chat" and chat_alert_json["obj"]["message"] == "Hello"
        # test read message and response
        read_socket_data = {
            "type": "read",
            "user": {
                "phone": test_settings.superuser_phone
            },
            "obj": {
                "id": chat_alert_json["obj"]["id"],
                "room_id": room_id,
            }
        }
        socket.send_json(read_socket_data)
        read_alert_json = socket.receive_json()
        assert read_alert_json["type"] == "read" and read_alert_json["obj"]["id"] == chat_alert_json["obj"]["id"]
        # test reading status
        read_status_socket_data = {
            "type": "reading",
            "user": {
                "phone": test_settings.superuser_phone
            }
        }
        socket.send_json(read_status_socket_data)
        read_status_alert_json = socket.receive_json()
        assert read_status_alert_json["type"] == "reading"
        # test away status
        away_status_socket_data = {
            "type": "away",
            "user": {
                "phone": test_settings.superuser_phone
            }
        }
        socket.send_json(away_status_socket_data)
        away_status_alert_json = socket.receive_json()
        assert away_status_alert_json["type"] == "away"
        # test typing status
        typing_status_socket_data = {
            "type": "typing",
            "user": {
                "phone": test_settings.superuser_phone
            }
        }
        socket.send_json(typing_status_socket_data)
        typing_status_alert_json = socket.receive_json()
        assert typing_status_alert_json["type"] == "typing"
        # test thinking status
        thinking_status_socket_data = {
            "type": "thinking",
            "user": {
                "phone": test_settings.superuser_phone
            }
        }
        socket.send_json(thinking_status_socket_data)
        thinking_status_alert_json = socket.receive_json()
        assert thinking_status_alert_json["type"] == "thinking"
        # test offline status
        offline_status_socket_data = {
            "type": "offline",
            "user": {
                "phone": test_settings.superuser_phone
            }
        }
        socket.send_json(offline_status_socket_data)
        offline_status_alert_json = socket.receive_json()
        assert offline_status_alert_json["type"] == "offline"
    