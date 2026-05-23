#include "DHT.h"

#define SOUND_SENSOR_PIN 2
#define WATER_SENSOR_PIN 3
#define DHTPIN 4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600); // Отправляем данные ESP32
  pinMode(SOUND_SENSOR_PIN, INPUT);
  pinMode(WATER_SENSOR_PIN, INPUT);
  dht.begin();
}

void loop() {
  int soundState = digitalRead(SOUND_SENSOR_PIN);
  int waterState = digitalRead(WATER_SENSOR_PIN);
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int lightLevel = analogRead(A0);

  Serial.print("TEMP:");
  Serial.println(temperature);

  Serial.print("HUMID:");
  Serial.println(humidity);

  Serial.print("WATER:");
  Serial.println(waterState);

  Serial.print("SOUND:");
  Serial.println(soundState);

  Serial.print("LIGHT:");
  Serial.println(lightLevel);

  delay(2000);
}