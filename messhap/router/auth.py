
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from messhap.db import fake_users_db as fake_users_db
from messhap.models import TokenData, User, UserInDb

SECRET_KEY = '753050f81ac0298391264d2a7d1c30dcdf2782e432b81faf9e81309b50fedde8'
ALGORITM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
oauth2_form = OAuth2PasswordRequestForm

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDb(**user_dict)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

#this would be replaced
def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "Could not validate credentials",
        headers= {"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, uname=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITM)
    return encoded_jwt

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Inactive User")
    return current_user

def fake_hash_password(password: str):
    return "fakehashed" + password

router = APIRouter(prefix="/login", tags= ["Authentication"])

