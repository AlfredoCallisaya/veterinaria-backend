from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Cita, Mascota
from ..serializers import CitaSerializer
from ..services import CitaService

class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer
    cita_service = CitaService()

    # ✅ LÓGICA DE NEGOCIO: Horarios disponibles
    @action(detail=False, methods=['get'])
    def horarios_disponibles(self, request):
        fecha_str = request.query_params.get('fecha')
        if not fecha_str:
            return Response(
                {'error': 'Parámetro fecha es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            horarios = self.cita_service.obtener_horarios_disponibles(fecha)
            return Response(horarios)
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    # ✅ LÓGICA DE NEGOCIO: Validar horario
    @action(detail=False, methods=['get'])
    def validar_horario(self, request):
        fecha_str = request.query_params.get('fecha')
        hora_str = request.query_params.get('hora')
        
        if not fecha_str or not hora_str:
            return Response(
                {'error': 'Parámetros fecha y hora son requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            disponible = self.cita_service.validar_horario_disponible(fecha_str, hora_str)
            return Response({'disponible': disponible})
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    # ✅ LÓGICA DE NEGOCIO: Cambiar estado de cita
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        cita = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if not nuevo_estado:
            return Response(
                {'error': 'Estado es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cita_actualizada = self.cita_service.cambiar_estado(cita, nuevo_estado)
            serializer = self.get_serializer(cita_actualizada)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )