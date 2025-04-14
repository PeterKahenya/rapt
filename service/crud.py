from sqlalchemy.orm import Session
from sqlalchemy import select,update,delete
from pydantic import UUID4, BaseModel
import models
import schemas
from config import logger
from typing import Optional,Sequence
from sqlalchemy import or_, exc
from fastapi import HTTPException, Query


"""
    Generic crud operations
"""
# generic create object
async def create_obj(db: Session, model: models.Model, schema_model: BaseModel) -> models.Model:
    logger.info(f"Creating {model.__name__} with params: {schema_model.model_dump()}")
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
    logger.info(f"Getting {model.__name__} with id: {id}")
    try:
        return db.execute(select(model).where(model.id == id)).scalar_one()
    except exc.NoResultFound:
        raise HTTPException(status_code=404,detail={"message":f"{model.__name__} with id {id} not found"})

# generic get object or return None
async def get_obj_or_None(db: Session, model: models.Model, id: UUID4) -> models.Model:
    """
        Returns one object from the database by pk id or return None if no result is found
    """
    logger.info(f"Getting {model.__name__} with id: {id}")
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
            'ilike': lambda col, val: col.ilike("%"+val+"%"),
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
    logger.info(f"Deleting {model.__name__} with id: {id}")
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
    update_data = permission_update.model_dump(exclude_unset=True)
    db.execute(update(models.Permission).where(models.Permission.id == permission_id).values(**update_data))
    db.commit()
    db.refresh(permission)
    return permission

# update role
async def update_role(db: Session, role_id: UUID4, role_update_data: schemas.RoleUpdate) -> models.Role:
    logger.info(f"Updating  with id: {role_id}")
    role: models.Role = await get_obj_or_404(db=db, model=models.Role,  id=role_id)
    role.name = role_update_data.name if role_update_data.name else role.name
    role.description = role_update_data.description if role_update_data.description else role.description
    if role_update_data.permissions:
        role.permissions.clear()
        db.commit()
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
    user: models.User = await get_obj_or_404(db=db, model=models.User,  id=user_id)
    update_data = user_update_data.model_dump(exclude_unset=True)
    roles = update_data.pop('roles', None)
    if 'phone' in update_data:
        user_with_phone = db.execute(select(models.User).where(models.User.phone == update_data['phone'])).scalar_one_or_none()
        if user_with_phone and user_with_phone.id != user.id:
            raise HTTPException(status_code=409,detail={"message":"User with phone number already exists"})    
    db.execute(update(models.User).where(models.User.id == user_id).values(**update_data))
    if roles is not None:
        if len(roles) == 0:
            user.roles.clear()
        else:
            role_ids = [r["id"] for r in roles]
            new_roles = db.execute(select(models.Role).where(models.Role.id.in_(role_ids))).scalars().all()
            user.roles = new_roles
    db.commit()
    db.refresh(user)
    logger.info(f"User updated: {user}")
    return user

# create contact
async def create_contact(db: Session, contact_create_data: schemas.ContactCreate) -> models.Contact:
    logger.info(f"Creating contact with data: {contact_create_data.model_dump()}")
    contact_user = db.execute(select(models.User).where(models.User.phone == contact_create_data.phone)).scalar_one_or_none()
    if not contact_user:
        contact_user = models.User(phone=contact_create_data.phone, name=contact_create_data.name)
        db.add(contact_user)
        db.commit()
        db.refresh(contact_user)
    contact_db = db.execute(select(models.Contact)
                            .where(models.Contact.contact_id == contact_user.id)
                            .where(models.Contact.user_id == contact_create_data.user_id)
                        ).scalar_one_or_none()
    if not contact_db:
        contact_db = models.Contact(name=contact_create_data.name, user_id=contact_create_data.user_id, contact_id=contact_user.id)
        db.add(contact_db)
    else:
        contact_db.name = contact_create_data.name
    db.commit()
    db.refresh(contact_db)
    return contact_db

# update contact
async def update_contact(db: Session, contact_update_data: schemas.ContactUpdate) -> models.Contact:
    logger.info(f"Updating contact with user id: {contact_update_data.user_id} ")
    contact = db.execute(
                            select(models.Contact)
                            .where(models.Contact.user_id == contact_update_data.user_id)
                            .where(models.Contact.contact_id == contact_update_data.contact_id)
                        ).scalar_one()
    contact.name = contact_update_data.name
    db.commit()
    db.refresh(contact)
    return contact

# update client app
async def update_clientapp(db: Session, client_app_id: UUID4, client_app_update_data: schemas.ClientAppUpdate) -> models.ClientApp:
    logger.info(f"Updating client app with id: {client_app_id}")
    client_app = await get_obj_or_404(db=db, model=models.ClientApp,  id=client_app_id)
    _ = await get_obj_or_404(db=db, model=models.User,  id=client_app_update_data.user_id)
    client_app.name = client_app_update_data.name if client_app_update_data.name else client_app.name
    client_app.description = client_app_update_data.description if client_app_update_data.description else client_app.description
    db.commit()
    db.refresh(client_app)
    return client_app

# create chatroom
async def create_chatroom(db: Session, chatroom_create_data: schemas.ChatRoomCreate) -> models.ChatRoom:
    logger.error(f"Creating chatroom with data: {chatroom_create_data.model_dump()}")
    print(f"Creating chatroom with data: {chatroom_create_data.model_dump()}")
    members = []
    for user in chatroom_create_data.members:
        user_obj = await get_obj_or_404(db=db, model=models.User, id=user.id)
        members.append(user_obj)
    chatroom = models.ChatRoom(chatroom_create_data.socket_room_id, members)
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    return chatroom

# update chatroom
async def update_chatroom(db: Session, chatroom_id: UUID4, chatroom_update_data: schemas.ChatRoomUpdate) -> models.ChatRoom:
    logger.info(f"Updating chatroom with id: {chatroom_id}")
    chatroom = await get_obj_or_404(db=db, model=models.ChatRoom,  id=chatroom_id)
    if chatroom_update_data.members:
        if len(chatroom_update_data.members) < 2:
            raise ValueError("Chatroom must have at least 2 members")
        members = []
        for user in chatroom_update_data.members:
            user_db = await get_obj_or_404(db=db, model=models.User,  id=user.id)
            members.append(user_db)
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
    room: models.Chat = await get_obj_or_404(db=db, model=models.ChatRoom, id=chat_create_data.room_id)
    if not room.is_member(sender):
        raise HTTPException(status_code=403,detail={"message":"User is not a member of this chat"})   
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
                    page: int = Query(1, ge=1),
                    size: int = Query(10, ge=1, le=100),
                    sort_by: str = "created_at,asc",
                    **params
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