# Ergonominador - Sistema de Monitoreo Ergonómico IoT

> **🎯 Rama Actual: `demo`** - Versión de demostración con datos simulados (sin hardware IoT). Para documentación de producción con MQTT, consultar rama `main`.

---

## 🎭 Demo: Simulación Sin Hardware

Esta rama (`demo`) está diseñada para **demostración en portfolio** sin necesidad de hardware IoT ni broker MQTT. Todos los datos son generados algorítmicamente para simular comportamiento realista del sistema.

### Stack Tecnológico (Demo)

- **Backend**: Django 5.1.2 + SQLite (solo para servir frontend)
- **Simulación de datos**: Python (backend) + JavaScript (frontend opcional)
- **Frontend**: jQuery + Chart.js + Bootstrap 4
- **Base de datos**: **NO consultada** - datos en memoria/localStorage

### ¿Qué se eliminó vs. producción?

- ❌ Cliente MQTT (`mqtt_client.py` no se inicia)
- ❌ Conexión a HiveMQ Cloud
- ❌ Modelos de BD no se consultan (SensorTemp, Alert, etc.)
- ✅ **Mantenido intacto**: Todo el frontend Django, templates, assets CSS/JS

---

## 📊 Sistema de Simulación Inteligente

### Generación de Datos del Backend (`ErgoProject/views.py`)

#### 1. **Endpoint `/get-alerts/`** - Sistema de Alertas con Lógica de Transición

**Rangos de simulación**:
```python
Temperatura: 22-32°C (range extendido para generar alertas)
Distancia: 35-70cm
Luz: 150-850 (escala arbitraria)
```

**Umbrales de alerta** (ajustados para mayor frecuencia en demo):
```python
Temperatura: 
  - Alerta ALTA si > 28°C (antes 30°C en producción)
  - Alerta BAJA si < 20°C (antes 18°C)

Distancia: 
  - Alerta si < 45cm (antes 40cm - menos sensible)

Luz: 
  - Alerta BAJA si < 250 (antes 200)
  - Alerta ALTA si > 750 (antes 800)
```

**Lógica de `seen` flag**:
```python
# Solo dispara alerta cuando hay TRANSICIÓN de estado
temp_seen = not (temp_alert_triggered and not last_alert_state['temp']['alert_triggered'])

# Ejemplo: Si temp está en 29°C (alerta) desde hace 3 polling, seen=True (no vuelve a sonar alarma)
# Si temp baja a 27°C (normal) y luego sube a 30°C → seen=False (nueva alerta)
```

#### 2. **Endpoint `/get-sensor-data/`** - Datos Incrementales con Historia Persistente

**Función con estado** (usando atributo de función para persistencia):
```python
get_sensor_data.sensor_history = {
    'temp_timestamps': [],
    'temp_values': [],
    ...
}
```

**Algoritmo de valores suaves** (evita saltos bruscos):
```python
delta_temp = (random.random() - 0.5) * 2  # ±1°C máximo
new_temp = round(max(22, min(28, last_temp + delta_temp)), 2)

# Mantiene rango centrado 22-28°C para gráficas realistas
# Valores acumulados en ventana deslizante de 20 puntos
```

**Ventana de datos**:
- Almacena últimos **20 puntos** (pop si len > 20)
- Se genera nuevo punto cada **10 segundos** (via `setInterval` en JS)
- Frontend actualiza gráficas cada **5 segundos**

#### 3. **Sistema de Semáforo de Postura** - Ciclo Temporal de 4 Segundos

**Variables de estado global**:
```python
postura_state = {
    'start_time': time.time(),
    'current_cycle': 0,  # 0=Verde, 1=Amarillo, 2=Rojo
    'pausas_counter': 0,  # Incrementa cada ciclo completo (Rojo→Verde)
    'verde_count': 0,     # Veces que estuvo en Verde
    'amarillo_count': 0,  # Veces que estuvo en Amarillo
    'rojo_count': 0       # Veces que estuvo en Rojo
}
```

**Algoritmo de rotación automática**:
```python
elapsed_time = time.time() - postura_state['start_time']
cycle_position = int(elapsed_time / 4) % 3  # Cambia cada 4 segundos

# Secuencia: Verde(0) → Amarillo(1) → Rojo(2) → Verde(0) → ...
# Ciclo completo = 12 segundos (3 colores × 4s)
```

**Incremento de contadores** (en cada transición):
```python
if cycle_position != postura_state['current_cycle']:
    if postura_state['current_cycle'] == 0:
        postura_state['verde_count'] += 1  # Saliendo de Verde
    elif postura_state['current_cycle'] == 1:
        postura_state['amarillo_count'] += 1  # Saliendo de Amarillo
    elif postura_state['current_cycle'] == 2:
        postura_state['rojo_count'] += 1     # Saliendo de Rojo
        postura_state['pausas_counter'] += 1  # Completó ciclo (Rojo→Verde)
```

**Respuesta JSON** (enviada al frontend):
```json
{
  "semaforo_tiempos": {
    "Verde": 15,     // Veces que estuvo en Verde
    "Amarillo": 14,  // Veces en Amarillo
    "Rojo": 14       // Veces en Rojo
  },
  "verde_count": 14  // Pausas activas completadas (ciclos Rojo→Verde)
}
```

---

### Frontend - Tabla de Contadores Dinámicos (`templates/index.html`)

**Sección de Monitoreo de Posturas**:
```html
<tr>
  <td class="text-muted">LED Verde</td>
  <td><div id="progress-verde" class="progress-bar" style="width: 0%"></div></td>
  <td><h5 id="led-verde-count">0</h5></td>  <!-- Contador dinámico -->
</tr>
<!-- Similar para Amarillo y Rojo -->
```

