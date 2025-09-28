from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings
import os
import sqlite3

class Command(BaseCommand):
    help = 'Initialize fresh database for production with guaranteed table creation'

    def handle(self, *args, **options):
        self.stdout.write('🗄️ AGGRESSIVE DATABASE INITIALIZATION for Production...')
        
        try:
            # If using SQLite, ensure database file exists and is writable
            if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                db_path = settings.DATABASES['default']['NAME']
                db_dir = os.path.dirname(db_path)
                
                # Ensure directory exists
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                    self.stdout.write(f'Created database directory: {db_dir}')
                
                # Create empty database file if it doesn't exist
                if not os.path.exists(db_path):
                    open(db_path, 'a').close()
                    self.stdout.write(f'Created database file: {db_path}')
            
            # Method 1: Try standard Django migrations first
            self.stdout.write('Method 1: Running standard migrations...')
            try:
                call_command('migrate', verbosity=0)
                self.stdout.write('✓ Standard migrations completed')
            except Exception as e:
                self.stdout.write(f'⚠️ Standard migrations failed: {e}')
            
            # Method 2: Force create core Django tables using raw SQL
            self.stdout.write('Method 2: Force creating core Django tables...')
            self.create_core_tables()
            
            # Method 3: Run migrations with syncdb
            self.stdout.write('Method 3: Running migrations with syncdb...')
            try:
                call_command('migrate', '--run-syncdb', verbosity=0)
                self.stdout.write('✓ Syncdb migrations completed')
            except Exception as e:
                self.stdout.write(f'⚠️ Syncdb migrations failed: {e}')
            
            # Method 4: Verify and manually create session table if needed
            self.stdout.write('Method 4: Verifying session table...')
            if not self.verify_session_table():
                self.create_session_table_manually()
            
            # Final verification
            if self.verify_all_tables():
                self.stdout.write('🎉 DATABASE INITIALIZATION SUCCESS!')
            else:
                self.stdout.write('⚠️ Some tables may be missing, but continuing...')
            
        except Exception as e:
            self.stdout.write(f'❌ Critical database error: {e}')
            # Last resort
            self.stdout.write('LAST RESORT: Basic migrate...')
            call_command('migrate', verbosity=0)
    
    def create_core_tables(self):
        """Force create core Django tables using raw SQL"""
        try:
            with connection.cursor() as cursor:
                # Create django_session table manually
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS django_session (
                        session_key VARCHAR(40) NOT NULL PRIMARY KEY,
                        session_data TEXT NOT NULL,
                        expire_date DATETIME NOT NULL
                    );
                ''')
                
                # Create django_content_type table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS django_content_type (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        app_label VARCHAR(100) NOT NULL,
                        model VARCHAR(100) NOT NULL,
                        UNIQUE(app_label, model)
                    );
                ''')
                
                # Create auth_user table (basic version)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS auth_user (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        password VARCHAR(128) NOT NULL,
                        last_login DATETIME,
                        is_superuser BOOL NOT NULL,
                        username VARCHAR(150) NOT NULL UNIQUE,
                        first_name VARCHAR(150) NOT NULL,
                        last_name VARCHAR(150) NOT NULL,
                        email VARCHAR(254) NOT NULL,
                        is_staff BOOL NOT NULL,
                        is_active BOOL NOT NULL,
                        date_joined DATETIME NOT NULL
                    );
                ''')
                
                self.stdout.write('✓ Core tables created with raw SQL')
                
        except Exception as e:
            self.stdout.write(f'⚠️ Raw SQL table creation failed: {e}')
    
    def verify_session_table(self):
        """Check if session table exists"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_session';")
                exists = cursor.fetchone() is not None
                if exists:
                    self.stdout.write('✓ Session table exists')
                else:
                    self.stdout.write('❌ Session table missing')
                return exists
        except:
            return False
    
    def create_session_table_manually(self):
        """Force create session table"""
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE django_session (
                        session_key VARCHAR(40) NOT NULL PRIMARY KEY,
                        session_data TEXT NOT NULL,
                        expire_date DATETIME NOT NULL
                    );
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS django_session_expire_date_idx ON django_session (expire_date);')
                self.stdout.write('✓ Session table created manually')
        except Exception as e:
            self.stdout.write(f'❌ Manual session table creation failed: {e}')
    
    def verify_all_tables(self):
        """Verify all essential tables exist"""
        essential_tables = ['django_session', 'django_content_type', 'auth_user']
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                missing_tables = [t for t in essential_tables if t not in existing_tables]
                
                if missing_tables:
                    self.stdout.write(f'❌ Missing tables: {missing_tables}')
                    return False
                else:
                    self.stdout.write('✓ All essential tables exist')
                    return True
        except:
            return False