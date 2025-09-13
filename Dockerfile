# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Install Poetry
RUN pip install poetry

# Set environment variables for Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Set workdir
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --no-root --without dev

# Copy application code
COPY . /app

# Expose FastAPI default port
EXPOSE 8000

# Run the app
CMD ["poetry", "run", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
