import pytest
from messhap import app
from fastapi.testclient import TestClient
from fastapi import Response
from messhap.db import fake_friends_db, fake_users_db
from messhap.models import FriendshipStatus, UserInDb
from messhap.router.auth import get_password_hash


@pytest.fixture()
def client() -> TestClient:
    client = TestClient(app)
    return client


@pytest.fixture()
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


@pytest.fixture()
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


@pytest.fixture()
def johndoe_requested():
    fake_friends_db.append(
        {
            'requester': "johndoe",
            "requestee": "erdurano",
            "status": FriendshipStatus.REQUESTED,
            "blocker": None,
        }
    )
    return fake_friends_db


@pytest.fixture()
def third_one_blocked(johndoe_requested):
    fake_friends_db.extend(
        [
            {
                'requester': "johndoe",
                "requestee": "sum_one",
                "status": FriendshipStatus.BLOCKED,
                "blocker": "sum_one",
            }

        ]
    )


@pytest.fixture(scope="function")
def user_blocked(johndoe_requested):
    fake_friends_db.extend(
        [
            {
                'requester': "johndoe",
                "requestee": "sum_one",
                "status": FriendshipStatus.BLOCKED,
                "blocker": "johndoe",
            }

        ]
    )

    fake_users_db.update(
        sum_one=UserInDb(
            username="sum_one",
            email="sum.one@sumthing.com",
            full_name=None,
            disabled=False,
            hashed_password=get_password_hash("123456")
        ).dict()
    )
