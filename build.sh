#!/bin/bash

# build.sh - Django build script for VPS deployment

echo "Starting build process..."

# Exit immediately if a command exits with a non-zero status
set -e

# Activate virtual environment (CRITICAL)
source ~/Apps/venvs/smartapplicant_venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
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
# exec gunicorn _core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --threads 6 --timeout 120 --log-level=info