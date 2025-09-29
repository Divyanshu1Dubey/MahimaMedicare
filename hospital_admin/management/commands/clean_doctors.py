"""
Management command to clean up all static doctor data
"""

from django.core.management.base import BaseCommand
from doctor.models import Doctor_Information
from hospital.models import User

class Command(BaseCommand):
    help = 'Remove all static doctor data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all doctor data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING('This will delete ALL doctor data. Use --confirm to proceed.')
            )
            doctor_count = Doctor_Information.objects.count()
            user_count = User.objects.filter(is_doctor=True).count()
            self.stdout.write(f'Found {doctor_count} doctor profiles and {user_count} doctor user accounts that will be deleted.')
            return

        # Delete all doctors and their user accounts
        doctor_count = Doctor_Information.objects.count()
        
        # Get all doctor users before deletion
        doctor_users = User.objects.filter(is_doctor=True)
        user_count = doctor_users.count()
        
        # Delete doctor information records
        Doctor_Information.objects.all().delete()
        
        # Delete doctor user accounts
        doctor_users.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {doctor_count} doctor profiles and {user_count} doctor user accounts from the database.')
        )
        self.stdout.write(
            self.style.SUCCESS('Database is now clean - ready for fresh doctor registrations!')
        )