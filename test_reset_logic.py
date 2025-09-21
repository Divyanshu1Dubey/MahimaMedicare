#!/usr/bin/env python
"""
Test script to verify the Unit Qty reset functionality
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from pharmacy.models import Medicine
from pharmacy.utils import check_and_reset_medicine_quantity


def test_reset_logic():
    """Test the reset functionality"""
    print("Testing Unit Qty reset logic...")
    
    # Create or get a test medicine
    test_medicine, created = Medicine.objects.get_or_create(
        name="Test Medicine",
        defaults={
            'quantity': 0,  # Unit Qty at 0
            'stock_quantity': 5,  # Stock Qty available
            'price': 100,
            'medicine_type': 'tablets'
        }
    )
    
    print(f"Initial state - Unit Qty: {test_medicine.quantity}, Stock Qty: {test_medicine.stock_quantity}")
    
    # Test the reset functionality
    was_reset, new_quantity, new_stock = check_and_reset_medicine_quantity(test_medicine)
    
    print(f"After reset - Unit Qty: {new_quantity}, Stock Qty: {new_stock}")
    print(f"Reset performed: {was_reset}")
    
    # Verify the reset worked correctly
    if new_quantity == 50 and new_stock == 4:
        print("✅ Reset logic working correctly!")
        return True
    else:
        print("❌ Reset logic failed!")
        return False


if __name__ == "__main__":
    test_reset_logic()
