from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Consulta, Mascota
from ..serializers import ConsultaSerializer, ConsultaConDetallesSerializer, MascotaConConsultasSerializer
from ..services import ConsultaService

class ConsultaViewSet(viewsets.ModelViewSet):
    queryset = Consulta.objects.all()
    consulta_service = ConsultaService()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ConsultaConDetallesSerializer
        return ConsultaSerializer

    def get_queryset(self):
        return Consulta.objects.select_related('mascota', 'veterinario').all()

    @action(detail=False, methods=['get'])
    def por_mascota(self, request, mascota_id=None):
        """Obtiene todas las consultas de una mascota específica"""
        try:
            consultas = self.consulta_service.obtener_consultas_por_mascota(mascota_id)
            serializer = self.get_serializer(consultas, many=True)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def mascotas_con_historial(self, request):
        """Obtiene mascotas con su historial de consultas"""
        try:
            mascotas = self.consulta_service.obtener_mascotas_con_historial()
            serializer = MascotaConConsultasSerializer(mascotas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de consultas"""
        try:
            estadisticas = self.consulta_service.obtener_estadisticas()
            return Response(estadisticas)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def generar_receta(self, request, pk=None):
        """Genera una receta médica para la consulta"""
        consulta = self.get_object()
        try:
            receta = self.consulta_service.generar_receta_medica(consulta)
            return Response(receta)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )