from django.db import models
from django.contrib.auth.models import AbstractUser

class AuditoriaMixin(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última Modificación")
    estado = models.BooleanField(default=True, verbose_name="Estado Activo")

    class Meta:
        abstract = True

class Rol(AuditoriaMixin):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Rol")
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']

class Usuario(AbstractUser, AuditoriaMixin):
    id_usuario = models.AutoField(primary_key=True) 
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')

    roles = models.ManyToManyField(
        Rol,
        through='UsuarioRol',
        related_name='usuarios',
        verbose_name="Roles del Usuario"
    )

    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    apellido = models.CharField(max_length=150, verbose_name="Apellido")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email 
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

class UsuarioRol(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'rol')
        verbose_name = "Rol de Usuario"
        verbose_name_plural = "Roles de Usuarios"

class Persona(AuditoriaMixin):
    id_persona = models.AutoField(primary_key=True)
    
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='persona_info',
        verbose_name="Cuenta de Usuario"
    )
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='personas_creadas')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='personas_modificadas')

    def __str__(self):
        return self.usuario.get_full_name() if self.usuario else f"Persona #{self.id_persona}"

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"

class Cliente(AuditoriaMixin):
    id_cliente = models.AutoField(primary_key=True)
    
    persona = models.OneToOneField(
        Persona, 
        on_delete=models.CASCADE, 
        related_name='cliente_info',
        verbose_name="Datos Personales del Cliente"
    )
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='clientes_creados')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='clientes_modificados')

    def __str__(self):
        return f"Cliente: {str(self.persona)}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"