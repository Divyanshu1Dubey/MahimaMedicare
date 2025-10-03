"""
AJAX API views for pharmacy features
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from .hsn_utils import auto_fetch_hsn_code, get_composition_suggestions
from .models import Medicine

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def fetch_hsn_code_ajax(request):
    """
    AJAX endpoint to fetch HSN code for a medicine
    """
    try:
        data = json.loads(request.body)
        medicine_name = data.get('name', '').strip()
        composition = data.get('composition', '').strip()
        category = data.get('category', '').strip()
        
        if not medicine_name:
            return JsonResponse({
                'success': False,
                'error': 'Medicine name is required'
            })
        
        # Fetch HSN code
        hsn_result = auto_fetch_hsn_code(
            medicine_name=medicine_name,
            composition=composition,
            category=category
        )
        
        return JsonResponse({
            'success': True,
            'hsn_code': hsn_result.get('hsn_code'),
            'source': hsn_result.get('source'),
            'confidence': hsn_result.get('confidence'),
            'suggestions': hsn_result.get('suggestions', [])
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def get_composition_suggestions_ajax(request):
    """
    AJAX endpoint to get composition suggestions for a medicine
    """
    try:
        data = json.loads(request.body)
        medicine_name = data.get('name', '').strip()
        
        if not medicine_name:
            return JsonResponse({
                'success': False,
                'error': 'Medicine name is required'
            })
        
        suggestions = get_composition_suggestions(medicine_name)
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def search_existing_medicines(request):
    """
    AJAX endpoint to search existing medicines for composition reference
    """
    try:
        query = request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Query must be at least 2 characters'
            })
        
        # Search in existing medicines
        medicines = Medicine.objects.filter(
            name__icontains=query
        )[:10]  # Limit to 10 results
        
        results = []
        for medicine in medicines:
            results.append({
                'name': medicine.name,
                'composition': medicine.composition or '',
                'hsn_code': medicine.hsn_code or '',
                'category': medicine.medicine_category or ''
            })
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })