#!/usr/bin/env python
"""
Script de build para Vercel
Ejecuta migraciones y collectstatic automáticamente en cada deploy
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ErgoProject.settings')
django.setup()

from django.core.management import call_command

# Ejecutar migraciones
call_command('migrate', '--noinput')
print("✅ Migraciones completadas")

# Recopilar archivos estáticos
call_command('collectstatic', '--noinput', '--clear')
print("✅ Archivos estáticos recopilados")
