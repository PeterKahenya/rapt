import uuid
import secrets
import string
import nanoid


def generate_random_string(length:int=6):
    choice_characters = string.ascii_uppercase+ string.digits
    random_string = ''.join(secrets.choice(choice_characters) for _ in range(length))
    return random_string

def generate_unique_socket_room_id():
    alphabet = string.ascii_lowercase+ string.digits
    return nanoid.generate(alphabet,50)

def generate_client_id():
    return str(uuid.uuid4())

def generate_client_secret():
    return secrets.token_urlsafe(50)