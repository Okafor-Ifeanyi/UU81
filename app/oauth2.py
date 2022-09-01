from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, models
from .config import settings

oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
EXPIRATION_DATE = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=EXPIRATION_DATE)
    to_encode.update({"exp": expire}) # (Prog-BIO)

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("user_id")
        admin: bool = payload.get("admin")

        if id is None:
            raise credentials_exception
        if admin is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id, admin=admin)
    except JWTError:
        raise credentials_exception

    return token_data
 
def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail=f"could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception) 

    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user


def verify_access_reset_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data
 
def get_reset_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail=f"could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_reset_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
