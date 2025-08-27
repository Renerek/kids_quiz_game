# math_quiz_game

A small Django-based math quiz web app used for local development and testing.

## Prerequisites

- Git
- Python 3.11+ (3.12 recommended)
- Optional: pyenv (if you manage multiple Python versions)

## Clone

Replace <repo-url> with your repository URL and run:

```bash
git clone <repo-url> math_quiz_game
cd math_quiz_game
```

## Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
# On Windows (PowerShell): .\\venv\\Scripts\\Activate.ps1
```

## Install dependencies

If this project provides a `requirements.txt`, install it. Otherwise at minimum install Django:

```bash
pip install -r requirements.txt  # if present
# or
pip install Django==5.2.5
```

## Database migrations

The project uses SQLite by default. Apply migrations and (optionally) create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser  # optional
```

## Run the development server

```bash
python manage.py runserver
# Visit http://127.0.0.1:8000/ in your browser
```

## Notes

- The repository may include a pre-built `venv/` directory. If present you can activate it with `source venv/bin/activate`.
- Static files are served automatically by Django's development server. For production, run `python manage.py collectstatic` and use a proper WSGI/ASGI server.
- The project ships with `db.sqlite3` for quick local testing. Do not use this DB file for production.

## Questions or issues

If you run into problems, paste the error output and I can help troubleshoot.
