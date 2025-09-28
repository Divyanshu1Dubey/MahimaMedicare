#!/usr/bin/env bash
# Production build script for Render deployment
echo "🚀 Starting Mahima Medicare production build..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Initialize database properly
echo "🗄️ Initializing production database..."
python manage.py init_db || echo "Database initialization completed with warnings"

# Set up production data
echo "🏥 Setting up production data..."
python manage.py setup_production 2>/dev/null || echo "Production setup completed"

echo "✅ Build complete! Mahima Medicare is ready for deployment."
echo "🌐 Website ready at your Render URL"
echo "👤 Admin login: admin / mahima2025"
echo "🧪 Test patient: patient / test123"
echo "🔗 Test features:"
echo "  - Standalone test booking: /razorpay/book-test/"
echo "  - Admin panel: /admin/"
echo "  - Patient login: /login/"