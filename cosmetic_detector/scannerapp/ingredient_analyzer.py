from PIL import Image
import pytesseract

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path):
    """
    Takes the path of an image and returns the extracted text as a string.
    """
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text


# ==========================
# HARMFUL INGREDIENTS DATA
# ==========================
HARMFUL_INGREDIENTS = {
    'parabens': {
        'keywords': ['paraben', 'methylparaben', 'propylparaben', 'butylparaben', 'ethylparaben', 'isobutylparaben'],
        'reasons': [
            'Can disrupt hormone function',
            'May cause skin irritation',
            'Potential breast cancer link'
        ],
        'risk_level': 'High',
        'age_restriction': None,  # None means no specific age restriction
        'health_conditions': ['hormone_imbalance', 'endocrine_disorders']
    },
    'sulfates': {
        'keywords': ['sodium lauryl sulfate', 'sls', 'sodium laureth sulfate', 'sles'],
        'reasons': [
            'Strips natural oils from skin and hair',
            'Can cause dryness and irritation',
            'May trigger allergic reactions'
        ],
        'risk_level': 'Medium',
        'age_restriction': None,
        'health_conditions': ['eczema', 'psoriasis', 'sensitive_skin', 'dry_skin']
    },
    'phthalates': {
        'keywords': ['phthalate', 'dbp', 'dehp', 'dep', 'diethyl phthalate'],
        'reasons': [
            'Endocrine disruptors',
            'May affect reproductive health',
            'Linked to developmental issues'
        ],
        'risk_level': 'High',
        'age_restriction': 16,  # Not recommended for under 16
        'health_conditions': ['pregnancy', 'hormone_imbalance', 'reproductive_issues']
    },
    'formaldehyde': {
        'keywords': ['formaldehyde', 'formalin', 'dmdm hydantoin', 'quaternium-15', 'imidazolidinyl urea', 'diazolidinyl urea', 'sodium hydroxymethylglycinate'],
        'reasons': [
            'Known carcinogen',
            'Can cause allergic skin reactions',
            'Respiratory irritant'
        ],
        'risk_level': 'High',
        'age_restriction': None,
        'health_conditions': ['asthma', 'respiratory_issues', 'allergies']
    },
    'triclosan': {
        'keywords': ['triclosan', 'triclocarban'],
        'reasons': [
            'Disrupts thyroid function',
            'Contributes to antibiotic resistance',
            'Environmental pollutant'
        ],
        'risk_level': 'High',
        'age_restriction': None,
        'health_conditions': ['thyroid_disorders', 'hormone_imbalance']
    },
    'mineral_oil': {
        'keywords': ['mineral oil', 'paraffinum liquidum', 'petrolatum'],
        'reasons': [
            'Clogs pores',
            'May contain harmful contaminants',
            'Prevents skin from breathing'
        ],
        'risk_level': 'Medium',
        'age_restriction': None,
        'health_conditions': ['acne', 'oily_skin']
    },
    'oxybenzone': {
        'keywords': ['oxybenzone', 'benzophenone'],
        'reasons': [
            'Hormone disruptor',
            'Can cause allergic reactions',
            'Harmful to coral reefs'
        ],
        'risk_level': 'High',
        'age_restriction': 12,  # Not recommended for children
        'health_conditions': ['hormone_imbalance', 'allergies']
    },
    'hydroquinone': {
        'keywords': ['hydroquinone'],
        'reasons': [
            'Linked to cancer',
            'Can cause skin discoloration',
            'Banned in many countries'
        ],
        'risk_level': 'High',
        'age_restriction': 18,
        'health_conditions': ['pregnancy', 'skin_sensitivity']
    },
    'coal_tar': {
        'keywords': ['coal tar', 'aminophenol', 'diaminobenzene', 'phenylenediamine'],
        'reasons': [
            'Known carcinogen',
            'Can cause skin sensitivity',
            'Contaminated with heavy metals'
        ],
        'risk_level': 'High',
        'age_restriction': None,
        'health_conditions': ['cancer_history', 'skin_sensitivity']
    },
    'aluminum': {
        'keywords': ['aluminum', 'aluminium chlorohydrate', 'aluminum zirconium'],
        'reasons': [
            'May be linked to breast cancer',
            'Clogs sweat glands',
            'Potential neurotoxin'
        ],
        'risk_level': 'Medium',
        'age_restriction': None,
        'health_conditions': ['kidney_disease', 'alzheimers']
    },
    'heavy_metals': {
        'keywords': ['lead', 'mercury', 'arsenic', 'chromium', 'thimerosal'],
        'reasons': [
            'Toxic contaminants that can cause systemic toxicity',
            'Linked to neurological and organ damage'
        ],
        'risk_level': 'High',
        'age_restriction': None,
        'health_conditions': ['pregnancy', 'kidney_disease', 'liver_disease']
    },
    'pfas': {
        'keywords': ['pfas', 'pfoa', 'pfos', 'perfluor'],
        'reasons': [
            'Linked to cancer and autoimmune problems',
            'Environmentally persistent'
        ],
        'risk_level': 'High',
        'age_restriction': None,
        'health_conditions': ['cancer_history', 'autoimmune_disorders']
    },
    'bht_bha': {
        'keywords': ['bht', 'bha'],
        'reasons': [
            'Possible hormone disruptor',
            'Potential carcinogen'
        ],
        'risk_level': 'Medium',
        'age_restriction': None,
        'health_conditions': ['hormone_imbalance', 'cancer_history']
    },
    'phenoxyethanol': {
        'keywords': ['phenoxyethanol'],
        'reasons': [
            'May cause irritation and systemic toxicity at higher doses'
        ],
        'risk_level': 'Medium',
        'age_restriction': None,
        'health_conditions': ['eczema', 'sensitive_skin']
    },
    'synthetic_fragrance': {
        'keywords': ['fragrance', 'parfum'],
        'reasons': [
            'Often contains undisclosed chemicals linked to irritation and hormone disruption'
        ],
        'risk_level': 'Medium',
        'age_restriction': None,
        'health_conditions': ['asthma', 'allergies', 'migraines', 'sensitive_skin']
    },
    'toluene': {
        'keywords': ['toluene'],
        'reasons': [
            'Linked to immune, reproductive, and developmental toxicity',
            'Common in nail products'
        ],
        'risk_level': 'High',
        'age_restriction': 18,
        'health_conditions': ['pregnancy', 'respiratory_issues']
    },
    'talcs': {
        'keywords': ['talc'],
        'reasons': [
            'May be contaminated with asbestos',
            'Can cause respiratory issues'
        ],
        'risk_level': 'Medium',
        'age_restriction': None,
        'health_conditions': ['respiratory_issues', 'asthma']
    },
    'acrylates': {
        'keywords': ['acrylate', 'polyacrylamide'],
        'reasons': [
            'Potential carcinogens when broken down',
            'Can cause skin irritation'
        ],
        'risk_level': 'Medium',
        'age_restriction': None,
        'health_conditions': ['skin_sensitivity', 'allergies']
    },
    'silicones': {
        'keywords': ['dimethicone', 'cyclopentasiloxane', 'cyclohexasiloxane', 'd4', 'd5', 'd6'],
        'reasons': [
            'May accumulate in the environment',
            'Can create a barrier on skin trapping dirt'
        ],
        'risk_level': 'Medium',
        'age_restriction': None,
        'health_conditions': ['acne', 'oily_skin']
    },
    'retinoids': {
        'keywords': ['retinol', 'retinyl palmitate', 'retinoic acid', 'tretinoin'],
        'reasons': [
            'Can cause severe birth defects',
            'Increases sun sensitivity'
        ],
        'risk_level': 'High',
        'age_restriction': 18,
        'health_conditions': ['pregnancy', 'trying_to_conceive']
    }
}

