from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from .auth import get_current_active_user, get_password_hash
from .db import (UserNotInDatabaseException, get_user_except_caller,
                 get_user_from_db, is_user_exists, sign_user_in_db)
from .models import User, UserInDb, UserRegister, UserUpdate

router = APIRouter(prefix="/users", tags=["User management"])


@router.post(
        "/",
        response_model=User,
        status_code=status.HTTP_201_CREATED)
async def sign_up_user(new_user: UserRegister):
    if is_user_exists(new_user.username):
        raise HTTPException(400, detail="User already exists. ")
    hashed_password = get_password_hash(new_user.password)
    new_user_to_db = UserInDb(hashed_password=hashed_password,
                              **new_user.dict())
    sign_user_in_db(new_user_to_db)
    return User(**new_user_to_db.dict())


@router.patch(
    "/",
    response_model=User,
    status_code=status.HTTP_200_OK
)
async def update_user(
        update_model: UserUpdate,
        current_user: User = Depends(get_current_active_user),
        ):
    if (update_model.username and
            update_model.username != current_user.username):
        raise HTTPException(
            status_code=401,
            detail="You can not change details of a user other than yours"
        )
    # TODO: Validation done. Need to code update mechanism


@router.get("/", response_model=List[User])
async def get_user_list(current_user: User = Depends(get_current_active_user)):
    return get_user_except_caller(current_user)


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/{username}", response_model=User)
async def get_user_with_username(
    username: str, current_user: User = Depends(get_current_active_user)
):
    if current_user.username == username:
        return RedirectResponse("/users/me")
    else:
        try:
            requested_user_dict = get_user_from_db(username)
            return User(**requested_user_dict)
        except UserNotInDatabaseException:
            raise HTTPException(
                status_code=404,
                detail=f"User {username} not registered yet.")
