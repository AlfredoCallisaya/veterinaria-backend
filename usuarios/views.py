from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .backends import EmailBackend
from .models import UsuarioPersonalizado, Rol
from django.http import JsonResponse

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        correo = request.POST.get('username')
        password = request.POST.get('password')
        
        backend = EmailBackend()
        user = backend.authenticate(request, username=correo, password=password)
        
        if user is not None:
            
            login(request, user, backend='usuarios.backends.EmailBackend')
            return redirect('dashboard')
        else:
            messages.error(request, 'Correo o contraseña incorrectos')
    
    return render(request, 'usuarios/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('login')

@login_required
def dashboard(request):
    user_id = request.session.get('_auth_user_id')
    if not user_id:
        return redirect('login')
    
    try:
        user = UsuarioPersonalizado.objects.get(id=user_id)
    except UsuarioPersonalizado.DoesNotExist:
        return redirect('login')
    
    usuarios = UsuarioPersonalizado.objects.all()
    return render(request, 'usuarios/dashboard.html', {'usuarios': usuarios})

@login_required
def lista_usuarios(request):
    if not (request.user.is_superuser or request.user.idRol.nombreRol == 'Administrador'):
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('dashboard')
    
    usuarios = UsuarioPersonalizado.objects.all()
    roles = Rol.objects.all() 
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios, 'roles': roles})


@login_required
def registrar_usuario(request):
    if not (request.user.is_superuser or request.user.idRol.nombreRol == 'Administrador'):
        messages.error(request, 'No tienes permisos para esta acción')
        return redirect('dashboard')
    
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        nombres = request.POST.get('nombres', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        correo = request.POST.get('correo', '').strip().lower()
        password = request.POST.get('password', '')
        id_rol = request.POST.get('idRol')
        
        # Validaciones
        if not all([nombres, apellidos, correo, id_rol]):
            messages.error(request, 'Todos los campos son obligatorios')
            return redirect('lista_usuarios')
        
        try:
            rol = Rol.objects.get(id=id_rol)

            if usuario_id:  
                usuario = get_object_or_404(UsuarioPersonalizado, id=usuario_id)
                usuario.nombres = nombres
                usuario.apellidos = apellidos
                usuario.correo = correo
                usuario.idRol = rol
                if password:
                    usuario.set_password(password)
                usuario.save()
                messages.success(request, f'Usuario {nombres} {apellidos} actualizado correctamente')

            else:  
                if not password:
                    messages.error(request, 'Debe ingresar una contraseña para crear un usuario nuevo')
                    return redirect('lista_usuarios')

                if UsuarioPersonalizado.objects.filter(correo=correo).exists():
                    messages.error(request, 'El correo ya está registrado')
                    return redirect('lista_usuarios')

                usuario = UsuarioPersonalizado(
                    nombres=nombres,
                    apellidos=apellidos,
                    correo=correo,
                    idRol=rol
                )
                usuario.set_password(password)
                usuario.save()
                messages.success(request, f'Usuario {nombres} {apellidos} registrado exitosamente')

        except Rol.DoesNotExist:
            messages.error(request, 'Rol no válido')
        except Exception as e:
            messages.error(request, f'Error: {e}')

        return redirect('lista_usuarios')

    usuarios = UsuarioPersonalizado.objects.all()
    roles = Rol.objects.all()
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios, 'roles': roles})

@login_required
def eliminar_usuario(request, user_id):
    if not request.user.idRol.nombreRol == 'Administrador':
        messages.error(request, 'Solo el Administrador puede eliminar usuarios')
        return redirect('lista_usuarios')
    
    usuario = get_object_or_404(UsuarioPersonalizado, id=user_id)
    
    if usuario == request.user:
        messages.error(request, 'No puedes eliminarte a ti mismo')
        return redirect('lista_usuarios')
    
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado exitosamente')
        return redirect('lista_usuarios')
    
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})
