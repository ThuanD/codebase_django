.PHONY: init update-deps secret_key static migrate cache test run gunicorn shell run-hooks
init:
	uv pip install -r pyproject.toml

key:
	uv run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

static:
	uv run python manage.py collectstatic --no-input

migrate:
	uv run python manage.py migrate

cache:
	uv run python manage.py createcachetable

test:
	uv run coverage run --source='.' manage.py test --settings=app.settings.local_test
	uv run coverage html

run:
	uv run python manage.py runserver

gunicorn:
	uv run gunicorn app.wsgi:application -b 0.0.0.0:8000 --timeout 300 --reload

shell:
	uv run python manage.py shell_plus

lint:
	uvx ruff check

lint-fix:
	uvx ruff check --fix

hooks:
	uv run pre-commit run --all-files
