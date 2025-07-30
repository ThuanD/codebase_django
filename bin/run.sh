#!/bin/bash
set -e

# Default values
RUN_MIGRATIONS=${RUN_MIGRATIONS:-true}
RUN_COLLECTSTATIC=${RUN_COLLECTSTATIC:-true}
SKIP_SETUP=${SKIP_SETUP:-false}
UPDATE_DEPENDENCIES=${UPDATE_DEPENDENCIES:-true}

# Cache directory for tracking changes
CACHE_DIR="/tmp/.app_cache"
mkdir -p "$CACHE_DIR"

# Function to check if dependencies need updating
needs_dependency_update() {
    # Create hash of dependency files
    local current_hash=""
    
    if [ -f "pyproject.toml" ]; then
        current_hash+=$(md5sum pyproject.toml | cut -d' ' -f1)
    fi
    
    if [ -f "uv.lock" ]; then
        current_hash+=$(md5sum uv.lock | cut -d' ' -f1)
    fi
    
    # Create final hash
    current_hash=$(echo "$current_hash" | md5sum | cut -d' ' -f1)
    
    # Check against stored hash
    local stored_hash_file="$CACHE_DIR/deps_hash"
    
    if [ ! -f "$stored_hash_file" ]; then
        echo "$current_hash" > "$stored_hash_file"
        return 0  # true - first run, need to install
    fi
    
    local stored_hash=$(cat "$stored_hash_file")
    
    if [ "$current_hash" != "$stored_hash" ]; then
        echo "$current_hash" > "$stored_hash_file"
        return 0  # true - hash changed, need to update
    fi
    
    return 1  # false - no changes
}

# Function to check if migrations are needed
needs_migration() {
    python manage.py showmigrations --plan --settings=${DJANGO_SETTINGS_MODULE} | grep -q "\[ \]"
}

# Function to check if static files need collecting
needs_collectstatic() {
    # Check if staticfiles directory exists and has content
    if [ ! -d "staticfiles" ] || [ -z "$(ls -A staticfiles 2>/dev/null)" ]; then
        return 0  # true - needs collecting
    fi
    
    # Check if any static files are newer than collected files
    if [ "$(find . -name '*.css' -o -name '*.js' -o -name '*.png' -o -name '*.jpg' -o -name '*.svg' -newer staticfiles 2>/dev/null | head -1)" ]; then
        return 0  # true - needs collecting
    fi
    
    return 1  # false - no need to collect
}

# Skip all setup if requested
if [ "$SKIP_SETUP" = "true" ]; then
    echo "Skipping setup (dependencies, migrations and static files)..."
else
    # Handle dependencies update
    if [ "$UPDATE_DEPENDENCIES" = "true" ]; then
        if needs_dependency_update; then
            echo "Dependencies changed, updating..."
            pip install --system --group dev pyproject.toml
        else
            echo "Dependencies up to date, skipping..."
        fi
    else
        echo "Dependency updates disabled by UPDATE_DEPENDENCIES=false"
    fi

    # Handle migrations
    if [ "$RUN_MIGRATIONS" = "true" ]; then
        if needs_migration; then
            echo "Running migrations..."
            python manage.py migrate --settings=${DJANGO_SETTINGS_MODULE}
        else
            echo "No migrations needed, skipping..."
        fi
    else
        echo "Migrations disabled by RUN_MIGRATIONS=false"
    fi

    # Handle static files
    if [ "$RUN_COLLECTSTATIC" = "true" ]; then
        if needs_collectstatic; then
            echo "Collecting static files..."
            python manage.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE}
        else
            echo "Static files up to date, skipping..."
        fi
    else
        echo "Static file collection disabled by RUN_COLLECTSTATIC=false"
    fi
fi

echo "Starting Gunicorn..."
exec python -m gunicorn \
    --workers ${GUNICORN_WORKERS:-4} \
    --bind 0.0.0.0:8000 \
    --env DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --keep-alive ${GUNICORN_KEEP_ALIVE:-5} \
    --reload \
    app.wsgi:application
