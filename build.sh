#!/bin/bash

# build.sh - Django build script for Render deployment

echo "Starting build process..."

# Exit immediately if a command exits with a non-zero status
set -e

# Install Python dependencies
echo "Installing Python dependencies..."
pip install gunicorn whitenoise
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Start the application with Gunicorn
# echo "Starting Gunicorn..."
# exec gunicorn _core.wsgi:application \
#     --bind 0.0.0.0:$PORT \
#     --workers 4 \
#     --timeout 120 \
#     --log-level=info
