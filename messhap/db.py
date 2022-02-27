from .models import User, UserInDb

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


class UserNotInDatabaseException(Exception):
    message = "User Not In Database"


def get_user_from_db(uname: str):
    if uname not in fake_users_db.keys():
        raise UserNotInDatabaseException
    else:
        return fake_users_db[uname]


def is_user_exists(username: str):
    return username in fake_users_db.keys()


def sign_user_in_db(newuser: UserInDb):
    fake_users_db.update({newuser.username: newuser.dict()})


def get_user_except_caller(caller: User):
    caller_username = caller.username
    response = []
    for username, profile in fake_users_db.items():
        if username != caller_username:
            response.append(User(**profile))
    return response
