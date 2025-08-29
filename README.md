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


## Running the App

Make sure you are in the project root directory (`math_quiz_game`) where `manage.py` is located before running any Django commands.

To start the development server:

```bash
cd math_quiz_game  # if not already in this folder
source venv/bin/activate  # activate your virtual environment
python manage.py runserver
# Visit http://127.0.0.1:8000/ in your browser
```

For deployment (e.g. on Render), ensure your `requirements.txt` is up to date and your `ALLOWED_HOSTS` setting in `mathquiz/settings.py` includes your deployed domain (e.g. `math-quiz-game.onrender.com`).

To run with Gunicorn in production:

```bash
gunicorn mathquiz.wsgi
```

## Running Tests

To run all automated tests for the project, use:

```bash
python manage.py test
```

This will discover and run all tests in the `quiz/tests.py` file and any other test modules in your Django apps.

## Notes

- The repository may include a pre-built `venv/` directory. If present you can activate it with `source venv/bin/activate`.
- Static files are served automatically by Django's development server. For production, run `python manage.py collectstatic` and use a proper WSGI/ASGI server.
- The project ships with `db.sqlite3` for quick local testing. Do not use this DB file for production.

## Questions or issues

If you run into problems, paste the error output and I can help troubleshoot.

## Notes & CI checklist

Use this checklist to reproduce the repository's CI checks locally before pushing changes.

Quick smoke tests (small project):

```bash
# from /home/admin1/projects/math_quiz_game
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or pip install Django==5.2.5 pillow
python manage.py migrate
python manage.py runserver
# Verify static assets, e.g. http://127.0.0.1:8000/static/quiz/images/learning_path.png
```


## Pre-commit checks

To run code quality checks before pushing:

1. Install pre-commit (already done):
	```bash
	pip install pre-commit
	```
2. Add the pre-commit config (already included in this repo).
3. Install the git hook:
	```bash
	pre-commit install
	```
4. Run all checks manually:
	```bash
	pre-commit run --all-files
	```

This will check formatting (black), linting (flake8), and import sorting (isort) before you push code.

Notes:

- Always activate the appropriate virtualenv before running `manage.py` (avoids ModuleNotFoundError for Django).
- `requirements.txt` at the project root enables `pip install -r requirements.txt` (a minimal one is included for local testing).
- Static images live under `quiz/static/quiz/images/` (e.g. `boy-girl-are-reading-books.jpg`). If an image doesn't appear in the browser, check the file exists and that the template uses the `{% static %}` tag.
- If CI fails on pre-commit or linters, run `pre-commit run --all-files` and fix the reported issues locally before pushing.
