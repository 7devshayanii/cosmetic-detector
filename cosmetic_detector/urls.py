from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cosmetic_detector.scannerapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Internationalization URL removed
    
    # Main pages
    path('', views.index, name='index'),
    path('results/<int:scan_id>/', views.results, name='results'),
    path('disclaimer/', views.disclaimer_view, name='disclaimer'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('products/', views.products_view, name='products'),
    
    # API endpoints
    path('api/scan/', views.scan_image, name='scan_image'),  # Existing image upload
    path('api/search/', views.search_product, name='search_product'),  # Product search
    path('api/analyze-product/', views.analyze_selected_product, name='analyze_selected_product'),  # Analyze selected product
    
    # User history (for logged-in users)
    path('history/', views.search_history, name='search_history'),
    path('api/history/delete/<int:history_id>/', views.delete_history_item, name='delete_history_item'),
    path('api/history/clear/', views.clear_all_history, name='clear_all_history'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)