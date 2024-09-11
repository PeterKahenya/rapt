from sqlalchemy import create_engine, select
import crud
import models
from sqlalchemy.orm import Session,sessionmaker
import config
from config import settings,DATABASE_URL


def initialize_db(db: Session):
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
                print(f"Permission: {permission_db.codename} added")
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
    # create superuser
    superuser = db.execute(select(models.User).where(models.User.phone=="254102227267")).scalar_one_or_none()
    if not superuser:
        superuser = models.User(phone="254102227267",name="Admin", is_superuser=True, is_active=True, is_verified=True)
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
        #TODO: Email developer with superuser phonenumber and default clientapp credentials
    print(f"Client ID: {clientapp.client_id} \nClient Secret: {clientapp.client_secret}")
    
    


if __name__ == '__main__':
    engine = create_engine(DATABASE_URL)
    models.Model.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False,autoflush=False,bind=engine)
    db = session_local()
    initialize_db(db)
    db.close()
    print("Database Initialized")