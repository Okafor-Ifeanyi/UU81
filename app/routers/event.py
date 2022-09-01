from fastapi import APIRouter, Response, status, HTTPException,UploadFile
from fastapi import Depends, File
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import cloudinary
import cloudinary.uploader
from ..database import get_db

# Router name and tag
router = APIRouter(
    prefix="/events",
    
    tags=["Events"]
)

@router.get("/", response_model= List[schemas.EventOut]) 
def get_my_events(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user),
limit: int = 10, skip: int = 0, search: Optional[str]=""):

    print(current_user)
    # events = db.query(models.Event).filter(models.Event.owner_id == current_user.id).all()

    # Get all Event created by current user, including options to make search more efficient
    events = db.query(models.Event, func.count(models.Booking.event_id).label("Booking")).join( 
        models.Booking, models.Booking.event_id == models.Event.id, isouter=True).group_by(
        models.Event.id).filter(models.Event.title.contains(search), models.Event.owner_id == current_user.id).limit(limit).offset(skip).all()

    return events

@router.get("/all", response_model= List[schemas.EventOut])
def get_all_events(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str]=""):
    
    # Get all Event, including options to make search more efficient
    events = db.query(models.Event, func.count(models.Booking.event_id).label("Booking")).join( 
        models.Booking, models.Booking.event_id == models.Event.id, isouter=True).group_by(
        models.Event.id).filter(models.Event.title.contains(search)).limit(limit).offset(skip).all()

    # if current_user.admin == True:
    #     return events
    # else:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                 detail = f"User with email: {current_user.email} is not an Admin")
    
    return events


@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.EventResponse)
def create_event(file: UploadFile = File(...), event: schemas.EventCreate = Depends(schemas.EventCreate.as_form),
 db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    
    # Upload file to Cloudinary and save link to "Image_url Model"
    try:
        event_image = cloudinary.uploader.upload(file.file)
        url = event_image.get("url")
        event.image_url = url
    except Exception as e:
        pass
        
    # Create new event with data provided on the form
    new_event = models.Event(owner_id = current_user.id, **event.dict()) 
    db.add(new_event) 
    db.commit() 
    db.refresh(new_event) 

    # Return created event shown in schema format
    return new_event

@router.get("/{id}", response_model= schemas.EventOut)
def get_an_event(id: int, db: Session = Depends(get_db), 
limit: int = 10, skip: int = 0, search: Optional[str]=""):

    # Get Event with id provided, including options to make search more efficient
    event = db.query(models.Event, func.count(models.Booking.event_id).label("Booking")).join( 
        models.Booking, models.Booking.event_id == models.Event.id, isouter=True).group_by(
        models.Event.id).filter(models.Event.title.contains(search), models.Event.id == id).limit(limit).offset(skip).first()

    # Report 404 if event isn't found
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"Event with id: {id} was not found")

    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
    #     detail="Not authorized to perform requested action")

    # Get Event found with ID provided
    return event

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    
    # Get event with id Provided
    deleted_event_query = db.query(models.Event).filter(models.Event.id == id)
    deleted = deleted_event_query.first()

    # Report 404 is event not found
    if deleted == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail = f"Event with id: {id} was not found")

    if deleted.owner_id == current_user.id or current_user.admin == True:
    # Delete Event 
        deleted_event_query.delete(synchronize_session=False)
        db.commit()
            
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    # Report 403 if user is not the Owner or an Admin, 1 of any is enough to pass this statement
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
        detail="Not authorized to perform requested action")
   

@router.put("/{id}", response_model= schemas.EventResponse)
def update_event(id: int, file: UploadFile = File(None), 
event: schemas.EventUpdate = Depends(schemas.EventUpdate.as_form),
db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    
    # Getting the Event with the id provided
    event_query = db.query(models.Event).filter(models.Event.id == id)
    updated_event = event_query.first()

    # Check if the event exists
    if updated_event == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"Event with id: {id} was not found")

    
    # If file is available upload to cloudinary then save the link into the "image model"
    if file:
        try:
            event_image = cloudinary.uploader.upload(file.file)
            url = event_image.get("url")
            event.image_url = url
        except Exception as e:
            pass
    else:
        event.image_url = None
        pass

    # Use old data if new data isn't provided
    if event.title:
        pass
    else: 
        event.title = updated_event.title
        
    if event.content:
        pass
    else:
        event.content = updated_event.content

    if event.image_url:
        pass
    else:
        event.image_url = updated_event.image_url

    if updated_event.owner_id == current_user.id or current_user.admin == True:
        # Update Event
        event_query.update(event.dict(), synchronize_session=False)
        db.commit()
        return event_query.first()
    # Report 403 if user is not the Owner or an Admin, 1 of any is enough to pass this statement
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
        detail="Not authorized to perform requested action")

@router.post("/test", status_code=status.HTTP_201_CREATED, response_model= schemas.EventResponse)
def create_posts(event: schemas.EventTest, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts(title, content, published) 
    #                 VALUES(%s, %s, %s) RETURNING * """,
    #                 (post.title, post.content, post.published))
    # new_post = cursor.fetchone() 

    # conn.commit()
    print(current_user.id)
    # print(current_user.email)
    new_event = models.Event(owner_id=current_user.id, **event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event

@router.put("/test/{id}", response_model= schemas.EventResponse)
def update_post(id: int, event: schemas.EventTest , db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute( 
    #     """UPDATE posts SET title = %s, content = %s, published = %s WHERE ID = %s RETURNING *""",
    #     (post.title, post.content, post.published, str),)
    # updated_post = cursor.fetchone()
    # conn.commit()
    print(current_user)
    event_query = db.query(models.Event).filter(models.Event.id == id)

    updated_event = event_query.first()

    if updated_event == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"Post with id: {id} was not found")

    if updated_event.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
        detail="Not authorized to perform requested action")


    event_query.update(event.dict(), synchronize_session=False)

    db.commit()

    return event_query.first()