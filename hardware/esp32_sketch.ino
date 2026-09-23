#include <WiFi.h>
#include <HTTPClient.h>

// Replace with your Wi‑Fi credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// Backend endpoint (replace with your actual URL)
const char* serverName = "https://your-backend-url/observations";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  // Placeholder: simulate an observation every 30 seconds
  if ((WiFi.status() == WL_CONNECTED)) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "multipart/form-data");
    // Here you would attach a real file. For demo we just send a dummy payload.
    int httpResponseCode = http.POST("dummy data");
    Serial.print("POST response code: ");
    Serial.println(httpResponseCode);
    http.end();
  }
  delay(30000);
}
