from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.oauth2 import create_access_token
from app.config import settings 
from app.database import get_db 
from app.database import Base
from app import models
from alembic import command



SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Ifeanyi058@localhost/UU81_test"
# SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Testing_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


# Dependency
def override_get_db():
    db = Testing_SessionLocal()
    try:
        yield db
    finally: 
        db.close()


@pytest.fixture()
def session():
    print("My session fixture ran")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = Testing_SessionLocal()
    try:
        yield db
    finally: 
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():

        try:
            yield session
        finally: 
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "hello123@gmail.com", 
                "password": "password123",
                "phone_number": "5542",
                "admin": "True",
                }
    res = client.post("/users/test_only", json=user_data)

    assert res.status_code == 201
    print(res.json())
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def token(test_user):
    access_token = create_access_token({"user_id": test_user['id'], "admin": test_user['admin']})
    return access_token

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization" : f"Bearer {token}"
    }
    return client


@pytest.fixture
def test_user_2(client):
    user_data = {"email": "zeus@gmail.com", 
                    "password": "password123",
                    "phone_number": "5542"
                    }
    res = client.post("/users/test_only", json=user_data)

    assert res.status_code == 201
    print(res.json())
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def token_2(test_user_2):
    access_token = create_access_token({"user_id": test_user_2['id'], "admin": test_user_2['admin']})
    return access_token

@pytest.fixture
def authorized_client_2(client, token_2):
    client.headers = {
        **client.headers,
        "Authorization" : f"Bearer {token_2}"
    }
    return client


@pytest.fixture
def test_events(test_user, session, test_user_2):
    events_data = [{
        "title": "Checking out an event",
        "content": "Lets see how it goes",
        "image_url": "http://res.cloudinary.com/prog-bio/image/upload/v1655657195/h6ovwbxsrcujbclg8w1v.jpg",
        "space_allowed": 50,
        "space_available": 20,
        "cost": 2000,
        "owner_id": test_user['id']
    },{
        "title": "Checking out the 2nd Event",
        "content": "See how it goes",
        # "image_url": "http://res.cloudinary.com/prog-bio/image/upload/v1655657195/h6ovwbxsrcujbclg8w1v.jpg",
        "space_allowed": 50,
        "space_available": 20,
        "cost": 2000,
        "owner_id": test_user['id']
    }, {
        "title": "Checking out the 3rd Event",
        "content": "How it goes",
        # "image_url": "http://res.cloudinary.com/prog-bio/image/upload/v1655657195/h6ovwbxsrcujbclg8w1v.jpg",
        "space_allowed": 50,
        "space_available": 20,
        "cost": 2000,
        "owner_id": test_user['id']
    },{
        "title": "Checking out the 4th Event",
        "content": "How it goes",
        # "image_url": "http://res.cloudinary.com/prog-bio/image/upload/v1655657195/h6ovwbxsrcujbclg8w1v.jpg",
        "space_allowed": 50,
        "space_available": 20,
        "cost": 2000,
        "owner_id": test_user_2['id']
    }]

    def create_events_model(event):
        return models.Event(**event)

    event_map = map(create_events_model, events_data)
    events = list(event_map)


    session.add_all(events)
    session.commit()

    events = session.query(models.Event).all()
    return events

@pytest.fixture
def test_bookings(session, test_events, test_user, test_user_2):
    booking_data = [{
        "event": test_events[0],
        "event_id": test_events[0].id,
        "user_id": test_user['id'],
        "user": [test_user, test_user_2],
        # "dir": 1,
        "space": 1
    },{
        "event": test_events[1],
        "event_id": test_events[1].id,
        "user_id": test_user['id'],
        "user": [test_user, test_user_2],
        # "dir": 1,
        "space": 1
    }, {
        "event": test_events[2],
        "event_id": test_events[2].id,
        "user_id": test_user['id'],
        "user": [test_user, test_user_2],
        # "dir": 1,
        "space": 1
    }, {
        "event": test_events[2],
        "event_id": test_events[2].id,
        "user_id": test_user_2['id'],
        "user": [test_user, test_user_2],
        # "dir": 1,
        "space": 1
    }, {
        "event": test_events[3],
        "event_id": test_events[3].id,
        "user_id": test_user_2['id'],
        "user": [test_user, test_user_2],
        # "dir": 1,
        "space": 1
    },{
        "event": test_events[3],
        "event_id": test_events[3].id,
        "user_id": test_user['id'],
        "user": [test_user, test_user_2],
        # "dir": 1,
        "space": 1
    }]
    

    def create_booking_model(booking):
        return models.Booking(**booking)

    booking_map = map(create_booking_model, booking_data)
    bookings = list(booking_map)


    session.add_all(bookings)
    session.commit()

    bookings = session.query(models.Booking).all()
    return bookings


