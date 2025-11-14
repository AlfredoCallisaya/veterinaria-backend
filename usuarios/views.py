# usuarios/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import check_password

from .models import Usuario, Rol, Persona
from .serializers import (
    LoginSerializer, UsuarioSerializer, RegistroSerializer, 
    PersonaSerializer, RolSerializer
)

# --- VISTAS DE AUTENTICACIÓN ---

# 1. Login (Generación de Tokens JWT)
# Utilizamos la vista estándar de simplejwt
class CustomTokenObtainPairView(TokenObtainPairView):
    # Serializer personalizado para validar correo/contraseña
    serializer_class = LoginSerializer 

# 2. Logout (No se requiere código de backend en Django para JWT Logout, 
# ya que el frontend simplemente elimina el token)

# 3. Obtener Datos del Usuario Autenticado y sus Roles
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Obtener el Usuario y la Persona relacionada
            usuario = Usuario.objects.get(id=request.user.id)
            persona = usuario.persona

            # Obtener los roles del usuario
            roles_queryset = usuario.roles.all()
            roles_data = [rol.nombre for rol in roles_queryset]
            
            # Serializar la data
            persona_serializer = PersonaSerializer(persona)
            usuario_serializer = UsuarioSerializer(usuario)

            return Response({
                'usuario': usuario_serializer.data,
                'persona': persona_serializer.data,
                'roles': roles_data
            })
        except Usuario.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        # 4. Registro de Clientes/Dueños (Crea Persona, Usuario y asigna Rol 'Dueño')
class RegisterView(generics.CreateAPIView):
    # Permite a cualquiera registrarse
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistroSerializer

    def perform_create(self, serializer):
        # La lógica de creación (Persona, Usuario, asignación de rol 'Dueño')
        # debe estar en el Serializer (RegistroSerializer) para mantener la lógica DRY.
        serializer.save()
        from rest_framework import viewsets
from .permissions import IsAdminOrReadOnly, IsAdminOnly # Necesitas crear permisos personalizados

# 5. Gestión de Usuarios del Sistema (Personal - CRUD)
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().select_related('persona').prefetch_related('roles')
    serializer_class = UsuarioSerializer
    # Solo los administradores pueden gestionar usuarios
    permission_classes = [permissions.IsAuthenticated, IsAdminOnly] 
    
    # Asegurar que se guardan los IDs de auditoría al crear y actualizar
    def perform_create(self, serializer):
        # Asigna al usuario que está logueado como creador
        serializer.save(UsuarioCreacion=self.request.user) 
        
    def perform_update(self, serializer):
        # Asigna al usuario que está logueado como modificador
        serializer.save(UsuarioModificacion=self.request.user) 

# 6. Gestión de Roles (CRUD)
class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    # Similar a UsuarioViewSet, implementas perform_create/update para auditoría.
    # usuarios/permissions.py
from rest_framework import permissions

class IsAdminOnly(permissions.BasePermission):
    """Permite el acceso solo si el usuario tiene el rol 'Administrador'."""
    def has_permission(self, request, view):
        # Verifica si el usuario está autenticado
        if not request.user.is_authenticated:
            return False
            
        # Verifica si el usuario tiene el rol 'Administrador'
        # Nota: La relación N:M requiere un filtro a través de la tabla intermedia
        return request.user.roles.filter(nombre='Administrador').exists()

class IsAdminOrReadOnly(permissions.BasePermission):
    """Permite el acceso de lectura a todos los autenticados y escritura solo al Administrador."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Permiso de escritura solo para el Administrador
        return request.user.roles.filter(nombre='Administrador').exists()