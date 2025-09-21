"""
Database backup management command for Mahima Medicare
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail
import os
import shutil
import datetime
import zipfile
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create a backup of the database and media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='store_true',
            help='Send backup notification email',
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress backup files',
        )

    def handle(self, *args, **options):
        try:
            # Create backup directory
            backup_dir = getattr(settings, 'BACKUP_ROOT', os.path.join(settings.BASE_DIR, 'backups'))
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create timestamped backup folder
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_folder = os.path.join(backup_dir, f'backup_{timestamp}')
            os.makedirs(backup_folder, exist_ok=True)
            
            # Backup database
            db_backup_path = self.backup_database(backup_folder)
            
            # Backup media files
            media_backup_path = self.backup_media_files(backup_folder)
            
            # Compress if requested
            if options['compress']:
                zip_path = self.compress_backup(backup_folder)
                self.stdout.write(
                    self.style.SUCCESS(f'Compressed backup created: {zip_path}')
                )
            
            # Send email notification if requested
            if options['email']:
                self.send_backup_notification(timestamp, backup_folder)
            
            # Clean old backups (keep last 7 days)
            self.cleanup_old_backups(backup_dir)
            
            self.stdout.write(
                self.style.SUCCESS(f'Backup completed successfully: {backup_folder}')
            )
            
        except Exception as e:
            logger.error(f'Backup failed: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Backup failed: {str(e)}')
            )

    def backup_database(self, backup_folder):
        """Backup the SQLite database"""
        db_path = settings.DATABASES['default']['NAME']
        backup_db_path = os.path.join(backup_folder, 'database.sqlite3')
        
        shutil.copy2(db_path, backup_db_path)
        self.stdout.write('Database backup completed')
        return backup_db_path

    def backup_media_files(self, backup_folder):
        """Backup media files"""
        media_root = settings.MEDIA_ROOT
        backup_media_path = os.path.join(backup_folder, 'media')
        
        if os.path.exists(media_root):
            shutil.copytree(media_root, backup_media_path)
            self.stdout.write('Media files backup completed')
        else:
            self.stdout.write('No media files to backup')
        
        return backup_media_path

    def compress_backup(self, backup_folder):
        """Compress backup folder"""
        zip_path = f'{backup_folder}.zip'
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_folder)
                    zipf.write(file_path, arcname)
        
        # Remove uncompressed folder
        shutil.rmtree(backup_folder)
        return zip_path

    def cleanup_old_backups(self, backup_dir):
        """Remove backups older than 7 days"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=7)
        
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            if os.path.isdir(item_path) or item.endswith('.zip'):
                # Extract timestamp from filename
                try:
                    if item.startswith('backup_'):
                        timestamp_str = item.replace('backup_', '').replace('.zip', '')
                        item_date = datetime.datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        
                        if item_date < cutoff_date:
                            if os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                            else:
                                os.remove(item_path)
                            self.stdout.write(f'Removed old backup: {item}')
                except ValueError:
                    continue

    def send_backup_notification(self, timestamp, backup_folder):
        """Send backup notification email"""
        try:
            subject = f'Mahima Medicare - Database Backup Completed ({timestamp})'
            message = f'''
            Database backup has been completed successfully.
            
            Backup Details:
            - Timestamp: {timestamp}
            - Location: {backup_folder}
            - Database: Backed up
            - Media Files: Backed up
            
            This is an automated message from Mahima Medicare Healthcare System.
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ['admin@mahimamedicare.com'],  # Update with actual admin email
                fail_silently=False,
            )
            
            self.stdout.write('Backup notification email sent')
            
        except Exception as e:
            logger.error(f'Failed to send backup notification: {str(e)}')
            self.stdout.write(f'Failed to send notification email: {str(e)}')
