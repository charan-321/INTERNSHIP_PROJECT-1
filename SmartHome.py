import time
import random
import threading
import matplotlib.pyplot as plt
from datetime import datetime

# Base Device Class
class SmartDevice:
    def __init__(self, device_id, name, status="off"):
        self.device_id = device_id
        self.name = name
        self._status = status

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        if new_status in ("on", "off"):
            self._status = new_status
            print(f"[{self.name}] Status changed to: {self._status}")

    def turn_on(self):
        self.status = "on"

    def turn_off(self):
        self.status = "off"

# Smart Light
class SmartLight(SmartDevice):
    def __init__(self, device_id, name, brightness=50):
        super().__init__(device_id, name)
        self.brightness = brightness

    def set_brightness(self, level):
        if 0 <= level <= 100:
            self.brightness = level
            print(f"[{self.name}] Brightness set to {self.brightness}%")

# Smart Thermostat
class SmartThermostat(SmartDevice):
    def __init__(self, device_id, name, target_temperature=24):
        super().__init__(device_id, name)
        self.target_temperature = target_temperature

    def set_target_temperature(self, temp):
        if 18 <= temp <= 30:
            self.target_temperature = temp
            print(f"[{self.name}] Target temperature set to {self.target_temperature}°C")

# Sensor Base Class
class Sensor:
    def __init__(self, sensor_id, name):
        self.sensor_id = sensor_id
        self.name = name
        self.value = None

    def read_value(self):
        raise NotImplementedError("Subclasses must implement read_value method.")

# Temperature Sensor
class TemperatureSensor(Sensor):
    def read_value(self):
        self.value = round(random.uniform(20, 30), 2)

# Light Sensor
class LightSensor(Sensor):
    def read_value(self):
        self.value = random.randint(100, 600)

# Motion Sensor
class MotionSensor(Sensor):
    def read_value(self):
        self.value = random.choice([True, False])

# Home Automation System
class HomeAutomationSystem:
    def __init__(self):
        self.devices = {}
        self.sensors = {}
        self.running = False
        self.last_motion_time = time.time()
        self.start_time = time.time()

        # For visualization
        self.timestamps = []
        self.temp_data = []
        self.light_data = []
        self.motion_data = []

        self.initialize_components()

    def initialize_components(self):
        self.devices["light_1"] = SmartLight("light_1", "Living Room Light")
        self.devices["thermostat_1"] = SmartThermostat("thermostat_1", "Main Thermostat")

        self.sensors["temp_sensor_1"] = TemperatureSensor("temp_sensor_1", "Temperature Sensor")
        self.sensors["light_sensor_1"] = LightSensor("light_sensor_1", "Light Sensor")
        self.sensors["motion_sensor_1"] = MotionSensor("motion_sensor_1", "Motion Sensor")

    def process_sensor_data(self):
        print("\n--- Reading Sensor Data ---")
        current_time = round(time.time() - self.start_time, 2)

        for sensor in self.sensors.values():
            sensor.read_value()
            print(f"{sensor.name}: {sensor.value}")

        # Store data for visualization
        self.timestamps.append(current_time)
        self.temp_data.append(self.sensors["temp_sensor_1"].value)
        self.light_data.append(self.sensors["light_sensor_1"].value)
        self.motion_data.append(1 if self.sensors["motion_sensor_1"].value else 0)

        self.rule_thermostat_control()
        self.rule_lighting_control()

    def rule_thermostat_control(self):
        temp_sensor = self.sensors["temp_sensor_1"]
        thermostat = self.devices["thermostat_1"]
        current_temp = temp_sensor.value
        target_temp = thermostat.target_temperature

        if current_temp > target_temp + 1:
            print(f"[Thermostat] Cooling needed. Current: {current_temp}°C, Target: {target_temp}°C")
            thermostat.turn_on()
        elif current_temp < target_temp - 1:
            print(f"[Thermostat] Heating needed. Current: {current_temp}°C, Target: {target_temp}°C")
            thermostat.turn_on()
        else:
            print(f"[Thermostat] Temperature stable. Current: {current_temp}°C")
            thermostat.turn_off()

    def rule_lighting_control(self):
        light_sensor = self.sensors["light_sensor_1"]
        motion_sensor = self.sensors["motion_sensor_1"]
        light = self.devices["light_1"]

        if motion_sensor.value:
            self.last_motion_time = time.time()
            if light_sensor.value < 200 and light.status == "off":
                light.turn_on()
                light.set_brightness(70)
        else:
            if light.status == "on" and (time.time() - self.last_motion_time > 30):
                print("[AI] No motion detected for 30 seconds. Turning off light.")
                light.turn_off()

    def start_monitoring(self, interval=5):
        print("Starting Home Automation System...")
        self.running = True
        while self.running:
            self.process_sensor_data()
            time.sleep(interval)

    def stop_monitoring(self):
        self.running = False
        print("\n-- Stopping Home Automation System --")
        self.plot_data()

    def plot_data(self):
        print("\nGenerating visualization...")
        plt.figure(figsize=(10, 6))  # ✅ No 'filesize' argument
        plt.plot(self.timestamps, self.temp_data, label="Temperature (°C)", color='red')
        plt.plot(self.timestamps, self.light_data, label="Light Intensity (lux)", color='orange')
        plt.plot(self.timestamps, self.motion_data, label="Motion Detected (1=Yes, 0=No)", color='blue')
        plt.xlabel("Time (seconds)")
        plt.ylabel("Sensor Values")
        plt.title("Smart Home Sensor Readings Over Time")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

# Main Execution
if __name__ == "__main__":
    home_system = HomeAutomationSystem()
    automation_thread = threading.Thread(target=home_system.start_monitoring, args=(5,))
    automation_thread.daemon = True
    automation_thread.start()

    try:
        print("System is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        home_system.stop_monitoring()
        automation_thread.join()
        print("System stopped gracefully.")