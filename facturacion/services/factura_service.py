from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import random
from ..models import Factura, Consulta

class FacturaService:
    IVA_PORCENTAJE = 0.13

    def generar_numero_factura(self):
        """Genera un número de factura único"""
        timestamp = int(timezone.now().timestamp())
        random_num = random.randint(1000, 9999)
        return f"FACT-{timestamp}-{random_num}"

    def calcular_totales(self, costo_base):
        """Calcula subtotal, IVA y total"""
        subtotal = costo_base
        iva = round(subtotal * self.IVA_PORCENTAJE, 2)
        total = round(subtotal + iva, 2)
        return subtotal, iva, total

    def obtener_consultas_para_facturar(self):
        """Obtiene consultas completadas sin factura"""
        consultas = Consulta.objects.filter(
            estado='Completada',
            factura__isnull=True
        ).select_related('mascota', 'mascota__usuario', 'veterinario')
        
        consultas_con_totales = []
        for consulta in consultas:
            subtotal, iva, total = self.calcular_totales(consulta.costo)
            consultas_con_totales.append({
                'consulta': consulta,
                'subtotal': subtotal,
                'iva': iva,
                'total': total
            })
        
        return consultas_con_totales

    def crear_factura_desde_consulta(self, consulta_id):
        """Crea una factura a partir de una consulta"""
        try:
            consulta = Consulta.objects.select_related('mascota', 'veterinario').get(
                id=consulta_id, 
                estado='Completada'
            )
            
            # Verificar que no tenga factura
            if hasattr(consulta, 'factura'):
                raise ValueError('Esta consulta ya tiene una factura asociada')
            
            subtotal, iva, total = self.calcular_totales(consulta.costo)
            
            fecha_emision = timezone.now().date()
            fecha_vencimiento = fecha_emision + timedelta(days=30)
            
            factura = Factura.objects.create(
                cliente=consulta.mascota.usuario,
                consulta=consulta,
                numero_factura=self.generar_numero_factura(),
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                subtotal=subtotal,
                iva=iva,
                total=total,
                estado='Pendiente',
                observaciones=f'Factura por consulta médica - {consulta.motivo}'
            )
            
            return factura
            
        except Consulta.DoesNotExist:
            raise ValueError('Consulta no encontrada o no está completada')

    def registrar_pago(self, factura, metodo_pago, observaciones=None):
        """Registra el pago de una factura"""
        if factura.estado != 'Pendiente':
            raise ValueError('Solo se pueden registrar pagos en facturas pendientes')
        
        if factura.fecha_vencimiento < timezone.now().date():
            raise ValueError('No se puede pagar una factura vencida')
        
        factura.estado = 'Pagada'
        factura.metodo_pago = metodo_pago
        factura.fecha_pago = timezone.now().date()
        
        if observaciones:
            factura.observaciones = f"{factura.observaciones}\nPago registrado: {observaciones}"
        
        factura.save()
        return factura

    def anular_factura(self, factura, motivo=None):
        """Anula una factura"""
        if factura.estado == 'Pagada':
            raise ValueError('No se puede anular una factura ya pagada')
        
        if factura.estado == 'Anulada':
            raise ValueError('La factura ya está anulada')
        
        factura.estado = 'Anulada'
        if motivo:
            factura.observaciones = f"Factura anulada - {motivo}\n{factura.observaciones}"
        else:
            factura.observaciones = f"Factura anulada\n{factura.observaciones}"
        
        factura.save()
        return factura

    def validar_anulacion(self, factura):
        """Valida si una factura puede ser anulada"""
        if factura.estado == 'Pagada':
            return {
                'puede_anular': False,
                'razon': 'No se puede anular una factura ya pagada'
            }
        
        if factura.estado == 'Anulada':
            return {
                'puede_anular': False,
                'razon': 'La factura ya está anulada'
            }
        
        # Verificar si la fecha de vencimiento ya pasó
        if factura.fecha_vencimiento < timezone.now().date():
            return {
                'puede_anular': True,
                'advertencia': 'La factura está vencida'
            }
        
        return {'puede_anular': True}

    def obtener_estadisticas(self):
        """Calcula estadísticas de facturación"""
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)
        
        # Totales por estado
        total_facturado = Factura.objects.aggregate(
            total=Sum('total')
        )['total'] or 0
        
        total_pagado = Factura.objects.filter(estado='Pagada').aggregate(
            total=Sum('total')
        )['total'] or 0
        
        total_pendiente = Factura.objects.filter(estado='Pendiente').aggregate(
            total=Sum('total')
        )['total'] or 0
        
        facturas_vencidas = Factura.objects.filter(
            estado='Pendiente',
            fecha_vencimiento__lt=hoy
        ).count()
        
        # Facturas por mes (últimos 6 meses)
        facturas_por_mes = []
        for i in range(6):
            mes = hoy.replace(day=1) - timedelta(days=30*i)
            total_mes = Factura.objects.filter(
                fecha_emision__year=mes.year,
                fecha_emision__month=mes.month
            ).aggregate(total=Sum('total'))['total'] or 0
            
            facturas_por_mes.append({
                'mes': mes.strftime('%Y-%m'),
                'total': float(total_mes)
            })
        
        return {
            'total_facturado': float(total_facturado),
            'total_pagado': float(total_pagado),
            'total_pendiente': float(total_pendiente),
            'facturas_vencidas': facturas_vencidas,
            'facturas_por_mes': facturas_por_mes
        }