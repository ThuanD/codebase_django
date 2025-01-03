.PHONY: init key static migrations migrate cache messages compilemessages test coverage docs admin run gunicorn shell lint lint-fix hooks
init:
	uv pip install -r pyproject.toml

key:
	uv run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

static:
	uv run python manage.py collectstatic --no-input

migrations:
	uv run python manage.py makemigrations

migrate:
	uv run python manage.py migrate

cache:
	uv run python manage.py createcachetable

messages:
	uv run python manage.py makemessages -l vi

compilemessages:
	uv run python manage.py compilemessages

test:
	uv run python manage.py test

coverage:
	uv run coverage run --source='.' manage.py test --settings=app.settings.local_test
	uv run coverage html

docs:
	uv run python manage.py spectacular --file schema.yml

admin:
	DJANGO_SUPERUSER_PASSWORD=admin uv run python manage.py createsuperuser --username admin --email admin@example.com --noinput

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
