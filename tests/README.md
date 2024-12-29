# Testing Guide

## Running Tests
bash

## Run all tests
```bash
uv run python manage.py test
```

## Run specific test file
```bash
uv run python manage.py test tests.app.django.test_exception --settings=app.settings.local_test
```

## Run with coverage
```bash
uv run coverage run --source='.' manage.py test --settings=app.settings.local_test
uv run coverage html
```


## Test Structure
- Unit Tests: `tests/app/`
- Integration Tests: `tests/integration/`
- Performance Tests: `tests/performance/`
