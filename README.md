# 🏭 IoT Temperature Monitoring System with HiveMQ

A real-time IoT temperature monitoring system using HiveMQ Cloud as MQTT broker for secure sensor data communication and alerting.

## 📋 Overview

This project demonstrates a complete IoT solution that:
- Simulates multiple temperature sensors across different locations
- Uses **HiveMQ Cloud** for secure MQTT messaging
- Implements real-time alerting for temperature thresholds
- Stores sensor data locally with SQLite
- Provides structured topic architecture for scalable IoT communication

## 🏗️ Architecture

```
[Temperature Sensors] → [HiveMQ Cloud MQTT Broker] → [Monitoring System]
                                   ↓
                            [Local SQLite Storage]
                                   ↓
                              [Alert System]
```

## ✨ Features

- **🔒 Secure Communication**: SSL/TLS encrypted MQTT over HiveMQ Cloud
- **📊 Real-time Monitoring**: Live temperature data from multiple sensors
- **🚨 Smart Alerting**: Automatic alerts for high/low temperature thresholds
- **💾 Data Persistence**: Local SQLite database for historical data
- **🔄 Robust Connection**: Auto-reconnection and error handling
- **📈 QoS Management**: Different quality of service levels for messages
- **🎯 Topic Structure**: Organized MQTT topics for scalability

## 🛠️ Tech Stack

- **Python 3.7+**
- **HiveMQ Cloud** (MQTT Broker)
- **Paho MQTT Client**
- **SQLite** (Local Storage)
- **Threading** (Concurrent Sensor Simulation)

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- HiveMQ Cloud account (free tier available)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd hivemq-iot-monitoring
   ```

2. **Install dependencies**
   ```bash
   pip install paho-mqtt
   ```

3. **Configure HiveMQ Cloud**
   - Create a free account at [HiveMQ Cloud](https://www.hivemq.com/)
   - Create a new cluster
   - Note your cluster URL, username, and password

4. **Update configuration**
   Edit the configuration variables in the script:
   ```python
   HIVEMQ_HOST = "your-cluster.s1.eu.hivemq.cloud"
   HIVEMQ_USERNAME = "your_username"
   HIVEMQ_PASSWORD = "your_password"
   ```

## 🚀 Usage

### Basic Execution
```bash
python iot_monitoring_system.py
```

### Expected Output
```
🏭 Système IoT de Surveillance avec HiveMQ
==================================================
➕ Capteur ajouté: TEMP_001 (Atelier Production)
➕ Capteur ajouté: TEMP_002 (Entrepôt)
➕ Capteur ajouté: TEMP_003 (Bureau)
➕ Capteur ajouté: TEMP_004 (Salle Serveurs)
🔄 Connexion à HiveMQ Cloud...
✅ Connecté à HiveMQ Cloud!
🚀 Démarrage système IoT avec HiveMQ...
📤 Données envoyées: TEMP_001 - 24.5°C
📤 Données envoyées: TEMP_002 - 19.8°C
🚨 ALERTE: Température élevée détectée: 38.2°C
```

### Stop the System
Press `Ctrl+C` to gracefully stop the monitoring system.

## 📡 MQTT Topics Structure

| Topic | Purpose | QoS | Description |
|-------|---------|-----|-------------|
| `factory/sensors/temperature` | Sensor Data | 1 | Real-time temperature readings |
| `factory/alerts/temperature` | Alerts | 2 | Temperature threshold alerts |
| `factory/sensors/status` | System Status | 1 | System online/offline status |

## 🔧 Configuration

### Temperature Thresholds
```python
temp_threshold_high = 35.0  # °C
temp_threshold_low = 10.0   # °C
```

### Sensor Update Intervals
```python
sensor_reading_interval = 2    # seconds
cycle_pause = 5               # seconds between full cycles
```

### HiveMQ Connection Settings
```python
HIVEMQ_PORT = 8883           # SSL/TLS port
keepalive = 60               # seconds
```

## 📊 Data Format

### Sensor Data Message
```json
{
  "sensor_id": "TEMP_001",
  "location": "Atelier Production",
  "temperature": 24.5,
  "timestamp": "2024-08-14T10:30:00.123456",
  "unit": "celsius"
}
```

### Alert Message
```json
{
  "alert_type": "HIGH_TEMPERATURE",
  "sensor_id": "TEMP_001",
  "location": "Atelier Production",
  "temperature": 38.2,
  "threshold": 35.0,
  "message": "Température élevée détectée: 38.2°C",
  "timestamp": "2024-08-14T10:30:00.123456",
  "severity": "HIGH"
}
```

## 🗄️ Database Schema

```sql
CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT,
    location TEXT,
    temperature REAL,
    timestamp TEXT,
    alert_triggered BOOLEAN DEFAULT FALSE
);
```

## 🔍 Monitoring

### View Database Content
```python
import sqlite3
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 10")
print(cursor.fetchall())
```

### HiveMQ Cloud Dashboard
Access your HiveMQ Cloud dashboard to monitor:
- Connection status
- Message throughput
- Topic activity
- Client sessions

## 🛡️ Security Features

- **TLS Encryption**: All communications encrypted in transit
- **Authentication**: Username/password authentication with HiveMQ
- **QoS Levels**: Appropriate quality of service for different message types
- **Error Handling**: Robust connection and message handling

## 🔧 Troubleshooting

### Common Issues

**Connection Failed**
- Verify HiveMQ credentials
- Check network connectivity
- Ensure TLS support is available

**No Messages Received**
- Verify topic subscriptions
- Check QoS levels
- Review HiveMQ Cloud logs

**Database Errors**
- Ensure write permissions in current directory
- Check SQLite installation

## 📈 Extending the Project

### Add New Sensor Types
```python
class HumiditySensor(TemperatureSensor):
    def generate_humidity(self):
        return random.uniform(30.0, 80.0)
```

### Custom Alert Rules
```python
def check_custom_alerts(self, sensor_data):
    # Implement custom alerting logic
    pass
```

### Web Dashboard
- Add Flask/FastAPI web interface
- Implement real-time charts with WebSockets
- Create historical data visualization


## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📞 Contact

For questions about this HiveMQ implementation, feel free to reach out.

---

*Built with ❤️ using HiveMQ Cloud and Python*