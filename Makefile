.PHONY: install key static makemigrations migrate test coverage docs admin run gunicorn shell lint lint-fix format format-check hooks

install:
	@echo "Installing dependencies..."
	uv pip install -r pyproject.toml --dev

key:
	@echo "Generating secret key..."
	uv run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

static:
	@echo "Collecting static files..."
	uv run python manage.py collectstatic --no-input

makemigrations:
	@echo "Making database migrations..."
	uv run python manage.py makemigrations

migrate:
	@echo "Migrating database..."
	uv run python manage.py migrate

cache:
	@echo "Creating cache table..."
	uv run python manage.py createcachetable

lang:
	@echo "Making messages..."
	uv run python manage.py makemessages -l vi

compile:
	@echo "Compiling messages..."
	uv run python manage.py compilemessages

test:
	@echo "Running tests..."
	uv run python manage.py test

coverage:
	@echo "Running tests with coverage report..."
	uv run coverage run --source='.' manage.py test --settings=app.settings.local_test
	uv run coverage html

docs:
	@echo "Generating API documentation..."
	uv run python manage.py spectacular --file schema.yml

admin:
	@echo "Creating superuser..."
	uv run python manage.py createsuperuser --username admin --email admin@example.com --noinput

run:
	@echo "Running development server..."
	uv run python manage.py runserver

gunicorn:
	@echo "Running app with Gunicorn..."
	uv run gunicorn app.wsgi:application --workers 4 -b 0.0.0.0:8000 --timeout 300

shell:
	@echo "Starting Django shell..."
	uv run python manage.py shell_plus

format-check:
	@echo "Formating code and check..."
	uvx ruff format . --check

format:
	@echo "Formating code..."
	uvx ruff format .

lint:
	@echo "Running linter..."
	uvx ruff check

lint-fix:
	@echo "Running linter and fixing errors..."
	uvx ruff check --fix

hooks:
	@echo "Running pre-commit hooks..."
	uv run pre-commit run --all-files
