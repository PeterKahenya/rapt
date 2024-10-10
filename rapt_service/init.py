from pydantic_settings import BaseSettings
from sqlalchemy import select
from sqlalchemy.orm import Session
from depends import get_db
import utils
import models
import config
from config import settings, logger


def initialize_db(db: Session, settings: BaseSettings, is_test: bool = False):
    for content in models.Model.metadata.tables.values():
        content_types = db.execute(select(models.ContentType).where(models.ContentType.content==content.name)).scalars().all()
        if not content_types:
            content_type = models.ContentType(content=content.name)
            db.add(content_type)
            db.commit()
            db.refresh(content_type)
        else:
            content_type = content_types[0]
        for permission in config.DEFAULT_PERMISSIONS_CLASSES:
            if not db.execute(select(models.Permission).where(models.Permission.codename==permission+"_"+content_type.content)).scalars().all():
                permission_db = models.Permission()
                permission_db.name = permission.title()+" "+content_type.content
                permission_db.codename = permission+"_"+content_type.content
                permission_db.content_type_id = content_type.id
                db.add(permission_db)
                db.commit()
                db.refresh(permission_db)
    # create superuser role
    superuser_role = db.execute(select(models.Role).where(models.Role.name=="Admin")).scalars().all()
    if not superuser_role:
        superuser_role = models.Role(name="Admin",description="System Administrator")
        for permission in db.execute(select(models.Permission)).scalars().all():
            superuser_role.permissions.append(permission)
        db.add(superuser_role)
        db.commit()
        db.refresh(superuser_role)
    else:
        superuser_role = superuser_role[0]
    # create chatter role
    chatter_role_get = db.execute(select(models.Role).where(models.Role.name=="Chatter")).scalars().all()
    if not chatter_role_get:
        chatter_role = models.Role(name="Chatter",description="Chat User")
    else:
        chatter_role = chatter_role_get[0]
        chatter_role.permissions.clear()
        db.commit()
        db.refresh(chatter_role)
    chatter_perm_codenames = [
        "read_users","update_users","create_users","delete_users",
        "read_contacts","create_contacts","update_contacts","delete_contacts",
        "create_chatrooms","read_chatrooms","update_chatrooms","delete_chatrooms",
        "read_groups","update_groups","create_groups","delete_groups",
        "read_chats","create_chats","delete_chats"
    ]
    chatter_role_permissions = db.execute(select(models.Permission).where(models.Permission.codename.in_(chatter_perm_codenames))).scalars().all()
    for permission in chatter_role_permissions:
        chatter_role.permissions.append(permission)
    db.add(chatter_role)
    db.commit()
    db.refresh(chatter_role)
    logger.info("Roles Chatter and Admin created")
    # create superuser
    superuser = db.execute(select(models.User).where(models.User.phone==settings.superuser_phone)).scalar_one_or_none()
    if not superuser:
        superuser = models.User(phone=settings.superuser_phone,name="Admin", is_superuser=True, is_active=True, is_verified=True)
        superuser.roles.append(superuser_role)
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
    # create default clientapp
    if superuser.client_apps:
        clientapp = superuser.client_apps[0]
    else:
        clientapp = models.ClientApp(name="DefaultApp",description="Default Application",user_id=superuser.id)
        db.add(clientapp)
        db.commit()
        db.refresh(clientapp)
    if not is_test:
        client_credentials_email = f"""
            Hello Admin,
            Your superuser phone number is: {superuser.phone}
            Your default clientapp credentials are:
            Client ID: {clientapp.client_id}
            Client Secret: {clientapp.client_secret}
        """
        utils.mailtrap_send_email(to=("kahenya0@gmail.com","System Admin"),subject="RaptChat Superuser Credentials",message=client_credentials_email)
    
    


if __name__ == '__main__':
    try:
        db = next(get_db())
        initialize_db(db, settings)
    except Exception as e:
        logger.error(e)
        raise e