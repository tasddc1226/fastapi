import pytest
from app import schemas
from tests.test_config import client, session


def test_새로운_유저_생성(client):
    res = client.post("/users/", json={"email": "test@example.com", "password": "test"})
    new_user = schemas.UserResponse(**res.json())

    assert res.status_code == 201
    assert new_user.email == "test@example.com"
