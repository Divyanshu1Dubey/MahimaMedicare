from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from .models import Medicine
from hospital.models import User

LOW_STOCK_THRESHOLD = 15
EXPIRY_DAYS_THRESHOLD = 30


def get_recipients():
    emails = list(User.objects.filter(is_hospital_admin=True).values_list('email', flat=True))
    emails += list(User.objects.filter(is_pharmacist=True).values_list('email', flat=True))
    # Filter out empty emails
    return [e for e in emails if e]


@receiver(post_save, sender=Medicine)
def medicine_alerts(sender, instance: Medicine, created, **kwargs):
    recipients = get_recipients()
    if not recipients:
        return

    alerts = []

    # Low stock alert
    try:
        qty = int(instance.quantity or 0)
    except Exception:
        qty = 0
    if qty < LOW_STOCK_THRESHOLD:
        alerts.append(f"Low stock: {instance.name} has only {qty} units left.")

    # Expiring soon alert
    try:
        if getattr(instance, 'is_expiring_soon', False):
            alerts.append(f"Expiring soon: {instance.name} expires on {instance.expiry_date}.")
    except Exception:
        pass

    if not alerts:
        return

    subject = "Pharmacy Alert: " + ("; ".join([a.split(':')[0] for a in alerts]))
    context = {
        'medicine': instance,
        'alerts': alerts,
    }
    html_message = render_to_string('pharmacy_mail_alert.html', context)
    plain_message = strip_tags(html_message)
    try:
        send_mail(subject, plain_message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'), recipients, html_message=html_message, fail_silently=True)
    except BadHeaderError:
        pass

