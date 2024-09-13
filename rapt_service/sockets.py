import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import UUID4
import models
from depends import authorize, get_db
import crud
from config import logger
import sqlalchemy
import schemas

class MessageType(str, Enum):
    ONLINE = "online" # user is online
    OFFLINE = "offline" # user is offline
    CHAT = "chat"
    READ = "read"
    READING = "reading"
    AWAY = "away"
    TYPING = "typing"
    THINKING = "thinking"
    
class SocketMessage(schemas.BaseModel): # for websocket messages both incoming and outgoing
    type: MessageType
    user: dict # user object
    obj: Optional[dict] = None # for chat messages
    timestamp: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)

class ConnectionManager:
    
    def __init__(self):
        self.rooms: dict[str, dict[dict[str,WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, room: str, user: models.User, db: models.Session):
        logger.info(f"User {user.phone} has joined the chat")
        await websocket.accept()
        if room not in self.rooms:
            self.rooms[room] = {}
        self.rooms[room][str(user.id)] = websocket
        user.last_seen = datetime.datetime.now(tz=datetime.timezone.utc)
        db.commit()
        db.refresh(user)
        user_dict = schemas.UserInDBBase.model_validate(user).model_dump()
        socket_message = SocketMessage(type=MessageType.ONLINE, user=user_dict)
        await self.broadcast(socket_message, room) # always be broadcasting

    async def disconnect(self, websocket: WebSocket, room: str, user: models.User, db: models.Session):
        logger.info(f"User {user.phone} has left the chat")
        user.last_seen = datetime.datetime.now(tz=datetime.timezone.utc)
        db.commit()
        db.refresh(user)
        self.rooms[room].pop(str(user.id))
        if not self.rooms[room]:
            del self.rooms[room]
        user_dict = schemas.UserInDBBase.model_validate(user).model_dump()
        socket_message = SocketMessage(type=MessageType.OFFLINE, user=user_dict)
        await self.broadcast(socket_message, room) # always be broadcasting        

    async def broadcast(self, message: SocketMessage, room: str):
        for id,connection in self.rooms.get(room, {}).items():
            await connection.send_json(message.model_dump(mode="json"))

manager = ConnectionManager()

async def chatsocket(
                        websocket: WebSocket, 
                        room_id: UUID4,
                        user: models.User = Depends(authorize(perm="create_chats")),
                        db: models.Session = Depends(get_db)
                    ):
    try:
        # connection logic
        room: models.ChatRoom = await crud.get_obj_or_404(db,models.ChatRoom,room_id)
        logger.info(f"User {user.phone} is trying to connect to room {room.to_dict()}")
        if not room.is_member(user):
            logger.error(f"User {user.phone} is not a member of room {room_id}")
            await websocket.close()
        await manager.connect(websocket, room=room.socket_room_id, user=user, db=db)
        # chat logic        
        while True:
            data = await websocket.receive_json()
            logger.info(f"User {user.phone} sent a message {data}")
            message = SocketMessage(**data)
            logger.info(f"User {user.phone} sent a message {message}")
            match message.type:
                case MessageType.CHAT:
                    chat_create = schemas.ChatCreate(**message.obj, sender_id=user.id, room_id=room.id)
                    chat = await crud.create_chat(db,chat_create)
                    socket_message = SocketMessage(type=MessageType.CHAT, user=message.user, obj=chat.to_dict())
                    await manager.broadcast(socket_message, room.socket_room_id)
                case MessageType.READ:
                    chat: models.Chat = await crud.get_obj_or_None(db,models.Chat,UUID(message.obj["id"]))
                    if not chat:
                        logger.error(f"Chat with id {message.obj['id']} not found")
                        continue
                    else:
                        chat.is_read = True
                        db.commit()
                        db.refresh(chat)
                    socket_message = SocketMessage(type=message.type, user=message.user, obj=chat.to_dict())
                    await manager.broadcast(socket_message, room.socket_room_id)
                case _:
                    socket_message = SocketMessage(type=message.type, user=user.to_dict())
                    await manager.broadcast(socket_message, room.socket_room_id)    
    except WebSocketDisconnect:
        logger.error(f"User {user.phone} has disconnected")
        await manager.disconnect(websocket, room = room.socket_room_id, user=user, db=db)
    except HTTPException as e:
        logger.error(f"Room with id {room_id} not found")
        await websocket.close()