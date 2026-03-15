from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extended user profile with health information for personalized analysis
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField()
    allergies = models.TextField(blank=True, help_text="Comma-separated list of allergies")
    health_conditions = models.TextField(blank=True, help_text="Comma-separated list of health conditions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_allergies_list(self):
        """Returns allergies as a list"""
        if self.allergies:
            return [allergy.strip().lower() for allergy in self.allergies.split(',')]
        return []
    
    def get_health_conditions_list(self):
        """Returns health conditions as a list"""
        if self.health_conditions:
            return [condition.strip().lower() for condition in self.health_conditions.split(',')]
        return []
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Scan(models.Model):
    """
    Stores scan results from both image upload and product search
    """
    SAFETY_CHOICES = [
        ('SAFE', 'Safe'),
        ('CAUTION', 'Caution'),
        ('HARMFUL', 'Harmful'),
    ]
    
    SOURCE_CHOICES = [
        ('IMAGE', 'Image Upload'),
        ('SEARCH', 'Product Search'),
    ]
    
    INGREDIENT_SOURCE_CHOICES = [
        ('ANIMAL', 'Animal-Derived'),
        ('PLANT', 'Plant-Derived'),
        ('SYNTHETIC', 'Synthetic'),
        ('MIXED', 'Mixed'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    # Link to user (optional for guest mode)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='scans')
    
    # Source of scan
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='IMAGE')
    
    # Product information
    product_name = models.CharField(max_length=255, blank=True, null=True)
    product_brand = models.CharField(max_length=255, blank=True, null=True)
    
    # Image-based scan data
    image = models.ImageField(upload_to='scans/', blank=True, null=True)
    extracted_text = models.TextField(blank=True)
    
    # Ingredient analysis results
    ingredients_list = models.TextField(blank=True)  # Raw ingredients text
    harmful_ingredients = models.JSONField(default=list)
    safety_rating = models.CharField(max_length=10, choices=SAFETY_CHOICES, default='SAFE')
    ingredient_source = models.CharField(max_length=15, choices=INGREDIENT_SOURCE_CHOICES, default='UNKNOWN')
    
    # Personalized analysis (for logged-in users or guest input)
    user_age = models.PositiveIntegerField(null=True, blank=True)
    user_allergies = models.TextField(blank=True)
    user_health_conditions = models.TextField(blank=True)
    personalized_warnings = models.JSONField(default=list)  # Age/allergy/health warnings
    
    # Animal-derived ingredients found
    animal_ingredients = models.JSONField(default=list)
    
    # Metadata
    scanned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scanned_at']
    
    def __str__(self):
        if self.product_name:
            return f"{self.product_name} - {self.safety_rating}"
        return f"Scan {self.id} - {self.safety_rating} ({self.scanned_at.strftime('%Y-%m-%d %H:%M')})"


class SearchHistory(models.Model):
    """
    Tracks product searches for registered users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='history_entries')
    searched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-searched_at']
        verbose_name_plural = 'Search Histories'
    
    def __str__(self):
        return f"{self.user.username} - {self.scan.product_name or 'Image Scan'} ({self.searched_at.strftime('%Y-%m-%d %H:%M')})"