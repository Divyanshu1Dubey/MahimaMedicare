from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta
from pharmacy.models import Medicine
from hospital.models import User


class Command(BaseCommand):
    help = 'Check for medicines expiring in 3 months and send notifications to admin'
    
    def handle(self, *args, **options):
        # Get medicines expiring in the next 90 days
        expiry_threshold = date.today() + timedelta(days=90)
        expiring_medicines = Medicine.objects.filter(
            expiry_date__lte=expiry_threshold,
            expiry_date__gte=date.today()
        ).order_by('expiry_date')
        
        if not expiring_medicines:
            self.stdout.write('No medicines expiring in the next 3 months.')
            return
        
        # Get all admin users
        admin_users = User.objects.filter(is_hospital_admin=True)
        admin_emails = [user.email for user in admin_users if user.email]
        
        if not admin_emails:
            self.stdout.write('No admin email addresses found.')
            return
        
        # Prepare email content
        message_lines = ['MEDICINE EXPIRY ALERT - 3 MONTH NOTICE', '=' * 50, '']
        
        for medicine in expiring_medicines:
            days_left = (medicine.expiry_date - date.today()).days
            message_lines.append(
                f"• {medicine.name} ({medicine.medicine_id}) - "
                f"Expires: {medicine.expiry_date} ({days_left} days left) - "
                f"Stock: {medicine.stock_quantity}"
            )
        
        message_lines.extend(['', 'Please take necessary action to replace expiring stock.'])
        email_message = '\n'.join(message_lines)
        
        try:
            send_mail(
                subject=f'Medicine Expiry Alert - {len(expiring_medicines)} items expiring soon',
                message=email_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=admin_emails,
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Expiry notification sent to {len(admin_emails)} admins for {len(expiring_medicines)} medicines.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            )