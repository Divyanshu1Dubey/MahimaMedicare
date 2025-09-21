from django.core.exceptions import ValidationError
from django.db.models import Q


def reset_unit_quantity_and_update_stock(medicine):
    """
    Reset Unit Qty to 50 and reduce Stock Qty by 1 when Unit Qty hits 0
    
    Args:
        medicine: Medicine instance
        
    Returns:
        bool: True if reset was successful, False otherwise
    """
    if medicine.quantity <= 0:
        # Check if we have enough stock to deduct
        if medicine.stock_quantity >= 1:
            medicine.quantity = 50
            medicine.stock_quantity -= 1
            medicine.save()
            return True
        else:
            # Not enough stock to reset
            raise ValidationError(
                f"Cannot reset {medicine.name} - insufficient stock quantity. "
                f"Stock: {medicine.stock_quantity}, required: 1"
            )
    return False


def check_and_reset_medicine_quantity(medicine):
    """
    Check if medicine needs reset and perform the reset
    
    Args:
        medicine: Medicine instance
        
    Returns:
        tuple: (was_reset, new_quantity, new_stock_quantity)
    """
    if medicine.quantity <= 0:
        old_quantity = medicine.quantity
        old_stock = medicine.stock_quantity
        
        if reset_unit_quantity_and_update_stock(medicine):
            return True, medicine.quantity, medicine.stock_quantity
    
    return False, medicine.quantity, medicine.stock_quantity


def searchMedicines(request):
    """
    Search medicines based on query parameters
    
    Args:
        request: HTTP request object
        
    Returns:
        tuple: (medicines queryset, search_query string)
    """
    from .models import Medicine
    
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    medicines = Medicine.objects.all()
    
    if search_query:
        medicines = medicines.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(medicine_category__icontains=search_query) |
            Q(medicine_type__icontains=search_query)
        )
    
    if category_filter:
        medicines = medicines.filter(medicine_category__iexact=category_filter)
    
    return medicines, search_query