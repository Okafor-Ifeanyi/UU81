from distutils.command.upload import upload
import profile
from fastapi import APIRouter, Response, status, HTTPException, Depends, UploadFile, File
from .. import models, schemas, utils, oauth2
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from ..database import get_db
from typing import Optional, List

router = APIRouter(
    prefix= "/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(file: UploadFile = File(None), user: schemas.UserCreate = Depends(schemas.UserCreate.as_form), db: Session = Depends(get_db)):

    # Hash the password - user.password    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    # Upload file to Cloudinary and save link to "Image_url Model"
    try:
        user_image = cloudinary.uploader.upload(file.file)
        url = user_image.get("url")
        user.image_url = url
    except Exception as e:
        pass

    email = db.query(models.User).filter(models.User.email == user.email)

    found_email = email.first()

    # if found_email:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #                 detail = f"{user.email} has already been registered")

    # Create new user with data provided on the form
    new_user = models.User(**user.dict())
    if user.email == found_email:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail = f"{user.email} has already been registered")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return created user shown in schema format
    return new_user 

@router.get("/all", response_model= List[schemas.UserOut])
def get_user(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
limit: int = 10, skip: int = 0, search: Optional[str]=""):

    # Get all users
    users = db.query(models.User).filter(models.User.email.contains(search)).limit(limit).offset(skip).all()

    if current_user.admin == True:
        return users
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = f"User with email: {current_user.email} is not an admin")
    

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # Get user with ID provided
    user = db.query(models.User).filter(models.User.id == id).first()

    # Report 404 if user Id not found
    if not user:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"User with id: {id} was not found")
    
    # Return user
    return user 


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id:int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Get user with id Provided
    deleted_user_query = db.query(models.User).filter(models.User.id == id)
    deleted = deleted_user_query.first()

    # Report 404 if user not found
    if deleted == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"User with id: {id} was not found")
    
    # Report 403 if user is not the Owner or an Admin, 1 of any is enough to pass this statement
    if current_user.admin == True or current_user.id == id:
        deleted_user_query.delete(synchronize_session=False)
        db.commit()             
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = f"User with email: {current_user.email} is the Owner or an Admin")


@router.put("/{id}", response_model=schemas.UserOut)
def update_user(id:int, file: UploadFile = File(None), 
user: schemas.UserUpdate = Depends(schemas.UserUpdate.as_form), 
db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # Getting the user with the id provided
    user_query = db.query(models.User).filter(models.User.id == id)
    updated_user = user_query.first()

    # Check if the user exists
    if updated_user == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"User with id: {id} was not found")

    # Report 403 if user is not the Owner or an Admin, 1 of any is enough to pass this statement
    
    # If file is available upload to cloudinary then save the link into the "image model"
    if file:
        try:
            user_image = cloudinary.uploader.upload(file.file)
            url = user_image.get("url")
            user.image_url = url
        except Exception as e:
            pass
    else:
        user.image_url = None

        pass
    # Use old data if new data isn't provided

    # Retain old data if nothing new is passed in
    if user.password:
        try:
            hashed_password = utils.hash(user.password)
            user.password = hashed_password
        except:
            pass
    else:
        user.password = current_user.password
    if user.phone_number:
        pass
    else: 
        user.phone_number = current_user.phone_number

    if user.image_url:
        pass
    else:
        user.image_url = current_user.image_url

    if user.first_name:
        pass
    else:
        user.first_name = current_user.first_name

    if user.last_name:
        pass
    else:
        user.last_name = current_user.last_name

# @router.get("/all", response_model= List[schemas.EventOut])
# def get_all_events(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str]=""):


# I tried creating a loop to call the function above automatically
# but it happens that the "user" cant make use of the "name" value i assigned 
# reason being, calling the var = "user" makes use of only the var's in "user"

    # for name, value in user:
    #     print(name)
    #     if user.name:
    #         pass
        
    #     elif user.name == "password":
    #         try:
    #             hashed_password = utils.hash(user.password)
    #             user.password = hashed_password
    #         except:
    #             pass

    #     else:
    #         user.name = current_user.name

    #     print(name)
    
    if current_user.admin == True or id == current_user.id:  
        user_query.update(user.dict(), synchronize_session=False)
        db.commit()
        return user_query.first()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = f"User email {current_user.email}: is not an Admin or the Owner of this Account")



# Test Routers
# This routers where created as plain as possible to support my tests
# but all still have the basic function of the routes within the main project

@router.post("/test_only", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_test_user(user: schemas.UserTest, db: Session = Depends(get_db)):

    # Hash the password - user.password    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user 

@router.put("/test/{id}", response_model=schemas.UserOut)
def update_test_user(id:int, user: schemas.UserCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)
    updated_user = user_query.first()

    if updated_user == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"User with id: {id} was not found")

    if current_user.admin != False or id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = f"User with id: {id} is not the Owner or Admin")
    
    user_query.update(user.dict(), synchronize_session=False)
    db.commit()
    return user_query.first()
