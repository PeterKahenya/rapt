
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy import select
from depends import authorize, get_db, authenticate
import models
import schemas
import utils
import crud
from config import logger
from honeybadger.contrib.fastapi import HoneybadgerRoute

router = APIRouter(dependencies=[Depends(get_db)],route_class=HoneybadgerRoute)

@router.post("/rooms",status_code=201,tags=["Rooms"])
async def create_room(
                        room_create: schemas.ChatRoomCreate,
                        user: models.User = Depends(authorize(perm="create_chatrooms")),
                        db: models.Session = Depends(get_db)
                    ) -> schemas.ChatRoomInDBBase:
    # check if the current user is a member of the room_create members list using user id
    if user.id not in [u.id for u in room_create.members]:
        room_create.members.append(schemas.ModelBase(id=user.id))
    members = [await crud.get_obj_or_404(db,models.User,u.id) for u in room_create.members]
    chatrooms = db.execute(select(models.ChatRoom)).scalars().all()
    chatroom = next((room for room in chatrooms if set(room.members) == set(members)), None)
    if not chatroom:
        room_create.socket_room_id = utils.generate_unique_socket_room_id()
        chatroom = await crud.create_chatroom(db,room_create)
    return chatroom


# TODO: we should add admin permission to 'read_all_chatrooms' otherwise we should only return chatrooms where the user is a member

# get all chatrooms where the user is a member
@router.get("/rooms",response_model=list[schemas.ChatRoomInDBBase],tags=["Rooms"])
async def get_rooms(
                        user: models.User = Depends(authorize(perm="read_chatrooms")),
                        db: models.Session = Depends(get_db)
                    ) -> List[schemas.ChatRoomInDBBase]:
    return user.chatrooms

# get single chatroom
@router.get("/rooms/{room_id}",response_model=schemas.ChatRoomInDBBase,tags=["Rooms"])
async def get_room(
                        room_id: UUID4,
                        user: models.User = Depends(authorize(perm="read_chatrooms")),
                        db: models.Session = Depends(get_db)
                    ) -> schemas.ChatRoomInDBBase:
    chatroom = await crud.get_obj_or_404(db,models.ChatRoom,room_id)
    if user not in chatroom.members:
        raise HTTPException(status_code=403,detail={"message":"User not authorized to view this resource"})
    return chatroom

# update chatroom
@router.put("/rooms/{room_id}",response_model=schemas.ChatRoomInDBBase,tags=["Rooms"])
async def update_room(
                        room_id: UUID4,
                        room_update: schemas.ChatRoomUpdate,
                        user: models.User = Depends(authorize(perm="update_chatrooms")),
                        db: models.Session = Depends(get_db)
                    ) -> schemas.ChatRoomInDBBase:
    # check if logged in user is a member of the room_update members list using user id
    if not any([u.id == user.id for u in room_update.members]):
        room_update.members.append(schemas.ModelBase(id=user.id))
    return await crud.update_chatroom(db,room_id,room_update)

# delete chatroom
@router.delete("/rooms/{room_id}",status_code=204,tags=["Rooms"])
async def delete_room(
                        room_id: UUID4,
                        user: models.User = Depends(authorize(perm="delete_chatrooms")),
                        db: models.Session = Depends(get_db)
                    ):
    chatroom = await crud.get_obj_or_404(db,models.ChatRoom,room_id)
    if not any([u.id == user.id for u in chatroom.members]):
        raise HTTPException(status_code=403,detail={"message":"User not authorized to delete this resource"})
    is_deleted = await crud.delete_obj(db,models.ChatRoom,room_id)
    if not is_deleted:
        raise HTTPException(status_code=500,detail={"message":"Something happened while trying to delete the resource"})
    return None

# create group
@router.post("/groups",status_code=201,tags=["Groups"])
async def create_group(
                        group_create: schemas.GroupCreate,
                        user: models.User = Depends(authorize(perm="create_groups")),
                        db: models.Session = Depends(get_db)
                    ) -> schemas.GroupInDBBase:
    chatroom = await crud.get_obj_or_404(db,models.ChatRoom,group_create.chatroom_id)
    if user not in chatroom.members:
        raise HTTPException(status_code=403,detail={"message":"User not authorized to create group in this chatroom"})
    return await crud.create_obj(db,models.Group,group_create)

