# pyright: reportMissingImports=false
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .backends import EmailBackend
from .models import UsuarioPersonalizado, Rol
from .serializers import UsuarioSerializer, UsuarioCreateSerializer, RolSerializer
import jwt
import datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def login_api(request):
    correo = request.data.get('correo')
    password = request.data.get('password')
    
    if not correo or not password:
        return Response(
            {'error': 'Correo y contraseña son requeridos'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    backend = EmailBackend()
    user = backend.authenticate(request, username=correo, password=password)
    
    if user is not None:
        # Crear token JWT
        payload = {
            'id': user.id,
            'correo': user.correo,
            'nombres': user.nombres,
            'apellidos': user.apellidos,
            'rol': user.idRol.nombreRol if user.idRol else None,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Hacer login en sesión Django (opcional)
        login(request, user, backend='usuarios.backends.EmailBackend')
        
        return Response({
            'token': token,
            'usuario': {
                'id': user.id,
                'nombres': user.nombres,
                'apellidos': user.apellidos,
                'correo': user.correo,
                'rol': user.idRol.nombreRol if user.idRol else None,
            }
        })
    
    return Response(
        {'error': 'Correo o contraseña incorrectos'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
def logout_api(request):
    logout(request)
    return Response({'message': 'Sesión cerrada correctamente'})

@api_view(['GET'])
def perfil_usuario(request):
    """Obtener información del usuario autenticado"""
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
def lista_usuarios_api(request):
    """Listar todos los usuarios (solo admin/superuser)"""
    if not (request.user.is_superuser or (request.user.idRol and request.user.idRol.nombreRol == 'Administrador')):
        return Response(
            {'error': 'No tienes permisos para acceder a esta sección'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    usuarios = UsuarioPersonalizado.objects.all()
    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def crear_usuario_api(request):
    """Crear nuevo usuario (solo admin/superuser)"""
    if not (request.user.is_superuser or (request.user.idRol and request.user.idRol.nombreRol == 'Administrador')):
        return Response(
            {'error': 'No tienes permisos para esta acción'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = UsuarioCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            # Verificar si el correo ya existe
            if UsuarioPersonalizado.objects.filter(correo=serializer.validated_data['correo']).exists():
                return Response(
                    {'error': 'Este correo electrónico ya está registrado'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            usuario = serializer.save()
            return Response(
                {'message': f'Usuario {usuario.nombres} {usuario.apellidos} registrado exitosamente'},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Error al registrar usuario: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def lista_roles_api(request):
    """Listar todos los roles"""
    roles = Rol.objects.all()
    serializer = RolSerializer(roles, many=True)
    return Response(serializer.data)

# Middleware para autenticación JWT
class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir login de la autenticación
        if request.path in ['/api/usuarios/login/', '/api/usuarios/verificar-token/']:
            return self.get_response(request)
            
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user = UsuarioPersonalizado.objects.get(id=payload['id'])
                request.user = user
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, UsuarioPersonalizado.DoesNotExist):
                pass
        
        return self.get_response(request)