from typing import Tuple
import uuid
import secrets
import string
import nanoid
from config import settings
import requests
import base64
import json

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

async def smsleopard_send_sms(phone: str, message: str) -> bool:
    try:
        phone = phone.strip()
        # mailtrap_send_email(("kahenya0@gmail.com","System Admin"),f"Backup OTP for {phone}",f"Your OTP is {message}")
        url = f"{settings.smsleopard_base_url}/sms/send"
        credentials = f"{settings.smsleopard_api_key}:{settings.smsleopard_api_secret}"
        headers = {
            "Authorization": f"Basic {base64.b64encode(credentials.encode()).decode()}"
        }
        body = {
            "source": "smsleopard",
            "destination": [{"number": phone}],
            "message": message
        }
        response = requests.post(url, data=json.dumps(body), headers=headers)
        if response.status_code == 201 and response.json().get("success"):
            return True
        else:
            raise Exception(f"{response.status_code} - {response.text}")
    except Exception as e:
        raise e
    
def mailtrap_send_email(to: Tuple[str,str], subject: str, message: str) -> bool:
    try:
        to_email, to_name = to
        url = "https://send.api.mailtrap.io/api/send"
        payload = {
            "to": [
                {
                    "email": to_email,
                    "name": to_name
                }
            ],
            "from": {
                "email": "hi@demomailtrap.com",
                "name": "Deployment Bot"
            },
            "subject": subject,
            "text": message,
            "category": "RaptChat"
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Api-Token": settings.mailtrap_api_token
        }
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        raise e