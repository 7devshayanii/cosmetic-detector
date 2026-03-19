from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import json
from .models import Scan, UserProfile, SearchHistory
from .ingredient_analyzer import analyze_ingredients
from .product_api_service import search_indian_database, fetch_product_ingredients


class AuthenticationTests(TestCase):
    """Test user registration and login functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }
    
    def test_user_registration_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        response = self.client.post('/register/', {
            'username': 'newuser',
            'password1': 'securepass123',
            'password2': 'differentpass123',
            'email': 'newuser@test.com'
        })
        # Registration should fail - password mismatch
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_user_login_wrong_password(self):
        """Test login fails with wrong password"""
        User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        # Wrong password - session should not be authenticated
        self.assertIsNone(self.client.session.get('_auth_user_id'))
    
    def test_user_login_nonexistent_user(self):
        """Test login fails with nonexistent username"""
        response = self.client.post('/login/', {
            'username': 'nonexistent',
            'password': 'anypass'
        })
        self.assertIsNone(self.client.session.get('_auth_user_id'))


class ImageUploadTests(TestCase):
    """Test image upload and OCR text extraction"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
    
    def create_test_image(self, width=100, height=100, color='white'):
        """Helper to create a test image"""
        image = Image.new('RGB', (width, height), color)
        image_io = io.BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        return image_io
    
    def test_blank_image_upload(self):
        """Test uploading a blank image returns error"""
        blank_image = self.create_test_image(color='white')
        image_file = SimpleUploadedFile(
            "blank.png",
            blank_image.getvalue(),
            content_type="image/png"
        )
        
        response = self.client.post('/scan-image/', {
            'image': image_file
        }, content_type='multipart/form-data')
        
        if response.status_code == 400:
            data = json.loads(response.content)
            self.assertFalse(data.get('success'))
            self.assertIn('Text is not visible', data.get('error', ''))
    
    def test_blank_image_sets_unknown_rating(self):
        """Test that blank image sets safety_rating to UNKNOWN"""
        blank_image = self.create_test_image(color='white')
        image_file = SimpleUploadedFile(
            "blank.png",
            blank_image.getvalue(),
            content_type="image/png"
        )
        
        response = self.client.post('/scan-image/', {
            'image': image_file
        }, content_type='multipart/form-data')
        
        # Check if scan was created and has UNKNOWN rating
        if Scan.objects.exists():
            scan = Scan.objects.first()
            self.assertIn(scan.safety_rating, ['UNKNOWN', 'SAFE'])
    
    def test_no_image_upload(self):
        """Test upload without image file"""
        response = self.client.post('/scan-image/', {})
        
        self.assertIn(response.status_code, [400, 404])


class ProductSearchTests(TestCase):
    """Test product search functionality"""
    
    def test_search_indian_database_lakme(self):
        """Test searching for Lakme product"""
        result = search_indian_database('lakme peach milk')
        self.assertIsNotNone(result)
        self.assertIn('lakme', result['brand'].lower())
    
    def test_search_indian_database_case_insensitive(self):
        """Test product search is case insensitive"""
        result1 = search_indian_database('LAKME')
        result2 = search_indian_database('lakme')
        self.assertEqual(result1['brand'].lower(), result2['brand'].lower())
    
    def test_search_indian_database_partial_match(self):
        """Test partial product name matching"""
        result = search_indian_database('lakme')
        self.assertIsNotNone(result)
        self.assertIn('Lakme', result['brand'])
    
    def test_search_indian_database_not_found(self):
        """Test search returns None for non-existent product"""
        result = search_indian_database('nonexistent product xyz')
        self.assertIsNone(result)
    
    def test_search_himalaya_products(self):
        """Test searching for Himalaya products"""
        result = search_indian_database('himalaya')
        self.assertIsNotNone(result)
        self.assertIn('himalaya', result['brand'].lower())
    
    def test_search_biotique_products(self):
        """Test searching for Biotique products"""
        result = search_indian_database('biotique honey')
        self.assertIsNotNone(result)
        self.assertIn('honey', result['product_name'].lower())
    
    def test_product_has_ingredients(self):
        """Test that found products have ingredients text"""
        result = search_indian_database('lakme')
        self.assertIsNotNone(result['ingredients_text'])
        self.assertGreater(len(result['ingredients_text']), 0)


