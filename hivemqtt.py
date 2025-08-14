# Système IoT de Surveillance de Température avec HiveMQ
# Projet démonstratif pour acquérir une expérience pratique avec HiveMQ

import paho.mqtt.client as mqtt
import json
import time
import random
import threading
from datetime import datetime
import sqlite3

# Configuration HiveMQ Cloud
HIVEMQ_HOST = "8b45fd6b0b6542839db63ad243e4deea.s1.eu.hivemq.cloud"  # my cluster
HIVEMQ_PORT = 8883
HIVEMQ_USERNAME = "hivemq.webclient.1755185938603"
HIVEMQ_PASSWORD = "AkZ9X30wYO@byl6,?>Sa"

# Topics MQTT
TEMP_TOPIC = "factory/sensors/temperature"
ALERT_TOPIC = "factory/alerts/temperature"
STATUS_TOPIC = "factory/sensors/status"

class TemperatureSensor:
    """Simulateur de capteur de température"""
    
    def __init__(self, sensor_id, location):
        self.sensor_id = sensor_id
        self.location = location
        self.is_running = False
        
    def generate_temperature(self):
        """Génère une température réaliste avec variations"""
        base_temp = 22.0  # Température de base
        variation = random.uniform(-3.0, 8.0)  # Variation normale
        
        # Simulation d'anomalies occasionnelles
        if random.random() < 0.05:  # 5% de chance d'anomalie
            variation += random.uniform(15.0, 25.0)
            
        return round(base_temp + variation, 2)
    
    def get_sensor_data(self):
        """Retourne les données du capteur au format JSON"""
        return {
            "sensor_id": self.sensor_id,
            "location": self.location,
            "temperature": self.generate_temperature(),
            "timestamp": datetime.now().isoformat(),
            "unit": "celsius"
        }

