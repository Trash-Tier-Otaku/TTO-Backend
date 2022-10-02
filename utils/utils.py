import secrets
import uuid

def get_new_code_verifier():
    token = secrets.token_urlsafe(100)
    return token[:128]

def get_new_uuid():
    return uuid.uuid4()