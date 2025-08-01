# Django Base Project

A production-ready Django project template with:

- Django REST Framework
- OpenAPI documentation (drf-spectacular)
- Environment configuration
- Testing setup
- Docker support
- Code quality tools (ruff, pre-commit)

### Local setup

#### Pre-requisites

- Python 3.12
- uv 0.5.5
- GNU Make 4.3

1. Clone this repository:
    ```bash
    git clone https://github.com/ThuanD/codebase_django.git
    cd codebase_django
    ```
2. Create virtual environment and Install dependencies:
    ```bash
    uv sync
    ```
3. Copy `.env.example` to `.env` and edit configurations:
    ```bash
    cp .env.example .env
    ```
   Create secret key and update `SECRET_KEY` in `.env` file
   ```bash
    make key
    ```
4. Collect static files:
    ```bash
    make static
    ```
5. Run migrations:
    ```bash
    make migrate
    ```
6. Create cache table:
    ```bash
    make cahce
    ```
7. Start server:
    ```bash
    make run
    ```
8. To run server with gunicorn:
    ```bash
    make gunicorn
    ```
9. Create superuser:

    Update `DJANGO_SUPERUSER_PASSWORD, username, email` in Makefile and run the following command:
    ```bash
    make admin
    ```

### Running Tests

1. To run all tests with django:

   ```bash
     make test
   ```
2. To run all tests with coverage:

   ```bash
     make coverage
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

### Docker setup

1. Build docker image:
    ```bash
    docker compose build
    ```
2. Run docker container:
    ```bash
    docker compose up
    ```
3. Stop docker container:
    ```bash
    docker compose down
    ```
4. Remove docker image:
    ```bash
    docker compose down --rmi all
    ```
