# CourseCompass

Professor rating site for KBTU students — PjM 101, Group 5.

**Stack:** React (Vite) · Django REST Framework · PostgreSQL

```
backend/    Django + DRF API
frontend/   React app (Vite)
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
- Optional demo data: `python manage.py seed_demo` (30 fictional professors, 11 courses, sample reviews, and demo accounts; it prints the logins)

No Postgres installed? `docker compose up -d` in the project root starts one with the settings from `.env.example`.

## Run the frontend

```bash
cd frontend
npm install
cp .env.example .env          # VITE_API_URL=http://localhost:8000/api
npm run dev                   # http://localhost:5173
```

## API (MVP)

| Method | URL | Who | What |
|---|---|---|---|
| POST | `/api/auth/register/` | anyone | Sign up with an `@kbtu.kz` email (`email`, `password`); sends a verification link |
| GET | `/api/auth/verify/?token=` | anyone | Confirms the email and activates the account |
| POST | `/api/auth/login/` | anyone | Returns `token`; send it as `Authorization: Token <token>` |
| POST | `/api/auth/logout/` | logged in | Deletes the token |
| GET | `/api/auth/me/` | logged in | Current user (`id`, `email`, `is_staff`) |
| GET | `/api/professors/?search=&faculty=&ordering=` | anyone | List / search professors with average rating; `ordering` = `name` (default), `rating` or `reviews` |
| GET | `/api/professors/faculties/` | anyone | Faculty codes for the filter |
| GET | `/api/professors/<id>/` | anyone | One professor, with how many 1–5 ratings they got |
| GET | `/api/professors/<id>/reviews/` | anyone | Approved reviews of a professor |
| GET | `/api/courses/` | anyone | List of courses |
| POST | `/api/reviews/` | logged in | Submit a review (`professor`, `course`, `rating` 1–5, `comment`) — starts as *pending* |

Reviews appear on the site only after an admin approves them in `/admin/` → Reviews (filter by *Pending*, select, then run *Approve selected reviews*).

**Response fields.** Professor: `id`, `full_name`, `faculty`, `average_rating`, `review_count` (+ `rating_distribution` on the detail page). Course: `id`, `code`, `title`. Review: `id`, `course`, `rating`, `comment`, `created_at` — the author is never returned, reviews are anonymous. Averages count approved reviews only.

**Email verification in development.** `.env.example` uses Django's console email backend: the verification link is printed in the backend terminal instead of being emailed (mock verification for the demo). For real emails, set `EMAIL_BACKEND` to SMTP and fill the `EMAIL_*` values.

## Data model

Four tables: `users`, `professors`, `courses`, `reviews` — see `docs/CourseCompass_ER_diagram.png`.
Only `@kbtu.kz` emails can register; one review per user per professor per course.
The database itself also rejects ratings outside 1–5 and duplicate reviews (`CHECK` and `UNIQUE` constraints).
