import os
import sys

# Añadir el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(__file__))

# Configurar las settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ErgoProject.settings')

# Importar la aplicación WSGI de Django
from ErgoProject.wsgi import application

# Vercel busca una variable llamada 'app' o 'handler'
# En este caso, 'application' es la app WSGI de Django
app = application