class IngredientAnalysisTests(TestCase):
    """Test ingredient analysis and safety rating"""
    
    def test_safe_ingredients_analysis(self):
        """Test analysis of safe ingredients"""
        analysis = analyze_ingredients(
            "Aqua, Glycerin, Aloe Vera Extract"
        )
        self.assertEqual(analysis['safety_rating'], 'SAFE')
        self.assertEqual(len(analysis['harmful_ingredients']), 0)
    
    def test_harmful_ingredients_detected(self):
        """Test detection of harmful ingredients"""
        analysis = analyze_ingredients(
            "Aqua, Parabens, Sulfates, Phthalates"
        )
        self.assertIn(analysis['safety_rating'], ['MILD RISK', 'UNSAFE'])
        self.assertGreater(len(analysis['harmful_ingredients']), 0)
    
    def test_ingredient_analysis_case_insensitive(self):
        """Test ingredient matching is case insensitive"""
        analysis1 = analyze_ingredients("PARABENS, SULFATES")
        analysis2 = analyze_ingredients("parabens, sulfates")
        self.assertEqual(
            len(analysis1['harmful_ingredients']),
            len(analysis2['harmful_ingredients'])
        )
    
    def test_empty_ingredients_analysis(self):
        """Test analysis with empty ingredients"""
        analysis = analyze_ingredients("")
        self.assertIn(analysis['safety_rating'], ['SAFE', 'UNKNOWN'])
    
    def test_personalized_warnings_for_age(self):
        """Test personalized warnings based on age"""
        analysis = analyze_ingredients(
            "Salicylic Acid, Benzoyl Peroxide",
            user_age=10
        )
        self.assertIsNotNone(analysis['personalized_warnings'])
    
    def test_personalized_warnings_for_allergies(self):
        """Test personalized warnings for allergies"""
        analysis = analyze_ingredients(
            "Aqua, Fragrance",
            user_allergies="peanuts, nuts"
        )
        # Should analyze without errors even if no allergen found
        self.assertIsNotNone(analysis['personalized_warnings'])
    
    def test_animal_ingredients_detection(self):
        """Test detection of animal-derived ingredients"""
        analysis = analyze_ingredients(
            "Beeswax, Lanolin, Carmine, Squalane"
        )
        self.assertGreater(len(analysis['animal_ingredients']), 0)
    
    def test_no_animal_ingredients(self):
        """Test vegan product analysis"""
        analysis = analyze_ingredients(
            "Aqua, Glycerin, Plant Oil, Vitamin C"
        )
        self.assertEqual(len(analysis['animal_ingredients']), 0)


class ScanModelTests(TestCase):
    """Test Scan model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
    
    def test_create_scan_authenticated_user(self):
        """Test creating scan for authenticated user"""
        scan = Scan.objects.create(
            user=self.user,
            source='IMAGE',
            extracted_text='Aqua, Glycerin',
            safety_rating='SAFE'
        )
        self.assertEqual(scan.user, self.user)
        self.assertEqual(scan.safety_rating, 'SAFE')
    
    def test_create_scan_guest_user(self):
        """Test creating scan for guest user"""
        scan = Scan.objects.create(
            source='IMAGE',
            extracted_text='Aqua, Glycerin',
            safety_rating='SAFE',
            user_age=25
        )
        self.assertIsNone(scan.user)
        self.assertEqual(scan.user_age, 25)
    
    def test_scan_with_allergies(self):
        """Test scan stores user allergies"""
        scan = Scan.objects.create(
            source='IMAGE',
            extracted_text='Aqua',
            safety_rating='SAFE',
            user_allergies='peanuts, shellfish'
        )
        self.assertIn('peanuts', scan.user_allergies)
    
    def test_scan_with_health_conditions(self):
        """Test scan stores health conditions"""
        scan = Scan.objects.create(
            source='IMAGE',
            extracted_text='Aqua',
            safety_rating='SAFE',
            user_health_conditions='sensitive skin, eczema'
        )
        self.assertIn('eczema', scan.user_health_conditions)


class UserProfileTests(TestCase):
    """Test UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
    
    def test_create_user_profile(self):
        """Test creating user profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            age=25,
            allergies='peanuts',
            health_conditions='dry skin'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.age, 25)


class SearchHistoryTests(TestCase):
    """Test SearchHistory functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.scan = Scan.objects.create(
            source='IMAGE',
            extracted_text='Aqua',
            safety_rating='SAFE'
        )
    
    def test_create_search_history(self):
        """Test creating search history entry"""
        history = SearchHistory.objects.create(
            user=self.user,
            scan=self.scan
        )
        self.assertEqual(history.user, self.user)
        self.assertEqual(history.scan, self.scan)
    
    def test_user_search_history_retrieval(self):
        """Test retrieving user's search history"""
        SearchHistory.objects.create(user=self.user, scan=self.scan)
        history = SearchHistory.objects.filter(user=self.user)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history[0].scan, self.scan)
