from pydantic import BaseModel, EmailStr, validator


class User(BaseModel):
    # General purpose user class that can be extensible
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserUpdate(User):
    username: str | None = None
    old_password: str | None = None
    new_password1: str | None = None
    new_password2: str | None = None
    disabled: bool | None = False

    @validator("new_password2")
    def password_match(cls, val, values, **kwargs):
        if 'new_password1' in values and val != values['new_password1']:
            raise ValueError('Passwords do not match')
        return val

    @validator("new_password1")
    def old_password_must_be_supplied(cls, val, values, **kwargs):
        if 'old_password' not in values:
            raise ValueError(
                "old password must be supplied for password change"
                )
        elif 'old_password' in values and not val:
            raise ValueError(
                "You should supply new password if you want to change password"
            )
        return val

    @validator("new_password1", allow_reuse=True)
    def password_structure(cls, value):
        if value is not None and (len(value) < 6 or not value.isalnum()):
            raise ValueError(('Password must be at least 6 chars long'
                              ' and must be alphanumerical'))
        return value


class UserRegister(User):
    password: str
    password2: str
    disabled: bool = False

    @validator("full_name")
    def name_must_contain_space(cls, value):
        if ' ' not in value:
            raise ValueError("must contain a space")
        return value

    @validator("password2")
    def password_match(cls, val, values, **kwargs):
        if 'password' in values and val != values['password']:
            raise ValueError('Passwords do not match')
        return val

    @validator("password", allow_reuse=True)
    def password_structure(cls, value):
        if len(value) < 6 or not value.isalnum():
            raise ValueError(('Password must be at least 6 chars long'
                              ' and must be alphanumerical'))
        return value


class UserInDb(User):
    hashed_password: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
