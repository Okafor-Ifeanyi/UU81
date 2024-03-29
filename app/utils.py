from itsdangerous import URLSafeTimedSerializer
from .config import settings
from passlib.context import CryptContext
from fastapi import HTTPException, status
import re

pwd_content = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str): # Prog-BIO
    return pwd_content.hash(password)

def verify(plain_password, hashed_password):
    return pwd_content.verify(plain_password, hashed_password)

def phone_number(number):
    phone = re.compile("^\+?\d{0,3}[-.\s]?\(?\d{0,3}\)?[-.\s]?\d{0,3}[-.\s]?\d{0,4}$") 

    if phone.match(number):
        return number
    else: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="wrong Format")

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email)

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, max_age=expiration)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Unable to validate credentials", headers={"WWW-Authenticate": "Bearer"})
    return email