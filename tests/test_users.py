import pytest
from fastapi import Response, status
from fastapi.testclient import TestClient
from messhap.main import app as app

client = TestClient(app)


@pytest.fixture
def get_token():
    client = TestClient(app)
    credentials = {"username": "johndoe", "password": "secret"}
    response: Response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=credentials,
    )
    return response.json()["access_token"]


class Test_Me:
    def test_without_token(self):
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    def test_with_token(self, get_token):
        token_header = {"Authorization": f"Bearer {get_token}"}
        response = client.get("/users/me", headers=token_header)
        assert response.status_code == status.HTTP_200_OK
