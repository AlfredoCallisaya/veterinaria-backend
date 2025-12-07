from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Mascota
from .serializers import (
    MascotaSerializer,
    MascotaCreateSerializer,
    MascotaUpdateSerializer,
    MascotaListSerializer
)
from .services import MascotaService

class MascotaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Mascota.objects.all().select_related('usuario')
        
        # Filtrar por búsqueda
        search_term = self.request.query_params.get('search', '')
        if search_term:
            queryset = MascotaService.buscar_mascotas(search_term)
        
        # Filtrar por estado si se especifica
        estado = self.request.query_params.get('estado', '')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MascotaCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MascotaUpdateSerializer
        elif self.action == 'list':
            return MascotaListSerializer
        return MascotaSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear nueva mascota"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            mascota = MascotaService.crear_mascota(serializer.validated_data)
            
            # Usar el serializer completo para la respuesta
            response_serializer = MascotaSerializer(mascota)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """Actualizar mascota existente"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            
            mascota = MascotaService.actualizar_mascota(
                instance.id, 
                serializer.validated_data
            )
            
            response_serializer = MascotaSerializer(mascota)
            return Response(response_serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado de una mascota"""
        try:
            nuevo_estado = request.data.get('estado')
            
            if not nuevo_estado:
                return Response(
                    {'error': 'El estado es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            mascota = MascotaService.cambiar_estado_mascota(pk, nuevo_estado)
            serializer = MascotaSerializer(mascota)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar una mascota"""
        try:
            mascota = MascotaService.cambiar_estado_mascota(pk, 'Activo')
            serializer = MascotaSerializer(mascota)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar una mascota"""
        try:
            mascota = MascotaService.cambiar_estado_mascota(pk, 'Inactivo')
            serializer = MascotaSerializer(mascota)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar mascota (eliminación suave)"""
        try:
            mascota = MascotaService.eliminar_mascota(kwargs['pk'])
            serializer = MascotaSerializer(mascota)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def por_cliente(self, request):
        """Obtener mascotas por cliente"""
        try:
            cliente_id = request.query_params.get('cliente_id')
            if not cliente_id:
                return Response(
                    {'error': 'El ID del cliente es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            mascotas = MascotaService.obtener_mascotas_por_cliente(cliente_id)
            serializer = MascotaListSerializer(mascotas, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': 'Error al obtener mascotas del cliente'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de mascotas"""
        try:
            stats = MascotaService.obtener_estadisticas()
            return Response(stats)
        except Exception as e:
            return Response(
                {'error': 'Error al obtener estadísticas'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def especies(self, request):
        """Obtener lista de especies disponibles"""
        especies = [choice[0] for choice in Mascota.ESPECIE_CHOICES]
        return Response(especies)