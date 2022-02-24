from typing import List, Optional
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    # General purpose user class that can be extensible
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDb(User):
    hashed_password: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