**JavaScript - Actualización cada 5 segundos**:
```javascript
$("#led-verde-count").text(data.semaforo_tiempos['Verde']);
$("#led-amarillo-count").text(data.semaforo_tiempos['Amarillo']);
$("#led-rojo-count").text(data.semaforo_tiempos['Rojo']);

// Barras de progreso proporcionales
var total = Verde + Amarillo + Rojo;
var verdePercent = Math.round((Verde / total) * 100);
$("#progress-verde").css('width', verdePercent + '%');
```

**Inicialización**: Todos los contadores empiezan en **0** al cargar la página.

---

## 🎨 Características de la Demo

### ✅ Funcionalidades Implementadas

1. **Gráficas en Tiempo Real**:
   - Temperatura, Distancia, Luz: Líneas con acumulación progresiva (no random)
   - Semáforo: Gráfico dona mostrando distribución de tiempo por color

2. **Sistema de Alertas Inteligente**:
   - Sonido (`sound_alert.mp3`) solo en transiciones normal→alerta
   - Animación visual (borde rojo 3s) en tarjetas de alerta
   - Mensajes contextuales según tipo de alerta

3. **Contadores de Postura**:
   - LED Verde/Amarillo/Rojo: Incrementan cada vez que el semáforo SALE de ese color
   - Pausas activas: Contador de ciclos completos (Rojo→Verde)
   - Barras de progreso proporcionales al total

4. **Datos Persistentes Durante Sesión**:
   - Historia de sensores acumulada en `sensor_history` (atributo de función)
   - Estado de semáforo persistente en `postura_state`
   - Reset solo al reiniciar servidor Django

---

## 🚀 Ejecución de la Demo

### Prerrequisitos

```bash
pip install django
```

### Iniciar servidor (rama demo)

```bash
git checkout demo  # Asegurarse de estar en rama demo
cd ErgoProject
python manage.py runserver
```

### Acceder al dashboard

- **Dashboard principal**: http://localhost:8000/
- **Vista de gráficas**: http://localhost:8000/sensors_view/

### Comportamiento esperado

1. Al abrir dashboard, contadores de LED en **0**
2. Cada **4 segundos**, semáforo cambia de color (Verde→Amarillo→Rojo→Verde)
3. Contadores incrementan al SALIR de cada color
4. Gráficas acumulan datos progresivamente (ventana de 20 puntos)
5. Alertas suenan solo cuando valores **cruzan** umbrales (no constantemente)

---

## 🔧 Diferencias Técnicas: Demo vs. Producción

| Aspecto | **Rama Demo** | **Rama Main (Producción)** |
|---------|---------------|----------------------------|
| **MQTT** | ❌ Deshabilitado (`wsgi.py` limpio) | ✅ Cliente activo, suscrito a topics |
| **Datos sensores** | 🎲 Simulados algorítmicamente | 📡 Recibidos de hardware IoT |
| **Base de datos** | 💤 No consultada | 📊 Lecturas y alertas persistidas |
| **Semáforo** | ⏱️ Ciclo temporal fijo (4s) | 🚦 Basado en postura real del usuario |
| **Alertas** | 🔔 Lógica de transición simulada | 🚨 Disparadas por hardware |
| **Umbral distancia** | < 45cm (menos sensible) | < 40cm (producción) |
| **Umbral temperatura** | 20-28°C (más alertas) | 18-30°C (producción) |
| **Umbral luz** | 250-750 (más alertas) | 200-800 (producción) |

---

## 📝 Archivos Modificados para Demo

### Backend
- `ErgoProject/wsgi.py`: ❌ Eliminadas líneas de `start_mqtt_client()`
- `ErgoProject/views.py`: ✅ Lógica completa de simulación inteligente
  - `get_alerts()`: Generación de valores random + detección de transiciones
  - `get_sensor_data()`: Historia incremental con ventana deslizante
  - `postura_state`: Sistema de ciclo temporal con contadores

### Frontend
- `templates/index.html`: 
  - ✅ IDs agregados: `#led-verde-count`, `#led-amarillo-count`, `#led-rojo-count`
  - ✅ JavaScript para actualizar contadores y barras de progreso
  - ✅ Valores iniciales cambiados de hardcoded (664, 560, 793) → 0

### Otros
- `static/js/mock-data.js`: ⚠️ Presente pero **NO usado en esta demo** (opcional para versión standalone)
- `demo-dashboard/`: ⚠️ Carpeta eliminada (era versión anterior sin Django)

---

## 🎓 Uso en Portfolio

### Ventajas de esta rama

- ✅ **No requiere hardware**: Demo ejecutable en cualquier laptop
- ✅ **Comportamiento realista**: Algoritmos de suavizado y transiciones naturales
- ✅ **Visualmente idéntica**: Mantiene toda la UI de producción
- ✅ **Educativa**: Código comentado muestra arquitectura real de IoT

### Para presentaciones

1. Mostrar dashboard en ejecución (localhost:8000)
2. Explicar diferencias demo vs. producción usando tabla comparativa
3. Enfatizar que **rama `main` tiene código completo de MQTT + persistencia BD**
4. Opcional: Mostrar archivo `views.py` para explicar lógica de simulación

---

## 🔗 Recursos Adicionales

- **Rama Main (Producción)**: `git checkout main` → Documentación de arquitectura IoT real
- **Broker MQTT**: HiveMQ Cloud (credenciales en `mqtt_client.py` de rama main)
- **Sensores físicos**: Temperatura (DHT22), Ultrasonido (HC-SR04), Luz (LDR)

---

## 📄 Licencia

Proyecto educativo - Universidad de Medellín © 2024