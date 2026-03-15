"""
Service to fetch cosmetic product ingredients from external APIs
"""
import requests
import logging
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class ProductAPIService:
    """
    Fetches cosmetic product information from Open Beauty Facts API
    """
    
    BASE_URL = "https://world.openbeautyfacts.org"
    SEARCH_URL = f"{BASE_URL}/cgi/search.pl"
    PRODUCT_URL = f"{BASE_URL}/api/v2/product"
    
    @staticmethod
    def normalize_search_term(product_name):
        """
        Normalize search term with aggressive variations including typo tolerance
        """
        # Remove extra spaces
        normalized = ' '.join(product_name.strip().split())
        
        # Create variations
        variations = [
            normalized,  # Original normalized
            normalized.lower(),  # Lowercase
            normalized.title(),  # Title Case
            normalized.upper(),  # UPPERCASE
            normalized.replace(' ', ''),  # NoSpaces (cerave)
            normalized.replace(' ', '-'),  # With-dashes (cera-ve)
            re.sub(r'[^a-zA-Z0-9]', '', normalized),  # Only alphanumeric
            re.sub(r'[^a-zA-Z0-9]', '', normalized).lower(),  # Alphanumeric lowercase
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for var in variations:
            if var and var not in seen:
                seen.add(var)
                unique_variations.append(var)
        
        return unique_variations
    
    @staticmethod
    def search_all_products(product_name):
        """
        FAST search for products - optimized for speed
        """
        try:
            # Use only basic normalized term for speed
            search_term = ' '.join(product_name.strip().split())
            all_products = []
            
            # Single optimized API call
            params = {
                'search_terms': search_term,
                'search_simple': 1,
                'action': 'process',
                'json': 1,
                'page_size': 5  # Reduced from 8
            }
            
            response = requests.get(ProductAPIService.SEARCH_URL, params=params, timeout=2)  # Reduced from 3
            response.raise_for_status()
            
            data = response.json()
            products = data.get('products', [])[:5]  # Reduced from 8
            
            for product in products:
                ingredients_text = product.get('ingredients_text', '')
                
                # Convert ingredients if needed
                if not ingredients_text and product.get('ingredients'):
                    ingredients_list = product.get('ingredients', [])
                    ingredients_text = ', '.join([
                        ing.get('text', ing.get('id', '')) 
                        for ing in ingredients_list 
                        if isinstance(ing, dict)
                    ])
                
                if ingredients_text:
                    product_info = {
                        'product_name': product.get('product_name', 'Unknown Product'),
                        'brand': product.get('brands', 'Unknown'),
                        'ingredients_text': ingredients_text,
                        'ingredients_list': product.get('ingredients', []),
                        'image_url': product.get('image_url', ''),
                        'barcode': product.get('code', ''),
                        'source': 'Open Beauty Facts'
                    }
                    all_products.append(product_info)
            
            # Quick deduplication
            unique_products = []
            seen = set()
            for prod in all_products:
                key = prod['product_name'].lower().strip()
                if key not in seen and key != 'unknown product':
                    seen.add(key)
                    unique_products.append(prod)
            
            return unique_products
            
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []
    
    @staticmethod
    def search_product(product_name):
        """
        Search for a SINGLE product (backward compatibility)
        Returns first matching product
        
        Args:
            product_name (str): Name of the cosmetic product
            
        Returns:
            dict: Product information including ingredients, or None if not found
        """
        products = ProductAPIService.search_all_products(product_name)
        
        if not products:
            return None
        
        # Return first product
        return products[0]
    
    @staticmethod
    def get_product_by_barcode(barcode):
        """
        Get product information by barcode
        
        Args:
            barcode (str): Product barcode
            
        Returns:
            dict: Product information or None
        """
        try:
            url = f"{ProductAPIService.PRODUCT_URL}/{barcode}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 1:
                return None
            
            product = data.get('product', {})
            
            result = {
                'product_name': product.get('product_name', 'Unknown Product'),
                'brand': product.get('brands', 'Unknown'),
                'ingredients_text': product.get('ingredients_text', ''),
                'ingredients_list': product.get('ingredients', []),
                'image_url': product.get('image_url', ''),
                'barcode': barcode,
                'source': 'Open Beauty Facts'
            }
            
            if not result['ingredients_text'] and result['ingredients_list']:
                result['ingredients_text'] = ', '.join([
                    ing.get('text', ing.get('id', '')) 
                    for ing in result['ingredients_list']
                    if isinstance(ing, dict)
                ])
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching product by barcode: {str(e)}")
            return None


# Expanded Manual Indian cosmetics database
# ============================================================================
# REPLACE THIS SECTION IN YOUR product_api_service.py
# Find: INDIAN_COSMETICS_DATABASE = {
# Replace with this entire block below
# ============================================================================

INDIAN_COSMETICS_DATABASE = {
    # ========== LAKME ==========
    'lakme': {
        'products': {
            'lakme 9 to 5 primer matte lipstick': {
                'brand': 'Lakme',
                'ingredients': 'Ricinus Communis (Castor) Seed Oil, Ethylhexyl Palmitate, Ozokerite, Copernicia Cerifera (Carnauba) Wax, Beeswax, Polybutene, Dimethicone, Fragrance, Tocopheryl Acetate, Propylparaben, BHT'
            },
            'lakme absolute argan oil lip color': {
                'brand': 'Lakme',
                'ingredients': 'Ricinus Communis Seed Oil, Ethylhexyl Palmitate, Ozokerite, Argania Spinosa Kernel Oil, Tocopheryl Acetate, Fragrance'
            },
            'lakme sun expert spf 50 sunscreen': {
                'brand': 'Lakme',
                'ingredients': 'Aqua, Ethylhexyl Methoxycinnamate, Benzophenone-3, Glycerin, C12-15 Alkyl Benzoate, Titanium Dioxide, Dimethicone, Fragrance'
            },
            'lakme 9 to 5 foundation': {
                'brand': 'Lakme',
                'ingredients': 'Aqua, Cyclopentasiloxane, Titanium Dioxide, Dimethicone, Glycerin, Talc, Phenoxyethanol, Fragrance, BHT'
            },
            'lakme eyeconic kajal': {
                'brand': 'Lakme',
                'ingredients': 'Hydrogenated Palm Oil, Mica, Copernicia Cerifera Wax, Talc, Tocopheryl Acetate, Propylparaben, BHT'
            },
            'lakme peach milk moisturizer': {
                'brand': 'Lakme',
                'ingredients': 'Aqua, Glycerin, Isopropyl Myristate, Dimethicone, Peach Extract, Milk Protein, Fragrance, Methylparaben'
            },
        }
    },
    
    # ========== HIMALAYA ==========
    'himalaya': {
        'products': {
            'himalaya nourishing skin cream': {
                'brand': 'Himalaya',
                'ingredients': 'Aqua, Glycerin, Cetearyl Alcohol, Glyceryl Stearate, Aloe Barbadensis Leaf Extract, Prunus Amygdalus Dulcis Oil, Triticum Vulgare Germ Oil'
            },
            'himalaya purifying neem face wash': {
                'brand': 'Himalaya',
                'ingredients': 'Aqua, Sodium Laureth Sulfate, Acrylates Copolymer, Cocamidopropyl Betaine, Neem Extract, Turmeric Extract, Fragrance'
            },
            'himalaya herbals anti-hair fall shampoo': {
                'brand': 'Himalaya',
                'ingredients': 'Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Glycerin, Bhringraj Extract, Butea Frondosa Extract'
            },
            'himalaya baby cream': {
                'brand': 'Himalaya',
                'ingredients': 'Aqua, Lanolin, Glycerin, Aloe Vera Extract, Almond Oil, Olive Oil, Fragrance'
            },
            'himalaya moisturizing cream': {
                'brand': 'Himalaya',
                'ingredients': 'Aqua, Aloe Vera, Almond Oil, Wheat Germ Oil, Glycerin, Cetearyl Alcohol'
            },
            'himalaya apricot scrub': {
                'brand': 'Himalaya',
                'ingredients': 'Aqua, Apricot Granules, Glycerin, Walnut Shell Powder, Wheat Germ Oil, Fragrance'
            },
        }
    },
    
    # ========== BIOTIQUE ==========
    'biotique': {
        'products': {
            'biotique bio honey gel refreshing foaming face wash': {
                'brand': 'Biotique',
                'ingredients': 'Aqua, Honey, Helianthus Annuus Seed Oil, Glycerin, Triticum Vulgare Germ Extract'
            },
            'biotique bio almond oil nourishing body soap': {
                'brand': 'Biotique',
                'ingredients': 'Soap Noodles, Prunus Amygdalus Dulcis Oil, Aqua, Glycerin, Fragrance'
            },
            'biotique morning nectar moisturizer': {
                'brand': 'Biotique',
                'ingredients': 'Aqua, Wheat Germ Oil, Sunflower Oil, Honey, Almond Oil, Glycerin'
            },
            'biotique papaya scrub': {
                'brand': 'Biotique',
                'ingredients': 'Aqua, Papaya Extract, Walnut Shell Powder, Glycerin, Aloe Vera, Fragrance'
            },
            'biotique sunscreen spf 50': {
                'brand': 'Biotique',
                'ingredients': 'Aqua, Titanium Dioxide, Zinc Oxide, Aloe Vera, Glycerin, Fragrance'
            },
        }
    },
    
    # ========== MAMAEARTH ==========
    'mamaearth': {
        'products': {
            'mamaearth vitamin c face wash': {
                'brand': 'Mamaearth',
                'ingredients': 'Aqua, Glycerin, Cocamidopropyl Betaine, Decyl Glucoside, Vitamin C, Turmeric Extract, Aloe Vera Extract'
            },
            'mamaearth onion hair oil': {
                'brand': 'Mamaearth',
                'ingredients': 'Onion Seed Extract, Redensyl, Anagain, Biotin, Sunflower Oil, Coconut Oil, Almond Oil'
            },
            'mamaearth ubtan face scrub': {
                'brand': 'Mamaearth',
                'ingredients': 'Aqua, Walnut Shell Powder, Turmeric, Saffron, Carrot Seed Oil, Almond Oil'
            },
            'mamaearth tea tree face wash': {
                'brand': 'Mamaearth',
                'ingredients': 'Aqua, Tea Tree Oil, Neem Extract, Salicylic Acid, Glycerin'
            },
            'mamaearth ubtan face wash': {
                'brand': 'Mamaearth',
                'ingredients': 'Aqua, Turmeric Extract, Saffron Extract, Glycerin, Cocamidopropyl Betaine'
            },
        }
    },
    
    # ========== PONDS ==========
    'ponds': {
        'products': {
            'ponds dreamflower talc': {
                'brand': 'Ponds',
                'ingredients': 'Talc, Fragrance, Zinc Stearate, Magnesium Carbonate'
            },
            'ponds magic freshness talc': {
                'brand': 'Ponds',
                'ingredients': 'Talc, Fragrance, Zinc Oxide, Magnesium Carbonate'
            },
            'ponds sandal radiance talc': {
                'brand': 'Ponds',
                'ingredients': 'Talc, Sandalwood Extract, Fragrance, Zinc Stearate'
            },
            'ponds angel face powder': {
                'brand': 'Ponds',
                'ingredients': 'Talc, Zinc Oxide, Fragrance, Titanium Dioxide'
            },
            'ponds cold cream': {
                'brand': 'Ponds',
                'ingredients': 'Aqua, Mineral Oil, Beeswax, Cetyl Alcohol, Fragrance'
            },
            'ponds bb magic powder': {
                'brand': 'Ponds',
                'ingredients': 'Talc, Titanium Dioxide, Mica, Fragrance, Dimethicone'
            },
            'ponds dreamflower lotion': {
                'brand': 'Ponds',
                'ingredients': 'Aqua, Glycerin, Mineral Oil, Dimethicone, Fragrance, Methylparaben'
            },
        }
    },
    
    # ========== YARDLEY ==========
    'yardley': {
        'products': {
            'yardley london english lavender talc': {
                'brand': 'Yardley London',
                'ingredients': 'Talc, Fragrance, Zinc Stearate, Lavender Oil'
            },
            'yardley london gold talc': {
                'brand': 'Yardley London',
                'ingredients': 'Talc, Fragrance, Zinc Stearate, Gold Mica'
            },
        }
    },
    
    # ========== NYCIL ==========
    'nycil': {
        'products': {
            'nycil prickly heat powder': {
                'brand': 'Nycil',
                'ingredients': 'Talc, Zinc Oxide, Boric Acid, Menthol, Fragrance'
            },
        }
    },
    
    # ========== FAIR & LOVELY / GLOW & LOVELY ==========
    'glow_lovely': {
        'products': {
            'glow & lovely face cream': {
                'brand': 'Glow & Lovely',
                'ingredients': 'Aqua, Glycerin, Niacinamide, Titanium Dioxide, Vitamin B3, Fragrance, Methylparaben'
            },
        }
    },
    
    # ========== VICCO ==========
    'vicco': {
        'products': {
            'vicco turmeric cream': {
                'brand': 'Vicco',
                'ingredients': 'Turmeric Oil, Sandalwood Oil, Base Cream, Fragrance'
            },
            'vicco turmeric wso skin cream': {
                'brand': 'Vicco',
                'ingredients': 'Turmeric Extract, Sandalwood Oil, Base Cream (No animal fats)'
            },
            'vicco vajradanti toothpaste': {
                'brand': 'Vicco',
                'ingredients': 'Calcium Carbonate, Sorbitol, Aqua, Clove Oil, Neem Extract, Black Pepper'
            },
        }
    },
    
    # ========== BOROPLUS ==========
    'boroplus': {
        'products': {
            'boroplus antiseptic cream': {
                'brand': 'Boroplus',
                'ingredients': 'Boric Acid, Zinc Oxide, Neem Extract, Aloe Vera, Tulsi Extract, Lanolin'
            },
        }
    },
    
    # ========== BOROLINE ==========
    'boroline': {
        'products': {
            'boroline antiseptic cream': {
                'brand': 'Boroline',
                'ingredients': 'Boric Acid, Zinc Oxide, Lanolin, Perfume'
            },
        }
    },
    
    # ========== NIVEA ==========
    'nivea': {
        'products': {
            'nivea soft cream': {
                'brand': 'Nivea',
                'ingredients': 'Aqua, Glycerin, Mineral Oil, Petrolatum, Dimethicone, Fragrance, Methylparaben'
            },
            'nivea body lotion': {
                'brand': 'Nivea',
                'ingredients': 'Aqua, Glycerin, Paraffinum Liquidum, Cetearyl Alcohol, Fragrance, Dimethicone'
            },
        }
    },
    
    # ========== PATANJALI ==========
    'patanjali': {
        'products': {
            'patanjali saundarya cream': {
                'brand': 'Patanjali',
                'ingredients': 'Aloe Vera, Turmeric, Sandalwood, Saffron, Almond Oil, Base Cream'
            },
            'patanjali neem face wash': {
                'brand': 'Patanjali',
                'ingredients': 'Aqua, Neem Extract, Tulsi Extract, Aloe Vera, Sodium Laureth Sulfate'
            },
            'patanjali dant kanti toothpaste': {
                'brand': 'Patanjali',
                'ingredients': 'Calcium Carbonate, Neem, Babool, Clove, Akarkara, Pudina'
            },
        }
    },
    
    # ========== GARNIER ==========
    'garnier': {
        'products': {
            'garnier bright complete face wash': {
                'brand': 'Garnier',
                'ingredients': 'Aqua, Glycerin, Sodium Laureth Sulfate, Vitamin C, Lemon Extract, Fragrance'
            },
            'garnier men face wash': {
                'brand': 'Garnier',
                'ingredients': 'Aqua, Glycerin, Sodium Laureth Sulfate, Charcoal Powder, Menthol, Fragrance'
            },
            'garnier light complete serum cream': {
                'brand': 'Garnier',
                'ingredients': 'Aqua, Glycerin, Niacinamide, Vitamin C, Titanium Dioxide, Fragrance, Methylparaben'
            },
        }
    },
    
    # ========== CLEAN & CLEAR ==========
    'clean_clear': {
        'products': {
            'clean & clear face wash': {
                'brand': 'Clean & Clear',
                'ingredients': 'Aqua, Sodium Laureth Sulfate, Glycerin, Salicylic Acid, Menthol, Fragrance'
            },
        }
    },
    
    # ========== MAYBELLINE ==========
    'maybelline': {
        'products': {
            'maybelline fit me foundation': {
                'brand': 'Maybelline',
                'ingredients': 'Aqua, Cyclopentasiloxane, Titanium Dioxide, Dimethicone, Glycerin, Talc, Fragrance'
            },
            'maybelline colossal kajal': {
                'brand': 'Maybelline',
                'ingredients': 'Cyclopentasiloxane, Trimethylsiloxysilicate, Mica, Synthetic Wax, Polyethylene'
            },
        }
    },
    
    # ========== BLUE HEAVEN ==========
    'blue_heaven': {
        'products': {
            'blue heaven lipstick': {
                'brand': 'Blue Heaven',
                'ingredients': 'Castor Oil, Beeswax, Carnauba Wax, Lanolin, Mica, Titanium Dioxide, Fragrance'
            },
        }
    },
    
    # ========== ELLE 18 ==========
    'elle_18': {
        'products': {
            'elle 18 lipstick': {
                'brand': 'Elle 18',
                'ingredients': 'Ricinus Communis Oil, Beeswax, Mica, Fragrance, Propylparaben'
            },
            'elle 18 nail polish': {
                'brand': 'Elle 18',
                'ingredients': 'Ethyl Acetate, Butyl Acetate, Nitrocellulose, Isopropyl Alcohol, Toluene'
            },
        }
    },
    
    # ========== COLORBAR ==========
    'colorbar': {
        'products': {
            'colorbar nail polish': {
                'brand': 'Colorbar',
                'ingredients': 'Ethyl Acetate, Butyl Acetate, Nitrocellulose, Adipic Acid, Isopropyl Alcohol'
            },
        }
    },
    
    # ========== PLUM ==========
    'plum': {
        'products': {
            'plum green tea alcohol-free toner': {
                'brand': 'Plum',
                'ingredients': 'Aqua, Glycerin, Green Tea Extract, Witch Hazel, Panthenol'
            },
            'plum face serum': {
                'brand': 'Plum',
                'ingredients': 'Aqua, Niacinamide, Hyaluronic Acid, Glycerin, Phenoxyethanol'
            },
        }
    },
    
    # ========== WOW SKIN SCIENCE ==========
    'wow': {
        'products': {
            'wow skin science vitamin c face wash': {
                'brand': 'WOW Skin Science',
                'ingredients': 'Aqua, Vitamin C, Aloe Vera Extract, Glycerin, Mulberry Extract'
            },
        }
    },
    
    # ========== LOTUS HERBALS ==========
    'lotus': {
        'products': {
            'lotus herbals safe sun sunscreen': {
                'brand': 'Lotus Herbals',
                'ingredients': 'Aqua, Titanium Dioxide, Zinc Oxide, Glycerin, Aloe Vera, Fragrance'
            },
            'lotus herbals kajal': {
                'brand': 'Lotus Herbals',
                'ingredients': 'Hydrogenated Vegetable Oil, Castor Oil, Almond Oil, Vitamin E, Camphor'
            },
        }
    },
    
    # ========== CLINIC PLUS ==========
    'clinic_plus': {
        'products': {
            'clinic plus shampoo': {
                'brand': 'Clinic Plus',
                'ingredients': 'Aqua, Sodium Laureth Sulfate, Glycerin, Dimethicone, Milk Protein, Fragrance'
            },
        }
    },
    
    # ========== SUNSILK ==========
    'sunsilk': {
        'products': {
            'sunsilk shampoo': {
                'brand': 'Sunsilk',
                'ingredients': 'Aqua, Sodium Laureth Sulfate, Dimethicone, Glycerin, Fragrance, Methylchloroisothiazolinone'
            },
        }
    },
    
    # ========== DOVE ==========
    'dove': {
        'products': {
            'dove shampoo': {
                'brand': 'Dove',
                'ingredients': 'Aqua, Sodium Laureth Sulfate, Glycerin, Dimethicone, Fragrance, DMDM Hydantoin'
            },
            'dove body wash': {
                'brand': 'Dove',
                'ingredients': 'Aqua, Cocamidopropyl Betaine, Sodium Laureth Sulfate, Glycerin, Fragrance'
            },
        }
    },
    
    # ========== PANTENE ==========
    'pantene': {
        'products': {
            'pantene shampoo': {
                'brand': 'Pantene',
                'ingredients': 'Aqua, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, Panthenol, Fragrance, Methylchloroisothiazolinone'
            },
        }
    },
    
    # ========== HEAD & SHOULDERS ==========
    'head_shoulders': {
        'products': {
            'head & shoulders shampoo': {
                'brand': 'Head & Shoulders',
                'ingredients': 'Aqua, Sodium Laureth Sulfate, Zinc Pyrithione, Dimethicone, Fragrance'
            },
        }
    },
    
    # ========== PARACHUTE ==========
    'parachute': {
        'products': {
            'parachute coconut oil': {
                'brand': 'Parachute',
                'ingredients': 'Cocos Nucifera (Coconut) Oil'
            },
        }
    },
    
    # ========== DABUR ==========
    'dabur': {
        'products': {
            'dabur amla hair oil': {
                'brand': 'Dabur',
                'ingredients': 'Mineral Oil, Amla Extract, Henna Extract, Almond Oil, Fragrance'
            },
            'dabur red toothpaste': {
                'brand': 'Dabur',
                'ingredients': 'Calcium Carbonate, Clove Oil, Pudina, Tomar, Pipli'
            },
        }
    },
    
    # ========== BAJAJ ==========
    'bajaj': {
        'products': {
            'bajaj almond drops oil': {
                'brand': 'Bajaj',
                'ingredients': 'Mineral Oil, Almond Oil, Vitamin E, Fragrance'
            },
        }
    },
    
    # ========== LUX ==========
    'lux': {
        'products': {
            'lux soap': {
                'brand': 'Lux',
                'ingredients': 'Sodium Palmate, Sodium Palm Kernelate, Aqua, Fragrance, Glycerin, Titanium Dioxide'
            },
        }
    },
    
    # ========== PEARS ==========
    'pears': {
        'products': {
            'pears soap': {
                'brand': 'Pears',
                'ingredients': 'Sodium Palmitate, Glycerin, Sodium Laureth Sulfate, Fragrance, Sorbitol'
            },
        }
    },
    
    # ========== LIFEBUOY ==========
    'lifebuoy': {
        'products': {
            'lifebuoy soap': {
                'brand': 'Lifebuoy',
                'ingredients': 'Sodium Palmate, Sodium Palm Kernelate, Aqua, Thymol, Fragrance'
            },
            'lifebuoy body wash': {
                'brand': 'Lifebuoy',
                'ingredients': 'Aqua, Sodium Laureth Sulfate, Thymol, Glycerin, Fragrance'
            },
        }
    },
    
    # ========== SANTOOR ==========
    'santoor': {
        'products': {
            'santoor soap': {
                'brand': 'Santoor',
                'ingredients': 'Sodium Palmate, Sandalwood Oil, Turmeric Extract, Aqua, Glycerin, Fragrance'
            },
        }
    },
    
    # ========== DETTOL ==========
    'dettol': {
        'products': {
            'dettol body wash': {
                'brand': 'Dettol',
                'ingredients': 'Aqua, Sodium Laureth Sulfate, Chloroxylenol, Glycerin, Fragrance'
            },
        }
    },
    
    # ========== VASELINE ==========
    'vaseline': {
        'products': {
            'vaseline petroleum jelly': {
                'brand': 'Vaseline',
                'ingredients': 'Petrolatum'
            },
            'vaseline healthy white lotion': {
                'brand': 'Vaseline',
                'ingredients': 'Aqua, Glycerin, Petrolatum, Niacinamide, Dimethicone, Fragrance'
            },
        }
    },
    
    # ========== VEET ==========
    'veet': {
        'products': {
            'veet hair removal cream': {
                'brand': 'Veet',
                'ingredients': 'Aqua, Calcium Thioglycolate, Cetearyl Alcohol, Paraffinum Liquidum, Fragrance'
            },
        }
    },
    
    # ========== EVERYUTH NATURALS ==========
    'everyuth': {
        'products': {
            'everyuth naturals scrub': {
                'brand': 'Everyuth Naturals',
                'ingredients': 'Aqua, Walnut Shell Powder, Glycerin, Apricot Extract, Fragrance'
            },
        }
    },
    
    # ========== OLAY ==========
    'olay': {
        'products': {
            'olay natural white cream': {
                'brand': 'Olay',
                'ingredients': 'Aqua, Glycerin, Niacinamide, Titanium Dioxide, Petrolatum, Fragrance, Methylparaben'
            },
        }
    },
    
    # ========== CINTHOL ==========
    'cinthol': {
        'products': {
            'cinthol lime talc': {
                'brand': 'Cinthol',
                'ingredients': 'Talc, Fragrance, Lime Oil, Zinc Stearate'
            },
        }
    },
    
    # ========== EVA ==========
    'eva': {
        'products': {
            'eva fresh talc': {
                'brand': 'Eva',
                'ingredients': 'Talc, Fragrance, Zinc Oxide'
            },
        }
    },
}



def search_indian_database_all(product_name):
    """
    Search the manual Indian cosmetics database - returns ALL matching products
    
    Args:
        product_name (str): Product name to search
        
    Returns:
        list: List of product information or empty list
    """
    # Normalize search term
    product_name_lower = ' '.join(product_name.strip().lower().split())
    product_name_no_space = product_name.replace(' ', '').lower()
    
    matching_products = []
    
    for brand, brand_data in INDIAN_COSMETICS_DATABASE.items():
        brand_variations = [
            brand.lower(),
            brand.replace(' ', '').lower()
        ]
        
        for product_key, product_info in brand_data['products'].items():
            product_key_lower = product_key.lower()
            product_key_no_space = product_key.replace(' ', '').lower()
            
            # Match if search term is in product name or brand
            if (product_key_lower in product_name_lower or 
                product_name_lower in product_key_lower or
                any(brand_var in product_name_lower for brand_var in brand_variations) or
                product_key_no_space in product_name_no_space or
                product_name_no_space in product_key_no_space):
                
                matching_products.append({
                    'product_name': product_key.title(),
                    'brand': product_info['brand'],
                    'ingredients_text': product_info['ingredients'],
                    'ingredients_list': [],
                    'image_url': '',
                    'barcode': '',
                    'source': 'Indian Database'
                })
    
    return matching_products


def search_indian_database(product_name):
    """
    Search the manual Indian cosmetics database - returns first match
    
    Args:
        product_name (str): Product name to search
        
    Returns:
        dict: Product information or None
    """
    products = search_indian_database_all(product_name)
    return products[0] if products else None


def fetch_product_ingredients(product_name):
    """
    Unified function to fetch product ingredients from multiple sources
    Returns first match only (for backward compatibility)
    
    Args:
        product_name (str): Product name to search
        
    Returns:
        dict: Product information with ingredients
    """
    # Try Open Beauty Facts first
    result = ProductAPIService.search_product(product_name)
    
    # If not found, try Indian database
    if not result or not result.get('ingredients_text'):
        result = search_indian_database(product_name)
    
    return result


def fetch_all_products(product_name):
    """
    Fast fetch of products from all sources with caching
    """
    from django.core.cache import cache
    
    cache_key = f"products_{product_name.lower().strip()}"
    cached_result = cache.get(cache_key)
    
    if cached_result is not None:
        return cached_result
    
    # Get from Open Beauty Facts (max 4)
    api_products = ProductAPIService.search_all_products(product_name)[:4]
    
    # Get from Indian database (max 3)
    indian_products = search_indian_database_all(product_name)[:3]
    
    # Combine and limit to 7 total
    all_products = (api_products + indian_products)[:7]
    
    # Cache for 10 minutes
    cache.set(cache_key, all_products, 600)
    
    return all_products