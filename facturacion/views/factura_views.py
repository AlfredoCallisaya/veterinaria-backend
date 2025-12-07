from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Factura, Consulta
from ..serializers import FacturaSerializer, FacturaConDetallesSerializer, ConsultaParaFacturarSerializer
from ..services import FacturaService

class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    factura_service = FacturaService()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FacturaConDetallesSerializer
        return FacturaSerializer

    def get_queryset(self):
        return Factura.objects.select_related('consulta', 'cliente').all()

    @action(detail=False, methods=['get'])
    def consultas_pendientes(self, request):
        """Obtiene consultas completadas sin factura"""
        try:
            consultas = self.factura_service.obtener_consultas_para_facturar()
            serializer = ConsultaParaFacturarSerializer(consultas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'])
    def registrar_pago(self, request, pk=None):
        """Registra el pago de una factura"""
        factura = self.get_object()
        metodo_pago = request.data.get('metodo_pago')
        observaciones = request.data.get('observaciones')

        if not metodo_pago:
            return Response(
                {'error': 'Método de pago es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            factura_actualizada = self.factura_service.registrar_pago(
                factura, metodo_pago, observaciones
            )
            serializer = self.get_serializer(factura_actualizada)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'])
    def anular(self, request, pk=None):
        """Anula una factura"""
        factura = self.get_object()
        motivo = request.data.get('motivo')

        try:
            factura_anulada = self.factura_service.anular_factura(factura, motivo)
            serializer = self.get_serializer(factura_anulada)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def validar_anulacion(self, request, pk=None):
        """Valida si una factura puede ser anulada"""
        factura = self.get_object()
        try:
            resultado = self.factura_service.validar_anulacion(factura)
            return Response(resultado)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de facturación"""
        try:
            estadisticas = self.factura_service.obtener_estadisticas()
            return Response(estadisticas)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def generar_pdf(self, request, pk=None):
        """Genera PDF de la factura"""
        factura = self.get_object()
        try:
            pdf_info = self.factura_service.generar_pdf(factura)
            return Response(pdf_info)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )