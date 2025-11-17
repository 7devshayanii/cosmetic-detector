from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from cosmetic_detector.scanner import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('results/<int:scan_id>/', views.results, name='results'),
    path('api/scan/', views.scan_image, name='scan_image'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
