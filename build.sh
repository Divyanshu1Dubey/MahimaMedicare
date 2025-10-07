#!/bin/bash
# Render Build Script for Mahima Medicare
# Your Health Partner

echo "Building Mahima Medicare Healthcare System..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

# Run migrations
python manage.py migrate

echo "Build completed successfully!"
echo "Mahima Medicare is ready for production deployment!"
