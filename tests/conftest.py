import pytest
from messhap import app
from fastapi.testclient import TestClient
from fastapi import Response
from messhap.db import fake_friends_db, fake_users_db
from messhap.models import FriendshipStatus, UserInDb
from messhap.router.auth import get_password_hash


@pytest.fixture(scope="function")
def user_db():
    fake_users_db.clear()
    fake_users_db.update(
        {
            "johndoe": {
                "username": "johndoe",
                "full_name": "John Doe",
                "email": "johndoe@example.com",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # noqa: E501
                "disabled": False,
                },
            "erdurano": {
                "username": "erdurano",
                "full_name": "Oğuzcan Erduran",
                "email": "erdurano@gmail.com",
                "hashed_password": "$2b$12$FMvogo12rGjaCrvPI17vs.WZdOIl/3xQEVb/gRpOoJ4vjsH2Znbe.",  # noqa: E501
                "disabled": False,
            },
        }
    )
    return fake_users_db


@pytest.fixture(scope="function")
def friends_db():
    fake_friends_db.clear()
    return fake_friends_db


@pytest.fixture(scope="function")
def client() -> TestClient:
    client = TestClient(app)
    return client


@pytest.fixture(scope="function")
def sum_one_is_in(user_db):
    if "sum_one" not in user_db.keys():
        user_db.update(
            sum_one=UserInDb(
                username="sum_one",
                email="sum.one@sumthing.com",
                full_name=None,
                disabled=False,
                hashed_password=get_password_hash("123456")
            ).dict()
        )
    return user_db


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def johndoe_requested(friends_db):
    friends_db.append(
        {
            'requester': "johndoe",
            "requestee": "erdurano",
            "status": FriendshipStatus.REQUESTED,
            "blocker": None,
        }
    )
    return friends_db


@pytest.fixture(scope="function")
def third_one_blocked(johndoe_requested, sum_one_is_in):
    johndoe_requested.extend(
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
def user_blocked(johndoe_requested, sum_one_is_in):
    if not any(
        [
            item["requester"] == "johndoe" and
            item["requestee"] == "sum_one"
            for item in johndoe_requested
        ]
    ):
        johndoe_requested.extend(
            [
                {
                    'requester': "johndoe",
                    "requestee": "sum_one",
                    "status": FriendshipStatus.BLOCKED,
                    "blocker": "johndoe",
                }

            ]
        )
