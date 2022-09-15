import pytest
from app import schemas
from app.core.config import settings
from tests.test_config import client, session, test_user

from jose import jwt


def test_새로운_유저_생성(client):
    res = client.post("/users/", json={"email": "test@example.com", "password": "test"})
    new_user = schemas.UserResponse(**res.json())

    assert res.status_code == 201
    assert new_user.email == "test@example.com"


def test_이미_존재하는_유저_생성(client, test_user):
    user_data = {"email": "test@demo.com", "password": "test"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 400
    assert res.json()["detail"] == "User already exists."


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

    assert res.status_code == 200


def test_존재하지_않는_유저_삭제(client):
    not_exist_id = 999
    res = client.delete(f"/users/{not_exist_id}")

    assert res.status_code == 404


def test_유저_로그인_성공(client, test_user):
    user_data = {"username": test_user["email"], "password": test_user["password"]}
    res = client.post("/login", data=user_data)
    login_res = schemas.Token(**res.json())

    payload = jwt.decode(login_res.access_token, settings.secret_key, settings.algorithm)
    id = payload.get("user_id")

    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize(
    "email, password, status",
    [
        ("wrong@email.com", "test", 403),
        ("test@demo.com", "wrong-password", 403),
        (None, "test", 422),
        ("test@demo.com", None, 422),
    ],
)
def test_유저_로그인_실패(client, test_user, email, password, status):
    wrong_user_data = {"username": email, "password": password}
    res = client.post("/login", data=wrong_user_data)
    assert res.status_code == status
