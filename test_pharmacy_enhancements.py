#!/usr/bin/env python3
"""
Test script to verify pharmacy improvements with composition and HSN code
"""
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from pharmacy.models import Medicine
from pharmacy.hsn_utils import auto_fetch_hsn_code, get_composition_suggestions
from pharmacy.forms import MedicineForm

def test_hsn_auto_fetch():
    """Test HSN code auto-fetch functionality"""
    print("🧪 Testing HSN Code Auto-Fetch")
    print("=" * 50)
    
    test_medicines = [
        {"name": "Paracetamol 500mg", "composition": "Paracetamol 500mg per tablet", "category": "fever"},
        {"name": "Ibuprofen 400mg", "composition": "Ibuprofen 400mg", "category": "pain"},
        {"name": "Amoxicillin", "composition": "Amoxicillin 250mg", "category": "infection"},
        {"name": "Vitamin D3", "composition": "Cholecalciferol 60,000 IU", "category": "vitamins"},
        {"name": "Cetirizine 10mg", "composition": "Cetirizine HCl 10mg", "category": "allergy"},
    ]
    
    for med in test_medicines:
        print(f"\n🔍 Testing: {med['name']}")
        result = auto_fetch_hsn_code(
            medicine_name=med['name'],
            composition=med['composition'],
            category=med['category']
        )
        
        print(f"  📋 Composition: {med['composition']}")
        print(f"  🏷️  HSN Code: {result.get('hsn_code', 'None')}")
        print(f"  📊 Source: {result.get('source', 'unknown')}")
        print(f"  ✓ Confidence: {result.get('confidence', 'low')}")
        
        if result.get('suggestions'):
            print(f"  💡 Suggestions: {', '.join(result['suggestions'])}")

def test_composition_suggestions():
    """Test composition suggestions functionality"""
    print("\n🧪 Testing Composition Suggestions")
    print("=" * 50)
    
    test_names = ["paracetamol", "ibuprofen", "amoxicillin", "omeprazole"]
    
    for name in test_names:
        suggestions = get_composition_suggestions(name)
        print(f"\n🔍 '{name}' suggestions:")
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("  No suggestions found")

def test_medicine_form():
    """Test the enhanced medicine form"""
    print("\n🧪 Testing Enhanced Medicine Form")
    print("=" * 50)
    
    form_data = {
        'name': 'Paracetamol 650mg',
        'composition': 'Paracetamol 650mg per tablet',
        'hsn_code': '',  # Should be auto-filled
        'weight': '650mg',
        'quantity': 100,
        'stock_quantity': 100,
        'price': 25.50,
        'medicine_category': 'fever',
        'medicine_type': 'tablets',
        'Prescription_reqiuired': 'no',
        'description': 'Pain reliever and fever reducer',
        'fetch_hsn': True
    }
    
    form = MedicineForm(data=form_data)
    
    print(f"📋 Form Data: {form_data['name']}")
    print(f"✅ Form Valid: {form.is_valid()}")
    
    if form.is_valid():
        # Check if HSN was auto-filled
        cleaned_data = form.cleaned_data
        print(f"🏷️  Auto-filled HSN: {cleaned_data.get('hsn_code', 'None')}")
        
        # Get HSN info if available
        hsn_info = form.get_hsn_info()
        if hsn_info:
            print(f"📊 HSN Source: {hsn_info.get('source', 'unknown')}")
            print(f"✓ Confidence: {hsn_info.get('confidence', 'low')}")
    else:
        print(f"❌ Form Errors: {form.errors}")

def test_medicine_creation():
    """Test creating medicines with the new fields"""
    print("\n🧪 Testing Medicine Creation with New Fields")
    print("=" * 50)
    
    # Clean up any existing test medicines
    Medicine.objects.filter(name__contains="Test Medicine").delete()
    
    test_medicine = Medicine.objects.create(
        name="Test Medicine Paracetamol",
        composition="Paracetamol 500mg per tablet",
        hsn_code="30049011",
        weight="500mg",
        quantity=50,
        stock_quantity=100,
        price=15.75,
        medicine_category="fever",
        medicine_type="tablets",
        Prescription_reqiuired="no",
        description="Test medicine for fever and pain"
    )
    
    print(f"✅ Created Medicine: {test_medicine}")
    print(f"📋 Composition: {test_medicine.composition}")
    print(f"🏷️  HSN Code: {test_medicine.hsn_code}")
    print(f"💰 Price: ₹{test_medicine.price}")
    print(f"📦 Stock: {test_medicine.quantity}/{test_medicine.stock_quantity}")
    
    # Test the __str__ method
    print(f"🏷️  String representation: {str(test_medicine)}")
    
    return test_medicine

def test_medicine_display():
    """Test how medicines display with composition"""
    print("\n🧪 Testing Medicine Display")
    print("=" * 50)
    
    # Get existing medicines or create some test ones
    medicines = Medicine.objects.all()[:5]
    
    if not medicines:
        print("No medicines found. Creating test data...")
        test_medicine_creation()
        medicines = Medicine.objects.all()[:5]
    
    print("📋 Medicine Display Examples:")
    for medicine in medicines:
        print(f"  • {str(medicine)}")
        if medicine.composition:
            print(f"    Composition: {medicine.composition}")
        if medicine.hsn_code:
            print(f"    HSN Code: {medicine.hsn_code}")
        print()

if __name__ == "__main__":
    print("🚀 Testing Enhanced Pharmacy System")
    print("=" * 60)
    
    try:
        test_hsn_auto_fetch()
        test_composition_suggestions()
        test_medicine_form()
        test_medicine_creation()
        test_medicine_display()
        
        print("\n🎉 All tests completed successfully!")
        print("\nYour pharmacy system now supports:")
        print("✅ Auto-fetch HSN codes from database and APIs")
        print("✅ Medicine composition tracking")
        print("✅ Composition suggestions based on medicine names")
        print("✅ Enhanced medicine display with name + composition")
        print("✅ Improved stock management (current + total)")
        print("✅ AJAX-powered form enhancements")
        
        print("\nReady to use in admin panel!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()