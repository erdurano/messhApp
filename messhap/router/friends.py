from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from messhap.db import (
    FriendNotFoundException,
    FriendshipNotInDatabaseException,
    add_friend_request_in_db,
    get_friend_from_db,
    get_friends_list_from_db,
    get_friendship,
    update_friendship_in_db,
)
from messhap.schemas import Friend, Friendship, FriendshipStatus, User
from messhap.router.auth import get_current_active_user

router = APIRouter(prefix="/friends", tags=["Friend Management"])


@router.get("", response_model=List[Friend], status_code=status.HTTP_200_OK)
async def get_friend_list(current_user: User = Depends(get_current_active_user)):

    return get_friends_list_from_db(current_user)


@router.get("/{requested_uname}", response_model=Friend, status_code=status.HTTP_200_OK)
async def get_friend(
    requested_uname: str, requester: User = Depends(get_current_active_user)
):
    try:
        return get_friend_from_db(requester.username, requested_uname)
    except FriendNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.post(
    "/{requested_uname}", response_model=Friend, status_code=status.HTTP_201_CREATED
)
async def post_friend_request(
    requested_uname: str, requester: User = Depends(get_current_active_user)
):
    try:
        friendship: Friendship = get_friendship(requester.username, requested_uname)

        if friendship.status != FriendshipStatus.NOT_FRIEND:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already interacted with this user",
            )
        elif (
            friendship.status == FriendshipStatus.BLOCKED
            and friendship.blocker == requested_uname
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are blocked by this user",
            )
    except FriendshipNotInDatabaseException:

        add_friend_request_in_db(requester.username, requested_uname)

        friend = get_friend_from_db(requester.username, requested_uname)
        return friend


@router.patch("/{username}", response_model=Friend, status_code=status.HTTP_200_OK)
async def update_friend_status(
    username: str,
    updated: Friendship,
    requester: User = Depends(get_current_active_user),
):
    try:
        friendship = get_friendship(requester.username, username)
    except FriendshipNotInDatabaseException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Neither you nor {username} requested friendship before",
        )
    if friendship.blocker == username and friendship.status == FriendshipStatus.BLOCKED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are blocked from interacting with this user",
        )
    elif (
        friendship.requester == requester.username
        and updated.status == FriendshipStatus.FRIEND
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can not accept user as friend since you requested",
        )
    else:
        update_friendship_in_db(requester.username, username, updated.status)
        return get_friend_from_db(requester.username, username)
