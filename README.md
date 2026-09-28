# fin-lab

Fintech project scaffold: Next.js frontend, Django/DRF API, Celery worker, PostgreSQL, and Redis.

## Stack

- **Frontend**: Next.js (App Router, TypeScript, Tailwind) — `frontend/`
- **Backend API**: Django + Django REST Framework — `backend/`
- **Async tasks**: Celery, broker + result backend on Redis
- **Database**: PostgreSQL
- **Interactive shell**: `django-extensions` `shell_plus` (IPython) for ops/debugging
- **Containers**: exactly five Docker Compose services: `frontend`, `backend` (API), `celery_worker`, `db` (PostgreSQL), and `redis`

The API and worker are separate runtime services built from the same Django codebase; the transaction-processing task is the current asynchronous service boundary. PostgreSQL and Redis provide persistence and messaging.

## Quick start (Docker)

```bash
cp .env.example .env   # adjust secrets as needed
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/health/
- Django admin: http://localhost:8000/admin/

The frontend uses the internal `backend` hostname for server-side API requests. The API container is health-checked before the frontend starts.

## Backend domains

The Django API is divided into `identity`, `accounts`, `core` (transfers), and `notifications` apps. They currently share one API process and database so a transfer can debit and credit accounts atomically; these are domain boundaries, not independently deployed microservices.

- `POST /api/auth/register/` accepts `username`, `email`, and `password`.
- `POST /api/auth/login/` returns a token. Send it as `Authorization: Token <token>` to protected endpoints.
- `GET /api/auth/me/` returns the authenticated user; `POST /api/auth/logout/` revokes the token.
- `GET` and `POST /api/accounts/` list or create accounts. New accounts start at zero; balances are read-only through the API.
- `GET` and `POST /api/transactions/` list transfers or queue a transfer. Create with `reference`, `source_account` (the id of one of your accounts), `destination_account` (the recipient's 16-character `account_number`), and `amount`; both accounts must use the same currency. Transfers are immutable once created: `PUT`, `PATCH`, and `DELETE` are not allowed.
- `GET /api/notifications/` lists the authenticated user's notifications. `POST /api/notifications/{id}/read/` marks one as read.

Transfers settle in the Celery worker. Insufficient funds or inactive accounts fail without changing balances. This scaffold has no deposit/funding endpoint or external email/SMS provider.

Run backend tests with `docker compose run --rm backend python manage.py test core identity notifications`.

Create a superuser for the admin site:

```bash
docker compose exec backend python manage.py createsuperuser
```

Open the interactive shell (IPython via shell_plus) inside the backend container:

```bash
docker compose exec backend python manage.py shell_plus
```

## Local development (without Docker)

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # POSTGRES_HOST/CELERY urls point at localhost
python manage.py migrate
python manage.py runserver
```

Run a Celery worker (separate terminal, Redis must be running locally):

```bash
cd backend && source .venv/bin/activate
celery -A config worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project layout

```
fin-lab/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── config/         # Django project (settings, urls, celery.py)
│   ├── core/           # Sample app: Transaction model/API + Celery task
│   ├── manage.py
│   └── requirements.txt
└── frontend/
    └── app/            # Next.js App Router
```

The transaction API enqueues settlement through `core/tasks.py`; completed and failed transfers create in-app notifications. Treat this as a development scaffold, not a production-ready ledger or payment system.
