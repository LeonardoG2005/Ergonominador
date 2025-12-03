from django.shortcuts import render
import os
import re


def documentation(request):
    """
    View para página de documentación técnica.
    Lee README.md y extrae información del código para generar documentación completa.
    """
    # Leer README.md
    readme_path = os.path.join(os.path.dirname(__file__), '../../README.md')
    readme_html = ""
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
            # Conversión simple de markdown a HTML (sin librería externa)
            readme_html = simple_markdown_to_html(readme_content)
    except FileNotFoundError:
        readme_html = "<p>README.md no encontrado</p>"
    
    # Información extraída del código
    endpoints = [
        {
            'url': '/get-alerts/',
            'method': 'GET',
            'description': 'Devuelve última alerta no vista por tipo + estado actual del semáforo de postura',
            'response_example': '''{
  "Distancia": {
    "type_alert": "Distancia",
    "message": "¡Distancia a la pantalla es muy baja!",
    "created_at": "14:30:15",
    "seen": false
  },
  "Temperatura": {...},
  "Luz": {...},
  "Postura": {
    "tiempo": 120,
    "semaforo": "Verde",
    "created_at": "14:30:15"
  }
}'''
        },
        {
            'url': '/get-sensor-data/',
            'method': 'GET',
            'description': 'Datos históricos de sensores (últimos 20 puntos) + tiempos acumulados del semáforo',
            'response_example': '''{
  "temp_timestamps": ["2025-12-02 14:30:15", ...],
  "temp_values": [28.5, 29.1, ...],
  "sonido_timestamps": [...],
  "sonido_values": [45.2, 46.8, ...],
  "luz_timestamps": [...],
  "luz_values": [512, 498, ...],
  "semaforo_tiempos": {
    "Verde": 1200,
    "Amarillo": 300,
    "Rojo": 120
  },
  "verde_count": 5
}'''
        },
        {
            'url': '/sensors_view/',
            'method': 'GET',
            'description': 'Dashboard con gráficos Chart.js para visualización en tiempo real',
            'response_example': 'Renderiza template HTML con gráficos de temperatura, distancia, luz y semáforo'
        },
        {
            'url': '/dashboard/',
            'method': 'GET',
            'description': 'Vista principal del dashboard de usuario',
            'response_example': 'Renderiza dashboard.html'
        },
        {
            'url': '/',
            'method': 'GET',
            'description': 'Página principal del sistema (index.html)',
            'response_example': 'Dashboard ergonómico con widgets y alertas'
        }
    ]
    
    mqtt_topics = [
        {
            'topic': 'sensorsPHOLLEO/temp',
            'type': 'PUBLISH (Hardware → Backend)',
            'payload': 'float (°C)',
            'description': 'Lecturas del sensor de temperatura DHT22',
            'example': '28.5'
        },
        {
            'topic': 'sensorsPHOLLEO/sonido',
            'type': 'PUBLISH (Hardware → Backend)',
            'payload': 'float (cm)',
            'description': 'Distancia medida por sensor ultrasónico HC-SR04',
            'example': '45.2'
        },
        {
            'topic': 'sensorsPHOLLEO/luz',
            'type': 'PUBLISH (Hardware → Backend)',
            'payload': 'int (0-1023)',
            'description': 'Intensidad de luz ambiente medida por fotoresistor LDR',
            'example': '512'
        },
        {
            'topic': 'alertPHOLLEO/distancia',
            'type': 'PUBLISH (Hardware → Backend)',
            'payload': 'trigger',
            'description': 'Alerta cuando usuario está muy cerca de la pantalla (<40cm)',
            'example': '1'
        },
        {
            'topic': 'alertPHOLLEO/temp',
            'type': 'PUBLISH (Hardware → Backend)',
            'payload': 'float (°C)',
            'description': 'Alerta de temperatura fuera de rango (>30°C o <18°C)',
            'example': '32.5'
        },
        {
            'topic': 'alertPHOLLEO/luz',
            'type': 'PUBLISH (Hardware → Backend)',
            'payload': 'int',
            'description': 'Alerta de iluminación inadecuada (muy baja <200 o muy alta >800)',
            'example': '150'
        },
        {
            'topic': 'alertPHOLLEO/postura/Verde',
            'type': 'PUBLISH (Hardware → Backend)',
            'payload': 'int (segundos)',
            'description': 'Tiempo en postura correcta (LED verde activo)',
            'example': '120'
        },
        {
            'topic': 'alertPHOLLEO/postura/Amarillo',
            'type': 'PUBLISH (Hardware → Backend)',
            'payload': 'int (segundos)',
            'description': 'Tiempo en advertencia (LED amarillo activo)',
            'example': '60'
        },
        {
            'topic': 'alertPHOLLEO/postura/Rojo',
            'type': 'PUBLISH (Hardware → Backend)',
            'payload': 'int (segundos)',
            'description': 'Tiempo en postura incorrecta (LED rojo activo)',
            'example': '45'
        },
        {
            'topic': 'alertPHOLLEO/postura/AmarilloVerde',
            'type': 'PUBLISH (Hardware → Backend)',
            'payload': 'int (segundos)',
            'description': 'Transición de amarillo a verde (agregado a tiempo amarillo)',
            'example': '30'
        }
    ]
    
    models_info = [
        {
            'name': 'SensorTemp',
            'description': 'Almacena lecturas históricas del sensor de temperatura',
            'fields': 'value (FloatField), date (DateTimeField)'
        },
        {
            'name': 'SensorSonido',
            'description': 'Almacena lecturas del sensor ultrasónico (distancia)',
            'fields': 'value (FloatField), date (DateTimeField)'
        },
        {
            'name': 'SensorLuz',
            'description': 'Almacena lecturas del sensor de luz ambiente',
            'fields': 'value (FloatField), date (DateTimeField)'
        },
        {
            'name': 'Alert',
            'description': 'Notificaciones clasificadas por tipo con flag de visto/no visto',
            'fields': 'type_alert (CharField), message (CharField), created_at (DateTimeField), seen (BooleanField)'
        },
        {
            'name': 'Postura',
            'description': 'Registra tiempo en cada estado del semáforo (Verde/Amarillo/Rojo)',
            'fields': 'tiempo (IntegerField), semaforo (CharField), created_at (DateTimeField)'
        }
    ]
    
    micropython_info = {
        'file': 'MQTT_ERGONOMINADOR.py',
        'description': 'Script MicroPython para ESP32 que gestiona sensores y publica datos vía MQTT',
        'classes': [
            {
                'name': 'UltrasonicSensor',
                'pins': 'trigger=25, echo=26',
                'function': 'Mide distancia a pantalla cada 1s usando time_pulse_us'
            },
            {
                'name': 'Tank',
                'pins': 'temp_sensor=32, input_valve=22, output_valve=23, botones=21,4,15',
                'function': 'Gestiona control de llenado/drenado con monitoreo de temperatura'
            }
        ],
        'mqtt_logic': 'El ESP32 publica lecturas de sensores a topics sensorsPHOLLEO/* y alertas a alertPHOLLEO/* cuando se detectan condiciones fuera de rango'
    }
    
    context = {
        'readme_html': readme_html,
        'endpoints': endpoints,
        'mqtt_topics': mqtt_topics,
        'models': models_info,
        'micropython': micropython_info,
        'repo_url': 'https://github.com/LeonardoG2005/Ergonominador',
        'current_branch': 'main'
    }
    
    return render(request, 'pages/documentation.html', context)


def simple_markdown_to_html(markdown_text):
    """
    Conversión simple de markdown a HTML sin dependencias externas.
    Soporta: headers, listas, code blocks, bold, italic, links.
    """
    html = markdown_text
    
    # Code blocks (triple backticks)
    html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>', html, flags=re.DOTALL)
    
    # Headers
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Links
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    
    # Lists
    html = re.sub(r'^\- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Line breaks
    html = html.replace('\n\n', '</p><p>')
    html = '<p>' + html + '</p>'
    
    return html
