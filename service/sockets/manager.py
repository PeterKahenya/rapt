from fastapi import WebSocket
from config import logger
import datetime
import models
import schemas
import uuid

class ConnectionManager:
    
    def __init__(self):
        """
        {
            "room_id": {
                "user_id": websocket
            }
        }
        """
        self.rooms: dict[str, dict[dict[str,WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, room: str, user: models.User, db: models.Session):
        logger.error(f"User {user.phone} has joined the chat")
        await websocket.accept()
        if room not in self.rooms:
            self.rooms[room] = {}
        self.rooms[room][str(user.id)] = websocket
        user.last_seen = datetime.datetime.now(tz=datetime.timezone.utc)
        db.commit()
        db.refresh(user)
        user_dict = schemas.UserInDBBase.model_validate(user).model_dump()
        socket_message = schemas.SocketMessage(type=schemas.MessageType.ONLINE, user=user_dict, id=uuid.uuid4())
        await self.broadcast(socket_message, room) # always be broadcasting

    async def disconnect(self, websocket: WebSocket, room: str, user: models.User, db: models.Session):
        logger.error(f"User {user.phone} has left the chat")
        user.last_seen = datetime.datetime.now(tz=datetime.timezone.utc)
        db.commit()
        db.refresh(user)
        self.rooms[room].pop(str(user.id))
        if not self.rooms[room]:
            del self.rooms[room]
        user_dict = schemas.UserInDBBase.model_validate(user).model_dump()
        socket_message = schemas.SocketMessage(type=schemas.MessageType.OFFLINE, user=user_dict, id=uuid.uuid4())
        await self.broadcast(socket_message, room) # always be broadcasting        

    async def broadcast(self, message: schemas.SocketMessage, room: str):
        logger.error(f"Broadcasting message {message.type} to room {room}")
        for user_id,connection in self.rooms.get(room, {}).items():
            logger.error(f"Broadcasting message {message.type} to room {room} user_id {user_id} and connection {connection}")
            await connection.send_json(message.model_dump(mode="json"))