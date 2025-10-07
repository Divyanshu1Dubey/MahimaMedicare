#!/usr/bin/env python
"""
Data export script to backup essential data before deployment
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from django.core import serializers
from pharmacy.models import Medicine, MedicineCategory
from doctor.models import Doctor, Department
from hospital.models import Patient

def export_data():
    """Export essential data to JSON files"""

    # Create backup directory
    backup_dir = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)

    try:
        # Export medicines
        medicines = Medicine.objects.all()
        with open(f"{backup_dir}/medicines.json", 'w') as f:
            serialized_data = serializers.serialize('json', medicines)
            f.write(serialized_data)
        print(f"Exported {medicines.count()} medicines")

        # Export medicine categories
        categories = MedicineCategory.objects.all()
        with open(f"{backup_dir}/medicine_categories.json", 'w') as f:
            serialized_data = serializers.serialize('json', categories)
            f.write(serialized_data)
        print(f"Exported {categories.count()} medicine categories")

        # Export doctors
        doctors = Doctor.objects.all()
        with open(f"{backup_dir}/doctors.json", 'w') as f:
            serialized_data = serializers.serialize('json', doctors)
            f.write(serialized_data)
        print(f"Exported {doctors.count()} doctors")

        # Export departments
        departments = Department.objects.all()
        with open(f"{backup_dir}/departments.json", 'w') as f:
            serialized_data = serializers.serialize('json', departments)
            f.write(serialized_data)
        print(f"Exported {departments.count()} departments")

        print(f"\nAll data exported successfully to '{backup_dir}' directory")
        print("Upload this directory to your server before running migrations")

    except Exception as e:
        print(f"Error exporting data: {e}")

if __name__ == "__main__":
    export_data()
