from fastapi import status
import pytest


class TestGet:
    @pytest.mark.usefixtures("client")
    def test_without_token(self, client):

        response = client.get("/friends")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.usefixtures("client", "get_token_header")
    def test_with_token(self, get_token_header, client):
        response = client.get("/friends", headers=get_token_header)
        # Empty dict since there is no firends yet
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    @pytest.mark.usefixtures(
        "client", "get_token_header", "johndoe_requested", "third_one_blocked"
    )
    def test_blocker_not_in_list(self, client, get_token_header):
        response = client.get("/friends", headers=get_token_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "username": "erdurano",
                "full_name": "Oğuzcan Erduran",
                "email": "erdurano@gmail.com",
                "disabled": False,
                "status": "requested",
            },
        ]

    @pytest.mark.usefixtures("client", "get_token_header", "user_blocked")
    def test_blocked_in_list(self, client, get_token_header):
        response = client.get("/friends", headers=get_token_header)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "username": "erdurano",
                "full_name": "Oğuzcan Erduran",
                "email": "erdurano@gmail.com",
                "disabled": False,
                "status": "requested",
            },
            {
                "username": "sum_one",
                "email": "sum.one@sumthing.com",
                "full_name": None,
                "disabled": False,
                "status": "blocked",
            },
        ]


class TestGetUname:
    @pytest.mark.usefixtures("client")
    def test_without_token(self, client):
        response = client.get("/friends/erdurano")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.usefixtures("client", "get_token_header")
    def test_with_token(self, client, get_token_header):
        response = client.get("/friends/abs", headers=get_token_header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.usefixtures("client", "get_token_header", "johndoe_requested")
    def test_requested(self, client, get_token_header):
        response = client.get("/friends/erdurano", headers=get_token_header)
        assert response.status_code == status.HTTP_200_OK


class TestPostUname:
    @pytest.mark.usefixtures("client")
    def test_without_token(self, client):
        response = client.post("/friends/erdurano")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.usefixtures("client", "get_token_header", "friends_db")
    def test_with_token(self, client, get_token_header):
        response = client.post("/friends/erdurano", headers=get_token_header)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures("client", "get_token_header", "friends_db")
    def test_with_multiple_request(self, client, get_token_header):
        response1 = client.post("/friends/erdurano", headers=get_token_header)
        assert response1.status_code == status.HTTP_201_CREATED
        response2 = client.post("/friends/erdurano", headers=get_token_header)
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert response2.json() == {"detail": "You already interacted with this user"}


class TestUpdate:
    @pytest.mark.usefixtures("client", "johndoe_requested")
    def test_without_token(self, client):
        response = client.patch("/friends/erdurano", json={"status": "friend"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.usefixtures(
        "client", "get_token_header", "get_2nd_token_header", "johndoe_requested"
    )
    def test_with_token(self, client, get_token_header, get_2nd_token_header):
        friendship = {
            "requester": "johndoe",
            "requestee": "erdurano",
            "status": "friend"
        }
        response = client.patch(
            "/friends/erdurano", headers=get_token_header, json=friendship
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": "You can not accept user as friend since you requested"
        }
        response_to_other = client.patch(
            "/friends/johndoe", headers=get_2nd_token_header, json=friendship
        )
        assert response_to_other.status_code == status.HTTP_200_OK
