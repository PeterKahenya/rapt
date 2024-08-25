from sqlalchemy.orm import Session
from sqlalchemy import select,update,delete
from pydantic import UUID4, BaseModel
import models
import schemas
from config import logger
from typing import List, Sequence
from sqlalchemy import or_


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
        query = query.where(CONDITION_MAP[condition](column, value))
    try:
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

