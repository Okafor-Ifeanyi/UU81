from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
from sqlalchemy.orm import Session
from .. import schemas, models, utils, oauth2
from .email import send_reset_email
from ..config import settings
from ..database import get_db

router = APIRouter(
    tags=["Authentication"]
)

@router.post('/login', response_model= schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail= f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail= f"Invalid Credentials")
    access_token = oauth2.create_access_token(data ={"user_id": user.id, "admin": user.admin})
    
    return {"access_token": access_token, "token_type": "bearer"}



   

@router.post('/reset_password', response_model=schemas.TokenReset)
async def request_reset(reset_request: schemas.RequestReset, db: Session = Depends(get_db)):
    
    user = db.query(models.User).filter(
        models.User.email == reset_request.email).first()
 
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail= f"Invalid Credentials") 

    access_token = oauth2.create_access_token(data ={"user_id": user.id})

    await send_reset_email([reset_request.email])
 
    return {
        "message": "An email has been sent with instructions to reset your passsword", 
        "access_token": access_token, 
        "token_type": "bearer",
    }
    # return router.url_path_for('login')

@router.post('/reset_password/UU81')
def reset_token(reset_password: schemas.ResetPassword, db: Session = Depends(get_db), reset_user: int = Depends(oauth2.get_reset_user)):
    
    print(reset_user)
    
    if reset_password.password == reset_password.confirm_password:
        # Hash the password - user.password    
        hashed_password = utils.hash(reset_password.password)
        reset_password.password = hashed_password
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail= f"Abeg Crosscheck da Password")

    reset_user.password = hashed_password
    db.commit()
    return {router.url_path_for('login')} 