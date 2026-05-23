from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__) #creates a web application

# === MQTT Configuration ===
MQTT_BROKER = "192.168.0.102"  # <-- Use your correct IP from ipconfig
MQTT_TOPIC_SUB = "/ic/Grupo0" # where data is received
MQTT_TOPIC_PUB = "/led/control" #where esp32 listens for commands

# === dictionary to store latest Sensor values store ===
sensor_data = {
    "TEMP": "N/A",
    "HUMID": "N/A",
    "WATER": "N/A",
    "SOUND": "N/A",
    "LIGHT": "N/A"
}

# === MQTT message callback ===
#decodes the payload
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"[MQTT] {msg.topic} → {message}")
    if ":" in message:
        key, value = message.split(":", 1)#splits it,Checks if key is one of the expected sensors
        key = key.strip().upper()
        if key in sensor_data:
            sensor_data[key] = value.strip()

# === MQTT background thread ===
def mqtt_thread():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883) #connects to broker
    client.subscribe(MQTT_TOPIC_SUB)#subscribes to /ic/Grupo0
    client.loop_forever() #Listens for messages forever using loop_forever()

# Start the MQTT listener in background
#Starts the mqtt_thread() #in the background so the Flask server can run at the same time.
threading.Thread(target=mqtt_thread, daemon=True).start()

# === HMI Route ===
@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        command = request.form.get("command")
        pub_client = mqtt.Client()
        pub_client.connect(MQTT_BROKER, 1883)
        pub_client.publish(MQTT_TOPIC_PUB, command)
        pub_client.disconnect()
        print(f"[HMI] Sent command: {command}")
    return render_template("dashboard.html")

# === Sensor Data API ===
@app.route("/data")
def get_data():
    return jsonify(sensor_data)#This API returns the latest sensor values in JSON format.

if __name__ == "__main__":
    app.run(debug=True) #Runs the Flask web server in debug mode on http:#127.0.0.1:5000/
