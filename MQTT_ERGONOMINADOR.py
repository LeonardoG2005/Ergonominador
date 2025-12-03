from machine import Pin, time_pulse_us, ADC, Timer
import time
import _thread
import gc  # Asegurarse de que se recolecta memoria periódicamente
from machine import Pin, Timer
import _thread
import time
import gc

class UltrasonicSensor:
    def __init__(self, trigger_number=25, echo_number=26):
        self.trigger_number = trigger_number
        self.echo_number = echo_number
        self.trigger = Pin(self.trigger_number, Pin.OUT)
        self.trigger.value(0)
        self.echo = Pin(self.echo_number, Pin.IN)
        self.level = None
        self.lock = _thread.allocate_lock()  # Semáforo para proteger acceso concurrente
        
        # Mover la ejecución de la tarea a un thread
        _thread.start_new_thread(self.measure_duration, ())
    
    def measure_duration(self):
        while True:
            self.trigger.value(1)
            #print("[INFO] Powering up trisger!")
            time.sleep(10e-6)
            ##print("[INFO] Powering down trisger!")
            self.trigger.value(0)
            #time.sleep(0.01)
            
            duracion = time_pulse_us(self.echo,1)
            with self.lock:
                measured_distance = (duracion * 0.0340) /2
                self.level = 100 - measured_distance  # Calcular el nivel del tanque
                print(f"Distancia: {measured_distance} cm")
                print(f"Current level: {self.level} cm")
            
            time.sleep(1)
        
    

