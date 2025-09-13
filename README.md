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