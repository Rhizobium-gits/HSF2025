from fastapi import FastAPI, Request, Form, UploadFile, File
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
import shutil
import json

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "change-me"))

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# OAuth configuration (replace with actual credentials)
oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "openid email profile"},
)

class Post(BaseModel):
    id: str
    author: str
    author_id: str
    author_picture: Optional[str] = None
    text: str
    image_url: Optional[str] = None
    likes: int = 0
    liked_by: List[str] = []

posts: List[Post] = []

POSTS_FILE = "posts.json"


def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "r") as f:
            data = json.load(f)
        posts.clear()
        for item in data:
            posts.append(Post(**item))


def save_posts():
    with open(POSTS_FILE, "w") as f:
        json.dump([p.dict() for p in posts], f, ensure_ascii=False, indent=2)


load_posts()


class Profile(BaseModel):
    building: str = "バジル"
    comment: str = ""

user_profiles: Dict[str, Profile] = {}

BUILDING_ICONS = {
    "バジル": "grass",
    "パプリカ": "local_florist",
    "ローズマリー": "spa",
    "ターメリック": "eco",
}
BUILDINGS = list(BUILDING_ICONS.keys())


def get_current_user(request: Request):
    return request.session.get('user')


@app.get('/')
async def root():
    return RedirectResponse('/timeline')


@app.get('/timeline')
async def timeline(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(
        'timeline.html',
        {
            'request': request,
            'user': user,
            'posts': posts,
            'profiles': user_profiles,
            'icons': BUILDING_ICONS,
            'active': 'timeline',
        },
    )


@app.get('/post')
async def post_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse('/login')
    return templates.TemplateResponse(
        'post.html',
        {
            'request': request,
            'user': user,
            'active': 'post',
        },
    )


@app.get('/profile')
async def profile(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse('/login')
    profile = user_profiles.get(user['id'], Profile())
    return templates.TemplateResponse(
        'profile.html',
        {
            'request': request,
            'user': user,
            'profile': profile,
            'buildings': BUILDINGS,
            'icons': BUILDING_ICONS,
            'active': 'profile',
        },
    )


@app.post('/profile')
async def update_profile(request: Request, building: str = Form(...), comment: str = Form("")):
    user = get_current_user(request)
    if not user:
        return RedirectResponse('/login')
    user_profiles[user['id']] = Profile(building=building, comment=comment)
    return RedirectResponse('/profile', status_code=303)


@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        # Most likely an invalid grant or redirect mismatch
        return templates.TemplateResponse(
            'error.html',
            {'request': request, 'error': f"OAuth failed: {e}"},
            status_code=400,
        )
    try:
        user = await oauth.google.parse_id_token(request, token)
    except Exception:
        # Fallback in case id_token is missing
        resp = await oauth.google.get('userinfo', token=token)
        user = resp.json()

    request.session['user'] = {
        'id': user['id'],
        'name': user['name'],
        'picture': user.get('picture'),
    }
    if user['id'] not in user_profiles:
        user_profiles[user['id']] = Profile()
    return RedirectResponse('/timeline')


@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse('/timeline')


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

    post = Post(
        id=uuid.uuid4().hex,
        author=user['name'],
        author_id=user['id'],
        author_picture=user.get('picture'),
        text=text,
        image_url=image_url,
    )
    posts.append(post)
    save_posts()
    return RedirectResponse('/timeline', status_code=303)


@app.post('/posts/{post_id}/delete')
async def delete_post(request: Request, post_id: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse('/login')
    for i, p in enumerate(posts):
        if p.id == post_id and p.author_id == user['id']:
            posts.pop(i)
            save_posts()
            break
    return RedirectResponse('/timeline', status_code=303)


@app.post('/posts/{post_id}/like')
async def like_post(request: Request, post_id: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse('/login')
    for p in posts:
        if p.id == post_id:
            if user['id'] in p.liked_by:
                p.liked_by.remove(user['id'])
                p.likes -= 1
            else:
                p.liked_by.append(user['id'])
                p.likes += 1
            break
    save_posts()
    return RedirectResponse('/timeline', status_code=303)
