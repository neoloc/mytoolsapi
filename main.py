from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl, ValidationError
from requests_html import HTMLSession, AsyncHTMLSession
from bs4 import BeautifulSoup
from pymemcache.client import base
import uvicorn
from base64 import b64encode, b64decode

# create connection to local memcached service
cache = base.Client(('127.0.0.1', 11211))

# create request item class
class urlrender_request(BaseModel):
    url: HttpUrl
    sleep: int

# start the fastapi app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to MyToolsAPI"}

@app.post("/url/render/title")
async def url_render_title(item: urlrender_request):
    # create a base64 encode of the URL as a key for memcached
    urlencode: str = b64encode(item.url.encode('ascii'))
    # check memcached for the key
    if cache.get(urlencode) is None:
        # doesnt exist, so render the page normally
        session = AsyncHTMLSession()
        resp = await session.get(item.url)
        await resp.html.arender(sleep=item.sleep)
        soup = BeautifulSoup(resp.html.html, "lxml")
        # encode soup object as base64, then store in memcached
        soupcode: str = b64encode(soup.encode('ascii'))
        cache.set(urlencode, soupcode)
    else:
        # already exists in memcached, create a new soup object from memcached
        soup = BeautifulSoup(b64decode(cache.get(urlencode)).decode("utf-8", "ignore"), 'lxml')
    # return the data as json
    return {
        "url": f"{item.url}",
        "title": f"{soup.title}"
    }

@app.post("/url/render/body")
async def url_render_body(item: urlrender_request):
    # create a base64 encode of the URL as a key for memcached
    urlencode: str = b64encode(item.url.encode('ascii'))
    # check memcached for the key
    if cache.get(urlencode) is None:
        # doesnt exist, so render the page normally
        session = AsyncHTMLSession()
        resp = await session.get(item.url)
        await resp.html.arender(sleep=item.sleep)
        soup = BeautifulSoup(resp.html.html, "lxml")
        # encode soup object as base64, then store in memcached
        soupcode: str = b64encode(soup.encode('ascii'))
        cache.set(urlencode, soupcode)
    else:
        # already exists in memcached, create a new soup object from memcached
        soup = BeautifulSoup(base64.b64decode(cache.get(urlencode)).decode("utf-8", "ignore"), 'lxml')
    # return the data as json
    return {
        "url": f"{item.url}",
        "body": f"{soup.body}"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