@router.get("/groups",response_model=list[schemas.GroupInDBBase],tags=["Groups"])
async def get_groups(
                        user: models.User = Depends(authorize(perm="read_groups")),
                        db: models.Session = Depends(get_db)
                    ) -> List[schemas.GroupInDBBase]:
    # get groups where the user is a member
    chatrooms = db.execute(select(models.ChatRoom).where(models.ChatRoom.members.contains(user))).scalars().all()
    chatroom_ids = [c.id for c in chatrooms]
    groups = db.execute(select(models.Group).where(models.Group.chatroom_id.in_(chatroom_ids))).scalars().all()
    return groups

@router.get("/groups/{group_id}",response_model=schemas.GroupInDBBase,tags=["Groups"])
async def get_group(
                        group_id: UUID4,
                        user: models.User = Depends(authorize(perm="read_groups")),
                        db: models.Session = Depends(get_db)
                    ) -> schemas.GroupInDBBase:
    group = await crud.get_obj_or_404(db,models.Group,group_id)
    if user not in group.chatroom.members:
        raise HTTPException(status_code=403,detail={"message":"User not authorized to view this resource"})
    return group

@router.put("/groups/{group_id}", response_model=schemas.GroupInDBBase,tags=["Groups"])
async def update_group(
                        group_id: UUID4,
                        group_update: schemas.GroupUpdate,
                        user: models.User = Depends(authorize(perm="update_groups")),
                        db: models.Session = Depends(get_db)
                    ) -> schemas.GroupInDBBase:
    group = await crud.get_obj_or_404(db,models.Group,group_id)
    if user not in group.chatroom.members:
        raise HTTPException(status_code=403,detail={"message":"User not authorized to update this resource"})
    return await crud.update_group(db,group_id,group_update)

@router.delete("/groups/{group_id}",status_code=204,tags=["Groups"])
async def delete_group(
                        group_id: UUID4,
                        user: models.User = Depends(authorize(perm="delete_groups")),
                        db: models.Session = Depends(get_db)
                    ):
    group = await crud.get_obj_or_404(db,models.Group,group_id)
    if user not in group.chatroom.members:
        raise HTTPException(status_code=403,detail={"message":"User not authorized to delete this resource"})
    is_deleted = await crud.delete_obj(db,models.Group,group_id)
    if not is_deleted:
        raise HTTPException(status_code=500,detail={"message":"Something happened while trying to delete the resource"})
    return None

# read chats
@router.get("/rooms/{room_id}/chats",response_model=list[schemas.ChatInDBBase],tags=["Chats"])
async def get_chats(
                        room_id: UUID4,
                        user: models.User = Depends(authorize(perm="read_chats")),
                        db: models.Session = Depends(get_db)
                    ) -> List[schemas.ChatInDBBase]:
    chatroom: models.ChatRoom = await crud.get_obj_or_404(db,models.ChatRoom,room_id)
    if not chatroom.is_member(user):
        return HTTPException(status_code=403,detail={"message":"User not authorized to view this resource"})
    return chatroom.room_chats

# get single chat
@router.get("/rooms/{room_id}/chats/{chat_id}",response_model=schemas.ChatInDBBase,tags=["Chats"])
async def get_chat(
                        room_id: UUID4,
                        chat_id: UUID4,
                        user: models.User = Depends(authorize(perm="read_chats")),
                        db: models.Session = Depends(get_db)
                    ) -> schemas.ChatInDBBase:
    chatroom: models.ChatRoom = await crud.get_obj_or_404(db,models.ChatRoom,room_id)
    if not chatroom.is_member(user):
        return HTTPException(status_code=403,detail={"message":"User not authorized to view this resource"})
    chat = await crud.get_obj_or_404(db,models.Chat,chat_id)
    return chat

# delete chat
@router.delete("/rooms/{room_id}/chats/{chat_id}",status_code=204,tags=["Chats"])
async def delete_chat(
                        room_id: UUID4,
                        chat_id: UUID4,
                        user: models.User = Depends(authorize(perm="delete_chats")),
                        db: models.Session = Depends(get_db)
                    ):
    chatroom: models.ChatRoom = await crud.get_obj_or_404(db,models.ChatRoom,room_id)
    if not chatroom.is_member(user):
        return HTTPException(status_code=403,detail={"message":"User not authorized to view this resource"})
    is_deleted = await crud.delete_obj(db,models.Chat,chat_id)
    if not is_deleted:
        raise HTTPException(status_code=500,detail={"message":"Something happened while trying to delete the resource"})
    return None