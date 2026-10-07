import os
import sys

# Añadir el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(__file__))

# Configurar las settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ErgoProject.settings')

# Importar la aplicación WSGI de Django
from ErgoProject.wsgi import application

# En Vercel la SQLite vive en /tmp y arranca vacía en cada cold start,
# así que se aplican las migraciones aquí (antes lo intentaba vercel_build.py,
# pero ese script corría en la máquina de build, no en la función).
if os.environ.get('VERCEL'):
    from django.core.management import call_command
    call_command('migrate', '--noinput')

# Vercel busca una variable llamada 'app' o 'handler'
# En este caso, 'application' es la app WSGI de Django
app = application
