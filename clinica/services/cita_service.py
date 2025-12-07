from datetime import datetime, time, date
from django.utils import timezone
from ..models import Cita

class CitaService:
    HORARIOS_LABORALES = {
        'semana': ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00'],
        'fin_semana': ['09:00', '10:00', '11:00']
    }

    def obtener_horarios_disponibles(self, fecha: date):
        """Obtiene horarios disponibles para una fecha específica"""
        dia_semana = fecha.weekday()
        es_fin_semana = dia_semana in [5, 6]  # 5=sábado, 6=domingo
        
        base_horarios = self.HORARIOS_LABORALES['fin_semana'] if es_fin_semana else self.HORARIOS_LABORALES['semana']
        
        # Obtener citas existentes para esa fecha
        citas_existentes = Cita.objects.filter(
            fechaCita=fecha,
            estado__in=['Agendada', 'Confirmada']
        ).values_list('horaCita', flat=True)
        
        horarios_ocupados = set(citas_existentes)
        
        horarios_disponibles = []
        for horario in base_horarios:
            disponible = horario not in horarios_ocupados
            horarios_disponibles.append({
                'fecha': fecha.isoformat(),
                'hora': horario,
                'disponible': disponible
            })
        
        return horarios_disponibles

    def validar_horario_disponible(self, fecha_str: str, hora_str: str) -> bool:
        """Valida si un horario específico está disponible"""
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora = hora_str
            
            # Validar que la fecha no sea en el pasado
            if fecha < timezone.now().date():
                return False
            
            # Validar formato de hora
            datetime.strptime(hora, '%H:%M')
            
            # Obtener horarios disponibles
            horarios = self.obtener_horarios_disponibles(fecha)
            
            # Buscar el horario específico
            for horario in horarios:
                if horario['hora'] == hora:
                    return horario['disponible']
            
            return False
            
        except ValueError:
            raise ValueError('Formato de fecha u hora inválido')

    def cambiar_estado(self, cita: Cita, nuevo_estado: str):
        """Cambia el estado de una cita con validaciones"""
        estados_permitidos = ['Agendada', 'Confirmada', 'Completada', 'Cancelada']
        
        if nuevo_estado not in estados_permitidos:
            raise ValueError(f'Estado {nuevo_estado} no permitido')
        
        # Validaciones específicas por estado
        if nuevo_estado == 'Completada' and cita.fechaCita > timezone.now().date():
            raise ValueError('No se puede completar una cita futura')
        
        if nuevo_estado == 'Cancelada' and cita.fechaCita < timezone.now().date():
            raise ValueError('No se puede cancelar una cita pasada')
        
        cita.estado = nuevo_estado
        cita.save()
        
        return cita