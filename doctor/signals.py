from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# from django.contrib.auth.models import User

from .models import Doctor_Information
from hospital.models import User


# # from django.core.mail import send_mail
# # from django.conf import settings


@receiver(post_save, sender=Doctor_Information)
def updateUser(sender, instance, created, **kwargs):
    # user.profile or below (1-1 relationship goes both ways)
    doctor = instance
    user = doctor.user

    if created == False:
        # Only update fields if they have valid values
        if doctor.name:
            user.first_name = doctor.name
        elif not user.first_name:
            # Set a default name if both doctor.name and user.first_name are empty
            user.first_name = user.username or "Doctor"
            
        if doctor.username:
            user.username = doctor.username
        
        if doctor.email:
            user.email = doctor.email
            
        user.save()
