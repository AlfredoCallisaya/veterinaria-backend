from rest_framework import serializers
from .models import Factura
from clinica.models import Consulta

class FacturaConDetallesSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.SerializerMethodField()
    mascota_nombre = serializers.SerializerMethodField()
    consulta_motivo = serializers.SerializerMethodField()
    veterinario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Factura
        fields = [
            'id', 'numero_factura', 'cliente_id', 'consulta_id', 
            'fecha_emision', 'fecha_vencimiento', 'fecha_pago',
            'subtotal', 'iva', 'total', 'estado', 'metodo_pago',
            'observaciones', 'cliente_nombre', 'mascota_nombre',
            'consulta_motivo', 'veterinario_nombre'
        ]

    def get_cliente_nombre(self, obj):
        return f"{obj.cliente.nombre} {obj.cliente.apellido}"

    def get_mascota_nombre(self, obj):
        return obj.consulta.mascota.nombre if obj.consulta else 'N/A'

    def get_consulta_motivo(self, obj):
        return obj.consulta.motivo if obj.consulta else 'N/A'

    def get_veterinario_nombre(self, obj):
        if obj.consulta and obj.consulta.veterinario:
            return f"{obj.consulta.veterinario.nombre} {obj.consulta.veterinario.apellido}"
        return 'N/A'

class ConsultaParaFacturarSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    iva = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Consulta
        fields = [
            'id', 'fecha_consulta', 'motivo', 'diagnostico', 'costo',
            'mascota_nombre', 'cliente_nombre', 'subtotal', 'iva', 'total'
        ]

    def get_cliente_nombre(self, obj):
        return f"{obj.mascota.usuario.nombre} {obj.mascota.usuario.apellido}"