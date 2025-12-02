from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta
import random

def get_alerts(request):
    mock_alerts = {
        'Distancia': {
            "type_alert": "Distancia",
            "message": "Postura correcta",
            "created_at": datetime.now().strftime("%H:%M:%S"),
            "seen": False
        },
        'Temperatura': {
            "type_alert": "Temperatura",
            "message": "Temperatura ambiente normal",
            "created_at": datetime.now().strftime("%H:%M:%S"),
            "seen": False
        },
        'Luz': {
            "type_alert": "Luz",
            "message": "Iluminación adecuada",
            "created_at": datetime.now().strftime("%H:%M:%S"),
            "seen": False
        },
        'Postura': {
            "tiempo": random.randint(60, 300),
            "semaforo": random.choice(['Verde', 'Amarillo', 'Rojo']),
            "created_at": datetime.now().strftime("%H:%M:%S")
        }
    }
    return JsonResponse(mock_alerts, safe=False)

def dashboard_view(request):
    return render(request, "dashboard.html")

def get_sensor_data(request):
    now = datetime.now()
    timestamps = [(now - timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S") for i in range(10, 0, -1)]
    
    mock_data = {
        "temp_timestamps": timestamps,
        "temp_values": [round(20 + random.uniform(0, 10), 2) for _ in range(10)],
        "sonido_timestamps": timestamps,
        "sonido_values": [round(20 + random.uniform(0, 60), 2) for _ in range(10)],
        "luz_timestamps": timestamps,
        "luz_values": [random.randint(200, 800) for _ in range(10)],
        'semaforo_tiempos': {
            'Verde': random.randint(500, 2000),
            'Amarillo': random.randint(100, 500),
            'Rojo': random.randint(50, 300)
        },
        'verde_count': random.randint(3, 15)
    }
    return JsonResponse(mock_data)

def sensors_view(request):
    return render(request, "get_sensorData.html")

def index(request):
    return render(request, 'index.html')

def buttons(request):
    return render(request, 'pages/ui-features/buttons.html')

def dropdowns(request):
    return render(request, 'pages/ui-features/dropdowns.html')

def typography(request):
    return render(request, 'pages/ui-features/typography.html')

def basic_elements(request):
    return render(request, 'pages/tables/basic_table.html')

def basic_tables(request):
    return render(request, 'pages/forms/basic_elements.html')

# Vista para el archivo ChartJs
def chart(request):
    return render(request, 'pages/charts/chartjs.html')

def mdi_view(request):
    return render(request, 'pages/icons/mdi.html')

# Nueva vista para Login
def login_view(request):
    return render(request, 'pages/samples/login.html')

# Nueva vista para Register
def register_view(request):
    return render(request, 'pages/samples/register.html')