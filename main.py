from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl, ValidationError
from requests_html import HTMLSession, AsyncHTMLSession
from bs4 import BeautifulSoup
import uvicorn

class urlrender_request(BaseModel):
    url: HttpUrl
    sleep: int

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/url/render/title")
async def url_render_title(item: urlrender_request):
    session = AsyncHTMLSession()
    resp = await session.get(item.url)
    await resp.html.arender(sleep=item.sleep)
    soup = BeautifulSoup(resp.html.html, "lxml")
    return {
        "url": f"{item.url}",
        "title": f"{soup.title}"
    }

@app.post("/url/render/body")
async def url_render_body(item: urlrender_request):
    session = AsyncHTMLSession()
    resp = await session.get(item.url)
    await resp.html.arender(sleep=item.sleep)
    soup = BeautifulSoup(resp.html.html, "lxml")
    return {
        "url": f"{item.url}",
        "body": f"{soup.body}"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
