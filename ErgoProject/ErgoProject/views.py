from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta
import random
import time

last_alert_state = {
    'temp': {'value': 25, 'alert_triggered': False},
    'distancia': {'value': 50, 'alert_triggered': False},
    'luz': {'value': 500, 'alert_triggered': False}
}

postura_state = {
    'start_time': time.time(),
    'current_cycle': 0,
    'pausas_counter': 0,
    'verde_count': 0,
    'amarillo_count': 0,
    'rojo_count': 0
}

def get_alerts(request):
    global last_alert_state, postura_state
    
    current_temp = round(22 + random.uniform(0, 10), 2)
    current_distancia = round(35 + random.uniform(0, 35), 2)
    current_luz = random.randint(150, 850)
    
    temp_alert_triggered = current_temp > 28 or current_temp < 20
    distancia_alert_triggered = current_distancia < 45
    luz_alert_triggered = current_luz < 250 or current_luz > 750
    
    temp_message = "Temperatura ambiente normal"
    if current_temp > 30:
        temp_message = f"⚠️ Temperatura alta: {current_temp}°C - Considere ventilar el área"
    elif current_temp < 18:
        temp_message = f"⚠️ Temperatura baja: {current_temp}°C - Ambiente muy frío"
    
    distancia_message = "Postura correcta"
    if current_distancia < 43:
        distancia_message = f"⚠️ Muy cerca de la pantalla: {current_distancia}cm - Aléjese"
    
    luz_message = "Iluminación adecuada"
    if current_luz < 220:
        luz_message = f"⚠️ Poca luz: {current_luz} - Ambiente muy oscuro"
    elif current_luz > 775:
        luz_message = f"⚠️ Exceso de luz: {current_luz} - Demasiado brillo"
    
    temp_seen = not (temp_alert_triggered and not last_alert_state['temp']['alert_triggered'])
    distancia_seen = not (distancia_alert_triggered and not last_alert_state['distancia']['alert_triggered'])
    luz_seen = not (luz_alert_triggered and not last_alert_state['luz']['alert_triggered'])
    
    last_alert_state['temp']['value'] = current_temp
    last_alert_state['temp']['alert_triggered'] = temp_alert_triggered
    last_alert_state['distancia']['value'] = current_distancia
    last_alert_state['distancia']['alert_triggered'] = distancia_alert_triggered
    last_alert_state['luz']['value'] = current_luz
    last_alert_state['luz']['alert_triggered'] = luz_alert_triggered
    
    elapsed_time = time.time() - postura_state['start_time']
    cycle_position = int(elapsed_time / 4) % 3
    
    if cycle_position != postura_state['current_cycle']:
        if postura_state['current_cycle'] == 0:
            postura_state['verde_count'] += 1
        elif postura_state['current_cycle'] == 1:
            postura_state['amarillo_count'] += 1
        elif postura_state['current_cycle'] == 2:
            postura_state['rojo_count'] += 1
            postura_state['pausas_counter'] += 1
        
        postura_state['current_cycle'] = cycle_position
    
    semaforo_colors = ['Verde', 'Amarillo', 'Rojo']
    current_semaforo = semaforo_colors[cycle_position]
    
    mock_alerts = {
        'Distancia': {
            "type_alert": "Distancia",
            "message": distancia_message,
            "created_at": datetime.now().strftime("%H:%M:%S"),
            "seen": distancia_seen
        },
        'Temperatura': {
            "type_alert": "Temperatura",
            "message": temp_message,
            "created_at": datetime.now().strftime("%H:%M:%S"),
            "seen": temp_seen
        },
        'Luz': {
            "type_alert": "Luz",
            "message": luz_message,
            "created_at": datetime.now().strftime("%H:%M:%S"),
            "seen": luz_seen
        },
        'Postura': {
            "tiempo": int(elapsed_time % 20),
            "semaforo": current_semaforo,
            "created_at": datetime.now().strftime("%H:%M:%S")
        }
    }
    return JsonResponse(mock_alerts, safe=False)

def dashboard_view(request):
    return render(request, "dashboard.html")

def get_sensor_data(request):
    if not hasattr(get_sensor_data, 'sensor_history'):
        get_sensor_data.sensor_history = {
            'temp_timestamps': [],
            'temp_values': [],
            'sonido_timestamps': [],
            'sonido_values': [],
            'luz_timestamps': [],
            'luz_values': []
        }
    
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    last_temp = get_sensor_data.sensor_history['temp_values'][-1] if get_sensor_data.sensor_history['temp_values'] else 25
    last_sonido = get_sensor_data.sensor_history['sonido_values'][-1] if get_sensor_data.sensor_history['sonido_values'] else 50
    last_luz = get_sensor_data.sensor_history['luz_values'][-1] if get_sensor_data.sensor_history['luz_values'] else 500
    
    delta_temp = (random.random() - 0.5) * 2
    delta_sonido = (random.random() - 0.5) * 2
    delta_luz = (random.random() - 0.5) * 20
    
    new_temp = round(max(22, min(28, last_temp + delta_temp)), 2)
    new_sonido = round(max(35, min(65, last_sonido + delta_sonido)), 2)
    new_luz = int(max(300, min(700, last_luz + delta_luz)))
    
    get_sensor_data.sensor_history['temp_timestamps'].append(current_time)
    get_sensor_data.sensor_history['temp_values'].append(new_temp)
    get_sensor_data.sensor_history['sonido_timestamps'].append(current_time)
    get_sensor_data.sensor_history['sonido_values'].append(new_sonido)
    get_sensor_data.sensor_history['luz_timestamps'].append(current_time)
    get_sensor_data.sensor_history['luz_values'].append(new_luz)
    
    if len(get_sensor_data.sensor_history['temp_timestamps']) > 20:
        get_sensor_data.sensor_history['temp_timestamps'].pop(0)
        get_sensor_data.sensor_history['temp_values'].pop(0)
        get_sensor_data.sensor_history['sonido_timestamps'].pop(0)
        get_sensor_data.sensor_history['sonido_values'].pop(0)
        get_sensor_data.sensor_history['luz_timestamps'].pop(0)
        get_sensor_data.sensor_history['luz_values'].pop(0)
    
    elapsed_time = time.time() - postura_state['start_time']
    total_cycles = int(elapsed_time / 60)
    
    mock_data = {
        "temp_timestamps": get_sensor_data.sensor_history['temp_timestamps'],
        "temp_values": get_sensor_data.sensor_history['temp_values'],
        "sonido_timestamps": get_sensor_data.sensor_history['sonido_timestamps'],
        "sonido_values": get_sensor_data.sensor_history['sonido_values'],
        "luz_timestamps": get_sensor_data.sensor_history['luz_timestamps'],
        "luz_values": get_sensor_data.sensor_history['luz_values'],
        'semaforo_tiempos': {
            'Verde': postura_state['verde_count'],
            'Amarillo': postura_state['amarillo_count'],
            'Rojo': postura_state['rojo_count']
        },
        'verde_count': postura_state['pausas_counter']
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