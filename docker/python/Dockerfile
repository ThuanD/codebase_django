FROM python:3.12.3-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Production environmental
#ENV UV_COMPILE_BYTECODE=1

# Install system dependencies
RUN <<OEF
apt-get update && apt-get install -y --no-install-recommends \
    vim \
    zsh \
    curl \
    make \
    ca-certificates
apt-get clean
rm -rf /var/lib/apt/lists/*
OEF

# Configure shell prompt
RUN echo "export PS1='🐳 \[\033[1;31m\]WHALE \[\033[1;36m\]\h \[\033[1;34m\]\W\[\033[0;35m\] \[\033[1;36m\]# \[\033[0m\]'" >> ~/.bashrc

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Set the working directory inside the container
WORKDIR /app

# Copy the pyproject.toml file to the working directory
COPY pyproject.toml uv.lock ./

# Sync the project into a new environment, using the frozen lockfile
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8000

# Ensure that all static files are collected on container startup and apply migrations
CMD ["uv", "run", "python", "manage.py", "migrate", "--settings=app.settings.docker", \
     "&&", "uv", "run", "python", "manage.py", "createcachetable", "--settings=app.settings.docker", \
     "&&", "uv", "run", "python", "manage.py", "collectstatic", "--noinput"]
