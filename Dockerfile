FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=healthstack.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        git \
        nginx \
        supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project
COPY . /app/

# Create production environment
RUN echo 'SECRET_KEY=mahima-medicare-docker-production-key-2025' > .env && \
    echo 'DEBUG=False' >> .env && \
    echo 'ALLOWED_HOSTS=139.84.155.25,localhost' >> .env && \
    echo 'DATABASE_URL=sqlite:///./db.sqlite3' >> .env

# Collect static files and setup database
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate
RUN python manage.py init_db

# Create media directory
RUN mkdir -p media

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/sites-available/default

# Copy supervisor configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create startup script
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# Expose port
EXPOSE 80

# Start services
CMD ["/start.sh"]