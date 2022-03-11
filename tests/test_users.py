import pytest
from fastapi import Response, status
from fastapi.testclient import TestClient
from messhap.main import app as app

client = TestClient(app)


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


class TestGetMe:
    @pytest.mark.usefixtures("client")
    def test_get_without_token(self, client):
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.usefixtures("client", "get_token_header")
    def test_get_with_token(self, get_token_header):
        response = client.get("/users/me", headers=get_token_header)
        assert response.status_code == status.HTTP_200_OK


class TestPatchMe:

    good_patch = {
        "email": "hi@example.com",
        "full_name": "J. Doe",
        "disabled": True,
    }
    bad_patch = {
        "email": "whatews",
        "full_name": "notbad",
        "old_password": "secre",
        "password1": "123456",
        "disabled": False,
    }

    @pytest.mark.usefixtures("client")
    def test_patch_without_token(self, client):
        response = client.patch("/users/me", json=self.good_patch)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    @pytest.mark.usefixtures("client", "get_token_header")
    def test_patch_with_token(self, client, get_token_header):
        response = client.patch(
            "/users/me", headers=get_token_header, json=self.good_patch
            )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "username": "johndoe",
            "email": "hi@example.com",
            "disabled": True,
            "full_name": "J. Doe",
        }

    @pytest.mark.usefixtures("client", "get_token_header")
    def test_patch_with_bad_json(self, client, get_token_header):
        response = client.patch(
            "/users/me", headers=get_token_header, json=self.bad_patch
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "__root__"],
                    "msg": "If you want to change password, all three fields are required",  # noqa
                    "type": "value_error",
                }
            ]
        }


class TestPost:
    bad_guy = {
        "username": "badguy123",
        "email": "who_cares",
        "password2": "dont_make_me_say_it_twice",
    }

    good_guy = {
        "username": "duh",
        "password1": "123456",
        "password2": "123456",
        "email": "whatever@cartmail.com",
        "full_name": "Denis U. Heartman",
    }

    @pytest.mark.usefixtures("client")
    def test_bad_credentials(self, client):
        response = client.post("/users", json=self.bad_guy)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address",
                    "type": "value_error.email",
                },
                {
                    "loc": ["body", "password1"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ]
        }

    @pytest.mark.usefixtures("client")
    def test_good_credentials(self, client):
        response = client.post("/users", json=self.good_guy)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "username": "duh",
            "disabled": False,
            "email": "whatever@cartmail.com",
            "full_name": "Denis U. Heartman",
        }
