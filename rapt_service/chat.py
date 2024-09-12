
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy import select
from depends import authorize, get_db, authenticate
import models
import schemas
import utils
import crud

router = APIRouter(dependencies=[Depends(get_db)])

@router.post("/rooms",status_code=201,tags=["Chat"])
async def create_room(
                        room_create: schemas.ChatRoomCreate,
                        user: models.User = Depends(authorize(perm="create_chatrooms")),
                        db: models.Session = Depends(get_db)
                    ) -> schemas.ChatRoomInDBBase:
    # check if the room already exists with the same members
    members = [await crud.get_obj_or_404(db,models.User,u.id) for u in room_create.members]
    if user not in members:
        members.append(user)
    chatrooms = db.execute(select(models.ChatRoom)).scalars().all()
    chatroom = next((room for room in chatrooms if set(room.members) == set(members)), None)
    if not chatroom:
        room_create.members.append(schemas.ModelBase(id=user.id))
        room_create.socket_room_id = utils.generate_unique_socket_room_id()
        chatroom = await crud.create_chatroom(db,room_create)
    return chatroom


# TODO: we should add admin permission to 'view_all_chatrooms' otherwise we should only return chatrooms where the user is a member

# get all chatrooms where the user is a member
@router.get("/rooms",response_model=list[schemas.ChatRoomInDBBase],tags=["Chat"])
async def get_rooms(
                        user: models.User = Depends(authorize(perm="view_chatrooms")),
                        db: models.Session = Depends(get_db)
                    ) -> List[schemas.ChatRoomInDBBase]:
    return user.chatrooms

# get single chatroom
@router.get("/rooms/{room_id}",response_model=schemas.ChatRoomInDBBase,tags=["Chat"])
async def get_room(
                        room_id: UUID4,
                        user: models.User = Depends(authorize(perm="view_chatrooms")),
                        db: models.Session = Depends(get_db)
                    ) -> schemas.ChatRoomInDBBase:
    chatroom = await crud.get_obj_or_404(db,models.ChatRoom,room_id)
    if user not in chatroom.members:
        raise HTTPException(status_code=403,detail={"message":"User not authorized to view this resource"})
    return chatroom

# update chatroom
@router.put("/rooms/{room_id}",response_model=schemas.ChatRoomInDBBase,tags=["Chat"])
async def update_room(
                        room_id: UUID4,
                        room_update: schemas.ChatRoomUpdate,
                        user: models.User = Depends(authorize(perm="update_chatrooms")),
                        db: models.Session = Depends(get_db)
                    ) -> schemas.ChatRoomInDBBase:
    # check if user is a member of the room_update members list using user id
    if not any([u.id == user.id for u in room_update.members]):
        room_update.members.append(schemas.ModelBase(id=user.id))
    return await crud.update_chatroom(db,room_id,room_update)

# delete chatroom
@router.delete("/rooms/{room_id}",status_code=204,tags=["Chat"])
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