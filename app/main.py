from typing import Annotated, Optional

import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.utils import add_short_link, get_long_link, update_short_link

app = FastAPI()


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


@app.post("/")
async def create_link(link: Annotated[str, Form()], short_code: Optional[str] = Form(None)):
    short_url = await add_short_link(link, short_code)
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


@app.get("/{url_code}")
async def short_to_long(url_code: str):
    long_url = await get_long_link(url_code)
    if long_url:
        return RedirectResponse(long_url)

    return 404


@app.post("/update")
async def update_short(url_code: Annotated[str, Form()], new_long_url: Annotated[str, Form()]):
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


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8009, log_level="info")
