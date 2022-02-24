from fastapi.testclient import TestClient
from messhap import app

client = TestClient(app)

def test_login():
    response = client.post("/login/", json={"username": "erdurano", "password": "1234"})
    assert response.status_code == 200
    assert response.json() == {"username": "erdurano", "interests": []}

    response2 = client.post(
        "/login/",
        json={
            "username": "erdurano",
            "password": "1234",
            "interests": ["baseball",]
            }
        )
    assert response2.status_code == 200
    assert response2.json() == {"username": "erdurano", "interests": ["baseball"]}
    