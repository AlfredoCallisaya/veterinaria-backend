from ..models import Usuario, Mascota

class ClienteService:
    
    def validar_eliminacion(self, cliente: Usuario):
        """Valida si un cliente puede ser eliminado"""
        mascotas_count = Mascota.objects.filter(usuario_id=cliente.id).count()
        
        if mascotas_count > 0:
            return {
                'puede_eliminar': False,
                'razon': f'El cliente tiene {mascotas_count} mascota(s) registrada(s)'
            }
        
        # Aquí puedes agregar más validaciones (ej: citas pendientes, facturas, etc.)
        
        return {'puede_eliminar': True}

    def validar_desactivacion(self, cliente: Usuario):
        """Valida si un cliente puede ser desactivado"""
        if cliente.estado == 'Inactivo':
            return {'puede_desactivar': True}
        
        mascotas_count = Mascota.objects.filter(
            usuario_id=cliente.id, 
            estado='Activo'
        ).count()
        
        if mascotas_count > 0:
            return {
                'puede_desactivar': False,
                'razon': f'El cliente tiene {mascotas_count} mascota(s) activa(s)'
            }
        
        # Validar si tiene citas pendientes
        from clinica.models import Cita
        citas_pendientes = Cita.objects.filter(
            mascota__usuario_id=cliente.id,
            estado='Agendada'
        ).count()
        
        if citas_pendientes > 0:
            return {
                'puede_desactivar': False,
                'razon': f'El cliente tiene {citas_pendientes} cita(s) pendiente(s)'
            }
        
        return {'puede_desactivar': True}

    def cambiar_estado(self, cliente: Usuario, nuevo_estado: str):
        """Cambia el estado de un cliente con validaciones"""
        if nuevo_estado not in ['Activo', 'Inactivo']:
            raise ValueError('Estado no válido')
        
        if nuevo_estado == 'Inactivo':
            validacion = self.validar_desactivacion(cliente)
            if not validacion['puede_desactivar']:
                raise ValueError(validacion['razon'])
        
        cliente.estado = nuevo_estado
        cliente.save()
        
        return cliente

    def obtener_info_mascotas(self, cliente: Usuario):
        """Obtiene información de mascotas del cliente"""
        mascotas = Mascota.objects.filter(usuario_id=cliente.id)
        
        return {
            'mascotas_count': mascotas.count(),
            'mascotas_names': [m.nombre for m in mascotas],
            'mascotas_activas': mascotas.filter(estado='Activo').count()
        }