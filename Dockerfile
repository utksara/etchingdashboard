# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIPENV_VENV_IN_PROJECT=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy Pipfile and Pipfile.lock first (for better caching)
COPY Pipfile Pipfile.lock /app/

# Install dependencies from Pipfile.lock
RUN pipenv install --deploy --system

# Copy project files
COPY . /app/

# Expose Django default port
EXPOSE 8000

# Run Django (you may replace with gunicorn for production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
