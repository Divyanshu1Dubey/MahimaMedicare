"""
Test the new features implemented:

1. ✅ Email Uniqueness Removed - Multiple users can register with same email
2. ✅ Medicine Expiry Notification - 3 months before (90 days)
3. ✅ Patient Prescription Upload - For pharmacist to see
4. ✅ Logo in Medicine Invoice - Mahima Medicare logo
5. ✅ All emails go to admin - marklegend029@gmail.com

TESTING INSTRUCTIONS:

## 1. Test Email Registration (Same Email Multiple Users)
Try registering multiple patients/doctors/admins with same email:
- Patient 1: username=john, email=test@test.com, password=john123
- Patient 2: username=jane, email=test@test.com, password=jane123
- Both should work now!

## 2. Test Medicine Expiry Notifications
Run command: python manage.py check_medicine_expiry
This will check medicines expiring in next 90 days and email admin

## 3. Test Patient Prescription Upload
- Login as patient
- Go to profile/edit
- Upload prescription image
- Pharmacist should be able to see it

## 4. Test Invoice with Logo
- Make a medicine order
- Complete payment
- Download invoice - should have Mahima Medicare logo

## 5. Test Admin Email Notifications
All system emails will go to: marklegend029@gmail.com

DEPLOYMENT NOTES:
- Changes committed and pushed to GitHub
- Will auto-deploy via CI/CD webhook
- Database migrations included
- Email settings updated for admin notifications
"""

# Test the expiry system
from datetime import date, timedelta
from pharmacy.models import Medicine

def test_expiry_system():
    print("Testing Medicine Expiry System...")
    
    # Check medicines expiring in next 90 days
    expiry_threshold = date.today() + timedelta(days=90)
    expiring_medicines = Medicine.objects.filter(
        expiry_date__lte=expiry_threshold,
        expiry_date__gte=date.today()
    )
    
    print(f"Found {expiring_medicines.count()} medicines expiring in next 3 months")
    
    for medicine in expiring_medicines[:5]:  # Show first 5
        days_left = (medicine.expiry_date - date.today()).days
        print(f"  • {medicine.name} - Expires: {medicine.expiry_date} ({days_left} days)")

if __name__ == "__main__":
    test_expiry_system()