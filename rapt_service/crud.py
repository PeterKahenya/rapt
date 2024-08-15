from sqlalchemy.orm import Session
from sqlalchemy import select,update,delete
from pydantic import UUID4, BaseModel
import models as models
import schemas as schemas
from config import logger
from typing import List


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

async def get_objects_list(db: Session, model: models.Model) -> List[models.Model]:
    logger.info(f"Getting all {model.__tablename__}")
    return db.scalars(select(model)).all()

async def filter_objects(db: Session, model: models.Model, params: dict) -> List[models.Model]:
    pass

#update
async def update_obj(db: Session, model: models.Model, id: UUID4, schema_model: BaseModel) -> models.Model:
    logger.info(f"Updating {model.__tablename__} with id: {id}")
    obj = await get_obj(db=db, model=model,  id=id)
    db.execute(update(model).where(model.id == id).values(schema_model.model_dump()))
    db.commit()
    db.refresh(obj)
    return obj

#delete
async def delete_obj(db: Session, model: models.Model, id: UUID4, ) -> models.Model:
    logger.info(f"Deleting {model.__tablename__} with id: {id}")
    obj = await get_obj(db=db, model=model,  id=id)
    db.execute(delete(model).where(model.id == obj.id))
    db.commit()
    return obj

#update role
async def update_role(db: Session, role_id: UUID4, role_update_data: schemas.RoleUpdate) -> models.Role:
    logger.info(f"Updating role with id: {role_id}")
    role = await get_obj(db=db, model=models.Role,  id=role_id)
    role.name = role_update_data.name
    role.description = role_update_data.description
    for perm in role_update_data.permissions:
        perm_obj = await get_obj(db=db, model=models.Permission,  id=perm.id)
        role.permissions.append(perm_obj)
    db.commit()
    db.refresh(role)
    return role

