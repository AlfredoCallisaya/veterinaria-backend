from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Todas las rutas de la API comienzan con /api/
    path('api/', include('usuarios.urls')),
    path('api/clinica/', include('clinica.urls')),
    # ... otras apps
]