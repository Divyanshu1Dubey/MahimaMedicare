#!/usr/bin/env python
"""
Data import script to restore essential data after deployment
"""
import os
import sys
import django
import json
from django.core.management import call_command

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from django.core import serializers

def import_data(backup_dir):
    """Import essential data from JSON files"""

    if not os.path.exists(backup_dir):
        print(f"Backup directory '{backup_dir}' not found!")
        return

    try:
        # Import in correct order to handle dependencies
        files_to_import = [
            'departments.json',
            'medicine_categories.json',
            'medicines.json',
            'doctors.json'
        ]

        for filename in files_to_import:
            filepath = os.path.join(backup_dir, filename)
            if os.path.exists(filepath):
                print(f"Importing {filename}...")
                with open(filepath, 'r') as f:
                    data = f.read()
                    for obj in serializers.deserialize('json', data):
                        obj.save()
                print(f"Successfully imported {filename}")
            else:
                print(f"Warning: {filename} not found in backup directory")

        print("\nAll data imported successfully!")

    except Exception as e:
        print(f"Error importing data: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        backup_dir = sys.argv[1]
    else:
        # Find the most recent backup directory
        backup_dirs = [d for d in os.listdir('.') if d.startswith('data_backup_')]
        if backup_dirs:
            backup_dir = sorted(backup_dirs)[-1]
            print(f"Using most recent backup: {backup_dir}")
        else:
            print("No backup directory found. Please specify backup directory as argument.")
            sys.exit(1)

    import_data(backup_dir)
