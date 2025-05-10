import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, WebSocket, WebSocketDisconnect, Depends
from honeybadger import honeybadger
from pydantic import UUID4
import models
from depends import authorize, get_db
import crud
from config import logger
import schemas
from .manager import ConnectionManager

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
            return
        await manager.connect(websocket, room=room.socket_room_id, user=user, db=db)
        # chat logic        
        while True:
            data = await websocket.receive_json()
            logger.info(f"User {user.phone} sent a message {data}")
            message = schemas.SocketMessage(**data)
            logger.info(f"User {user.phone} sent a message {message}")
            match message.type:
                case schemas.MessageType.CHAT:
                    chat_create = schemas.ChatCreate(**message.obj, sender_id=user.id, room_id=room.id)
                    chat = await crud.create_chat(db,chat_create)
                    socket_message = schemas.SocketMessage(type=schemas.MessageType.CHAT, user=message.user, obj=chat.to_dict(), id=message.id)
                    await manager.broadcast(socket_message, room.socket_room_id)
                case schemas.MessageType.READ:
                    chat: models.Chat = await crud.get_obj_or_None(db,models.Chat,UUID(message.obj["id"]))
                    if not chat:
                        logger.error(f"Chat with id {message.obj['id']} not found")
                        continue
                    else:
                        chat.is_read = True
                        db.commit()
                        db.refresh(chat)
                    socket_message = schemas.SocketMessage(type=message.type, user=message.user, obj=chat.to_dict())
                    await manager.broadcast(socket_message, room.socket_room_id)
                case _:
                    socket_message = schemas.SocketMessage(type=message.type, user=user.to_dict())
                    await manager.broadcast(socket_message, room.socket_room_id)    
    except WebSocketDisconnect:
        logger.error(f"User {user.phone} has disconnected")
        await manager.disconnect(websocket, room = room.socket_room_id, user=user, db=db)
    except HTTPException as e:
        logger.error(f"Room with id {room_id} not found")
        await websocket.close()

async def chatsocket_wrapper(
                        websocket: WebSocket, 
                        room_id: UUID4,
                        user: models.User = Depends(authorize(perm="create_chats")),
                        db: models.Session = Depends(get_db)
                    ):
    try:
        await chatsocket(websocket, room_id, user=user, db=db)
    except Exception as e:
        honeybadger.notify(e)
        raise