import pytest
from app import schemas
from tests.test_config import client, session, test_user


def test_새로운_유저_생성(client):
    res = client.post("/users/", json={"email": "test@example.com", "password": "test"})
    new_user = schemas.UserResponse(**res.json())

    assert res.status_code == 201
    assert new_user.email == "test@example.com"


def test_이미_존재하는_유저_생성(client, test_user):
    user_data = {"email": "test@demo.com", "password": "test"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 400
    assert res.json()["detail"] == "Duplicate email"


def test_존재하는_유저_조회(client, test_user):
    id = test_user["id"]
    res = client.get(f"/users/{id}")

    assert res.status_code == 200
    assert res.json()["email"] == test_user["email"]


def test_존재하지_않는_유저_조회(client):
    id = 999
    res = client.get(f"/users/{id}")

    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"


def test_존재하는_유저_삭제(client, test_user):
    id = test_user["id"]
    res = client.delete(f"/users/{id}")

    assert res.status_code == 204


def test_존재하지_않는_유저_삭제(client):
    not_exist_id = 999
    res = client.delete(f"/users/{not_exist_id}")

    assert res.status_code == 404
