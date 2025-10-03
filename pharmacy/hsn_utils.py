"""
HSN Code Auto-Fetch Utilities for Medicines
"""
import requests
import json
import re
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Common medicine HSN codes database (as fallback)
MEDICINE_HSN_CODES = {
    # Common medicines and their HSN codes
    'paracetamol': '30049011',
    'acetaminophen': '30049011', 
    'aspirin': '30049013',
    'acetylsalicylic acid': '30049013',
    'ibuprofen': '30049019',
    'diclofenac': '30049019',
    'amoxicillin': '30049041',
    'azithromycin': '30049043',
    'ciprofloxacin': '30049045',
    'metformin': '30049051',
    'amlodipine': '30049061',
    'atenolol': '30049063',
    'losartan': '30049065',
    'omeprazole': '30049071',
    'pantoprazole': '30049071',
    'ranitidine': '30049073',
    'cetirizine': '30049081',
    'loratadine': '30049081',
    'dextromethorphan': '30049091',
    'salbutamol': '30049093',
    'insulin': '30049095',
    'multivitamin': '30049097',
    'vitamin d': '30049097',
    'vitamin c': '30049097',
    'calcium': '30049097',
    'iron': '30049097',
    'zinc': '30049097',
}

# Medicine category to HSN mapping
CATEGORY_HSN_MAPPING = {
    'fever': '30049011',  # Paracetamol family
    'pain': '30049019',   # NSAIDs
    'cough': '30049091',  # Cough syrups
    'cold': '30049081',   # Antihistamines
    'flu': '30049081',    # Antihistamines
    'diabetes': '30049051', # Antidiabetic
    'bloodpressure': '30049061', # Antihypertensives
    'heartdisease': '30049061',  # Cardiovascular
    'vitamins': '30049097',      # Vitamins/minerals
    'digestivehealth': '30049071', # Antacids
    'allergy': '30049081',       # Antihistamines
    'asthma': '30049093',        # Bronchodilators
    'infection': '30049041',     # Antibiotics
    'eye': '30049099',           # Ophthalmic preparations
    'ear': '30049099',           # Otic preparations
    'skin': '30049099',          # Topical preparations
}

def clean_medicine_name(name: str) -> str:
    """Clean medicine name for better matching"""
    if not name:
        return ""
    
    # Convert to lowercase and remove common suffixes
    cleaned = name.lower().strip()
    
    # Remove dosage information (like 500mg, 10ml, etc.)
    cleaned = re.sub(r'\d+\s*(mg|ml|mcg|g|gm|tab|caps|capsule|tablet|syrup)', '', cleaned)
    
    # Remove brand name indicators
    cleaned = re.sub(r'\(.*?\)', '', cleaned)  # Remove text in parentheses
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Normalize spaces
    
    return cleaned

def extract_active_ingredient(medicine_name: str, composition: str = None) -> str:
    """Extract the main active ingredient from medicine name or composition"""
    # If composition is available, try to extract from there
    if composition:
        # Look for common patterns like "Paracetamol 500mg"
        match = re.search(r'([a-zA-Z\s]+?)(?:\s*\d+\s*(?:mg|mcg|g|%|ml))', composition.lower())
        if match:
            return match.group(1).strip()
    
    # Extract from medicine name
    cleaned_name = clean_medicine_name(medicine_name)
    
    # Check if it contains known active ingredients
    for ingredient in MEDICINE_HSN_CODES.keys():
        if ingredient in cleaned_name:
            return ingredient
    
    return cleaned_name

def get_hsn_from_database(medicine_name: str, composition: str = None, category: str = None) -> Optional[str]:
    """Get HSN code from local database using various methods"""
    
    # Method 1: Direct match with medicine name
    cleaned_name = clean_medicine_name(medicine_name)
    if cleaned_name in MEDICINE_HSN_CODES:
        return MEDICINE_HSN_CODES[cleaned_name]
    
    # Method 2: Extract active ingredient and match
    active_ingredient = extract_active_ingredient(medicine_name, composition)
    if active_ingredient in MEDICINE_HSN_CODES:
        return MEDICINE_HSN_CODES[active_ingredient]
    
    # Method 3: Match by category
    if category and category in CATEGORY_HSN_MAPPING:
        return CATEGORY_HSN_MAPPING[category]
    
    # Method 4: Partial matching with known ingredients
    for ingredient, hsn in MEDICINE_HSN_CODES.items():
        if ingredient in cleaned_name or (composition and ingredient in composition.lower()):
            return hsn
    
    return None

