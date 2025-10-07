"""
HSN Code Auto-Fetch Utilities for Medicines
"""
import requests
import json
import re
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Comprehensive medicine HSN codes database (Updated for accurate Indian GST classification)
MEDICINE_HSN_CODES = {
    # Analgesics and Antipyretics (30042019)
    'paracetamol': '30042019',
    'acetaminophen': '30042019', 
    'aspirin': '30042019',
    'acetylsalicylic acid': '30042019',
    'ibuprofen': '30042019',
    'diclofenac': '30042019',
    'nimesulide': '30042019',
    'aceclofenac': '30042019',
    'mefenamic acid': '30042019',
    'piroxicam': '30042019',
    
    # Antibiotics and Antimicrobials (30042011)
    'amoxicillin': '30042011',
    'azithromycin': '30042011',
    'ciprofloxacin': '30042011',
    'doxycycline': '30042011',
    'erythromycin': '30042011',
    'cephalexin': '30042011',
    'cloxacillin': '30042011',
    'ampicillin': '30042011',
    'norfloxacin': '30042011',
    'ofloxacin': '30042011',
    
    # Antidiabetic Medicines (30049091)
    'metformin': '30049091',
    'glimepiride': '30049091',
    'gliclazide': '30049091',
    'glipizide': '30049091',
    'pioglitazone': '30049091',
    'sitagliptin': '30049091',
    'insulin': '30042090',  # Injectable insulin
    
    # Cardiovascular Medicines (30049021)
    'amlodipine': '30049021',
    'atenolol': '30049021',
    'losartan': '30049021',
    'telmisartan': '30049021',
    'enalapril': '30049021',
    'ramipril': '30049021',
    'carvedilol': '30049021',
    'metoprolol': '30049021',
    'nifedipine': '30049021',
    'valsartan': '30049021',
    
    # Gastrointestinal Medicines (30049061)
    'omeprazole': '30049061',
    'pantoprazole': '30049061',
    'ranitidine': '30049061',
    'lansoprazole': '30049061',
    'esomeprazole': '30049061',
    'domperidone': '30049061',
    'ondansetron': '30049061',
    'loperamide': '30049061',
    
    # Antihistamines and Anti-allergic (30049051)
    'cetirizine': '30049051',
    'loratadine': '30049051',
    'fexofenadine': '30049051',
    'chlorpheniramine': '30049051',
    'hydroxyzine': '30049051',
    'desloratadine': '30049051',
    
    # Respiratory Medicines (30049031)
    'salbutamol': '30049031',
    'theophylline': '30049031',
    'montelukast': '30049031',
    'terbutaline': '30049031',
    'bambuterol': '30049031',
    
    # Cough and Cold Preparations (30049041)
    'dextromethorphan': '30049041',
    'guaifenesin': '30049041',
    'bromhexine': '30049041',
    'ambroxol': '30049041',
    'phenylephrine': '30049041',
    
    # Vitamins and Supplements (21069090)
    'multivitamin': '21069090',
    'vitamin d': '21069090',
    'vitamin c': '21069090',
    'vitamin b complex': '21069090',
    'folic acid': '21069090',
    'calcium': '21069090',
    'iron': '21069090',
    'zinc': '21069090',
    'magnesium': '21069090',
    'omega 3': '21069090',
    
    # Neurological Medicines (30049071)
    'pregabalin': '30049071',
    'gabapentin': '30049071',
    'duloxetine': '30049071',
    'fluoxetine': '30049071',
    'sertraline': '30049071',
    'alprazolam': '30049071',
    'lorazepam': '30049071',
    'clonazepam': '30049071',
}

# Medicine category to HSN mapping (Updated with correct codes)
CATEGORY_HSN_MAPPING = {
    # Analgesics and Antipyretics
    'fever': '30042019',                    # Paracetamol and fever reducers
    'pain': '30042019',                     # NSAIDs and analgesics
    
    # Respiratory System
    'cough': '30049041',                    # Cough preparations
    'cold': '30049041',                     # Cold medicines  
    'flu': '30049041',                      # Flu medicines
    'Respiratory (Asthma, Bronchitis)': '30049031', # Bronchodilators
    
    # Endocrine System
    'diabetes': '30049091',                 # Antidiabetic medicines
    'Diabetes': '30049091',                 # Antidiabetic medicines
    'Diabetic': '30049091',                 # Diabetic care medicines
    
    # Cardiovascular System
    'bloodpressure': '30049021',            # Antihypertensives
    'heartdisease': '30049021',             # Cardiovascular medicines
    'Hypertension / Heart': '30049021',     # Heart medicines
    
    # Gastrointestinal System
    'digestivehealth': '30049061',          # Digestive medicines
    'Stomach / Digestion': '30049061',      # GI medicines
    
    # Immune System
    'allergy': '30049051',                  # Antihistamines
    'Allergy': '30049051',                  # Anti-allergic medicines
    
    # Respiratory Disorders
    'asthma': '30049031',                   # Bronchodilators
    
    # Anti-infective
    'infection': '30042011',                # Antibiotics
    'Infection (Antibiotics)': '30042011',  # Antimicrobials
    
    # Nervous System
    'Neuropathy': '30049071',               # Neurological medicines
    
    # Specialized Preparations
    'eye': '30049081',                      # Ophthalmic preparations
    'ear': '30049081',                      # Otic preparations
    'Eye / Ear / Nose': '30049081',         # ENT preparations
    'skin': '30051019',                     # Dermatological preparations
    'Skin': '30051019',                     # Topical medicines
    
    # Nutritional Supplements
    'vitamins': '21069090',                 # Vitamin preparations
    'Vitamins & Supplements': '21069090',   # Supplements
    
    # Genitourinary System
    'Urinary': '30049099',                  # Urological medicines
    
    # Emergency and First Aid
    'First Aid': '30059090',                # External use medicaments
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