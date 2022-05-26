from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
from sqlalchemy.orm import Session
from .. import schemas, models, utils, oauth2
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


# Mail configuration for sending request
conf = ConnectionConfig(
    MAIL_USERNAME= settings.mail_username,
    MAIL_PASSWORD= settings.mail_password,
    MAIL_FROM= settings.mail_from,
    MAIL_PORT= settings.mail_port,
    MAIL_SERVER= settings.mail_server,
    MAIL_TLS= settings.mail_tls,
    MAIL_SSL= settings.mail_ssl,
    USE_CREDENTIALS= settings.use_credentials,
)

# link = print(router.url_path_for('request_reset'))
link = print("//https")

html = f"""
<p> Hi current_user /n /n Kindly click here {link} to reset your password /n /n Thanks /n UU81</p> 
"""


async def send_reset_email(user) -> JSONResponse:
    message = MessageSchema(
        subject="UNIQUE UNIPORT 81",
        recipients=user.dict().get("email"),  # List of recipients, as many as you can pass 
        body=html,
        subtype="html"
        )
    fm = FastMail(conf)
    print(conf.MAIL_FROM, conf.MAIL_PASSWORD)
    await fm.send_message(message)
    
    return JSONResponse(status_code=200, content={"message": "email has been sent"}) 
   

@router.post('/reset_password', response_model=schemas.TokenReset)
def request_reset(reset_request: schemas.RequestReset, db: Session = Depends(get_db)):
    
    user = db.query(models.User).filter(
        models.User.email == reset_request.email).first()
 
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail= f"Invalid Credentials") 

    access_token = oauth2.create_access_token(data ={"user_id": user.id})

    send_reset_email(user)
 
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