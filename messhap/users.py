from fastapi import APIRouter, Depends
from .models import User
from .auth import get_current_active_user

router = APIRouter(prefix="/users", tags=['User management'])

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user