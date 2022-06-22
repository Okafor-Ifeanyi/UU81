from distutils.command.upload import upload
import profile
from fastapi import APIRouter, Response, status, HTTPException, Depends, UploadFile, File
from .. import models, schemas, utils, oauth2
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from ..database import get_db


router = APIRouter(
    prefix= "/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(file: UploadFile = File(None), user: schemas.UserCreate = Depends(schemas.UserCreate.as_form), db: Session = Depends(get_db)):

    # Hash the password - user.password    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    
    try:
        user_image = cloudinary.uploader.upload(file.file)
        url = user_image.get("url")
        user.image_url = url
    except Exception as e:
        pass

    # email = db.query(models.User).filter(models.User.email == user.email)

    # found_email = email.first()

    # if found_email:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #                 detail = f"{user.email} has already been registered")

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user 


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"User with id: {id} was not found")
    
    return user 


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id:int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    deleted_user_query = db.query(models.User).filter(models.User.id == id)

    deleted = deleted_user_query.first()
    if deleted == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"User with id: {id} was not found")
    if current_user.admin == False or id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = f"User with id: {id} is not the Owner or Admin")
    deleted_user_query.delete(synchronize_session=False)
    db.commit()             
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.UserOut)
def update_user(id:int, file: UploadFile = File(None), 
user: schemas.UserUpdate = Depends(schemas.UserUpdate.as_form), 
db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    user_query = db.query(models.User).filter(models.User.id == id)
    updated_user = user_query.first()

    if updated_user == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"User with id: {id} was not found")

    if current_user.admin != True or id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = f"User email {current_user.email}: is not an Admin or the Owner of this Account")

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
    
    user_query.update(user.dict(), synchronize_session=False)
    db.commit()
    return user_query.first()


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
