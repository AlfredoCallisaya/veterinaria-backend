# Sistema de Gestión Veterinaria

Este proyecto es una aplicación web desarrollada en Django para la gestión de una clínica veterinaria.  
Permite administrar clientes, mascotas, citas, consultas, inventario, compras, facturación y pagos.

------------------------------------------------------------------------------------------------------

## Descripción
Backend del sistema de gestión veterinaria desarrollado con Django y MySQL.

## Tecnologías
- Django 5.2.6
- MySQL 8.0
- Python 3.13
- Django REST Framework (opcional)

## Base de Datos
- MySQL 8.0+
- Diagrama ER: `Diagrama_ER.png`
- Diagrama Relacional: `Diagrama_Relacional.png`

## Migraciones de Base de Datos

### Para desarrolladores:
1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno: `venv\Scripts\activate`
4. Instalar dependencias: `pip install -r requirements.txt`
5. **Generar migraciones**: `python manage.py makemigrations`
6. **Aplicar migraciones**: `python manage.py migrate`
7. Ejecutar servidor: `python manage.py runserver`

### Nota importante:
- Las migraciones NO están incluidas en el repositorio
- Cada desarrollador debe generarlas localmente
- Esto previene conflictos en las migraciones

# Crear carpeta migrations vacía
mkdir usuarios/migrations
New-Item -Path usuarios/migrations -Name "__init__.py" -ItemType File

# Generar migraciones frescas
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate