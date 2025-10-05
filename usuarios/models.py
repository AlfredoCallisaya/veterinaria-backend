from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Rol(models.Model):
    id = models.AutoField(primary_key=True, db_column='idRol')
    nombreRol = models.CharField(max_length=50, db_column='nombreRol')
    descripcion = models.TextField(blank=True, null=True, db_column='descripcion')
    estado = models.BooleanField(default=True, db_column='estado')
    
    class Meta:
        db_table = 'Rol'
        managed = True
    
    def __str__(self):
        return self.nombreRol

class UsuarioPersonalizado(models.Model):
    id = models.AutoField(primary_key=True, db_column='idUsuario')
    nombres = models.CharField(max_length=100, db_column='nombres')
    apellidos = models.CharField(max_length=100, db_column='apellidos')
    correo = models.EmailField(unique=True, db_column='correo')
    contrasena = models.CharField(max_length=255, db_column='contraseña')
    idRol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, db_column='idRol')
    
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombres', 'apellidos']
    
    class Meta:
        db_table = 'Usuario'
        managed = True
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    def set_password(self, raw_password):
        self.contrasena = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.contrasena)
    
    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}"
    
    def get_short_name(self):
        return self.nombres

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_staff(self):
        if self.idRol:
            return self.idRol.nombreRol in ['Superusuario', 'Administrador']
        return False
    
    @property
    def is_superuser(self):
        if self.idRol:
            return self.idRol.nombreRol == 'Superusuario'
        return False
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser