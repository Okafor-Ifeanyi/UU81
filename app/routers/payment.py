from fastapi import APIRouter, HTTPException, status, Depends
from app import oauth2
from .. import models, schemas, database
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def make_payment(payment_form: schemas.PaymentBase, db: Session =Depends(database.get_db), current_user: str = Depends(oauth2.get_current_user)):
    
    print(current_user)

    if payment_form.is_valid():
        payment = payment_form.save()
        return payment
    else:
        make_payment(payment_form, current_user)
    return payment_form

# @router.get("/")
# def verify_payment(payment_form: schemas.PaymentBase, db: Session =Depends(database.get_db), current_user: str = Depends(oauth2.get_current_user), ref= str):
#     payment = db.query(models.Payment, ref=ref)
#     verified = payment.verify_payment()
#     if verified:
#         raise HTTPException(status_code=status.HTTP_201_CREATED)
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                              detail = f"Payment route was not found, please try again in soon time")
#     return verified