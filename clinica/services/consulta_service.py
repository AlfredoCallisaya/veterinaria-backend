from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Consulta, Mascota, Usuario

class ConsultaService:

    def obtener_consultas_por_mascota(self, mascota_id):
        """Obtiene consultas de una mascota ordenadas por fecha"""
        if not Mascota.objects.filter(id=mascota_id).exists():
            raise ValueError('Mascota no encontrada')
        
        consultas = Consulta.objects.filter(
            mascota_id=mascota_id
        ).select_related('veterinario').order_by('-fecha_consulta')
        
        return consultas

    def obtener_mascotas_con_historial(self):
        """Obtiene mascotas con información de sus consultas"""
        mascotas = Mascota.objects.annotate(
            consultas_count=Count('consulta'),
            consultas_recientes_count=Count('consulta', filter=Q(
                consulta__fecha_consulta__gte=timezone.now() - timedelta(days=30)
            ))
        ).prefetch_related('consulta_set')
        
        mascotas_con_consultas = []
        for mascota in mascotas:
            consultas_recientes = mascota.consulta_set.order_by('-fecha_consulta')[:3]
            mascotas_con_consultas.append({
                'mascota': mascota,
                'consultas_count': mascota.consultas_count,
                'consultas_recientes': consultas_recientes
            })
        
        return mascotas_con_consultas

    def obtener_estadisticas(self):
        """Calcula estadísticas de consultas"""
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)
        
        total_consultas = Consulta.objects.count()
        consultas_completadas = Consulta.objects.filter(estado='Completada').count()
        consultas_pendientes = Consulta.objects.filter(estado='Pendiente').count()
        ingresos_totales = Consulta.objects.aggregate(
            total=Sum('costo')
        )['total'] or 0
        
        consultas_este_mes = Consulta.objects.filter(
            fecha_consulta__gte=inicio_mes
        ).count()
        
        return {
            'total_consultas': total_consultas,
            'consultas_completadas': consultas_completadas,
            'consultas_pendientes': consultas_pendientes,
            'ingresos_totales': float(ingresos_totales),
            'consultas_este_mes': consultas_este_mes,
            'tasa_completamiento': (
                (consultas_completadas / total_consultas * 100) 
                if total_consultas > 0 else 0
            )
        }

    def validar_consulta(self, consulta_data):
        """Valida los datos de una consulta antes de guardar"""
        errores = []
        
        # Validar fecha no futura para consultas completadas
        if consulta_data.get('estado') == 'Completada':
            fecha_consulta = consulta_data.get('fecha_consulta')
            if fecha_consulta and fecha_consulta > timezone.now().date():
                errores.append('No se puede completar una consulta con fecha futura')
        
        # Validar costo positivo
        if consulta_data.get('costo', 0) < 0:
            errores.append('El costo debe ser un valor positivo')
        
        # Validar peso y temperatura en rangos razonables
        peso = consulta_data.get('peso')
        if peso and (peso < 0.1 or peso > 200):
            errores.append('El peso debe estar entre 0.1 y 200 kg')
        
        temperatura = consulta_data.get('temperatura')
        if temperatura and (temperatura < 30 or temperatura > 45):
            errores.append('La temperatura debe estar entre 30°C y 45°C')
        
        return errores

    def generar_receta_medica(self, consulta):
        """Genera una receta médica basada en la consulta"""
        if consulta.estado != 'Completada':
            raise ValueError('Solo se pueden generar recetas para consultas completadas')
        
        if not consulta.tratamiento and not consulta.medicamentos:
            raise ValueError('La consulta no tiene tratamiento ni medicamentos prescritos')
        
        receta = {
            'consulta_id': consulta.id,
            'fecha_emision': timezone.now().date(),
            'mascota': consulta.mascota.nombre,
            'especie': consulta.mascota.especie,
            'propietario': f"{consulta.mascota.usuario.nombre} {consulta.mascota.usuario.apellido}",
            'veterinario': f"{consulta.veterinario.nombre} {consulta.veterinario.apellido}",
            'diagnostico': consulta.diagnostico,
            'tratamiento': consulta.tratamiento,
            'medicamentos': consulta.medicamentos,
            'observaciones': consulta.observaciones,
            'instrucciones': 'Seguir al pie de la letra las indicaciones del veterinario'
        }
        
        return receta