# QuickBite — Render deployment notes

This package contains the latest QuickBite source files from the uploaded project archive, including the customer ordering page, portfolio page, admin login, and the updated admin dashboard.

## Render service settings

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

## Required Render environment variables

- `SECRET_KEY`: set a long, random private value. Do not put it in source code or commit it to GitHub.
- `ADMIN_PASSWORD`: set the password you want to use for the admin login. Do not put it in source code or commit it to GitHub.

The app reads both values from environment variables. If `ADMIN_PASSWORD` is missing, the admin login will display that the password is not configured.

## Database note

The app creates `foodie.db` automatically when it starts. The database is deliberately excluded from this source package so local order/customer records are not uploaded to GitHub. On Render, SQLite data may be lost when the service's ephemeral filesystem is replaced. For long-term order storage, attach a Render persistent disk and configure the app to use a database path on that disk, or migrate to a managed database before using this for real customers.

## What is included

- `app.py`
- `templates/index.html`
- `templates/admin.html`
- `templates/login.html`
- `templates/portfolio.html`
- `requirements.txt`
- `Procfile`
- `.gitignore`

The local virtual environment, Git metadata, SQLite database, and backup HTML file are intentionally excluded.
