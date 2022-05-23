from fastapi import APIRouter, Depends, Response, status, HTTPException
from typing import List, Optional
from app import oauth2
from sqlalchemy import func
from .. import models, schemas, database
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

@router.get("/user", response_model= List[schemas.BookingResponse], status_code=status.HTTP_200_OK)
def get_my_bookings(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user),
limit: int = 10, skip: int = 0):

    print(current_user)

    bookings = db.query(models.Booking).filter(models.Booking.user_id == current_user.id).all()
    return bookings 

@router.post("/events", response_model= List[schemas.BookingResponse], status_code=status.HTTP_200_OK)
def get_all_bookings(book:schemas.BookingGetEvents, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):

    print(current_user)

    event = db.query(models.Event).filter(models.Event.id == book.event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event id of {book.event_id} does not exist")

    bookings = db.query(models.Booking).filter(models.Booking.event_id == book.event_id).all()
    if current_user.admin == True:
        print(bookings)
        return bookings
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = f"User with email: {current_user.email} is not an Admin")


@router.post("/", status_code=status.HTTP_201_CREATED)
def book_event(book: schemas.Booking, db: Session =Depends(database.get_db), 
                    current_user: str = Depends(oauth2.get_current_user)):

    event = db.query(models.Event).filter(models.Event.id == book.event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event id of {book.event_id} does not exist")

    bookings_query = db.query(models.Booking).filter(
        models.Booking.event_id == book.event_id, 
        models.Booking.user_id == current_user.id)
    found_booking = bookings_query.first()
    if (book.dir == 1):
        if found_booking:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=f"{current_user.email} has already booked on {book.event_id} this event")
        new_book = models.Booking(event_id = book.event_id, user_id = current_user.id, space = book.space)
        db.add(new_book)
        db.commit()
        return {"message": "Successfully added to your bookings"}

    else:
        if not found_booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking not found")

        bookings_query.delete(synchronize_session=False)
        db.commit()

        return{"message": "Successfully deleted booking"}

@router.get("/{id}", response_model= schemas.BookingResponse)
def get_booking(id: int, db: Session = Depends(get_db), 
                    limit: int = 10, skip: int = 0, search: Optional[str]="", 
                        current_user: str = Depends(oauth2.get_current_user)):

    # event = db.query(models.Event).filter(models.Event.id == id).first()
    print(current_user)

    # booking = db.query(models.Booking).filter(models.Booking.id == id).limit(limit).offset(skip).first()

    booking = db.query(models.Booking).filter(models.Booking.id == id).first()

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"Booking with id: {id} was not found")


    return booking

# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def book_event(id: int, book: schemas.Booking, db: Session = Depends(database.get_db), current_user: str = Depends(oauth2.get_current_user)):
    
#     book_query = db.query(models.Booking).filter(
#             models.Booking.event_id == book.event_id, 
#             models.Booking.user_id == current_user.id,
#             models.Booking.id == id)
#     found_vote = book_query.first()

#     if not found_vote:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking not found")

#     book_query.delete(synchronize_session=False)
#     db.commit()

#     return{"message": "Successfully deleted booking"}
