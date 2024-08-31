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


#create
async def create_obj(db: Session, model: models.Model, schema_model: BaseModel) -> models.Model:
    logger.info(f"Creating {model.__tablename__} with params: {schema_model.model_dump()}")
    obj = model(**schema_model.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

#read
async def get_obj(db: Session, model: models.Model, id: UUID4, ) -> models.Model:
    logger.info(f"Getting {model.__tablename__} with id: {id}")
    return db.execute(select(model).where(model.id == id)).scalar_one()

async def get_objects_list(db: Session, model: models.Model) -> Sequence[models.Model]:
    logger.info(f"Getting all {model.__tablename__}")
    return db.scalars(select(model)).all()

async def filter_objects(db: Session, model: models.Model, params: dict) -> Sequence[models.Model]:
    logger.info(f"Filtering {model.__tablename__} with params: {params}")
    try:
        CONDITION_MAP = {
            'eq': lambda col, val: col == val,
            'ne': lambda col, val: col != val,
            'lt': lambda col, val: col < val,
            'le': lambda col, val: col <= val,
            'gt': lambda col, val: col > val,
            'ge': lambda col, val: col >= val,
            'like': lambda col, val: col.like(val),
            'ilike': lambda col, val: col.ilike(val),
            'in': lambda col, val: col.in_(val),
        }
        query = select(model)
        for key, value in params.items():
            if '__' in key:
                column_name, condition = key.split('__', 1)
            else:
                column_name, condition = key, 'eq'
            column = getattr(model, column_name)
            if column.type.python_type == datetime.datetime:
                value = datetime.datetime.fromisoformat(value)
            elif column.type.python_type == int:
                value = int(value)
            query = query.where(CONDITION_MAP[condition](column, value))
        return db.scalars(query).all()
    except:
        return []
    

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

#update
async def update_obj(db: Session, model: models.Model, id: UUID4, schema_model: BaseModel) -> models.Model:
    logger.info(f"Updating {model.__tablename__} with id: {id} data {schema_model.model_dump()}")
    obj = await get_obj(db=db, model=model,  id=id)
    for key, value in schema_model.model_dump().items():
        if value is not None and type(value) != list:
            setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

#delete
async def delete_obj(db: Session, model: models.Model, id: UUID4, ) -> bool:
    logger.info(f"Deleting {model.__tablename__} with id: {id}")
    obj = await get_obj(db=db, model=model,  id=id)
    db.execute(delete(model).where(model.id == obj.id))
    db.commit()
    return True

#update role
async def update_role(db: Session, role_id: UUID4, role_update_data: schemas.RoleUpdate) -> models.Role:
    logger.info(f"Updating role with id: {role_id}")
    role = await get_obj(db=db, model=models.Role,  id=role_id)
    role = await update_obj(db=db, model=models.Role, id=role_id, schema_model=role_update_data)
    for perm in role_update_data.permissions:
        perm_obj = await get_obj(db=db, model=models.Permission,  id=perm.id)
        if perm_obj not in role.permissions:
            role.permissions.append(perm_obj)
    db.commit()
    db.refresh(role)
    return role

#update or create user
async def update_or_create_user_contact(db: Session, user_update_data: schemas.Contact) -> models.User:
    logger.info(f"Updating or creating user with data: {user_update_data}")
    user = await filter_objects(db=db, model=models.User, params={"phone":user_update_data.phone})
    if len(user) == 0:
        user = await create_obj(db=db, model=models.User, schema_model=user_update_data)
    else:
        user = user[0]
        user.name = user_update_data.name
        db.commit()
    db.refresh(user)
    return user


#update user
async def update_user(db: Session, user_id: UUID4, user_update_data: schemas.UserUpdate) -> models.User:
    logger.info(f"Updating user with id: {user_id}")
    user = await get_obj(db=db, model=models.User,  id=user_id)
    user = await update_obj(db=db, model=models.User, id=user_id, schema_model=user_update_data)
    for role in user_update_data.roles:
        role_obj = await get_obj(db=db, model=models.Role,  id=role.id)
        if role_obj not in user.roles:
            user.roles.append(role_obj)
    logger.info(f"Updating user contacts with data: {user_update_data}")
    if not user.contacts:
        user.contacts.clear()
        for contact in user_update_data.contacts:
            user_contact = await update_or_create_user_contact(db=db, user_update_data=contact)
            logger.info(f"User contact: {user_contact.to_dict()}")
            user.contacts.append(user_contact)
    db.commit()
    db.refresh(user)
    return user


class Pagination(BaseModel):
    total: int
    page: int
    size: int
    data: List[Any]

async def paginate(
                    db: Session, 
                    model: models.Model,
                    schema: BaseModel,
                    q: Optional[str] = None,
                    params: Optional[Dict] = None,
                    page: int = Query(1, ge=1),
                    size: int = Query(10, ge=1, le=100),
                ) -> Pagination:
    if q:
        data = await search_objects(db=db, model=model,q=q)
    elif params and len(params) > 0:
        data = await filter_objects(db=db, model=model,params=params)
    else:
        data = await get_objects_list(db=db, model=model)
    offset = (page - 1) * size
    total = len(data)
    paginated_items = data[offset:offset + size]
    paginated_items = [schema.model_validate(item) for item in paginated_items]
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "data": paginated_items
    }