from asyncio import new_event_loop
import pytest
from app import models, schemas

@pytest.fixture()
def test_booking(test_events, session, test_user):
    new_booking = models.Booking(event_id = test_events[3].id, user_id = test_user["id"], space = 1)
    session.add(new_booking)
    session.commit()

def test_booking_on_events(authorized_client, test_events):
    res = authorized_client.post(
        "/bookings/", json={"event_id": test_events[3].id, "dir": 1})

    assert res.status_code == 201

def test_booking_twice_events(authorized_client, test_events, test_booking):
    res = authorized_client.post(
        "/bookings/", json={"event_id": test_events[3].id, "dir": 1})

    assert res.status_code == 409

def test_delete_booking(authorized_client, test_events, test_booking):
    res = authorized_client.post(
        "/bookings/", json={"event_id": test_events[3].id, "dir": 0})
    assert res.status_code == 201

def test_delete_booking_non_exist(authorized_client, test_events):
    res = authorized_client.post(
        "/bookings/", json={"event_id": test_events[3].id, "dir": 0})
    assert res.status_code == 404

def test_booking_non_exist(client, test_events):
    res = client.post(
        "/bookings/", json={"event_id": test_events[3].id, "dir": 1})
    assert res.status_code == 401

def test_get_booking(authorized_client, test_events, test_user):
    res = authorized_client.post(
        "/bookings/events", json={"event_id": test_events[1].id})
    assert res.status_code == 200

# def test_get_one_booking(authorized_client, test_bookings):
#     res = authorized_client.get(f"/bookings/{test_bookings[1].id}")
    
#     # booking = schemas.BookingResponse(**res.json())
#     # assert booking.id ==test_bookings[0].id
#     # assert booking.event.title == test_bookings[0].event_title
#     # assert booking.user.id == test_bookings[0].user_id

#     assert res.status_code == 200

# def test_get_one_event(client, test_events):
#     res = client.get(f"/events/{test_events[0].id}")
#     print(res.json())
#     event = schemas.EventOut(**res.json())
#     assert event.Event.id ==test_events[0].id
#     assert event.Event.title ==test_events[0].title

#     assert res.status_code == 200

# def test_get_user_bookings(authorized_client, test_bookings, test_events, test_user, test_user_2):
#     res = authorized_client.get("/bookings/user")

#     # def validate(bookings):
#     #     return schemas.Booking(**bookings)
#     # booking_map = map(validate, res.json())
#     # assert len(res.json()) == len(test_bookings.user_id)
#     assert res.status_code == 200

# def test_get_event_bookings(authorized_client, test_bookings, test_events, test_user, test_user_2):
#     res = authorized_client.post(
#         "/bookings/event",json={"event_id": 2,})

    # def validate(bookings):
    #     return schemas.BookingGetEvents(**bookings)
    # booking_map = map(validate, res.json())
    # assert len(res.json()) == len(test_bookings.event_id[2])
    # assert res.status_code == 200
