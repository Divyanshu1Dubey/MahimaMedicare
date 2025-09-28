from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Flush all data and reset database for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will DELETE ALL DATA from the database!\n'
                    'Run with --confirm to proceed: python manage.py flush_all_data --confirm'
                )
            )
            return

        self.stdout.write('🗑️  Flushing all data from database...')
        
        try:
            # Flush the database
            call_command('flush', '--noinput')
            self.stdout.write('✓ Database flushed successfully')
            
            # Remove SQLite database file if it exists
            if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                db_path = settings.DATABASES['default']['NAME']
                if os.path.exists(db_path):
                    os.remove(db_path)
                    self.stdout.write('✓ SQLite database file removed')
            
            # Run migrations to recreate tables
            self.stdout.write('🔄 Running migrations...')
            call_command('migrate')
            self.stdout.write('✓ Database tables recreated')
            
            self.stdout.write(
                self.style.SUCCESS(
                    '\n🎉 Database completely reset!\n\n'
                    'Next steps:\n'
                    '1. Run: python manage.py setup_test_data\n'
                    '2. Run: python manage.py collectstatic\n'
                    '3. Deploy to production\n\n'
                    'Ready for fresh production deployment!'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error flushing database: {e}')
            )