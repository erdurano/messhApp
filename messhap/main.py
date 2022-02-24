from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from .router import auth, users
from .db import fake_users_db
from .models import UserInDb, Token

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: auth.oauth2_form = Depends()):
    user = auth.authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            details = "Incorrect username or password",
            headers= {"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes= auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta= access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}