# math_quiz_game

An educational Django web app with multiple kid‑friendly learning mini‑games and a lightweight authentication + email verification system.

## Key Features

- Math Quiz (addition, subtraction, multiplication, division, mixed mode) with difficulty levels (easy/medium/hard)
- Spelling Game
- "What Time Is It" clock reading game
- Basic Q&A (personal information questions flow)
- Fruits & Animals recognition games (image + multiple choice + summaries)
- Mixed Game mode combining activities
- Dynamic audio feedback (intros, correct/incorrect, encouragement streaks)
- Optional personalized spoken encouragement (Web Speech API client side)
- Video mascot on home page (muted autoplay with explicit unmute/restart)
- User accounts (signup, login, logout)
- Email verification (inactive until verified)
- Resend verification email endpoint
- Password reset flow (request → email link → set new password)
- Contact form (emails sent via configured backend)
- Internationalization scaffolding (language switching endpoint)

---

## Prerequisites

- Git
- Python 3.11+ (3.12 recommended)
- Optional: pyenv (if you manage multiple Python versions)

## Clone

Replace YOUR_REPO_URL with your repository URL and run:

```bash
git clone YOUR_REPO_URL math_quiz_game
cd math_quiz_game
```

## Quickstart with Makefile (recommended)

This repository includes a `Makefile` with convenient targets that wrap virtualenv activation and common Django tasks. Run the commands from the project root (where `manage.py` lives).

Common targets:

- `make setup` — create a `.venv` and install `requirements.txt` into it
- `make migrate` — run database migrations
- `make makemigrations` — create new migrations
- `make run` — start the development server (runs via the `.venv` created by `make setup`)
- `make superuser` — create a Django superuser
- `make pytest` — run tests with pytest (uses `python -m pytest`)
- `make test` — run Django's test runner
- `make collectstatic` — collect static files
- `make precommit` — run pre-commit hooks
- `make reset` — convenience target: `setup` + `resetdb` (removes local DB/media, migrates, creates superuser)

Examples (copy/paste):

```bash
# create venv and install runtime deps
make setup

# run migrations and start the server
make migrate
make run

# run the test suite
make pytest
```

Notes:

- Always activate the appropriate virtualenv before running `manage.py` (avoids ModuleNotFoundError for Django).
- `requirements.txt` at the project root enables `pip install -r requirements.txt` (a minimal one is included for local testing).
- Static images live under `quiz/static/quiz/images/` (e.g. `boy-girl-are-reading-books.jpg`). If an image doesn't appear in the browser, check the file exists and that the template uses the `{% static %}` tag.
- If CI fails on pre-commit or linters, run `pre-commit run --all-files` and fix the reported issues locally before pushing.
- Email verification & password reset rely on correctly configured `DEFAULT_FROM_EMAIL` and chosen backend.
- If password reset emails 500 with reverse errors, ensure the `quiz` URLs are included and that you are using the provided namespaced patterns (already configured in `quiz/urls.py`).
- The Makefile creates/uses `.venv` by default. If you prefer a different name, you can still use the virtualenv manually, but `make` targets expect `.venv` unless you edit the Makefile.
- If you need developer tools (pytest, pre-commit, debug toolbar) installed into your venv, run `pip install -r requirements-dev.txt` inside the venv or use `make setup` and then manually install dev deps.

If you prefer not to use the Makefile, the manual commands previously shown (creating a venv, pip installing requirements, running `python manage.py migrate` and `python manage.py runserver`) will still work.

For deployment (e.g. on Render), ensure your `requirements.txt` is up to date and your `ALLOWED_HOSTS` setting in `mathquiz/settings.py` includes your deployed domain (e.g. `math-quiz-game.onrender.com`).

To run with Gunicorn in production:

```bash
gunicorn mathquiz.wsgi
```

## Running Tests

See `docs/testing.md` for deeper guidance on the suite structure and category runner script. For the quick version:

To run all automated tests for the project, use:

```bash
python manage.py test  # runs all 70 tests (models, games, auth, email flows)
```

### Run Specific Test Categories

For faster testing during development, run specific test categories:

