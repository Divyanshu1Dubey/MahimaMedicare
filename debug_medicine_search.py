#!/usr/bin/env python
"""
Medicine Search Debug Script
Check if medicines are properly accessible for search
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from pharmacy.models import Medicine

def debug_medicine_search():
    print("=" * 50)
    print("MEDICINE SEARCH DEBUG")
    print("=" * 50)
    
    # Get all medicines
    medicines = Medicine.objects.all()
    print(f"Total medicines: {medicines.count()}")
    
    if medicines.count() > 0:
        print("\nAvailable medicines for search:")
        for med in medicines:
            print(f"ID: {med.serial_number}")
            print(f"Name: {med.name}")
            print(f"Price: ₹{med.price}")
            print(f"Stock: {med.quantity}")
            print(f"Composition: {getattr(med, 'composition', 'N/A')}")
            print("-" * 30)
    
    # Test search functionality
    search_terms = ['para', 'flex', 'test', 'ibu']
    
    print(f"\nTesting search with terms: {search_terms}")
    for term in search_terms:
        results = Medicine.objects.filter(name__icontains=term, quantity__gt=0)
        print(f"'{term}': {results.count()} results")
        for med in results:
            print(f"  - {med.name} (₹{med.price})")

if __name__ == "__main__":
    debug_medicine_search()