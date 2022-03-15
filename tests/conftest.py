import pytest
from messhap import app
from fastapi.testclient import TestClient
from fastapi import Response
from messhap.db import fake_friends_db
from messhap.models import FriendshipStatus


@pytest.fixture(scope="module")
def client() -> TestClient:
    client = TestClient(app)
    return client


@pytest.fixture
def get_token_header():
    client = TestClient(app)
    credentials = {"username": "johndoe", "password": "secret"}
    response: Response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=credentials,
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def get_2nd_token_header():
    client = TestClient(app)
    credentials = {"username": "erdurano", "password": "123456"}
    response: Response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=credentials,
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def johndoe_requested():
    fake_friends_db.append(
        {
            'requester': "johndoe",
            "requestee": "erdurano",
            "status": FriendshipStatus.REQUESTED,
            "blocker": None,
        }
    )
