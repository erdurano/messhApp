import pytest

from fastapi import Response, status
from fastapi.testclient import TestClient
from messhap.main import app


@pytest.mark.usefixtures("user_db", "client")
def test_token():
    client = TestClient(app)
    credentials = {"username": "johndoe", "password": "secret"}
    response: Response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=credentials,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["token_type"] == "bearer"
