from pydantic import BaseModel, EmailStr, root_validator, validator


class User(BaseModel):
    # General purpose user class that can be extensible
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserRegister(User):
    password1: str
    password2: str
    disabled: bool = False

    @validator("full_name")
    def name_must_contain_space(cls, value):
        if ' ' not in value:
            raise ValueError("must contain a space")
        return value

    @validator("password2")
    def password_match(cls, val, values):
        if 'password' in values and val != values['password']:
            raise ValueError('Passwords do not match')
        return val

    @validator("password1", allow_reuse=True)
    def password_structure(cls, value):
        if len(value) < 6 or not value.isalnum():
            raise ValueError(('Password must be at least 6 chars long'
                              ' and must be alphanumerical'))
        return value


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    disabled: bool | None = False
    old_password: str | None = None
    password1: str | None = None
    password2: str | None = None

    @validator("full_name")
    def name_must_contain_space(cls, value):
        if ' ' not in value:
            raise ValueError("must contain a space")
        return value

    @validator("password1", "password2", allow_reuse=True)
    def password_structure(cls, value):
        if len(value) < 6 or not value.isalnum():
            raise ValueError('Password must be at least 6 chars long'
                             ' and must be alphanumerical')
        return value

    @root_validator(pre="True")
    def old_password_must_be_supplied(cls, values: dict):
        if any(values.get(key) for key in (
                "old_password", "password1", "password2"
                )):
            if not all(values.get(key) for key in (
                    "old_password", "password1", "password2"
                    )):
                raise ValueError("If you want to change password"
                                 ", all three fields are required")
        return values


class UserInDb(User):
    hashed_password: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
