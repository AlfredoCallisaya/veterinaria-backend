from django.db import transaction
from django.db.models import Q
from .models import Mascota
from usuarios.models import Usuario

class MascotaService:
    
    @staticmethod
    def obtener_mascotas_activas():
        """Obtiene todas las mascotas activas"""
        return Mascota.objects.filter(estado='Activo').select_related('usuario')
    
    @staticmethod
    def buscar_mascotas(termino_busqueda):
        """Busca mascotas por nombre, especie, raza o dueño"""
        return Mascota.objects.filter(
            Q(nombre__icontains=termino_busqueda) |
            Q(especie__icontains=termino_busqueda) |
            Q(raza__icontains=termino_busqueda) |
            Q(usuario__nombre__icontains=termino_busqueda) |
            Q(usuario__apellido__icontains=termino_busqueda)
        ).select_related('usuario')
    
    @staticmethod
    def obtener_mascotas_por_cliente(cliente_id):
        """Obtiene mascotas de un cliente específico"""
        return Mascota.objects.filter(
            usuario_id=cliente_id, 
            estado='Activo'
        ).select_related('usuario')
    
    @staticmethod
    def crear_mascota(datos_mascota):
        """Crea una nueva mascota"""
        try:
            with transaction.atomic():
                # Verificar que el usuario existe y es cliente
                usuario = Usuario.objects.get(
                    id=datos_mascota['usuario'],
                    rol__nombre='Cliente',
                    estado='Activo'
                )
                
                mascota = Mascota.objects.create(**datos_mascota)
                return mascota
                
        except Usuario.DoesNotExist:
            raise ValueError('El cliente especificado no existe o no está activo')
        except Exception as e:
            raise ValueError(f'Error al crear mascota: {str(e)}')
    
    @staticmethod
    def actualizar_mascota(mascota_id, datos_actualizados):
        """Actualiza una mascota existente"""
        try:
            with transaction.atomic():
                mascota = Mascota.objects.get(id=mascota_id)
                
                # Verificar usuario si se está actualizando
                if 'usuario' in datos_actualizados:
                    usuario = Usuario.objects.get(
                        id=datos_actualizados['usuario'],
                        rol__nombre='Cliente',
                        estado='Activo'
                    )
                
                for attr, value in datos_actualizados.items():
                    setattr(mascota, attr, value)
                
                mascota.save()
                return mascota
                
        except Mascota.DoesNotExist:
            raise ValueError('Mascota no encontrada')
        except Usuario.DoesNotExist:
            raise ValueError('El cliente especificado no existe o no está activo')
        except Exception as e:
            raise ValueError(f'Error al actualizar mascota: {str(e)}')
    
    @staticmethod
    def cambiar_estado_mascota(mascota_id, nuevo_estado):
        """Cambia el estado de una mascota"""
        try:
            with transaction.atomic():
                mascota = Mascota.objects.get(id=mascota_id)
                
                if nuevo_estado not in ['Activo', 'Inactivo']:
                    raise ValueError('Estado no válido')
                
                mascota.estado = nuevo_estado
                mascota.save()
                return mascota
                
        except Mascota.DoesNotExist:
            raise ValueError('Mascota no encontrada')
    
    @staticmethod
    def eliminar_mascota(mascota_id):
        """Elimina una mascota (eliminación suave cambiando estado)"""
        try:
            with transaction.atomic():
                mascota = Mascota.objects.get(id=mascota_id)
                
                # Verificar si la mascota tiene consultas activas
                from clinica.models import Consulta
                consultas_activas = Consulta.objects.filter(
                    mascota=mascota,
                    estado__in=['Programada', 'En Progreso']
                ).exists()
                
                if consultas_activas:
                    raise ValueError('No se puede eliminar una mascota con consultas activas')
                
                # Cambiar estado a inactivo en lugar de eliminar
                mascota.estado = 'Inactivo'
                mascota.save()
                return mascota
                
        except Mascota.DoesNotExist:
            raise ValueError('Mascota no encontrada')
    
    @staticmethod
    def obtener_estadisticas():
        """Obtiene estadísticas de mascotas"""
        total_mascotas = Mascota.objects.count()
        mascotas_activas = Mascota.objects.filter(estado='Activo').count()
        mascotas_inactivas = Mascota.objects.filter(estado='Inactivo').count()
        
        # Estadísticas por especie
        especies_stats = Mascota.objects.filter(estado='Activo').values(
            'especie'
        ).annotate(
            total=models.Count('id')
        ).order_by('-total')
        
        return {
            'total_mascotas': total_mascotas,
            'mascotas_activas': mascotas_activas,
            'mascotas_inactivas': mascotas_inactivas,
            'especies_stats': list(especies_stats)
        }