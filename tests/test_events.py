from typing import List
from app import schemas
import pytest



def test_get_all_events(authorized_client, test_events):
    res = authorized_client.get("/events/all")
    print(res.json())

    def validate(events):
        return schemas.EventOut(**events)
    event_map = map(validate, res.json())
    assert len(res.json()) == len(test_events)
    assert res.status_code == 200


def test_get_events(authorized_client, test_events, test_user):
    res = authorized_client.get("/events")
    # print(res.json())

    def validate(events):
        return schemas.EventOut(**events)
    event_map = map(validate, res.json())
    # user = print(f"{test_events[0].owner_id}, {test_events[1].owner_id}, {test_events[2].owner_id},")
    # assert len(res.json()) == len(test_events[test_user.id])
    assert res.status_code == 200


def test_unauthorized_get_all_events(client, test_events):
    res = client.get("/events/")
    assert res.status_code == 401


def test_unauthorized_get_one_event(client, test_events):
    res = client.get(f"/events/{test_events[0].id}")
    assert res.status_code == 200
                          

def test_get_unavailable_event(authorized_client, test_events):
    res = authorized_client.get("/events/8888")
    assert res.status_code == 404


def test_get_one_event(client, test_events):
    res = client.get(f"/events/{test_events[0].id}")
    print(res.json())
    event = schemas.EventOut(**res.json())
    assert event.Event.id ==test_events[0].id
    assert event.Event.title ==test_events[0].title

    assert res.status_code == 200

@pytest.mark.parametrize("title, content, status, image_url", [ 
    ("Dope title", "awesome new content", True, "http://res.cloudinary.com/prog-bio/image/upload/v1655657195/h6ovwbxsrcujbclg8w1v.jpg"),
    ("Favorite Pizza", "I love pepporoni", False, "http://res.cloudinary.com/prog-bio/image/upload/v1655657195/h6ovwbxsrcujbclg8w1v.jpg"),
    ("tallest skyscrapper", "I just want the money", True, "http://res.cloudinary.com/prog-bio/image/upload/v1655657195/h6ovwbxsrcujbclg8w1v.jpg")
])


def test_create_event(authorized_client, test_user, test_events, title, content, status):
    res = authorized_client.post("/events/", 
            json={"title": title, "content": content, "status": status})
    
    created_event = schemas.EventResponse(**res.json())
    assert res.status_code == 201
    assert created_event.title ==  title
    assert created_event.content ==  content
    assert created_event.status ==  status
    assert created_event.owner_id ==  test_user['id']

def test_create_events_default_published_true(authorized_client, test_user, test_events):
    res = authorized_client.post(
        "/events/", json={"title": "arbitrary title", 
                            "content": "aasdfjasdf"})
    
    created_event = schemas.EventResponse(**res.json())
    assert res.status_code == 201
    assert created_event.title == "arbitrary title"
    assert created_event.content ==  "aasdfjasdf"
    assert created_event.status == True
    assert created_event.owner_id ==  test_user['id']

def test_unauthorized_user_create_event(client, test_user, test_events):
    res = client.post(
        "/events/", json={"title": "arbitrary title", "content": "aasdfjasdf"})
    assert res.status_code == 401  

def test_unauthorized_user_delete_eventt(client, test_user, test_events):
    res = client.delete(
        f"/events/{test_events[0].id}")
    assert res.status_code == 401

def test_delete_event(authorized_client, test_user, test_events):
    res = authorized_client.delete(
        f"/events/{test_events[0].id}")
    assert res.status_code == 204

def test_delete_event_non_exist(authorized_client, test_user, test_events):
    res = authorized_client.delete(
        "/events/80000")
    assert res.status_code == 404

def test_delete_other_users_events(authorized_client_2, test_user_2, test_events):
   res = authorized_client_2.delete(f"/events/{test_events[0].id}")
   assert res.status_code == 403

def test_update_event(authorized_client, test_user, test_events):
    data = {
        "title": "Updated Title",
        "content": "Upload Content",
        "id": test_events[0].id
    }
    res = authorized_client.put(f"/events/{test_events[0].id}", json=data)
    updated_events = schemas.EventResponse(**res.json())
    assert res.status_code == 200
    assert updated_events.title == data["title"]
    assert updated_events.content == data["content"]

def test_update_other_user_event(authorized_client, test_user, test_events, test_user_2):
    data = {
        "title": "Updated Title",
        "content": "Upload Content",
        "id": test_events[3].id
    }
    res = authorized_client.put(f"/events/{test_events[3].id}", json=data)
    assert res.status_code == 403

def test_unauthorized_user_update_event(client, test_user, test_events):
    res = client.put(
        f"/events/{test_events[0].id}")
    assert res.status_code == 401

def test_update_event_non_exist(authorized_client, test_user, test_events):
    data = {
        "title": "Updated Title",
        "content": "Upload Content",
        "id": test_events[3].id
    }
    
    res = authorized_client.put(
        "/events/80000", json=data)

    assert res.status_code == 404