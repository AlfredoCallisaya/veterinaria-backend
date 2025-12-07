from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, RolViewSet, PersonaViewSet, ClienteViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolViewSet)
router.register(r'personas', PersonaViewSet)
router.register(r'clientes', ClienteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
