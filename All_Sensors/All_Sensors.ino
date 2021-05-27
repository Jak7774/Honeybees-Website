#include <OneWire.h>
#include <DallasTemperature.h>
#include "DHT.h"
#include <HX711_ADC.h>
#if defined(ESP8266)|| defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif

/* --- Setup Temperature Sensors --- */
#define ONE_WIRE_BUS 2 // Temp pins on D2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

/* --- Seupt Humidity Sensors ---*/
#define DHTTYPE DHT22
#define DHTPIN1 3
#define DHTPIN2 4

DHT dht[] = {
  {DHTPIN1, DHT22},
  {DHTPIN2, DHT22},
};

/* --- Setup Scale Sensors --- */
const int DOUT_PIN = 5;
const int SCK_PIN = 6;

//float calibration = 22.20; // Calibration Factor 
HX711_ADC LoadCell(DOUT_PIN, SCK_PIN);
const int calVal_eepromAddress = 0;
unsigned long t = 0;

float humidity[2];
float temperature[2];

void setup(void) {
  // Start Serial Communication for Debugging
  //Serial.begin(9600);
  Serial.begin(57600); delay(10);
  
  sensors.begin(); // temp sensors
  for (auto& sensor : dht) {
    sensor.begin();
  }

  float calibrationValue;
  #if defined(ESP8266) || defined(ESP32)
    EEPROM.begin(512);
  #endif
  EEPROM.get(calVal_eepromAddress, calibrationValue);
  
  LoadCell.begin();
  unsigned long stabilizingtime = 2000; // preciscion right after power-up can be improved by adding a few seconds of stabilizing time
  boolean _tare = false; //set this to false if you don't want tare to be performed in the next step
  LoadCell.start(stabilizingtime, _tare);
  LoadCell.setCalFactor(calibrationValue);
  LoadCell.update();
  LoadCell.refreshDataSet();
}

void loop(void){
  // Call below to issue a global temp and request to all sensors 
  sensors.requestTemperatures();
  
  // Temp Sensors
  /* --- First Sensor --- */
  //Serial.print("temp1");
  Serial.print(sensors.getTempCByIndex(0));
  
  /* --- Second Sensor --- */
  Serial.print(", ");
  Serial.print(sensors.getTempCByIndex(1));
  
  //DHT Humidity Sensors
  for (int i = 0; i < 2; i++) {
    temperature[i] = dht[i].readTemperature();
    humidity[i] = dht[i].readHumidity();
  }
  
  for (int i = 0; i < 2; i++) {
    Serial.print(F(", "));
    //Serial.print(i);
    //Serial.print(": ");
    Serial.print(humidity[i]);
    //Serial.print(F("%"));
    Serial.print(F(", "));
    //Serial.print(i + 3);
    //Serial.print(": ");
    Serial.print(temperature[i]);
  }


  /* --- Weight Sensor Output --- */
  Serial.print(", ");
  static boolean newDataReady = 0;
  const int serialPrintInterval = 0;

  if (LoadCell.update()) newDataReady = true;

  if (newDataReady) {
    if (millis() > t + serialPrintInterval ) {
      float w = LoadCell.getData();
      Serial.print(w);
      newDataReady = 0;
      t = millis();
    }
  }
 
  Serial.println(" ");
  
  delay(1000);
}
