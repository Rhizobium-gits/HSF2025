from fastapi import FastAPI, Request, Form, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel
from typing import List, Optional
import uuid
import shutil

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="CHANGE_ME")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# OAuth configuration (replace with actual credentials)
oauth = OAuth()
oauth.register(
    name='google',
    client_id='GOOGLE_CLIENT_ID',
    client_secret='GOOGLE_CLIENT_SECRET',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

class Post(BaseModel):
    id: str
    author: str
    text: str
    image_url: Optional[str] = None
    likes: int = 0

posts: List[Post] = []


def get_current_user(request: Request):
    return request.session.get('user')


@app.get('/')
async def home(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse('home.html', {'request': request, 'user': user, 'posts': posts})


@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    request.session['user'] = {'id': user['sub'], 'name': user['name']}
    return RedirectResponse('/')


@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse('/')


@app.post('/posts')
async def create_post(request: Request, text: str = Form(...), image: UploadFile = File(None)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse('/login')

    image_url = None
    if image:
        filename = f"static/{uuid.uuid4().hex}_{image.filename}"
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = "/" + filename

    post = Post(id=uuid.uuid4().hex, author=user['name'], text=text, image_url=image_url)
    posts.append(post)
    return RedirectResponse('/', status_code=303)


@app.post('/posts/{post_id}/like')
async def like_post(request: Request, post_id: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse('/login')
    for p in posts:
        if p.id == post_id:
            p.likes += 1
            break
    return RedirectResponse('/', status_code=303)
