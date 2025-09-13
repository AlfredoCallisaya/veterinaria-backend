from django.contrib.auth.backends import BaseBackend
from .models import UsuarioPersonalizado

class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UsuarioPersonalizado.objects.get(correo=username)
            if user.check_password(password): 
                return user
            else: 
                return None  
        except UsuarioPersonalizado.DoesNotExist:
            return None
        except Exception as e:
            return None
    def get_user(self, user_id):
        try:
            if isinstance(user_id, str):
                user_id = int(user_id)  
            user = UsuarioPersonalizado.objects.get(id=user_id)
            return user
        except (UsuarioPersonalizado.DoesNotExist, ValueError, TypeError) as e:
            return None