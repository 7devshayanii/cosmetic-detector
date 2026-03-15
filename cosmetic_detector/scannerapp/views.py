from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from PIL import Image
import pytesseract
import json
import re
from .models import Scan, SearchHistory, UserProfile
from .ingredient_analyzer import analyze_ingredients
from .product_api_service import fetch_product_ingredients


def index(request):
    """Main page with upload and search functionality"""
    context = {}
    
    # If user is logged in, get their profile for auto-fill
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            context['user_profile'] = profile
        except UserProfile.DoesNotExist:
            context['user_profile'] = None
    
    return render(request, 'index.html', context)


def disclaimer_view(request):
    """Display comprehensive disclaimer and terms"""
    return render(request, 'disclaimer.html')


def results(request, scan_id):
    """Display scan results with personalized analysis"""
    scan = get_object_or_404(Scan, id=scan_id)
    
    # Highlight harmful ingredients in extracted text
    harmful_names = [item['name'] for item in scan.harmful_ingredients]
    
    if scan.source == 'IMAGE':
        text_to_highlight = scan.extracted_text
    else:
        text_to_highlight = scan.ingredients_list
    
    highlighted_text = text_to_highlight
    for name in harmful_names:
        highlighted_text = re.sub(
            re.escape(name), 
            f'<span class="highlight">{name}</span>', 
            highlighted_text, 
            flags=re.IGNORECASE
        )
    
    context = {
        'scan': scan,
        'extracted_text': text_to_highlight,
        'highlighted_text': mark_safe(highlighted_text),
        'harmful_ingredients': scan.harmful_ingredients,
        'safety_rating': scan.safety_rating,
        'ingredient_source': scan.ingredient_source,
        'personalized_warnings': scan.personalized_warnings,
        'animal_ingredients': scan.animal_ingredients,
    }
    
    return render(request, 'results.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def scan_image(request):
    """
    Handle image upload, OCR extraction, and ingredient analysis
    This is the existing flow - DO NOT CHANGE
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        image_file = request.FILES['image']
        
        # Get user info if logged in or from guest form
        user = request.user if request.user.is_authenticated else None
        user_age = None
        user_allergies = ''
        user_health_conditions = ''
        
        if user and hasattr(user, 'profile'):
            profile = user.profile
            user_age = profile.age
            user_allergies = profile.allergies
            user_health_conditions = profile.health_conditions
        else:
            # Get from POST data (guest mode)
            user_age = request.POST.get('age')
            user_allergies = request.POST.get('allergies', '')
            user_health_conditions = request.POST.get('health_conditions', '')
            
            if user_age:
                user_age = int(user_age)
        
        # Create scan record
        scan = Scan(
            image=image_file,
            source='IMAGE',
            user=user,
            user_age=user_age,
            user_allergies=user_allergies,
            user_health_conditions=user_health_conditions
        )
        scan.save()
        
        # Extract text using OCR
        try:
            img = Image.open(scan.image.path)
            extracted_text = pytesseract.image_to_string(img)
        except Exception as ocr_error:
            # Handle OCR failures (Tesseract not installed, etc.)
            scan.extracted_text = f'OCR Error: {str(ocr_error)}'
            scan.safety_rating = 'UNKNOWN'
            scan.ingredient_source = 'UNKNOWN'
            scan.save()
            
            return JsonResponse({
                'error': 'OCR (text recognition) is not available. Please install Tesseract OCR or try searching for products by name instead.',
                'scan_id': scan.id
            }, status=500)
        
        if not extracted_text.strip():
            scan.extracted_text = 'No text detected'
            scan.safety_rating = 'UNKNOWN'
            scan.ingredient_source = 'UNKNOWN'
            scan.save()
            
            return JsonResponse({
                'success': False,
                'error': 'Text is not visible in the image. Please ensure the product label is clearly visible and try again.',
                'scan_id': scan.id
            }, status=400)
        
        # Analyze ingredients with personalized data
        analysis = analyze_ingredients(
            extracted_text,
            user_age=user_age,
            user_allergies=user_allergies,
            user_health_conditions=user_health_conditions
        )
        
        # Update scan with analysis results
        scan.extracted_text = extracted_text
        scan.ingredients_list = extracted_text
        scan.harmful_ingredients = analysis['harmful_ingredients']
        scan.safety_rating = analysis['safety_rating']
        scan.ingredient_source = analysis['ingredient_source']
        scan.animal_ingredients = analysis.get('animal_ingredients', [])
        scan.personalized_warnings = analysis.get('personalized_warnings', [])
        scan.save()
        
        # Save to search history if user is logged in
        if user:
            SearchHistory.objects.create(user=user, scan=scan)
        
        return JsonResponse({
            'success': True,
            'scan_id': scan.id
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def search_product(request):
    """
    Handle product search by name using external API
    Smart detection: brand-only vs specific product
    """
    try:
        data = json.loads(request.body)
        product_name = data.get('product_name', '').strip()
        
        if not product_name:
            return JsonResponse({'error': 'Product name is required'}, status=400)
        
        # Get user info if logged in or from request
        user = request.user if request.user.is_authenticated else None
        user_age = data.get('age')
        user_allergies = data.get('allergies', '')
        user_health_conditions = data.get('health_conditions', '')
        
        if user and hasattr(user, 'profile'):
            profile = user.profile
            user_age = user_age or profile.age
            user_allergies = user_allergies or profile.allergies
            user_health_conditions = user_health_conditions or profile.health_conditions
        
        # Convert user_age to int if it's not empty, otherwise set to None
        if user_age and str(user_age).strip():
            user_age = int(user_age)
        else:
            user_age = None
        
        # Fetch ALL matching products
        from .product_api_service import fetch_all_products
        all_products = fetch_all_products(product_name)
        
        if not all_products:
            return JsonResponse({
                'error': f'No products found for "{product_name}"',
                'suggestions': [
                    'Upload product image instead',
                    'Search specific product name',
                    'Check spelling'
                ]
            }, status=404)
        
        # SMART DETECTION: Brand-only vs Specific product
        word_count = len(product_name.split())
        products_found = len(all_products)
        
        # If brand-only search (word count <= 2 AND multiple products found)
        if word_count <= 2 and products_found > 3:
            # Return product list for selection
            return JsonResponse({
                'multiple_products': True,
                'products': all_products,
                'search_term': product_name,
                'user_data': {
                    'age': user_age,
                    'allergies': user_allergies,
                    'health_conditions': user_health_conditions
                }
            })
        
        # Specific product search - analyze directly
        product_data = all_products[0]  # Take first match
        
        if not product_data.get('ingredients_text'):
            return JsonResponse({
                'error': f'No ingredient information available for "{product_data["product_name"]}"'
            }, status=404)
        
        # Analyze ingredients
        analysis = analyze_ingredients(
            product_data['ingredients_text'],
            user_age=user_age,
            user_allergies=user_allergies,
            user_health_conditions=user_health_conditions
        )
        
        # Create scan record for search result
        scan = Scan(
            source='SEARCH',
            user=user,
            product_name=product_data['product_name'],
            product_brand=product_data.get('brand', 'Unknown'),
            ingredients_list=product_data['ingredients_text'],
            harmful_ingredients=analysis['harmful_ingredients'],
            safety_rating=analysis['safety_rating'],
            ingredient_source=analysis['ingredient_source'],
            animal_ingredients=analysis.get('animal_ingredients', []),
            user_age=user_age,
            user_allergies=user_allergies,
            user_health_conditions=user_health_conditions,
            personalized_warnings=analysis.get('personalized_warnings', [])
        )
        scan.save()
        
        # Save to search history if user is logged in
        if user:
            SearchHistory.objects.create(user=user, scan=scan)
        
        return JsonResponse({
            'success': True,
            'scan_id': scan.id,
            'product_name': product_data['product_name'],
            'brand': product_data.get('brand', 'Unknown')
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_selected_product(request):
    """
    Analyze a specific product selected from the product list
    """
    try:
        data = json.loads(request.body)
        product_data = data.get('product')
        user_data = data.get('user_data', {})
        
        if not product_data:
            return JsonResponse({'error': 'Product data is required'}, status=400)
        
        # Check if product has ingredients
        if not product_data.get('ingredients_text'):
            return JsonResponse({'error': f'No ingredient information available for "{product_data.get("product_name", "this product")}"'}, status=404)
        
        # Get user info
        user = request.user if request.user.is_authenticated else None
        user_age = user_data.get('age')
        user_allergies = user_data.get('allergies', '')
        user_health_conditions = user_data.get('health_conditions', '')
        
        if user and hasattr(user, 'profile'):
            profile = user.profile
            user_age = user_age or profile.age
            user_allergies = user_allergies or profile.allergies
            user_health_conditions = user_health_conditions or profile.health_conditions
        
        # Convert user_age to int if it's not empty, otherwise set to None
        if user_age and str(user_age).strip():
            user_age = int(user_age)
        else:
            user_age = None
        
        # Analyze ingredients
        analysis = analyze_ingredients(
            product_data['ingredients_text'],
            user_age=user_age,
            user_allergies=user_allergies,
            user_health_conditions=user_health_conditions
        )
        
        # Create scan record
        scan = Scan(
            source='SEARCH',
            user=user,
            product_name=product_data['product_name'],
            product_brand=product_data.get('brand', 'Unknown'),
            ingredients_list=product_data['ingredients_text'],
            harmful_ingredients=analysis['harmful_ingredients'],
            safety_rating=analysis['safety_rating'],
            ingredient_source=analysis['ingredient_source'],
            animal_ingredients=analysis.get('animal_ingredients', []),
            user_age=user_age,
            user_allergies=user_allergies,
            user_health_conditions=user_health_conditions,
            personalized_warnings=analysis.get('personalized_warnings', [])
        )
        scan.save()
        
        # Save to search history if user is logged in
        if user:
            SearchHistory.objects.create(user=user, scan=scan)
        
        return JsonResponse({
            'success': True,
            'scan_id': scan.id,
            'product_name': product_data['product_name'],
            'brand': product_data.get('brand', 'Unknown')
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def search_history(request):
    """Display user's search history"""
    history = SearchHistory.objects.filter(user=request.user).select_related('scan')
    
    context = {
        'history': history
    }
    
    return render(request, 'history.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def delete_history_item(request, history_id):
    """Delete a specific history item"""
    try:
        history_item = get_object_or_404(SearchHistory, id=history_id, user=request.user)
        scan = history_item.scan
        
        # Delete history entry
        history_item.delete()
        
        # Delete scan if no other history entries reference it
        if not SearchHistory.objects.filter(scan=scan).exists():
            scan.delete()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def clear_all_history(request):
    """Clear all search history for the current user"""
    try:
        # Get all history items
        history_items = SearchHistory.objects.filter(user=request.user)
        scan_ids = list(history_items.values_list('scan_id', flat=True))
        
        # Delete all history entries
        history_items.delete()
        
        # Delete scans that are no longer referenced
        for scan_id in scan_ids:
            if not SearchHistory.objects.filter(scan_id=scan_id).exists():
                Scan.objects.filter(id=scan_id).delete()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def products_view(request):
    """Display multiple products for selection"""
    search_term = request.GET.get('search', '')
    products_json = request.GET.get('products', '[]')
    
    try:
        products = json.loads(products_json)
    except Exception:
        products = []
    
    context = {
        'search_term': search_term,
        'products': products,
        'user_data': {
            'age': request.GET.get('age'),
            'allergies': request.GET.get('allergies', ''),
            'health_conditions': request.GET.get('health_conditions', '')
        }
    }
    
    return render(request, 'products.html', context)


# =============================================
# AUTHENTICATION VIEWS
# =============================================

def register_view(request):
    """User registration page"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        age = request.POST.get('age', '')
        allergies = request.POST.get('allergies', '').strip()
        health_conditions = request.POST.get('health_conditions', '').strip()
        
        # Validate required fields
        if not name:
            messages.error(request, 'Full name is required.')
            return redirect('register')
        
        if not email:
            messages.error(request, 'Email is required.')
            return redirect('register')
        
        if not password1 or not password2:
            messages.error(request, 'Passwords are required.')
            return redirect('register')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('register')
        
        if not age:
            messages.error(request, 'Age is required.')
            return redirect('register')
        
        # Validate age
        try:
            age_int = int(age)
            if age_int < 1 or age_int > 120:
                messages.error(request, 'Age must be between 1 and 120.')
                return redirect('register')
        except ValueError:
            messages.error(request, 'Age must be a valid number.')
            return redirect('register')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if User.objects.filter(username=name).exists():
            messages.error(request, 'This name is already taken. Please choose a different one.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered. Please use a different email or login.')
            return redirect('register')
        
        try:
            user = User.objects.create_user(username=name, email=email, password=password1)
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                age=age_int,
                allergies=allergies or '',
                health_conditions=health_conditions or ''
            )
            
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Cosmetic Detector.')
            return redirect('index')
        except Exception as e:
            messages.error(request, f'An error occurred during registration. Please try again.')
            return redirect('register')
    
    return render(request, 'register.html')


def login_view(request):
    """User login page"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Try to get user by email
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
    
    return render(request, 'login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


@login_required
def profile_view(request):
    """User profile page"""
    if request.method == 'POST':
        age = request.POST.get('age')
        allergies = request.POST.get('allergies')
        health_conditions = request.POST.get('health_conditions')
        
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if age:
            profile.age = int(age)
        profile.allergies = allergies
        profile.health_conditions = health_conditions
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('index')
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = None
    
    context = {
        'profile': profile
    }
    return render(request, 'profile.html', context)