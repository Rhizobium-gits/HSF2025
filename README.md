# HSF2025

## Project Overview
This repository holds a prototype of an SNS for a school festival. Accounts are associated with Google using OAuth authentication. Users are able to post text and images and other users can like those posts.

## Implementation Plan
1. **Framework**: Build the server with **FastAPI**. Static pages and templates are served directly by Python, so the front‑end can be implemented with standard HTML templates.
2. **Google OAuth**: Use **Authlib** to integrate Google login. Successful authentication stores basic user information in the session.
3. **Data Model**: For the prototype, posts and likes are stored in-memory. Each post contains an id, author data, text, optional image URL, and a like counter.
4. **Endpoints**:
   - `/` – Home page showing posts.
   - `/login` – Redirects the user to Google for authentication.
   - `/auth` – OAuth callback. After verification the user is returned to `/`.
   - `/logout` – Clears the session.
   - `/posts` – API for creating and listing posts.
   - `/posts/{post_id}/like` – Toggles a like for the authenticated user.
5. **Front-end**: The initial UI uses simple Jinja2 templates rendered by FastAPI. JavaScript is kept minimal for posting and liking actions.
6. **Next Steps**: Later iterations may add a database (SQLAlchemy + Alembic), improved API structure, and a React/Vite front-end.

Run `uvicorn main:app --reload` to start the development server after installing dependencies from `requirements.txt`.
