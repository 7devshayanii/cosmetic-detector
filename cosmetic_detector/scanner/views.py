from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from PIL import Image
import pytesseract
import json
from .models import Scan
from .ingredient_analyzer import analyze_ingredients


def index(request):
    return render(request, 'index.html')


def results(request):
    return render(request, 'results.html')


@csrf_exempt
@require_http_methods(["POST"])
def scan_image(request):
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        image_file = request.FILES['image']
        
        scan = Scan(image=image_file)
        scan.save()
        
        img = Image.open(scan.image.path)
        
        extracted_text = pytesseract.image_to_string(img)
        
        if not extracted_text.strip():
            return JsonResponse({
                'error': 'No text detected in image',
                'extracted_text': '',
                'harmful_ingredients': [],
                'safety_rating': 'UNKNOWN',
                'veg_status': 'UNKNOWN'
            }, status=200)
        
        analysis = analyze_ingredients(extracted_text)
        
        scan.extracted_text = extracted_text
        scan.harmful_ingredients = analysis['harmful_ingredients']
        scan.safety_rating = analysis['safety_rating']
        scan.veg_status = analysis['veg_status']
        scan.save()
        
        return JsonResponse({
            'success': True,
            'scan_id': scan.id,
            'extracted_text': extracted_text,
            'harmful_ingredients': analysis['harmful_ingredients'],
            'safety_rating': analysis['safety_rating'],
            'veg_status': analysis['veg_status'],
            'animal_ingredients': analysis['animal_ingredients'],
            'harmful_count': analysis['harmful_count']
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
