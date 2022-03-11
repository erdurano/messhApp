from fastapi import status
import pytest


class TestGet:

    @pytest.mark.usefixtures("client")
    def test_without_token(client):

        response = client.get("/friends")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.usefixtures("client", "get_token_header")
    def test_with_token(get_token_header, client):
        response = client.get("/friends", headers=get_token_header)
        # Empty dict since there is no firends yet
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestPost:

    @pytest.mark.usefixtures("client")
    def test_without_token(client):
        response = client.post("/friends/erdurano")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.usefixtures("client", "get_token_header")
    def test_with_token(client, get_token_header):
        response = client.post("/friends", headers=get_token_header)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures("client", "get_token_header")
    def test_with_multiple_request(client, get_token_header):
        response1 = client.post("/friends", headers=get_token_header)
        assert response1.status_code == status.HTTP_201_CREATED
        response2 = client.post("/friends", headers=get_token_header)
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert response2.json() == {
            "message": "You can not send friend request to a person"
                       "that you already requested"
        }


class TestUpdate:

    @pytest.mark.usefixtures("client")
    def test_without_token(client):
        response = client.update(
            "/friends/erdurano",
            json={"status": "friend"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.usefixtures("client",
                             "get_token_header",
                             "get_2nd_token_header")
    def test_with_token(client, get_token_header, get_2nd_token_header):
        response = client.update(
            "/friends/erdurano",
            headers=get_token_header,
            json={"status": "friend"}
        )
        assert response.status == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "message": "You can not accept user as friend since you requested"
        }
        response_to_other = client.update(
            "/friends/johndoe",
            headers=get_2nd_token_header,
            json={"status": "friend"}
        )
        assert response_to_other.status == status.HTTP_200_OK
