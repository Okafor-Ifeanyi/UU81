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

    # Query bookings db for all booking of the current user
    bookings = db.query(models.Booking).filter(models.Booking.user_id == current_user.id).all()
    
    # Return Bookings found
    return bookings 

@router.get("/events/{id}", response_model= List[schemas.BookingResponse], status_code=status.HTTP_200_OK)
def get_all_bookings(id : int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):

    # Query db for the event with ID provided
    event = db.query(models.Event).filter(models.Event.id == id).first()
    
    # Report status code 404 if event id isn't found
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event id of {id} does not exist")

    # Query db for all bookings with the "event id" matching the id provided
    # If current user = Admin show data else Report status code 401
    bookings = db.query(models.Booking).filter(models.Booking.event_id == id).all()
    if current_user.admin == True:
        print(bookings)
        return bookings
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = f"User with email: {current_user.email} is not an Admin")


@router.post("/", status_code=status.HTTP_201_CREATED)
def book_event(book: schemas.Booking, db: Session =Depends(database.get_db), 
                    current_user: str = Depends(oauth2.get_current_user)):

    # Query db for the event with ID provided
    event = db.query(models.Event).filter(models.Event.id == book.event_id).first()

    # Report status code 404 if event id isn't found
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event id of {book.event_id} does not exist")

    # Query booking to get event and current user. Booked requests
    bookings_query = db.query(models.Booking).filter(
        models.Booking.event_id == book.event_id, 
        models.Booking.user_id == current_user.id)

    # Get first booking query found
    found_booking = bookings_query.first()
    # book.dir is an option of [0,1] ,[0 to delete, 1 to add }
    if (book.dir == 1):
        # Cross-check if user has already booked
        if found_booking:
            # Report status code 409 if already booked
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=f"{current_user.email} has already booked on {book.event_id} this event")
        # Book request on event id with current user id 
        new_book = models.Booking(event_id = book.event_id, user_id = current_user.id, space = book.space)
        db.add(new_book)
        db.commit()
        
        return {"message": "Successfully added to your bookings"}

    else:
        # Report status code 404 if booking not found # Prog_BIO
        if not found_booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking not found")

        # book.dir = 0, delete booking 
        bookings_query.delete(synchronize_session=False)
        db.commit()

        return{"message": "Successfully deleted booking"}

@router.get("/{id}", response_model= schemas.BookingResponse)
def get_booking(id: int, db: Session = Depends(get_db), 
                    limit: int = 10, skip: int = 0, search: Optional[str]="", 
                        current_user: str = Depends(oauth2.get_current_user)):

    # Query booking db with id provided
    booking = db.query(models.Booking).filter(models.Booking.id == id).first()

    # Report status code 404 if booking not found
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"Booking with id: {id} was not found")

    # Return booking
    retu