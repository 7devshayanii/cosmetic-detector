HARMFUL_INGREDIENTS = {
    'parabens': {
        'keywords': ['paraben', 'methylparaben', 'propylparaben', 'butylparaben', 'ethylparaben'],
        'reasons': [
            'Can disrupt hormone function',
            'May cause skin irritation',
            'Potential breast cancer link'
        ]
    },
    'sulfates': {
        'keywords': ['sodium lauryl sulfate', 'sls', 'sodium laureth sulfate', 'sles'],
        'reasons': [
            'Strips natural oils from skin and hair',
            'Can cause dryness and irritation',
            'May trigger allergic reactions'
        ]
    },
    'phthalates': {
        'keywords': ['phthalate', 'dbp', 'dehp', 'dep'],
        'reasons': [
            'Endocrine disruptors',
            'May affect reproductive health',
            'Linked to developmental issues'
        ]
    },
    'formaldehyde': {
        'keywords': ['formaldehyde', 'formalin', 'dmdm hydantoin', 'quaternium-15', 'imidazolidinyl urea'],
        'reasons': [
            'Known carcinogen',
            'Can cause allergic skin reactions',
            'Respiratory irritant'
        ]
    },
    'triclosan': {
        'keywords': ['triclosan', 'triclocarban'],
        'reasons': [
            'Disrupts thyroid function',
            'Contributes to antibiotic resistance',
            'Environmental pollutant'
        ]
    },
    'mineral_oil': {
        'keywords': ['mineral oil', 'paraffinum liquidum', 'petrolatum'],
        'reasons': [
            'Clogs pores',
            'May contain harmful contaminants',
            'Prevents skin from breathing'
        ]
    },
    'oxybenzone': {
        'keywords': ['oxybenzone', 'benzophenone'],
        'reasons': [
            'Hormone disruptor',
            'Can cause allergic reactions',
            'Harmful to coral reefs'
        ]
    },
    'hydroquinone': {
        'keywords': ['hydroquinone'],
        'reasons': [
            'Linked to cancer',
            'Can cause skin discoloration',
            'Banned in many countries'
        ]
    },
    'coal_tar': {
        'keywords': ['coal tar', 'aminophenol', 'diaminobenzene', 'phenylenediamine'],
        'reasons': [
            'Known carcinogen',
            'Can cause skin sensitivity',
            'Contaminated with heavy metals'
        ]
    },
    'aluminum': {
        'keywords': ['aluminum', 'aluminium chlorohydrate', 'aluminum zirconium'],
        'reasons': [
            'May be linked to breast cancer',
            'Clogs sweat glands',
            'Potential neurotoxin'
        ]
    }
}

ANIMAL_DERIVED_INGREDIENTS = [
    'lanolin',
    'beeswax',
    'honey',
    'carmine',
    'cochineal',
    'collagen',
    'elastin',
    'keratin',
    'gelatin',
    'squalene',
    'squalane',
    'guanine',
    'stearic acid',
    'oleic acid',
    'caprylic acid',
    'myristic acid',
    'palmitic acid',
    'milk',
    'lactose',
    'whey',
    'casein',
    'silk',
    'pearl',
    'snail mucin',
    'royal jelly',
    'propolis',
    'cholesterol',
    'estrogen',
    'placenta',
    'retinol',
    'biotin',
    'amino acids',
    'panthenol',
    'allantoin'
]


def analyze_ingredients(text):
    text_lower = text.lower()
    
    detected_harmful = []
    total_harmful_count = 0
    
    for ingredient_name, ingredient_data in HARMFUL_INGREDIENTS.items():
        for keyword in ingredient_data['keywords']:
            if keyword in text_lower:
                detected_harmful.append({
                    'name': keyword.title(),
                    'category': ingredient_name.replace('_', ' ').title(),
                    'reasons': ingredient_data['reasons']
                })
                total_harmful_count += 1
                break
    
    is_non_veg = False
    animal_ingredients_found = []
    
    for animal_ingredient in ANIMAL_DERIVED_INGREDIENTS:
        if animal_ingredient in text_lower:
            is_non_veg = True
            animal_ingredients_found.append(animal_ingredient.title())
    
    if total_harmful_count == 0:
        safety_rating = 'SAFE'
    elif total_harmful_count <= 2:
        safety_rating = 'CAUTION'
    else:
        safety_rating = 'HARMFUL'
    
    veg_status = 'NON_VEG' if is_non_veg else 'VEG'
    
    return {
        'harmful_ingredients': detected_harmful,
        'safety_rating': safety_rating,
        'veg_status': veg_status,
        'animal_ingredients': animal_ingredients_found,
        'harmful_count': total_harmful_count
    }
