from typing import List
from fastapi import APIRouter, Depends, status
from messhap.db import get_friends_list_from_db

from messhap.models import Friend, User
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
