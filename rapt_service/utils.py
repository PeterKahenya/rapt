import uuid
import random


def generate_random_string(length:int=6):
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=length))

def generate_client_id():
    return str(uuid.uuid4())

def generate_client_secret():
    return str(uuid.uuid4())+str(uuid.uuid4())