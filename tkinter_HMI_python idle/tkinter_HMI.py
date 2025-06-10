import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import threading

# === MQTT CONFIG ===
MQTT_BROKER = "192.168.0.102"
MQTT_PORT = 1883
MQTT_TOPIC_SUB = "/ic/Grupo0"
MQTT_TOPIC_PUB = "/led/control"

# === Global dictionary for sensor data ===
sensor_data = {
    "TEMP": "N/A",
    "HUMID": "N/A",
    "WATER": "N/A",
    "SOUND": "N/A",
    "LIGHT": "N/A"
}

# === MQTT Callback ===
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[MQTT] {msg.topic} -> {payload}")
    if ":" in payload:
        key, value = payload.split(":", 1)
        key = key.strip().upper()
        value = value.strip()
        if key in sensor_data:
            sensor_data[key] = value
            update_labels()

def mqtt_loop():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC_SUB)
    client.loop_forever()

# === GUI Setup ===
root = tk.Tk()
root.title("IoT Sensor Monitoring & Control Panel")
root.geometry("500x450")
root.resizable(False, False)
root.configure(bg="#ecf0f1")

# === Widgets ===
title_label = tk.Label(root, text="IoT Sensor Dashboard", font=("Arial", 18, "bold"), bg="#2c3e50", fg="white", pady=10)
title_label.pack(fill=tk.X)

frame = tk.Frame(root, bg="#ecf0f1", padx=10, pady=10)
frame.pack(pady=20)

labels = {}

def update_labels():
    for key in sensor_data:
        labels[key].config(text=sensor_data[key])

row = 0
for key in sensor_data:
    tk.Label(frame, text=f"{key}:", font=("Arial", 12, "bold"), bg="#ecf0f1").grid(row=row, column=0, sticky='w', pady=5)
    labels[key] = tk.Label(frame, text="N/A", font=("Arial", 12), bg="#dff9fb", width=10)
    labels[key].grid(row=row, column=1, pady=5, padx=10)
    row += 1

# === Command Button Area ===
def send_command(cmd):
    try:
        pub_client = mqtt.Client()
        pub_client.connect(MQTT_BROKER, MQTT_PORT)
        pub_client.publish(MQTT_TOPIC_PUB, cmd)
        pub_client.disconnect()
        status_label.config(text=f"Sent: {cmd}")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

button_frame = tk.Frame(root, bg="#ecf0f1")
button_frame.pack(pady=10)

ping_btn = tk.Button(button_frame, text="Send PING", bg="#3498db", fg="white", font=("Arial", 12),
                     command=lambda: send_command("PING"), width=15)
ping_btn.grid(row=0, column=0, padx=10)

test_btn = tk.Button(button_frame, text="Send TEST", bg="#2ecc71", fg="white", font=("Arial", 12),
                     command=lambda: send_command("TEST"), width=15)
test_btn.grid(row=0, column=1, padx=10)

status_label = tk.Label(root, text="", bg="#ecf0f1", fg="green", font=("Arial", 10))
status_label.pack()

# === Start MQTT Thread ===
threading.Thread(target=mqtt_loop, daemon=True).start()

root.mainloop()
