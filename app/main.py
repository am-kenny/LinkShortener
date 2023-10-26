from hashlib import md5
from typing import Annotated, Optional

import uvicorn
from fastapi import FastAPI, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.models import UserInDB, User
from app.utils import add_short_link, get_long_link, update_short_link, add_redirect, get_user_by_token, \
    get_user_by_username, check_url_master

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

"""
ID користувача використовується як токен (як на занятті) і потребується аутентифікація для створення та редагування посилань 
"""


@app.get("/")
async def root():
    response_content = """
    <html>
        <head>
            <title>Link shortener</title>
        </head>
        <body>
            <h1>Shorten your link!</h1>
            <form method="post">
                <input type="text" name="link" placeholder="Your link"></input>
                <input type="text" name="short_code" placeholder="Short link"></input>
                <input type="submit" value="Submit">
            </form>
            <br>
            <br>
            <h2>Update your link!</h2>
            <form action="/update" method="post">
                <input type="text" name="url_code" placeholder="Your short link"></input>
                <input type="text" name="new_long_url" placeholder="Your new long link"></input>
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """

    return HTMLResponse(content=response_content, status_code=200)


def hash_password(password: str):
    return md5(password.encode('utf-8')).hexdigest()


async def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user_dict = await get_user_by_token(token)
    if user_dict:
        return UserInDB(**user_dict)
    return None


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)]
):
    user = await fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user_dict = await get_user_by_username(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = str(user_dict["_id"])

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.post("/")
async def create_link(
        link: Annotated[str, Form()],
        current_user: Annotated[User, Depends(get_current_active_user)],
        short_code: Optional[str] = Form(None)
):
    user_dict = await get_user_by_username(current_user.username)
    token = user_dict["_id"]
    short_url = await add_short_link(link, short_code, token=token)
    if not short_url:

        return {'error': 'short url already exists'}

    response_content = f"""
    <html>
        <head>
            <title>Link is ready!</title>
        </head>
        <body>
            <p>Your link:</p>
            <a href="{app.url_path_for('short_to_long', url_code=short_url)}" target="_blank">{short_url}</a>
        </body>
    </html>
    """

    return HTMLResponse(content=response_content, status_code=200)


@app.post("/update")
async def update_short(url_code: Annotated[str, Form()],
                       new_long_url: Annotated[str, Form()],
                       current_user: Annotated[User, Depends(get_current_active_user)]):
    user_dict = await get_user_by_username(current_user.username)
    token = user_dict["_id"]
    isMaster = check_url_master(url_code, token)
    if isMaster:
        short_url = await update_short_link(url_code, new_long_url)
        if short_url:
            response_content = f"""
            <html>
                <head>
                    <title>Link is ready!</title>
                </head>
                <body>
                    <p>Your link:</p>
                    <a href="{app.url_path_for('short_to_long', url_code=short_url)}" target="_blank">{short_url}</a>
                </body>
            </html>
            """

            return HTMLResponse(content=response_content, status_code=200)

    return {'error': 'nothing modified'}


@app.get("/{url_code}")
async def short_to_long(url_code: str):
    long_url = await get_long_link(url_code)
    await add_redirect(url_code)
    if long_url:
        return RedirectResponse(long_url)

    return 404


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8009, log_level="debug")
