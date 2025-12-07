from rest_framework import serializers
from .models import Usuario, Rol, Persona, Cliente, UsuarioRol
from django.contrib.auth import get_user_model
from clinica.models import Mascota
User = get_user_model()


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id_rol', 'nombre', 'descripcion']


class UsuarioSerializer(serializers.ModelSerializer):
    roles = RolSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id_usuario', 'email', 'nombre', 'apellido',
            'roles', 'password', 'estado'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UsuarioRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioRol
        fields = ['usuario', 'rol']


class PersonaSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Persona
        fields = [
            'id_persona', 'telefono', 'direccion',
            'usuario', 'fecha_creacion', 'fecha_modificacion', 'estado'
        ]


class ClienteSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer()

    class Meta:
        model = Cliente
        fields = [
            'id_cliente', 'persona',
            'fecha_creacion', 'fecha_modificacion', 'estado'
        ]



class ClienteConMascotasSerializer(serializers.ModelSerializer):
    mascotas_count = serializers.SerializerMethodField()
    mascotas_names = serializers.SerializerMethodField()
    tipo_cliente = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre', 'apellido', 'correo', 'telefono', 'direccion',
            'estado', 'fechaRegistro', 'mascotas_count', 'mascotas_names', 'tipo_cliente'
        ]

    def get_mascotas_count(self, obj):
        return Mascota.objects.filter(usuario_id=obj.id).count()

    def get_mascotas_names(self, obj):
        mascotas = Mascota.objects.filter(usuario_id=obj.id)
        return [m.nombre for m in mascotas]

    def get_tipo_cliente(self, obj):
        return 'Usuario Web' if obj.correo else 'Cliente Directo'