class HiveMQManager:
    """Gestionnaire de connexion et communication HiveMQ"""
    
    def __init__(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(HIVEMQ_USERNAME, HIVEMQ_PASSWORD)
        self.client.tls_set()  # SSL/TLS pour HiveMQ Cloud
        
        # Callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        self.is_connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback de connexion"""
        if rc == 0:
            print(f"✅ Connecté à HiveMQ Cloud!")
            self.is_connected = True
            
            # S'abonner aux topics d'alerte
            client.subscribe(ALERT_TOPIC)
            client.subscribe(STATUS_TOPIC)
            
        else:
            print(f"❌ Échec de connexion, code: {rc}")
            
    def on_message(self, client, userdata, msg):
        """Callback de réception de message"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            if topic == ALERT_TOPIC:
                self.handle_temperature_alert(payload)
            elif topic == STATUS_TOPIC:
                self.handle_status_update(payload)
                
        except Exception as e:
            print(f"❌ Erreur traitement message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback de déconnexion"""
        print("🔌 Déconnecté de HiveMQ")
        self.is_connected = False
    
    def connect(self):
        """Connexion à HiveMQ Cloud"""
        try:
            print("🔄 Connexion à HiveMQ Cloud...")
            self.client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
            self.client.loop_start()
            
            # Attendre la connexion
            timeout = 10
            while not self.is_connected and timeout > 0:
                time.sleep(1)
                timeout -= 1
                
            return self.is_connected
            
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    def publish_sensor_data(self, sensor_data):
        """Publier les données de capteur"""
        if self.is_connected:
            payload = json.dumps(sensor_data)
            result = self.client.publish(TEMP_TOPIC, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"📤 Données envoyées: {sensor_data['sensor_id']} - {sensor_data['temperature']}°C")
                return True
            else:
                print(f"❌ Échec envoi données")
                return False
        return False
    
    def publish_alert(self, alert_data):
        """Publier une alerte"""
        if self.is_connected:
            payload = json.dumps(alert_data)
            self.client.publish(ALERT_TOPIC, payload, qos=2)  # QoS 2 pour les alertes
            print(f"🚨 ALERTE: {alert_data['message']}")
    
    def handle_temperature_alert(self, alert_data):
        """Traiter les alertes de température"""
        print(f"🚨 ALERTE REÇUE: {alert_data['message']}")
        print(f"   Capteur: {alert_data['sensor_id']}")
        print(f"   Température: {alert_data['temperature']}°C")
        
    def handle_status_update(self, status_data):
        """Traiter les mises à jour de statut"""
        print(f"ℹ️ Statut: {status_data['message']}")
    
    def disconnect(self):
        """Déconnexion propre"""
        if self.is_connected:
            self.client.loop_stop()
            self.client.disconnect()

class DataStorage:
    """Stockage local des données"""
    
    def __init__(self, db_path="sensor_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT,
                location TEXT,
                temperature REAL,
                timestamp TEXT,
                alert_triggered BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_reading(self, sensor_data, alert_triggered=False):
        """Stocker une lecture de capteur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_readings 
            (sensor_id, location, temperature, timestamp, alert_triggered)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            sensor_data['sensor_id'],
            sensor_data['location'],
            sensor_data['temperature'],
            sensor_data['timestamp'],
            alert_triggered
        ))
        
        conn.commit()
        conn.close()

class IoTMonitoringSystem:
    """Système principal de surveillance IoT"""
    
    def __init__(self):
        self.hivemq_manager = HiveMQManager()
        self.data_storage = DataStorage()
        self.sensors = []
        self.is_running = False
        
        # Seuils d'alerte
        self.temp_threshold_high = 35.0
        self.temp_threshold_low = 10.0
    
    def add_sensor(self, sensor_id, location):
        """Ajouter un capteur"""
        sensor = TemperatureSensor(sensor_id, location)
        self.sensors.append(sensor)
        print(f"➕ Capteur ajouté: {sensor_id} ({location})")
    
    def check_temperature_alerts(self, sensor_data):
        """Vérifier et envoyer des alertes si nécessaire"""
        temp = sensor_data['temperature']
        alert_triggered = False
        
        if temp > self.temp_threshold_high:
            alert_data = {
                "alert_type": "HIGH_TEMPERATURE",
                "sensor_id": sensor_data['sensor_id'],
                "location": sensor_data['location'],
                "temperature": temp,
                "threshold": self.temp_threshold_high,
                "message": f"Température élevée détectée: {temp}°C",
                "timestamp": sensor_data['timestamp'],
                "severity": "HIGH"
            }
            self.hivemq_manager.publish_alert(alert_data)
            alert_triggered = True
            
        elif temp < self.temp_threshold_low:
            alert_data = {
                "alert_type": "LOW_TEMPERATURE",
                "sensor_id": sensor_data['sensor_id'],
                "location": sensor_data['location'],
                "temperature": temp,
                "threshold": self.temp_threshold_low,
                "message": f"Température basse détectée: {temp}°C",
                "timestamp": sensor_data['timestamp'],
                "severity": "MEDIUM"
            }
            self.hivemq_manager.publish_alert(alert_data)
            alert_triggered = True
        
        return alert_triggered
    
    def sensor_monitoring_loop(self):
        """Boucle principale de surveillance des capteurs"""
        print("🔄 Démarrage surveillance capteurs...")
        
        while self.is_running:
            for sensor in self.sensors:
                if not self.is_running:
                    break
                
                # Générer et publier données capteur
                sensor_data = sensor.get_sensor_data()
                
                # Publier via HiveMQ
                success = self.hivemq_manager.publish_sensor_data(sensor_data)
                
                if success:
                    # Vérifier alertes
                    alert_triggered = self.check_temperature_alerts(sensor_data)
                    
                    # Stocker en local
                    self.data_storage.store_reading(sensor_data, alert_triggered)
                
                time.sleep(2)  # Lecture toutes les 2 secondes
            
            time.sleep(5)  # Pause entre cycles complets
    
    def start_monitoring(self):
        """Démarrer le système de surveillance"""
        print("🚀 Démarrage système IoT avec HiveMQ...")
        
        # Connexion HiveMQ
        if not self.hivemq_manager.connect():
            print("❌ Impossible de se connecter à HiveMQ")
            return False
        
        # Publier statut système
        status_data = {
            "system": "IoT Temperature Monitoring",
            "status": "ONLINE",
            "sensors_count": len(self.sensors),
            "timestamp": datetime.now().isoformat(),
            "message": "Système de surveillance démarré"
        }
        self.hivemq_manager.client.publish(STATUS_TOPIC, json.dumps(status_data))
        
        # Démarrer surveillance
        self.is_running = True
        monitoring_thread = threading.Thread(target=self.sensor_monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        print("✅ Système de surveillance actif!")
        return True
    
    def stop_monitoring(self):
        """Arrêter le système"""
        print("🛑 Arrêt du système...")
        self.is_running = False
        
        # Publier statut d'arrêt
        status_data = {
            "system": "IoT Temperature Monitoring",
            "status": "OFFLINE",
            "timestamp": datetime.now().isoformat(),
            "message": "Système arrêté"
        }
        self.hivemq_manager.client.publish(STATUS_TOPIC, json.dumps(status_data))
        
        time.sleep(2)
        self.hivemq_manager.disconnect()
        print("✅ Système arrêté proprement")

def main():
    """Fonction principale - Démonstration du système"""
    
    print("🏭 Système IoT de Surveillance avec HiveMQ")
    print("=" * 50)
    
    # Créer le système
    iot_system = IoTMonitoringSystem()
    
    # Ajouter des capteurs
    iot_system.add_sensor("TEMP_001", "Atelier Production")
    iot_system.add_sensor("TEMP_002", "Entrepôt")
    iot_system.add_sensor("TEMP_003", "Bureau")
    iot_system.add_sensor("TEMP_004", "Salle Serveurs")
    
    try:
        # Démarrer surveillance
        if iot_system.start_monitoring():
            print("\n📊 Surveillance en cours... (Ctrl+C pour arrêter)")
            
            # Boucle principale
            while True:
                time.sleep(10)
                print(f"⏰ Système actif - {datetime.now().strftime('%H:%M:%S')}")
                
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par utilisateur")
        
    finally:
        iot_system.stop_monitoring()

if __name__ == "__main__":
    main()

# CONFIGURATION REQUISE :
# pip install paho-mqtt

# CONFIGURATION HIVEMQ CLOUD :
# 1. Créer un compte sur https://www.hivemq.com/
# 2. Créer un cluster gratuit
# 3. Configurer les credentials (username/password)
# 4. Remplacer les variables HIVEMQ_* avec vos informations