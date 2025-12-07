from rest_framework import serializers
from .models import Cliente, Mascota, Cita, Consulta, Tratamiento, ConsultaTratamiento
from usuarios.serializers import UsuarioSerializer, PersonaSerializer 
from usuarios.serializers import UsuarioBasicSerializer
# Nota: Necesitas importar Persona y Usuario de tu app 'usuarios'

# --- 1. CLIENTE y MASCOTA ---

class ClienteSerializer(serializers.ModelSerializer):
    # La información de Persona se muestra dentro del Cliente
    persona_data = PersonaSerializer(source='persona', read_only=True)
    
    class Meta:
        model = Cliente
        fields = ['id', 'persona', 'persona_data', 'Estado']
        read_only_fields = ['id']

class MascotaSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar el nombre del dueño
    nombre_cliente = serializers.CharField(source='cliente.persona.nombre', read_only=True)
    
    class Meta:
        model = Mascota
        # cliente_id es el campo FK, nombre_cliente es el campo de solo lectura
        fields = ['id', 'nombre', 'especie', 'raza', 'sexo', 'edad', 'cliente_id', 'nombre_cliente', 'Estado']
        read_only_fields = ['id']

# --- 2. GESTIÓN DE CITAS ---

class CitaSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para saber qué mascota es sin cargar todo el objeto Mascota
    nombre_mascota = serializers.CharField(source='mascota.nombre', read_only=True)
    nombre_cliente = serializers.CharField(source='mascota.cliente.persona.nombre', read_only=True)
    
    class Meta:
        model = Cita
        fields = ['id', 'mascota', 'nombre_mascota', 'nombre_cliente', 'fechaHoraCita', 'motivo', 'Estado']
        read_only_fields = ['id']

# --- 3. SERVICIOS Y TRATAMIENTOS ---

class TratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tratamiento
        fields = '__all__'
        read_only_fields = ['id']

class ConsultaTratamientoSerializer(serializers.ModelSerializer):
    # Mostrar el nombre del Tratamiento dentro del detalle
    nombre_tratamiento = serializers.CharField(source='tratamiento.nombre', read_only=True)

    class Meta:
        model = ConsultaTratamiento
        # Tratamiento y Consulta son los FK que forman la PK compuesta
        fields = ['tratamiento', 'nombre_tratamiento', 'cantidad', 'costoAplicado']
        # No ponemos 'consulta' aquí si lo anidamos dentro de ConsultaSerializer

# --- 4. CONSULTA (El Corazón de la Facturación) ---

class ConsultaSerializer(serializers.ModelSerializer):
    # Relación anidada: Muestra todos los tratamientos aplicados a esta consulta
    tratamientos_aplicados = ConsultaTratamientoSerializer(
        source='consultatratamiento_set', # Django reverse lookup (consulta.consultatratamiento_set.all())
        many=True,
        read_only=True
    )
    
    # Campo de solo lectura para identificar al veterinario
    nombre_veterinario = serializers.CharField(source='usuario.persona.nombre', read_only=True)
    
    # Campo de solo lectura para la fecha de la cita (útil para el historial)
    fecha_cita = serializers.DateTimeField(source='cita.fechaHoraCita', read_only=True)
    
    class Meta:
        model = Consulta
        # Incluye las claves foráneas (cita, usuario) y los campos de negocio
        fields = [
            'id', 'cita', 'usuario', 'nombre_veterinario', 'fecha_cita',
            'diagnostico', 'observaciones', 'costo',
            'tratamientos_aplicados', 'Estado'
        ]
        read_only_fields = ['id']

    # Método para calcular el total antes de guardar la Factura (lógica de negocio)
    def get_costo_total(self, obj):
        # Suma el costo base de la consulta + el costo de todos los tratamientos
        costo_base = obj.costo
        costo_tratamientos = obj.consultatratamiento_set.aggregate(
            total_tratamientos=models.Sum(F('cantidad') * F('costoAplicado'))
        )['total_tratamientos'] or 0
        
        return costo_base + costo_tratamientos
    


class ConsultaConDetallesSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    mascota_especie = serializers.CharField(source='mascota.especie', read_only=True)
    veterinario_nombre = serializers.SerializerMethodField()
    cliente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Consulta
        fields = [
            'id', 'mascota_id', 'veterinario_id', 'fecha_consulta', 'motivo',
            'diagnostico', 'tratamiento', 'medicamentos', 'observaciones',
            'costo', 'peso', 'temperatura', 'estado', 'mascota_nombre',
            'mascota_especie', 'veterinario_nombre', 'cliente_nombre'
        ]

    def get_veterinario_nombre(self, obj):
        return f"{obj.veterinario.nombre} {obj.veterinario.apellido}"

    def get_cliente_nombre(self, obj):
        return f"{obj.mascota.usuario.nombre} {obj.mascota.usuario.apellido}"

class MascotaConConsultasSerializer(serializers.ModelSerializer):
    consultas_count = serializers.IntegerField(read_only=True)
    consultas_recientes = ConsultaConDetallesSerializer(many=True, read_only=True)
    cliente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Mascota
        fields = [
            'id', 'nombre', 'especie', 'raza', 'edad', 'sexo', 'estado',
            'consultas_count', 'consultas_recientes', 'cliente_nombre'
        ]

    def get_cliente_nombre(self, obj):
        return f"{obj.usuario.nombre} {obj.usuario.apellido}"
    
    

class MascotaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    cliente_telefono = serializers.CharField(source='usuario.telefono', read_only=True)
    cliente_email = serializers.CharField(source='usuario.email', read_only=True)
    edad_display = serializers.CharField(source='edad_con_unidad', read_only=True)
    
    class Meta:
        model = Mascota
        fields = [
            'id', 'nombre', 'especie', 'raza', 'edad', 'edad_display', 
            'sexo', 'usuario', 'cliente_nombre', 'cliente_telefono', 
            'cliente_email', 'estado', 'fecha_registro', 'observaciones'
        ]
        read_only_fields = ['fecha_registro']

class MascotaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'edad', 'sexo', 'usuario', 'observaciones']

class MascotaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'edad', 'sexo', 'usuario', 'estado', 'observaciones']

class MascotaListSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    sexo_display = serializers.CharField(source='get_sexo_display', read_only=True)
    
    class Meta:
        model = Mascota
        fields = [
            'id', 'nombre', 'especie', 'raza', 'edad', 'sexo', 'sexo_display',
            'cliente_nombre', 'estado', 'fecha_registro'
        ]

class MascotaBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = ['id', 'nombre', 'especie', 'raza']