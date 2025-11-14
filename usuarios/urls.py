from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView, RegisterView, UserProfileView

urlpatterns = [
    # 1. Obtener Token (Login)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 2. Refrescar Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 3. Registrar Nuevo Cliente/Dueño
    path('register/', RegisterView.as_view(), name='register'),
    # 4. Obtener perfil y roles del usuario logueado
    path('perfil/', UserProfileView.as_view(), name='user_profile'),
]