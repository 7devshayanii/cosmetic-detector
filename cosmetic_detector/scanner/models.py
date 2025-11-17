from django.db import models

class Scan(models.Model):
    SAFETY_CHOICES = [
        ('SAFE', 'Safe'),
        ('CAUTION', 'Caution'),
        ('HARMFUL', 'Harmful'),
    ]
    
    VEG_CHOICES = [
        ('VEG', 'Vegetarian'),
        ('NON_VEG', 'Non-Vegetarian'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    image = models.ImageField(upload_to='scans/')
    extracted_text = models.TextField(blank=True)
    harmful_ingredients = models.JSONField(default=list)
    safety_rating = models.CharField(max_length=10, choices=SAFETY_CHOICES, default='SAFE')
    veg_status = models.CharField(max_length=10, choices=VEG_CHOICES, default='UNKNOWN')
    scanned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scanned_at']
    
    def __str__(self):
        return f"Scan {self.id} - {self.safety_rating} ({self.scanned_at.strftime('%Y-%m-%d %H:%M')})"
