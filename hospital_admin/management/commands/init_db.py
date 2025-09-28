from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Initialize fresh database for production'

    def handle(self, *args, **options):
        self.stdout.write('🗄️ Initializing production database...')
        
        try:
            # If using SQLite and the database doesn't exist, create it
            if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                db_path = settings.DATABASES['default']['NAME']
                if not os.path.exists(db_path):
                    self.stdout.write('Creating new SQLite database...')
            
            # Try to create all tables from scratch
            self.stdout.write('Creating all database tables...')
            
            # First run migrations for core Django apps
            core_apps = ['contenttypes', 'auth', 'sessions']
            for app in core_apps:
                try:
                    call_command('migrate', app, verbosity=0)
                    self.stdout.write(f'✓ Created {app} tables')
                except Exception as e:
                    self.stdout.write(f'⚠️ {app} tables: {e}')
            
            # Then run all migrations
            try:
                call_command('migrate', '--run-syncdb', verbosity=0)
                self.stdout.write('✓ Created all application tables')
            except Exception as e:
                self.stdout.write(f'⚠️ Some tables may not be created: {e}')
                # Try without syncdb
                call_command('migrate', verbosity=0)
            
            # Verify session table exists
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_session';")
                if cursor.fetchone():
                    self.stdout.write('✅ Session table verified')
                else:
                    self.stdout.write('❌ Session table missing - trying to create...')
                    call_command('migrate', 'sessions', verbosity=0)
            
            self.stdout.write('🎉 Database initialization complete!')
            
        except Exception as e:
            self.stdout.write(f'❌ Database initialization error: {e}')
            # Last resort - try basic migrate
            call_command('migrate', verbosity=0)