```bash
# Core functionality only
python manage.py test quiz.tests.QuizModelTests quiz.tests.SpellingGameTests quiz.tests.FruitGameTests quiz.tests.AnimalGameTests

# All game features
python manage.py test quiz.tests.FruitGameTests quiz.tests.AnimalGameTests quiz.tests.MixedGameTests quiz.tests.MathQuizTests

# Use the automated test runner script (for CI/CD)
python run_tests.py
```

## Authentication & Accounts

### Signup & Email Verification

1. User signs up at `/quiz/signup/` with username, email, name, (optional) age, city, country.
2. Account is created inactive and a signed, time‑limited (48h) verification link is emailed.
3. User clicks link (`/quiz/verify/<token>/`) to activate the account.

### Resend Verification

If the email is lost/expired: `/quiz/resend-verification/` → enter email → new link sent (still 48h validity from new token).

### Login / Logout

- Login: `/quiz/login/`
- Logout POST (or GET redirect) at `/quiz/logout/`
- Inactive (unverified) users are prevented from logging in and see a hint to resend the verification email.

### Password Reset

1. Request: `/quiz/password-reset/` (enter email; non‑enumerating response)
2. Email delivers link to: `/quiz/reset/<uidb64>/<token>/`
3. Set new password form → redirects to `/quiz/reset/done/`

### Contact Form

`/quiz/contact/` sends an email to the configured recipient (currently hardcoded address in `quiz/views.py`). Adjust as needed.

## Email Configuration

By default emails use the console backend (printed to terminal). Provide environment variables to enable SMTP or file backend.

Supported environment variables (set before running `runserver`):

| Variable | Purpose | Default |
|----------|---------|---------|
| `EMAIL_BACKEND` | Override backend directly | `django.core.mail.backends.console.EmailBackend` |
| `EMAIL_HOST` | SMTP host; if set and `EMAIL_BACKEND` unset, switches to SMTP backend | (empty) |
| `EMAIL_PORT` | SMTP port | 587 |
| `EMAIL_USE_TLS` | Use TLS (true/false) | true |
| `EMAIL_HOST_USER` | SMTP username | (empty) |
| `EMAIL_HOST_PASSWORD` | SMTP password | (empty) |
| `DEFAULT_FROM_EMAIL` | From header | `ntumngiar@gmail.com` |
| `EMAIL_FILE_PATH` | Directory for file backend if chosen | `./sent_emails` |

Example (Unix shell):

```bash
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_HOST_USER="your@gmail.com"
export EMAIL_HOST_PASSWORD="app_password_here"
export EMAIL_USE_TLS=true
python manage.py runserver
```

To use the file backend:

```bash
export EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
export EMAIL_FILE_PATH=$(pwd)/sent_emails
python manage.py runserver
```

## Audio Generation (Optional)

The project includes an advanced audio generation system for creating kid-friendly voice audio files. This is optional for development but creates consistent, high-quality audio for the game.

### Setup Audio Generation

```bash
# Install audio generation dependencies (optional)
pip install -r docs/audio_requirements.txt

# On Ubuntu/Debian, you may also need system dependencies:
sudo apt-get install ffmpeg

# On macOS with Homebrew:
brew install ffmpeg
```

### Generate Audio Files

```bash
# Generate all audio files with default kid-friendly settings
python make_intro.py

# Custom pitch and speed
python make_intro.py --pitch 1.4 --speed 0.8

# Generate single custom audio file
python make_intro.py --text "Hello, welcome to our game!"

# List all audio files that will be generated
python make_intro.py --list

# Legacy format (still supported)
python make_intro.py 1.3 0.9 "Custom text"
```

The audio generation system creates:

- Welcome messages and game introductions
- Feedback sounds (correct/incorrect responses)
- Encouragement messages
- Game-specific audio for each activity

All audio uses consistent kid-friendly pitch (higher) and speed (slightly slower for clarity).

## Notes

- The repository may include a pre-built virtual environment directory (either `venv/` or `.venv/`). Activate accordingly.
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
python manage.py collectstatic
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

Notes:
