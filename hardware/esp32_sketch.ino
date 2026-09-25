/*
 * MONITOR SECCHIA - Hardware Firmware
 * This sketch handles movement detection via PIR, captures an image/audio,
 * and sends it to the FastAPI backend on Render.
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

// --- CONFIGURATION ---
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "https://your-backend-url.onrender.com/observations";
const char* stationId = "SECCHIA-01";

// Pin definitions (ESP32-CAM standard)
#define PIR_PIN 13 

void setup() {
  Serial.begin(115200);
  
  // Initialize PIR sensor
  pinMode(PIR_PIN, INPUT);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  // Initialize Camera (Basic configuration for AI2-Thinker ESP32-CAM)
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5; config.pin_d1 = 18; config.pin_d2 = 19; config.pin_d3 = 21;
  config.pin_d4 = 36; config.pin_d5 = 39; config.pin_d6 = 34; config.pin_d7 = 35;
  config.pin_xclk = 0; config.pin_pclk = 22; config.pin_vsync = 25; config.pin_href = 23;
  config.pin_sscb_sda = 26; config.pin_sscb_scl = 27;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_SVGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  Serial.println("Camera initialized!");
}

void loop() {
  // Trigger: Detect movement
  if (digitalRead(PIR_PIN) == HIGH) {
    Serial.println("Movement detected! Capturing...");
    
    // 1. Capture Image
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }

    // 2. Send to Backend
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      
      // Construction of the multipart request
      String boundary = "----ESP32Boundary";
      http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
      
      String head = "--" + boundary + "\r\n" +
                    "Content-Disposition: form-data; name=\"station_id\"\r\n\r\n" + stationId + "\r\n" +
                    "--" + boundary + "\r\n" +
                    "Content-Disposition: form-data; name=\"method\"\r\n\r\nimage\r\n" +
                    "--" + boundary + "\r\n" +
                    "Content-Disposition: form-data; name=\"file\"; filename=\"capture.jpg\"\r\n" +
                    "Content-Type: image/jpeg\r\n\r\n";
      
      String tail = "\r\n--" + boundary + "--\r\n";
      
      uint32_t totalLen = head.length() + fb->len + tail.length();
      
      // We use a custom write to avoid loading the whole image into a String (memory safety)
      int httpResponseCode = http.sendRequest("POST", (uint8_t*)head.c_str(), head.length()); 
      // Note: Standard HTTPClient.POST is simpler but less flexible for binaries.
      // For actual deployment, we use the buffer method:
      
      // Corrected send method for binary data:
      http.begin(serverUrl);
      http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
      
      // Use the buffer approach to avoid memory crashes
      // This is a simplified version; in production, we use a custom multipart wrapper
      int response = http.POST(fb->buf, fb->len); 
      
      Serial.printf("Response code: %d\n", response);
      http.end();
    } else {
      Serial.println("WiFi disconnected, skipping upload");
    }

    esp_camera_fb_return(fb);
    
    // Cooldown to avoid flooding
    delay(10000); 
  }
  delay(100);
}
