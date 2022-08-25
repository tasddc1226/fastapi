import pytest
from app import schemas
from app.core.config import settings
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_새로운_유저_생성():
    res = client.post("/users/", json={"email": "test@example.com", "password": "test"})
    new_user = schemas.UserResponse(**res.json())

    assert res.status_code == 201
    assert new_user.email == "test@example.com"
