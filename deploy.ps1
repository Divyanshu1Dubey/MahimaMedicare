# PowerShell Deployment script for Mahima Medicare Test Environment

Write-Host "=== MAHIMA MEDICARE DEPLOYMENT SCRIPT ===" -ForegroundColor Green
Write-Host "Setting up production environment..." -ForegroundColor Yellow

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Cyan
python manage.py migrate

# Set up test data
Write-Host "Setting up test data and user accounts..." -ForegroundColor Cyan
python manage.py setup_test_data

# Collect static files
Write-Host "Collecting static files..." -ForegroundColor Cyan
python manage.py collectstatic --noinput

Write-Host ""
Write-Host "=== DEPLOYMENT COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Mahima Medicare is ready for testing!" -ForegroundColor Green
Write-Host ""
Write-Host "Website: https://mahima-test.onrender.com/" -ForegroundColor Blue
Write-Host ""
Write-Host "=== LOGIN CREDENTIALS ===" -ForegroundColor Yellow
Write-Host "SUPERUSER:" -ForegroundColor White
Write-Host "  Username: admin" -ForegroundColor Gray
Write-Host "  Password: admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "ADMIN:" -ForegroundColor White
Write-Host "  Username: hospital_admin" -ForegroundColor Gray
Write-Host "  Password: admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "DOCTOR:" -ForegroundColor White
Write-Host "  Username: dr_sharma" -ForegroundColor Gray
Write-Host "  Password: doctor123" -ForegroundColor Gray
Write-Host ""
Write-Host "PATIENT:" -ForegroundColor White
Write-Host "  Username: test_patient" -ForegroundColor Gray
Write-Host "  Password: patient123" -ForegroundColor Gray
Write-Host ""
Write-Host "LAB TECHNICIAN:" -ForegroundColor White
Write-Host "  Username: lab_tech" -ForegroundColor Gray
Write-Host "  Password: tech123" -ForegroundColor Gray
Write-Host ""
Write-Host "=== TESTING FEATURES ===" -ForegroundColor Yellow
Write-Host "✅ Standalone Test Booking (no login required)" -ForegroundColor Green
Write-Host "✅ COD (Cash on Delivery) System" -ForegroundColor Green
Write-Host "✅ Razorpay Payment Integration" -ForegroundColor Green
Write-Host "✅ Pharmacy with Medicine Catalog" -ForegroundColor Green
Write-Host "✅ Lab Test Management" -ForegroundColor Green
Write-Host "✅ Admin Dashboard" -ForegroundColor Green
Write-Host "✅ Doctor Portal" -ForegroundColor Green
Write-Host "✅ Patient Dashboard" -ForegroundColor Green
Write-Host ""
Write-Host "Ready for comprehensive manual testing!" -ForegroundColor Green