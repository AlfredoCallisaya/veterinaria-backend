# pyright: reportMissingImports=false
from rest_framework import serializers
from .models import CategoriaProducto, TipoMovimiento, Proveedor, Producto, Compra, DetalleCompra, MovimientoInventario

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = '__all__'

class TipoMovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMovimiento
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    nombre_proveedor = serializers.CharField(source='idproveedor.nombreproveedor', read_only=True)
    nombre_categoria = serializers.CharField(source='idcategoria.nombrecategoria', read_only=True)
    
    class Meta:
        model = Producto
        fields = '__all__'
                
class CompraSerializer(serializers.ModelSerializer):
    nombre_proveedor = serializers.CharField(source='idproveedor.nombreproveedor', read_only=True)
    
    class Meta:
        model = Compra
        fields = '__all__'

class DetalleCompraSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(source='idproducto.nombreproducto', read_only=True)
    
    class Meta:
        model = DetalleCompra
        fields = '__all__'

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(source='idproducto.nombreproducto', read_only=True)
    tipo_movimiento = serializers.CharField(source='idtipomovimiento.nombretipo', read_only=True)
    
    class Meta:
        model = MovimientoInventario
        fields = '__all__'