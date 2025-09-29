"""
Healthstack Django App Initialization
Ensures database is properly set up on startup for production deployments
"""

import os
import django
from django.conf import settings

def initialize_database():
    """
    Aggressive database initialization on app startup
    This ensures all Django tables exist when the app starts
    """
    if os.environ.get('RUN_DB_INIT', 'True').lower() == 'true':
        try:
            # Only run if Django is properly configured
            if hasattr(settings, 'DATABASES'):
                from django.core.management import execute_from_command_line
                from django.db import connection
                from django.core.management.commands.migrate import Command as MigrateCommand
                
                print("🗄️ AUTO-INITIALIZING DATABASE ON STARTUP...")
                
                # Method 1: Try migrations
                try:
                    execute_from_command_line(['manage.py', 'migrate', '--verbosity=0'])
                    print("✓ Migrations completed")
                except Exception as e:
                    print(f"Migration warning: {e}")
                
                # Method 2: Ensure core tables exist with raw SQL
                try:
                    with connection.cursor() as cursor:
                        # Create django_session table if not exists
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS django_session (
                                session_key varchar(40) PRIMARY KEY,
                                session_data text NOT NULL,
                                expire_date datetime NOT NULL
                            );
                        """)
                        
                        # Create django_content_type table if not exists
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS django_content_type (
                                id integer PRIMARY KEY AUTOINCREMENT,
                                app_label varchar(100) NOT NULL,
                                model varchar(100) NOT NULL,
                                UNIQUE(app_label, model)
                            );
                        """)
                        
                        # Create auth_permission table if not exists
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS auth_permission (
                                id integer PRIMARY KEY AUTOINCREMENT,
                                content_type_id integer NOT NULL,
                                codename varchar(100) NOT NULL,
                                name varchar(255) NOT NULL,
                                UNIQUE(content_type_id, codename)
                            );
                        """)
                        
                        print("✓ Core Django tables ensured")
                        
                        # Verify session table exists
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_session';")
                        if cursor.fetchone():
                            print("✅ Session table confirmed on startup!")
                        else:
                            print("❌ Session table still missing!")
                            
                except Exception as e:
                    print(f"Raw SQL setup warning: {e}")
                
                print("🎉 Database initialization completed on startup!")
                    
        except Exception as e:
            print(f"Startup DB init error: {e}")

# Only initialize database in production or when specifically requested
if os.environ.get('DJANGO_SETTINGS_MODULE') and ('render' in os.environ.get('PATH', '').lower() or os.environ.get('FORCE_DB_INIT')):
    # Import Django first
    try:
        django.setup()
        initialize_database()
    except:
        # If Django isn't ready yet, we'll handle it in middleware
        pass