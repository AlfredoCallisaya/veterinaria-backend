# Sistema de Gestión Veterinaria

Este proyecto es una aplicación web desarrollada en Django para la gestión de una clínica veterinaria.  
Permite administrar clientes, mascotas, citas, consultas, inventario, compras, facturación y pagos.

## 🐳 Ejecutar con Docker 

### Prerrequisitos
- Docker
- Docker Compose

### Instalación rápida
```bash
# Clonar el repositorio
- git clone https://github.com/AlfredoCallisaya/veterinaria-backend.git
- cd veterinaria-backend
- git clone https://github.com/AlfredoCallisaya/veterinaria-frontend.git
# Ejecutar con Docker Compose
- docker-compose up -d
# Hacer las migraciones de manera manual, por que no funciona de otra manera :'v
- docker-compose exec web python manage.py makemigrations
- docker-compose exec web python manage.py migrate 
# Si dice que la tabla usuario o rol ya existen usar este comando
- docker-compose exec web python manage.py migrate --fake
### Acceder a la aplicación
- Aplicación: http://localhost:8001
- Base de datos MySQL: localhost:3306

### Usuario por defecto
- Correo: admin@veterinaria.com
- Contraseña: admin123

### Comandos útiles
# Ver logs en tiempo real
- docker-compose exec db mysql -u root -proot_password -e "USE veterinaria; SHOW TABLES;"
- docker-compose logs -f web

# Ejecutar comandos Django
- docker-compose exec web python manage.py showmigrations
- docker-compose exec web python manage.py makemigrations
- docker-compose exec web python manage.py migrate
- docker-compose exec web python manage.py createsuperuser
- docker-compose exec web python manage.py migrate --fake

# Detener la aplicación
- docker-compose down

# Reiniciar
- docker-compose restart

### Instalación sin docker
# Crear entorno virtual
- python -m venv venv
- venv\Scripts\activate  

# Instalar dependencias
- pip install -r requirements.txt

# Configurar base de datos MySQL

# (Crear base de datos 'veterinaria')

# Migraciones
- python manage.py migrate
- python manage.py runserver