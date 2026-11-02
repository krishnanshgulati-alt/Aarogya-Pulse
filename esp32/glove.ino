/*
  OPTIONAL ESP32-to-backend example (Wi-Fi POST).

  IMPORTANT:
  - Replace WIFI_NAME and WIFI_PASSWORD.
  - Replace SERVER_IP with the IP address of the computer running FastAPI.
  - Computer and ESP32 must be on the same Wi-Fi network.
  - This sketch uses placeholder sensor values to demonstrate networking.
  - It does NOT yet read the MAX30102, DS18B20 or MPU6050.
  - Do not use placeholder values as real health measurements.
*/

#include <WiFi.h>
#include <HTTPClient.h>

const char* WIFI_NAME = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_IP = "192.168.1.100"; // Change this to your computer's LAN IP.
const int SERVER_PORT = 8000;

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_NAME, WIFI_PASSWORD);

  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected. ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String("http://") + SERVER_IP + ":" + SERVER_PORT + "/api/readings";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    // DEMO ONLY: Replace this JSON with actual sensor readings once your
    // MAX30102, DS18B20 and MPU6050 code is integrated.
    String json = "{\"heart_rate\":80,\"spo2\":98,\"skin_temperature\":32.5,"
                  "\"pulse_feature\":0.5,\"motion_detected\":false,\"source\":\"esp32-demo\"}";

    int statusCode = http.POST(json);
    Serial.print("Backend HTTP status: ");
    Serial.println(statusCode);
    Serial.println(http.getString());
    http.end();
  } else {
    Serial.println("Wi-Fi disconnected; reconnecting...");
    WiFi.reconnect();
  }

  delay(5000); // Send every 5 seconds in this networking demo.
}
