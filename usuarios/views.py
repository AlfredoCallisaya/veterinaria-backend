# usuarios/views.py

from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Usuario, Rol, Persona, Cliente
from .serializers import (
    LoginSerializer,
    UsuarioSerializer,
    RegistroSerializer,
    PersonaSerializer,
    RolSerializer,
    ClienteSerializer
)
from .permissions import IsAdminOnly, IsAdminOrReadOnly


# =============================
# 1. LOGIN JWT
# =============================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = LoginSerializer


# =============================
# 2. PERFIL DE USUARIO AUTENTICADO
# =============================
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user  # más seguro
        persona = getattr(usuario, 'persona', None)
        roles_data = [rol.nombre for rol in usuario.roles.all()]

        return Response({
            "usuario": UsuarioSerializer(usuario).data,
            "persona": PersonaSerializer(persona).data if persona else None,
            "roles": roles_data
        })


# =============================
# 3. REGISTRO (CREA USUARIO + PERSONA + ROL)
# =============================
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer

    def perform_create(self, serializer):
        serializer.save()


# =============================
# 4. CRUD DE USUARIOS (ADMIN)
# =============================
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().prefetch_related("roles")
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, IsAdminOnly]

    def perform_create(self, serializer):
        serializer.save(usuario_creacion=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario_modificacion=self.request.user)


# =============================
# 5. CRUD DE ROLES (SOLO ADMIN EDITA)
# =============================
class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


# =============================
# 6. CRUD DE PERSONAS
# =============================
class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer
    permission_classes = [IsAuthenticated]


# =============================
# 7. CRUD DE CLIENTES
# =============================
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
