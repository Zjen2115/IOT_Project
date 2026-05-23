#include <WiFi.h>
#include <PubSubClient.h>

// === WiFi & MQTT Config ===
const char* ssid = "DuckNet";
const char* password = "DuckieUPT";
const char* mqtt_server = "192.168.0.102";  // IP of your MQTT broker
#define mqtt_port 1883

#define MQTT_PUB_TOPIC "/ic/Grupo0"       // ESP32 publishes sensor data here
#define MQTT_SUB_TOPIC "/led/control"     // ESP32 listens for control commands here
const char* clientId = "Arduino0";        // MQTT client ID for ESP32

// === UART Pins (ESP32 <-> Arduino UNO) ===
#define RXD2 16
#define TXD2 17

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// === Connect to WiFi ===
void setup_wifi() {
  Serial.println("Connecting to WiFi... ");
  Serial.println(ssid);
  Serial.println(password);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// === Ping the MQTT Broker ===
bool PingHost(IPAddress ip) {
  WiFiClient client;
  Serial.print("Trying to connect to ");
  Serial.print(ip);
  Serial.print(":");
  Serial.println(mqtt_port);

  if (client.connect(ip, mqtt_port)) {
    client.stop();
    return true;
  } else {
    return false;
  }
}

// === Reconnect to MQTT if disconnected ===
void reconnect() {
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (mqttClient.connect(clientId)) {
      Serial.println("Connected to MQTT broker");

      mqttClient.publish(MQTT_PUB_TOPIC, "hello world");
      Serial.print("Published to ");
      Serial.print(MQTT_PUB_TOPIC);
      Serial.println(" : hello world");

      boolean res = mqttClient.subscribe(MQTT_SUB_TOPIC);
      Serial.print("Subscribed to ");
      Serial.print(MQTT_SUB_TOPIC);
      Serial.println(res ? "  OK" : "  FAIL");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" - retrying in 5 seconds");
      delay(5000);
    }
  }
}

// === Handle incoming MQTT messages ===
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

// === Publish serial sensor data to MQTT ===
void publishSerialData(const String& msg) {
  if (!mqttClient.connected()) {
    reconnect();
  }
  mqttClient.publish(MQTT_PUB_TOPIC, msg.c_str());
  Serial.print("Published to ");
  Serial.print(MQTT_PUB_TOPIC);
  Serial.print(" : ");
  Serial.println(msg);
}

// === Setup ===
void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);

  setup_wifi();

  IPAddress mqttIP;
  if (WiFi.hostByName(mqtt_server, mqttIP)) {
    Serial.print("Resolved MQTT broker IP: ");
    Serial.println(mqttIP);

    if (PingHost(mqttIP)) {
      Serial.println("MQTT broker reachable!");
    } else {
      Serial.println("MQTT broker NOT reachable!");
    }
  } else {
    Serial.println("Could not resolve MQTT server hostname.");
  }

  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(callback);
  reconnect();
}

// === Main loop ===
void loop() {
  mqttClient.loop();

  if (Serial2.available()) {
    String msg = Serial2.readStringUntil('\n');
    msg.trim();
    if (msg.length() > 0) {
      Serial.print("Received from Arduino UNO: ");
      Serial.println(msg);
      publishSerialData(msg);
    }
  }
}
