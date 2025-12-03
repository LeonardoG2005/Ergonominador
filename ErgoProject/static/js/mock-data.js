const MockDataGenerator = {
    init: function() {
        if (!localStorage.getItem('sensorData')) {
            this.resetData();
        }
        this.startSimulation();
    },

    resetData: function() {
        const initialData = {
            temp_timestamps: [],
            temp_values: [],
            sonido_timestamps: [],
            sonido_values: [],
            luz_timestamps: [],
            luz_values: [],
            semaforo_tiempos: { Verde: 0, Amarillo: 0, Rojo: 0 }
        };
        localStorage.setItem('sensorData', JSON.stringify(initialData));
    },

    generateSensorValue: function(min, max, previousValue) {
        if (previousValue !== undefined) {
            const delta = (Math.random() - 0.5) * 2;
            const newValue = previousValue + delta;
            return Math.max(min, Math.min(max, newValue));
        }
        return Math.random() * (max - min) + min;
    },

    updateSemaforoState: function(distancia, semaforoData) {
        if (distancia > 50) {
            semaforoData.Verde += 5;
        } else if (distancia >= 40) {
            semaforoData.Amarillo += 5;
        } else {
            semaforoData.Rojo += 5;
        }
    },

    addDataPoint: function() {
        const data = JSON.parse(localStorage.getItem('sensorData'));
        const now = new Date().toLocaleTimeString();
        
        const lastTemp = data.temp_values[data.temp_values.length - 1];
        const lastSonido = data.sonido_values[data.sonido_values.length - 1];
        const lastLuz = data.luz_values[data.luz_values.length - 1];

        const newTemp = this.generateSensorValue(22, 28, lastTemp);
        const newSonido = this.generateSensorValue(35, 65, lastSonido);
        const newLuz = this.generateSensorValue(300, 700, lastLuz);

        data.temp_timestamps.push(now);
        data.temp_values.push(parseFloat(newTemp.toFixed(2)));
        
        data.sonido_timestamps.push(now);
        data.sonido_values.push(parseFloat(newSonido.toFixed(2)));
        
        data.luz_timestamps.push(now);
        data.luz_values.push(parseFloat(newLuz.toFixed(2)));

        this.updateSemaforoState(newSonido, data.semaforo_tiempos);

        if (data.temp_timestamps.length > 20) {
            data.temp_timestamps.shift();
            data.temp_values.shift();
            data.sonido_timestamps.shift();
            data.sonido_values.shift();
            data.luz_timestamps.shift();
            data.luz_values.shift();
        }

        localStorage.setItem('sensorData', JSON.stringify(data));
    },

    getData: function() {
        return JSON.parse(localStorage.getItem('sensorData'));
    },

    startSimulation: function() {
        setInterval(() => {
            this.addDataPoint();
        }, 10000);
    }
};

MockDataGenerator.init();
