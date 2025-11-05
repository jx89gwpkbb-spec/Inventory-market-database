Inventory Management Demo (SQLite)

This small demo provides a simple inventory database schema and a lightweight Python CLI
that exercises basic operations (add product, add warehouse, stock in/out, transfer).

Files added:
- `inventory/db/schema.sql` - SQL schema compatible with SQLite (also portable to Postgres with small tweaks)
- `inventory/models.py` - data layer using sqlite3
- `inventory/app.py` - CLI to demo operations
- `tests/test_inventory.py` - pytest tests for a basic flow

![Unit tests](https://github.com/jx89gwpkbb-spec/Inventory-market-database/actions/workflows/ci-unit.yml/badge.svg) ![E2E tests](https://github.com/jx89gwpkbb-spec/Inventory-market-database/actions/workflows/ci-e2e.yml/badge.svg)

Quick start (Windows PowerShell):

# create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# install test dependency
pip install pytest

# initialize the DB
python -m inventory.app init

# create example product and warehouses
python -m inventory.app add-product --sku PROD1 --name "Widget"
python -m inventory.app add-warehouse --name "Main"
python -m inventory.app add-warehouse --name "Overflow"

# stock in
python -m inventory.app stock-in --sku PROD1 --warehouse 1 --qty 100

# transfer
python -m inventory.app transfer --sku PROD1 --from 1 --to 2 --qty 20

# run tests
pytest -q

Run the web demo (Flask):

Make sure Flask is installed (see requirements.txt).

Windows PowerShell:
```powershell
python -m inventory.web
```

Then open http://127.0.0.1:5000/users/new to add users via a web form.

Switchboard (central demo UI):

Open http://127.0.0.1:5000/ for a small switchboard with quick links and an inline "create user" form.

Static assets:
- Message CSS is at `inventory/static/css/messages.css`
- Message JS is at `inventory/static/js/messages.js` (auto-dismiss and close button behavior)

Security: set a production secret
- The app uses `app.secret_key` for sessions and CSRF. Set an environment variable `FLASK_SECRET` in production.
	Example (PowerShell):
	```powershell
	$env:FLASK_SECRET = 'replace-with-secure-random-string'
	python -m inventory.web
	```

Notes / next steps:
- For production, use a proper DB (Postgres), add migrations (alembic, flyway, or SQL migration files), and connection pooling.
- Add validations, authentication, and an HTTP API (Flask/FastAPI) if you want a service layer.

Notes, rationale, and caveats
--------------------------------
- CSRF and sessions: The demo enables CSRF protection using `Flask-WTF` and reads the session secret from the `FLASK_SECRET` environment
	variable. This is intended to demonstrate good practice: CSRF must be enabled for any state-changing POST endpoints in a web app.
	For production, set `FLASK_SECRET` to a secure random value (do not commit it to source control).

- Password storage: Passwords are stored as hashes using Werkzeug's `generate_password_hash` (PBKDF2). This is suitable for a demo and
	avoids storing plaintext, but a production system should choose a vetted password policy, ensure strong hashing parameters, and add
	account protections (rate limiting, lockout, MFA).

- SQLite limitations: The project uses SQLite for simplicity. SQLite is fine for local demos and tests, but not for concurrent production
	deployments. When moving to Postgres or another server DB, add migrations (alembic) and update the data layer to use connection pooling
	or an ORM (SQLAlchemy) to avoid rewriting raw SQL across the codebase.

- Flash messages and UX: Flash messages are implemented via Flask's `flash()` and rendered by the `_messages.html` partial. Messages are
	one-request (persist across one redirect), shown in order, and categorized (`success`, `error`, `info`). The project includes a small
	JS snippet to auto-dismiss messages and a close button. Keep messages short — long messages will bloat the signed cookie session.

- Tests and CSRF: Tests disable CSRF (`WTF_CSRF_ENABLED = False`) for convenience when using the Flask test client. If you want to test
	CSRF behavior itself, do not disable CSRF: fetch the token from the GET response and include it in POSTs from the test client.

- Security posture: The demo intentionally keeps things simple. Before using anything like this in production, you must:
	1. Remove the dev fallback for `FLASK_SECRET` and supply a secure secret via environment or secret manager.
	2. Add HTTPS/TLS, secure cookie flags, and a production session backend.
	3. Add authentication/authorization around destructive actions (e.g., user deletion) and audit sensitive operations.

- Recommended immediate next steps for production hardening:
	- Switch to Postgres + alembic for migrations, and run the app under Gunicorn behind a reverse proxy.
	- Add Flask-Login (or equivalent) for session management and `@login_required` for protected routes.
	- Add Flask-Limiter or another rate limiter to protect login endpoints.

If you'd like, I can implement any of the above hardening steps (CSRF tests, Flask-Login integration, Postgres + migrations, CI workflow).
