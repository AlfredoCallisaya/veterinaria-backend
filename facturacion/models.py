from django.db import models
from usuarios.models import Cliente, Usuario, AuditoriaMixin
from clinica.models import Consulta 

class Pago(AuditoriaMixin):
    id_pago = models.AutoField(primary_key=True)
    
    METODO_CHOICES = [
        ('Efectivo', 'Efectivo'),
        ('Tarjeta Débito', 'Tarjeta Débito'),
        ('Tarjeta Crédito', 'Tarjeta Crédito'),
        ('Transferencia', 'Transferencia'),
    ]
    metodo_pago = models.CharField(max_length=50, choices=METODO_CHOICES, verbose_name="Método de Pago")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField()
    
    ESTADO_CHOICES = [
        ('Completado', 'Completado'),
        ('Rechazado', 'Rechazado'),
    ]
    estado_pago = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Completado', verbose_name="Estado del Pago")
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='pagos_creados')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='pagos_modificados')
    
    def __str__(self):
        return f"Pago {self.id_pago} - {self.monto}"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"


class Factura(AuditoriaMixin):
    id_factura = models.AutoField(primary_key=True)
    numero_factura = models.CharField(max_length=100, unique=True, verbose_name="Número de Factura")
    
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.PROTECT, 
        related_name='facturas',
        verbose_name="Cliente"
    )
    
    consulta = models.OneToOneField(
        Consulta, 
        on_delete=models.PROTECT, 
        related_name='factura_generada',
        verbose_name="Consulta Asociada"
    )
    
    pago = models.ForeignKey(
        Pago,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='facturas_pagadas',
        verbose_name="Transacción de Pago"
    )

    fecha_emision = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Pagada', 'Pagada'),
        ('Anulada', 'Anulada'),
    ]
    estado_pago = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente', verbose_name="Estado de Pago")
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='facturas_creadas')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='facturas_modificadas')
    
    def __str__(self):
        return self.numero_factura

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha_emision']


class DetalleFactura(AuditoriaMixin):
    id_detalle_factura = models.AutoField(primary_key=True)
    
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)

    descripcion = models.CharField(max_length=255, verbose_name="Descripción del Ítem")
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='detallesfactura_creados')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='detallesfactura_modificados')
    
    class Meta:
        verbose_name = "Detalle de Factura"
        verbose_name_plural = "Detalles de Facturas"
        unique_together = ('factura', 'descripcion')