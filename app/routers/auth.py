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

# Router name and tag
router = APIRouter(
    tags=["Authentication"]
)

@router.post('/login', response_model= schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # Get user using email address provided
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    # Report status code 403 if user not found
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail= f"Invalid Credentials")

    # Report status code 403 on wrong password
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail= f"Invalid Credentials")

    # Create JWt token with payload of user's ID and Admin
    access_token = oauth2.create_access_token(data ={"user_id": user.id, "admin": user.admin})
    
    # Return JWT token and type
    return {"access_token": access_token, "token_type": "bearer"}

    

@router.post('/reset_password', response_model=schemas.TokenReset)
async def request_reset(reset_request: schemas.RequestReset, db: Session = Depends(get_db)):
    
    # Query db for email provided
    user = db.query(models.User).filter(
        models.User.email == reset_request.email).first()
 
    # Report status code 403 if user not found
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail= f"Invalid Credentials") 

    # Create acces token with payload of user's ID
    # access_token = oauth2.create_access_token(data ={"user_id": user.id})

    # Send Email to email address provided. 
    # "await" makes the system wait till this task is achieved
    await send_reset_email([reset_request.email])
 
    return {
        "message": "An email has been sent with instructions to reset your passsword", 
        # "access_token": access_token, 
        "token_type": "bearer"
    }


@router.post('/reset_password/UU81')
def reset_token(reset_password: schemas.ResetPassword, token: str, db: Session = Depends(get_db)):

    # Verify and Get reset user
    token_str = f"'{token}'"
    user = oauth2.get_reset_user(token_str)
        
    # Cross-check the password, hash it and if it doesnt match
    # report status code 406
    if reset_password.password == reset_password.confirm_password:
        # Hash the password - user.password    
        hashed_password = utils.hash(reset_password.password)
        reset_password.password = hashed_password
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail= f"Abeg Crosscheck da Password")

    # Reset user password
    user.password = hashed_password
    db.commit()
    return {router.url_path_for('login')} 