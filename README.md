# Django Base Project

A production-ready Django project template with:

- Django REST Framework
- OpenAPI documentation (drf-spectacular)
- Environment configuration
- Testing setup
- Docker support
- Code quality tools (ruff, pre-commit)

### Setup

1. Clone this repository:
    ```bash
    git clone https://github.com/ThuanD/base_django.git
    cd base_django
    ```
2. Create virtual environment:
    ```bash
    python -m venv venv
    ```
3. Copy `.env.example` to `.env` and configure:
    ```bash
    cp .env.example .env
    ```
   Create secret key and update `SECRET_KEY` in `.env` file
   ```bash
    uv run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Run migrations:
    ```bash
    python manage.py migrate
    ```
6. Start server:
    ```bash
    python manage.py runserver
    ```

### Running Tests

To run all tests:

```bash
  uv run coverage run --source='.' manage.py test --settings=app.settings.local_test
  uv run coverage html
```

### Lint check

1. Check only
    ```bash
    uvx ruff check
    ```
2. Check and fix
    ```bash
    uvx ruff check --fix
    ```
