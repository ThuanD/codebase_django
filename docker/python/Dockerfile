FROM python:3.12.3-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Production environmental
#ENV UV_COMPILE_BYTECODE=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ca-certificates \
    curl \
    libpq-dev \
    make \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Configure shell prompt
RUN echo "export PS1='🐳 \[\033[1;31m\]WHALE \[\033[1;36m\]\h \[\033[1;34m\]\W\[\033[0;35m\] \[\033[1;36m\]# \[\033[0m\]'" >> ~/.bashrc

# Install uv
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --no-cache-dir uv

# Copy pyproject.toml and install project dependencies
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/pip \
    uv pip install -r pyproject.toml --system

# Expose port
EXPOSE 8000
