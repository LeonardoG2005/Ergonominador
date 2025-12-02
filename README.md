# Ergonominador - Sistema de Monitoreo Ergonómico IoT

## Arquitectura General

Sistema Django que integra sensores IoT vía MQTT para monitorear condiciones ergonómicas del espacio de trabajo. La arquitectura sigue el patrón: **Hardware → MQTT Broker → Backend Django → Frontend Dashboard**.

### Stack Tecnológico

- **Backend**: Django 5.1.2 + SQLite
- **Comunicación IoT**: MQTT (Paho-MQTT + HiveMQ Cloud)
- **Frontend**: jQuery + Chart.js + Bootstrap 4
- **Protocolo**: MQTT over TLS (puerto 8883)

## Componentes Clave

### 1. Cliente MQTT (mqttApp/mqtt_client.py)

**Responsabilidad**: Suscripción permanente a topics, recepción de datos de sensores y persistencia en BD.

**Topics suscritos**:
- `sensorsPHOLLEO/{temp|sonido|luz}` - Lecturas de sensores
- `alertPHOLLEO/{distancia|temp|luz}` - Alertas generadas por hardware
- `alertPHOLLEO/postura/{Verde|Amarillo|Rojo|AmarilloVerde}` - Estados del semáforo de postura

**Inicio**: Se ejecuta automáticamente en `wsgi.py` al desplegar Django, creando un thread daemon que mantiene conexión MQTT permanente.

### 2. Modelos de Datos (mqttApp/models.py)

- **SensorTemp/SensorSonido/SensorLuz**: Almacenan lecturas históricas (valor + timestamp)
- **Alert**: Notificaciones clasificadas por tipo (Distancia, Temperatura, Luz, Postura) con flag `seen`
- **Postura**: Registra tiempo en cada estado del semáforo (Verde/Amarillo/Rojo)

### 3. API REST (ErgoProject/views.py)

- **/get-alerts/**: Devuelve última alerta no vista por tipo + estado actual del semáforo
- **/get-sensor-data/**: Datos de últimos 5 minutos + agregados de tiempo por color de semáforo
- **/sensors_view/**: Dashboard con gráficos en tiempo real (polling cada 5s)

### 4. Frontend

**Dashboard principal** (`get_sensorData.html`): 4 gráficos Chart.js actualizados vía AJAX polling:
- Temperatura (°C), Ultrasonido (cm), Luz (intensidad) - tipo línea
- Semáforo de postura - gráfico dona mostrando distribución temporal

## Flujo IoT Real

### Hardware → Backend

1. **Sensores físicos** (temperatura, ultrasonido, fotoresistor) conectados a microcontrolador (ej: ESP32/Arduino)
2. **Microcontrolador** publica datos vía WiFi al broker MQTT público (HiveMQ):
   ```
   PUBLISH sensorsPHOLLEO/temp → 28.5
   PUBLISH alertPHOLLEO/distancia → trigger
   ```
3. **Backend Django** recibe mensajes en tiempo real y almacena en SQLite
4. **Frontend** consulta API vía polling y visualiza datos históricos

### Sistema de Semáforo (2 LEDs)

**Lógica del circuito**: El hardware mide distancia a pantalla con sensor ultrasónico. Según el tiempo transcurrido en postura adecuada/inadecuada, activa LEDs indicadores:

- **LED Verde**: Postura correcta (distancia >50cm). Tiempo acumulado enviado como `alertPHOLLEO/postura/Verde`
- **LED Amarillo**: Advertencia preventiva (40-50cm o tiempo límite acercándose). Topic: `postura/Amarillo`
- **LED Rojo**: Postura incorrecta (<40cm). El circuito publica `postura/Rojo` con segundos transcurridos

**Transiciones**: El hardware envía `postura/AmarilloVerde` cuando cambia de amarillo→verde (agregado a tiempo amarillo en backend).

El dashboard muestra proporción de tiempo en cada estado vía gráfico dona, permitiendo análisis de hábitos posturales.

## Ejecución Local

### Prerrequisitos

```bash
pip install django paho-mqtt
```

### Iniciar servidor

```bash
cd ErgoProject
python manage.py migrate
python manage.py runserver
```

### Endpoints principales

- **Dashboard gráficos**: http://localhost:8000/sensors_view/
- **API alertas**: http://localhost:8000/get-alerts/
- **API datos sensores**: http://localhost:8000/get-sensor-data/

## Datos Esperados en Producción

**MQTT Topics** (publicados por hardware):
```
sensorsPHOLLEO/temp: float (°C)
sensorsPHOLLEO/sonido: float (cm del ultrasonido)
sensorsPHOLLEO/luz: int (0-1023 sensor analógico)
alertPHOLLEO/distancia: trigger (valor ignorado)
alertPHOLLEO/temp: float (valor que disparó alerta)
alertPHOLLEO/postura/{color}: int (segundos en ese estado)
```

**Response /get-sensor-data/**:
```json
{
  "temp_timestamps": ["2025-12-02 14:30:15", ...],
  "temp_values": [28.5, 29.1, ...],
  "semaforo_tiempos": {"Verde": 1200, "Amarillo": 300, "Rojo": 120},
  "verde_count": 5
}
```