import pytest
from app import schemas
from jose import jwt
from app.config import settings


def test_root(client):
    res = client.get("/")
    print(res.json().get('message'))
    assert res.json().get('message') == "I have added the new routers as I said today 23rd 10pm!"
    assert res.status_code == 200

def test_create_user(client):
    res = client.post(
        "/users/test_only", json={"email": "hello123@gmail.com", "password": "password123", "phone_number": "99874"})
    print(res.json())
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201

def test_login_user(test_user, client):
    res = client.post(
        "/login", data={"username": test_user['email'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, 
                settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user['id']  
    assert login_res.token_type == "bearer"
    assert res.status_code == 200

def test_incorrect_login(test_user, client):
    res = client.post(
        "/login", data={"username": test_user['email'], "password": 'wrongPassword'})

    assert res.status_code == 403
    assert res.json().get('detail') == "Invalid Credentials"

@pytest.mark.parametrize("email, password, status_code", [ 
    ("bolaji@gmail.com", "password", 403),
    ("zeusifeanyi@gmail.com", 'password222', 403),
    ("hel@gmail.comlo123@gmail.com", 'passweed', 403),
    (None, 'passweed', 422)
])

def test_incorrect_login_email(client, email, password, status_code):
    res = client.post(
        "/login", data={"username": email, "password": password})

    assert res.status_code == status_code
    # assert res.json().get('detail') == "Invalid Credentials"