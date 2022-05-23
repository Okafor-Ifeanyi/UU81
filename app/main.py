from fastapi import FastAPI, Request
from typing import List
from .routers import event, user, auth, booking, payment
from .config import Settings
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


settings = Settings()
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(event.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(booking.router)
app.include_router(payment.router)

@app.get("/")
def root():
    return {"message": "I have added the new routers as I said today 23rd 10pm!"} 

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    error_message = f"Unexpected error occurred: {exc}"
    return JSONResponse(status_code=500, content={"detail": error_message})

@app.get('/', response_model=List[int])
async def foo() -> List[int]:
    return 1