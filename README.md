## Base Project - Django

Python version 3.12.3

uv 0.5.6

### Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/ThuanD/base_django.git
    cd base_django
    ```
2. Create virtual environment:
    ```bash
    uv venv --python 3.12.3
    ```
3. Install dependencies:
    ```bash
    uv pip install -r pyproject.toml
    ```
4. Set up environment variables:
    ```bash
    cp .env.example .env
    ```
   Create secret key and update `SECRET_KEY` in `.env` file
   ```bash
    uv run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
    ```
5. Collect static files:
    ```bash
    uv run python manage.py collectstatic --no-input
    ```
6. Apply migrations:
    ```bash
    uv run python manage.py migrate
    ```
7. Create cache table:
    ```bash
    uv run python manage.py createcachetable
    ```
8. Run the development server:
    ```bash
    uv run python manage.py runserver
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
