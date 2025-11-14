from django.db import models
from usuarios.models import Cliente, Usuario, AuditoriaMixin

class Mascota(AuditoriaMixin):
    id_mascota = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    especie = models.CharField(max_length=50, verbose_name="Especie") 
    raza = models.CharField(max_length=100, verbose_name="Raza")
    edad = models.IntegerField(verbose_name="Edad (años)")
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('H', 'Hembra'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    
    dueño = models.ForeignKey(
        Cliente, 
        on_delete=models.PROTECT, 
        related_name='mascotas',
        verbose_name="Cliente/Dueño"
    )
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='mascotas_creadas')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='mascotas_modificadas')

    def __str__(self):
        return f"{self.nombre} ({self.especie})"

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"


class Cita(AuditoriaMixin):
    id_cita = models.AutoField(primary_key=True)
    
    mascota = models.ForeignKey(
        Mascota, 
        on_delete=models.CASCADE, 
        related_name='citas',
        verbose_name="Mascota"
    )
    
    veterinario = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='citas_asignadas',
        verbose_name="Veterinario Asignado"
    )

    fecha_cita = models.DateField(verbose_name="Fecha de la Cita")
    hora_cita = models.TimeField(verbose_name="Hora de la Cita")
    
    ESTADO_CHOICES = [
        ('Agendada', 'Agendada'),
        ('Completada', 'Completada'),
        ('Cancelada', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Agendada')
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='citas_creadas')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='citas_modificadas')

    def __str__(self):
        return f"Cita {self.id_cita} - {self.mascota.nombre} - {self.fecha_cita}"

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"


class Tratamiento(AuditoriaMixin):
    id_tratamiento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, verbose_name="Nombre del Tratamiento")
    descripcion = models.TextField(blank=True, null=True)
    duracion = models.CharField(max_length=50, blank=True, null=True)
    costo_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Base")
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='tratamientos_creados')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='tratamientos_modificados')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tratamiento"
        verbose_name_plural = "Tratamientos"


class Consulta(AuditoriaMixin):
    id_consulta = models.AutoField(primary_key=True)
    
    mascota = models.ForeignKey(
        Mascota, 
        on_delete=models.PROTECT, 
        related_name='consultas',
        verbose_name="Mascota Consultada"
    )
    
    veterinario = models.ForeignKey(
        Usuario, 
        on_delete=models.PROTECT, 
        related_name='consultas_realizadas',
        verbose_name="Veterinario Responsable"
    )
    
    cita = models.OneToOneField(
        Cita, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Cita Relacionada"
    )

    fecha_consulta = models.DateField(auto_now_add=True)
    motivo = models.CharField(max_length=255)
    diagnostico = models.TextField()
    observaciones = models.TextField(blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Total de Consulta")
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='consultas_creadas')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='consultas_modificadas')
    
    def __str__(self):
        return f"Consulta {self.id_consulta} - {self.mascota.nombre}"

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"


class ConsultaTratamiento(AuditoriaMixin):
    id_consulta_tratamiento = models.AutoField(primary_key=True)
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.PROTECT)
    
    cantidad = models.IntegerField(default=1)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2) 
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='consultatratamientos_creados')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='consultatratamientos_modificados')
    
    class Meta:
        verbose_name = "Detalle de Tratamiento"
        verbose_name_plural = "Detalles de Tratamientos"
        unique_together = ('consulta', 'tratamiento') 


class HistorialMedico(AuditoriaMixin):
    id_historial_medico = models.AutoField(primary_key=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE)
    
    usuario_creacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='historiales_creados')
    usuario_modificacion = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='historiales_modificados')
    
    class Meta:
        verbose_name = "Historial Médico"
        verbose_name_plural = "Historiales Médicos"
        unique_together = ('mascota', 'consulta')