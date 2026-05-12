#!/bin/bash

# Production Deployment Script for EQUILA STYLE
# Make sure to run this from the project root directory

echo "🚀 Starting EQUILA STYLE Production Deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Please copy .env.example to .env and update with your production values"
    exit 1
fi

# Load environment variables
source .env

echo "✅ Environment variables loaded"
echo "🔧 DEBUG: $DEBUG"
echo "🌐 Domain: $ALLOWED_HOSTS"

# Install dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if needed (optional)
echo "👤 Creating superuser (if needed)..."
# python manage.py createsuperuser --noinput

echo "✅ Deployment setup complete!"
echo "🌐 Ready to serve at: https://equilastyle.com"
echo ""
echo "To start the production server:"
echo "gunicorn --bind 187.127.147.152:8000 equila_fashion.wsgi:application"
echo ""
echo "Or use systemd service for production deployment"
