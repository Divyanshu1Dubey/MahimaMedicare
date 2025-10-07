from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
from doctor.models import testCart, testOrder, Prescription_test
from hospital_admin.models import Test_Information
from decimal import Decimal


def get_lab_test_vat():
    """Get lab test VAT amount from settings"""
    return getattr(settings, 'LAB_TEST_VAT_AMOUNT', 20.00)


@login_required
def enhanced_lab_test_booking(request):
    """Enhanced lab test booking with home collection option"""
    try:
        # Get user's current cart items
        cart_items = testCart.objects.filter(user=request.user, purchased=False)
        
        if not cart_items.exists():
            messages.info(request, 'No tests found in your cart. Please add tests first.')
            return redirect('patient-dashboard')

        # Calculate pricing
        tests_total = sum(item.total for item in cart_items)
        vat_amount = get_lab_test_vat()
        total_amount = tests_total + vat_amount

        # Get today's date for minimum date validation
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        context = {
            'cart_items': cart_items,
            'tests_total': tests_total,
            'vat_amount': vat_amount,
            'total_amount': total_amount,
            'VAT_AMOUNT': vat_amount,
            'today': tomorrow.isoformat(),  # Minimum date (tomorrow)
        }

        if request.method == 'POST':
            return process_enhanced_test_booking(request, cart_items, tests_total, vat_amount)

        return render(request, 'lab-test-booking.html', context)

    except Exception as e:
        messages.error(request, f'Error loading lab test booking: {str(e)}')
        return redirect('patient-dashboard')


def process_enhanced_test_booking(request, cart_items, tests_total, vat_amount):
    """Process the enhanced test booking with home collection"""
    try:
        # Get form data
        collection_type = request.POST.get('collection_type', 'center')
        payment_method = request.POST.get('payment_method', 'online')
        
        # Home collection specific fields
        preferred_collection_date = request.POST.get('preferred_collection_date')
        preferred_collection_time = request.POST.get('preferred_collection_time')
        collection_address = request.POST.get('collection_address', '').strip()
        
        # Validate home collection fields if applicable
        if collection_type == 'home':
            if not all([preferred_collection_date, preferred_collection_time, collection_address]):
                messages.error(request, 'All home collection details are required.')
                return redirect('enhanced-lab-test-booking')
            
            # Validate collection date (must be at least tomorrow)
            try:
                collection_date = datetime.strptime(preferred_collection_date, '%Y-%m-%d').date()
                tomorrow = timezone.now().date() + timedelta(days=1)
                if collection_date < tomorrow:
                    messages.error(request, 'Collection date must be at least tomorrow.')
                    return redirect('enhanced-lab-test-booking')
            except ValueError:
                messages.error(request, 'Invalid collection date format.')
                return redirect('enhanced-lab-test-booking')

        # Calculate total with home collection fee
        home_collection_fee = Decimal('99.00') if collection_type == 'home' else Decimal('0.00')
        final_total = Decimal(str(tests_total)) + home_collection_fee + Decimal(str(vat_amount))

        # Create test order
        test_order = testOrder.objects.create(
            user=request.user,
            payment_status='pending',
            collection_type=collection_type,
            home_collection_fee=home_collection_fee,
            collection_address=collection_address if collection_type == 'home' else '',
            preferred_collection_date=preferred_collection_date if collection_type == 'home' else None,
            preferred_collection_time=preferred_collection_time if collection_type == 'home' else None,
            collection_status='pending'
        )

        # Add cart items to order
        for cart_item in cart_items:
            test_order.orderitems.add(cart_item)

        test_order.save()

        # Handle payment method
        if payment_method == 'cod':
            # Cash on Delivery - mark as ordered but unpaid
            test_order.payment_status = 'cod_pending'
            test_order.ordered = True
            test_order.save()

            # Update cart items as purchased
            cart_items.update(purchased=True)

            # Set appropriate collection status
            if collection_type == 'home':
                test_order.collection_status = 'scheduled'
                success_message = f'Lab test booking successful! Home collection scheduled for {preferred_collection_date}. Payment: ₹{final_total} (Cash on Delivery)'
            else:
                test_order.collection_status = 'pending'
                success_message = f'Lab test booking successful! Please visit our center for sample collection. Payment: ₹{final_total} (Cash on Delivery)'
            
            test_order.save()
            messages.success(request, success_message)
            return redirect('patient-lab-tests')

        else:
            # Online payment - redirect to payment gateway
            return redirect('lab-test-payment', test_order_id=test_order.id)

    except Exception as e:
        messages.error(request, f'Error processing booking: {str(e)}')
        return redirect('enhanced-lab-test-booking')


@login_required
def add_test_to_cart(request):
    """Add test to cart for enhanced booking"""
    if request.method == 'POST':
        try:
            test_id = request.POST.get('test_id')
            
            # Get test information
            test_info = get_object_or_404(Test_Information, test_id=test_id)
            
            # Create prescription test entry
            prescription_test = Prescription_test.objects.create(
                test_name=test_info.test_name,
                test_info_price=test_info.test_price,
                test_info_id=test_info.test_id,
                test_status='prescribed'
            )
            
            # Check if test already in cart
            existing_cart_item = testCart.objects.filter(
                user=request.user,
                item=prescription_test,
                purchased=False
            ).first()
            
            if existing_cart_item:
                messages.info(request, f'{test_info.test_name} is already in your cart.')
            else:
                # Add to cart
                cart_item = testCart.objects.create(
                    user=request.user,
                    item=prescription_test,
                    purchased=False
                )
                messages.success(request, f'{test_info.test_name} added to cart successfully.')
            
            return redirect('enhanced-lab-test-booking')
            
        except Exception as e:
            messages.error(request, f'Error adding test to cart: {str(e)}')
            return redirect('patient-dashboard')
    
    return redirect('patient-dashboard')


@login_required
def remove_test_from_cart(request, cart_item_id):
    """Remove test from cart"""
    try:
        cart_item = get_object_or_404(testCart, id=cart_item_id, user=request.user, purchased=False)
        test_name = cart_item.item.test_name
        
        # Delete the prescription test and cart item
        prescription_test = cart_item.item
        cart_item.delete()
        prescription_test.delete()
        
        messages.success(request, f'{test_name} removed from cart.')
        
    except Exception as e:
        messages.error(request, f'Error removing test: {str(e)}')
    
    return redirect('enhanced-lab-test-booking')


@login_required
def lab_test_catalog(request):
    """Display available lab tests for selection"""
    try:
        # Get all available tests
        available_tests = Test_Information.objects.all().order_by('test_name')
        
        # Get user's current cart items
        cart_items = testCart.objects.filter(user=request.user, purchased=False)
        cart_test_names = [item.item.test_name for item in cart_items]
        
        context = {
            'available_tests': available_tests,
            'cart_test_names': cart_test_names,
            'cart_count': cart_items.count(),
        }
        
        return render(request, 'lab-test-catalog.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading test catalog: {str(e)}')
        return redirect('patient-dashboard')