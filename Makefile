test:


# Essential Makefile for Django project management
# Usage: make <command>

VENV=.venv/bin/activate
MIGRATION ?= zero


# Show help by default
.DEFAULT_GOAL := help

help:
	@echo "Available make commands:"
	@echo "  make setup         - Create venv and install dependencies"
	@echo "  make migrate       - Run database migrations"
	@echo "  make makemigrations- Create new migrations"
	@echo "  make run           - Start the development server"
	@echo "  make superuser     - Create a Django superuser"
	@echo "  make pytest        - Run pytest tests"
	@echo "  make test          - Run Django tests"
	@echo "  make coverage      - Run coverage for tests"
	@echo "  make precommit     - Run pre-commit checks"
	@echo "  make rmdb          - Remove local database file"
	@echo "  make rmmedia       - Remove local media folder"
	@echo "  make resetdb       - Reset DB, media, migrations, superuser"
	@echo "  make reset         - Full reset (setup + resetdb)"
	@echo "  make collectstatic - Collect static files"

# Create virtual environment
init:
	python -m venv .venv

# Install dependencies
setup: init
	. $(VENV) && pip install --upgrade pip
	. $(VENV) && pip install -r requirements.txt

# Run database migrations
migrate:
	. $(VENV) && python manage.py migrate

# Make new migrations
makemigrations:
	. $(VENV) && python manage.py makemigrations

# Run the development server
run:
	. $(VENV) && python manage.py runserver

# Create a superuser
superuser:
	. $(VENV) && python manage.py createsuperuser

# Run tests (pytest)
pytest:
	. $(VENV) && python -m pytest

# Run Django tests
test:
	. $(VENV) && python manage.py test

# Run coverage
coverage:
	. $(VENV) && coverage run -m pytest
	. $(VENV) && coverage report
	. $(VENV) && coverage html -d coverage_html

# Run pre-commit checks
precommit:
	. $(VENV) && pre-commit run --all-files

# Remove local DB and media
rmdb:
	rm ./db.sqlite3 || echo "Local DB file already deleted"

rmmedia:
	rm -rf ./media || echo "Media folder already deleted"

# Reset DB and media, then migrate and create superuser
resetdb: rmdb rmmedia makemigrations migrate superuser

reset: setup resetdb

# Collect static files
collectstatic:
	. $(VENV) && python manage.py collectstatic --noinput --clear