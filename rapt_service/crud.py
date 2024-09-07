from sqlalchemy.orm import Session
from sqlalchemy import select,update,delete
from pydantic import UUID4, BaseModel
import models
import schemas
from config import logger
from typing import List, Any, Dict,Optional,Sequence
from sqlalchemy import or_
import datetime
from fastapi import Query
import uuid


"""
    Generic crud operations
"""
# generic create object
async def create_obj(db: Session, model: models.Model, schema_model: BaseModel) -> models.Model:
    logger.info(f"Creating {model.__name__.__class__} with params: {schema_model.model_dump()}")
    obj = model(**schema_model.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# generic get object or raise exception
async def get_obj_or_404(db: Session, model: models.Model, id: UUID4) -> models.Model:
    """
        Returns one object from the database by pk id or raise an exception:  sqlalchemy.orm.exc.NoResultFound if no result is found
    """
    logger.info(f"Getting {model.__name__.__class__} with id: {id}")
    return db.execute(select(model).where(model.id == id)).scalar_one()

# generic get object or return None
async def get_obj_or_None(db: Session, model: models.Model, id: UUID4) -> models.Model:
    """
        Returns one object from the database by pk id or return None if no result is found
    """
    logger.info(f"Getting {model.__name__.__class__} with id: {id}")
    return db.execute(select(model).where(model.id == id)).scalar_one_or_none()

# generic filter objects
async def filter_objects(db: Session, model: models.Model, params: dict = {}, sort_by:str = "created_at,asc" ) -> Sequence[models.Model]:
    """
        Returns a list of objects from the database filtered by the given params
    """
    logger.info(f"Filtering {model.__tablename__} with params: {params}")
    try:
        sort_key, sort_order = tuple(sort_by.split(','))
        sort_column = getattr(model, sort_key)
        CONDITION_MAP = {
            'eq': lambda col, val: col == val,
            'ne': lambda col, val: col != val,
            'lt': lambda col, val: col < val,
            'lte': lambda col, val: col <= val,
            'gt': lambda col, val: col > val,
            'gte': lambda col, val: col >= val,
            'like': lambda col, val: col.like(val),
            'ilike': lambda col, val: col.ilike(val),
            'contains': lambda col, val: col.contains(val),
            'in': lambda col, val: col.in_(val),
        }
        query = select(model)
        for key, value in params.items():
            if '__' in key:
                column_name, condition = key.split('__', 1)
            else:
                column_name, condition = key, 'eq'
            column = getattr(model, column_name)
            query = query.where(CONDITION_MAP[condition](column, value))
        query = query.order_by(sort_column.asc() if sort_order == 'asc' else sort_column.desc())
        logger.info(f"Query: {query.compile()}")
        return db.scalars(query).all()
    except Exception as e:
        logger.error(f"Error: {str(e)} filtering {model.__tablename__} with params: {params}")
        raise e
    
# generic search objects
async def search_objects(db: Session, model: models.Model, q: str) -> Sequence[models.Model]:
    logger.info(f"Searching {model.__tablename__} with query: {q}")
    query = select(model)
    conditions = []
    for column in model.__table__.columns:
        if column.type.python_type == str:
            conditions.append(column.ilike(f"%{q}%"))
    if conditions:
        query = query.where(or_(*conditions))
    return db.scalars(query).all()

# generic delete object
async def delete_obj(db: Session, model: models.Model, id: UUID4) -> bool:
    logger.info(f"Deleting {model.__name__.__class__} with id: {id}")
    obj = await get_obj_or_404(db, model, id)
    db.execute(delete(model).where(model.id == obj.id))
    db.commit()
    return True

# update content type
async def update_content_type(db: Session, content_type_id: UUID4, content_type_update: schemas.ContentTypeUpdate) -> models.ContentType:
    logger.info(f"Updating ContentType with id: {content_type_id}")
    content_type = await get_obj_or_404(db, models.ContentType, content_type_id)
    content_type.content = content_type_update.content
    db.commit()
    db.refresh(content_type)
    return content_type

# update permission
async def update_permission(db: Session, permission_id: UUID4, permission_update: schemas.PermissionUpdate) -> models.Permission:
    logger.info(f"Updating Permission with id: {permission_id}")
    permission = await get_obj_or_404(db, models.Permission, permission_id)
    permission.name = permission_update.name if permission_update.name else permission.name
    permission.codename = permission_update.codename if permission_update.codename else permission.codename
    permission.content_type_id = permission_update.content_type_id if permission_update.content_type_id else permission.content_type_id
    db.commit()
    db.refresh(permission)
    return permission

# update role
async def update_role(db: Session, role_id: UUID4, role_update_data: schemas.RoleUpdate) -> models.Role:
    logger.info(f"Updating  with id: {role_id}")
    role = await get_obj_or_404(db=db, model=models.Role,  id=role_id)
    role.name = role_update_data.name if role_update_data.name else role.name
    role.description = role_update_data.description if role_update_data.description else role.description
    if role_update_data.permissions:
        if len(role_update_data.permissions) == 0:
            role.permissions.clear()
            db.commit()
        else:
            for perm in role_update_data.permissions:
                perm_obj = await get_obj_or_404(db=db, model=models.Permission,  id=perm.id)
                if perm_obj not in role.permissions:
                    role.permissions.append(perm_obj)
            db.commit()
    db.commit()
    db.refresh(role)
    return role

#update user
async def update_user(db: Session, user_id: UUID4, user_update_data: schemas.UserUpdate) -> models.User:
    logger.info(f"Updating user with id: {user_id}")
    user = await get_obj_or_404(db=db, model=models.User,  id=user_id)
    user.name = user_update_data.name if user_update_data.name else user.name
    user.phone = user_update_data.phone if user_update_data.phone else user.phone
    user.is_superuser = user_update_data.is_superuser if user_update_data.is_superuser else user.is_superuser
    user.is_active = user_update_data.is_active if user_update_data.is_active else user.is_active
    user.is_verified = user_update_data.is_verified if user_update_data.is_verified else user.is_verified
    user.phone_verification_code = user_update_data.phone_verification_code if user_update_data.phone_verification_code else user.phone_verification_code
    user.phone_verification_code_expiry_at = user_update_data.phone_verification_code_expiry_at if user_update_data.phone_verification_code_expiry_at else user.phone_verification_code_expiry_at
    user.last_seen = user_update_data.last_seen if user_update_data.last_seen else user.last_seen
    if user_update_data.roles:
        if len(user_update_data.roles) == 0:
            user.roles.clear()
            db.commit()
        else:
            for role in user_update_data.roles:
                role_obj = await get_obj_or_404(db=db, model=models.Role,  id=role.id)
                if role_obj not in user.roles:
                    user.roles.append(role_obj)
            db.commit()
    logger.info(f"Updating user contacts with data: {user_update_data}")
    if user_update_data.contacts:
        if len(user_update_data.contacts) == 0:
            user.contacts.clear()
            db.commit()
        else:
            for contact in user_update_data.contacts:
                contact_obj = await get_obj_or_None(db=db, model=models.User,  id=contact.id)
                if not contact_obj:
                    contact_obj = await create_obj(db=db, model=models.User, schema_model=schemas.UserCreate(name=contact.name, phone=contact.phone))
                if contact_obj not in user.contacts:
                    user.contacts.append(contact_obj)
            db.commit()
    db.commit()
    db.refresh(user)
    return user

# update client app
async def update_clientapp(db: Session, client_app_id: UUID4, client_app_update_data: schemas.ClientAppUpdate) -> models.ClientApp:
    logger.info(f"Updating client app with id: {client_app_id}")
    client_app = await get_obj_or_404(db=db, model=models.ClientApp,  id=client_app_id)
    client_app.name = client_app_update_data.name if client_app_update_data.name else client_app.name
    client_app.description = client_app_update_data.description if client_app_update_data.description else client_app.description
    client_app.user_id = client_app_update_data.user_id if client_app_update_data.user_id else client_app.user_id
    db.commit()
    db.refresh(client_app)
    return client_app

# create chatroom
async def create_chatroom(db: Session, chatroom_create_data: schemas.ChatRoomCreate) -> models.ChatRoom:
    logger.info(f"Creating chatroom with data: {chatroom_create_data}")
    members = []
    for user in chatroom_create_data.members:
        user_obj = await get_obj_or_404(db=db, model=models.User, id=user.id)
        members.append(user_obj)
    chatroom = models.ChatRoom(chatroom_create_data.fcm_room_id, chatroom_create_data.socket_room_id, members)
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    return chatroom

# update chatroom
async def update_chatroom(db: Session, chatroom_id: UUID4, chatroom_update_data: schemas.ChatRoomUpdate) -> models.ChatRoom:
    logger.info(f"Updating chatroom with id: {chatroom_id}")
    chatroom = await get_obj_or_404(db=db, model=models.ChatRoom,  id=chatroom_id)
    chatroom.fcm_room_id = chatroom_update_data.fcm_room_id if chatroom_update_data.fcm_room_id else chatroom.fcm_room_id
    chatroom.socket_room_id = chatroom_update_data.socket_room_id if chatroom_update_data.socket_room_id else chatroom.socket_room_id
    if chatroom_update_data.members:
        if len(chatroom_update_data.members) < 2:
            raise ValueError("Chatroom must have at least 2 members")
        members = []
        for user in chatroom_update_data.members:
            user_obj = await get_obj_or_404(db=db, model=models.User,  id=user.id)
            members.append(user_obj)
        if len(members) != len(set(members)):
            raise ValueError("Chatroom members must be unique")
        for member in members:
            if member not in chatroom.members:
                chatroom.members.append(member)
    db.commit()
    db.refresh(chatroom)
    return chatroom

# update group
async def update_group(db: Session, group_id: UUID4, group_update_data: schemas.GroupUpdate) -> models.Group:
    logger.info(f"Updating group with id: {group_id}")
    group = await get_obj_or_404(db=db, model=models.Group,  id=group_id)
    group.name = group_update_data.name if group_update_data.name else group.name
    group.description = group_update_data.description if group_update_data.description else group.description
    if group_update_data.chatroom_id:
        chatroom = await get_obj_or_404(db=db, model=models.ChatRoom,  id=group_update_data.chatroom_id)
        group.chatroom_id = chatroom.id
    db.commit()
    db.refresh(group)
    return group

# create chat
async def create_chat(db: Session, chat_create_data: schemas.ChatCreate) -> models.Chat:
    logger.info(f"Creating chat with data: {chat_create_data}")
    sender = await get_obj_or_404(db=db, model=models.User, id=chat_create_data.sender_id)
    room = await get_obj_or_404(db=db, model=models.ChatRoom, id=chat_create_data.room_id)
    chat = models.Chat(chat_create_data.message, sender=sender, room=room)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    if chat_create_data.media:
        for media in chat_create_data.media:
            media_obj = models.Media(link=media.link, file_type=media.file_type, chat_id=chat.id)
            db.add(media_obj)
            db.commit()
            db.refresh(media_obj)
    db.refresh(chat)
    return chat

# update chat
async def update_chat(db: Session, chat_id: UUID4, chat_update_data: schemas.ChatUpdate) -> models.Chat:
    logger.info(f"Updating chat with id: {chat_id}")
    chat = await get_obj_or_404(db=db, model=models.Chat,  id=chat_id)
    chat.message = chat_update_data.message if chat_update_data.message else chat.message
    chat.is_read = chat_update_data.is_read if chat_update_data.is_read else chat.is_read
    if chat_update_data.media:
        for media in chat_update_data.media:
            if media.id:
                media_obj = await get_obj_or_404(db=db, model=models.Media,  id=media.id)
                if media_obj not in chat.media:
                    chat.media.append(media_obj)
            else:
                media_obj = models.Media(link=media.link, file_type=media.file_type)
                db.add(media_obj)
                db.commit()
                db.refresh(media_obj)
                chat.media.append(media_obj)
    db.commit()
    db.refresh(chat)
    return chat


# update media
async def update_media(db: Session, media_id: UUID4, media_update_data: schemas.MediaUpdate) -> models.Media:
    logger.info(f"Updating media with id: {media_id}")
    media = await get_obj_or_404(db=db, model=models.Media,  id=media_id)
    media.link = media_update_data.link if media_update_data.link else media.link
    media.file_type = media_update_data.file_type if media_update_data.file_type else media.file_type
    if media_update_data.chat_id:
        chat = await get_obj_or_404(db=db, model=models.Chat,  id=media_update_data.chat_id)
        media.chat_id = chat.id
    db.commit()
    db.refresh(media)
    return media

# paginate objects
async def paginate(
                    db: Session, 
                    model: models.Model,
                    schema: BaseModel,
                    q: Optional[str] = None,
                    params: Optional[Dict] = None,
                    page: int = Query(1, ge=1),
                    size: int = Query(10, ge=1, le=100),
                    sort_by: str = "created_at,asc"
                ) -> schemas.ListResponse:
    if q:
        data = await search_objects(db=db, model=model,q=q)
    elif params and len(params) > 0:
        data = await filter_objects(db=db, model=model,params=params,sort_by=sort_by)
    else:
        data = await filter_objects(db=db, model=model, params={},sort_by=sort_by)
    offset = (page - 1) * size
    total = len(data)
    paginated_items = data[offset:offset + size]
    paginated_items = [schema.model_validate(item) for item in paginated_items]
    
    return schemas.ListResponse(**{
        "total": total,
        "page": page,
        "size": size,
        "data": paginated_items
    })