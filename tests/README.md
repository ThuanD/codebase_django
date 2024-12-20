# Testing Guide

## Running Tests
bash

## Run all tests
```bash
make test
```

## Run specific test file
```bash
poetry run python manage.py test tests.app.django.test_pagination
```

## Run with coverage
```bash
poetry run coverage run manage.py test
poetry run coverage report
```


## Test Structure
- Unit Tests: `tests/app/`
- Integration Tests: `tests/integration/`
- Performance Tests: `tests/performance/`