class Tank:
    def __init__(self, filling_button=21, draining_button=4, stop_button=15, input_valve_pin=22, output_valve_pin=23, temp_sensor_pin=32, num_samples=100, max_level=90
                 , min_level=75, max_temp=20, adc_min=0, adc_max=1697, v_min=0, v_max=150):
        # Inicialización de atributos
        self.adc_min = adc_min
        self.adc_max = adc_max
        self.v_min = v_min
        self.v_max = v_max

        self.executing = False  # Cambiado a False para iniciar detenido
        self.lock = _thread.allocate_lock()  # Semáforo para acceso a válvulas

        # Válvulas
        self.input_valve = Pin(input_valve_pin, Pin.OUT)
        self.output_valve = Pin(output_valve_pin, Pin.OUT)

        # Botones
        self.filling_button = Pin(filling_button, Pin.IN, Pin.PULL_DOWN)
        self.draining_button = Pin(draining_button, Pin.IN, Pin.PULL_DOWN)
        self.stop_button = Pin(stop_button, Pin.IN, Pin.PULL_DOWN)

        # Sensor de temperatura
        self.temp_sensor = ADC(temp_sensor_pin)
        self.temp_sensor.atten(ADC.ATTN_11DB)

        # Sensor ultrasónico
        self.ultrasonic = UltrasonicSensor()

        self.max_level = max_level
        self.min_level = min_level
        self.max_temp = max_temp
        self.numTemp_samples = num_samples
        self.temp_value = None

        # Inicializar temporizadores como None
        self.fill_timer = None
        self.drain_timer = None

        _thread.start_new_thread(self.read_temperature, ())

        # Configurar interrupciones para botones
        self.filling_button.irq(trigger=Pin.IRQ_FALLING, handler=self.debounceFilling)
        self.draining_button.irq(trigger=Pin.IRQ_FALLING, handler=self.debounceDraining)
        self.stop_button.irq(trigger=Pin.IRQ_FALLING, handler=self.debounceStopping)

        self.timF = Timer(0)
        self.timD = Timer(1)
        self.timS = Timer(2)

    def debounceFilling(self, input_pin):
        self.timF.init(mode=Timer.ONE_SHOT, period=200, callback=self.start_filling)

    def debounceDraining(self, input_pin):
        self.timD.init(mode=Timer.ONE_SHOT, period=200, callback=self.start_draining)

    def debounceStopping(self, input_pin=None):
        self.timS.init(mode=Timer.ONE_SHOT, period=200, callback=self.stop_process)

    def start_filling(self, tim):
        with self.lock:  # Asegurar que sólo un proceso acceda a las válvulas
            self.executing = True  # Establecer a True al iniciar el llenado
            #if self.drain_timer is not None:
                #self.drain_timer.deinit()
                #print("switching from draining to filling")
            if self.ultrasonic.level >= self.max_level:
                print("[ALERT] Tank is already full.")
            else:
                self.input_valve.value(1)
                self.fill_timer = Timer(3)  # Crear el temporizador
                self.fill_timer.init(period=100, mode=Timer.PERIODIC, callback=self.check_filling)

    def check_filling(self, t):
        if self.ultrasonic.level >= self.max_level or not self.executing:
            self.input_valve.value(0)
            if self.fill_timer is not None:
                self.fill_timer.deinit()  # Detener el temporizador
                print("[INFO] Fill timer stopped.")
                self.fill_timer = None  # Restablecer a None después de detener
            print("Tank filled successfully.")
        else:
            print("[INFO] Filling tank...")

    def start_draining(self, tim):
        with self.lock:  # Asegurar que sólo un proceso acceda a las válvulas
            self.executing = True  # Establecer a True al iniciar el drenado
            #if self.fill is not None:
                #self.fill.deinit()
                #print("switching from filling to draining")
            if self.ultrasonic.level <= self.min_level:
                print("[ALERT] Tank is already at the minimum level.")
            else:
                self.output_valve.value(1)
                self.drain_timer = Timer(4)  # Crear el temporizador
                self.drain_timer.init(period=100, mode=Timer.PERIODIC, callback=self.check_draining)

    def check_draining(self, t):
        if self.ultrasonic.level <= self.min_level or not self.executing:
            self.output_valve.value(0)
            if self.drain_timer is not None:
                self.drain_timer.deinit()  # Detener el temporizador
                print("[INFO] Drain timer stopped.")
                self.drain_timer = None  # Restablecer a None después de detener
            print("Tank drained successfully.")
        else:
            print("[INFO] Draining tank...")

    def stop_process(self, tim=None):
        with self.lock:
            self.input_valve.value(0)
            self.output_valve.value(0)
            print("Stopping all processes...")

            # Comprobar si los temporizadores están activos
            if self.fill_timer is not None:
                self.fill_timer.deinit()  # Detener el temporizador
                print("[INFO] Fill timer stopped.")
                self.fill_timer = None  # Restablecer a None después de detener

            if self.drain_timer is not None:
                self.drain_timer.deinit()  # Detener el temporizador
                print("[INFO] Drain timer stopped.")
                self.drain_timer = None  # Restablecer a None después de detener

            self.executing = False  # Reiniciar ejecutando a False
        time.sleep_ms(100)
        print("[INFO] All processes stopped.")

    def read_temperature(self):
        while True:
            list_values = []
            for i in range(0, self.numTemp_samples):
                value = self.temp_sensor.read()
                list_values.append(value)
                time.sleep(1e-3)
            list_values.sort()
            self.temp_value = (list_values[self.numTemp_samples // 2] + list_values[self.numTemp_samples // 2 + 1]) / 2
            self.temp_value = self.scale_temp()
            if self.temp_value >= self.max_temp:
                print("[WARNING] High temperature detected.")
                self.stop_process()
            time.sleep(1)

    def scale_temp(self):
        m = (self.v_max - self.v_min) / (self.adc_max - self.adc_min)
        b = self.v_min - m * self.adc_min
        value = m * self.temp_value + b
        print(f"[INFO] Temperature: {value:.2f} degrees")
        return value
    
    

if __name__ == "__main__":
    System = Tank()
    try:
        while True:
            gc.collect()  # Liberar memoria
            time.sleep(2)
    except KeyboardInterrupt:
        print("Program terminated.")

