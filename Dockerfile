# --- Stage 1: Build Environment ---
# We'll use a larger base image for building to ensure all C libraries for dependencies are available.
FROM python:3.12-bookworm as builder

# Set environment variables for Pipenv
ENV PIPENV_VENV_IN_PROJECT=1
ENV PIPENV_COLORBLIND=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Pipenv and any build dependencies
RUN pip install --no-cache-dir pipenv

# Set the working directory
WORKDIR /usr/src/app

# Copy Pipfile and Pipfile.lock first to leverage Docker's cache
COPY Pipfile Pipfile.lock ./

# Install project dependencies. The --system flag installs packages directly into the
# system's Python, avoiding a virtual environment inside the container.
# The --deploy flag ensures that the Pipfile.lock is up-to-date with Pipfile.
# If it's not, the build will fail, which is good for production stability.
# COPY --chown=appuser:appuser . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libgl1 \
    libglu1-mesa \
    libsm6 \
    libice6 \
    && rm -rf /var/lib/apt/lists/*

RUN pipenv install --deploy --system --skip-lock

# --- Stage 2: Production Environment ---
# We'll use a lightweight, production-ready base image.
# We're building from scratch and only adding what's absolutely necessary.
FROM python:3.12-bookworm

# Create a non-root user for security and set it as the user.
RUN useradd -ms /bin/bash appuser
USER appuser

# Set the working directory
WORKDIR /usr/src/app

# Copy the application code from your project directory.
# This assumes your app files are in the same directory as the Dockerfile.
COPY --chown=appuser:appuser . .

# Copy the installed packages from the builder stage's system site-packages
# This is what makes the final image small and fast.
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Collect static files. Ensure you have 'whitenoise' or similar installed for production.
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# The command to run your Django app using Gunicorn, a production-grade WSGI server.
# Replace 'your_project_name.wsgi' with your actual project's WSGI file path.
# For example, if your project is named 'myproject', it would be 'myproject.wsgi'.
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "etchingdashboard.wsgi"]
