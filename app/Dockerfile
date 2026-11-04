# 1. Start from a small official Python image
FROM python:3.12-slim

# 2. Work inside /app in the container
WORKDIR /app

# 3. Install dependencies first (Docker caches this layer,
#    so rebuilds are fast when only app.py changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the application code
COPY app.py .

# 5. Version is baked into the image; override with --build-arg
ARG APP_VERSION=1.0.0
ENV APP_VERSION=${APP_VERSION}

# 6. Do not run as root inside the container
RUN useradd --create-home appuser
USER appuser

# 7. Document the port and define the start command
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "app:app"]
