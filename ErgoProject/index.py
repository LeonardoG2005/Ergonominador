"""
Handler de Vercel para Django
Este archivo es el punto de entrada para Vercel Serverless Functions
"""
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ErgoProject.settings')

# Importar WSGI application
from ErgoProject.wsgi import application

# Handler para Vercel
def handler(request, context):
    return application(request, context)

# Exportar como app para compatibilidad
app = application
