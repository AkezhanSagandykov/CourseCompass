# CourseCompass

Professor rating site for KBTU students — PjM 101, Group 5.

**Stack:** React (Vite) · Django REST Framework · PostgreSQL

```
backend/    Django + DRF API
frontend/   React app (Akezhan creates it with: npm create vite@latest frontend -- --template react)
```

## Run the backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate     macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then put your Postgres password in .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- API: http://127.0.0.1:8000/api/
- Admin (add professors, moderate reviews): http://127.0.0.1:8000/admin/
- Tests: `python manage.py test`

## API (MVP)

| Method | URL | Who | What |
|---|---|---|---|
| GET | `/api/professors/?search=&faculty=` | anyone | List / search professors with average rating |
| GET | `/api/professors/<id>/` | anyone | One professor |
| GET | `/api/professors/<id>/reviews/` | anyone | Approved reviews of a professor |
| GET | `/api/courses/` | anyone | List of courses |
| POST | `/api/reviews/` | logged in | Submit a review (`professor`, `course`, `rating` 1–5, `comment`) — starts as *pending* |

Reviews appear on the site only after an admin approves them in `/admin/` → Reviews.

## Data model

Four tables: `users`, `professors`, `courses`, `reviews` — see `docs/CourseCompass_ER_diagram.png`.
Only `@kbtu.kz` emails can register; one review per user per professor per course.
