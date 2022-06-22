from fastapi import APIRouter, Response, status, HTTPException,UploadFile
from fastapi import Depends, File
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import cloudinary
import cloudinary.uploader
from ..database import get_db

router = APIRouter(
    prefix="/events",
    
    tags=["Events"]
)

@router.get("/", response_model= List[schemas.EventOut]) 
def get_my_events(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user),
limit: int = 10, skip: int = 0, search: Optional[str]=""):

    print(current_user)
    # events = db.query(models.Event).filter(models.Event.owner_id == current_user.id).all()

    events = db.query(models.Event, func.count(models.Booking.event_id).label("Booking")).join( 
        models.Booking, models.Booking.event_id == models.Event.id, isouter=True).group_by(
        models.Event.id).filter(models.Event.title.contains(search), models.Event.owner_id == current_user.id).limit(limit).offset(skip).all()

    return events

@router.get("/all", response_model= List[schemas.EventOut])
def get_all_events(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str]=""):
    
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
    
    try:
        event_image = cloudinary.uploader.upload(file.file)
        url = event_image.get("url")
        event.image_url = url
    except Exception as e:
        template = f"""
                    <html>
                        <body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
                            <img src="/app/routers/templates/static/profile_male.jpg">
                        </body>
                    </html>
                    """

        file = template
        
    # print(current_user)
    new_event = models.Event(owner_id = current_user.id, **event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event

@router.get("/{id}", response_model= schemas.EventOut)
def get_an_event(id: int, db: Session = Depends(get_db), 
limit: int = 10, skip: int = 0, search: Optional[str]=""):

    # event = db.query(models.Event).filter(models.Event.id == id).first()

    event = db.query(models.Event, func.count(models.Booking.event_id).label("Booking")).join( 
        models.Booking, models.Booking.event_id == models.Event.id, isouter=True).group_by(
        models.Event.id).filter(models.Event.title.contains(search), models.Event.id == id).limit(limit).offset(skip).first()


    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"Event with id: {id} was not found")

    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
    #     detail="Not authorized to perform requested action")

    return event

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    
    print(current_user)
    deleted_event_query = db.query(models.Event).filter(models.Event.id == id)
    
    deleted = deleted_event_query.first()

    if deleted == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail = f"Event with id: {id} was not found")

    if deleted.owner_id != current_user.id or current_user.admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
        detail="Not authorized to perform requested action")

    deleted_event_query.delete(synchronize_session=False)
    db.commit()
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)
   

@router.put("/{id}", response_model= schemas.EventResponse)
def update_event(id: int, file: UploadFile = File(None), 
event: schemas.EventUpdate = Depends(schemas.EventUpdate.as_form),
db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):

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
                    detail = f"Event with id: {id} was not found")

    if updated_event.owner_id != current_user.id or current_user.admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
        detail="Not authorized to perform requested action")

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

    event_query.update(event.dict(), synchronize_session=False)

    db.commit()

    return event_query.first()