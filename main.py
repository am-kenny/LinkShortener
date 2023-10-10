from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

links = {}


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
                <input type="text" name="link">Your link</input>
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=response_content, status_code=200)


@app.post("/")
async def create_link(link: Annotated[str, Form()]):
    generated_code = str(uuid4())
    links[generated_code] = link
    response_content = f"""
    <html>
        <head>
            <title>Link is ready!</title>
        </head>
        <body>
            <p>Your link:</p>
            <a href="http://127.0.0.1:8000/{generated_code}" target="_blank">http://127.0.0.1:8000/{generated_code}</a>
        </body>
    </html>
    """
    return HTMLResponse(content=response_content, status_code=200)


@app.get("/{code}")
async def short_to_long(code: str):
    if code in links.keys():
        return RedirectResponse(links[code])
    else:
        return 404
