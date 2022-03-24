from typing import List

from .schemas import (Friend, Friendship, FriendshipStatus, User, UserInDb,
                      UserUpdate)

fake_users_db = {
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

fake_friends_db: List[dict] = []


class UserNotInDatabaseException(Exception):
    message = "User Not In Database"


class FriendshipNotInDatabaseException(Exception):
    pass


class FriendNotFoundException(Exception):
    message = "You are not yet interacted with user"


def get_user_from_db(uname: str):
    if uname not in fake_users_db.keys():
        raise UserNotInDatabaseException
    else:
        return fake_users_db[uname]


def is_user_exists(username: str):
    return username in fake_users_db.keys()


def sign_user_in_db(newuser: UserInDb):
    if not is_user_exists(newuser.username):
        fake_users_db.update({newuser.username: newuser.dict()})


def update_user_in_db(current_user: User, update_model: UserUpdate):
    fake_users_db[current_user.username].update(
        update_model.dict(exclude_unset=True)
        )
    return fake_users_db[current_user.username]


def get_user_except_caller(caller: User):
    caller_username = caller.username
    response = []
    for username, profile in fake_users_db.items():
        if username != caller_username:
            response.append(User(**profile))
    return response


def get_friends_list_from_db(caller: User) -> List[Friend]:
    friend_status = []

    for friendship in fake_friends_db:
        if (
            friendship["status"] is not FriendshipStatus.BLOCKED
            or friendship["blocker"] == caller.username
        ):
            status = friendship["status"]
            friend_uname = (
                friendship["requester"]
                if friendship["requester"] != caller.username
                else friendship["requestee"]
            )
            friend_dict = fake_users_db[friend_uname]
            friend = Friend(status=status, **friend_dict)

            friend_status.append(friend)

    return friend_status


def get_friendship(requester: str, requestee: str) -> Friendship:
    for friendship in fake_friends_db:
        if (
            (
                friendship["requester"] == requester
                and friendship["requestee"] == requestee
            ) or (
                friendship["requester"] == requestee
                and friendship["requestee"] == requester
            )
        ):
            return Friendship(**friendship)
    raise FriendshipNotInDatabaseException


def add_friend_request_in_db(requester: str, requestee: str):
    friendship = Friendship(
        requester=requester,
        requestee=requestee,
        status=FriendshipStatus.REQUESTED
    )
    fake_friends_db.append(friendship.dict())


def get_friend_from_db(requester: str, requestee: str) -> Friend:
    try:
        friendship = get_friendship(requester, requestee)
        friend = Friend(
            status=friendship.status,
            **get_user_from_db(requestee)
        )
        return friend
    except FriendshipNotInDatabaseException as e:
        raise FriendNotFoundException from e


def update_friendship_in_db(
        requester: str, requestee: str, status: FriendshipStatus
        ) -> None:
    fship = get_friendship(requester, requestee)
    ind = fake_friends_db.index(fship.dict())
    fship.status = status
    fake_friends_db[ind] = fship.dict()
