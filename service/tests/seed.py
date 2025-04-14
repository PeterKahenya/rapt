from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import Session
import models

faker = Faker()

# seed database with faker data for all models
def seed_db(db: Session):
    # faker add content types
    for i in range(10):
        content_type = models.ContentType(content=faker.unique.word())
        db.add(content_type)
    db.commit()
    # faker add permissions
    for i in range(10):
        content_type = db.execute(select(models.ContentType)).scalars().first()
        permission = models.Permission(name=faker.word(),codename=faker.unique.word(),content_type=content_type)
        db.add(permission)
    db.commit()
    # faker add roles
    for i in range(10):
        permissions = db.execute(select(models.Permission)).scalars().all()[0:5]
        role = models.Role(name=faker.word(),description=faker.word(),permissions=permissions)
        db.add(role)
    db.commit()
    # faker add users
    for i in range(10):
        user = models.User(phone=f"254 {faker.unique.phone_number()[0:8]}",name=faker.name(),roles=db.execute(select(models.Role)).scalars().all()[0:5])
        db.add(user)
    db.commit()
    # faker add contacts
    user = db.execute(select(models.User)).scalars().first()
    for i in range(20):
        contact_user = models.User(phone=faker.unique.phone_number()[0:11],name=faker.name())
        db.add(contact_user)
        db.commit()
        contact = models.Contact(name=faker.name(),user_id=user.id,contact_id=contact_user.id)
        db.add(contact_user)
        db.add(contact)
        db.add(user)
    db.commit()
    # faker client apps
    for i in range(10):
        user = db.execute(select(models.User)).scalars().first()
        client_app = models.ClientApp(name=faker.word(),description=faker.word(),user_id=user.id)
        db.add(client_app)
    db.commit()
    # faker add chatrooms
    members = db.execute(select(models.User)).scalars().all()[0:15]
    for i in range(11):
        chatroom = models.ChatRoom(socket_room_id=faker.uuid4(),members=[members[0],members[i+1]])
        db.add(chatroom)
    db.commit()
    # faker add chat groups
    chatrooms = db.execute(select(models.ChatRoom)).scalars().all()[0:7]
    for i in range(4):
        chat_group = models.Group(name=faker.word(),description=faker.text(),chatroom=chatrooms[i])
        db.add(chat_group)
    db.commit()
    # faker add chat messages
    for i in range(6):
        chatroom = chatrooms[i]
        message = models.Chat(message=faker.text(),room=chatroom,sender=chatroom.members[0 if i%2==0 else 1])
        db.add(message)
    db.commit()
    # faker add media
    chats = db.execute(select(models.Chat)).scalars().all()[0:6]
    for i in range(5):
        media = models.Media(link=faker.url(),file_type=faker.file_extension(),chat=chats[i])
        db.add(media)
    db.commit()
