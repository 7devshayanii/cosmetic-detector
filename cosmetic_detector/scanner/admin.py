from django.contrib import admin
from .models import Scan


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ['id', 'safety_rating', 'veg_status', 'scanned_at']
    list_filter = ['safety_rating', 'veg_status', 'scanned_at']
    search_fields = ['extracted_text']
    readonly_fields = ['scanned_at']
    
    fieldsets = (
        ('Scan Information', {
            'fields': ('image', 'scanned_at')
        }),
        ('Extracted Data', {
            'fields': ('extracted_text',)
        }),
        ('Analysis Results', {
            'fields': ('harmful_ingredients', 'safety_rating', 'veg_status')
        }),
    )
