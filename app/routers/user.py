from fastapi import APIRouter, Response, status, HTTPException, Depends
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix= "/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate , db: Session = Depends(get_db)):

    # Hash the password - user.password    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user 


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"User with id: {id} was not found")
    
    return user 


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id:int, db: Session = Depends(get_db)):

    deleted_user_query = db.query(models.User).filter(models.User.id == id)

    deleted = deleted_user_query.first()
    if deleted == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"User with id: {id} was not found")
    if models.User.admin == True:
        deleted_user_query.delete(synchronize_session=False)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = f"User with id: {id} is not an Admin")
                    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.UserOut)
def update_user(id:int, user: schemas.UserCreate , db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    updated_user = user_query.first()

    if updated_user == None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail = f"User with id: {id} was not found")

    if models.User.admin == True:
        user_query.update(user.dict(), synchronize_session=False)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail = f"User with id: {id} is not an Admin")

    return user_query.first()
