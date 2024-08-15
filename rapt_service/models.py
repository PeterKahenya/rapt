import uuid
import datetime
from sqlalchemy import Column,Uuid,String,ForeignKey,Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,relationship
from typing import Optional,List

class Model(DeclarativeBase):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

role_permissions_association = Table(
    'role_permissions',
    Model.metadata,
    Column('role_id', Uuid, ForeignKey('roles.id',ondelete="CASCADE"), primary_key=True),
    Column('permission_id', Uuid, ForeignKey('permissions.id',ondelete="CASCADE"), primary_key=True)
)

class ContentType(Model):
    __tablename__ = "content_types"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)    
    content: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    permissions: Mapped[List["Permission"]] = relationship(back_populates="content_type")


class Permission(Model):
    __tablename__ = "permissions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    codename: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)
    content_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_types.id"))
    content_type: Mapped[ContentType] = relationship(back_populates="permissions")
    roles: Mapped[List["Role"]] = relationship(secondary=role_permissions_association,back_populates='permissions')


class Role(Model):
    __tablename__ = "roles"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,unique=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(onupdate=datetime.datetime.now)   
    permissions: Mapped[List["Permission"]] = relationship(secondary=role_permissions_association,back_populates='roles')



