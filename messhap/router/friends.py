from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from messhap.db import (FriendshipNotInDatabaseException,
                        add_friend_request_in_db, get_friend_from_db,
                        get_friends_list_from_db, get_friendship)
from messhap.models import Friend, Friendship, FriendshipStatus, User
from messhap.router.auth import get_current_active_user

router = APIRouter(prefix="/friends", tags=["Friend Management"])


@router.get(
    '',
    response_model=List[Friend],
    status_code=status.HTTP_200_OK)
async def get_friend_list(
    current_user: User = Depends(get_current_active_user)
):

    return get_friends_list_from_db(current_user)


@router.get(
    '/{requested_uname}',
    response_model=Friend,
    status_code=status.HTTP_200_OK
)
async def get_friend(
    requested_uname: str,
    requester: User = Depends(get_current_active_user)
):
    try:
        return get_friend_from_db(
            requester.username,
            requested_uname
        )
    except FriendshipNotInDatabaseException as e:
        raise HTTPException(
            status_code=404,
            detail=e.message
        )


@router.post(
    '/{requested_uname}',
    response_model=Friend,
    status_code=status.HTTP_201_CREATED
)
async def post_friend_request(
    requested_uname: str,
    requester: User = Depends(get_current_active_user)
):
    friendship: Friendship = get_friendship(
        requester.username,
        requested_uname)

    if friendship.status != FriendshipStatus.NOT_FRIEND:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already interacted with this user"
        )
    elif friendship.status == FriendshipStatus.BLOCKED\
            and friendship.blocker == requested_uname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are blocked by this user"
        )
    add_friend_request_in_db(requester.username, requested_uname)

    friend = get_friend_from_db(
        requester.username,
        requested_uname)
    return friend
