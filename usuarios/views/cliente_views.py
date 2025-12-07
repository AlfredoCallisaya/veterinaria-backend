from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from ..models import Usuario, Mascota
from ..serializers import UsuarioSerializer, ClienteConMascotasSerializer
from ..services import ClienteService

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    cliente_service = ClienteService()

    def get_queryset(self):
        # Solo usuarios con rol Cliente
        return Usuario.objects.filter(rol_nombre='Cliente')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ClienteConMascotasSerializer
        return UsuarioSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Crear un nuevo cliente (usuario con rol Cliente)"""
        try:
            data = request.data.copy()
            data['rol_nombre'] = 'Cliente'
            
            # Si no viene contraseña, asignar una por defecto
            if not data.get('contrasena'):
                data['contrasena'] = 'cliente123'
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            cliente = serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error al crear cliente: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    # ✅ LÓGICA DE NEGOCIO: Validar eliminación
    @action(detail=True, methods=['get'])
    def validar_eliminacion(self, request, pk=None):
        cliente = self.get_object()
        try:
            resultado = self.cliente_service.validar_eliminacion(cliente)
            return Response(resultado)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    # ✅ LÓGICA DE NEGOCIO: Validar desactivación
    @action(detail=True, methods=['get'])
    def validar_desactivacion(self, request, pk=None):
        cliente = self.get_object()
        try:
            resultado = self.cliente_service.validar_desactivacion(cliente)
            return Response(resultado)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    # ✅ LÓGICA DE NEGOCIO: Cambiar estado
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        cliente = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'Estado es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cliente_actualizado = self.cliente_service.cambiar_estado(cliente, nuevo_estado)
            serializer = self.get_serializer(cliente_actualizado)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )