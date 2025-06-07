# HSF2025

## Project Overview
This repository holds a prototype of an SNS for a school festival. Accounts are associated with Google using OAuth authentication. Users are able to post text and images and other users can like those posts.

## Implementation Plan
1. **Framework**: Build the server with **FastAPI**. HTML templates and static files are served directly from Python for a lightweight front end.
2. **Google OAuth**: Use **Authlib** to integrate Google login. The client ID,
   client secret and the session secret key are loaded from environment
   variables. Register `http://localhost:8000/auth` as the callback URL in the
   Google Developer Console.
3. **Data Model**: Posts and likes are stored in memory. Each post contains an id, author name, text, optional image URL, and a like counter.
4. **Endpoints**:
   - `/` – Home page showing posts.
   - `/login` – Redirects to Google for authentication.
   - `/auth` – OAuth callback; after verification the user is returned home.
   - `/logout` – Clears the session.
   - `/posts` – Create a new post.
   - `/posts/{post_id}/like` – Like a post.
5. **Front-end**: Jinja2 templates render the pages. A small stylesheet under `static/style.css` adds a simple card layout and form styling for a cleaner look.
6. **Next Steps**: Later iterations may add persistent storage (SQLAlchemy + PostgreSQL) and a full React/Vite interface.

Set the following environment variables before running the server:
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
SESSION_SECRET=some-random-string
```

Run `uvicorn main:app --reload` after installing dependencies from `requirements.txt`.

The unused `index.html` from an earlier prototype was removed to avoid confusion.
