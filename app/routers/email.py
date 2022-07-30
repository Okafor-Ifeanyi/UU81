from typing import List
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, APIRouter
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from ..config import settings

# Mail configuration for sending request
conf = ConnectionConfig(
    MAIL_USERNAME= settings.mail_username,
    MAIL_PASSWORD= settings.mail_password,
    MAIL_FROM= settings.mail_from,
    MAIL_PORT= settings.mail_port,
    MAIL_SERVER= settings.mail_server,
    MAIL_FROM_NAME= settings.mail_from_name,
    # MAIL_FROM_NAME= "From BIO",
    MAIL_TLS= settings.mail_tls,
    MAIL_SSL= settings.mail_ssl,
    USE_CREDENTIALS= settings.use_credentials,
)


# Function to send the email
async def send_reset_email(email: List) -> JSONResponse:

    # Message Implementation html format
    html =  f"""
                <!DOCTYPE html>
                <html>
                <head>
                </head>
                <body>
                        <h3> Account Verification </h3>
                        <br>
                        <p>Welcome to the UU81 reset password private email service, please 
                        click on the link below to verify your account</p> 
                        <br>
                        <a style=" padding: 0.5rem; border-radius: 0.5rem; font-size: 0.8rem; 
                        text-decoration: arial; background: #ee88ee; color: white;" 
                        href="https://uu81.herokuapp.com/docs#/Authentication/reset_token_reset_password_UU81_post">
                            Verify your email
                        <a>
                    
                </body>
                </html>
            """

    # Fastapi mail sending format
    message = MessageSchema(
        subject="UNIQUE UNIPORT 81",
        recipients=email,  # List of recipients, as many as you can pass 
        body=html,
        subtype="html"
        )
    # Configuration of details then send message
    fm = FastMail(conf)
    await fm.send_message(message)
    
    return JSONResponse(status_code=200, content={"message": "email has been sent"}) 