from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

class Command(BaseCommand):
    help = 'Ensure all essential Django tables are created'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Ensuring essential Django tables exist...')
        
        try:
            # Check if session table exists
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='django_session';
                """)
                if not cursor.fetchone():
                    self.stdout.write('Creating session table...')
                    call_command('migrate', 'sessions', '0001', verbosity=0)
            
            # Ensure auth tables exist
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='auth_user';
                """)
                if not cursor.fetchone():
                    self.stdout.write('Creating auth tables...')
                    call_command('migrate', 'auth', verbosity=0)
            
            # Ensure contenttypes table exists
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='django_content_type';
                """)
                if not cursor.fetchone():
                    self.stdout.write('Creating contenttypes tables...')
                    call_command('migrate', 'contenttypes', verbosity=0)
            
            self.stdout.write('✅ Essential Django tables verified/created')
            
        except Exception as e:
            self.stdout.write(f'⚠️ Error checking tables: {e}')
            # Try to create all tables
            call_command('migrate', '--run-syncdb', verbosity=0)
            self.stdout.write('✅ Ran syncdb to create missing tables')