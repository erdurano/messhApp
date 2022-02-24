from fastapi import APIRouter, Depends
from messhap.models import User
from messhap.router.auth import get_current_active_user

router = APIRouter(prefix="/users", tags=['User and Friend Management'])

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user