# ==========================
# INGREDIENT SOURCE CLASSIFICATION
# ==========================
ANIMAL_DERIVED_INGREDIENTS = {
    'lanolin': 'ANIMAL',
    'beeswax': 'ANIMAL',
    'honey': 'ANIMAL',
    'carmine': 'ANIMAL',
    'cochineal': 'ANIMAL',
    'collagen': 'ANIMAL',
    'elastin': 'ANIMAL',
    'keratin': 'ANIMAL',
    'gelatin': 'ANIMAL',
    'squalene': 'ANIMAL',  # Can be plant-based too
    'guanine': 'ANIMAL',
    'stearic acid': 'ANIMAL',  # Can be plant-based too
    'milk': 'ANIMAL',
    'lactose': 'ANIMAL',
    'whey': 'ANIMAL',
    'casein': 'ANIMAL',
    'silk': 'ANIMAL',
    'pearl': 'ANIMAL',
    'snail mucin': 'ANIMAL',
    'royal jelly': 'ANIMAL',
    'propolis': 'ANIMAL',
    'cholesterol': 'ANIMAL',
    'placenta': 'ANIMAL'
}

PLANT_DERIVED_INGREDIENTS = {
    'aloe vera': 'PLANT',
    'coconut oil': 'PLANT',
    'shea butter': 'PLANT',
    'argan oil': 'PLANT',
    'jojoba oil': 'PLANT',
    'rosehip oil': 'PLANT',
    'tea tree oil': 'PLANT',
    'chamomile': 'PLANT',
    'lavender': 'PLANT',
    'vitamin e': 'PLANT',
    'squalane': 'PLANT',  # Plant-derived version
    'glycerin': 'PLANT',  # Can be synthetic too
    'hyaluronic acid': 'PLANT'  # Usually synthetic/fermented now
}

