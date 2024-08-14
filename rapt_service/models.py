import uuid
import datetime
from sqlalchemy import Column,Uuid,String,DateTime,ForeignKey,Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Model(Base):
    __abstract__ = True
    metadata = Base.metadata

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

role_permissions_association = Table(
    'role_permissions',
    Model.metadata,
    Column('role_id', Uuid, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Uuid, ForeignKey('permissions.id'), primary_key=True)
)

class ContentType(Model):
    __tablename__ = "content_types"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    content = Column(String(100))
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)
    permissions = relationship("Permission",back_populates="content_type")


class Permission(Model):
    __tablename__ = "permissions"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    name = Column(String(100))
    codename = Column(String(100))
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)
    content_type_id = Column(Uuid,ForeignKey("content_types.id"))
    content_type = relationship("ContentType",back_populates="permissions")
    roles = relationship(
        'Role',
        secondary=role_permissions_association,
        back_populates='permissions'
    )


class Role(Model):
    __tablename__ = "roles"
    id = Column(Uuid,primary_key=True,unique=True,default=uuid.uuid4)
    name = Column(String(100))
    description = Column(String(500))
    created_at = Column(DateTime(),default=datetime.datetime.now)
    updated_at = Column(DateTime(),onupdate=datetime.datetime.now)
    permissions = relationship(
        'Permission',
        secondary=role_permissions_association,
        back_populates='roles'
    )