def fetch_hsn_from_api(medicine_name: str, composition: str = None) -> Optional[Dict[str, Any]]:
    """
    Attempt to fetch HSN code from online APIs
    Note: This is a placeholder for actual API integration
    """
    try:
        # This is where you would integrate with actual APIs like:
        # 1. GST HSN Code APIs
        # 2. Drug information APIs
        # 3. Pharmaceutical databases
        
        # For now, we'll simulate an API response
        # In production, you might use APIs like:
        # - India's GST portal API
        # - OpenFDA API
        # - DrugBank API
        # - Custom pharmaceutical databases
        
        # Placeholder API call (replace with actual implementation)
        # response = requests.get(f"https://api.example.com/hsn?medicine={medicine_name}", timeout=5)
        # if response.status_code == 200:
        #     data = response.json()
        #     return data.get('hsn_code')
        
        return None
        
    except requests.RequestException as e:
        logger.warning(f"API request failed for medicine {medicine_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching HSN for {medicine_name}: {e}")
        return None

def auto_fetch_hsn_code(medicine_name: str, composition: str = None, category: str = None) -> Dict[str, Any]:
    """
    Automatically fetch HSN code for a medicine
    
    Returns:
        Dict with 'hsn_code', 'source', and 'confidence' keys
    """
    result = {
        'hsn_code': None,
        'source': 'none',
        'confidence': 'low',
        'suggestions': []
    }
    
    if not medicine_name:
        return result
    
    # Try local database first (faster and more reliable)
    hsn_code = get_hsn_from_database(medicine_name, composition, category)
    
    if hsn_code:
        result.update({
            'hsn_code': hsn_code,
            'source': 'database',
            'confidence': 'high'
        })
        return result
    
    # Try API fetch as fallback
    api_result = fetch_hsn_from_api(medicine_name, composition)
    if api_result:
        result.update({
            'hsn_code': api_result.get('hsn_code'),
            'source': 'api',
            'confidence': api_result.get('confidence', 'medium')
        })
        return result
    
    # Provide default HSN code based on category
    default_hsn = '30049099'  # General pharmaceutical preparations
    if category in CATEGORY_HSN_MAPPING:
        default_hsn = CATEGORY_HSN_MAPPING[category]
        result['confidence'] = 'medium'
    
    result.update({
        'hsn_code': default_hsn,
        'source': 'default',
    })
    
    # Add suggestions for manual verification
    result['suggestions'] = [
        "Please verify HSN code manually",
        "HSN codes may vary based on exact composition",
        "Consult GST guidelines for accurate classification"
    ]
    
    return result

def get_composition_suggestions(medicine_name: str) -> list:
    """Get composition suggestions based on medicine name"""
    suggestions = []
    
    # Common compositions for known medicines
    composition_db = {
        'paracetamol': [
            'Paracetamol 500mg',
            'Paracetamol 650mg', 
            'Paracetamol 125mg (Pediatric)'
        ],
        'ibuprofen': [
            'Ibuprofen 400mg',
            'Ibuprofen 200mg',
            'Ibuprofen 600mg'
        ],
        'amoxicillin': [
            'Amoxicillin 500mg',
            'Amoxicillin 250mg',
            'Amoxicillin 875mg + Clavulanic Acid 125mg'
        ],
        'omeprazole': [
            'Omeprazole 20mg',
            'Omeprazole 40mg'
        ]
        # Add more as needed
    }
    
    cleaned_name = clean_medicine_name(medicine_name)
    
    for key, comps in composition_db.items():
        if key in cleaned_name:
            suggestions.extend(comps)
    
    return suggestions[:5]  # Return top 5 suggestions