SYNTHETIC_INGREDIENTS = {
    'niacinamide': 'SYNTHETIC',
    'salicylic acid': 'SYNTHETIC',
    'glycolic acid': 'SYNTHETIC',
    'lactic acid': 'SYNTHETIC',
    'hyaluronic acid': 'SYNTHETIC',
    'peptides': 'SYNTHETIC',
    'ceramides': 'SYNTHETIC'
}

# Common allergens
COMMON_ALLERGENS = {
    'fragrance', 'parfum', 'limonene', 'linalool', 'citronellol', 'geraniol',
    'cinnamal', 'citral', 'eugenol', 'coumarin', 'farnesol', 'benzyl alcohol',
    'benzyl benzoate', 'benzyl salicylate', 'lanolin', 'latex', 'nickel',
    'formaldehyde', 'quaternium-15', 'methylisothiazolinone', 
    'methylchloroisothiazolinone', 'paraphenylenediamine', 'ppd', 
    'cocamidopropyl betaine', 'propolis', 'balsam of peru', 'tea tree oil',
    'lavender oil', 'peppermint oil', 'cinnamon'
}


def analyze_ingredients(text, user_age=None, user_allergies=None, user_health_conditions=None):
    """
    Analyzes cosmetic ingredients with personalized recommendations.
    
    Args:
        text (str): Ingredient text to analyze
        user_age (int, optional): User's age
        user_allergies (list, optional): List of user allergies
        user_health_conditions (list, optional): List of user health conditions
    
    Returns:
        dict: Analysis results with harmful ingredients, safety rating, warnings, etc.
    """
    text_lower = text.lower()
    
    # Convert inputs to lists if they're strings
    if isinstance(user_allergies, str):
        user_allergies = [a.strip().lower() for a in user_allergies.split(',') if a.strip()]
    elif user_allergies is None:
        user_allergies = []
    
    if isinstance(user_health_conditions, str):
        user_health_conditions = [c.strip().lower() for c in user_health_conditions.split(',') if c.strip()]
    elif user_health_conditions is None:
        user_health_conditions = []
    
    # Detect harmful ingredients
    detected_harmful = []
    total_harmful_count = 0
    personalized_warnings = []
    
    for ingredient_name, ingredient_data in HARMFUL_INGREDIENTS.items():
        for keyword in ingredient_data['keywords']:
            if keyword in text_lower:
                harmful_item = {
                    'name': keyword.title(),
                    'category': ingredient_name.replace('_', ' ').title(),
                    'reasons': ingredient_data['reasons'],
                    'risk_level': ingredient_data['risk_level']
                }
                detected_harmful.append(harmful_item)
                total_harmful_count += 1
                
                # Check age restrictions
                if user_age and ingredient_data.get('age_restriction'):
                    if user_age < ingredient_data['age_restriction']:
                        personalized_warnings.append({
                            'type': 'age_restriction',
                            'ingredient': keyword.title(),
                            'message': f"Not recommended for users under {ingredient_data['age_restriction']} years old",
                            'severity': 'high'
                        })
                
                # Check health condition conflicts
                if user_health_conditions and ingredient_data.get('health_conditions'):
                    for condition in user_health_conditions:
                        if condition in ingredient_data['health_conditions']:
                            personalized_warnings.append({
                                'type': 'health_condition',
                                'ingredient': keyword.title(),
                                'condition': condition.replace('_', ' ').title(),
                                'message': f"May aggravate {condition.replace('_', ' ')}",
                                'severity': 'high'
                            })
                
                break  # Only count each ingredient category once
    
    # Check for allergens
    if user_allergies:
        for allergen in COMMON_ALLERGENS:
            if allergen in text_lower:
                for user_allergen in user_allergies:
                    if user_allergen in allergen or allergen in user_allergen:
                        personalized_warnings.append({
                            'type': 'allergy',
                            'ingredient': allergen.title(),
                            'message': f"Contains {allergen.title()} - may trigger allergic reaction",
                            'severity': 'critical'
                        })
    
    # Classify ingredient sources (animal/plant/synthetic)
    animal_ingredients_found = []
    plant_ingredients_found = []
    synthetic_ingredients_found = []
    
    for ingredient, source in ANIMAL_DERIVED_INGREDIENTS.items():
        if ingredient in text_lower:
            animal_ingredients_found.append(ingredient.title())
    
    for ingredient, source in PLANT_DERIVED_INGREDIENTS.items():
        if ingredient in text_lower:
            plant_ingredients_found.append(ingredient.title())
    
    for ingredient, source in SYNTHETIC_INGREDIENTS.items():
        if ingredient in text_lower:
            synthetic_ingredients_found.append(ingredient.title())
    
    # Determine ingredient source classification
    if animal_ingredients_found and not plant_ingredients_found and not synthetic_ingredients_found:
        ingredient_source = 'ANIMAL'
    elif plant_ingredients_found and not animal_ingredients_found and not synthetic_ingredients_found:
        ingredient_source = 'PLANT'
    elif synthetic_ingredients_found and not animal_ingredients_found and not plant_ingredients_found:
        ingredient_source = 'SYNTHETIC'
    elif animal_ingredients_found or plant_ingredients_found or synthetic_ingredients_found:
        ingredient_source = 'MIXED'
    else:
        ingredient_source = 'UNKNOWN'
    
    # Determine safety rating
    critical_warnings = [w for w in personalized_warnings if w['severity'] == 'critical']
    high_warnings = [w for w in personalized_warnings if w['severity'] == 'high']
    
    if critical_warnings or total_harmful_count > 3:
        safety_rating = 'HARMFUL'
    elif high_warnings or total_harmful_count > 1:
        safety_rating = 'MILD RISK'
    else:
        safety_rating = 'SAFE'
    
    return {
        'harmful_ingredients': detected_harmful,
        'safety_rating': safety_rating,
        'ingredient_source': ingredient_source,
        'animal_ingredients': animal_ingredients_found,
        'plant_ingredients': plant_ingredients_found,
        'synthetic_ingredients': synthetic_ingredients_found,
        'harmful_count': total_harmful_count,
        'personalized_warnings': personalized_warnings,
        'has_age_restrictions': any(w['type'] == 'age_restriction' for w in personalized_warnings),
        'has_allergy_warnings': any(w['type'] == 'allergy' for w in personalized_warnings),
        'has_health_warnings': any(w['type'] == 'health_condition' for w in personalized_warnings)
    }