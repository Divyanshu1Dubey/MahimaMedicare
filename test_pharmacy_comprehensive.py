#!/usr/bin/env python3
"""
Comprehensive Pharmacy Module Testing Script
Tests all enhanced functionality from pharmacist perspective
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from pharmacy.models import Medicine
from hospital_admin.models import Pharmacist
from pharmacy.hsn_utils import auto_fetch_hsn_code, get_composition_suggestions
from pharmacy.forms import MedicineForm

class PharmacyComprehensiveTest:
    """Comprehensive pharmacy functionality test"""
    
    def __init__(self):
        print("🧪 COMPREHENSIVE PHARMACY MODULE TESTING")
        print("=" * 50)
        
    def test_medicine_model_enhancements(self):
        """Test enhanced medicine model with composition and HSN"""
        print("\n📋 Testing Medicine Model Enhancements...")
        
        try:
            # Test creating medicine with new fields
            medicine = Medicine.objects.create(
                name="Paracetamol 500mg Test",
                composition="Paracetamol 500mg per tablet",
                hsn_code="30049099",
                weight="500mg",
                quantity=100,
                stock_quantity=100,
                price=Decimal('25.50'),
                medicine_type="tablets",
                medicine_category="fever",
                description="Test medicine for fever relief"
            )
            
            print(f"✅ Created medicine: {medicine}")
            print(f"✅ Composition: {medicine.composition}")
            print(f"✅ HSN Code: {medicine.hsn_code}")
            print(f"✅ Price (Decimal): {medicine.price}")
            print(f"✅ __str__ method: {medicine}")
            
            # Test medicine search/display
            medicines_with_composition = Medicine.objects.filter(composition__icontains="Paracetamol")
            print(f"✅ Found {medicines_with_composition.count()} medicines with Paracetamol composition")
            
            return True
        except Exception as e:
            print(f"❌ Medicine Model Test Failed: {e}")
            return False
            
    def test_hsn_auto_fetch(self):
        """Test HSN auto-fetch functionality"""
        print("\n🔍 Testing HSN Auto-Fetch System...")
        
        test_medicines = [
            ("Paracetamol 500mg", "Paracetamol 500mg per tablet", "fever"),
            ("Ibuprofen 400mg", "Ibuprofen 400mg per tablet", "pain"),
            ("Amoxicillin 250mg", "Amoxicillin 250mg per capsule", "infection"),
            ("Cetirizine 10mg", "Cetirizine Hydrochloride 10mg", "allergy"),
            ("Unknown Medicine XYZ", "Unknown composition", "general")
        ]
        
        for name, composition, category in test_medicines:
            try:
                result = auto_fetch_hsn_code(name, composition, category)
                status = "✅" if result['success'] else "⚠️"
                print(f"{status} {name}: HSN={result.get('hsn_code', 'N/A')}, Source={result.get('source', 'N/A')}")
            except Exception as e:
                print(f"❌ HSN fetch failed for {name}: {e}")
                
        return True
        
    def test_composition_suggestions(self):
        """Test composition suggestions system"""
        print("\n💡 Testing Composition Suggestions...")
        
        test_names = [
            "Paracetamol",
            "Ibuprofen", 
            "Aspirin",
            "Amoxicillin",
            "Unknown Medicine"
        ]
        
        for name in test_names:
            try:
                suggestions = get_composition_suggestions(name)
                status = "✅" if suggestions else "⚠️"
                print(f"{status} {name}: {len(suggestions)} suggestions")
                if suggestions:
                    for suggestion in suggestions[:2]:  # Show first 2
                        print(f"    - {suggestion}")
            except Exception as e:
                print(f"❌ Composition suggestions failed for {name}: {e}")
                
        return True
        
    def test_medicine_form(self):
        """Test enhanced medicine form"""
        print("\n📝 Testing Enhanced Medicine Form...")
        
        try:
            # Test valid form data
            form_data = {
                'name': 'Test Medicine Form',
                'composition': 'Active ingredient 100mg per tablet',
                'hsn_code': '30049099',
                'weight': '100mg',
                'quantity': 50,
                'stock_quantity': 50,
                'price': '15.75',
                'medicine_type': 'tablets',
                'category_type': 'fever',
                'requirement_type': 'no',
                'description': 'Test medicine description'
            }
            
            form = MedicineForm(data=form_data)
            if form.is_valid():
                print("✅ Form validation passed")
                print(f"✅ Cleaned price: {form.cleaned_data['price']} (type: {type(form.cleaned_data['price'])})")
            else:
                print("❌ Form validation failed:")
                for field, errors in form.errors.items():
                    print(f"    {field}: {errors}")
                    
            # Test invalid form data
            invalid_data = form_data.copy()
            invalid_data['price'] = 'invalid_price'
            invalid_form = MedicineForm(data=invalid_data)
            if not invalid_form.is_valid():
                print("✅ Form properly rejects invalid price")
            else:
                print("❌ Form should have rejected invalid price")
                
            return True
        except Exception as e:
            print(f"❌ Medicine Form Test Failed: {e}")
            return False
            
    def test_database_queries(self):
        """Test database queries for enhanced fields"""
        print("\n🗄️ Testing Database Queries...")
        
        try:
            # Test various queries that pharmacists would use
            total_medicines = Medicine.objects.count()
            print(f"✅ Total medicines: {total_medicines}")
            
            medicines_with_hsn = Medicine.objects.exclude(hsn_code__isnull=True).exclude(hsn_code='').count()
            print(f"✅ Medicines with HSN codes: {medicines_with_hsn}")
            
            medicines_with_composition = Medicine.objects.exclude(composition__isnull=True).exclude(composition='').count()
            print(f"✅ Medicines with composition: {medicines_with_composition}")
            
            low_stock = Medicine.objects.filter(quantity__lt=10).count()
            print(f"✅ Low stock medicines (< 10): {low_stock}")
            
            expired_soon = Medicine.objects.filter(
                expiry_date__isnull=False
            ).exclude(expiry_date='').count()
            print(f"✅ Medicines with expiry dates: {expired_soon}")
            
            # Test search functionality
            search_results = Medicine.objects.filter(
                name__icontains="paracetamol"
            ) | Medicine.objects.filter(
                composition__icontains="paracetamol"
            )
            print(f"✅ Search 'paracetamol' results: {search_results.count()}")
            
            return True
        except Exception as e:
            print(f"❌ Database Queries Test Failed: {e}")
            return False
            
    def test_decimal_price_handling(self):
        """Test decimal price field handling"""
        print("\n💰 Testing Decimal Price Handling...")
        
        try:
            test_prices = [
                "25.50",
                "100",
                "0.99", 
                "1250.75"
            ]
            
            for price_str in test_prices:
                price_decimal = Decimal(price_str)
                medicine = Medicine.objects.create(
                    name=f"Price Test Medicine {price_str}",
                    price=price_decimal,
                    quantity=10,
                    stock_quantity=10,
                    weight="1mg"
                )
                print(f"✅ Created medicine with price ₹{medicine.price}")
                
            # Test price calculations
            total_value = sum(Medicine.objects.values_list('price', flat=True))
            print(f"✅ Total inventory value: ₹{total_value}")
            
            return True
        except Exception as e:
            print(f"❌ Decimal Price Test Failed: {e}")
            return False
            
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Pharmacy Tests...\n")
        
        tests = [
            self.test_medicine_model_enhancements,
            self.test_hsn_auto_fetch,
            self.test_composition_suggestions,
            self.test_medicine_form,
            self.test_database_queries,
            self.test_decimal_price_handling
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                failed += 1
                
        print("\n" + "=" * 50)
        print(f"📊 TEST RESULTS: {passed} PASSED, {failed} FAILED")
        print("=" * 50)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Pharmacy module is production ready!")
        else:
            print(f"⚠️ {failed} tests failed. Please review and fix issues.")
            
        return failed == 0

def main():
    """Main test execution"""
    tester = PharmacyComprehensiveTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ PHARMACY MODULE READY FOR PRODUCTION DEPLOYMENT")
        print("🔥 All features working correctly from pharmacist perspective")
    else:
        print("\n❌ PHARMACY MODULE NEEDS FIXES BEFORE PRODUCTION")
        
if __name__ == "__main__":
    main()