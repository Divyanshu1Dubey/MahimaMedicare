#!/bin/bash
# Deployment script for Mahima Medicare Test Environment

echo "=== MAHIMA MEDICARE DEPLOYMENT SCRIPT ==="
echo "Setting up production environment..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Set up test data
echo "Setting up test data and user accounts..."
python manage.py setup_test_data

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo ""
echo "🎉 Mahima Medicare is ready for testing!"
echo ""
echo "Website: https://mahima-test.onrender.com/"
echo ""
echo "=== LOGIN CREDENTIALS ==="
echo "SUPERUSER:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "ADMIN:"
echo "  Username: hospital_admin" 
echo "  Password: admin123"
echo ""
echo "DOCTOR:"
echo "  Username: dr_sharma"
echo "  Password: doctor123"
echo ""
echo "PATIENT:"
echo "  Username: test_patient"
echo "  Password: patient123"
echo ""
echo "LAB TECHNICIAN:"
echo "  Username: lab_tech"
echo "  Password: tech123"
echo ""
echo "=== TESTING FEATURES ==="
echo "✅ Standalone Test Booking (no login required)"
echo "✅ COD (Cash on Delivery) System"
echo "✅ Razorpay Payment Integration" 
echo "✅ Pharmacy with Medicine Catalog"
echo "✅ Lab Test Management"
echo "✅ Admin Dashboard"
echo "✅ Doctor Portal"
echo "✅ Patient Dashboard"
echo ""
echo "Ready for comprehensive manual testing!"